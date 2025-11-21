import FreeSimpleGUI as sg

class TelaOrganizador:
    def __init__(self):
        pass

    def exibir_painel(self, nome_organizador: str, dados_eventos: list):
        sg.theme('DarkBlue14')

        cabecalhos = ['Nome do Evento', 'Data', 'Inscritos', 'Status']

        layout_eventos = [
            [sg.Text('Meus Eventos', font=('Helvetica', 18))],
            [sg.Table(
                values=dados_eventos,
                headings=cabecalhos,
                key='-TABELA_EVENTOS-',
                auto_size_columns=False,
                col_widths=[25, 10, 8, 15],
                justification='left',
                num_rows=10,
                enable_events=True,
                display_row_numbers=False,
                expand_x=True
            )],
            [sg.Button('Gerenciar Entrega de Kits', key='-GERENCIAR_KITS-'),
             sg.Button('Editar Evento Selecionado', key='-EDITAR_EVENTO-'),
             sg.Button('Importar Tempo dos Participantes', key='-IMPORTAR_TEMPOS-')]
        ]

        layout = [
            [sg.Text('Painel do Organizador', font=('Helvetica', 25, 'bold'))],
            [sg.Text(f'Bem-vindo, {nome_organizador}!', font=('Helvetica', 14))],
            [sg.Button('Criar Novo Evento', key='-CRIAR_EVENTO-', size=(20, 2), pad=((0,0), (10, 20)))],
            [sg.HSeparator()],
            [sg.Frame('', layout_eventos, background_color=sg.theme_background_color(), border_width=0)],
            [sg.Push(), sg.Button('Sair (Logout)', key='-SAIR-')]
        ]

        return sg.Window('PaceHub - Painel do Organizador', layout, finalize=True, size=(800, 600))