import FreeSimpleGUI as sg

class TelaAtleta:
    def __init__(self):
        pass

    def exibir_painel(self, nome_atleta: str, dados_eventos, dados_inscricoes=None, dados_resultados=None):
        sg.theme('DarkBlue14')

        cabecalhos_eventos = ['Nome do Evento', 'Data', 'Distância', 'Status']
        cabecalhos_inscricoes = ['Nome do Evento', 'Data do Evento', 'Data Inscrição', 'Kit']
        cabecalhos_resultados = ['Nome do Evento', 'Tempo', 'Classificação Geral', 'Classificação Categoria']

        # Layout de cada aba
        layout_eventos = [
            [sg.Text('Eventos Disponíveis', font=('Helvetica', 18))],
            [sg.Table(
                values=dados_eventos if dados_eventos else [],
                headings=cabecalhos_eventos,
                key='-TABELA_EVENTOS-',
                auto_size_columns=False,
                col_widths=[25, 10, 8, 15],
                justification='left',
                num_rows=10,
                enable_events=True,
                display_row_numbers=False,
                expand_x=True,
                expand_y=True
            )],
            [sg.Button('Inscrever-se no Evento', key='-INSCREVER_EVENTO-')]
        ]

        layout_inscricoes = [
            [sg.Text('Minhas Inscrições', font=('Helvetica', 18))],
            [sg.Table(
                values=dados_inscricoes if dados_inscricoes else [],
                headings=cabecalhos_inscricoes,
                key='-TABELA_INSCRICOES-',
                auto_size_columns=False,
                col_widths=[25, 12, 12, 20],
                justification='left',
                num_rows=12,
                enable_events=True,
                display_row_numbers=False,
                expand_x=True,
                expand_y=True
            )],
            [sg.Button('Cancelar Inscrição', key='-CANCELAR_INSCRICAO-')]
        ]

        layout_resultados = [
            [sg.Text('Meus Resultados', font=('Helvetica', 18))],
            [sg.Table(
                values=dados_resultados if dados_resultados else [],
                headings=cabecalhos_resultados,
                key='-TABELA_RESULTADOS-',
                auto_size_columns=False,
                col_widths=[25, 12, 20, 25],
                justification='left',
                num_rows=12,
                enable_events=True,
                display_row_numbers=False,
                expand_x=True,
                expand_y=True
            )],
            [sg.Button('Ver Detalhes do Resultado', key='-VER_RESULTADO_INDIVIDUAL-')]
        ]

        # Abas
        tab_eventos = sg.Tab('Eventos Disponíveis', layout_eventos, key='-TAB_EVENTOS-')
        tab_inscricoes = sg.Tab('Minhas Inscrições', layout_inscricoes, key='-TAB_INSCRICOES-')
        tab_resultados = sg.Tab('Meus Resultados', layout_resultados, key='-TAB_RESULTADOS-')

        tab_group = sg.TabGroup(
            [[tab_eventos, tab_inscricoes, tab_resultados]],
            key='-TAB_GROUP-',
            expand_x=True,
            expand_y=True
        )

        # Coluna com botões à direita (mesmo tamanho do organizador)
        tamanho_botao = (len('Editar informações do cadastro') + 2, 1)
        botoes_direita = [
            [sg.Button('Editar informações do cadastro', key='-EDITAR_INFOS-', size=tamanho_botao)],
            [sg.Button('Apagar Conta', key='-APAGAR_CONTA-', size=tamanho_botao)]
        ]

        layout = [
            [sg.Text('Painel do Atleta', font=('Helvetica', 25, 'bold')),
             sg.Push(),
             sg.Column(botoes_direita, element_justification='right', vertical_alignment='top')],
            [sg.Text(f'Bem-vindo, {nome_atleta}!', font=('Helvetica', 14), key='-TEXTO_BEM_VINDO-')],
            [sg.HSeparator()],
            [tab_group],
            [sg.Push(), sg.Button('Sair (Logout)', key='-SAIR-')]
        ]

        return sg.Window('PaceHub - Painel do Atleta', layout, finalize=True, size=(900, 700), resizable=True)