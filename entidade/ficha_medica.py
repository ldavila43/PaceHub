class FichaMedica:
    def __init__(self, inscricao_id: int, preenchida: bool = False, 
                 pergunta1: int = None, pergunta2: int = None, pergunta3: int = None,
                 pergunta4: int = None, pergunta5: int = None, pergunta6: int = None,
                 pergunta7: int = None, declaracao_saude: bool = False):
        self.__inscricao_id = inscricao_id
        self.__preenchida = preenchida
        self.__pergunta1 = pergunta1
        self.__pergunta2 = pergunta2
        self.__pergunta3 = pergunta3
        self.__pergunta4 = pergunta4
        self.__pergunta5 = pergunta5
        self.__pergunta6 = pergunta6
        self.__pergunta7 = pergunta7
        self.__declaracao_saude = declaracao_saude

    @property
    def inscricao_id(self):
        return self.__inscricao_id

    @property
    def preenchida(self):
        return self.__preenchida

    @preenchida.setter
    def preenchida(self, preenchida: bool):
        self.__preenchida = preenchida

    @property
    def pergunta1(self):
        return self.__pergunta1

    @pergunta1.setter
    def pergunta1(self, valor: int):
        self.__pergunta1 = valor

    @property
    def pergunta2(self):
        return self.__pergunta2

    @pergunta2.setter
    def pergunta2(self, valor: int):
        self.__pergunta2 = valor

    @property
    def pergunta3(self):
        return self.__pergunta3

    @pergunta3.setter
    def pergunta3(self, valor: int):
        self.__pergunta3 = valor

    @property
    def pergunta4(self):
        return self.__pergunta4

    @pergunta4.setter
    def pergunta4(self, valor: int):
        self.__pergunta4 = valor

    @property
    def pergunta5(self):
        return self.__pergunta5

    @pergunta5.setter
    def pergunta5(self, valor: int):
        self.__pergunta5 = valor

    @property
    def pergunta6(self):
        return self.__pergunta6

    @pergunta6.setter
    def pergunta6(self, valor: int):
        self.__pergunta6 = valor

    @property
    def pergunta7(self):
        return self.__pergunta7

    @pergunta7.setter
    def pergunta7(self, valor: int):
        self.__pergunta7 = valor

    @property
    def declaracao_saude(self):
        return self.__declaracao_saude

    @declaracao_saude.setter
    def declaracao_saude(self, valor: bool):
        self.__declaracao_saude = valor

