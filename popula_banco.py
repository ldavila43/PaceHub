import sqlite3
import bcrypt
from datetime import datetime

# Script gerador de evento, inscrições e CSV de resultados válidos
import gerar_evento_teste


STATUS_PENDENTE = 1
STATUS_PAGA = 3

# Senha padrão para todos os atletas de teste: "senha123"
SENHA_HASH_PADRAO = bcrypt.hashpw('senha123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def limpar_tabelas(cursor):
    """Limpa as tabelas na ordem correta (respeitando chaves estrangeiras)."""
    print("Limpando tabelas existentes...")
    try:
        cursor.execute("DELETE FROM Resultados;")
        cursor.execute("DELETE FROM FichasMedicas;")
        cursor.execute("DELETE FROM inscricoes;")
        cursor.execute("DELETE FROM KitsDeCorrida;")
        cursor.execute("DELETE FROM Eventos;")
        cursor.execute("DELETE FROM usuarios;")
        print("Tabelas limpas com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao limpar tabelas: {e}")
        raise


def popular_usuarios(cursor):
    """Popula a tabela 'usuarios' com seus dados."""
    dados_usuarios = [
        # Organizador
        ('12671115938', 'Lucas Dutra de Ávila', 'lucas@gmail.com',
         '$2b$12$UG3pOfSFPWBlC8..bQJj/.KNJpf5Gz4x/5UL1Z3iPfXWN159oewbe', '0', None, None, None),
        # Atletas existentes
        ('90869210009', 'pedro', 'pedro@gmail.com', '$2b$12$Uam7cGVgCZwE7IsdxDTRBOxK8hmPvnlBJNTSnwKjwhKgrWS6AtqAa', '1',
         '1990-06-21', 'Masculino', 0),
        ('93061326030', 'Ruan', 'ruan@gmail.com', '$2b$12$8HzUdli/sypVopzMXe7Qjupq81iXJyzebn3eRAtksNslKfzE0DBOO', '1',
         '1980-08-05', 'Masculino', 0),
        ('07998448962', 'Gustavo', 'gustavo@gmail.com', SENHA_HASH_PADRAO, '0', None, None, None),
        
        # Júnior Masculino (15 atletas) - nascidos entre 2006-2008
        ('79913284147', 'Lucas Ferraz', 'lucas.ferraz@email.com', SENHA_HASH_PADRAO, '1', '2008-03-15', 'Masculino', 0),
        ('21335157557', 'Pedro Santos', 'pedro.santos@email.com', SENHA_HASH_PADRAO, '1', '2007-07-22', 'Masculino', 0),
        ('70929952561', 'Gabriel Oliveira', 'gabriel.oliveira@email.com', SENHA_HASH_PADRAO, '1', '2006-12-10', 'Masculino', 0),
        ('32027879773', 'Rafael Costa', 'rafael.costa@email.com', SENHA_HASH_PADRAO, '1', '2008-05-05', 'Masculino', 0),
        ('06115197554', 'Felipe Silva', 'felipe.silva@email.com', SENHA_HASH_PADRAO, '1', '2007-09-18', 'Masculino', 0),
        ('99186211846', 'Bruno Lima', 'bruno.lima@email.com', SENHA_HASH_PADRAO, '1', '2006-01-03', 'Masculino', 0),
        ('59777936508', 'Diego Souza', 'diego.souza@email.com', SENHA_HASH_PADRAO, '1', '2008-11-28', 'Masculino', 0),
        ('83426068729', 'Thiago Alves', 'thiago.alves@email.com', SENHA_HASH_PADRAO, '1', '2007-06-14', 'Masculino', 0),
        ('55365286960', 'Marcos Pereira', 'marcos.pereira@email.com', SENHA_HASH_PADRAO, '1', '2006-04-07', 'Masculino', 0),
        ('95471933095', 'André Rocha', 'andre.rocha@email.com', SENHA_HASH_PADRAO, '1', '2008-08-25', 'Masculino', 0),
        ('60926359681', 'Carlos Mendes', 'carlos.mendes@email.com', SENHA_HASH_PADRAO, '1', '2007-02-12', 'Masculino', 0),
        ('92774726778', 'João Pedro', 'joao.pedro@email.com', SENHA_HASH_PADRAO, '1', '2006-10-19', 'Masculino', 0),
        ('45972018667', 'Vitor Hugo', 'vitor.hugo@email.com', SENHA_HASH_PADRAO, '1', '2008-12-31', 'Masculino', 0),
        ('79123533137', 'Eduardo Nunes', 'eduardo.nunes@email.com', SENHA_HASH_PADRAO, '1', '2007-07-16', 'Masculino', 0),
        ('04788874776', 'Henrique Dias', 'henrique.dias@email.com', SENHA_HASH_PADRAO, '1', '2006-03-08', 'Masculino', 0),
        
        # Júnior Feminino (15 atletas)
        ('69005296232', 'Clara Martins', 'clara.martins@email.com', SENHA_HASH_PADRAO, '1', '2008-04-20', 'Feminino', 0),
        ('59813787600', 'Ana Beatriz', 'ana.beatriz@email.com', SENHA_HASH_PADRAO, '1', '2007-08-13', 'Feminino', 0),
        ('86440596454', 'Maria Eduarda', 'maria.eduarda@email.com', SENHA_HASH_PADRAO, '1', '2006-11-27', 'Feminino', 0),
        ('21128605007', 'Larissa Silva', 'larissa.silva@email.com', SENHA_HASH_PADRAO, '1', '2008-06-09', 'Feminino', 0),
        ('45421174565', 'Beatriz Costa', 'beatriz.costa@email.com', SENHA_HASH_PADRAO, '1', '2007-01-15', 'Feminino', 0),
        ('42224856598', 'Isabella Santos', 'isabella.santos@email.com', SENHA_HASH_PADRAO, '1', '2006-09-03', 'Feminino', 0),
        ('51275590993', 'Gabriela Lima', 'gabriela.lima@email.com', SENHA_HASH_PADRAO, '1', '2008-05-22', 'Feminino', 0),
        ('94732872247', 'Camila Souza', 'camila.souza@email.com', SENHA_HASH_PADRAO, '1', '2007-12-11', 'Feminino', 0),
        ('68168731735', 'Julia Oliveira', 'julia.oliveira@email.com', SENHA_HASH_PADRAO, '1', '2006-07-28', 'Feminino', 0),
        ('85915538886', 'Livia Alves', 'livia.alves@email.com', SENHA_HASH_PADRAO, '1', '2008-03-06', 'Feminino', 0),
        ('29380453876', 'Sophia Pereira', 'sophia.pereira@email.com', SENHA_HASH_PADRAO, '1', '2007-10-19', 'Feminino', 0),
        ('69934226626', 'Valentina Rocha', 'valentina.rocha@email.com', SENHA_HASH_PADRAO, '1', '2006-08-14', 'Feminino', 0),
        ('79372378801', 'Helena Mendes', 'helena.mendes@email.com', SENHA_HASH_PADRAO, '1', '2008-04-25', 'Feminino', 0),
        ('04539948229', 'Alice Dias', 'alice.dias@email.com', SENHA_HASH_PADRAO, '1', '2007-11-17', 'Feminino', 0),
        ('02560278979', 'Laura Nunes', 'laura.nunes@email.com', SENHA_HASH_PADRAO, '1', '2006-06-02', 'Feminino', 0),
        
        # Adulto Masculino (15 atletas) - nascidos entre 1976-2005
        ('58093825843', 'Fernando Gomes', 'fernando.gomes@email.com', SENHA_HASH_PADRAO, '1', '1990-03-15', 'Masculino', 0),
        ('99296696712', 'Thiago Nunes', 'thiago.nunes@email.com', SENHA_HASH_PADRAO, '1', '1985-07-22', 'Masculino', 0),
        ('98296125200', 'Ricardo Lima', 'ricardo.lima@email.com', SENHA_HASH_PADRAO, '1', '1992-12-10', 'Masculino', 0),
        ('12143711409', 'Paulo Costa', 'paulo.costa@email.com', SENHA_HASH_PADRAO, '1', '1988-05-05', 'Masculino', 0),
        ('13892988250', 'Roberto Silva', 'roberto.silva@email.com', SENHA_HASH_PADRAO, '1', '1995-09-18', 'Masculino', 0),
        ('65171197954', 'Marcelo Santos', 'marcelo.santos@email.com', SENHA_HASH_PADRAO, '1', '1987-01-03', 'Masculino', 0),
        ('66859927941', 'Antonio Souza', 'antonio.souza@email.com', SENHA_HASH_PADRAO, '1', '1993-11-28', 'Masculino', 0),
        ('32038118809', 'José Pereira', 'jose.pereira@email.com', SENHA_HASH_PADRAO, '1', '1989-06-14', 'Masculino', 0),
        ('52229053574', 'Carlos Andrade', 'carlos.andrade@email.com', SENHA_HASH_PADRAO, '1', '1991-04-07', 'Masculino', 0),
        ('53444997361', 'João Silva', 'joao.silva@email.com', SENHA_HASH_PADRAO, '1', '1986-08-25', 'Masculino', 0),
        ('00153991763', 'Francisco Mendes', 'francisco.mendes@email.com', SENHA_HASH_PADRAO, '1', '1994-02-12', 'Masculino', 0),
        ('71754994695', 'Manuel Dias', 'manuel.dias@email.com', SENHA_HASH_PADRAO, '1', '1988-10-19', 'Masculino', 0),
        ('17825000145', 'Sebastião Rocha', 'sebastiao.rocha@email.com', SENHA_HASH_PADRAO, '1', '1992-12-31', 'Masculino', 0),
        ('77008711409', 'Raimundo Alves', 'raimundo.alves@email.com', SENHA_HASH_PADRAO, '1', '1987-07-16', 'Masculino', 0),
        ('54811083130', 'Pedro Henrique', 'pedro.henrique@email.com', SENHA_HASH_PADRAO, '1', '1990-03-08', 'Masculino', 0),
        
        # Adulto Feminino (15 atletas)
        ('07299596008', 'Ana Beatriz', 'ana.beatriz.adulto@email.com', SENHA_HASH_PADRAO, '1', '1990-04-20', 'Feminino', 0),
        ('38125865926', 'Carla Dias', 'carla.dias@email.com', SENHA_HASH_PADRAO, '1', '1985-08-13', 'Feminino', 0),
        ('40870626272', 'Mariana Silva', 'mariana.silva@email.com', SENHA_HASH_PADRAO, '1', '1992-11-27', 'Feminino', 0),
        ('12883062889', 'Patricia Costa', 'patricia.costa@email.com', SENHA_HASH_PADRAO, '1', '1988-06-09', 'Feminino', 0),
        ('69967538139', 'Juliana Santos', 'juliana.santos@email.com', SENHA_HASH_PADRAO, '1', '1995-01-15', 'Feminino', 0),
        ('47716336576', 'Fernanda Lima', 'fernanda.lima@email.com', SENHA_HASH_PADRAO, '1', '1987-09-03', 'Feminino', 0),
        ('36836498017', 'Cristina Souza', 'cristina.souza@email.com', SENHA_HASH_PADRAO, '1', '1993-05-22', 'Feminino', 0),
        ('05274785557', 'Sandra Oliveira', 'sandra.oliveira@email.com', SENHA_HASH_PADRAO, '1', '1989-12-11', 'Feminino', 0),
        ('41044566248', 'Denise Alves', 'denise.alves@email.com', SENHA_HASH_PADRAO, '1', '1991-07-28', 'Feminino', 0),
        ('61220218227', 'Monica Pereira', 'monica.pereira@email.com', SENHA_HASH_PADRAO, '1', '1986-03-06', 'Feminino', 0),
        ('79950333466', 'Adriana Rocha', 'adriana.rocha@email.com', SENHA_HASH_PADRAO, '1', '1994-10-19', 'Feminino', 0),
        ('73054633020', 'Silvia Mendes', 'silvia.mendes@email.com', SENHA_HASH_PADRAO, '1', '1988-08-14', 'Feminino', 0),
        ('45329022401', 'Regina Dias', 'regina.dias@email.com', SENHA_HASH_PADRAO, '1', '1992-04-25', 'Feminino', 0),
        ('29465745120', 'Eliane Nunes', 'eliane.nunes@email.com', SENHA_HASH_PADRAO, '1', '1987-11-17', 'Feminino', 0),
        ('87002242946', 'Rosana Gomes', 'rosana.gomes@email.com', SENHA_HASH_PADRAO, '1', '1990-06-02', 'Feminino', 0),
        
        # Master Masculino (8 atletas) - nascidos antes de 1976
        ('76199465784', 'Roberto Assis', 'roberto.assis@email.com', SENHA_HASH_PADRAO, '1', '1970-03-15', 'Masculino', 0),
        ('70308601017', 'Jose Carlos', 'jose.carlos@email.com', SENHA_HASH_PADRAO, '1', '1965-07-22', 'Masculino', 0),
        ('77128514090', 'Antonio Silva', 'antonio.silva.master@email.com', SENHA_HASH_PADRAO, '1', '1972-12-10', 'Masculino', 0),
        ('89010920690', 'Francisco Costa', 'francisco.costa@email.com', SENHA_HASH_PADRAO, '1', '1968-05-05', 'Masculino', 0),
        ('32172502901', 'Manuel Santos', 'manuel.santos@email.com', SENHA_HASH_PADRAO, '1', '1975-09-18', 'Masculino', 0),
        ('19095687163', 'Sebastião Lima', 'sebastiao.lima@email.com', SENHA_HASH_PADRAO, '1', '1967-01-03', 'Masculino', 0),
        ('32921413116', 'Raimundo Souza', 'raimundo.souza@email.com', SENHA_HASH_PADRAO, '1', '1973-11-28', 'Masculino', 0),
        ('72713408822', 'Pedro Oliveira', 'pedro.oliveira@email.com', SENHA_HASH_PADRAO, '1', '1969-06-14', 'Masculino', 0),
        
        # Master Feminino (8 atletas)
        ('55440179216', 'Sônia Braga', 'sonia.braga@email.com', SENHA_HASH_PADRAO, '1', '1970-04-20', 'Feminino', 0),
        ('67889584911', 'Maria Silva', 'maria.silva.master@email.com', SENHA_HASH_PADRAO, '1', '1965-08-13', 'Feminino', 0),
        ('72657019412', 'Ana Costa', 'ana.costa.master@email.com', SENHA_HASH_PADRAO, '1', '1972-11-27', 'Feminino', 0),
        ('07184000030', 'Lucia Santos', 'lucia.santos@email.com', SENHA_HASH_PADRAO, '1', '1968-06-09', 'Feminino', 0),
        ('90977046001', 'Rosa Lima', 'rosa.lima@email.com', SENHA_HASH_PADRAO, '1', '1975-01-15', 'Feminino', 0),
        ('27679072230', 'Teresa Souza', 'teresa.souza@email.com', SENHA_HASH_PADRAO, '1', '1967-09-03', 'Feminino', 0),
        ('88479545097', 'Carmen Oliveira', 'carmen.oliveira@email.com', SENHA_HASH_PADRAO, '1', '1973-05-22', 'Feminino', 0),
        ('02366018738', 'Isabel Alves', 'isabel.alves@email.com', SENHA_HASH_PADRAO, '1', '1969-12-11', 'Feminino', 0),
        
        # PCD Masculino (2 atletas)
        ('12799110932', 'João Silva PCD', 'joao.silva.pcd@email.com', SENHA_HASH_PADRAO, '1', '1985-03-15', 'Masculino', 1),
        ('45241254340', 'Pedro Santos PCD', 'pedro.santos.pcd@email.com', SENHA_HASH_PADRAO, '1', '1990-07-22', 'Masculino', 1),
        
        # PCD Feminino (2 atletas)
        ('00507469011', 'Maria Oliveira PCD', 'maria.oliveira.pcd@email.com', SENHA_HASH_PADRAO, '1', '1988-04-20', 'Feminino', 1),
        ('16571495287', 'Ana Costa PCD', 'ana.costa.pcd@email.com', SENHA_HASH_PADRAO, '1', '1992-08-13', 'Feminino', 1),
    ]

    sql = """
    INSERT INTO usuarios 
    (cpf, nome, email, senha_hash, perfil, data_nascimento, genero, pcd)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    cursor.executemany(sql, dados_usuarios)
    print(f"{cursor.rowcount} usuários inseridos.")


def popular_eventos(cursor):
    """Popula a tabela 'Eventos' com seus dados."""
    dados_eventos = [
        (1, 'corrida oficial de teste', '16/12/2025', 5, 'Av. Beira Mar Norte', '6:0', '12/11/2025', '12671115938'),
        (2, 'corrida numero 2', '30/01/2026', 10, 'Rua', '6:0', '21/11/2025', '12671115938'),
        (3, 'evento para teste 3', '12/08/2026', 42, 'Rua 3', '6:0', '24/12/2025', '12671115938')
    ]

    sql = """
    INSERT INTO Eventos
    (id, nome, data, distancia, local_largada, tempo_corte, data_limite_cred, organizador_cpf)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    cursor.executemany(sql, dados_eventos)
    print(f"{cursor.rowcount} eventos inseridos.")


def popular_kits(cursor):
    """Popula a tabela 'KitsDeCorrida' com seus dados."""
    dados_kits = [
        (1, 'kit de teste', 'este kit contem:\n1 camiseta\n1 garrafa', 15.0, 1),
        (2, 'kit de teste casal', 'Este kit contem:\n2 camisetas', 25.0, 1),
        (3, 'sdasfr', 'asfdd', 45.0, 2),
        (4, 'sqrgherthb', '12341', 90.0, 2),
        (5, 'e235rfdc', '12323', 67.0, 2),
        (6, 's3er', '2ewrefd', 23.0, 3),
        (7, '12312', '41324dsfd', 12.0, 3)
    ]

    sql = """
    INSERT INTO KitsDeCorrida
    (id, nome, descricao, valor, evento_id)
    VALUES (?, ?, ?, ?, ?);
    """

    cursor.executemany(sql, dados_kits)
    print(f"{cursor.rowcount} kits inseridos.")


def popular_inscricoes(cursor):
    """Popula a tabela 'inscricoes' com dados de teste."""

    data_agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    dados_inscricoes = [
        (data_agora, 0, STATUS_PAGA, '90869210009', 1, 1),
        (data_agora, 1, STATUS_PAGA, '93061326030', 1, 2),
        (data_agora, 0, STATUS_PENDENTE, '64590032031', 2, 3),
        (data_agora, 0, STATUS_PAGA, '90869210009', 3, 6)
    ]

    # --- CORREÇÃO AQUI ---
    sql = """
    INSERT INTO inscricoes 
    (data_inscricao, kit_entregue, status, atleta_cpf, evento_id, kit_id)
    VALUES (?, ?, ?, ?, ?, ?);
    """

    cursor.executemany(sql, dados_inscricoes)
    print(f"{cursor.rowcount} inscrições inseridas.")


def popular_banco():
    conexao = None
    try:
        conexao = sqlite3.connect('banco.db')
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        limpar_tabelas(cursor)
        popular_usuarios(cursor)
        popular_eventos(cursor)
        popular_kits(cursor)
        popular_inscricoes(cursor)

        # Persistir dados básicos antes de gerar evento/CSV de teste
        conexao.commit()

        # Gerar evento de teste, inscrições e CSV de resultados válidos
        print("\n--- GERANDO EVENTO DE TESTE E CSV DE RESULTADOS ---")
        gerar_evento_teste.main()

        print("\n--- BANCO POPULADO COM SUCESSO! ---")

    except sqlite3.Error as e:
        print(f"\n--- OCORREU UM ERRO ---")
        print(f"Erro: {e}")
        if conexao:
            print("Revertendo transações (rollback)...")
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()

if __name__ == "__main__":
    popular_banco()