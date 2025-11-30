import FreeSimpleGUI as sg


class TelaFichaMedica:
    def __init__(self):
        pass

    def exibir_tela_ficha_medica(self):
        """Exibe a tela do questionário PAR-Q (Physical Activity Readiness Questionnaire)."""
        sg.theme('DarkBlue14')

        layout = [
            [sg.Text('Questionário de Prontidão para Atividade Física (PAR-Q)', 
                    font=('Helvetica', 20))],
            [sg.HorizontalSeparator()],
            [sg.Text('Por favor, leia as perguntas cuidadosamente e responda cada uma honestamente.', 
                    font=('Helvetica', 12))],
            [sg.Text('Marque SIM ou NÃO para cada pergunta:', font=('Helvetica', 10))],
            [sg.HorizontalSeparator()],
            
            # Pergunta 1
            [sg.Text('1. Algum médico já disse que você possui algum problema de coração e que só deveria realizar atividade física supervisionado por profissionais de saúde?', 
                    font=('Helvetica', 10), size=(80, 2))],
            [sg.Radio('SIM', 'pergunta1', key='-PERGUNTA1_SIM-'), 
             sg.Radio('NÃO', 'pergunta1', key='-PERGUNTA1_NAO-', default=True)],
            [sg.HorizontalSeparator()],
            
            # Pergunta 2
            [sg.Text('2. Você sente dores no peito quando pratica atividade física?', 
                    font=('Helvetica', 10))],
            [sg.Radio('SIM', 'pergunta2', key='-PERGUNTA2_SIM-'), 
             sg.Radio('NÃO', 'pergunta2', key='-PERGUNTA2_NAO-', default=True)],
            [sg.HorizontalSeparator()],
            
            # Pergunta 3
            [sg.Text('3. No último mês, você sentiu dores no peito quando praticou atividade física?', 
                    font=('Helvetica', 10))],
            [sg.Radio('SIM', 'pergunta3', key='-PERGUNTA3_SIM-'), 
             sg.Radio('NÃO', 'pergunta3', key='-PERGUNTA3_NAO-', default=True)],
            [sg.HorizontalSeparator()],
            
            # Pergunta 4
            [sg.Text('4. Você apresenta desequilíbrio devido à tontura e/ou perda de consciência?', 
                    font=('Helvetica', 10))],
            [sg.Radio('SIM', 'pergunta4', key='-PERGUNTA4_SIM-'), 
             sg.Radio('NÃO', 'pergunta4', key='-PERGUNTA4_NAO-', default=True)],
            [sg.HorizontalSeparator()],
            
            # Pergunta 5
            [sg.Text('5. Você possui algum problema ósseo ou articular que poderia ser piorado pela atividade física?', 
                    font=('Helvetica', 10), size=(80, 2))],
            [sg.Radio('SIM', 'pergunta5', key='-PERGUNTA5_SIM-'), 
             sg.Radio('NÃO', 'pergunta5', key='-PERGUNTA5_NAO-', default=True)],
            [sg.HorizontalSeparator()],
            
            # Pergunta 6
            [sg.Text('6. Sabe de alguma outra razão pela qual você não deve praticar atividade física?', 
                    font=('Helvetica', 10))],
            [sg.Radio('SIM', 'pergunta6', key='-PERGUNTA6_SIM-'), 
             sg.Radio('NÃO', 'pergunta6', key='-PERGUNTA6_NAO-', default=True)],
            [sg.HorizontalSeparator()],
            
            # Pergunta 7
            [sg.Text('7. Você toma atualmente algum medicamento para pressão arterial e/ou problema de coração?', 
                    font=('Helvetica', 10))],
            [sg.Radio('SIM', 'pergunta7', key='-PERGUNTA7_SIM-'), 
             sg.Radio('NÃO', 'pergunta7', key='-PERGUNTA7_NAO-', default=True)],
            [sg.HorizontalSeparator()],
            
            # Declaração
            [sg.Text('Declaração', font=('Helvetica', 15))],
            [sg.Checkbox('Atesto que estou em condições de saúde aptas para a prática da atividade física.', 
                        key='-DECLARACAO_SAUDE-')],
            [sg.HorizontalSeparator()],
            
            [sg.Text('* Campos obrigatórios', text_color='red')],
            [sg.Button('Salvar', key='-SALVAR-'), sg.Button('Voltar', key='-VOLTAR-')]
        ]

        return sg.Window('PaceHub - Ficha Médica (PAR-Q)', layout, finalize=True, resizable=True, size=(800, 700))

