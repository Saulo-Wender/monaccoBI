import pandas as pd
import numpy as np
import streamlit as st
from services.tratamento import gerar_dados_teste

def ler_e_padronizar(arquivo_upload, natureza_conta: str, status_forcado: str = None) -> pd.DataFrame:
    """Lê o arquivo individual, força a natureza e mapeia datas de vencimento vs pagamento."""
    try:
        if arquivo_upload.name.upper().endswith('.CSV'):
            try:
                df_bruto = pd.read_csv(arquivo_upload, sep=';', decimal=',', encoding='utf-8')
            except UnicodeDecodeError:
                arquivo_upload.seek(0)
                df_bruto = pd.read_csv(arquivo_upload, sep=';', decimal=',', encoding='latin1')
        else:
            df_bruto = pd.read_excel(arquivo_upload)
        
        df = pd.DataFrame()
        
        # 1. Tenta extrair a data padrão de Caixa (Nibo usa 'Data de pagamento' ou 'Data de recebimento')
        col_data = 'Data de pagamento' if 'Data de pagamento' in df_bruto.columns else ('Data de recebimento' if 'Data de recebimento' in df_bruto.columns else 'Vencimento')
        if col_data in df_bruto.columns:
            df['Data'] = pd.to_datetime(df_bruto[col_data], format='%d/%m/%Y', errors='coerce')
        else:
            df['Data'] = pd.NaT
            
        # 2. INTELIGÊNCIA DO RADAR: Extrair data de Vencimento original
        col_venc = 'Vencimento' if 'Vencimento' in df_bruto.columns else ('Data de vencimento' if 'Data de vencimento' in df_bruto.columns else col_data)
        if col_venc in df_bruto.columns:
            df['Vencimento'] = pd.to_datetime(df_bruto[col_venc], format='%d/%m/%Y', errors='coerce')
        else:
            df['Vencimento'] = df['Data'] # Fallback
            
        # Extração de valores (Positivo Absoluto)
        col_valor = 'Valor categoria/centro de custo' if 'Valor categoria/centro de custo' in df_bruto.columns else 'Valor'
        if col_valor in df_bruto.columns:
            valores = pd.to_numeric(df_bruto[col_valor].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            df['Valor'] = valores.abs()
        else:
            df['Valor'] = 0.0

        df['Tipo'] = natureza_conta
        df['Categoria'] = df_bruto.get('Categoria', 'Diversos').fillna('Sem Categoria')
        df['Descrição'] = df_bruto.get('Descrição', '').fillna('-')
        df['Pessoa'] = df_bruto.get('Nome', 'Não informado').fillna('Não informado')
        df['Empresa'] = 'Dados Importados (Nibo)'

        # Força o status correto com base no upload
        if status_forcado:
            df['Status'] = status_forcado
        else:
            df['Status'] = np.where(df_bruto.get(col_data).notna(), 'Pago/Recebido', 'Pendente')

        return df
    except Exception as e:
        st.sidebar.error(f"Erro ao processar {arquivo_upload.name}: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def processar_arquivos_multiplos(arq_rec, arq_desp, arq_prev_rec, arq_prev_desp):
    """Consolida os ficheiros de caixa realizado e previsões futuras."""
    frames = []
    
    if arq_rec:
        df1 = ler_e_padronizar(arq_rec, "Receita", status_forcado="Pago/Recebido")
        if not df1.empty: frames.append(df1)
            
    if arq_desp:
        df2 = ler_e_padronizar(arq_desp, "Despesa", status_forcado="Pago/Recebido")
        if not df2.empty: frames.append(df2)
        
    if arq_prev_rec:
        df3 = ler_e_padronizar(arq_prev_rec, "Receita", status_forcado="Pendente")
        if not df3.empty: frames.append(df3)
        
    if arq_prev_desp:
        df4 = ler_e_padronizar(arq_prev_desp, "Despesa", status_forcado="Pendente")
        if not df4.empty: frames.append(df4)
            
    if frames:
        df_consolidado = pd.concat(frames, ignore_index=True)
        return df_consolidado, True
    else:
        return gerar_dados_teste(), False