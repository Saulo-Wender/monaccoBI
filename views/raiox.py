import streamlit as st
import pandas as pd
import plotly.express as px
from utils.formatters import formatar_moeda
from utils.relatorio_raiox import criar_download_relatorio_raiox

def render(df):
    st.markdown("### 🔬 Raio-X de Margens e Unidades de Negócio", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Auditoria de rentabilidade isolada por Centro de Custo, Projeto ou Serviço.</p>", unsafe_allow_html=True)

    if df is None or df.empty:
        st.warning("Dados insuficientes para a análise.")
        return

    # Procura a coluna de Centro de Custo no Nibo (pode variar de nome)
    col_cc = next((col for col in df.columns if col.lower() in ['centro de custo', 'centro de custos', 'projeto', 'unidade']), None)

    # 1. ALERTA DE CONSULTORIA (Se o cliente não tiver a contabilidade bem feita)
    if not col_cc or df[col_cc].isna().all():
        st.markdown("""
        <div style='background-color: #451A03; padding: 20px; border-radius: 8px; border-left: 5px solid #F59E0B;'>
            <h4 style='color: #FBBF24; margin-top: 0;'>⚠️ Oportunidade de Consultoria Identificada</h4>
            <p style='color: #FEF3C7; font-size: 15px; line-height: 1.5;'><b>Analista Monacco:</b> O sistema não encontrou dados de "Centro de Custo" ou "Projeto" nas planilhas importadas deste cliente.</p>
            <p style='color: #FDE68A; font-size: 14px;'><b>Ação Recomendada:</b> Na próxima reunião, explique ao cliente a importância de categorizar as receitas e despesas por Unidade de Negócio ou Serviço no Nibo. Sem isso, não conseguimos dizer-lhe onde ele está a perder dinheiro.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 2. MOTOR DE CÁLCULO
    df_cc = df.dropna(subset=[col_cc]).copy()
    
    # Remove marcações inúteis comuns em ERPs
    df_cc = df_cc[~df_cc[col_cc].isin(['', '-', 'N/A', 'Não Informado'])]

    if df_cc.empty:
        st.info("Todos os lançamentos estão sem centro de custo atribuído.")
        return

    # Agrupamento de Receitas e Despesas por Centro de Custo
    df_resumo = df_cc.groupby([col_cc, 'Tipo'])['Valor'].sum().unstack(fill_value=0).reset_index()
    
    if 'Receita' not in df_resumo.columns: df_resumo['Receita'] = 0
    if 'Despesa' not in df_resumo.columns: df_resumo['Despesa'] = 0
        
    df_resumo['Resultado Líquido'] = df_resumo['Receita'] - df_resumo['Despesa']
    df_resumo['Margem (%)'] = df_resumo.apply(lambda row: (row['Resultado Líquido'] / row['Receita'] * 100) if row['Receita'] > 0 else 0, axis=1)
    
    df_resumo = df_resumo.sort_values(by='Resultado Líquido', ascending=False)

    # Identifica o Melhor e o Pior
    melhor = df_resumo.iloc[0]
    pior = df_resumo.iloc[-1]
    
    dict_melhor = {'Nome': melhor[col_cc], 'Margem': f"{melhor['Margem (%)']:.1f}%", 'Resultado': formatar_moeda(melhor['Resultado Líquido'])}
    dict_pior = {'Nome': pior[col_cc], 'Margem': f"{pior['Margem (%)']:.1f}%", 'Resultado': formatar_moeda(pior['Resultado Líquido'])}

    # Prepara a tabela para o PDF
    df_print = df_resumo.copy()
    df_print.rename(columns={col_cc: 'Centro de Custo', 'Receita': 'Faturamento', 'Despesa': 'Gastos'}, inplace=True)
    df_print['Faturamento'] = df_print['Faturamento'].apply(formatar_moeda)
    df_print['Gastos'] = df_print['Gastos'].apply(formatar_moeda)
    df_print['Resultado Líquido'] = df_print['Resultado Líquido'].apply(formatar_moeda)
    df_print['Margem (%)'] = df_print['Margem (%)'].apply(lambda x: f"{x:.1f}%")

    # Botão de Exportação
    empresa_nome = df['Empresa'].iloc[0] if 'Empresa' in df.columns else "Cliente Monacco"
    link_download = criar_download_relatorio_raiox(empresa_nome, df_print, dict_melhor, dict_pior)
    st.markdown(link_download, unsafe_allow_html=True)

    # 3. INTERFACE VISUAL
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌟 Motor de Lucro (Vaca Leiteira)")
        st.metric(dict_melhor['Nome'], dict_melhor['Resultado'], delta=f"Margem: {dict_melhor['Margem']}")
        
    with col2:
        st.markdown("#### ⚠️ Ralo de Capital (Ponto de Atenção)")
        st.metric(dict_pior['Nome'], dict_pior['Resultado'], delta=f"Margem: {dict_pior['Margem']}", delta_color="inverse")

    st.markdown("---")
    
    # 4. GRÁFICO DE RENTABILIDADE (TREEMAP)
    st.markdown("### Mapa de Rentabilidade e Tamanho")
    st.markdown("<p style='font-size: 13px; color: #64748B;'>O tamanho do bloco representa o volume de Faturamento. A cor representa a saúde da Margem (Verde = Lucro alto, Vermelho = Prejuízo).</p>", unsafe_allow_html=True)
    
    # Só desenha se houver receitas
    if df_resumo['Receita'].sum() > 0:
        fig_tree = px.treemap(
            df_resumo, 
            path=[col_cc], 
            values='Receita',
            color='Margem (%)',
            color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
            color_continuous_midpoint=0,
            hover_data=['Resultado Líquido']
        )
        fig_tree.update_layout(margin=dict(t=10, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Helvetica Neue"))
        # Formatação do hover text para exibir dinheiro corretamente
        fig_tree.update_traces(hovertemplate='<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<br>Margem: %{color:.1f}%')
        st.plotly_chart(fig_tree, use_container_width=True)
    else:
        st.info("Não há faturamento mapeado em centros de custo para desenhar o mapa.")

    st.markdown("### Detalhamento Analítico")
    st.dataframe(df_print, hide_index=True, use_container_width=True)