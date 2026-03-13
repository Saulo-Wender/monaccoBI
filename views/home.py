import streamlit as st

def render():
    st.markdown("""
    <style>
        .home-container { padding: 2rem 0; }
        .hero-title { font-size: 2.5rem; font-weight: 700; color: #E2E8F0; margin-bottom: 0.5rem; }
        .hero-title span { color: #C5A059; }
        .hero-subtitle { font-size: 1.2rem; color: #94A3B8; margin-bottom: 3rem; font-weight: 300; }
        
        .step-card { background-color: #1E293B; border-left: 4px solid #C5A059; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .step-number { font-size: 1.5rem; font-weight: bold; color: #C5A059; margin-bottom: 10px; }
        .step-title { font-size: 1.1rem; font-weight: bold; color: #E2E8F0; margin-bottom: 5px; }
        .step-text { color: #94A3B8; font-size: 0.95rem; line-height: 1.5; }
        
        .contact-box { background-color: #0F172A; border: 1px solid #334155; padding: 20px; border-radius: 8px; text-align: center; margin-top: 40px; border-top: 3px solid #38BDF8; }
        .contact-box h4 { color: #E2E8F0; margin-top: 0; }
        .contact-box p { color: #94A3B8; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='home-container'>", unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("<div class='hero-title'>Central de Inteligência <span>Monacco</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Ambiente analítico exclusivo para Consultores e Backoffice.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([6, 4])

    with col1:
        st.markdown("### Workflow de Fecho Mensal")
        
        st.markdown("""
        <div class='step-card'>
            <div class='step-number'>01</div>
            <div class='step-title'>Importação da Base (Nibo)</div>
            <div class='step-text'>Extraia os relatórios do cliente no Nibo (Realizado e Pendentes) e faça o upload na barra lateral. O motor higieniza a base instantaneamente.</div>
        </div>
        
        <div class='step-card'>
            <div class='step-number'>02</div>
            <div class='step-title'>Auditoria e Classificação</div>
            <div class='step-text'>Acesse a <b>DRE Estruturada</b> e garanta que as categorias de Impostos, Custos Variáveis e Retiradas de Sócios estão mapeadas corretamente na barra lateral.</div>
        </div>
        
        <div class='step-card'>
            <div class='step-number'>03</div>
            <div class='step-title'>Geração do Dossiê Executivo</div>
            <div class='step-text'>Navegue pelas abas analíticas, calibre os saldos reais em banco e exporte os PDFs de cada módulo para enviar ao cliente ou preparar a reunião de apresentação.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Check-list de Análise:")
        st.info("📉 **Termômetro de Sócios:** O cliente está a descapitalizar a empresa? (Aba Boardroom)")
        st.info("🎯 **Ponto de Equilíbrio:** A meta mínima de vendas foi batida? (Aba Desempenho)")
        st.info("⏳ **Runway:** A empresa sobrevive 3 meses sem vendas? (Aba Desempenho)")
        st.info("🚨 **Risco de Caixa:** Há calotes ou vales da morte previstos? (Aba Radar)")
        st.info("🔍 **Pareto:** Há dependência perigosa de um cliente/fornecedor? (Aba Inteligência)")
        
        st.markdown("""
        <div class='contact-box'>
            <h4>Atenção ao Cliente</h4>
            <p>Lembre-se: O valor do nosso BPO não está nos gráficos, está na sua capacidade de traduzir estes números em ações para o dono da empresa.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)