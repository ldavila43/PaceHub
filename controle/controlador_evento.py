import FreeSimpleGUI as sg
from entidade.organizador import Organizador
from limite.tela_evento import TelaEvento
from entidade.evento import Evento
from entidade.kit_de_corrida import KitDeCorrida
from datetime import datetime
from persistencia.evento_dao import EventoDAO
from persistencia.usuario_dao import UsuarioDAO


class ControladorEvento:
    def __init__(self, controlador_sistema, evento_dao: EventoDAO, usuario_dao: UsuarioDAO):
        self.__controlador_sistema = controlador_sistema
        self.__tela_evento = TelaEvento()
        self.__evento_dao = evento_dao
        self.__usuario_dao = usuario_dao

    def abre_tela_novo_evento(self, organizador_logado: Organizador):

        janela_principal = self.__tela_evento.exibir_janela_novo_evento()
        kits_do_evento_obj = []

        while True:
            window, event, values = sg.read_all_windows()

            if window == janela_principal and event in (sg.WIN_CLOSED, '-CANCELAR-'):
                break

            if event == '-BOTAO_CALENDARIO_EVENTO-' or event == '-BOTAO_CALENDARIO_CANCEL-':
                meses = ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
                         'Outubro', 'Novembro', 'Dezembro')
                dias = ('Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb')

                data_tuple = sg.popup_get_date(
                    month_names=meses,
                    day_abbreviations=dias,
                    title="Selecione uma data"
                )

                if data_tuple:
                    mes, dia, ano = data_tuple
                    data_formatada = f"{dia:02d}/{mes:02d}/{ano}"

                    if event == '-BOTAO_CALENDARIO_EVENTO-':
                        janela_principal['-DATA_EVENTO-'].update(data_formatada)
                    else:
                        janela_principal['-DATA_CANCEL-'].update(data_formatada)

            if event == '-CADASTRAR_KITS-':
                janela_kits = self.__tela_evento.exibir_janela_cadastro_kit([str(k) for k in kits_do_evento_obj])
                kit_sendo_editado: KitDeCorrida | None = None
                while True:
                    event_kit, values_kit = janela_kits.read()
                    if event_kit in (sg.WIN_CLOSED, '-SALVAR_KITS-'):
                        break

                    if event_kit == '-ADICIONAR_KIT-':
                        nome = values_kit['-NOME_KIT-']
                        descricao = values_kit['-DESCRICAO-']
                        valor_str = values_kit['-VALOR-']

                        if nome and descricao and valor_str:
                            try:
                                valor = float(valor_str.replace(',', '.'))
                                novo_kit = KitDeCorrida(nome, descricao, valor)
                                kits_do_evento_obj.append(novo_kit)
                                janela_kits['-LISTA_KITS-'].update(values=[str(k) for k in kits_do_evento_obj])

                                janela_kits['-NOME_KIT-'].update('')
                                janela_kits['-DESCRICAO-'].update('')
                                janela_kits['-VALOR-'].update('')
                            except ValueError:
                                self.__controlador_sistema.exibir_popup_erro(
                                    'O valor do kit deve ser um número válido.')
                        else:
                            self.__controlador_sistema.exibir_popup_erro('Todos os campos do kit são obrigatórios.')

                    if event_kit == '-REMOVER_KIT-':
                        selecionados = values_kit['-LISTA_KITS-']
                        if selecionados:
                            kit_str_para_remover = selecionados[0]
                            kit_para_remover = next((k for k in kits_do_evento_obj if str(k) == kit_str_para_remover),
                                                    None)

                            if kit_para_remover:
                                kits_do_evento_obj.remove(kit_para_remover)
                                janela_kits['-LISTA_KITS-'].update(values=[str(k) for k in kits_do_evento_obj])
                        
                    if event_kit == '-EDITAR_KIT-':
                        selecionados = values_kit['-LISTA_KITS-']
                        if not selecionados:
                            self.__controlador_sistema.exibir_popup_erro("Por favor, selecione um kit da lista para editar.")
                            continue

                        kit_str_para_editar = selecionados[0]
                        kit_para_editar = next((k for k in kits_do_evento_obj if str(k) == kit_str_para_editar), None)

                        if kit_para_editar:
                            kit_sendo_editado = kit_para_editar
                            
                            janela_kits['-NOME_KIT-'].update(kit_sendo_editado.nome)
                            janela_kits['-DESCRICAO-'].update(kit_sendo_editado.descricao)
                            valor_formatado = f'{kit_sendo_editado.valor:.2f}'.replace('.', ',')
                            janela_kits['-VALOR-'].update(valor_formatado)
                            
                            janela_kits['-ADICIONAR_KIT-'].update(visible=False)
                            janela_kits['-SALVAR_EDICAO-'].update(visible=True)
                            janela_kits['-CANCELAR_EDICAO-'].update(visible=True)
                            
                            janela_kits['-EDITAR_KIT-'].update(disabled=True)
                            janela_kits['-REMOVER_KIT-'].update(disabled=True)

                    if event_kit == '-SALVAR_EDICAO-':
                        nome = values_kit['-NOME_KIT-']
                        descricao = values_kit['-DESCRICAO-']
                        valor_str = values_kit['-VALOR-']
                        
                        if not (nome and descricao and valor_str):
                            self.__controlador_sistema.exibir_popup_erro('Todos os campos do kit são obrigatórios.')
                            continue
                        
                        try:
                            valor = float(valor_str.replace(',', '.'))
                        except ValueError:
                            self.__controlador_sistema.exibir_popup_erro('O valor do kit deve ser um número válido.')
                            continue
                        
                        if kit_sendo_editado:
                            kit_sendo_editado.nome = nome
                            kit_sendo_editado.descricao = descricao
                            kit_sendo_editado.valor = valor

                        kit_sendo_editado = None
                        janela_kits['-LISTA_KITS-'].update(values=[str(k) for k in kits_do_evento_obj])
                        janela_kits['-NOME_KIT-'].update('')
                        janela_kits['-DESCRICAO-'].update('')
                        janela_kits['-VALOR-'].update('')
                        
                        janela_kits['-ADICIONAR_KIT-'].update(visible=True)
                        janela_kits['-SALVAR_EDICAO-'].update(visible=False)
                        janela_kits['-CANCELAR_EDICAO-'].update(visible=False)
                        janela_kits['-EDITAR_KIT-'].update(disabled=False)
                        janela_kits['-REMOVER_KIT-'].update(disabled=False)

                    if event_kit == '-CANCELAR_EDICAO-':
                        kit_sendo_editado = None

                        janela_kits['-NOME_KIT-'].update('')
                        janela_kits['-DESCRICAO-'].update('')
                        janela_kits['-VALOR-'].update('')

                        janela_kits['-ADICIONAR_KIT-'].update(visible=True)
                        janela_kits['-SALVAR_EDICAO-'].update(visible=False)
                        janela_kits['-CANCELAR_EDICAO-'].update(visible=False)
                        janela_kits['-EDITAR_KIT-'].update(disabled=False)
                        janela_kits['-REMOVER_KIT-'].update(disabled=False)
                janela_kits.close()
                janela_principal['-STATUS_KITS-'].update(f'{len(kits_do_evento_obj)} kit(s) cadastrado(s).',
                                                         text_color='lime')

            if event == '-SALVAR_EVENTO-':
                campos_obrigatorios = ['-NOME_EVENTO-', '-DATA_EVENTO-', '-DISTANCIA-', '-LOCAL-', '-HORAS-',
                                       '-MINUTOS-', '-DATA_CANCEL-']
                if any(not values[campo] for campo in campos_obrigatorios) or not kits_do_evento_obj:
                    self.__controlador_sistema.exibir_popup_erro(
                        'Por favor, preencha todos os campos e cadastre pelo menos um kit.')
                    continue

                try:
                    data_evento_str = values['-DATA_EVENTO-']
                    data_cancel_str = values['-DATA_CANCEL-']

                    data_evento_obj = datetime.strptime(data_evento_str, '%d/%m/%Y')
                    data_cancel_obj = datetime.strptime(data_cancel_str, '%d/%m/%Y')

                    if data_cancel_obj > data_evento_obj:
                        self.__controlador_sistema.exibir_popup_erro(
                            'A data limite para cancelamento não pode ser posterior à data do evento.')
                        continue
                    if data_evento_obj < datetime.now():
                        self.__controlador_sistema.exibir_popup_erro('A data do evento não pode ser no passado.')
                        continue

                except ValueError:
                    self.__controlador_sistema.exibir_popup_erro('As datas inseridas não são válidas.')
                    continue

                

                try:
                    horas_int = int(values['-HORAS-'])
                    minutos_int = int(values['-MINUTOS-'])
                    
                
                    if not (0 <= horas_int <= 24) or not (0 <= minutos_int <= 59):
                         raise ValueError("Valores fora do intervalo permitido.")
                    if horas_int == 24 and minutos_int > 0:
                         raise ValueError("Tempo máximo não pode exceder 24h00.")
                
                except ValueError:
                    self.__controlador_sistema.exibir_popup_erro(
                        'O tempo de corte (horas e minutos) deve ser um número válido (Ex: 6 horas e 0 minutos).')
                    continue 


                tempo_corte = f"{horas_int}:{minutos_int}" 
                distancia_str = values['-DISTANCIA-']

                evento = Evento(
                    nome=values['-NOME_EVENTO-'],
                    data=values['-DATA_EVENTO-'],
                    distancia=int(distancia_str),
                    local_largada=values['-LOCAL-'],
                    tempo_corte=tempo_corte,
                    data_limite_cred=values['-DATA_CANCEL-'],
                    organizador_cpf=organizador_logado.cpf
                )
                evento.kits = kits_do_evento_obj

                try:
                    self.__evento_dao.add_evento(evento)
                    self.__controlador_sistema.exibir_popup_sucesso('Evento criado e salvo no banco de dados.')
                    break
                except Exception as e:
                    self.__controlador_sistema.exibir_popup_erro(f'Erro ao salvar evento no banco de dados: {e}')

        janela_principal.close()

    def abre_tela_editar_evento(self, evento_para_editar: Evento, organizador_logado: Organizador):
        
        kits_do_evento_obj = self.__evento_dao.get_kits_by_evento_id(evento_para_editar.id)
        evento_para_editar.kits = kits_do_evento_obj 

        janela_principal = self.__tela_evento.exibir_janela_novo_evento()
        
        janela_principal['-NOME_EVENTO-'].update(evento_para_editar.nome)
        janela_principal['-DATA_EVENTO-'].update(evento_para_editar.data)
        janela_principal['-DISTANCIA-'].update(evento_para_editar.distancia)
        janela_principal['-LOCAL-'].update(evento_para_editar.local_largada)
        
        try:
            horas, minutos = evento_para_editar.tempo_corte.split(':')
        except ValueError:
            horas, minutos = '6', '0' 
        janela_principal['-HORAS-'].update(horas)
        janela_principal['-MINUTOS-'].update(minutos)
        janela_principal['-DATA_CANCEL-'].update(evento_para_editar.data_limite_cred)
        janela_principal['-STATUS_KITS-'].update(f'{len(kits_do_evento_obj)} kit(s) cadastrado(s).', text_color='lime')
        
        while True:
            window, event, values = sg.read_all_windows()

            if window == janela_principal and event in (sg.WIN_CLOSED, '-CANCELAR-'):
                break
            
            if event == '-BOTAO_CALENDARIO_EVENTO-' or event == '-BOTAO_CALENDARIO_CANCEL-':
                # ... (copie e cole o bloco de calendário do método "abre_tela_novo_evento") ...
                meses = ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
                         'Outubro', 'Novembro', 'Dezembro')
                dias = ('Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb')

                data_tuple = sg.popup_get_date(
                    month_names=meses,
                    day_abbreviations=dias,
                    title="Selecione uma data"
                )

                if data_tuple:
                    mes, dia, ano = data_tuple
                    data_formatada = f"{dia:02d}/{mes:02d}/{ano}"

                    if event == '-BOTAO_CALENDARIO_EVENTO-':
                        janela_principal['-DATA_EVENTO-'].update(data_formatada)
                    else:
                        janela_principal['-DATA_CANCEL-'].update(data_formatada)

            if event == '-CADASTRAR_KITS-':
                # ... (copie e cole TODO o bloco "-CADASTRAR_KITS-" do método "abre_tela_novo_evento") ...
                # ... (incluindo a implementação do CRUD de kits que fizemos) ...
                kit_sendo_editado: KitDeCorrida | None = None
                janela_kits = self.__tela_evento.exibir_janela_cadastro_kit([str(k) for k in kits_do_evento_obj])

                while True:
                    event_kit, values_kit = janela_kits.read()
                    if event_kit in (sg.WIN_CLOSED, '-SALVAR_KITS-'):
                        break
                    
                    # ... (cole toda a lógica de -ADICIONAR_KIT-, -REMOVER_KIT-, -EDITAR_KIT-, etc) ...
                    if event_kit == '-ADICIONAR_KIT-':
                        nome = values_kit['-NOME_KIT-']
                        descricao = values_kit['-DESCRICAO-']
                        valor_str = values_kit['-VALOR-']

                        if nome and descricao and valor_str:
                            try:
                                valor = float(valor_str.replace(',', '.'))
                                novo_kit = KitDeCorrida(nome, descricao, valor)
                                kits_do_evento_obj.append(novo_kit)
                                janela_kits['-LISTA_KITS-'].update(values=[str(k) for k in kits_do_evento_obj])

                                janela_kits['-NOME_KIT-'].update('')
                                janela_kits['-DESCRICAO-'].update('')
                                janela_kits['-VALOR-'].update('')
                            except ValueError:
                                self.__controlador_sistema.exibir_popup_erro(
                                    'O valor do kit deve ser um número válido.')
                        else:
                            self.__controlador_sistema.exibir_popup_erro('Todos os campos do kit são obrigatórios.')

                    if event_kit == '-REMOVER_KIT-':
                        selecionados = values_kit['-LISTA_KITS-']
                        if selecionados:
                            kit_str_para_remover = selecionados[0]
                            kit_para_remover = next((k for k in kits_do_evento_obj if str(k) == kit_str_para_remover),
                                                    None)

                            if kit_para_remover:
                                kits_do_evento_obj.remove(kit_para_remover)
                                janela_kits['-LISTA_KITS-'].update(values=[str(k) for k in kits_do_evento_obj])
                    
                    # --- Lógica de Editar Kit (Colar o código da nossa conversa anterior) ---
                    if event_kit == '-EDITAR_KIT-':
                        selecionados = values_kit['-LISTA_KITS-']
                        if not selecionados:
                            self.__controlador_sistema.exibir_popup_erro("Por favor, selecione um kit da lista para editar.")
                            continue
                        kit_str_para_editar = selecionados[0]
                        kit_para_editar = next((k for k in kits_do_evento_obj if str(k) == kit_str_para_editar), None)
                        if kit_para_editar:
                            kit_sendo_editado = kit_para_editar
                            janela_kits['-NOME_KIT-'].update(kit_sendo_editado.nome)
                            janela_kits['-DESCRICAO-'].update(kit_sendo_editado.descricao)
                            valor_formatado = f'{kit_sendo_editado.valor:.2f}'.replace('.', ',')
                            janela_kits['-VALOR-'].update(valor_formatado)
                            janela_kits['-ADICIONAR_KIT-'].update(visible=False)
                            janela_kits['-SALVAR_EDICAO-'].update(visible=True)
                            janela_kits['-CANCELAR_EDICAO-'].update(visible=True)
                            janela_kits['-EDITAR_KIT-'].update(disabled=True)
                            janela_kits['-REMOVER_KIT-'].update(disabled=True)
                    if event_kit == '-SALVAR_EDICAO-':
                        nome = values_kit['-NOME_KIT-']
                        descricao = values_kit['-DESCRICAO-']
                        valor_str = values_kit['-VALOR-']
                        if not (nome and descricao and valor_str):
                            self.__controlador_sistema.exibir_popup_erro('Todos os campos do kit são obrigatórios.')
                            continue
                        try:
                            valor = float(valor_str.replace(',', '.'))
                        except ValueError:
                            self.__controlador_sistema.exibir_popup_erro('O valor do kit deve ser um número válido.')
                            continue
                        if kit_sendo_editado:
                            kit_sendo_editado.nome = nome
                            kit_sendo_editado.descricao = descricao
                            kit_sendo_editado.valor = valor
                        kit_sendo_editado = None
                        janela_kits['-LISTA_KITS-'].update(values=[str(k) for k in kits_do_evento_obj])
                        janela_kits['-NOME_KIT-'].update('')
                        janela_kits['-DESCRICAO-'].update('')
                        janela_kits['-VALOR-'].update('')
                        janela_kits['-ADICIONAR_KIT-'].update(visible=True)
                        janela_kits['-SALVAR_EDICAO-'].update(visible=False)
                        janela_kits['-CANCELAR_EDICAO-'].update(visible=False)
                        janela_kits['-EDITAR_KIT-'].update(disabled=False)
                        janela_kits['-REMOVER_KIT-'].update(disabled=False)
                    if event_kit == '-CANCELAR_EDICAO-':
                        kit_sendo_editado = None
                        janela_kits['-NOME_KIT-'].update('')
                        janela_kits['-DESCRICAO-'].update('')
                        janela_kits['-VALOR-'].update('')
                        janela_kits['-ADICIONAR_KIT-'].update(visible=True)
                        janela_kits['-SALVAR_EDICAO-'].update(visible=False)
                        janela_kits['-CANCELAR_EDICAO-'].update(visible=False)
                        janela_kits['-EDITAR_KIT-'].update(disabled=False)
                        janela_kits['-REMOVER_KIT-'].update(disabled=False)

                janela_kits.close()
                janela_principal['-STATUS_KITS-'].update(f'{len(kits_do_evento_obj)} kit(s) cadastrado(s).',
                                                         text_color='lime')

            # --- LÓGICA DE SALVAR (AQUI ESTÁ A MUDANÇA) ---
            if event == '-SALVAR_EVENTO-':
                # Validações (copie e cole as validações de campos obrigatórios, datas e tempo de corte)
                campos_obrigatorios = ['-NOME_EVENTO-', '-DATA_EVENTO-', '-DISTANCIA-', '-LOCAL-', '-HORAS-',
                                       '-MINUTOS-', '-DATA_CANCEL-']
                if any(not values[campo] for campo in campos_obrigatorios) or not kits_do_evento_obj:
                    self.__controlador_sistema.exibir_popup_erro(
                        'Por favor, preencha todos os campos e cadastre pelo menos um kit.')
                    continue
                try:
                    data_evento_str = values['-DATA_EVENTO-']
                    data_cancel_str = values['-DATA_CANCEL-']
                    data_evento_obj = datetime.strptime(data_evento_str, '%d/%m/%Y')
                    data_cancel_obj = datetime.strptime(data_cancel_str, '%d/%m/%Y')
                    if data_cancel_obj > data_evento_obj:
                        self.__controlador_sistema.exibir_popup_erro(
                            'A data limite para cancelamento não pode ser posterior à data do evento.')
                        continue
                    # Não vamos mais checar se a data é no passado. O usuário pode querer editar um evento antigo.
                except ValueError:
                    self.__controlador_sistema.exibir_popup_erro('As datas inseridas não são válidas.')
                    continue
                try:
                    horas_int = int(values['-HORAS-'])
                    minutos_int = int(values['-MINUTOS-'])
                    if not (0 <= horas_int <= 24) or not (0 <= minutos_int <= 59):
                         raise ValueError("Valores fora do intervalo permitido.")
                    if horas_int == 24 and minutos_int > 0:
                         raise ValueError("Tempo máximo não pode exceder 24h00.")
                except ValueError:
                    self.__controlador_sistema.exibir_popup_erro(
                        'O tempo de corte (horas e minutos) deve ser um número válido (Ex: 6 horas e 0 minutos).')
                    continue
                
                tempo_corte = f"{horas_int}:{minutos_int}"
                distancia_str = values['-DISTANCIA-']

                evento_para_editar.nome = values['-NOME_EVENTO-']
                evento_para_editar.data = values['-DATA_EVENTO-']
                evento_para_editar.distancia = int(distancia_str)
                evento_para_editar.local_largada = values['-LOCAL-']
                evento_para_editar.tempo_corte = tempo_corte
                evento_para_editar.data_limite_cred = values['-DATA_CANCEL-']
                
                try:
                    self.__evento_dao.update_evento(evento_para_editar)
                    self.__controlador_sistema.exibir_popup_sucesso('Evento ATUALIZADO no banco de dados.')
                    break 
                except Exception as e:
                    self.__controlador_sistema.exibir_popup_erro(f'Erro ao atualizar evento no banco de dados: {e}')

        janela_principal.close()