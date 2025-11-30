"""
Script para gerar evento de teste, inscrições e arquivo CSV de resultados.
Cria:
- Evento: Maratona Internacional de Florianopolis (11/11/2025, 10km)
- 30 inscrições mantendo proporção por categoria/gênero
- Arquivo CSV com CPF e tempos realistas
"""
import sqlite3
import csv
import random
import os
from datetime import datetime
from entidade.atleta import Atleta

STATUS_PAGA = 3


def gerar_cpf_valido() -> str:
    """
    Gera um CPF válido com dígitos verificadores calculados.
    
    Returns:
        CPF válido como string (11 dígitos)
    """
    # Gerar 9 primeiros dígitos (não pode ser todos iguais)
    while True:
        cpf_base = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        if cpf_base != cpf_base[0] * 9:  # Não pode ser todos iguais
            break
    
    # Calcular primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf_base[i]) * (10 - i)
    
    resto = soma % 11
    digito_1 = 0 if resto < 2 else 11 - resto
    cpf_com_digito_1 = cpf_base + str(digito_1)
    
    # Calcular segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf_com_digito_1[i]) * (11 - i)
    
    resto = soma % 11
    digito_2 = 0 if resto < 2 else 11 - resto
    
    return cpf_com_digito_1 + str(digito_2)


def validar_cpf(cpf: str) -> bool:
    """
    Valida um CPF usando o mesmo algoritmo do sistema.
    
    Args:
        cpf: CPF para validar
        
    Returns:
        True se válido, False caso contrário
    """
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf_limpo) != 11:
        return False
    
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    
    # Validar primeiro dígito
    soma = 0
    for i in range(9):
        soma += int(cpf_limpo[i]) * (10 - i)
    
    resto = soma % 11
    digito_verificador_1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf_limpo[9]) != digito_verificador_1:
        return False
    
    # Validar segundo dígito
    soma = 0
    for i in range(10):
        soma += int(cpf_limpo[i]) * (11 - i)
    
    resto = soma % 11
    digito_verificador_2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf_limpo[10]) != digito_verificador_2:
        return False
    
    return True


# CPF do organizador (validar ou gerar um válido)
ORGANIZADOR_CPF = '07998448962'

# Verificar se o CPF do organizador é válido
if not validar_cpf(ORGANIZADOR_CPF):
    print(f"CPF do organizador {ORGANIZADOR_CPF} é inválido. Gerando um válido...")
    ORGANIZADOR_CPF = gerar_cpf_valido()
    print(f"Novo CPF do organizador: {ORGANIZADOR_CPF}")


def garantir_organizador_existe(cursor):
    """Garante que o organizador existe no banco."""
    cursor.execute("SELECT * FROM usuarios WHERE cpf = ? AND perfil = '0'", (ORGANIZADOR_CPF,))
    if cursor.fetchone():
        print(f"Organizador {ORGANIZADOR_CPF} já existe no banco.")
        return
    
    # Criar organizador se não existir
    import bcrypt
    senha_hash = bcrypt.hashpw('senha123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""
        INSERT INTO usuarios (cpf, nome, email, senha_hash, perfil, data_nascimento, genero, pcd)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ORGANIZADOR_CPF, 'Organizador Teste', 'organizador@teste.com', senha_hash, '0', None, None, None))
    print(f"Organizador {ORGANIZADOR_CPF} criado no banco.")


def obter_atletas_por_categoria(cursor):
    """Obtém atletas do banco agrupados por categoria/gênero."""
    
    cursor.execute("SELECT * FROM usuarios WHERE perfil = '1'")
    usuarios = cursor.fetchall()
    
    atletas_por_categoria = {
        'Júnior_Masculino': [],
        'Júnior_Feminino': [],
        'Adulto_Masculino': [],
        'Adulto_Feminino': [],
        'Master_Masculino': [],
        'Master_Feminino': [],
        'PCD_Masculino': [],
        'PCD_Feminino': []
    }
    
    data_evento = "11/11/2025"
    
    for usuario in usuarios:
        if usuario[4] == '1':  # É atleta
            try:
                atleta = Atleta(
                    nome=usuario[1],
                    cpf=usuario[0],
                    email=usuario[2],
                    senha_hash=usuario[3],
                    data_nascimento=usuario[5],
                    genero=usuario[6],
                    pcd=bool(usuario[7])
                )
                
                categoria = atleta.calcular_categoria(data_evento)
                genero = atleta.genero
                
                chave = f"{categoria}_{genero}"
                if chave in atletas_por_categoria:
                    atletas_por_categoria[chave].append(atleta)
            except Exception as e:
                print(f"Erro ao processar atleta {usuario[0]}: {e}")
                continue
    
    return atletas_por_categoria


def gerar_tempo_realista_10km(genero: str, categoria: str) -> str:
    """
    Gera tempo realista para 10km baseado em gênero e categoria.
    
    Args:
        genero: 'Masculino' ou 'Feminino'
        categoria: 'Júnior', 'Adulto', 'Master', 'PCD'
        
    Returns:
        Tempo no formato HH:MM:SS
    """
    # Tempos realistas para 10km (em minutos)
    # Baseado em tempos médios de corredores amadores
    
    if categoria == 'PCD':
        # PCD geralmente tem tempos um pouco maiores
        if genero == 'Masculino':
            tempo_min = random.uniform(45, 90)  # 45-90 minutos
        else:
            tempo_min = random.uniform(50, 95)  # 50-95 minutos
    elif categoria == 'Júnior':
        # Jovens geralmente são mais rápidos
        if genero == 'Masculino':
            tempo_min = random.uniform(35, 65)  # 35-65 minutos
        else:
            tempo_min = random.uniform(40, 70)  # 40-70 minutos
    elif categoria == 'Adulto':
        # Adultos têm boa performance
        if genero == 'Masculino':
            tempo_min = random.uniform(30, 60)  # 30-60 minutos
        else:
            tempo_min = random.uniform(35, 65)  # 35-65 minutos
    else:  # Master
        # Masters ainda mantêm boa forma
        if genero == 'Masculino':
            tempo_min = random.uniform(40, 75)  # 40-75 minutos
        else:
            tempo_min = random.uniform(45, 80)  # 45-80 minutos
    
    # Converter para HH:MM:SS
    horas = int(tempo_min // 60)
    minutos = int(tempo_min % 60)
    segundos = int((tempo_min % 1) * 60)
    
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def selecionar_atletas_proporcionais(atletas_por_categoria: dict, total: int = 30):
    """
    Seleciona atletas mantendo proporção por categoria/gênero.
    
    Args:
        atletas_por_categoria: Dicionário com atletas agrupados
        total: Total de atletas a selecionar
        
    Returns:
        Lista de atletas selecionados
    """
    # Distribuição proporcional (baseada nos 50 atletas)
    # Júnior: 15M + 15F = 30 (60%)
    # Adulto: 15M + 15F = 30 (60%)
    # Master: 8M + 8F = 16 (32%)
    # PCD: 2M + 2F = 4 (8%)
    
    # Para 30 atletas:
    # Júnior: ~9 (4-5M, 4-5F)
    # Adulto: ~9 (4-5M, 4-5F)
    # Master: ~9 (4-5M, 4-5F)
    # PCD: ~3 (1-2M, 1-2F)
    
    selecionados = []
    
    # Júnior Masculino: 5
    if len(atletas_por_categoria['Júnior_Masculino']) >= 5:
        selecionados.extend(random.sample(atletas_por_categoria['Júnior_Masculino'], 5))
    else:
        selecionados.extend(atletas_por_categoria['Júnior_Masculino'])
    
    # Júnior Feminino: 5
    if len(atletas_por_categoria['Júnior_Feminino']) >= 5:
        selecionados.extend(random.sample(atletas_por_categoria['Júnior_Feminino'], 5))
    else:
        selecionados.extend(atletas_por_categoria['Júnior_Feminino'])
    
    # Adulto Masculino: 5
    if len(atletas_por_categoria['Adulto_Masculino']) >= 5:
        selecionados.extend(random.sample(atletas_por_categoria['Adulto_Masculino'], 5))
    else:
        selecionados.extend(atletas_por_categoria['Adulto_Masculino'])
    
    # Adulto Feminino: 5
    if len(atletas_por_categoria['Adulto_Feminino']) >= 5:
        selecionados.extend(random.sample(atletas_por_categoria['Adulto_Feminino'], 5))
    else:
        selecionados.extend(atletas_por_categoria['Adulto_Feminino'])
    
    # Master Masculino: 4
    if len(atletas_por_categoria['Master_Masculino']) >= 4:
        selecionados.extend(random.sample(atletas_por_categoria['Master_Masculino'], 4))
    else:
        selecionados.extend(atletas_por_categoria['Master_Masculino'])
    
    # Master Feminino: 4
    if len(atletas_por_categoria['Master_Feminino']) >= 4:
        selecionados.extend(random.sample(atletas_por_categoria['Master_Feminino'], 4))
    else:
        selecionados.extend(atletas_por_categoria['Master_Feminino'])
    
    # PCD Masculino: 1
    if len(atletas_por_categoria['PCD_Masculino']) >= 1:
        selecionados.extend(random.sample(atletas_por_categoria['PCD_Masculino'], 1))
    else:
        selecionados.extend(atletas_por_categoria['PCD_Masculino'])
    
    # PCD Feminino: 1
    if len(atletas_por_categoria['PCD_Feminino']) >= 1:
        selecionados.extend(random.sample(atletas_por_categoria['PCD_Feminino'], 1))
    else:
        selecionados.extend(atletas_por_categoria['PCD_Feminino'])
    
    # Se não chegou a 30, completar aleatoriamente
    if len(selecionados) < total:
        todos_atletas = []
        for lista in atletas_por_categoria.values():
            todos_atletas.extend(lista)
        
        # Remover duplicatas
        cpfs_selecionados = {atleta.cpf for atleta in selecionados}
        disponiveis = [a for a in todos_atletas if a.cpf not in cpfs_selecionados]
        
        faltam = total - len(selecionados)
        if len(disponiveis) >= faltam:
            selecionados.extend(random.sample(disponiveis, faltam))
        else:
            selecionados.extend(disponiveis)
    
    # Limitar a 30
    return selecionados[:30]


def criar_evento(cursor):
    """Cria o evento no banco."""
    # Verificar se evento já existe
    cursor.execute("SELECT id FROM Eventos WHERE nome = ?", ('Maratona Internacional de Florianopolis',))
    evento_existente = cursor.fetchone()
    
    if evento_existente:
        evento_id = evento_existente[0]
        print(f"Evento já existe com ID: {evento_id}")
        # Buscar kit do evento
        cursor.execute("SELECT id FROM KitsDeCorrida WHERE evento_id = ? LIMIT 1", (evento_id,))
        kit_row = cursor.fetchone()
        if kit_row:
            kit_id = kit_row[0]
        else:
            # Criar kit se não existir
            cursor.execute("""
                INSERT INTO KitsDeCorrida (nome, descricao, valor, evento_id)
                VALUES (?, ?, ?, ?)
            """, ('Kit Básico', 'Kit contém: Camiseta, Medalha, Número de peito', 50.0, evento_id))
            kit_id = cursor.lastrowid
        return evento_id, kit_id
    
    # Criar evento
    cursor.execute("""
        INSERT INTO Eventos (nome, data, distancia, local_largada, tempo_corte, data_limite_cred, organizador_cpf)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        'Maratona Internacional de Florianopolis',
        '11/11/2025',
        10,
        'Av. Beira Mar Norte, Florianópolis',
        '2:0',
        '10/11/2025',
        ORGANIZADOR_CPF
    ))
    
    evento_id = cursor.lastrowid
    print(f"Evento criado com ID: {evento_id}")
    
    # Criar um kit para o evento
    cursor.execute("""
        INSERT INTO KitsDeCorrida (nome, descricao, valor, evento_id)
        VALUES (?, ?, ?, ?)
    """, (
        'Kit Básico',
        'Kit contém: Camiseta, Medalha, Número de peito',
        50.0,
        evento_id
    ))
    
    kit_id = cursor.lastrowid
    print(f"Kit criado com ID: {kit_id}")
    
    return evento_id, kit_id


def criar_inscricoes(cursor, evento_id: int, kit_id: int, atletas: list):
    """Cria inscrições para os atletas no evento."""
    data_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    inscricoes_criadas = 0
    for atleta in atletas:
        # Verificar se já está inscrito
        cursor.execute("""
            SELECT id FROM inscricoes 
            WHERE atleta_cpf = ? AND evento_id = ?
        """, (atleta.cpf, evento_id))
        
        if cursor.fetchone():
            continue
        
        # Criar inscrição
        kit_entregue = random.choice([0, 1])  # Variar entre entregue e não entregue
        
        cursor.execute("""
            INSERT INTO inscricoes (data_inscricao, kit_entregue, status, atleta_cpf, evento_id, kit_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data_agora, kit_entregue, STATUS_PAGA, atleta.cpf, evento_id, kit_id))
        
        inscricoes_criadas += 1
    
    print(f"{inscricoes_criadas} inscrições criadas.")
    return inscricoes_criadas


def _caminho_csv(nome_arquivo: str) -> str:
    """
    Gera o caminho absoluto para salvar o CSV dentro da pasta 'csv'.
    Sobrescreve arquivos existentes.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pasta_csv = os.path.join(base_dir, 'csv')
    os.makedirs(pasta_csv, exist_ok=True)
    return os.path.join(pasta_csv, nome_arquivo)


def gerar_csv_resultados(atletas: list, nome_arquivo: str = 'resultados_teste.csv'):
    """Gera arquivo CSV com CPF e tempos dos atletas."""
    dados_csv = []
    
    for atleta in atletas:
        categoria = atleta.calcular_categoria("11/11/2025")
        tempo = gerar_tempo_realista_10km(atleta.genero, categoria)
        dados_csv.append([atleta.cpf, tempo])
    
    # Ordenar por tempo (mais rápido primeiro)
    dados_csv.sort(key=lambda x: sum(int(t) * (60 ** (2 - i)) for i, t in enumerate(x[1].split(':'))))
    
    # Escrever CSV
    caminho = _caminho_csv(nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        # Sem cabeçalho conforme especificado
        writer.writerows(dados_csv)
    
    print(f"Arquivo CSV '{caminho}' gerado com {len(dados_csv)} resultados.")
    return caminho


def gerar_csv_erro_cpf_invalido(atletas: list):
    """Gera CSV com CPFs inválidos para testar validação."""
    dados_csv = []
    
    # Pegar alguns atletas válidos e alguns com CPF inválido
    for i, atleta in enumerate(atletas[:10]):
        if i < 5:
            # CPFs inválidos (tamanho errado, dígitos inválidos, etc)
            cpfs_invalidos = [
                '123456789',  # Muito curto
                '123456789012',  # Muito longo
                '00000000000',  # Todos zeros
                '11111111111',  # Todos iguais
                '123.456.789-10'  # Com formatação (mas dígitos verificadores inválidos)
            ]
            dados_csv.append([cpfs_invalidos[i], gerar_tempo_realista_10km(atleta.genero, atleta.calcular_categoria("11/11/2025"))])
        else:
            # CPF válido para comparação
            dados_csv.append([atleta.cpf, gerar_tempo_realista_10km(atleta.genero, atleta.calcular_categoria("11/11/2025"))])
    
    nome_arquivo = 'resultados_erro_cpf_invalido.csv'
    caminho = _caminho_csv(nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(dados_csv)
    
    print(f"Arquivo CSV '{caminho}' gerado com {len(dados_csv)} linhas (5 com CPF inválido).")
    return caminho


def gerar_csv_erro_atleta_nao_cadastrado():
    """Gera CSV com CPFs de atletas não cadastrados no banco."""
    
    dados_csv = []
    
    # Gerar CPFs válidos mas que não existem no banco
    for i in range(10):
        cpf_inexistente = gerar_cpf_valido()
        # Gerar tempo aleatório
        horas = random.randint(0, 1)
        minutos = random.randint(30, 60)
        segundos = random.randint(0, 59)
        tempo = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        dados_csv.append([cpf_inexistente, tempo])
    
    nome_arquivo = 'resultados_erro_atleta_nao_cadastrado.csv'
    caminho = _caminho_csv(nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(dados_csv)
    
    print(f"Arquivo CSV '{caminho}' gerado com {len(dados_csv)} linhas (atletas não cadastrados).")
    return caminho


def gerar_csv_erro_tempo_nao_informado(atletas: list):
    """Gera CSV com tempos não informados (vazios)."""
    dados_csv = []
    
    for i, atleta in enumerate(atletas[:10]):
        if i < 5:
            # Tempo vazio ou apenas espaço
            dados_csv.append([atleta.cpf, ''])
        else:
            # Tempo válido para comparação
            categoria = atleta.calcular_categoria("11/11/2025")
            tempo = gerar_tempo_realista_10km(atleta.genero, categoria)
            dados_csv.append([atleta.cpf, tempo])
    
    nome_arquivo = 'resultados_erro_tempo_nao_informado.csv'
    caminho = _caminho_csv(nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(dados_csv)
    
    print(f"Arquivo CSV '{caminho}' gerado com {len(dados_csv)} linhas (5 com tempo não informado).")
    return caminho


def gerar_csv_erro_tempo_invalido(atletas: list):
    """Gera CSV com tempos em formato inválido."""
    dados_csv = []
    
    tempos_invalidos = [
        '25:70:30',  # Minutos > 59
        '10:30:70',  # Segundos > 59
        '1:30:45',   # Formato sem zero à esquerda (pode ser aceito, mas testa)
        '10:30',     # Falta segundos
        '10',        # Apenas horas
        'abc:def:ghi',  # Não numérico
        '10:30:45:50',  # Muitos campos
        '-10:30:45',    # Negativo
        '99:99:99'      # Valores muito altos
    ]
    
    for i, atleta in enumerate(atletas[:10]):
        if i < len(tempos_invalidos):
            dados_csv.append([atleta.cpf, tempos_invalidos[i]])
        else:
            # Tempo válido para comparação
            categoria = atleta.calcular_categoria("11/11/2025")
            tempo = gerar_tempo_realista_10km(atleta.genero, categoria)
            dados_csv.append([atleta.cpf, tempo])
    
    nome_arquivo = 'resultados_erro_tempo_invalido.csv'
    caminho = _caminho_csv(nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(dados_csv)
    
    print(f"Arquivo CSV '{caminho}' gerado com {len(dados_csv)} linhas (9 com tempo inválido).")
    return caminho


def gerar_csv_erro_formato_invalido(atletas: list):
    """Gera CSV com formato inválido (menos colunas, mais colunas, etc)."""
    dados_csv = []
    
    # Linhas com formato incorreto
    dados_csv.append([atletas[0].cpf])  # Falta tempo
    dados_csv.append([atletas[1].cpf, '00:30:45', 'extra'])  # Coluna extra
    dados_csv.append([])  # Linha vazia
    dados_csv.append(['', '00:30:45'])  # CPF vazio
    dados_csv.append([atletas[2].cpf, gerar_tempo_realista_10km(atletas[2].genero, atletas[2].calcular_categoria("11/11/2025"))])  # Válido
    
    nome_arquivo = 'resultados_erro_formato_invalido.csv'
    caminho = _caminho_csv(nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(dados_csv)
    
    print(f"Arquivo CSV '{caminho}' gerado com {len(dados_csv)} linhas (formato inválido).")
    return caminho


def gerar_csv_erro_atleta_nao_inscrito(cursor, evento_id: int):
    """Gera CSV com atletas que existem no banco mas não estão inscritos no evento."""
    # Buscar atletas que não estão inscritos no evento
    cursor.execute("""
        SELECT u.* FROM usuarios u
        WHERE u.perfil = '1'
        AND u.cpf NOT IN (
            SELECT atleta_cpf FROM inscricoes WHERE evento_id = ?
        )
        LIMIT 10
    """, (evento_id,))
    
    atletas_nao_inscritos = cursor.fetchall()
    
    if not atletas_nao_inscritos:
        print("Não há atletas não inscritos para gerar CSV de erro.")
        return None
    
    dados_csv = []
    for usuario in atletas_nao_inscritos:
        try:
            atleta = Atleta(
                nome=usuario[1],
                cpf=usuario[0],
                email=usuario[2],
                senha_hash=usuario[3],
                data_nascimento=usuario[5],
                genero=usuario[6],
                pcd=bool(usuario[7])
            )
            categoria = atleta.calcular_categoria("11/11/2025")
            tempo = gerar_tempo_realista_10km(atleta.genero, categoria)
            dados_csv.append([atleta.cpf, tempo])
        except Exception as e:
            print(f"Erro ao processar atleta {usuario[0]}: {e}")
            continue
    
    nome_arquivo = 'resultados_erro_atleta_nao_inscrito.csv'
    caminho = _caminho_csv(nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(dados_csv)
    
    print(f"Arquivo CSV '{caminho}' gerado com {len(dados_csv)} linhas (atletas não inscritos).")
    return caminho


def gerar_csv_erro_multiplos_erros(atletas: list):
    """Gera CSV com múltiplos tipos de erros misturados."""
    
    dados_csv = []
    
    # Misturar diferentes tipos de erros
    dados_csv.append(['123456789', '00:30:45'])  # CPF inválido (curto)
    dados_csv.append([atletas[0].cpf, ''])  # Tempo não informado
    dados_csv.append([atletas[1].cpf, '25:70:30'])  # Tempo inválido
    dados_csv.append([gerar_cpf_valido(), '00:35:20'])  # Atleta não cadastrado
    dados_csv.append([atletas[2].cpf])  # Formato inválido (falta tempo)
    dados_csv.append(['00000000000', '00:40:15'])  # CPF inválido (todos zeros)
    dados_csv.append([atletas[3].cpf, 'abc:def:ghi'])  # Tempo não numérico
    dados_csv.append([atletas[4].cpf, '00:45:30'])  # Válido para comparação
    
    nome_arquivo = 'resultados_erro_multiplos_erros.csv'
    caminho = _caminho_csv(nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(dados_csv)
    
    print(f"Arquivo CSV '{caminho}' gerado com {len(dados_csv)} linhas (múltiplos erros).")
    return caminho


def main():
    """Função principal."""
    print("=" * 60)
    print("GERADOR DE EVENTO DE TESTE")
    print("=" * 60)
    
    conexao = None
    try:
        conexao = sqlite3.connect('banco.db')
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Garantir que organizador existe
        print("\n1. Verificando organizador...")
        garantir_organizador_existe(cursor)
        
        # 2. Obter atletas do banco
        print("\n2. Obtendo atletas do banco...")
        atletas_por_categoria = obter_atletas_por_categoria(cursor)
        
        total_atletas = sum(len(lista) for lista in atletas_por_categoria.values())
        print(f"   Total de atletas encontrados: {total_atletas}")
        for categoria, lista in atletas_por_categoria.items():
            print(f"   {categoria}: {len(lista)} atletas")
        
        if total_atletas < 30:
            print(f"\nERRO: Não há atletas suficientes no banco. Encontrados: {total_atletas}, Necessários: 30")
            print("Execute popula_banco.py primeiro para popular o banco com atletas.")
            return
        
        # 3. Selecionar 30 atletas mantendo proporção
        print("\n3. Selecionando 30 atletas...")
        atletas_selecionados = selecionar_atletas_proporcionais(atletas_por_categoria, 30)
        print(f"   {len(atletas_selecionados)} atletas selecionados")
        
        # 4. Criar evento
        print("\n4. Criando evento...")
        evento_id, kit_id = criar_evento(cursor)
        
        # 5. Criar inscrições
        print("\n5. Criando inscrições...")
        criar_inscricoes(cursor, evento_id, kit_id, atletas_selecionados)
        
        # 6. Gerar CSV válido
        print("\n6. Gerando arquivo CSV válido...")
        gerar_csv_resultados(atletas_selecionados, 'resultados_teste.csv')
        
        # 7. Gerar CSVs com erros para testes
        print("\n7. Gerando CSVs com erros para testes...")
        gerar_csv_erro_cpf_invalido(atletas_selecionados)
        gerar_csv_erro_atleta_nao_cadastrado()
        gerar_csv_erro_tempo_nao_informado(atletas_selecionados)
        gerar_csv_erro_tempo_invalido(atletas_selecionados)
        gerar_csv_erro_formato_invalido(atletas_selecionados)
        gerar_csv_erro_atleta_nao_inscrito(cursor, evento_id)
        gerar_csv_erro_multiplos_erros(atletas_selecionados)
        
        conexao.commit()
        print("\n" + "=" * 60)
        print("PROCESSO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"Evento ID: {evento_id}")
        print(f"\nArquivos CSV gerados:")
        print(f"  - resultados_teste.csv (válido)")
        print(f"  - resultados_erro_cpf_invalido.csv")
        print(f"  - resultados_erro_atleta_nao_cadastrado.csv")
        print(f"  - resultados_erro_tempo_nao_informado.csv")
        print(f"  - resultados_erro_tempo_invalido.csv")
        print(f"  - resultados_erro_formato_invalido.csv")
        print(f"  - resultados_erro_atleta_nao_inscrito.csv")
        print(f"  - resultados_erro_multiplos_erros.csv")
        print(f"\nTotal de inscrições: {len(atletas_selecionados)}")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()


if __name__ == "__main__":
    main()

