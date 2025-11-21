import FreeSimpleGUI as sg
import re
from entidade.kit_de_corrida import KitDeCorrida
from limite.tela_inscricao import TelaInscricao
from persistencia.inscricao_dao import InscricaoDAO
from persistencia.usuario_dao import UsuarioDAO
from entidade.atleta import Atleta
from entidade.inscricao import Inscricao


class ControladorInscricao:

    def __init__(self, controlador_sistema, inscricao_dao: InscricaoDAO, usuario_dao: UsuarioDAO):
        self.__controlador_sistema = controlador_sistema
        self.__tela_inscricao = TelaInscricao()
        self.__inscricao_dao = inscricao_dao
        self.__usuario_dao = usuario_dao
        self.__inscricao_encontrada: Inscricao | None = None
        self.__atleta_encontrado: Atleta | None = None
        self.__kit_encontrado: KitDeCorrida | None = None

    def abre_tela_gerenciar_kits(self, evento_id: int, evento_nome: str):
        self.__inscricao_encontrada = None
        self.__atleta_encontrado = None
        self.__kit_encontrado = None

        janela = self.__tela_inscricao.exibir_tela_gerenciar_kit(evento_nome)

        while True:
            evento, valores = janela.read()

            if evento in (sg.WIN_CLOSED, '-VOLTAR-'):
                break

            if evento == '-BUSCAR-':
                input_busca = valores['-INPUT_BUSCA-']
                if not input_busca:
                    continue

                self.buscar_atleta_inscricao(janela, input_busca, evento_id)

            if evento == '-SALVAR-':
                if self.__inscricao_encontrada:
                    novo_status_kit = valores['-KIT_ENTREGUE-']
                    self.__inscricao_dao.update_kit_entregue(
                        self.__inscricao_encontrada.id,
                        novo_status_kit
                    )
                    self.__controlador_sistema.exibir_popup_sucesso("Status do kit atualizado!")
                    self.limpar_campos_busca(janela)
                else:
                    self.__controlador_sistema.exibir_popup_erro("Nenhuma inscrição selecionada para salvar.")

        janela.close()

    def buscar_atleta_inscricao(self, janela, input_busca: str, evento_id: int):

        self.limpar_campos_busca(janela)

        cpf_busca = re.sub(r'[^0-9]', '', input_busca)
        usuario = self.__usuario_dao.get(cpf_busca)

        if not isinstance(usuario, Atleta):
            self.__controlador_sistema.exibir_popup_erro("Nenhum atleta encontrado com este CPF.")
            return

        self.__atleta_encontrado = usuario

        inscricao, kit = self.__inscricao_dao.get_by_atleta_e_evento(
            self.__atleta_encontrado.cpf,
            evento_id
        )

        if not inscricao:
            self.__controlador_sistema.exibir_popup_erro("Este atleta não está inscrito neste evento ou não selecionou kit.")
            self.limpar_campos_busca(janela)
            return

        # como é inner join, não precisamos verificar se if not kit, só irá buscar os atletas com kits cadastrados

        self.__inscricao_encontrada = inscricao
        self.__kit_encontrado = kit

        janela['-NOME_ATLETA-'].update(self.__atleta_encontrado.nome)
        janela['-CPF_ATLETA-'].update(self.__atleta_encontrado.cpf)

        if self.__kit_encontrado:
            janela['-NOME_KIT-'].update(self.__kit_encontrado.nome)
            janela['-VALOR_KIT-'].update(f"R$ {self.__kit_encontrado.valor:.2f}")

        status_kit = bool(self.__inscricao_encontrada.kit_entregue)
        janela['-KIT_ENTREGUE-'].update(value=status_kit, disabled=False)

        janela['-SALVAR-'].update(disabled=False)

    def limpar_campos_busca(self, janela):
        self.__inscricao_encontrada = None
        self.__atleta_encontrado = None
        self.__kit_encontrado = None

        janela['-NOME_ATLETA-'].update('[Nome do Atleta]')
        janela['-CPF_ATLETA-'].update('[CPF do Atleta]')

        janela['-NOME_KIT-'].update('[Kit]')
        janela['-VALOR_KIT-'].update('[R$ 0,00]')

        janela['-KIT_ENTREGUE-'].update(value=False, disabled=True)
        janela['-SALVAR-'].update(disabled=True)