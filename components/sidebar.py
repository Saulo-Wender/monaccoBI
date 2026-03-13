import streamlit as st
import pandas as pd
from services.importacao import processar_arquivos_multiplos

def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='color: white !important; text-align: center;'>MONACCO</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.expander("📥 Nibo (Realizado / Caixa)", expanded=True):
            st.markdown("<small>Contas Recebidas (Entradas)</small>", unsafe_allow_html=True)
            arq_receitas = st.file_uploader("", type=["xlsx", "xls", "csv"], key="upload_rec")
            
            st.markdown("<small>Contas Pagas (Saídas)</small>", unsafe_allow_html=True)
            arq_despesas = st.file_uploader("", type=["xlsx", "xls", "csv"], key="upload_desp")

        with st.expander("📥 Nibo (Previsões / Pendentes)", expanded=False):
            st.markdown("<small>Contas a Receber (Clientes)</small>", unsafe_allow_html=True)
            arq_prev_rec = st.file_uploader("", type=["xlsx", "xls", "csv"], key="upload_prev_rec")
            
            st.markdown("<small>Contas a Pagar (Fornecedores)</small>", unsafe_allow_html=True)
            arq_prev_desp = st.file_uploader("", type=["xlsx", "xls", "csv"], key="upload_prev_desp")
        
        df, is_real_data = processar_arquivos_multiplos(arq_receitas, arq_despesas, arq_prev_rec, arq_prev_desp)

        st.markdown("---")
        st.header("⚙️ Filtros Executivos")
        
        empresas = df['Empresa'].unique().tolist() if 'Empresa' in df.columns else []
        empresa_selecionada = st.selectbox("Unidade de Negócio:", ["Todas as Unidades"] + empresas)
        
        if empresa_selecionada != "Todas as Unidades":
            df = df[df['Empresa'] == empresa_selecionada]

        if 'Data' in df.columns:
            df = df.dropna(subset=['Data']) 
            
        if df is None or df.empty:
            # Atualizado para retornar também a lista vazia do cat_socios
            return df, [], [], [], empresa_selecionada, None, None, pd.DataFrame()

        min_date = df['Data'].min().date()
        max_date = df['Data'].max().date()
        
        datas_selecionadas = st.date_input(
            "Horizonte de Análise:", 
            [min_date, max_date], 
            min_value=min_date, 
            max_value=max_date
        )
        
        if len(datas_selecionadas) == 2:
            data_inicio, data_fim = datas_selecionadas
        else:
            data_inicio = datas_selecionadas[0]
            data_fim = datas_selecionadas[0] 
            st.warning("⚠️ Selecione a data final no calendário.")
        
        df = df[(df['Data'].dt.date >= data_inicio) & (df['Data'].dt.date <= data_fim)]
        df_full = df.copy() 

        lista_status = df['Status'].unique().tolist()
        padrao_status = ['Pago/Recebido'] if 'Pago/Recebido' in lista_status else lista_status
        status_selecionado = st.multiselect("Estado (Visão Dashboard):", lista_status, default=padrao_status)
        df = df[df['Status'].isin(status_selecionado)]

        st.markdown("---")
        with st.expander("⚙️ Configuração da DRE e Sócios", expanded=False):
            todas_categorias = df_full['Categoria'].unique().tolist()
            
            cat_impostos_auto = [c for c in todas_categorias if any(x in str(c).strip().lower() for x in ['imposto', 'simples', 'iss', 'irpj', 'csll', 'iva', 'das'])]
            cat_custos_auto = [c for c in todas_categorias if any(x in str(c).strip().lower() for x in ['insumo', 'mercadoria', 'fornecedor', 'produto', 'deslocamento', 'comiss'])]
            # NOVO: Mapeamento de Sócios
            cat_socios_auto = [c for c in todas_categorias if any(x in str(c).strip().lower() for x in ['pró-labore', 'pro-labore', 'pro labore', 'lucro', 'sócio', 'socio', 'pessoal', 'retirada'])]
            
            if 'cat_impostos' not in st.session_state: st.session_state['cat_impostos'] = cat_impostos_auto
            if 'cat_custos' not in st.session_state: st.session_state['cat_custos'] = cat_custos_auto
            if 'cat_socios' not in st.session_state: st.session_state['cat_socios'] = cat_socios_auto
                
            safe_impostos_default = [c for c in st.session_state['cat_impostos'] if c in todas_categorias]
            safe_custos_default = [c for c in st.session_state['cat_custos'] if c in todas_categorias]
            safe_socios_default = [c for c in st.session_state['cat_socios'] if c in todas_categorias]

            if not safe_impostos_default and cat_impostos_auto: safe_impostos_default = cat_impostos_auto
            if not safe_custos_default and cat_custos_auto: safe_custos_default = cat_custos_auto
            if not safe_socios_default and cat_socios_auto: safe_socios_default = cat_socios_auto
                
            cat_impostos = st.multiselect("Mapear Impostos/Deduções", todas_categorias, default=safe_impostos_default)
            st.session_state['cat_impostos'] = cat_impostos 
            
            cat_custos = st.multiselect("Mapear Custos Variáveis", todas_categorias, default=safe_custos_default)
            st.session_state['cat_custos'] = cat_custos 
            
            # NOVO: Input de Sócios
            cat_socios = st.multiselect("Mapear Retiradas de Sócios (PF)", todas_categorias, default=safe_socios_default)
            st.session_state['cat_socios'] = cat_socios

    # Atualizado o Return para enviar o cat_socios
    return df, cat_impostos, cat_custos, cat_socios, empresa_selecionada, data_inicio, data_fim, df_full