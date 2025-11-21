# controle/controlador_importacao.py
import csv
import os
import re
from typing import List, Tuple, Dict, Any, Optional
from entidade.resultado import Resultado, criar_resultado_para_atleta, ordenar_resultados_por_tempo, separar_resultados_por_genero
from entidade.atleta import Atleta
from persistencia.resultado_dao import ResultadoDAO
from persistencia.inscricao_dao import InscricaoDAO
from persistencia.usuario_dao import UsuarioDAO
from persistencia.evento_dao import EventoDAO


class ControladorImportacao:
    """
    Controlador responsável pelo processamento de arquivos CSV e cálculo de rankings.
    Implementa as regras de negócio RN04, RN06 e RN07.
    """
    
    def __init__(self, resultado_dao: ResultadoDAO, inscricao_dao: InscricaoDAO, 
                 usuario_dao: UsuarioDAO, evento_dao: EventoDAO):
        """
        Inicializa o controlador com instâncias dos DAOs.
        
        Args:
            resultado_dao: DAO para operações com resultados
            inscricao_dao: DAO para validação de inscrições
            usuario_dao: DAO para buscar atletas
            evento_dao: DAO para buscar eventos
        """
        self.__resultado_dao = resultado_dao
        self.__inscricao_dao = inscricao_dao
        self.__usuario_dao = usuario_dao
        self.__evento_dao = evento_dao
    
    def processar_csv(self, caminho_arquivo: str, evento_id: int) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Processa um arquivo CSV de resultados e salva no banco.
        
        Args:
            caminho_arquivo: Caminho para o arquivo CSV
            evento_id: ID do evento
            
        Returns:
            Tupla (total_importados, lista_erros)
        """
        print(f"\n[CONTROLADOR] Processando CSV: {caminho_arquivo}")
        print(f"[CONTROLADOR] Evento ID: {evento_id}")
        
        # Validar arquivo
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
        
        # Buscar evento do banco
        evento = self.__evento_dao.get_by_id(evento_id)
        if not evento:
            print(f"[CONTROLADOR] ERRO: Evento ID {evento_id} não encontrado!")
            raise ValueError(f"Evento com ID {evento_id} não encontrado")
        
        print(f"[CONTROLADOR] Evento encontrado: {evento.nome}")
        
        # Validar se evento está concluído (data no passado)
        from datetime import datetime
        try:
            data_evento_obj = datetime.strptime(evento.data, '%d/%m/%Y')
            if data_evento_obj >= datetime.now():
                raise ValueError(f"Evento '{evento.nome}' ainda não foi concluído. Apenas eventos concluídos podem ter resultados importados.")
        except ValueError as e:
            if "Evento" in str(e):
                raise e
            raise ValueError(f"Formato de data do evento inválido: {evento.data}")
        
        # Ler e processar CSV
        resultados = []
        erros = []
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                leitor = csv.reader(arquivo)
                
                # Pular cabeçalho se existir
                primeira_linha = next(leitor, None)
                num_linha = 1
                
                if primeira_linha and not self._eh_linha_dados(primeira_linha):
                    # É cabeçalho, pular
                    num_linha = 2
                else:
                    # Primeira linha é dados, processar
                    if primeira_linha:
                        resultado, erro = self._processar_linha(primeira_linha, evento.data, evento_id)
                        if resultado:
                            resultados.append(resultado)
                        if erro:
                            erro['linha'] = num_linha
                            erros.append(erro)
                        num_linha = 2
                
                # Processar demais linhas
                for linha in leitor:
                    resultado, erro = self._processar_linha(linha, evento.data, evento_id)
                    if resultado:
                        resultados.append(resultado)
                    if erro:
                        erro['linha'] = num_linha
                        erros.append(erro)
                    num_linha += 1
        
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo CSV: {e}")
        
        print(f"[CONTROLADOR] Linhas processadas: {len(resultados)} válidas, {len(erros)} com erro")
        
        if not resultados:
            print("[CONTROLADOR] ERRO: Nenhum resultado válido encontrado!")
            raise ValueError("Nenhum resultado válido encontrado no arquivo")
        
        # Calcular rankings
        print(f"[CONTROLADOR] Calculando rankings...")
        resultados_com_rankings = self.calcular_rankings(resultados)
        
        # Limpar resultados anteriores do evento
        print(f"[CONTROLADOR] Limpando resultados anteriores do evento {evento_id}...")
        removidos = self.__resultado_dao.limpar_resultados_evento(evento_id)
        print(f"[CONTROLADOR] {removidos} resultados anteriores removidos")
        
        # Definir evento_id nos resultados
        print(f"[CONTROLADOR] Definindo evento_id={evento_id} em {len(resultados_com_rankings)} resultados")
        for resultado in resultados_com_rankings:
            resultado.evento_id = evento_id
        
        # Salvar no banco
        print(f"[CONTROLADOR] Salvando resultados no banco...")
        total_salvos = self.__resultado_dao.salvar_lote_resultados(resultados_com_rankings)
        print(f"[CONTROLADOR] Total salvo: {total_salvos}")
        
        return total_salvos, erros
    
    def _eh_linha_dados(self, linha: List[str]) -> bool:
        """
        Verifica se uma linha contém dados válidos (não é cabeçalho).
        
        Args:
            linha: Lista de strings da linha
            
        Returns:
            True se é linha de dados, False caso contrário
        """
        if len(linha) < 2:
            return False
        
        # Verificar se o segundo campo parece ser um tempo
        tempo = linha[1].strip()
        return self._validar_formato_tempo(tempo)
    
    def _processar_linha(self, linha: List[str], data_evento: str, evento_id: int) -> Tuple[Optional[Resultado], Optional[Dict[str, Any]]]:
        """
        Processa uma linha do CSV.
        
        Args:
            linha: Lista de strings da linha
            data_evento: Data do evento
            evento_id: ID do evento para validação de inscrição
            
        Returns:
            Tupla (resultado, erro)
        """
        erro = None
        
        # Validar formato da linha
        if len(linha) < 2:
            erro = {
                'tipo': 'formato_invalido',
                'mensagem': 'Linha deve ter pelo menos 2 colunas (CPF, Tempo)',
                'dados': linha
            }
            return None, erro
        
        cpf = linha[0].strip()
        tempo = linha[1].strip()
        
        # Validar CPF
        if not self._validar_cpf(cpf):
            erro = {
                'tipo': 'cpf_invalido',
                'mensagem': f'CPF inválido: {cpf}',
                'dados': {'cpf': cpf, 'tempo': tempo}
            }
            return None, erro
        
        # Validar tempo
        if not self._validar_formato_tempo(tempo):
            erro = {
                'tipo': 'tempo_invalido',
                'mensagem': f'Formato de tempo inválido: {tempo}',
                'dados': {'cpf': cpf, 'tempo': tempo}
            }
            return None, erro
        
        # Limpar CPF para busca
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)
        
        # Buscar atleta no banco
        usuario = self.__usuario_dao.get(cpf_limpo)
        if not usuario:
            erro = {
                'tipo': 'atleta_nao_encontrado',
                'mensagem': f'Atleta com CPF {cpf} não encontrado',
                'dados': {'cpf': cpf, 'tempo': tempo}
            }
            return None, erro
        
        # Verificar se é atleta
        if not isinstance(usuario, Atleta):
            erro = {
                'tipo': 'nao_e_atleta',
                'mensagem': f'CPF {cpf} pertence a um organizador, não a um atleta',
                'dados': {'cpf': cpf, 'tempo': tempo}
            }
            return None, erro
        
        atleta = usuario
        
        # Validar se atleta está inscrito no evento
        inscricao = self.__inscricao_dao.get_by_atleta_and_evento(cpf_limpo, evento_id)
        if not inscricao:
            erro = {
                'tipo': 'atleta_nao_inscrito',
                'mensagem': f'Atleta com CPF {cpf} não está inscrito no evento',
                'dados': {'cpf': cpf, 'tempo': tempo}
            }
            return None, erro
        
        # Criar resultado
        try:
            resultado = criar_resultado_para_atleta(atleta, tempo, data_evento)
            return resultado, None
        except Exception as e:
            erro = {
                'tipo': 'erro_criacao',
                'mensagem': f'Erro ao criar resultado: {e}',
                'dados': {'cpf': cpf, 'tempo': tempo}
            }
            return None, erro
    
    def _validar_cpf(self, cpf: str) -> bool:
        """
        Valida formato básico do CPF.
        
        Args:
            cpf: CPF para validar
            
        Returns:
            True se formato é válido, False caso contrário
        """
        # Limpar CPF (remover pontos, traços, espaços)
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        
        # Verificar se tem 11 dígitos
        return len(cpf_limpo) == 11
    
    def _validar_formato_tempo(self, tempo: str) -> bool:
        """
        Valida formato do tempo HH:MM:SS.
        
        Args:
            tempo: Tempo para validar
            
        Returns:
            True se formato é válido, False caso contrário
        """
        try:
            partes = tempo.split(':')
            if len(partes) != 3:
                return False
            
            horas = int(partes[0])
            minutos = int(partes[1])
            segundos = int(partes[2])
            
            # Validações básicas
            if horas < 0 or minutos < 0 or segundos < 0:
                return False
            if minutos >= 60 or segundos >= 60:
                return False
            
            return True
        except (ValueError, IndexError):
            return False
    
    def calcular_rankings(self, resultados: List[Resultado]) -> List[Resultado]:
        """
        Calcula as classificações dos resultados baseado nas regras de negócio.
        
        Implementa:
        - RN06: Classificação Geral = Top 5 de cada gênero
        - RN07: Demais atletas classificados por categoria (Júnior, Adulto, Master)
        - PCD compete separadamente
        
        Args:
            resultados: Lista de resultados sem classificações
            
        Returns:
            Lista de resultados com classificações calculadas
        """
        # Limpar classificações existentes
        for resultado in resultados:
            resultado.limpar_classificacoes()
        
        # Separar PCD dos demais
        resultados_pcd = [r for r in resultados if r.pcd]
        resultados_nao_pcd = [r for r in resultados if not r.pcd]
        
        # Processar PCD separadamente
        if resultados_pcd:
            masculino_pcd, feminino_pcd = separar_resultados_por_genero(resultados_pcd)
            masculino_pcd_ordenado = ordenar_resultados_por_tempo(masculino_pcd)
            feminino_pcd_ordenado = ordenar_resultados_por_tempo(feminino_pcd)
            
            # PCD: Top 5 de cada gênero = Geral, demais por categoria
            for i, resultado in enumerate(masculino_pcd_ordenado[:5], 1):
                resultado.definir_classificacao_geral(i)
            for i, resultado in enumerate(feminino_pcd_ordenado[:5], 1):
                resultado.definir_classificacao_geral(i)
            
            self._calcular_classificacao_categoria(masculino_pcd_ordenado[5:])
            self._calcular_classificacao_categoria(feminino_pcd_ordenado[5:])
        
        # Processar não-PCD
        if resultados_nao_pcd:
            # Separar por gênero
            masculino, feminino = separar_resultados_por_genero(resultados_nao_pcd)
            
            # Ordenar por tempo
            masculino_ordenado = ordenar_resultados_por_tempo(masculino)
            feminino_ordenado = ordenar_resultados_por_tempo(feminino)
            
            # RN06: Classificação Geral (Top 5 de cada gênero)
            for i, resultado in enumerate(masculino_ordenado[:5], 1):
                resultado.definir_classificacao_geral(i)
            
            for i, resultado in enumerate(feminino_ordenado[:5], 1):
                resultado.definir_classificacao_geral(i)
            
            # RN07: Classificação por categoria para os demais
            self._calcular_classificacao_categoria(masculino_ordenado[5:])
            self._calcular_classificacao_categoria(feminino_ordenado[5:])
        
        return resultados
    
    def _calcular_classificacao_categoria(self, resultados: List[Resultado]):
        """
        Calcula classificação por categoria para uma lista de resultados.
        
        Args:
            resultados: Lista de resultados (já ordenados por tempo)
        """
        # Separar por categoria
        categorias = {}
        for resultado in resultados:
            categoria = resultado.categoria
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(resultado)
        
        # Calcular posição em cada categoria
        for categoria, resultados_categoria in categorias.items():
            # Já estão ordenados por tempo
            for i, resultado in enumerate(resultados_categoria, 1):
                resultado.definir_classificacao_categoria(i)
    
    def obter_resumo_importacao(self, total_importados: int, erros: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cria um resumo da importação para exibição.
        
        Args:
            total_importados: Número de resultados importados
            erros: Lista de erros encontrados
            
        Returns:
            Dicionário com resumo da importação
        """
        # Contar erros por tipo
        erros_por_tipo = {}
        for erro in erros:
            tipo = erro['tipo']
            erros_por_tipo[tipo] = erros_por_tipo.get(tipo, 0) + 1
        
        return {
            'total_importados': total_importados,
            'total_erros': len(erros),
            'erros_por_tipo': erros_por_tipo,
            'sucesso': len(erros) == 0,
            'taxa_sucesso': (total_importados / (total_importados + len(erros))) * 100 if (total_importados + len(erros)) > 0 else 0
        }
    
    def validar_arquivo_csv(self, caminho_arquivo: str) -> Tuple[bool, str]:
        """
        Valida se um arquivo é um CSV válido para importação.
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tupla (é_válido, mensagem_erro)
        """
        if not os.path.exists(caminho_arquivo):
            return False, "Arquivo não encontrado"
        
        if not caminho_arquivo.lower().endswith('.csv'):
            return False, "Arquivo deve ter extensão .csv"
        
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                leitor = csv.reader(arquivo)
                
                # Verificar se tem pelo menos uma linha
                primeira_linha = next(leitor, None)
                if not primeira_linha:
                    return False, "Arquivo está vazio"
                
                # Verificar se tem pelo menos 2 colunas
                if len(primeira_linha) < 2:
                    return False, "Arquivo deve ter pelo menos 2 colunas (CPF, Tempo)"
                
                # Contar linhas
                total_linhas = 1  # Já lemos a primeira
                for linha in leitor:
                    total_linhas += 1
                
                if total_linhas < 1:
                    return False, "Arquivo deve ter pelo menos uma linha de dados"
                
                return True, f"Arquivo válido com {total_linhas} linhas"
                
        except Exception as e:
            return False, f"Erro ao ler arquivo: {e}"

