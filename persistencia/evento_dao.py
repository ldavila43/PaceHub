# persistencia/evento_dao.py
import sqlite3
from entidade.evento import Evento
from entidade.kit_de_corrida import KitDeCorrida


class EventoDAO:

    def __init__(self, db_path='banco.db'):
        self.__db_path = db_path

    def __conectar(self):
        return sqlite3.connect(self.__db_path)

    def add_evento(self, evento: Evento):
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()

            dados_evento = (
                evento.nome,
                evento.data,
                evento.distancia,
                evento.local_largada,
                evento.tempo_corte,
                evento.data_limite_cred,
                evento.organizador_cpf
            )

            sql_evento = """
            INSERT INTO Eventos 
            (nome, data, distancia, local_largada, tempo_corte, data_limite_cred, organizador_cpf)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(sql_evento, dados_evento)

            evento_id = cursor.lastrowid

            if evento.kits:
                sql_kit = """
                INSERT INTO KitsDeCorrida (nome, descricao, valor, evento_id)
                VALUES (?, ?, ?, ?);
                """
                dados_kits = []
                for kit in evento.kits:
                    dados_kits.append((kit.nome, kit.descricao, kit.valor, evento_id))

                cursor.executemany(sql_kit, dados_kits)

            conexao.commit()
            print(f"Evento {evento.nome} e {len(evento.kits)} kits salvos com ID {evento_id}.")

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao salvar evento no SQLite: {e}")
            raise e

        finally:
            if conexao:
                conexao.close()

    def get_all_by_organizador(self, organizador_cpf: str):
        conexao = None
        eventos_objs = []
        try:
            conexao = self.__conectar()
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()

            sql = "SELECT * FROM Eventos WHERE organizador_cpf = ?;"
            cursor.execute(sql, (organizador_cpf,))

            lista_dados = cursor.fetchall()

            for dados in lista_dados:
                evento = Evento(
                    nome=dados['nome'],
                    data=dados['data'],
                    distancia=dados['distancia'],
                    local_largada=dados['local_largada'],
                    tempo_corte=dados['tempo_corte'],
                    data_limite_cred=dados['data_limite_cred'],
                    organizador_cpf=dados['organizador_cpf']
                )
                evento.id = dados['id']
                eventos_objs.append(evento)

            return eventos_objs

        except sqlite3.Error as e:
            print(f"Erro ao buscar eventos: {e}")
            return []
        finally:
            if conexao:
                conexao.close()

    def get_by_id(self, evento_id: int):
        """Busca um evento por ID."""
        conexao = None
        try:
            conexao = self.__conectar()
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()

            sql = "SELECT * FROM Eventos WHERE id = ?;"
            cursor.execute(sql, (evento_id,))

            dados = cursor.fetchone()

            if dados:
                evento = Evento(
                    nome=dados['nome'],
                    data=dados['data'],
                    distancia=dados['distancia'],
                    local_largada=dados['local_largada'],
                    tempo_corte=dados['tempo_corte'],
                    data_limite_cred=dados['data_limite_cred'],
                    organizador_cpf=dados['organizador_cpf']
                )
                evento.id = dados['id']
                return evento

            return None

        except sqlite3.Error as e:
            print(f"Erro ao buscar evento: {e}")
            return None
        finally:
            if conexao:
                conexao.close()

    def get_kits_by_evento_id(self, evento_id: int):
        """Busca todos os kits associados a um ID de evento."""
        conexao = None
        kits_objs = []
        try:
            conexao = self.__conectar()
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()

            sql = "SELECT * FROM KitsDeCorrida WHERE evento_id = ?;"
            cursor.execute(sql, (evento_id,))

            lista_dados = cursor.fetchall()

            for dados in lista_dados:
                kit = KitDeCorrida(
                    nome=dados['nome'],
                    descricao=dados['descricao'],
                    valor=dados['valor']
                )
                kit.id = dados['id']
                kits_objs.append(kit)

            return kits_objs

        except sqlite3.Error as e:
            print(f"Erro ao buscar kits: {e}")
            return []
        finally:
            if conexao:
                conexao.close()

    def update_evento(self, evento: Evento):
        """Atualiza um evento existente e seus kits no banco."""
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            conexao.execute("BEGIN TRANSACTION;")

            dados_evento = (
                evento.nome,
                evento.data,
                evento.distancia,
                evento.local_largada,
                evento.tempo_corte,
                evento.data_limite_cred,
                evento.organizador_cpf,
                evento.id  
            )
            sql_evento = """
            UPDATE Eventos SET
                nome = ?,
                data = ?,
                distancia = ?,
                local_largada = ?,
                tempo_corte = ?,
                data_limite_cred = ?,
                organizador_cpf = ?
            WHERE id = ?;
            """
            cursor.execute(sql_evento, dados_evento)

            cursor.execute("DELETE FROM KitsDeCorrida WHERE evento_id = ?;", (evento.id,))

            if evento.kits:
                sql_kit = """
                INSERT INTO KitsDeCorrida (nome, descricao, valor, evento_id)
                VALUES (?, ?, ?, ?);
                """
                dados_kits = []
                for kit in evento.kits:
                    dados_kits.append((kit.nome, kit.descricao, kit.valor, evento.id))
                
                cursor.executemany(sql_kit, dados_kits)
            
            conexao.commit()
            print(f"Evento ID {evento.id} e {len(evento.kits)} kits atualizados.")

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback() 
            print(f"Erro ao atualizar evento no SQLite: {e}")
            raise e
        finally:
            if conexao:
                conexao.close()