import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.formatters import formatar_moeda
from utils.relatorio_dre import criar_download_relatorio_dre

def render(df, metricas):
    st.subheader("Demonstração do Resultado do Exercício (Visão Monacco)")
    st.markdown("Acompanhamento contábil-gerencial estruturado. Configure os grupos de contas no painel lateral.")
    
    # 1. Montagem da estrutura sintética
    linhas_dre = [
        {"Estrutura": "1. RECEITA OPERACIONAL BRUTA", "Valor": metricas.get('receitas', 0), "Bg": "#F8FAFC", "Color": "#1E3A8A", "Bold": True},
        {"Estrutura": "(-) Deduções e Impostos", "Valor": -metricas.get('dre_impostos', 0), "Bg": "#FFFFFF", "Color": "#E11D48", "Bold": False},
        {"Estrutura": "2. RECEITA OPERACIONAL LÍQUIDA", "Valor": metricas.get('dre_receita_liquida', 0), "Bg": "#F1F5F9", "Color": "#059669", "Bold": True},
        {"Estrutura": "(-) Custos Variáveis / Insumos", "Valor": -metricas.get('dre_custos', 0), "Bg": "#FFFFFF", "Color": "#E11D48", "Bold": False},
        {"Estrutura": "3. MARGEM DE CONTRIBUIÇÃO", "Valor": metricas.get('dre_margem_contribuicao', 0), "Bg": "#EFF6FF", "Color": "#2563EB", "Bold": True},
        {"Estrutura": "(-) Despesas Fixas Operacionais", "Valor": -metricas.get('dre_despesas_fixas', 0), "Bg": "#FFFFFF", "Color": "#E11D48", "Bold": False},
        {"Estrutura": "4. RESULTADO OPERACIONAL (EBITDA)", "Valor": metricas.get('dre_resultado', 0), "Bg": "#0F172A" if metricas.get('dre_resultado', 0) >= 0 else "#9F1239", "Color": "white", "Bold": True}
    ]
    
    receitas_totais = metricas.get('receitas', 0)
    
    # Prepara os dados limpos para a exportação
    df_dre_export = pd.DataFrame(linhas_dre)[['Estrutura', 'Valor']]
    df_dre_export['Análise Vertical (%)'] = df_dre_export['Valor'].apply(lambda x: f"{((abs(x) / receitas_totais) * 100):.1f}%" if receitas_totais > 0 else "0.0%")
    st.session_state['dre_export'] = df_dre_export.copy()

    # --- BOTÃO DE EXPORTAÇÃO ---
    df_print = df_dre_export.copy()
    df_print['Valor'] = df_print['Valor'].apply(formatar_moeda) 
    
    empresa_nome = metricas.get('empresa', 'Cliente Monacco')
    resultado_ebitda = metricas.get('dre_resultado', 0)
    margem = (resultado_ebitda / receitas_totais * 100) if receitas_totais > 0 else 0
    
    link_download = criar_download_relatorio_dre(empresa_nome, df_print, receitas_totais, resultado_ebitda, margem)
    st.markdown(link_download, unsafe_allow_html=True)
    # ---------------------------
    
    # 2. Renderização da Tabela Plotly (Visão Executiva)
    col_estrutura, col_valor, col_av, cor_fundo, cor_texto = [], [], [], [], []
    for row in linhas_dre:
        av = ((abs(row['Valor']) / receitas_totais) * 100) if receitas_totais > 0 else 0
        texto_str = f"<b>{row['Estrutura']}</b>" if row['Bold'] else f"&nbsp;&nbsp;&nbsp;&nbsp;{row['Estrutura']}"
        val_str = f"<b>{formatar_moeda(row['Valor']).replace('R$ -', '- R$ ')}</b>" if row['Bold'] else formatar_moeda(row['Valor']).replace('R$ -', '- R$ ')
        av_str = f"<b>{av:.1f}%</b>" if row['Bold'] else f"{av:.1f}%"
        
        col_estrutura.append(texto_str)
        col_valor.append(val_str)
        col_av.append(av_str)
        cor_fundo.append(row['Bg'])
        cor_texto.append(row['Color'])
    
    # CORREÇÃO DE ALINHAMENTO APLICADA AQUI (`align=['left', 'center', 'right']`)
    fig_dre_table = go.Figure(data=[go.Table(
        columnwidth=[50, 25, 25],
        header=dict(
            values=['<b>Descrição da Rubrica</b>', '<b>Valor (R$)</b>', '<b>Análise Vertical (%)</b>'],
            fill_color='#1E3A8A', align=['left', 'center', 'right'], 
            font=dict(color='white', size=14), height=40
        ),
        cells=dict(
            values=[col_estrutura, col_valor, col_av],
            fill_color=[cor_fundo]*3, align=['left', 'center', 'right'],
            font=dict(color=[cor_texto]*3, size=14), height=35
        )
    )])
    fig_dre_table.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=300)
    st.plotly_chart(fig_dre_table, use_container_width=True)

    # =========================================================
    # 3. DRILL-DOWN E ANÁLISE HORIZONTAL
    # =========================================================
    st.markdown("---")
    st.markdown("### 🔬 Painel de Auditoria e Evolução (Drill-Down)")
    
    tab_detalhe, tab_horizontal = st.tabs(["📂 Abertura de Contas Nibo", "📅 DRE Horizontal (Mês a Mês)"])

    with tab_detalhe:
        st.markdown("<p style='color: #64748B;'>Detalhamento das saídas de caixa organizadas pela sua natureza no plano de contas.</p>", unsafe_allow_html=True)
        
        if not df.empty:
            cat_impostos = st.session_state.get('cat_impostos', [])
            cat_custos = st.session_state.get('cat_custos', [])
            
            df_desp = df[df['Tipo'] == 'Despesa'].copy()
            
            def classificar_macro(c):
                if c in cat_impostos: return "1. Impostos e Deduções"
                elif c in cat_custos: return "2. Custos Variáveis"
                else: return "3. Despesas Fixas"
                
            df_desp['Grupo Macro'] = df_desp['Categoria'].apply(classificar_macro)
            
            df_analitico = df_desp.groupby(['Grupo Macro', 'Categoria'])['Valor'].sum().reset_index()
            df_analitico = df_analitico.sort_values(by=['Grupo Macro', 'Valor'], ascending=[True, False])
            
            df_analitico['% do Faturamento'] = df_analitico['Valor'].apply(lambda x: f"{(x / receitas_totais * 100):.1f}%" if receitas_totais > 0 else "0.0%")
            df_analitico['Valor'] = df_analitico['Valor'].apply(formatar_moeda)
            
            st.dataframe(df_analitico, hide_index=True, use_container_width=True)
        else:
            st.info("Nenhum dado disponível para auditoria.")

    with tab_horizontal:
        st.markdown("<p style='color: #64748B;'>Análise de tendência do Resultado. Avalie se as margens estão a melhorar ou a piorar ao longo do tempo.</p>", unsafe_allow_html=True)
        
        if not df.empty and 'Data' in df.columns:
            df_temp = df.copy()
            df_temp['Mês'] = df_temp['Data'].dt.to_period('M').astype(str)
            meses_disponiveis = sorted(df_temp['Mês'].unique())
            
            if len(meses_disponiveis) > 1:
                dados_horizontais = []
                
                for mes in meses_disponiveis:
                    df_mes = df_temp[df_temp['Mês'] == mes]
                    
                    rec_mes = df_mes[df_mes['Tipo'] == 'Receita']['Valor'].sum()
                    desp_mes = df_mes[df_mes['Tipo'] == 'Despesa']['Valor'].sum()
                    imp_mes = df_mes[(df_mes['Categoria'].isin(st.session_state.get('cat_impostos', []))) & (df_mes['Tipo'] == 'Despesa')]['Valor'].sum()
                    cust_mes = df_mes[(df_mes['Categoria'].isin(st.session_state.get('cat_custos', []))) & (df_mes['Tipo'] == 'Despesa')]['Valor'].sum()
                    
                    rec_liq = rec_mes - imp_mes
                    margem_contrib = rec_liq - cust_mes
                    desp_fixas = desp_mes - imp_mes - cust_mes
                    resultado = margem_contrib - desp_fixas
                    margem_perc = f"{(resultado / rec_mes * 100):.1f}%" if rec_mes > 0 else "0.0%"
                    
                    dados_horizontais.append({
                        "Mês": mes,
                        "1. Receita Bruta": formatar_moeda(rec_mes),
                        "2. Deduções": formatar_moeda(-imp_mes),
                        "3. Margem Contribuição": formatar_moeda(margem_contrib),
                        "4. Despesas Fixas": formatar_moeda(-desp_fixas),
                        "5. EBITDA": formatar_moeda(resultado),
                        "Margem (%)": margem_perc
                    })
                
                df_horiz = pd.DataFrame(dados_horizontais).set_index("Mês").T
                st.dataframe(df_horiz, use_container_width=True)
                
            else:
                st.info("💡 A DRE Horizontal requer dados de mais de um mês. Amplie o período no filtro 'Horizonte de Análise' na barra lateral.")