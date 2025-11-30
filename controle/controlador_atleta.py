import bcrypt
import FreeSimpleGUI as sg
import re
from datetime import datetime
from entidade.atleta import Atleta
from limite.tela_cadastro import TelaCadastro
from limite.tela_atleta import TelaAtleta
from persistencia.evento_dao import EventoDAO
from persistencia.inscricao_dao import InscricaoDAO
from persistencia.resultado_dao import ResultadoDAO
from limite.tela_resultados import TelaResultados


class ControladorAtleta:
    def __init__(self, controlador_sistema, usuario_dao):
        self.__controlador_sistema = controlador_sistema
        self.__tela_cadastro = TelaCadastro()
        self.__tela_atleta = TelaAtleta()
        self.__usuario_dao = usuario_dao
        self.__evento_dao = EventoDAO()
        self.__inscricao_dao = InscricaoDAO()
        self.__resultado_dao = ResultadoDAO()
        self.__tela_resultados = TelaResultados()

    def abre_tela_cadastro(self):
        evento, valores = self.__tela_cadastro.exibir_janela_cadastro('Atleta')
        if evento is None or evento == sg.WIN_CLOSED or evento == '-VOLTAR-':
            return

        campos_obrigatorios = ['-NOME-', '-CPF-', '-EMAIL-', '-DATA_NASC-', '-GENERO-', '-SENHA-']
        if evento == '-CADASTRAR-':

            if any(not valores[key].strip() for key in campos_obrigatorios):
                self.__controlador_sistema.exibir_popup_erro('Todos os campos com * devem ser preenchidos')
                return

            cpf_limpo_para_consulta = re.sub(r'[^0-9]', '', valores['-CPF-'])
            cpf_existente = self.__usuario_dao.get(cpf_limpo_para_consulta)

            if cpf_existente:
                self.__controlador_sistema.exibir_popup_erro('O CPF informado já está cadastrado')
                return

            try:
                senha_pura = valores['-SENHA-'].encode('utf-8')
                senha_hash = bcrypt.hashpw(senha_pura, bcrypt.gensalt()).decode('utf-8')

                novo_atleta = Atleta(
                    nome=valores['-NOME-'],
                    cpf=valores['-CPF-'],
                    email=valores['-EMAIL-'],
                    senha_hash=senha_hash,
                    data_nascimento=valores['-DATA_NASC-'],
                    genero=valores['-GENERO-'],
                    pcd=valores['-PCD_SIM-'],
                )
                self.__usuario_dao.add(novo_atleta)
                self.__controlador_sistema.exibir_popup_sucesso('Cadastro Efetuado com sucesso')

                print('Atelta adicionad à lista', novo_atleta.nome)
            except Exception as e:
                self.__controlador_sistema.exibir_popup_erro(f'Erro ao criar atleta: {e}')

    def preparar_dados_eventos_disponiveis(self, eventos):
        """Prepara dados dos eventos para exibição na tabela."""
        dados_formatados = []
        for evento in eventos:
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
                evento.distancia,
                status
            ])
        return dados_formatados

    def preparar_dados_inscricoes(self, inscricoes):
        """Prepara dados das inscrições para exibição na tabela."""
        dados_formatados = []
        for inscricao in inscricoes:
            # Formatar data de inscrição
            try:
                data_insc_obj = datetime.strptime(inscricao['data_inscricao'], '%Y-%m-%d %H:%M:%S')
                data_insc_formatada = data_insc_obj.strftime('%d/%m/%Y')
            except:
                data_insc_formatada = inscricao['data_inscricao']

            dados_formatados.append([
                inscricao['evento_nome'],
                inscricao['evento_data'],
                data_insc_formatada,
                inscricao['kit_nome']
            ])
        return dados_formatados

    def preparar_dados_resultados(self, resultados):
        """Prepara dados dos resultados para exibição na tabela."""
        dados_formatados = []
        for resultado in resultados:
            classificacao_geral = resultado.get('classificacao_geral', '')
            classificacao_categoria = resultado.get('classificacao_categoria', '')
            
            classif_geral_str = f"{classificacao_geral}º" if classificacao_geral else "-"
            classif_cat_str = f"{classificacao_categoria}º" if classificacao_categoria else "-"

            dados_formatados.append([
                resultado['evento_nome'],
                resultado['tempo_final'],
                classif_geral_str,
                classif_cat_str
            ])
        return dados_formatados

    def abrir_painel_principal(self, atleta: Atleta):
        eventos_disponiveis = self.__evento_dao.get_all_disponiveis()
        dados_tabela_eventos = self.preparar_dados_eventos_disponiveis(eventos_disponiveis)
        
        # Carregar inscrições do atleta
        inscricoes = self.__inscricao_dao.get_all_by_atleta(atleta.cpf)
        dados_tabela_inscricoes = self.preparar_dados_inscricoes(inscricoes)
        
        # Carregar resultados do atleta em eventos publicados
        resultados = self.__resultado_dao.buscar_resultados_por_cpf_em_eventos_publicados(atleta.cpf)
        dados_tabela_resultados = self.preparar_dados_resultados(resultados)
        
        janela_painel = self.__tela_atleta.exibir_painel(
            atleta.nome, 
            dados_tabela_eventos,
            dados_tabela_inscricoes,
            dados_tabela_resultados
        )
        
        while True:
            evento, valores = janela_painel.read()
            if evento in(sg.WIN_CLOSED, '-SAIR-'):
                break
            if evento == '-EDITAR_INFOS-':
                self.abre_tela_editar(atleta)
                janela_painel['-TEXTO_BEM_VINDO-'].update(f'Bem-vindo, {atleta.nome}!')
            if evento == '-APAGAR_CONTA-':
                if sg.popup_yes_no(
                    'Tem certeza que deseja apagar sua conta? Todas as inscrições em eventos não concluídos serão deletadas. Essa ação não pode ser desfeita.',
                    title='Atenção'
                ) == 'Yes':
                    self.deletar_atleta_e_inscricoes_ativas(atleta)
                    self.__controlador_sistema.exibir_popup_sucesso('Conta apagada com sucesso.')
                    break
            if evento == '-CANCELAR_INSCRICAO-':
                indices_selecionados = valores['-TABELA_INSCRICOES-']
                if not indices_selecionados:
                    self.__controlador_sistema.exibir_popup_erro("Por favor, selecione uma inscrição na tabela primeiro.")
                    continue
                
                indice_selecionado = indices_selecionados[0]
                inscricao_selecionada = inscricoes[indice_selecionado]
                
                # Validar se pode cancelar (verificar data_limite_cred)
                try:
                    data_limite_obj = datetime.strptime(inscricao_selecionada['data_limite_cred'], '%d/%m/%Y')
                    if data_limite_obj < datetime.now():
                        self.__controlador_sistema.exibir_popup_erro("O prazo para cancelamento já expirou.")
                        continue
                except ValueError:
                    self.__controlador_sistema.exibir_popup_erro("Data limite de cancelamento inválida.")
                    continue
                
                # Confirmar cancelamento
                if sg.popup_yes_no(
                    f'Deseja realmente cancelar sua inscrição no evento "{inscricao_selecionada["evento_nome"]}"?',
                    title='Confirmar Cancelamento'
                ) == 'Yes':
                    sucesso = self.__inscricao_dao.delete_by_atleta_e_evento(
                        atleta.cpf,
                        inscricao_selecionada['evento_id']
                    )
                    if sucesso:
                        self.__controlador_sistema.exibir_popup_sucesso("Inscrição cancelada com sucesso.")
                        # Atualizar lista de inscrições
                        inscricoes = self.__inscricao_dao.get_all_by_atleta(atleta.cpf)
                        dados_tabela_inscricoes = self.preparar_dados_inscricoes(inscricoes)
                        janela_painel['-TABELA_INSCRICOES-'].update(values=dados_tabela_inscricoes)
                    else:
                        self.__controlador_sistema.exibir_popup_erro("Erro ao cancelar inscrição.")
            if evento == '-VER_RESULTADO_INDIVIDUAL-':
                indices_selecionados = valores['-TABELA_RESULTADOS-']
                if not indices_selecionados:
                    self.__controlador_sistema.exibir_popup_erro("Por favor, selecione um resultado na tabela primeiro.")
                    continue
                
                indice_selecionado = indices_selecionados[0]
                resultado_selecionado = resultados[indice_selecionado]
                
                # Exibir resultado individual
                self.__tela_resultados.exibir_resultado_individual(
                    resultado_selecionado['evento_nome'],
                    resultado_selecionado
                )
            if evento == '-INSCREVER_EVENTO-':
                indices_selecionados = valores['-TABELA_EVENTOS-']
                if not indices_selecionados:
                    self.__controlador_sistema.exibir_popup_erro("Por favor, selecione um evento na tabela primeiro.")
                    continue
                
                indice_selecionado = indices_selecionados[0]
                evento_selecionado = eventos_disponiveis[indice_selecionado]
                
                # Verificar se o evento tem ID
                if not hasattr(evento_selecionado, 'id') or not evento_selecionado.id:
                    self.__controlador_sistema.exibir_popup_erro("Erro ao obter informações do evento.")
                    continue
                
                # Abrir tela de inscrição
                self.__controlador_sistema.abrir_tela_inscricao_atleta(evento_selecionado.id, atleta)
                
                # Atualizar lista de inscrições após possível nova inscrição
                inscricoes = self.__inscricao_dao.get_all_by_atleta(atleta.cpf)
                dados_tabela_inscricoes = self.preparar_dados_inscricoes(inscricoes)
                janela_painel['-TABELA_INSCRICOES-'].update(values=dados_tabela_inscricoes)
                
                # Atualizar lista de eventos disponíveis (pode ter mudado o status)
                eventos_disponiveis = self.__evento_dao.get_all_disponiveis()
                dados_tabela_eventos = self.preparar_dados_eventos_disponiveis(eventos_disponiveis)
                janela_painel['-TABELA_EVENTOS-'].update(values=dados_tabela_eventos)
        janela_painel.close()

    def deletar_atleta_e_inscricoes_ativas(self, atleta: Atleta):
        """
        Deleta a conta do atleta e todas as inscrições em eventos não concluídos.
        Um evento é considerado não concluído se sua data for hoje ou uma data futura.
        """
        # Buscar todas as inscrições do atleta
        inscricoes = self.__inscricao_dao.get_all_by_atleta(atleta.cpf)
        agora = datetime.now()

        for inscricao in inscricoes:
            try:
                data_evento_obj = datetime.strptime(inscricao['evento_data'], '%d/%m/%Y')
                # Eventos não concluídos: data do evento hoje ou no futuro
                if data_evento_obj >= agora:
                    self.__inscricao_dao.delete_by_atleta_e_evento(
                        atleta.cpf,
                        inscricao['evento_id']
                    )
            except ValueError:
                # Se a data estiver inválida, por segurança considera como não concluído e remove
                self.__inscricao_dao.delete_by_atleta_e_evento(
                    atleta.cpf,
                    inscricao['evento_id']
                )

        # Remover o atleta do cadastro
        self.__usuario_dao.remove(atleta.cpf)

    def abre_tela_editar(self, atleta:Atleta):
        evento, valores = self.__tela_cadastro.exibir_janela_edicao(atleta.nome, atleta.email)
        if evento is None or evento == sg.WIN_CLOSED or evento == '-VOLTAR-':
            return

        if evento == '-ATUALIZAR-':
            novo_nome = valores['-NOME-']
            novo_email = valores['-EMAIL-']
            nova_senha = valores['-SENHA-']
            try:
                if nova_senha and nova_senha.strip():
                    senha_pura = nova_senha.encode('utf-8')
                    senha_hash = bcrypt.hashpw(senha_pura, bcrypt.gensalt()).decode('utf-8')
                    atleta.set_senha_hash(senha_hash)
                if novo_nome and novo_nome.strip() and novo_nome != atleta.nome:
                    atleta.nome = novo_nome
                if novo_email and novo_nome.strip() and novo_email != atleta.email:
                    atleta.email = novo_email
                self.__usuario_dao.update(atleta)
                self.__controlador_sistema.exibir_popup_sucesso('Dados atualizados com sucesso')
            except ValueError as e:
                self.__controlador_sistema.exibir_popup_erro(str(e))