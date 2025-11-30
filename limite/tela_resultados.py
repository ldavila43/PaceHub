import FreeSimpleGUI as sg
from entidade.resultado import Resultado, separar_resultados_por_categoria, separar_resultados_por_genero, ordenar_resultados_por_tempo


class TelaResultados:
    def __init__(self):
        pass

    def _criar_tabela_resultados(self, resultados, mostrar_classificacao=True):
        """
        Cria uma tabela com os resultados.
        
        Args:
            resultados: Lista de objetos Resultado
            mostrar_classificacao: Se deve mostrar coluna de classificação
            
        Returns:
            Lista de dados para a tabela
        """
        dados = []
        for resultado in resultados:
            classificacao = ""
            if mostrar_classificacao:
                if resultado.classificacao_geral:
                    classificacao = f"Geral: {resultado.classificacao_geral}º"
                elif resultado.classificacao_categoria:
                    classificacao = f"{resultado.classificacao_categoria}º"
            
            linha = [resultado.nome_atleta, resultado.tempo_final]
            if mostrar_classificacao:
                linha.append(classificacao)
            dados.append(linha)
        
        return dados

    def exibir_resultados_por_categoria(self, nome_evento: str, resultados: list):
        """
        Exibe uma janela com os resultados do evento separados por categoria em abas.
        Aba Geral mostra top 5 de cada gênero.
        Atletas no top 5 não aparecem nas categorias normais.
        Todas as abas são sempre exibidas, mesmo que vazias.
        Cada aba separa resultados por gênero.
        
        Args:
            nome_evento: Nome do evento
            resultados: Lista de objetos Resultado
        """
        sg.theme('DarkBlue14')
        
        # Separar por gênero primeiro
        masculino, feminino = separar_resultados_por_genero(resultados)
        
        # Ordenar por tempo
        masculino_ordenado = ordenar_resultados_por_tempo(masculino)
        feminino_ordenado = ordenar_resultados_por_tempo(feminino)
        
        # Top 5 de cada gênero para categoria Geral
        top5_masculino = masculino_ordenado[:5]
        top5_feminino = feminino_ordenado[:5]
        
        # Criar conjunto de CPFs dos top 5 para filtrar das categorias normais
        cpfs_top5 = set()
        for resultado in top5_masculino:
            cpfs_top5.add(resultado.cpf_atleta)
        for resultado in top5_feminino:
            cpfs_top5.add(resultado.cpf_atleta)
        
        # Filtrar resultados que não estão no top 5
        resultados_sem_top5 = [r for r in resultados if r.cpf_atleta not in cpfs_top5]
        
        # Separar resultados restantes por categoria
        resultados_por_categoria = separar_resultados_por_categoria(resultados_sem_top5)
        
        # Ordenar cada categoria por tempo
        for categoria in resultados_por_categoria:
            resultados_por_categoria[categoria] = ordenar_resultados_por_tempo(resultados_por_categoria[categoria])
        
        # Criar aba Geral com separação por gênero
        dados_masc_geral = []
        dados_fem_geral = []
        
        # Preparar dados top 5 masculino
        for i, resultado in enumerate(top5_masculino, 1):
            classificacao = f"Geral: {i}º"
            dados_masc_geral.append([
                resultado.nome_atleta,
                resultado.tempo_final,
                classificacao
            ])
        
        # Preparar dados top 5 feminino
        for i, resultado in enumerate(top5_feminino, 1):
            classificacao = f"Geral: {i}º"
            dados_fem_geral.append([
                resultado.nome_atleta,
                resultado.tempo_final,
                classificacao
            ])
        
        # Layout da aba Geral
        layout_geral = []
        cabecalhos_geral = ['Nome', 'Tempo', 'Classificação']
        
        if dados_masc_geral or dados_fem_geral:
            if dados_masc_geral:
                layout_geral.append([sg.Text('Masculino', font=('Helvetica', 14, 'bold'))])
                layout_geral.append([sg.Table(
                    values=dados_masc_geral,
                    headings=cabecalhos_geral,
                    auto_size_columns=False,
                    col_widths=[40, 15, 20],
                    justification='left',
                    num_rows=min(10, len(dados_masc_geral)),
                    display_row_numbers=False,
                    expand_x=True
                )])
            
            if dados_fem_geral:
                if dados_masc_geral:
                    layout_geral.append([sg.Text('')])  # Espaçamento
                layout_geral.append([sg.Text('Feminino', font=('Helvetica', 14, 'bold'))])
                layout_geral.append([sg.Table(
                    values=dados_fem_geral,
                    headings=cabecalhos_geral,
                    auto_size_columns=False,
                    col_widths=[40, 15, 20],
                    justification='left',
                    num_rows=min(10, len(dados_fem_geral)),
                    display_row_numbers=False,
                    expand_x=True
                )])
        else:
            layout_geral.append([sg.Text('Nenhum resultado encontrado.', font=('Helvetica', 12))])
        
        # Criar abas para todas as categorias
        tabs = [sg.Tab('Geral', layout_geral, key='-TAB_GERAL-')]
        
        # Ordem das categorias
        ordem_categorias = ['Júnior', 'Adulto', 'Master', 'PCD']
        
        for categoria in ordem_categorias:
            # Buscar resultados da categoria (pode estar vazio)
            resultados_categoria = resultados_por_categoria.get(categoria, [])
            
            # Separar por gênero dentro da categoria
            masc_cat, fem_cat = separar_resultados_por_genero(resultados_categoria)
            
            # Ordenar por tempo
            masc_cat = ordenar_resultados_por_tempo(masc_cat)
            fem_cat = ordenar_resultados_por_tempo(fem_cat)
            
            # Preparar dados
            dados_masc = []
            dados_fem = []
            
            # Adicionar resultados masculinos
            for resultado in masc_cat:
                classificacao = ""
                if resultado.classificacao_categoria:
                    classificacao = f"{resultado.classificacao_categoria}º"
                
                dados_masc.append([
                    resultado.nome_atleta,
                    resultado.tempo_final,
                    classificacao
                ])
            
            # Adicionar resultados femininos
            for resultado in fem_cat:
                classificacao = ""
                if resultado.classificacao_categoria:
                    classificacao = f"{resultado.classificacao_categoria}º"
                
                dados_fem.append([
                    resultado.nome_atleta,
                    resultado.tempo_final,
                    classificacao
                ])
            
            # Criar layout da categoria com separação por gênero
            layout_categoria = []
            cabecalhos = ['Nome', 'Tempo', 'Classificação']
            
            if dados_masc or dados_fem:
                if dados_masc:
                    layout_categoria.append([sg.Text('Masculino', font=('Helvetica', 14, 'bold'))])
                    layout_categoria.append([sg.Table(
                        values=dados_masc,
                        headings=cabecalhos,
                        auto_size_columns=False,
                        col_widths=[40, 15, 15],
                        justification='left',
                        num_rows=min(10, len(dados_masc)),
                        display_row_numbers=False,
                        expand_x=True
                    )])
                
                if dados_fem:
                    if dados_masc:
                        layout_categoria.append([sg.Text('')])  # Espaçamento
                    layout_categoria.append([sg.Text('Feminino', font=('Helvetica', 14, 'bold'))])
                    layout_categoria.append([sg.Table(
                        values=dados_fem,
                        headings=cabecalhos,
                        auto_size_columns=False,
                        col_widths=[40, 15, 15],
                        justification='left',
                        num_rows=min(10, len(dados_fem)),
                        display_row_numbers=False,
                        expand_x=True
                    )])
            else:
                layout_categoria.append([sg.Text('Nenhum resultado nesta categoria.', font=('Helvetica', 12))])
            
            tabs.append(sg.Tab(categoria, layout_categoria, key=f'-TAB_{categoria}-'))
        
        # Criar grupo de abas
        tab_group = sg.TabGroup([tabs], key='-TAB_GROUP-', expand_x=True, expand_y=True)
        
        layout = [
            [sg.Text(f'Resultados - {nome_evento}', font=('Helvetica', 20, 'bold'))],
            [sg.HSeparator()],
            [tab_group],
            [sg.Button('Fechar', key='-FECHAR-')]
        ]
        
        janela = sg.Window(
            f'PaceHub - Resultados - {nome_evento}',
            layout,
            finalize=True,
            size=(900, 700),
            resizable=True
        )
        
        while True:
            evento, valores = janela.read()
            if evento in (sg.WIN_CLOSED, '-FECHAR-'):
                break
        
        janela.close()

    def exibir_resultado_individual(self, nome_evento: str, resultado: dict):
        """
        Exibe uma janela com o resultado individual de um atleta.
        
        Args:
            nome_evento: Nome do evento
            resultado: Dicionário com dados do resultado
        """
        sg.theme('DarkBlue14')
        
        # Preparar informações para exibição
        classificacao_geral = resultado.get('classificacao_geral', '')
        classificacao_categoria = resultado.get('classificacao_categoria', '')
        
        classif_geral_str = f"{classificacao_geral}º lugar" if classificacao_geral else "Não classificado"
        classif_cat_str = f"{classificacao_categoria}º lugar na categoria {resultado.get('categoria', '')}" if classificacao_categoria else "Não classificado"
        
        layout = [
            [sg.Text(f'Resultado Individual - {nome_evento}', font=('Helvetica', 20, 'bold'))],
            [sg.HSeparator()],
            [sg.Text('Atleta:', font=('Helvetica', 12, 'bold')), 
             sg.Text(resultado.get('nome_atleta', ''), font=('Helvetica', 12))],
            [sg.Text('Tempo Final:', font=('Helvetica', 12, 'bold')), 
             sg.Text(resultado.get('tempo_final', ''), font=('Helvetica', 12))],
            [sg.Text('Categoria:', font=('Helvetica', 12, 'bold')), 
             sg.Text(resultado.get('categoria', ''), font=('Helvetica', 12))],
            [sg.Text('Classificação Geral:', font=('Helvetica', 12, 'bold')), 
             sg.Text(classif_geral_str, font=('Helvetica', 12))],
            [sg.Text('Classificação por Categoria:', font=('Helvetica', 12, 'bold')), 
             sg.Text(classif_cat_str, font=('Helvetica', 12))],
            [sg.HSeparator()],
            [sg.Button('Fechar', key='-FECHAR-')]
        ]
        
        janela = sg.Window(
            f'PaceHub - Resultado Individual - {nome_evento}',
            layout,
            finalize=True,
            size=(600, 300),
            resizable=False
        )
        
        while True:
            evento, valores = janela.read()
            if evento in (sg.WIN_CLOSED, '-FECHAR-'):
                break
        
        janela.close()
