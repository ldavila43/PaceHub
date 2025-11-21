import re
from datetime import datetime
import FreeSimpleGUI as sg
from controle.controlador_organizador import ControladorOrganizador
from entidade.atleta import Atleta
from entidade.organizador import Organizador
from limite.tela_organizador import TelaOrganizador
from limite.tela_principal import TelaPrincipal
from controle.controlador_atleta import ControladorAtleta
from persistencia.inscricao_dao import InscricaoDAO
from persistencia.usuario_dao import UsuarioDAO
from controle.controlador_evento import ControladorEvento
from persistencia.evento_dao import EventoDAO
from controle.controlador_inscricao import ControladorInscricao
from controle.controlador_importacao import ControladorImportacao
from persistencia.resultado_dao import ResultadoDAO
from limite.tela_importar_resultados import executar_janela_importacao


class ControladorSistema:
    def __init__(self):
        self.__tela_principal = TelaPrincipal()
        self.__evento_dao = EventoDAO()
        self.__usuario_dao = UsuarioDAO()
        self.__inscricao_dao = InscricaoDAO()
        self.__tela_organizador = TelaOrganizador()
        self.__controlador_atleta = ControladorAtleta(self, self.__usuario_dao)
        self.__controlador_organizador = ControladorOrganizador(self, self.__usuario_dao)
        self.__controlador_evento = ControladorEvento(self, self.__evento_dao, self.__usuario_dao)
        self.__controlador_inscricao = ControladorInscricao(self,self.__inscricao_dao, self.__usuario_dao)
        self.__resultado_dao = ResultadoDAO()
        self.__controlador_importacao = ControladorImportacao(
            self.__resultado_dao,
            self.__inscricao_dao,
            self.__usuario_dao,
            self.__evento_dao
        )

    def iniciar(self):
        while True:
            evento, valores = self.__tela_principal.exibir_janela_login()

            if evento is None or evento == sg.WIN_CLOSED:
                break
            if evento == '-CADASTRO_ATLETA-':
                self.__controlador_atleta.abre_tela_cadastro()
            elif evento == '-CADASTRO_ORGANIZADOR-':
                self.__controlador_organizador.abre_tela_cadastro()
            elif evento == 'Login':
                self.processar_login(valores)
            elif evento == '-LISTAR_ATLETAS-':
                self.__controlador_atleta.listar_atletas()
            elif evento == '-LISTAR_ORGANIZADORES-':
                self.__controlador_organizador.listar_organizadores()

    def processar_login(self, valores_login):
        cpf_input = valores_login.get('-CPF_LOGIN-', '')

        if not cpf_input:
            self.exibir_popup_erro("Por favor, insira um CPF.")
            return

        cpf_limpo = re.sub(r'[^0-9]', '', cpf_input)
        usuario = self.__usuario_dao.get(cpf_limpo)

        if usuario is None:
            self.exibir_popup_erro("CPF não encontrado.")
            return

        if isinstance(usuario, Organizador):
            self.iniciar_painel_organizador(usuario)
        elif isinstance(usuario, Atleta):
            self.exibir_popup_erro("Painel do Atleta ainda não implementado.")
        else:
            self.exibir_popup_erro("Tipo de usuário desconhecido.")

    def iniciar_painel_organizador(self, organizador: Organizador):

        eventos_do_organizador = self.__evento_dao.get_all_by_organizador(organizador.cpf)

        dados_tabela = self.preparar_dados_tabela_eventos(eventos_do_organizador)

        janela_painel = self.__tela_organizador.exibir_painel(organizador.nome, dados_tabela)

        while True:
            evento, valores = janela_painel.read()
            if evento in(sg.WIN_CLOSED, '-SAIR-'):
                break
            if evento == '-CRIAR_EVENTO-':
                self.__controlador_evento.abre_tela_novo_evento(organizador)

                eventos_do_organizador = self.__evento_dao.get_all_by_organizador(organizador.cpf)
                dados_tabela_novos = self.preparar_dados_tabela_eventos(eventos_do_organizador)
                janela_painel['-TABELA_EVENTOS-'].update(values=dados_tabela_novos)

            if evento == '-GERENCIAR_KITS-':
                indices_selecionados = valores['-TABELA_EVENTOS-']
                if not indices_selecionados:
                    self.exibir_popup_erro("Por favor, selecione um evento na tabela primeiro.")
                    continue
            
                indice_selecionado = indices_selecionados[0]

                evento_selecionado = eventos_do_organizador[indice_selecionado]

                self.__controlador_inscricao.abre_tela_gerenciar_kits(
                    evento_selecionado.id,
                    evento_selecionado.nome
                )
            if evento == '-EDITAR_EVENTO-':
                indices_selecionados = valores['-TABELA_EVENTOS-']
                if not indices_selecionados:
                    self.exibir_popup_erro("Por favor, selecione um evento na tabela primeiro.")
                    continue

                indice_selecionado = indices_selecionados[0]
                evento_selecionado = eventos_do_organizador[indice_selecionado]
                
                self.__controlador_evento.abre_tela_editar_evento(
                    evento_selecionado,
                    organizador
                )
                
                eventos_do_organizador = self.__evento_dao.get_all_by_organizador(organizador.cpf)
                dados_tabela_novos = self.preparar_dados_tabela_eventos(eventos_do_organizador)
                janela_painel['-TABELA_EVENTOS-'].update(values=dados_tabela_novos)
            if evento == '-IMPORTAR_TEMPOS-':
                indices_selecionados = valores['-TABELA_EVENTOS-']
                if not indices_selecionados:
                    self.exibir_popup_erro("Por favor, selecione um evento na tabela primeiro.")
                    continue
                
                indice_selecionado = indices_selecionados[0]
                evento_selecionado = eventos_do_organizador[indice_selecionado]
                
                # Verificar se evento está concluído
                try:
                    data_evento_obj = datetime.strptime(evento_selecionado.data, '%d/%m/%Y')
                    if data_evento_obj >= datetime.now():
                        self.exibir_popup_erro("Apenas eventos concluídos podem ter resultados importados.")
                        continue
                except ValueError:
                    self.exibir_popup_erro("Data do evento inválida.")
                    continue
                
                # Abrir tela de importação
                sucesso = executar_janela_importacao(
                    self.__controlador_importacao,
                    evento_selecionado.id,
                    evento_selecionado.nome
                )
                
                if sucesso:
                    # Atualizar tabela de eventos se necessário
                    eventos_do_organizador = self.__evento_dao.get_all_by_organizador(organizador.cpf)
                    dados_tabela_novos = self.preparar_dados_tabela_eventos(eventos_do_organizador)
                    janela_painel['-TABELA_EVENTOS-'].update(values=dados_tabela_novos)
        janela_painel.close()

    def preparar_dados_tabela_eventos(self, eventos_do_organizador) -> list:
        dados_formatados = []
        for evento in eventos_do_organizador:
            contagem_inscritos = self.__inscricao_dao.count_by_evento(evento.id)
            status = "Inscrições Abertas"
            try:
                data_evento_obj = datetime.strptime(evento.data, '%d/%m/%Y')
                if data_evento_obj < datetime.now():
                    status = "Concluído"
            except ValueError:
                status = "Data Inválida"

            dados_formatados.append([
                evento.nome,
                evento.data,
                contagem_inscritos,
                status
            ])

        return dados_formatados


    def exibir_popup_erro(self, mensagem: str):
        sg.popup_error(mensagem, title="Erro")

    def exibir_popup_sucesso(self, mensagem: str):
        sg.popup_ok(mensagem, title="Sucesso")