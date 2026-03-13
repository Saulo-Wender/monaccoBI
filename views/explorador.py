import streamlit as st
import plotly.graph_objects as go
from utils.formatters import formatar_moeda

def render(df, metricas=None):
    st.markdown("### 🎛️ Laboratório de Cenários (Simulador What-If)", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Simule o impacto de mudanças nas vendas e cortes de gastos para prever a rentabilidade futura da operação.</p>", unsafe_allow_html=True)

    if metricas is None:
        st.error("Erro de contexto: As métricas financeiras não foram carregadas no simulador.")
        return

    receita_atual = metricas.get('receitas', 0)
    
    if receita_atual == 0:
        st.info("⚠️ É necessário ter faturamento registado no período base para poder realizar simulações de crescimento ou queda.")
        return

    # Captura da Base Atual
    impostos_atual = metricas.get('dre_impostos', 0)
    custos_atual = metricas.get('dre_custos', 0)
    fixas_atual = metricas.get('dre_despesas_fixas', 0)
    ebitda_atual = metricas.get('dre_resultado', 0)
    margem_atual = metricas.get('margem', 0)

    # ==========================================
    # 1. PAINEL DE ALAVANCAS (SLIDERS)
    # ==========================================
    st.markdown("""
    <div style='background-color: #0F172A; padding: 20px; border-radius: 8px; border-left: 5px solid #C5A059; margin-bottom: 25px;'>
        <h4 style='color: #C5A059; margin-top: 0;'>1. Ajuste as Alavancas da Operação</h4>
        <p style='color: #E2E8F0; font-size: 14px; margin-bottom: 0;'>Arraste os controlos abaixo para simular novos cenários. O cálculo dos impostos ajusta-se automaticamente com base na variação do faturamento.</p>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        var_receita = st.slider("📈 Variação no Faturamento (%)", min_value=-50, max_value=100, value=0, step=1)
    with col_s2:
        var_custos = st.slider("📦 Variação em Custos Variáveis (%)", min_value=-50, max_value=100, value=0, step=1, help="Simula renegociação com fornecedores ou aumento no preço de insumos.")
    with col_s3:
        var_fixas = st.slider("🏢 Variação em Despesas Fixas (%)", min_value=-50, max_value=100, value=0, step=1, help="Simula cortes em folha, aluguer, etc., ou novos investimentos estruturais.")

    # ==========================================
    # 2. MOTOR DE PROJEÇÃO MATEMÁTICA
    # ==========================================
    fator_rec = 1 + (var_receita / 100)
    fator_custos = 1 + (var_custos / 100)
    fator_fixas = 1 + (var_fixas / 100)

    proj_receita = receita_atual * fator_rec
    # Premissa: Se a receita sobe 10%, os impostos sobem 10% (são indexados)
    proj_impostos = impostos_atual * fator_rec 
    proj_custos = custos_atual * fator_custos
    proj_fixas = fixas_atual * fator_fixas

    proj_ebitda = proj_receita - proj_impostos - proj_custos - proj_fixas
    proj_margem = (proj_ebitda / proj_receita * 100) if proj_receita > 0 else 0

    # ==========================================
    # 3. PAINEL DE RESULTADOS (KPIs)
    # ==========================================
    st.markdown("#### 2. Comparativo: Cenário Atual vs Projetado")
    
    # Custom CSS para os Cards do Simulador
    st.markdown("""
    <style>
        .sim-card { background-color: #1E293B; padding: 15px; border-radius: 8px; border: 1px solid #334155; }
        .sim-title { font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
        .sim-value { font-size: 24px; font-weight: bold; color: #E2E8F0; }
        .sim-delta-pos { color: #10B981; font-size: 14px; font-weight: bold; }
        .sim-delta-neg { color: #EF4444; font-size: 14px; font-weight: bold; }
        .sim-delta-neu { color: #64748B; font-size: 14px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    def formatar_delta(valor, inverso=False):
        if valor == 0: return f"<span class='sim-delta-neu'>Sem alteração</span>"
        sinal = "+" if valor > 0 else ""
        cor = "sim-delta-pos" if (valor > 0 and not inverso) or (valor < 0 and inverso) else "sim-delta-neg"
        return f"<span class='{cor}'>{sinal}{formatar_moeda(valor)}</span>"

    def formatar_delta_perc(valor, inverso=False):
        if valor == 0: return f"<span class='sim-delta-neu'>Sem alteração</span>"
        sinal = "+" if valor > 0 else ""
        cor = "sim-delta-pos" if (valor > 0 and not inverso) or (valor < 0 and inverso) else "sim-delta-neg"
        return f"<span class='{cor}'>{sinal}{valor:.1f} p.p.</span>"

    with c1:
        delta_rec = proj_receita - receita_atual
        st.markdown(f"<div class='sim-card'><div class='sim-title'>Faturamento Estimado</div><div class='sim-value'>{formatar_moeda(proj_receita)}</div>{formatar_delta(delta_rec)}</div>", unsafe_allow_html=True)

    with c2:
        proj_saidas = proj_custos + proj_fixas
        saidas_atual = custos_atual + fixas_atual
        delta_saidas = proj_saidas - saidas_atual
        st.markdown(f"<div class='sim-card'><div class='sim-title'>Custos & Despesas Estimadas</div><div class='sim-value'>-{formatar_moeda(proj_saidas)}</div>{formatar_delta(delta_saidas, inverso=True)}</div>", unsafe_allow_html=True)

    with c3:
        delta_ebitda = proj_ebitda - ebitda_atual
        st.markdown(f"<div class='sim-card'><div class='sim-title'>Novo Resultado Líquido</div><div class='sim-value' style='color:#C5A059;'>{formatar_moeda(proj_ebitda)}</div>{formatar_delta(delta_ebitda)}</div>", unsafe_allow_html=True)

    with c4:
        delta_margem = proj_margem - margem_atual
        st.markdown(f"<div class='sim-card'><div class='sim-title'>Nova Margem Operacional</div><div class='sim-value'>{proj_margem:.1f}%</div>{formatar_delta_perc(delta_margem)}</div>", unsafe_allow_html=True)

    # ==========================================
    # 4. GRÁFICO DO NOVO CENÁRIO (CASCATA)
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 3. Estrutura do Novo Cenário Simulado")

    if proj_receita > 0:
        fig_waterfall = go.Figure(go.Waterfall(
            name="Cenário Simulado", orientation="v",
            measure=["relative", "relative", "relative", "relative", "total"],
            x=["Novo Faturamento", "Impostos Estimados", "Custos Projetados", "Despesas Fixas", "Novo EBITDA"],
            textposition="outside",
            text=[formatar_moeda(proj_receita), f"-{formatar_moeda(proj_impostos)}", f"-{formatar_moeda(proj_custos)}", f"-{formatar_moeda(proj_fixas)}", formatar_moeda(proj_ebitda)],
            y=[proj_receita, -proj_impostos, -proj_custos, -proj_fixas, proj_ebitda],
            connector={"line":{"color":"#475569", "width": 2, "dash": "dot"}},
            decreasing={"marker":{"color":"#E11D48"}}, 
            increasing={"marker":{"color":"#059669"}}, 
            totals={"marker":{"color":"#C5A059"}}      
        ))
        
        fig_waterfall.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(family="Helvetica Neue", color="#E2E8F0"),
            title=dict(text="Cascata de Resultados (Visão Projetada)", font=dict(color="#94A3B8", size=14)), 
            margin=dict(t=40, b=30, l=10, r=10),
            yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.2)', title="Valor (R$)")
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

    # Dica Consultiva
    if proj_ebitda > ebitda_atual:
        st.success("💡 **Diagnóstico do Cenário:** Este cenário gera **Criação de Valor**. O ajuste nas alavancas incrementou a geração de caixa em relação à realidade atual.")
    elif proj_ebitda < ebitda_atual:
        st.error("🚨 **Diagnóstico do Cenário:** Este cenário gera **Destruição de Valor**. As projeções de aumento de custos ou queda de receita penalizam gravemente o caixa da operação.")