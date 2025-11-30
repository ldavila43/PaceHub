import sqlite3

conexao = sqlite3.connect('banco.db')

cursor = conexao.cursor()

sql_usuarios = """
    CREATE TABLE IF NOT EXISTS usuarios (
        cpf TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        senha_hash TEXT NOT NULL,
        perfil TEXT NOT NULL,
        data_nascimento TEXT,
        genero TEXT,
        pcd INTEGER
    );
    """

sql_eventos = """
            CREATE TABLE IF NOT EXISTS Eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data TEXT NOT NULL,
                distancia INTEGER NOT NULL,
                local_largada TEXT,
                tempo_corte TEXT,
                data_limite_cred TEXT,
                organizador_cpf TEXT NOT NULL,
                resultados_publicados INTEGER DEFAULT 0,
                FOREIGN KEY (organizador_cpf) REFERENCES usuarios (cpf)
            );"""

sql_kits = """
            CREATE TABLE IF NOT EXISTS KitsDeCorrida (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                valor REAL NOT NULL,
                evento_id INTEGER NOT NULL,
                FOREIGN KEY (evento_id) REFERENCES Eventos (id)
            );"""

sql_inscricao = """
            CREATE TABLE IF NOT EXISTS Inscricoes (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            data_inscricao text not null,
            kit_entregue INTEGER NOT NULL DEFAULT 0,
            status INTEGER NOT NULL,
            -- FKS
            atleta_cpf TEXT NOT NULL,
            evento_id INTEGER NOT NULL,
            kit_id INTEGER NOT NULL,
            FOREIGN KEY (atleta_cpf) REFERENCES usuarios (cpf),
            FOREIGN KEY (evento_id) REFERENCES Eventos (id),
            FOREIGN KEY (kit_id) REFERENCES KitsDeCorrida (id)
            );
            """

sql_fichas_medicas = """
            CREATE TABLE IF NOT EXISTS FichasMedicas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inscricao_id INTEGER NOT NULL UNIQUE,
                preenchida INTEGER NOT NULL DEFAULT 0,
                pergunta1 INTEGER,
                pergunta2 INTEGER,
                pergunta3 INTEGER,
                pergunta4 INTEGER,
                pergunta5 INTEGER,
                pergunta6 INTEGER,
                pergunta7 INTEGER,
                declaracao_saude INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (inscricao_id) REFERENCES Inscricoes(ID) ON DELETE CASCADE
            );
            """

sql_resultados = """
            CREATE TABLE IF NOT EXISTS Resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evento_id INTEGER NOT NULL,
                cpf_atleta TEXT NOT NULL,
                nome_atleta TEXT NOT NULL,
                genero_atleta TEXT NOT NULL,
                tempo_final TEXT NOT NULL,
                categoria TEXT NOT NULL,
                classificacao_geral INTEGER,
                classificacao_categoria INTEGER,
                pcd INTEGER DEFAULT 0,
                FOREIGN KEY (evento_id) REFERENCES Eventos(id) ON DELETE CASCADE
            );
            """

try:
    cursor.execute(sql_usuarios)
    print('Tabela "usuarios" criada com sucesso (ou já existia)!')
except Exception as e:
    print(f"Erro ao criar tabela usuarios: {e}")

try:
    cursor.execute(sql_eventos)
    print('Tabela "Eventos" criada com sucesso (ou já existia)!')
except Exception as e:
    print(f"Erro ao criar tabela Eventos: {e}")

try:
    cursor.execute(sql_kits)
    print('Tabela "KitsDeCorrida" criada com sucesso (ou já existia)!')
except Exception as e:
    print(f"Erro ao criar tabela KitsDeCorrida: {e}")

try:
    cursor.execute(sql_inscricao)
    print('Tabela "Inscirções" criada com sucesso (ou já existia)!')
except Exception as e:
    print(f"Erro ao criar tabela Inscrições: {e}")

try:
    cursor.execute(sql_fichas_medicas)
    print('Tabela "FichasMedicas" criada com sucesso (ou já existia)!')
except Exception as e:
    print(f"Erro ao criar tabela FichasMedicas: {e}")

try:
    cursor.execute(sql_resultados)
    print('Tabela "Resultados" criada com sucesso (ou já existia)!')
    
    # Criar índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resultados_evento ON Resultados(evento_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resultados_cpf ON Resultados(cpf_atleta);")
    print('Índices da tabela "Resultados" criados com sucesso!')
except Exception as e:
    print(f"Erro ao criar tabela Resultados: {e}")

# Migração: Adicionar coluna resultados_publicados se não existir
try:
    cursor.execute("PRAGMA table_info(Eventos)")
    colunas = [row[1] for row in cursor.fetchall()]
    if 'resultados_publicados' not in colunas:
        cursor.execute("ALTER TABLE Eventos ADD COLUMN resultados_publicados INTEGER DEFAULT 0;")
        conexao.commit()
        print('Coluna "resultados_publicados" adicionada à tabela Eventos!')
except Exception as e:
    print(f"Erro ao adicionar coluna resultados_publicados: {e}")

# Migração: Criar tabela FichasMedicas se não existir (para bancos antigos)
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='FichasMedicas';")
    if not cursor.fetchone():
        cursor.execute(sql_fichas_medicas)
        conexao.commit()
        print('Tabela "FichasMedicas" criada via migração!')
except Exception as e:
    print(f"Erro ao criar tabela FichasMedicas via migração: {e}")

conexao.commit()
conexao.close()