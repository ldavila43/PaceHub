# limite/tela_importar_resultados.py
import FreeSimpleGUI as sg
from typing import Tuple
from controle.controlador_importacao import ControladorImportacao


def criar_janela_importar_resultados(evento_id: int, evento_nome: str) -> sg.Window:
    """
    Cria a janela para importação de resultados de um evento.
    
    Args:
        evento_id: ID do evento para importação (obrigatório)
        evento_nome: Nome do evento (obrigatório)
        
    Returns:
        Janela PySimpleGUI configurada
    """
    sg.theme('DarkBlue14')
    
    layout = [
        [sg.Text('Importar Resultados', font=('Helvetica', 20))],
        [sg.HorizontalSeparator()],
        [sg.Text('Evento selecionado:', font=('Helvetica', 11, 'bold'))],
        [sg.Text(evento_nome, font=('Helvetica', 12), text_color='yellow')],
        [sg.Text('')],
        [sg.Text('Selecione o arquivo de resultados (.csv):')],
        [sg.Input(key='-ARQUIVO-', readonly=True, size=(40, 1)), 
         sg.FileBrowse('Selecionar Arquivo', file_types=(('CSV Files', '*.csv'),))],
        [sg.Text('')],
        [sg.Text('Formato esperado do CSV:', font=('Helvetica', 10, 'italic'))],
        [sg.Text('CPF,Tempo', font=('Courier', 9))],
        [sg.Text('Exemplo: 12345678901,01:30:45', font=('Courier', 9))],
        [sg.Text('')],
        [sg.Button('Importar', key='-IMPORTAR-', size=(12, 1)), 
         sg.Button('Cancelar', key='-CANCELAR-', size=(12, 1))],
        [sg.Text('', key='-STATUS-', size=(50, 2))]
    ]
    
    return sg.Window(
        f'PaceHub - Importar Resultados - {evento_nome}', 
        layout, 
        size=(600, 400), 
        finalize=True, 
        resizable=True
    )


def processar_importacao(janela: sg.Window, controlador: ControladorImportacao, 
                        evento_id: int, arquivo_csv: str) -> Tuple[bool, str]:
    """
    Processa a importação de resultados.
    
    Args:
        janela: Janela PySimpleGUI
        controlador: Instância do ControladorImportacao
        evento_id: ID do evento
        arquivo_csv: Caminho do arquivo CSV
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        print(f"\n[IMPORTACAO] Iniciando importação para evento ID: {evento_id}")
        print(f"[IMPORTACAO] Arquivo: {arquivo_csv}")
        
        # Atualizar status na janela
        janela['-STATUS-'].update("Processando arquivo...")
        janela.refresh()
        
        # Processar CSV
        total_importados, erros = controlador.processar_csv(arquivo_csv, evento_id)
        
        print(f"[IMPORTACAO] Processamento concluído: {total_importados} importados, {len(erros)} erros")
        
        # Criar mensagem de resultado
        if erros:
            mensagem = f"Importação concluída com avisos:\n"
            mensagem += f"✓ {total_importados} resultados importados\n"
            mensagem += f"⚠ {len(erros)} linhas com problemas"
            
            # Mostrar detalhes dos erros em popup scrollable
            detalhes_erros = _formatar_erros_detalhados(erros)
            sg.popup_scrolled(
                detalhes_erros,
                title="Detalhes da Importação",
                size=(1280, 720)
            )
        else:
            mensagem = f"Importação concluída com sucesso!\n✓ {total_importados} resultados importados"
            sg.popup(mensagem, title="Importação Bem-sucedida")
        
        return True, mensagem
        
    except FileNotFoundError:
        erro_msg = "Arquivo não encontrado!"
        print(f"[IMPORTACAO] ERRO: {erro_msg}")
        return False, erro_msg
    except ValueError as e:
        erro_msg = f"Erro de validação: {e}"
        print(f"[IMPORTACAO] ERRO: {erro_msg}")
        return False, erro_msg
    except Exception as e:
        erro_msg = f"Erro inesperado: {e}"
        print(f"[IMPORTACAO] ERRO: {erro_msg}")
        import traceback
        traceback.print_exc()
        return False, erro_msg


def _formatar_erros_detalhados(erros: list) -> str:
    """
    Formata lista de erros para exibição detalhada.
    
    Args:
        erros: Lista de dicionários de erro
        
    Returns:
        String formatada com detalhes dos erros
    """
    if not erros:
        return "Nenhum erro encontrado."
    
    detalhes = []
    
    # Agrupar erros por tipo
    erros_por_tipo = {}
    for erro in erros:
        tipo = erro['tipo']
        if tipo not in erros_por_tipo:
            erros_por_tipo[tipo] = []
        erros_por_tipo[tipo].append(erro)
    
    # Formatar cada tipo de erro
    for tipo, lista_erros in erros_por_tipo.items():
        detalhes.append(f"\n=== {_traduzir_tipo_erro(tipo)} ({len(lista_erros)} ocorrências) ===")
        
        for erro in lista_erros[:10]:  # Limitar a 10 por tipo
            linha = erro.get('linha', 'N/A')
            mensagem = erro['mensagem']
            dados = erro.get('dados', {})
            
            detalhes.append(f"Linha {linha}: {mensagem}")
            if dados:
                detalhes.append(f"  Dados: {dados}")
        
        if len(lista_erros) > 10:
            detalhes.append(f"  ... e mais {len(lista_erros) - 10} erros similares")
    
    return "\n".join(detalhes)


def _traduzir_tipo_erro(tipo: str) -> str:
    """
    Traduz tipo de erro para português.
    
    Args:
        tipo: Tipo do erro
        
    Returns:
        Descrição em português
    """
    traducoes = {
        'formato_invalido': 'Formato Inválido',
        'cpf_invalido': 'CPF Inválido',
        'tempo_invalido': 'Tempo Inválido',
        'atleta_nao_encontrado': 'Atleta Não Encontrado',
        'atleta_nao_inscrito': 'Atleta Não Inscrito',
        'nao_e_atleta': 'Não é Atleta',
        'erro_criacao': 'Erro na Criação'
    }
    
    return traducoes.get(tipo, tipo)


def executar_janela_importacao(controlador: ControladorImportacao, 
                               evento_id: int, evento_nome: str) -> bool:
    """
    Executa a janela de importação e retorna se foi bem-sucedida.
    
    Args:
        controlador: Instância do ControladorImportacao
        evento_id: ID do evento para importação
        evento_nome: Nome do evento
        
    Returns:
        True se importação foi bem-sucedida, False caso contrário
    """
    janela = criar_janela_importar_resultados(evento_id, evento_nome)
    
    if not janela:
        return False
    
    sucesso = False
    
    while True:
        event, values = janela.read()
        
        if event in (sg.WIN_CLOSED, '-CANCELAR-'):
            break
        
        if event == '-IMPORTAR-':
            arquivo = values['-ARQUIVO-']
            
            if not arquivo:
                sg.popup_error('Por favor, selecione um arquivo CSV.')
                continue
            
            # Validar arquivo antes de processar
            arquivo_valido, mensagem_validacao = controlador.validar_arquivo_csv(arquivo)
            
            if not arquivo_valido:
                sg.popup_error(f'Arquivo inválido: {mensagem_validacao}')
                continue
            
            # Processar importação
            sucesso_importacao, mensagem = processar_importacao(janela, controlador, evento_id, arquivo)
            
            if sucesso_importacao:
                janela['-STATUS-'].update("Importação concluída com sucesso!")
                sucesso = True
                # Aguardar um pouco antes de fechar
                import time
                time.sleep(1)
                break
            else:
                janela['-STATUS-'].update(f"Erro: {mensagem}")
                sg.popup_error(mensagem)
    
    janela.close()
    return sucesso

