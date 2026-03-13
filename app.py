import streamlit as st
from assets.styles import aplicar_estilos
from components.sidebar import render_sidebar
from services.calculos import calcular_metricas_dre, calcular_tendencia_mensal
from utils.exportacao import convert_df_to_csv

# Importação das views (AGORA COM O RAIO-X)
from views import home, dashboard, boardroom, kpis, dre, inteligencia, radar, explorador, desempenho, raiox

st.set_page_config(
    page_title="Monacco BI | Executive Finance",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    aplicar_estilos()

    col_logo, col_title = st.columns([1, 8])
    with col_title:
        st.markdown("<h1>Monacco BI <span style='color: #64748B; font-weight: 300;'>| Executive Finance</span></h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-size: 18px;'>Plataforma de Inteligência Analítica para Gestão de Resultados</p>", unsafe_allow_html=True)

    df, cat_impostos, cat_custos, cat_socios, empresa_selecionada, data_inicio, data_fim, df_full = render_sidebar()

    fez_upload = any(st.session_state.get(key) is not None for key in ['upload_rec', 'upload_desp', 'upload_prev_rec', 'upload_prev_desp'])
    
    if not fez_upload:
        st.warning("⚠️ **NENHUM CLIENTE CARREGADO:** O sistema está a gerar dados de teste. Analista, faça o upload das planilhas do Nibo na barra lateral para processar a carteira real.")

    if df_full is None or df_full.empty:
        st.error("⚠️ Erro crítico: Falha ao carregar a base de dados.")
        st.stop()

    with st.spinner("A processar dados financeiros..."):
        metricas = calcular_metricas_dre(df, cat_impostos, cat_custos, cat_socios)
        metricas['df_tendencia'] = calcular_tendencia_mensal(df)
        metricas['data_inicio'] = data_inicio
        metricas['data_fim'] = data_fim
        metricas['empresa'] = empresa_selecionada

    tem_radar = 'Status' in df_full.columns and not df_full[df_full['Status'] == 'Pendente'].empty

    # INCLUINDO O RAIO-X NAS ABAS
    titulos_abas = [
        "🏠 Início",
        "📈 Dashboard", 
        "🖥️ Boardroom", 
        "📊 Finanças",
        "📑 DRE",
        "🚀 Desempenho",
        "🔬 Raio-X Unidades" # <--- NOVA ABA AQUI
    ]
    
    if tem_radar:
        titulos_abas.append("🚨 Radar")
        
    titulos_abas.extend([
        "🔍 Inteli. ABC", 
        "🔎 Explorador", 
        "📤 Exportação"
    ])

    abas = st.tabs(titulos_abas)

    # DISTRIBUIÇÃO
    with abas[titulos_abas.index("🏠 Início")]: 
        home.render() 

    with abas[titulos_abas.index("📈 Dashboard")]: 
        dashboard.render(df, metricas)
        
    with abas[titulos_abas.index("🖥️ Boardroom")]: 
        boardroom.render(metricas)
        
    with abas[titulos_abas.index("📊 Finanças")]: 
        kpis.render(metricas)
        
    with abas[titulos_abas.index("📑 DRE")]: 
        dre.render(df, metricas)
        
    with abas[titulos_abas.index("🚀 Desempenho")]: 
        desempenho.render(df_full, metricas)
        
    with abas[titulos_abas.index("🔬 Raio-X Unidades")]: 
        raiox.render(df_full) # RENDERIZA O RAIO X
    
    if tem_radar:
        with abas[titulos_abas.index("🚨 Radar")]: 
            radar.render(df_full) 
            
    with abas[titulos_abas.index("🔍 Inteli. ABC")]: 
        inteligencia.render(df)
        
    with abas[titulos_abas.index("🔎 Explorador")]: 
        explorador.render(df, metricas)
        
    with abas[titulos_abas.index("📤 Exportação")]:
        st.subheader("Central de Descargas")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            st.markdown("#### 1. DRE Gerencial")
            if 'dre_export' in st.session_state:
                csv_dre = convert_df_to_csv(st.session_state['dre_export'])
                st.download_button("📥 Baixar DRE (.csv)", data=csv_dre, file_name=f"DRE_Monacco_{empresa_selecionada}.csv", mime='text/csv')
                
        with col_exp2:
            st.markdown("#### 2. Base Tratada Consolidada")
            csv_raw = convert_df_to_csv(df_full)
            st.download_button("📥 Baixar Transações (.csv)", data=csv_raw, file_name=f"Transacoes_Totais_{empresa_selecionada}.csv", mime='text/csv')

if __name__ == "__main__":
    main()