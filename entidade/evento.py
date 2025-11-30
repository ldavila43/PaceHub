from entidade.kit_de_corrida import KitDeCorrida
from typing import List

class Evento:
    def __init__(self, nome: str, data: str, distancia: int, local_largada: str, tempo_corte: str, data_limite_cred: str, organizador_cpf: str):
        self.nome = nome
        self.data = data
        self.distancia = distancia
        self.local_largada = local_largada
        self.tempo_corte = tempo_corte
        self.data_limite_cred = data_limite_cred
        self.organizador_cpf = organizador_cpf
        self.kits: List[KitDeCorrida] = []
        self.resultados_publicados: int = 0