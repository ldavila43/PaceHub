import FreeSimpleGUI as sg
import re
from entidade.kit_de_corrida import KitDeCorrida
from limite.tela_inscricao import TelaInscricao
from limite.tela_ficha_medica import TelaFichaMedica
from persistencia.inscricao_dao import InscricaoDAO
from persistencia.usuario_dao import UsuarioDAO
from persistencia.evento_dao import EventoDAO
from persistencia.ficha_medica_dao import FichaMedicaDAO
from entidade.atleta import Atleta
from entidade.inscricao import Inscricao
from entidade.ficha_medica import FichaMedica


class ControladorInscricao:

    def __init__(self, controlador_sistema, inscricao_dao: InscricaoDAO, usuario_dao: UsuarioDAO):
        self.__controlador_sistema = controlador_sistema
        self.__tela_inscricao = TelaInscricao()
        self.__tela_ficha_medica = TelaFichaMedica()
        self.__inscricao_dao = inscricao_dao
        self.__usuario_dao = usuario_dao
        self.__evento_dao = EventoDAO()
        self.__ficha_medica_dao = FichaMedicaDAO()
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
                novo_status_kit = valores['-KIT_ENTREGUE-']
                self.__inscricao_encontrada.kit_entregue = novo_status_kit
                self.__inscricao_dao.update_kit_entregue(
                    self.__inscricao_encontrada.id,
                    novo_status_kit
                )
                self.exibir_popup_sucesso("Status do kit atualizado!")
                self.limpar_campos_busca(janela)

        janela.close()

    def buscar_atleta_inscricao(self, janela, input_busca: str, evento_id: int):

        self.limpar_campos_busca(janela)

        cpf_busca = re.sub(r'[^0-9]', '', input_busca)
        usuario = self.__usuario_dao.get(cpf_busca)

        if not isinstance(usuario, Atleta):
            self.exibir_popup_erro("Nenhum atleta encontrado com este CPF.")
            return

        self.__atleta_encontrado = usuario

        inscricao, kit = self.__inscricao_dao.get_by_atleta_e_evento(
            self.__atleta_encontrado.cpf,
            evento_id
        )

        if not inscricao:
            self.exibir_popup_erro("Este atleta não está inscrito neste evento ou não selecionou kit.")
            self.limpar_campos_busca(janela)
            return

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

    def exibir_popup_erro(self, mensagem: str):
        sg.popup_error(mensagem, title="Erro")

    def exibir_popup_sucesso(self, mensagem: str):
        sg.popup_ok(mensagem, title="Sucesso")

    def abre_tela_inscricao_atleta(self, evento_id: int, atleta: Atleta):
        """Abre a tela de inscrição para o atleta se inscrever em um evento."""
        # Buscar evento
        evento = self.__evento_dao.get_by_id(evento_id)
        if not evento:
            self.exibir_popup_erro("Evento não encontrado.")
            return

        # Verificar se atleta já está inscrito
        inscricao_existente, _ = self.__inscricao_dao.get_by_atleta_e_evento(atleta.cpf, evento_id)
        if inscricao_existente:
            self.exibir_popup_erro("Você já está inscrito neste evento.")
            return

        # Buscar kits do evento
        kits = self.__evento_dao.get_kits_by_evento_id(evento_id)
        if not kits:
            self.exibir_popup_erro("Este evento não possui kits cadastrados.")
            return

        # Abrir tela de inscrição
        janela = self.__tela_inscricao.exibir_tela_inscricao_atleta(
            evento.nome,
            atleta.nome,
            atleta.cpf,
            kits
        )

        ficha_medica_preenchida = False
        ficha_medica_respostas = None

        while True:
            evento_janela, valores = janela.read()

            if evento_janela in (sg.WIN_CLOSED, '-VOLTAR-'):
                break

            if evento_janela == '-FICHA_MEDICA-':
                # Abrir tela de ficha médica
                janela_ficha = self.__tela_ficha_medica.exibir_tela_ficha_medica()
                
                while True:
                    evento_ficha, valores_ficha = janela_ficha.read()
                    
                    if evento_ficha in (sg.WIN_CLOSED, '-VOLTAR-'):
                        break

                    if evento_ficha == '-SALVAR-':
                        # Validar declaração de saúde
                        if not valores_ficha.get('-DECLARACAO_SAUDE-', False):
                            sg.popup_error('Você precisa atestar sua condição de saúde.', title='Erro')
                            continue

                        # Coletar respostas das perguntas
                        respostas = []
                        for i in range(1, 8):
                            sim_key = f'-PERGUNTA{i}_SIM-'
                            nao_key = f'-PERGUNTA{i}_NAO-'
                            if valores_ficha.get(sim_key, False):
                                respostas.append(1)  # SIM
                            elif valores_ficha.get(nao_key, False):
                                respostas.append(0)  # NÃO
                            else:
                                respostas.append(None)  # Não respondida

                        # Verificar se todas as perguntas foram respondidas
                        if None in respostas:
                            sg.popup_error('Por favor, responda todas as perguntas.', title='Erro')
                            continue

                        # Armazenar respostas da ficha médica (será criada após a inscrição)
                        ficha_medica_respostas = {
                            'pergunta1': respostas[0],
                            'pergunta2': respostas[1],
                            'pergunta3': respostas[2],
                            'pergunta4': respostas[3],
                            'pergunta5': respostas[4],
                            'pergunta6': respostas[5],
                            'pergunta7': respostas[6]
                        }

                        # Verificar se há respostas SIM (aviso)
                        if any(respostas):
                            sg.popup('ATENÇÃO: Uma ou mais respostas indicam que você deve consultar um médico antes de praticar atividade física.\n\nRecomendamos que você procure orientação médica antes de participar do evento.', 
                                    title='Atenção')

                        ficha_medica_preenchida = True
                        sg.popup_ok('Ficha médica salva com sucesso!', title='Sucesso')
                        break

                janela_ficha.close()

            if evento_janela == '-CONFIRMAR-':
                # Validar kit selecionado
                kit_selecionado = valores.get('-KIT-', '')
                if not kit_selecionado:
                    self.exibir_popup_erro("Por favor, selecione um kit.")
                    continue

                # Validar ficha médica
                if not ficha_medica_preenchida or ficha_medica_respostas is None:
                    self.exibir_popup_erro("Você deve preencher a ficha médica antes de finalizar a inscrição.")
                    continue

                # Validar checkboxes
                termo_aceito = valores.get('-TERMO_ACEITO-', False)
                saude_ok = valores.get('-SAUDE_OK-', False)

                if not termo_aceito:
                    self.exibir_popup_erro("Você deve aceitar os termos de responsabilidade.")
                    continue

                if not saude_ok:
                    self.exibir_popup_erro("Você deve atestar que está em condições de saúde aptas.")
                    continue

                # Extrair kit_id do kit selecionado
                kit_id = None
                for kit in kits:
                    kit_str = f"{kit.nome} - R${kit.valor:.2f}"
                    if kit_str == kit_selecionado:
                        kit_id = kit.id
                        break

                if not kit_id:
                    self.exibir_popup_erro("Kit selecionado inválido.")
                    continue

                try:
                    # Criar inscrição (status=1 = Paga)
                    nova_inscricao = Inscricao(
                        atleta_cpf=atleta.cpf,
                        evento_id=evento_id,
                        kit_id=kit_id,
                        status=1,
                        data_inscricao=None,  # Será gerada automaticamente
                        kit_entregue=0
                    )

                    # Salvar inscrição
                    self.__inscricao_dao.add(nova_inscricao)

                    # Criar ficha médica com o ID da inscrição
                    ficha_medica_obj = FichaMedica(
                        inscricao_id=nova_inscricao.id,
                        preenchida=True,
                        pergunta1=ficha_medica_respostas['pergunta1'],
                        pergunta2=ficha_medica_respostas['pergunta2'],
                        pergunta3=ficha_medica_respostas['pergunta3'],
                        pergunta4=ficha_medica_respostas['pergunta4'],
                        pergunta5=ficha_medica_respostas['pergunta5'],
                        pergunta6=ficha_medica_respostas['pergunta6'],
                        pergunta7=ficha_medica_respostas['pergunta7'],
                        declaracao_saude=True
                    )

                    # Salvar ficha médica
                    self.__ficha_medica_dao.add(ficha_medica_obj)

                    self.exibir_popup_sucesso(f'Inscrição realizada com sucesso!\n\nKit Selecionado: {kit_selecionado}')
                    break

                except Exception as e:
                    self.exibir_popup_erro(f"Erro ao realizar inscrição: {e}")

        janela.close()