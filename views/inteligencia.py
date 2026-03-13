import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.formatters import formatar_moeda
from utils.relatorio_abc import criar_download_relatorio_abc

def calcular_curva_abc(df_filtro):
    if df_filtro.empty: return pd.DataFrame()
    df_abc = df_filtro.groupby('Pessoa')['Valor'].sum().reset_index()
    df_abc = df_abc[df_abc['Valor'] > 0]
    if df_abc.empty: return pd.DataFrame()

    df_abc = df_abc.sort_values('Valor', ascending=False).reset_index(drop=True)
    total = df_abc['Valor'].sum()
    df_abc['% Participação'] = (df_abc['Valor'] / total) * 100
    df_abc['% Acumulada'] = df_abc['% Participação'].cumsum()
    
    def classificar(acumulado):
        if acumulado <= 80.01: return 'Classe A (Crítico)'
        elif acumulado <= 95.01: return 'Classe B (Moderado)'
        else: return 'Classe C (Baixo Impacto)'
        
    df_abc['Classificação'] = df_abc['% Acumulada'].apply(classificar)
    return df_abc

def render_grafico_pareto(df_abc, titulo, cor_barra):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df_abc['Pessoa'], y=df_abc['Valor'], name="Valor (R$)", marker_color=cor_barra), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_abc['Pessoa'], y=df_abc['% Acumulada'], name="% Acumulada", mode='lines+markers', line=dict(color='#C5A059', width=3), marker=dict(size=8)), secondary_y=True)

    fig.update_layout(
        title=dict(text=titulo, font=dict(color="#E2E8F0", size=16)),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Helvetica Neue", color="#E2E8F0"),
        hovermode="x unified", margin=dict(t=50, b=30, l=10, r=10), showlegend=False
    )
    fig.update_yaxes(title_text="Valor em Reais (R$)", showgrid=True, gridcolor='rgba(148, 163, 184, 0.2)', secondary_y=False)
    fig.update_yaxes(title_text="Percentual Acumulado (%)", range=[0, 105], showgrid=False, secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

def formatar_tabela_exibicao(df, col_nome_pessoa):
    df_exibicao = df[['Pessoa', 'Valor', '% Participação', '% Acumulada']].copy()
    df_exibicao.rename(columns={'Pessoa': col_nome_pessoa}, inplace=True)
    df_exibicao['Valor'] = df_exibicao['Valor'].apply(formatar_moeda)
    df_exibicao['% Participação'] = df_exibicao['% Participação'].apply(lambda x: f"{x:.2f}%")
    df_exibicao['% Acumulada'] = df_exibicao['% Acumulada'].apply(lambda x: f"{x:.2f}%")
    return df_exibicao

def render(df):
    st.markdown("### 🔍 Inteligência ABC (Princípio de Pareto)", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-bottom: 1rem;'>Análise de concentração e risco: descubra quais clientes e fornecedores dominam 80% do seu caixa.</p>", unsafe_allow_html=True)

    if df.empty or 'Pessoa' not in df.columns:
        st.info("⚠️ Dados insuficientes. Certifique-se de que os seus ficheiros possuem a coluna 'Nome' ou 'Pessoa' preenchida.")
        return

    # Processamento Global para Relatório e Tela
    df_limpo = df[~df['Pessoa'].isin(['Não informado', '-', 'Sem Categoria'])]
    df_receitas = df_limpo[df_limpo['Tipo'] == 'Receita']
    df_despesas = df_limpo[df_limpo['Tipo'] == 'Despesa']

    df_abc_rec = calcular_curva_abc(df_receitas)
    df_abc_desp = calcular_curva_abc(df_despesas)

    # Métricas Comerciais (Clientes)
    qtd_a, qtd_total, perc_concentracao = 0, 0, 0
    df_exibicao_rec = pd.DataFrame()
    if not df_abc_rec.empty:
        clientes_a = df_abc_rec[df_abc_rec['Classificação'] == 'Classe A (Crítico)']
        qtd_a = len(clientes_a)
        qtd_total = len(df_abc_rec)
        perc_concentracao = (qtd_a / qtd_total * 100) if qtd_total > 0 else 0
        df_exibicao_rec = formatar_tabela_exibicao(clientes_a, 'Cliente')

    # Métricas Operacionais (Fornecedores)
    qtd_forn_a, qtd_forn_total, perc_forn_a = 0, 0, 0
    df_exibicao_desp = pd.DataFrame()
    if not df_abc_desp.empty:
        forn_a = df_abc_desp[df_abc_desp['Classificação'] == 'Classe A (Crítico)']
        qtd_forn_a = len(forn_a)
        qtd_forn_total = len(df_abc_desp)
        perc_forn_a = (qtd_forn_a / qtd_forn_total * 100) if qtd_forn_total > 0 else 0
        df_exibicao_desp = formatar_tabela_exibicao(forn_a, 'Fornecedor / Beneficiário')

    # --- BOTÃO DE EXPORTAÇÃO (RELATÓRIO EXECUTIVO ABC) ---
    empresa_nome = df['Empresa'].iloc[0] if 'Empresa' in df.columns else "Cliente Monacco"
    link_download = criar_download_relatorio_abc(
        empresa_nome, qtd_a, qtd_total, perc_concentracao, df_exibicao_rec,
        qtd_forn_a, qtd_forn_total, perc_forn_a, df_exibicao_desp
    )
    st.markdown(link_download, unsafe_allow_html=True)
    # ---------------------------------------------------

    # Interface Gráfica
    tab_clientes, tab_fornecedores = st.tabs(["🟢 Concentração de Clientes (Receitas)", "🔴 Dependência de Fornecedores (Saídas)"])

    with tab_clientes:
        if df_receitas.empty or df_abc_rec.empty:
            st.warning("Não há dados de receita suficientes para esta análise.")
        else:
            st.markdown("#### Diagnóstico de Risco Comercial")
            col1, col2 = st.columns([7, 3])
            
            with col1:
                if perc_concentracao <= 20:
                    st.error(f"🚨 **Alto Risco de Concentração!** Apenas **{qtd_a} cliente(s)** (que representam {perc_concentracao:.1f}% da sua carteira) são responsáveis por cerca de 80% do seu faturamento. A perda de um destes clientes pode ser fatal.")
                elif perc_concentracao <= 40:
                    st.warning(f"⚠️ **Risco Moderado.** **{qtd_a} clientes** ({perc_concentracao:.1f}% da base) compõem 80% do faturamento. Recomendável diversificar.")
                else:
                    st.success(f"✅ **Carteira Saudável.** O faturamento está bem distribuído. O núcleo de 80% depende de **{qtd_a} clientes** ({perc_concentracao:.1f}% da base).")
            
            with col2:
                st.metric("Total de Clientes Ativos", f"{qtd_total} clientes", delta=f"{qtd_a} na Classe A", delta_color="off")

            st.markdown("<br>", unsafe_allow_html=True)
            render_grafico_pareto(df_abc_rec.head(15), "Top 15 Clientes vs Participação Acumulada", "#34D399")
            
            st.markdown("**Detalhamento - Clientes Classe A (80% do Faturamento)**")
            st.dataframe(df_exibicao_rec, hide_index=True, use_container_width=True)

    with tab_fornecedores:
        if df_despesas.empty or df_abc_desp.empty:
            st.warning("Não há dados de saídas suficientes para esta análise.")
        else:
            st.markdown("#### Onde o seu dinheiro se concentra?")
            st.info(f"💡 Apenas **{qtd_forn_a} fornecedor(es)** ({perc_forn_a:.1f}% do total) estão a consumir aproximadamente 80% de todo o caixa. Foque as suas renegociações de preços com estes parceiros.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            render_grafico_pareto(df_abc_desp.head(15), "Top 15 Maiores Saídas vs Participação Acumulada", "#F87171")
            
            st.markdown("**Detalhamento - Maiores Escoamentos de Caixa (Classe A)**")
            st.dataframe(df_exibicao_desp, hide_index=True, use_container_width=True)