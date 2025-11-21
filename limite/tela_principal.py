# limite/tela_principal_psg.py
import FreeSimpleGUI as sg


class TelaPrincipal:

    def __init__(self):
        pass

    def exibir_janela_login(self):
        sg.theme('DarkBlue14')

        layout_login = [
            [sg.Text("CPF*", size=(5, 1)), sg.Input(key='-CPF_LOGIN-')],
            [sg.Text("Senha*", size=(5, 1)), sg.Input(key='-SENHA_LOGIN-', password_char='*')],
        ]

        layout = [
            [sg.Push(), sg.Text("PaceHub", font=("Helvetica", 25)), sg.Push()],
            [sg.Push(), sg.Text("Sua plataforma de gestão de corridas.", font=("Helvetica", 12)), sg.Push()],
            [sg.Frame("Login", layout_login, pad=(0, 10))],
            [sg.Button("Login", key='Login', expand_x=True, pad=(0, (10, 0)))],
            [sg.HSeparator(pad=(0, 10))],
            [sg.Text("Ainda não tem uma conta? Cadastre-se agora!", justification='center', expand_x=True)],
            [sg.Button("Cadastrar como Atleta", key='-CADASTRO_ATLETA-', expand_x=True, pad=(0, (10, 0)))],
            [sg.Button("Cadastrar como Organizador", key='-CADASTRO_ORGANIZADOR-', expand_x=True,pad=(0, (10, 0)))],
            [sg.Button("Criar Novo Evento", key='-CRIAR_EVENTO-', expand_x=True, pad=(0, (10, 0)))],
            [sg.Button("Listar Atletas", key='-LISTAR_ATLETAS-', expand_x=True, pad=(0, (10, 0)))],
            [sg.Button("Listar Organizadores", key='-LISTAR_ORGANIZADORES-', expand_x=True, pad=(0, (10, 0)))]
        ]

        janela = sg.Window("PaceHub - Bem-vindo", layout, element_justification='center', size=(400, 400))

        evento, valores = janela.read()
        janela.close()

        if evento == sg.WIN_CLOSED:
            return None, None

        return evento, valores