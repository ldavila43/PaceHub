# persistencia/resultado_dao.py
import sqlite3
from typing import List, Optional
from entidade.resultado import Resultado


class ResultadoDAO:
    def __init__(self, db_path='banco.db'):
        self.__db_path = db_path

    def __conectar(self):
        conexao = sqlite3.connect(self.__db_path)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    def salvar_resultado(self, resultado: Resultado) -> bool:
        """
        Salva um resultado no banco de dados.
        
        Args:
            resultado: Objeto Resultado para salvar
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            cursor.execute("""
                INSERT INTO Resultados 
                (evento_id, cpf_atleta, nome_atleta, genero_atleta, 
                 tempo_final, categoria, classificacao_geral, classificacao_categoria, pcd)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resultado.evento_id,
                resultado.cpf_atleta,
                resultado.nome_atleta,
                resultado.genero_atleta,
                resultado.tempo_final,
                resultado.categoria,
                resultado.classificacao_geral,
                resultado.classificacao_categoria,
                1 if resultado.pcd else 0
            ))
            
            resultado.id = cursor.lastrowid
            conexao.commit()
            return True
            
        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao salvar resultado: {e}")
            return False
        finally:
            if conexao:
                conexao.close()

    def salvar_lote_resultados(self, resultados: List[Resultado]) -> int:
        """
        Salva múltiplos resultados em uma única transação.
        
        Args:
            resultados: Lista de objetos Resultado
            
        Returns:
            Número de resultados salvos com sucesso
        """
        if not resultados:
            return 0
        
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            # Inserir resultados e obter IDs
            # SQLite não retorna lastrowid corretamente com executemany,
            # então inserimos um por um para obter os IDs
            for i, resultado in enumerate(resultados):
                cursor.execute("""
                    INSERT INTO Resultados 
                    (evento_id, cpf_atleta, nome_atleta, genero_atleta, 
                     tempo_final, categoria, classificacao_geral, classificacao_categoria, pcd)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    resultado.evento_id,
                    resultado.cpf_atleta,
                    resultado.nome_atleta,
                    resultado.genero_atleta,
                    resultado.tempo_final,
                    resultado.categoria,
                    resultado.classificacao_geral,
                    resultado.classificacao_categoria,
                    1 if resultado.pcd else 0
                ))
                resultado.id = cursor.lastrowid
            
            conexao.commit()
            return len(resultados)
            
        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao salvar lote de resultados: {e}")
            return 0
        finally:
            if conexao:
                conexao.close()

    def buscar_resultados_por_evento(self, evento_id: int) -> List[Resultado]:
        """
        Busca todos os resultados de um evento, ordenados por tempo.
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Lista de objetos Resultado ordenados por tempo
        """
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT * FROM Resultados 
                WHERE evento_id = ? 
                ORDER BY tempo_final ASC
            """, (evento_id,))
            
            rows = cursor.fetchall()
            resultados = []
            
            for row in rows:
                resultado = Resultado(
                    cpf_atleta=row['cpf_atleta'],
                    nome_atleta=row['nome_atleta'],
                    genero_atleta=row['genero_atleta'],
                    tempo_final=row['tempo_final'],
                    categoria=row['categoria'],
                    pcd=bool(row['pcd'])
                )
                resultado.id = row['id']
                resultado.evento_id = row['evento_id']
                resultado.classificacao_geral = row['classificacao_geral']
                resultado.classificacao_categoria = row['classificacao_categoria']
                resultados.append(resultado)
            
            return resultados
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar resultados por evento: {e}")
            return []
        finally:
            if conexao:
                conexao.close()

    def buscar_resultado_por_cpf(self, cpf: str, evento_id: int) -> Optional[Resultado]:
        """
        Busca um resultado específico por CPF e evento.
        
        Args:
            cpf: CPF do atleta
            evento_id: ID do evento
            
        Returns:
            Objeto Resultado se encontrado, None caso contrário
        """
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT * FROM Resultados 
                WHERE cpf_atleta = ? AND evento_id = ?
            """, (cpf, evento_id))
            
            row = cursor.fetchone()
            
            if row:
                resultado = Resultado(
                    cpf_atleta=row['cpf_atleta'],
                    nome_atleta=row['nome_atleta'],
                    genero_atleta=row['genero_atleta'],
                    tempo_final=row['tempo_final'],
                    categoria=row['categoria'],
                    pcd=bool(row['pcd'])
                )
                resultado.id = row['id']
                resultado.evento_id = row['evento_id']
                resultado.classificacao_geral = row['classificacao_geral']
                resultado.classificacao_categoria = row['classificacao_categoria']
                return resultado
            
            return None
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar resultado por CPF: {e}")
            return None
        finally:
            if conexao:
                conexao.close()

    def limpar_resultados_evento(self, evento_id: int) -> int:
        """
        Remove todos os resultados de um evento.
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Número de resultados removidos
        """
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            cursor.execute("DELETE FROM Resultados WHERE evento_id = ?", (evento_id,))
            
            removidos = cursor.rowcount
            conexao.commit()
            return removidos
            
        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao limpar resultados do evento: {e}")
            return 0
        finally:
            if conexao:
                conexao.close()

    def contar_resultados_evento(self, evento_id: int) -> int:
        """
        Conta quantos resultados existem para um evento.
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Número de resultados
        """
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM Resultados WHERE evento_id = ?", (evento_id,))
            
            count = cursor.fetchone()[0]
            return count
            
        except sqlite3.Error as e:
            print(f"Erro ao contar resultados: {e}")
            return 0
        finally:
            if conexao:
                conexao.close()

    def atualizar_resultado(self, resultado: Resultado) -> bool:
        """
        Atualiza um resultado existente no banco.
        
        Args:
            resultado: Objeto Resultado com dados atualizados
            
        Returns:
            True se atualizou com sucesso, False caso contrário
        """
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            cursor.execute("""
                UPDATE Resultados SET
                    nome_atleta = ?, genero_atleta = ?, tempo_final = ?,
                    categoria = ?, classificacao_geral = ?, classificacao_categoria = ?, pcd = ?
                WHERE id = ?
            """, (
                resultado.nome_atleta,
                resultado.genero_atleta,
                resultado.tempo_final,
                resultado.categoria,
                resultado.classificacao_geral,
                resultado.classificacao_categoria,
                1 if resultado.pcd else 0,
                resultado.id
            ))
            
            sucesso = cursor.rowcount > 0
            conexao.commit()
            return sucesso
            
        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao atualizar resultado: {e}")
            return False
        finally:
            if conexao:
                conexao.close()

    def deletar_resultado(self, resultado_id: int) -> bool:
        """
        Deleta um resultado do banco.
        
        Args:
            resultado_id: ID do resultado
            
        Returns:
            True se deletou com sucesso, False caso contrário
        """
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            cursor.execute("DELETE FROM Resultados WHERE id = ?", (resultado_id,))
            
            sucesso = cursor.rowcount > 0
            conexao.commit()
            return sucesso
            
        except sqlite3.Error as e:
            if conexao:
                conexao.rollback()
            print(f"Erro ao deletar resultado: {e}")
            return False
        finally:
            if conexao:
                conexao.close()

    def buscar_resultados_por_cpf_em_eventos_publicados(self, cpf: str) -> List[dict]:
        """
        Busca todos os resultados de um atleta em eventos com resultados publicados.
        
        Args:
            cpf: CPF do atleta
            
        Returns:
            Lista de dicionários com dados do resultado e nome do evento
        """
        conexao = None
        try:
            conexao = self.__conectar()
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT r.*, e.nome as evento_nome
                FROM Resultados r
                JOIN Eventos e ON r.evento_id = e.id
                WHERE r.cpf_atleta = ? AND e.resultados_publicados = 1
                ORDER BY e.data DESC
            """, (cpf,))
            
            rows = cursor.fetchall()
            resultados = []
            
            for row in rows:
                resultado_dict = {
                    'id': row['id'],
                    'evento_id': row['evento_id'],
                    'evento_nome': row['evento_nome'],
                    'cpf_atleta': row['cpf_atleta'],
                    'nome_atleta': row['nome_atleta'],
                    'genero_atleta': row['genero_atleta'],
                    'tempo_final': row['tempo_final'],
                    'categoria': row['categoria'],
                    'classificacao_geral': row['classificacao_geral'],
                    'classificacao_categoria': row['classificacao_categoria'],
                    'pcd': bool(row['pcd'])
                }
                resultados.append(resultado_dict)
            
            return resultados
            
        except sqlite3.Error as e:
            print(f"Erro ao buscar resultados por CPF em eventos publicados: {e}")
            return []
        finally:
            if conexao:
                conexao.close()

