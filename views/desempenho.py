import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.formatters import formatar_moeda
from utils.relatorio_desempenho import criar_download_relatorio_desempenho

def render(df_full, metricas):
    st.markdown("### 🚀 Indicadores de Desempenho e Sobrevivência", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-bottom: 1rem;'>Análise de eficiência operacional, risco de quebra e conversão de resultados em caixa real.</p>", unsafe_allow_html=True)

    if metricas is None or df_full.empty:
        st.warning("Dados insuficientes para calcular os indicadores de desempenho.")
        return

    # Entrada do Saldo Atual para o cálculo de Sobrevivência (Runway)
    st.markdown("<div style='background-color: #0F172A; padding: 15px; border-radius: 8px; border-left: 4px solid #10B981; margin-bottom: 20px;'>", unsafe_allow_html=True)
    saldo_banco = st.number_input("💰 Calibragem de Liquidez: Qual é o Saldo Atual Real na conta bancária da empresa? (R$)", value=0.0, step=100.0, key="saldo_desempenho")
    st.markdown("</div>", unsafe_allow_html=True)

    # CÁLCULO DOS INDICADORES
    receitas = metricas.get('receitas', 0)
    despesas_fixas = abs(metricas.get('dre_despesas_fixas', 0))
    margem_contrib_valor = metricas.get('dre_margem_contribuicao', 0)
    ebitda = metricas.get('dre_resultado', 0)
    caixa_gerado = metricas.get('saldo', 0)

    margem_contrib_perc = (margem_contrib_valor / receitas) if receitas > 0 else 0
    pe = (despesas_fixas / margem_contrib_perc) if margem_contrib_perc > 0 else 0
    margem_seguranca = ((receitas - pe) / receitas * 100) if receitas > 0 and receitas > pe else 0

    recebiveis = 0
    if 'Status' in df_full.columns:
        df_pendente_rec = df_full[(df_full['Status'] == 'Pendente') & (df_full['Tipo'] == 'Receita')]
        recebiveis = df_pendente_rec['Valor'].sum() if not df_pendente_rec.empty else 0
    
    runway_meses = (saldo_banco + recebiveis) / despesas_fixas if despesas_fixas > 0 else 0
    conversao = (caixa_gerado / ebitda * 100) if ebitda > 0 else 0

    # BOTÃO DE EXPORTAÇÃO
    empresa_nome = metricas.get('empresa', 'Cliente Monacco')
    link_download = criar_download_relatorio_desempenho(
        empresa_nome, pe, margem_seguranca, runway_meses, conversao, 
        receitas, despesas_fixas, saldo_banco, recebiveis, ebitda, caixa_gerado
    )
    st.markdown(link_download, unsafe_allow_html=True)
    st.markdown("---")

    # ==========================================
    # RENDERIZAÇÃO ALINHADA (2 LINHAS x 2 COLUNAS)
    # ==========================================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 Ponto de Equilíbrio (Break-Even)")
        st.markdown("<p style='font-size: 13px; color: #64748B; margin-bottom: 25px;'>Faturamento mínimo necessário para não ter prejuízo.</p>", unsafe_allow_html=True)
        st.metric("Meta Mínima de Faturamento", formatar_moeda(pe), delta=f"Faturado: {formatar_moeda(receitas)}", delta_color="normal" if receitas >= pe else "inverse")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if receitas >= pe:
            st.success("✅ **Operação no Azul:** O faturamento atual já cobriu todas as despesas fixas da empresa.")
        else:
            st.error(f"🚨 **Alerta Vermelho:** Faltam {formatar_moeda(pe - receitas)} em faturamento apenas para empatar as contas.")

    with col2:
        st.markdown("#### 🛡️ Margem de Segurança")
        st.markdown("<p style='font-size: 13px; color: #64748B;'>O quanto as vendas podem cair antes de gerar prejuízo.</p>", unsafe_allow_html=True)
        
        # Aumentada a altura (height) para evitar cortes em baixo
        fig_ms = go.Figure(go.Indicator(
            mode = "gauge+number", value = margem_seguranca,
            number = {'suffix': "%", 'font': {'color': '#E2E8F0', 'size': 36}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#38BDF8"},
                'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 2, 'bordercolor': "gray",
                'steps': [
                    {'range': [0, 10], 'color': "rgba(239, 68, 68, 0.3)"},
                    {'range': [10, 30], 'color': "rgba(245, 158, 11, 0.3)"},
                    {'range': [30, 100], 'color': "rgba(16, 185, 129, 0.3)"}
                ],
                'threshold': {'line': {'color': "#10B981", 'width': 4}, 'thickness': 0.75, 'value': 30}
            }
        ))
        fig_ms.update_layout(height=250, margin=dict(t=20, b=10, l=30, r=30), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ms, use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### ⏳ Índice de Sobrevivência (Runway)")
        st.markdown("<p style='font-size: 13px; color: #64748B;'>Meses de sobrevivência de portas abertas se a receita for a zero.</p>", unsafe_allow_html=True)
        
        cor_runway = "#10B981" if runway_meses >= 3 else ("#F59E0B" if runway_meses >= 1 else "#EF4444")
        max_runway = max(12, runway_meses * 1.2) # Escala dinâmica para o gráfico respirar

        # Otimização do Bullet Chart: Fonte menor e gráfico mais fino
        fig_runway = go.Figure(go.Indicator(
            mode = "number+gauge", value = runway_meses,
            number = {'suffix': " meses", 'font': {'size': 20, 'color': '#E2E8F0'}},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'shape': "bullet", 'axis': {'range': [0, max_runway]},
                'threshold': {'line': {'color': "white", 'width': 2}, 'thickness': 0.75, 'value': 3},
                'bar': {'color': cor_runway, 'thickness': 0.5}, # Barra mais fina para ser elegante
                'steps': [
                    {'range': [0, 1], 'color': "rgba(239, 68, 68, 0.2)"},
                    {'range': [1, 3], 'color': "rgba(245, 158, 11, 0.2)"},
                    {'range': [3, max_runway], 'color': "rgba(16, 185, 129, 0.2)"}
                ]
            }
        ))
        fig_runway.update_layout(height=160, margin=dict(t=40, b=20, l=10, r=60), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_runway, use_container_width=True)
        st.info("💡 Meta recomendada: Mínimo de 3 meses em liquidez imediata.")

    with col4:
        st.markdown("#### 🔄 Conversão de Lucro em Caixa")
        st.markdown("<p style='font-size: 13px; color: #64748B;'>Qual a % do EBITDA que virou dinheiro real na conta.</p>", unsafe_allow_html=True)
        
        if ebitda <= 0:
            st.error("A empresa operou com EBITDA negativo (prejuízo). Não há lucro para converter em caixa.")
        else:
            fig_conv = go.Figure(go.Indicator(
                mode = "gauge+number", value = conversao,
                number = {'suffix': "%", 'font': {'color': '#E2E8F0', 'size': 36}},
                gauge = {
                    'axis': {'range': [0, max(150, conversao * 1.2)], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#C5A059"},
                    'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 2, 'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.3)"},
                        {'range': [50, 80], 'color': "rgba(245, 158, 11, 0.3)"},
                        {'range': [80, max(150, conversao * 1.2)], 'color': "rgba(16, 185, 129, 0.3)"}
                    ],
                    'threshold': {'line': {'color': "#10B981", 'width': 4}, 'thickness': 0.75, 'value': 80}
                }
            ))
            fig_conv.update_layout(height=250, margin=dict(t=20, b=10, l=30, r=30), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_conv, use_container_width=True)