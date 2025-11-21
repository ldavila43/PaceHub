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
    cursor.execute(sql_resultados)
    print('Tabela "Resultados" criada com sucesso (ou já existia)!')
    
    # Criar índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resultados_evento ON Resultados(evento_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resultados_cpf ON Resultados(cpf_atleta);")
    print('Índices da tabela "Resultados" criados com sucesso!')
except Exception as e:
    print(f"Erro ao criar tabela Resultados: {e}")

conexao.close()