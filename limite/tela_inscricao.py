import FreeSimpleGUI as sg


class TelaInscricao:

    def __init__(self):
        pass

    def exibir_tela_gerenciar_kit(self, nome_evento: str):
        sg.theme('DarkBlue14')  # Mesmo tema da imagem

        layout_busca = [
            [sg.Text('Buscar por Nome ou CPF:'),
             sg.Input(key='-INPUT_BUSCA-', size=(30, 1)),
             sg.Button('Buscar', key='-BUSCAR-')]
        ]

        coluna_atleta = sg.Column([
            [sg.Text('Nome do Atleta:', size=(15, 1)), sg.Text('[Nome do Atleta]', key='-NOME_ATLETA-')],
            [sg.Text('CPF:', size=(15, 1)), sg.Text('[CPF do Atleta]', key='-CPF_ATLETA-')],
            [sg.Checkbox('Kit Entregue', key='-KIT_ENTREGUE-', disabled=True)]
        ])

        coluna_kit = sg.Column([
            [sg.Text('Kit:', size=(15, 1)), sg.Text('[Kit]', key='-NOME_KIT-')],
            [sg.Text('Valor:', size=(15, 1)), sg.Text('[R$ 0,00]', key='-VALOR_KIT-')],
        ])

        layout_dados = [[coluna_atleta, sg.VSeparator(), coluna_kit]]

        layout = [
            [sg.Text(f'Gerenciar Entrega de Kits - {nome_evento}', font=('Helvetica', 20, 'bold'))],
            [sg.Frame('Buscar Inscrição', layout_busca)],
            [sg.Frame('Dados da Inscrição', layout_dados)],
            [sg.Button('Salvar', key='-SALVAR-', disabled=True), sg.Button('Voltar', key='-VOLTAR-')]
        ]

        return sg.Window('PaceHub - Gerenciar Kits', layout, finalize=True, modal=True)

    def exibir_lista_inscritos(self, nome_evento: str, dados_inscritos: list):
        """Exibe uma janela com a lista de inscritos no evento."""
        sg.theme('DarkBlue14')

        cabecalhos = ['Nome', 'CPF', 'Data Inscrição', 'Kit', 'Status']

        # Preparar dados para a tabela
        dados_tabela = []
        for inscricao in dados_inscritos:
            # Formatar data de inscrição
            try:
                from datetime import datetime
                data_obj = datetime.strptime(inscricao['data_inscricao'], '%Y-%m-%d %H:%M:%S')
                data_formatada = data_obj.strftime('%d/%m/%Y %H:%M')
            except:
                data_formatada = inscricao['data_inscricao']

            # Formatar status
            status_map = {0: 'Pendente', 1: 'Paga'}
            status = status_map.get(inscricao['status'], 'Desconhecido')

            dados_tabela.append([
                inscricao['atleta_nome'],
                inscricao['atleta_cpf'],
                data_formatada,
                inscricao['kit_nome'],
                status
            ])

        layout = [
            [sg.Text(f'Lista de Inscritos - {nome_evento}', font=('Helvetica', 20, 'bold'))],
            [sg.HSeparator()],
            [sg.Text(f'Total de inscritos: {len(dados_tabela)}', font=('Helvetica', 12))],
            [sg.Table(
                values=dados_tabela,
                headings=cabecalhos,
                auto_size_columns=False,
                col_widths=[30, 15, 18, 25, 12],
                justification='left',
                num_rows=min(15, len(dados_tabela)) if dados_tabela else 1,
                display_row_numbers=False,
                expand_x=True,
                expand_y=True,
                key='-TABELA_INSCRITOS-'
            )],
            [sg.Button('Fechar', key='-FECHAR-')]
        ]

        janela = sg.Window(
            f'PaceHub - Lista de Inscritos - {nome_evento}',
            layout,
            finalize=True,
            size=(900, 600),
            resizable=True
        )

        while True:
            evento, valores = janela.read()
            if evento in (sg.WIN_CLOSED, '-FECHAR-'):
                break

        janela.close()

    def exibir_tela_inscricao_atleta(self, nome_evento: str, nome_atleta: str, cpf_atleta: str, kits: list):
        """Exibe a tela de inscrição para o atleta se inscrever em um evento."""
        sg.theme('DarkBlue14')

        termo_responsabilidade = """Declaro que participo deste evento por livre e espontânea vontade, isentando de qualquer responsabilidade os organizadores, patrocinadores e realizadores, em meu nome e de meus sucessores. Declaro estar em boas condições de saúde e ter treinado apropriadamente para a prova."""

        # Preparar lista de kits para o dropdown
        combo_items = []
        for kit in kits:
            combo_items.append(f"{kit.nome} - R${kit.valor:.2f}")

        default_combo = combo_items[0] if combo_items else ''

        layout = [
            [sg.Text(f'Inscrição: {nome_evento}', font=('Helvetica', 20))],
            [sg.HorizontalSeparator()],
            [sg.Text('Confirme seus dados cadastrais:')],
            [sg.Text('Nome:'), sg.Text(nome_atleta, key='-NOME-', size=(40, 1))],
            [sg.Text('CPF:'), sg.Text(cpf_atleta, key='-CPF-', size=(20, 1))],
            [sg.HorizontalSeparator()],
            [sg.Text('Escolha do Kit*', size=(15, 1)),
             sg.Combo(combo_items, default_value=default_combo, readonly=True, key='-KIT-', size=(30, 1))],
            [sg.HorizontalSeparator()],
            [sg.Text('Ficha Médica e Termo de Responsabilidade', font=('Helvetica', 12))],
            [sg.Text('Preencha a ficha médica'), 
             sg.Button('Preencher', key='-FICHA_MEDICA-', size=(10, 1))],
            [sg.Multiline(default_text=termo_responsabilidade, disabled=True, size=(60, 8), 
                         autoscroll=True, key='-TERMO_TEXT-')],
            [sg.Checkbox('Li e aceito os termos de responsabilidade e isenção de riscos.', 
                        key='-TERMO_ACEITO-')],
            [sg.Checkbox('Atesto que estou em condições de saúde aptas para a prática da atividade física.', 
                        key='-SAUDE_OK-')],
            [sg.VPush()],
            [sg.Button('Confirmar Inscrição', key='-CONFIRMAR-'), 
             sg.Button('Voltar', key='-VOLTAR-')]
        ]

        return sg.Window('PaceHub - Inscrição', layout, size=(600, 550), finalize=True, resizable=True)