import streamlit as st

def aplicar_estilos():
    """Estilização complementar para os componentes customizados da Monacco."""
    st.markdown("""
        <style>
        /* =========================================================
           CARDS DE MÉTRICAS (Kpis Superiores)
           ========================================================= */
        [data-testid="metric-container"] {
            background-color: #1E293B !important;
            border: 1px solid rgba(197, 160, 89, 0.2) !important;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        [data-testid="stMetricLabel"] {color: #94A3B8 !important; font-size: 14px !important; font-weight: 600; text-transform: uppercase;}
        [data-testid="stMetricValue"] {color: #F8FAFC !important; font-size: 30px !important; font-weight: 800;}
        
        /* Títulos Gerais e Abas */
        h1, h2, h3, h4 {color: #C5A059 !important; font-family: 'Helvetica Neue', sans-serif;}
        
        button[data-baseweb="tab"] {background-color: transparent !important; color: #94A3B8 !important;}
        button[data-baseweb="tab"][aria-selected="true"] {color: #C5A059 !important; border-bottom: 2px solid #C5A059 !important;}

        /* =========================================================
           MODO BOARDROOM E FINANÇAS CORPORATIVAS
           ========================================================= */
        .board-container {
            background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%); 
            padding: 40px; border-radius: 16px; border: 1px solid rgba(197, 160, 89, 0.2);
        }
        .board-title {font-size: 38px !important; font-weight: 800; color: #C5A059; text-align: center; margin-bottom: 5px;}
        .board-subtitle {font-size: 16px; text-align: center; color: #94A3B8; margin-bottom: 30px;}
        .board-metric-box {background-color: rgba(11, 17, 32, 0.8); padding: 30px; border-radius: 12px; text-align: center; border: 1px solid rgba(197, 160, 89, 0.3);}
        .board-label {font-size: 15px; color: #94A3B8; text-transform: uppercase;}
        .board-value {font-size: 42px !important; font-weight: 800; margin: 10px 0;}
        .board-value-fat {color: #C5A059 !important;} 
        .board-value-pos {color: #34D399 !important;} 
        .board-value-neg {color: #F87171 !important;} 
        
        .kpi-box {border-left: 4px solid #C5A059; background-color: #1E293B; padding: 20px; border-radius: 8px; margin-bottom: 15px;}
        .kpi-title {font-size: 17px; font-weight: bold; color: #F8FAFC;}
        .kpi-value {font-size: 26px; font-weight: 800; color: #C5A059; margin-top: 5px;}
        .kpi-desc {font-size: 13px; color: #94A3B8;}
        </style>
    """, unsafe_allow_html=True)