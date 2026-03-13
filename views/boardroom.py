import streamlit as st
import plotly.graph_objects as go
from utils.formatters import formatar_moeda

def render(metricas):
    layout_padrao = dict(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(family="Helvetica Neue", color="#334155")
    )

    st.markdown("""
    <div class="board-container">
        <div class="board-title">Comitê Executivo de Resultados</div>
        <div class="board-subtitle">Síntese de Performance Operacional e Financeira</div>
    """, unsafe_allow_html=True)
    
    b_col1, b_col2, b_col3 = st.columns(3)
    
    with b_col1:
        st.markdown(f"""
        <div class="board-metric-box">
            <div class="board-label">Faturamento</div>
            <div class="board-value board-value-fat">{formatar_moeda(metricas.get('receitas', 0))}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with b_col2:
        st.markdown(f"""
        <div class="board-metric-box">
            <div class="board-label">Gastos Globais</div>
            <div class="board-value board-value-neg">-{formatar_moeda(metricas.get('despesas', 0))}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with b_col3:
        saldo = metricas.get('saldo', 0)
        cor_classe = "board-value-pos" if saldo >= 0 else "board-value-neg"
        sinal = "+" if saldo >= 0 else ""
        st.markdown(f"""
        <div class="board-metric-box">
            <div class="board-label">Caixa Gerado</div>
            <div class="board-value {cor_classe}">{sinal}{formatar_moeda(saldo)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

    col_gauge, col_water = st.columns([3, 7])
    
    with col_gauge:
        st.markdown("<h4 style='text-align: center; color: #0F172A;'>Saúde Financeira</h4>", unsafe_allow_html=True)
        receitas_totais = metricas.get('receitas', 0)
        
        if receitas_totais > 0:
            marg_ebitda = (metricas.get('dre_resultado', 0) / receitas_totais) * 100
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = marg_ebitda,
                number = {'suffix': "%", 'font': {'color': '#1E293B'}},
                title = {'text': "Margem EBITDA", 'font': {'size': 16, 'color': '#64748B'}},
                gauge = {
                    'axis': {'range': [-20, 50], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#C5A059"}, 
                    'bgcolor': "white", 'borderwidth': 2, 'bordercolor': "gray",
                    'steps': [
                        {'range': [-20, 0], 'color': "#FEE2E2"},   
                        {'range': [0, 15], 'color': "#FEF3C7"},    
                        {'range': [15, 50], 'color': "#D1FAE5"}],  
                    'threshold': {'line': {'color': "#059669", 'width': 4}, 'thickness': 0.75, 'value': 15}
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(t=40, b=0, l=10, r=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.info("💡 A zona verde indica margens acima de 15% (Alvo).")
        else:
            st.warning("Sem faturamento para calcular margens de rentabilidade.")

    with col_water:
        receitas = metricas.get('receitas', 0)
        impostos_custos = metricas.get('dre_impostos', 0) + metricas.get('dre_custos', 0)
        fixas = metricas.get('dre_despesas_fixas', 0)
        resultado = metricas.get('dre_resultado', 0)

        fig_waterfall = go.Figure(go.Waterfall(
            name="Resultado", orientation="v",
            measure=["relative", "relative", "relative", "total"],
            x=["Faturamento Bruto", "Impostos/Custos Var.", "Despesas Fixas", "Resultado (EBITDA)"],
            textposition="outside",
            text=[formatar_moeda(receitas), f"-{formatar_moeda(impostos_custos)}", f"-{formatar_moeda(fixas)}", formatar_moeda(resultado)],
            y=[receitas, -impostos_custos, -fixas, resultado],
            connector={"line":{"color":"#94A3B8", "width": 2, "dash": "dot"}},
            decreasing={"marker":{"color":"#E11D48"}}, 
            increasing={"marker":{"color":"#059669"}}, 
            totals={"marker":{"color":"#C5A059"}}      
        ))
        
        fig_waterfall.update_layout(
            **layout_padrao, 
            title=dict(text="Formação de Resultado Monetário", font=dict(color="#1E293B", size=18)), 
            title_x=0.5, margin=dict(t=50, b=30),
            yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.2)', title="Valor (R$)")
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

    # =========================================================
    # NOVO: TERMÔMETRO DE DESCAPITALIZAÇÃO (PF VS PJ)
    # =========================================================
    st.markdown("---")
    st.markdown("### 🌡️ Termômetro de Descapitalização (Sócio vs Empresa)", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Monitorização da saúde do caixa face às retiradas pessoais dos sócios (Pró-Labore, Lucros, Gastos PF).</p>", unsafe_allow_html=True)

    retiradas = metricas.get('retiradas_socios', 0)
    saldo_final = metricas.get('saldo', 0)
    
    # O Caixa Operacional é quanto a empresa gerou ANTES do sócio meter a mão no dinheiro
    caixa_operacional = saldo_final + retiradas

    col_t1, col_t2 = st.columns([4, 6])
    
    with col_t1:
        st.markdown("#### Indicadores de Retirada")
        st.metric("Caixa Gerado pela Operação", formatar_moeda(caixa_operacional))
        st.metric("Retiradas Totais do Sócio", formatar_moeda(retiradas), delta="-Saídas PF", delta_color="inverse")
        
        if caixa_operacional <= 0 and retiradas > 0:
            st.error("🚨 **ALERTA CRÍTICO:** A empresa não gerou caixa positivo, mas houve retiradas do sócio. O negócio está a ser financiado por capital de terceiros ou reservas, gerando descapitalização imediata.")
        elif retiradas > caixa_operacional:
            st.error(f"🚨 **DESCAPITALIZAÇÃO:** As retiradas do sócio superaram o caixa gerado pela operação em **{formatar_moeda(retiradas - caixa_operacional)}**. A empresa está a perder fôlego financeiro.")
        elif retiradas > (caixa_operacional * 0.7):
            st.warning("⚠️ **RISCO MODERADO:** As retiradas do sócio estão a consumir mais de 70% do caixa gerado. Sobra pouco capital para reinvestimento e segurança do negócio.")
        elif retiradas == 0:
            st.info("💡 Não foram mapeadas retiradas de sócios neste período.")
        else:
            st.success("✅ **SUSTENTÁVEL:** As retiradas do sócio estão controladas e alinhadas com a geração de caixa da empresa.")

    with col_t2:
        if retiradas > 0 or caixa_operacional > 0:
            # Gráfico de Bullet (Termômetro)
            fig_bullet = go.Figure(go.Indicator(
                mode = "number+gauge",
                value = retiradas,
                number = {'prefix': "R$ ", 'font': {'size': 20, 'color': '#1E293B'}},
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Retiradas<br><span style='font-size:0.8em;color:gray'>vs Caixa Operacional</span>", 'font': {"size": 14}},
                gauge = {
                    'shape': "bullet",
                    'axis': {'range': [None, max(caixa_operacional * 1.5, retiradas * 1.2)]},
                    'threshold': {
                        'line': {'color': "red", 'width': 3},
                        'thickness': 0.75,
                        'value': caixa_operacional # A linha de limite é o Caixa Operacional
                    },
                    'bar': {'color': "#F59E0B" if retiradas <= caixa_operacional else "#EF4444"},
                    'steps': [
                        {'range': [0, max(0, caixa_operacional)], 'color': "#D1FAE5"}, # Zona Verde Segura
                        {'range': [max(0, caixa_operacional), max(caixa_operacional * 1.5, retiradas * 1.2)], 'color': "#FEE2E2"} # Zona Vermelha de Risco
                    ]
                }
            ))
            fig_bullet.update_layout(height=200, margin=dict(t=30, b=20, l=150, r=30), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bullet, use_container_width=True)
            st.markdown("<small style='color: #64748B;'>* A linha vermelha vertical (Threshold) representa o limite máximo seguro (o Total de Caixa Gerado). A barra ultrapassar esta linha indica sangria do negócio.</small>", unsafe_allow_html=True)