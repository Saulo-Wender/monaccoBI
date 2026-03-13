import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.formatters import formatar_moeda

def render(df, metricas):
    # Layout otimizado para não ofuscar o texto do Dark Mode
    layout_padrao = dict(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(family="Helvetica Neue"), 
        title_font=dict(size=18, color="#C5A059", family="Helvetica Neue"), 
        hoverlabel=dict(font_size=14, font_family="Helvetica Neue")
    )
    plotly_colors = ['#C5A059', '#34D399', '#F87171', '#60A5FA', '#A78BFA', '#38BDF8']

    # 1. CORREÇÃO DE DATAS
    dt_ini = metricas.get('data_inicio')
    dt_fim = metricas.get('data_fim')
    periodo_str = "Período Consolidado" 
    
    if dt_ini and dt_fim:
        try:
            str_ini = dt_ini.strftime('%d/%m/%Y') if hasattr(dt_ini, 'strftime') else str(dt_ini)
            str_fim = dt_fim.strftime('%d/%m/%Y') if hasattr(dt_fim, 'strftime') else str(dt_fim)
            if "undefined" not in str_ini.lower() and "undefined" not in str_fim.lower():
                periodo_str = f"{str_ini} a {str_fim}"
        except Exception:
            pass 

    st.markdown(f"### Visão Geral da Operação | <span style='opacity: 0.6; font-weight: 400; font-size: 0.8em;'>{periodo_str}</span>", unsafe_allow_html=True)
    
    # 2. CARDS SUPERIORES DE INDICADORES (CORREÇÃO DE DESIGN)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento Bruto", formatar_moeda(metricas.get('receitas', 0)), delta="Entradas")
    
    # CORREÇÃO AQUI: Mudámos para delta_color="normal" para que o sinal "-" force a cor Vermelha.
    col2.metric("Custos e Despesas", formatar_moeda(metricas.get('despesas', 0)), delta="-Saídas", delta_color="normal")
    
    if metricas.get('receitas', 0) == 0:
        col3.metric("Consumo de Caixa (Burn)", formatar_moeda(metricas.get('despesas', 0)), delta="-Sem Receitas", delta_color="normal")
        col4.metric("Margem EBITDA", "N/A", delta="Requer receita", delta_color="off")
    else:
        saldo = metricas.get('saldo', 0)
        # Ajuste inteligente: Verde se superávite, Vermelho se défice
        col3.metric("Fluxo de Caixa Livre", formatar_moeda(saldo), delta=f"{'Superávite' if saldo >= 0 else '-Défice'}", delta_color="normal")
        
        margem_ebitda = (metricas.get('dre_resultado', 0) / metricas.get('receitas', 1)) * 100
        # Ajuste inteligente: Verde se saudável, Vermelho se estiver em risco
        col4.metric("Margem EBITDA", f"{margem_ebitda:.1f}%", delta="Saudável" if margem_ebitda > 15 else "-Atenção", delta_color="normal")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. GRÁFICOS DIÁRIOS E COMPOSIÇÃO
    col_graf1, col_graf2 = st.columns([6, 4])
    
    with col_graf1:
        if not df.empty:
            df_diario = df.groupby(['Data', 'Tipo'])['Valor'].sum().reset_index()
            fig_area = px.area(
                df_diario, x='Data', y='Valor', color='Tipo', 
                color_discrete_map={'Receita': 'rgba(52, 211, 153, 0.7)', 'Despesa': 'rgba(248, 113, 113, 0.7)'},
                title="Evolução Diária do Fluxo Financeiro"
            )
            fig_area.update_layout(**layout_padrao, yaxis_title="Reais (R$)", xaxis_title="", legend_title="")
            fig_area.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.2)')
            fig_area.update_layout(margin=dict(t=50, b=10, l=10, r=10))
            st.plotly_chart(fig_area, use_container_width=True, theme="streamlit")

    with col_graf2:
        df_despesas = df[df['Tipo'] == 'Despesa']
        if not df_despesas.empty:
            df_cat_despesas = df_despesas.groupby('Categoria')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
            
            if len(df_cat_despesas) > 5:
                top5 = df_cat_despesas.head(5)
                valor_outras = df_cat_despesas.iloc[5:]['Valor'].sum()
                outros = pd.DataFrame([{'Categoria': 'Outras', 'Valor': valor_outras}])
                df_cat_despesas = pd.concat([top5, outros], ignore_index=True)
                
            fig_rosca = px.pie(
                df_cat_despesas, values='Valor', names='Categoria', hole=0.6,
                color_discrete_sequence=plotly_colors, title="Composição de Saídas"
            )
            fig_rosca.update_traces(textposition='inside', textinfo='percent')
            fig_rosca.update_layout(
                **layout_padrao, 
                showlegend=True, 
                legend=dict(orientation="h", y=-0.2),
                margin=dict(t=50, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_rosca, use_container_width=True, theme="streamlit")

    # 4. GRÁFICO DE TENDÊNCIA MENSAL
    df_tendencia = metricas.get('df_tendencia')
    if df_tendencia is not None and not df_tendencia.empty:
        st.markdown("<br>### Evolução Mensal Consolidada", unsafe_allow_html=True)
        
        fig_mensal = go.Figure()

        if 'Receita' in df_tendencia.columns:
            fig_mensal.add_trace(go.Bar(
                x=df_tendencia['Mes_Ano'], y=df_tendencia['Receita'],
                name='Receitas', marker_color='#34D399' # Verde
            ))
            
        if 'Despesa' in df_tendencia.columns:
            fig_mensal.add_trace(go.Bar(
                x=df_tendencia['Mes_Ano'], y=df_tendencia['Despesa'],
                name='Despesas', marker_color='#F87171' # Vermelho
            ))

        if 'Saldo' in df_tendencia.columns:
            fig_mensal.add_trace(go.Scatter(
                x=df_tendencia['Mes_Ano'], y=df_tendencia['Saldo'],
                name='Saldo Líquido', mode='lines+markers',
                line=dict(color='#C5A059', width=3), marker=dict(size=8, color='#C5A059') # Dourado
            ))

        fig_mensal.update_layout(
            **layout_padrao, 
            barmode='group', 
            yaxis_title="Reais (R$)", 
            xaxis_title="Período",
            legend_title="Indicadores", 
            hovermode="x unified", 
            margin=dict(t=30, b=10, l=10, r=10)
        )
        fig_mensal.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.2)')
        
        st.plotly_chart(fig_mensal, use_container_width=True, theme="streamlit")