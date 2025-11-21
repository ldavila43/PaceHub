import bcrypt
import FreeSimpleGUI as sg
import re
from entidade.organizador import Organizador
from limite.tela_cadastro import TelaCadastro


class ControladorOrganizador:
    def __init__(self, controlador_sistema, usuario_dao):
        self.__controlador_sistema = controlador_sistema
        self.__tela_cadastro = TelaCadastro()
        self.__usuario_dao = usuario_dao

    def abre_tela_cadastro(self):
        evento, valores = self.__tela_cadastro.exibir_janela_cadastro('Organizador')
        if evento is None or evento == sg.WIN_CLOSED or evento == '-VOLTAR-':
            return

        campos_obrigatorios = ['-NOME-', '-CPF-', '-EMAIL-', '-SENHA-']
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

                novo_organizador = Organizador(
                    nome=valores['-NOME-'],
                    cpf=valores['-CPF-'],
                    email=valores['-EMAIL-'],
                    senha_hash=senha_hash
                )
                self.__usuario_dao.add(novo_organizador)
                self.__controlador_sistema.exibir_popup_sucesso('Cadastro Efetuado com sucesso')

                print('Organizador adicionad à lista', novo_organizador.nome)
            except Exception as e:
                self.__controlador_sistema.exibir_popup_erro(f'Erro ao criar atleta: {e}')

    def listar_organizadores(self):
        print("\n--- LISTANDO ORGANIZADORES CADASTRADOS ---")
        todos_usuarios = self.__usuario_dao.get_all()

        organizadores_encontrados = False
        for usuario in todos_usuarios:
            if isinstance(usuario, Organizador):
                print(
                    f"Nome: {usuario.nome}, CPF: {usuario.cpf}, Email: {usuario.email}")
                organizadores_encontrados = True

        if not organizadores_encontrados:
            print("Nenhum Organizador cadastrado no momento.")
            self.__controlador_sistema.exibir_popup_sucesso("Nenhum organizador cadastrado.")
            return

        print("------------------------------------")
        self.__controlador_sistema.exibir_popup_sucesso("Lista de organizadores impressa no console/terminal!")