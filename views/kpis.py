import streamlit as st
import plotly.graph_objects as go
from utils.formatters import formatar_moeda
from utils.relatorio_financas import criar_download_relatorio_financas

def render(metricas):
    st.markdown("### 📊 Finanças Corporativas e Eficiência", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-bottom: 1rem;'>Análise de Unit Economics, Decomposição da Receita e Volume de Negócio.</p>", unsafe_allow_html=True)

    if metricas is None or metricas.get('receitas', 0) == 0:
        st.warning("Dados de receita insuficientes para calcular a eficiência corporativa.")
        return

    # Extração de Métricas
    receitas = metricas.get('receitas', 0)
    impostos = abs(metricas.get('dre_impostos', 0))
    custos = abs(metricas.get('dre_custos', 0))
    fixas = abs(metricas.get('dre_despesas_fixas', 0))
    ebitda = metricas.get('dre_resultado', 0)

    p_imp = (impostos / receitas) * 100
    p_cus = (custos / receitas) * 100
    p_fix = (fixas / receitas) * 100
    p_lucro = (ebitda / receitas) * 100

    ticket_medio = 0 
    qtd_vendas = 0

    # --- BOTÃO DE EXPORTAÇÃO ---
    empresa_nome = metricas.get('empresa', 'Cliente Monacco')
    link_download = criar_download_relatorio_financas(
        empresa_nome, receitas, impostos, custos, fixas, ebitda, qtd_vendas, ticket_medio
    )
    st.markdown(link_download, unsafe_allow_html=True)
    st.markdown("---")

    col_1, col_2 = st.columns([5, 5])

    # 1. DECOMPOSIÇÃO DE R$ 100
    with col_1:
        st.markdown("#### 💵 A cada R$ 100 faturados, para onde vai o dinheiro?")
        st.markdown("<p style='font-size: 13px; color: #64748B; margin-bottom: 20px;'>A estrutura de custos absorve o faturamento até sobrar a margem real.</p>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 5px; color: #E2E8F0;'>
                <span>Impostos ({p_imp:.1f}%)</span>
                <span style='font-weight: bold;'>R$ {p_imp:.2f}</span>
            </div>
            <div style='background-color: #1E293B; border-radius: 10px; height: 12px; width: 100%;'>
                <div style='background-color: #F59E0B; height: 100%; border-radius: 10px; width: {p_imp}%;'></div>
            </div>
        </div>
        
        <div style='margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 5px; color: #E2E8F0;'>
                <span>Custos Variáveis ({p_cus:.1f}%)</span>
                <span style='font-weight: bold;'>R$ {p_cus:.2f}</span>
            </div>
            <div style='background-color: #1E293B; border-radius: 10px; height: 12px; width: 100%;'>
                <div style='background-color: #EF4444; height: 100%; border-radius: 10px; width: {p_cus}%;'></div>
            </div>
        </div>
        
        <div style='margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 5px; color: #E2E8F0;'>
                <span>Despesas Fixas ({p_fix:.1f}%)</span>
                <span style='font-weight: bold;'>R$ {p_fix:.2f}</span>
            </div>
            <div style='background-color: #1E293B; border-radius: 10px; height: 12px; width: 100%;'>
                <div style='background-color: #64748B; height: 100%; border-radius: 10px; width: {p_fix}%;'></div>
            </div>
        </div>
        
        <div style='margin-top: 25px; padding: 15px; background-color: #0F172A; border-radius: 8px; border-left: 4px solid {'#10B981' if ebitda > 0 else '#EF4444'};'>
            <div style='display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 5px; color: #E2E8F0;'>
                <span style='font-weight: bold; color: #C5A059;'>Lucro Restante (EBITDA)</span>
                <span style='font-weight: bold; color: {'#10B981' if ebitda > 0 else '#EF4444'};'>R$ {p_lucro:.2f}</span>
            </div>
            <p style='margin: 0; font-size: 12px; color: #94A3B8;'>De cada 100 Reais que entram, sobram {p_lucro:.1f} Reais livres na operação.</p>
        </div>
        """, unsafe_allow_html=True)

    # 2. FUNIL DE ABSORÇÃO DE CAIXA (CORRIGIDO)
    with col_2:
        st.markdown("#### 🌪️ Funil de Absorção (Erosão do Faturamento)")
        
        # Valores calculados
        v_receitas = receitas
        v_apos_imp = receitas - impostos
        v_apos_cus = v_apos_imp - custos
        v_ebitda = ebitda

        # Textos pré-formatados para evitar dezenas de casas decimais e garantir legibilidade
        textos_funil = [
            f"{formatar_moeda(v_receitas)}<br>100%",
            f"{formatar_moeda(v_apos_imp)}<br>{(v_apos_imp/receitas)*100:.1f}%",
            f"{formatar_moeda(v_apos_cus)}<br>{(v_apos_cus/receitas)*100:.1f}%",
            f"{formatar_moeda(v_ebitda)}<br>{(v_ebitda/receitas)*100:.1f}%"
        ]

        fig_funnel = go.Figure(go.Funnel(
            y = ["Faturamento Bruto", "Após Impostos", "Margem Contrib.", "Lucro (EBITDA)"],
            x = [v_receitas, v_apos_imp, v_apos_cus, v_ebitda],
            textinfo = "text",
            text = textos_funil,
            marker = {"color": ["#38BDF8", "#F59E0B", "#8B5CF6", "#10B981" if ebitda > 0 else "#EF4444"]},
            textfont = dict(color="white", size=14, family="Helvetica Neue") # Força a cor branca para leitura perfeita
        ))

        fig_funnel.update_layout(
            margin=dict(t=20, b=10, l=10, r=10),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Helvetica Neue", color="#E2E8F0", size=13),
            height=320
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    # 3. PAINEL DE AVALIAÇÃO DE EFICIÊNCIA (DESIGN CORRIGIDO)
    st.markdown("---")
    st.markdown("### 🔍 Diagnóstico de Eficiência Estrutural")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        cor_alerta1 = "#EF4444" if p_imp > 15 else "#10B981"
        texto_alerta1 = "Alto (Requer planeamento)" if p_imp > 15 else "Adequado"
        st.markdown(f"""
        <div style='background-color: #0F172A; border: 1px solid #1E293B; border-top: 4px solid #F59E0B; border-radius: 8px; padding: 20px; text-align: center;'>
            <h4 style='margin:0; color:#94A3B8; font-size:13px; text-transform:uppercase;'>Peso Tributário</h4>
            <h2 style='margin:10px 0; color:white; font-size: 28px;'>{p_imp:.1f}%</h2>
            <p style='margin:0; font-size:13px; font-weight:bold; color:{cor_alerta1};'>{texto_alerta1}</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        cor_alerta2 = "#EF4444" if p_cus > 50 else "#10B981"
        texto_alerta2 = "Crítico (Baixa Margem)" if p_cus > 50 else "Controlado"
        st.markdown(f"""
        <div style='background-color: #0F172A; border: 1px solid #1E293B; border-top: 4px solid #EF4444; border-radius: 8px; padding: 20px; text-align: center;'>
            <h4 style='margin:0; color:#94A3B8; font-size:13px; text-transform:uppercase;'>Custo da Operação</h4>
            <h2 style='margin:10px 0; color:white; font-size: 28px;'>{p_cus:.1f}%</h2>
            <p style='margin:0; font-size:13px; font-weight:bold; color:{cor_alerta2};'>{texto_alerta2}</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        cor_alerta3 = "#EF4444" if p_fix > 35 else "#10B981"
        texto_alerta3 = "Empresa Pesada (Risco)" if p_fix > 35 else "Estrutura Enxuta"
        st.markdown(f"""
        <div style='background-color: #0F172A; border: 1px solid #1E293B; border-top: 4px solid #64748B; border-radius: 8px; padding: 20px; text-align: center;'>
            <h4 style='margin:0; color:#94A3B8; font-size:13px; text-transform:uppercase;'>Peso da Estrutura Fixa</h4>
            <h2 style='margin:10px 0; color:white; font-size: 28px;'>{p_fix:.1f}%</h2>
            <p style='margin:0; font-size:13px; font-weight:bold; color:{cor_alerta3};'>{texto_alerta3}</p>
        </div>
        """, unsafe_allow_html=True)