from datetime import datetime
from typing import Optional, List, Tuple

class Resultado:
    """
    Classe que representa um resultado de corrida de um atleta.
    Contém informações sobre tempo, categoria e classificações.
    """
    
    def __init__(self, cpf_atleta: str, nome_atleta: str, genero_atleta: str, 
                 tempo_final: str, categoria: str, pcd: bool = False):
        """
        Inicializa um resultado.
        
        Args:
            cpf_atleta: CPF do atleta
            nome_atleta: Nome do atleta
            genero_atleta: Gênero do atleta ('Masculino' ou 'Feminino')
            tempo_final: Tempo final no formato HH:MM:SS
            categoria: Categoria do atleta ('Júnior', 'Adulto', 'Master', 'PCD')
            pcd: Se o atleta é pessoa com deficiência
        """
        self.id = None  # Preenchido após salvar no banco
        self.evento_id = None
        self.cpf_atleta = cpf_atleta
        self.nome_atleta = nome_atleta
        self.genero_atleta = genero_atleta
        self.tempo_final = tempo_final  # string HH:MM:SS
        self.categoria = categoria
        self.classificacao_geral = None  # Posição na classificação geral (top 5)
        self.classificacao_categoria = None  # Posição na categoria
        self.pcd = pcd
    
    def tempo_em_segundos(self) -> int:
        """
        Converte o tempo HH:MM:SS para segundos.
        Útil para ordenação e cálculos.
        
        Returns:
            Tempo em segundos
        """
        try:
            partes = self.tempo_final.split(':')
            if len(partes) != 3:
                raise ValueError(f"Formato de tempo inválido: {self.tempo_final}")
            
            horas = int(partes[0])
            minutos = int(partes[1])
            segundos = int(partes[2])
            
            return horas * 3600 + minutos * 60 + segundos
        except (ValueError, IndexError):
            raise ValueError(f"Formato de tempo inválido: {self.tempo_final}")
    
    def tempo_formatado(self) -> str:
        """
        Retorna o tempo formatado para exibição.
        
        Returns:
            Tempo no formato HH:MM:SS
        """
        return self.tempo_final
    
    def tem_classificacao_geral(self) -> bool:
        """
        Verifica se o atleta tem classificação geral (top 5).
        
        Returns:
            True se tem classificação geral, False caso contrário
        """
        return self.classificacao_geral is not None and self.classificacao_geral <= 5
    
    def tem_classificacao_categoria(self) -> bool:
        """
        Verifica se o atleta tem classificação por categoria.
        
        Returns:
            True se tem classificação por categoria, False caso contrário
        """
        return self.classificacao_categoria is not None
    
    def definir_classificacao_geral(self, posicao: int):
        """
        Define a classificação geral do atleta.
        
        Args:
            posicao: Posição na classificação geral (1-5)
        """
        if posicao < 1 or posicao > 5:
            raise ValueError("Classificação geral deve estar entre 1 e 5")
        self.classificacao_geral = posicao
    
    def definir_classificacao_categoria(self, posicao: int):
        """
        Define a classificação por categoria do atleta.
        
        Args:
            posicao: Posição na categoria
        """
        if posicao < 1:
            raise ValueError("Classificação por categoria deve ser maior que 0")
        self.classificacao_categoria = posicao
    
    def limpar_classificacoes(self):
        """
        Limpa as classificações do resultado.
        """
        self.classificacao_geral = None
        self.classificacao_categoria = None
    
    def to_dict(self) -> dict:
        """
        Converte o resultado para dicionário.
        Útil para operações de banco de dados.
        
        Returns:
            Dicionário com os dados do resultado
        """
        return {
            'id': self.id,
            'evento_id': self.evento_id,
            'cpf_atleta': self.cpf_atleta,
            'nome_atleta': self.nome_atleta,
            'genero_atleta': self.genero_atleta,
            'tempo_final': self.tempo_final,
            'categoria': self.categoria,
            'classificacao_geral': self.classificacao_geral,
            'classificacao_categoria': self.classificacao_categoria,
            'pcd': 1 if self.pcd else 0
        }
    
    @classmethod
    def from_dict(cls, dados: dict) -> 'Resultado':
        """
        Cria um resultado a partir de um dicionário.
        Útil para operações de banco de dados.
        
        Args:
            dados: Dicionário com os dados do resultado
            
        Returns:
            Objeto Resultado
        """
        resultado = cls(
            cpf_atleta=dados['cpf_atleta'],
            nome_atleta=dados['nome_atleta'],
            genero_atleta=dados['genero_atleta'],
            tempo_final=dados['tempo_final'],
            categoria=dados['categoria'],
            pcd=bool(dados.get('pcd', 0))
        )
        
        resultado.id = dados.get('id')
        resultado.evento_id = dados.get('evento_id')
        resultado.classificacao_geral = dados.get('classificacao_geral')
        resultado.classificacao_categoria = dados.get('classificacao_categoria')
        
        return resultado
    
    def __str__(self):
        classificacao_str = ""
        if self.tem_classificacao_geral():
            classificacao_str += f" (Geral: {self.classificacao_geral}º)"
        if self.tem_classificacao_categoria():
            classificacao_str += f" ({self.categoria}: {self.classificacao_categoria}º)"
        
        return f"{self.nome_atleta} - {self.tempo_final}{classificacao_str}"
    
    def __repr__(self):
        return (f"Resultado(cpf='{self.cpf_atleta}', nome='{self.nome_atleta}', "
                f"tempo='{self.tempo_final}', categoria='{self.categoria}')")
    
    def __lt__(self, other):
        """
        Comparação para ordenação por tempo (menor tempo = melhor posição).
        """
        if not isinstance(other, Resultado):
            return NotImplemented
        return self.tempo_em_segundos() < other.tempo_em_segundos()
    
    def __eq__(self, other):
        """
        Comparação de igualdade por CPF e evento.
        """
        if not isinstance(other, Resultado):
            return NotImplemented
        return (self.cpf_atleta == other.cpf_atleta and 
                self.evento_id == other.evento_id)


def criar_resultado_para_atleta(atleta, tempo_final: str, data_evento: str) -> Resultado:
    """
    Cria um resultado para um atleta específico.
    
    Args:
        atleta: Objeto Atleta
        tempo_final: Tempo final no formato HH:MM:SS
        data_evento: Data do evento para cálculo da categoria
        
    Returns:
        Objeto Resultado
    """
    categoria = atleta.calcular_categoria(data_evento)
    
    return Resultado(
        cpf_atleta=atleta.cpf,
        nome_atleta=atleta.nome,
        genero_atleta=atleta.genero,
        tempo_final=tempo_final,
        categoria=categoria,
        pcd=atleta.pcd
    )


def ordenar_resultados_por_tempo(resultados: List[Resultado]) -> List[Resultado]:
    """
    Ordena uma lista de resultados por tempo (crescente).
    
    Args:
        resultados: Lista de objetos Resultado
        
    Returns:
        Lista ordenada por tempo
    """
    return sorted(resultados, key=lambda r: r.tempo_em_segundos())


def separar_resultados_por_genero(resultados: List[Resultado]) -> Tuple[List[Resultado], List[Resultado]]:
    """
    Separa resultados por gênero.
    
    Args:
        resultados: Lista de objetos Resultado
        
    Returns:
        Tupla (resultados_masculino, resultados_feminino)
    """
    masculino = [r for r in resultados if r.genero_atleta == 'Masculino']
    feminino = [r for r in resultados if r.genero_atleta == 'Feminino']
    
    return masculino, feminino


def separar_resultados_por_categoria(resultados: List[Resultado]) -> dict:
    """
    Separa resultados por categoria.
    
    Args:
        resultados: Lista de objetos Resultado
        
    Returns:
        Dicionário com resultados separados por categoria
    """
    categorias = {}
    
    for resultado in resultados:
        categoria = resultado.categoria
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append(resultado)
    
    return categorias

