import pandas as pd

# NOVO: A função agora aceita cat_socios
def calcular_metricas_dre(df: pd.DataFrame, cat_impostos: list, cat_custos: list, cat_socios: list = None) -> dict:
    if df is None or df.empty:
        return {k: 0 for k in ["receitas", "despesas", "saldo", "margem", "dre_impostos", "dre_custos", "dre_receita_liquida", "dre_margem_contribuicao", "dre_despesas_fixas", "dre_resultado", "retiradas_socios"]}

    if cat_socios is None:
        cat_socios = []

    receitas = df[df['Tipo'] == 'Receita']['Valor'].sum()
    despesas = df[df['Tipo'] == 'Despesa']['Valor'].sum()
    saldo = receitas - despesas
    margem = (saldo / receitas * 100) if receitas > 0 else 0

    dre_impostos = df[(df['Categoria'].isin(cat_impostos)) & (df['Tipo'] == 'Despesa')]['Valor'].sum()
    dre_custos = df[(df['Categoria'].isin(cat_custos)) & (df['Tipo'] == 'Despesa')]['Valor'].sum()

    dre_receita_liquida = receitas - dre_impostos
    dre_margem_contribuicao = dre_receita_liquida - dre_custos

    dre_despesas_fixas = despesas - dre_impostos - dre_custos
    dre_resultado = dre_margem_contribuicao - dre_despesas_fixas

    # NOVO: Cálculo das retiradas dos sócios isoladas
    retiradas_socios = df[(df['Categoria'].isin(cat_socios)) & (df['Tipo'] == 'Despesa')]['Valor'].sum()

    return {
        "receitas": receitas,
        "despesas": despesas,
        "saldo": saldo,
        "margem": margem,
        "dre_impostos": dre_impostos,
        "dre_custos": dre_custos,
        "dre_receita_liquida": dre_receita_liquida,
        "dre_margem_contribuicao": dre_margem_contribuicao,
        "dre_despesas_fixas": dre_despesas_fixas,
        "dre_resultado": dre_resultado,
        "retiradas_socios": retiradas_socios # Variável enviada para as Views
    }

def calcular_tendencia_mensal(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or 'Data' not in df.columns:
        return pd.DataFrame()

    df_temp = df.copy()
    df_temp['Mes_Ano'] = df_temp['Data'].dt.to_period('M')
    
    tendencia = df_temp.groupby(['Mes_Ano', 'Tipo'])['Valor'].sum().unstack().fillna(0)
    
    if 'Receita' not in tendencia.columns: tendencia['Receita'] = 0
    if 'Despesa' not in tendencia.columns: tendencia['Despesa'] = 0
        
    tendencia['Saldo'] = tendencia['Receita'] - tendencia['Despesa']
    tendencia.index = tendencia.index.astype(str)
    
    return tendencia.reset_index()