from entidade.usuario import Usuario
from datetime import datetime

class Atleta(Usuario):
    def __init__(self, nome, cpf, email, senha_hash, data_nascimento, genero, pcd):
        super().__init__(cpf, nome, email, senha_hash)
        try:
            data_convertida = datetime.strptime(data_nascimento, "%d/%m/%Y")
        except ValueError:
            try:
                data_convertida = datetime.strptime(data_nascimento, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"O formato da data '{data_nascimento}' é inválido. Use dd/mm/yyyy.")
        if data_convertida > datetime.now():
            raise ValueError("A data de nascimento não pode ser uma data futura.")
        self.__data_nascimento = data_convertida
        self.__genero = genero
        self.__pcd = pcd

    @property
    def data_nascimento(self):
        return self.__data_nascimento

    @property
    def genero(self):
        return self.__genero

    @genero.setter
    def genero(self, genero):
        self.__genero = genero

    @property
    def pcd(self):
        return self.__pcd

    @pcd.setter
    def pcd(self, pcd):
        self.__pcd = pcd

    @property
    def data_nascimento_str(self):
        return self.__data_nascimento.strftime('%Y-%m-%d')

    def calcula_idade(self, ano_evento):
        idade = ano_evento - self.__data_nascimento.year
        return idade

    def calcular_categoria(self, data_evento: str) -> str:
        """
        Calcula a categoria do atleta baseada na RN04.
        RN04: A categoria do atleta é definida pela idade que ele terá 
        em 31 de dezembro do ano do evento.
        
        Args:
            data_evento: Data do evento no formato DD/MM/YYYY
            
        Returns:
            Categoria: 'PCD', 'Júnior', 'Adulto' ou 'Master'
        """
        # Se é PCD, sempre compete na categoria PCD
        if self.pcd:
            return 'PCD'
        
        # Calcular idade em 31/12 do ano do evento
        try:
            ano_evento = datetime.strptime(data_evento, '%d/%m/%Y').year
            idade = ano_evento - self.__data_nascimento.year
            
            # Ajustar para idade em 31/12
            data_31_dezembro = datetime(ano_evento, 12, 31)
            if (data_31_dezembro.month, data_31_dezembro.day) < (self.__data_nascimento.month, self.__data_nascimento.day):
                idade -= 1
            
            # RN07: Classificação por faixas etárias
            if idade <= 17:
                return 'Júnior'
            elif idade <= 49:
                return 'Adulto'
            else:  # 50+ anos
                return 'Master'
                
        except ValueError:
            raise ValueError(f"Formato de data inválido: {data_evento}")