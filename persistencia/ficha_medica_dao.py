# persistencia/ficha_medica_dao.py
import sqlite3
from entidade.ficha_medica import FichaMedica


class FichaMedicaDAO:
    def __init__(self, db_path='banco.db'):
        self.__db_path = db_path

    def __conectar(self):
        return sqlite3.connect(self.__db_path)

    def add(self, ficha_medica: FichaMedica):
        """Adiciona uma nova ficha médica ao banco de dados."""
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()

            dados = (
                ficha_medica.inscricao_id,
                int(ficha_medica.preenchida),
                ficha_medica.pergunta1,
                ficha_medica.pergunta2,
                ficha_medica.pergunta3,
                ficha_medica.pergunta4,
                ficha_medica.pergunta5,
                ficha_medica.pergunta6,
                ficha_medica.pergunta7,
                int(ficha_medica.declaracao_saude)
            )

            sql = """
            INSERT INTO FichasMedicas
            (inscricao_id, preenchida, pergunta1, pergunta2, pergunta3, pergunta4, 
             pergunta5, pergunta6, pergunta7, declaracao_saude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            cursor.execute(sql, dados)
            ficha_medica.id = cursor.lastrowid

            conexao.commit()
            print(f"Ficha médica ID {ficha_medica.id} salva para inscrição {ficha_medica.inscricao_id}")
            return ficha_medica.id

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao salvar ficha médica: {e}")
            raise e
        finally:
            if conexao:
                conexao.close()

    def get_by_inscricao_id(self, inscricao_id: int):
        """Busca uma ficha médica pelo ID da inscrição."""
        conexao = None
        try:
            conexao = self.__conectar()
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()

            sql = "SELECT * FROM FichasMedicas WHERE inscricao_id = ?;"
            cursor.execute(sql, (inscricao_id,))

            dados = cursor.fetchone()

            if dados:
                ficha_medica = FichaMedica(
                    inscricao_id=dados['inscricao_id'],
                    preenchida=bool(dados['preenchida']),
                    pergunta1=dados['pergunta1'],
                    pergunta2=dados['pergunta2'],
                    pergunta3=dados['pergunta3'],
                    pergunta4=dados['pergunta4'],
                    pergunta5=dados['pergunta5'],
                    pergunta6=dados['pergunta6'],
                    pergunta7=dados['pergunta7'],
                    declaracao_saude=bool(dados['declaracao_saude'])
                )
                ficha_medica.id = dados['id']
                return ficha_medica
            return None

        except sqlite3.Error as e:
            print(f"Erro ao buscar ficha médica: {e}")
            return None
        finally:
            if conexao:
                conexao.close()

    def update_preenchida(self, ficha_medica_id: int, preenchida: bool):
        """Atualiza o status de preenchida da ficha médica."""
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()

            sql = "UPDATE FichasMedicas SET preenchida = ? WHERE id = ?;"
            cursor.execute(sql, (int(preenchida), ficha_medica_id))

            conexao.commit()
            print(f"Status de preenchida da ficha médica ID {ficha_medica_id} atualizado.")

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao atualizar ficha médica: {e}")
        finally:
            if conexao:
                conexao.close()

    def update(self, ficha_medica: FichaMedica):
        """Atualiza uma ficha médica completa no banco."""
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()

            sql = """
            UPDATE FichasMedicas 
            SET preenchida = ?, pergunta1 = ?, pergunta2 = ?, pergunta3 = ?,
                pergunta4 = ?, pergunta5 = ?, pergunta6 = ?, pergunta7 = ?,
                declaracao_saude = ?
            WHERE id = ?;
            """
            cursor.execute(sql, (
                int(ficha_medica.preenchida),
                ficha_medica.pergunta1,
                ficha_medica.pergunta2,
                ficha_medica.pergunta3,
                ficha_medica.pergunta4,
                ficha_medica.pergunta5,
                ficha_medica.pergunta6,
                ficha_medica.pergunta7,
                int(ficha_medica.declaracao_saude),
                ficha_medica.id
            ))

            conexao.commit()
            print(f"Ficha médica ID {ficha_medica.id} atualizada.")

        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao atualizar ficha médica: {e}")
            raise e
        finally:
            if conexao:
                conexao.close()

