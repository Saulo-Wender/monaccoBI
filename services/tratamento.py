import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data
def gerar_dados_teste():
    """Gera um DataFrame fictício para demonstração da plataforma quando não há upload."""
    np.random.seed(42)
    datas = [datetime(2023, 1, 1) + timedelta(days=x) for x in range(365)]
    categorias_receita = ['Consultoria Estratégica', 'Projetos de Implantação', 'Licenças de Software', 'Mentoria']
    categorias_impostos = ['Simples Nacional', 'ISS']
    categorias_custos_var = ['Comissões Vendas', 'Serviços Terceiros', 'Deslocamento']
    categorias_despesas_fixas = ['Folha de Pagamento', 'Aluguel Sede', 'Software BPO', 'Marketing e Tráfego', 'Contabilidade Monacco']
    
    dados = []
    for _ in range(800):
        tipo_macro = np.random.choice(['Receita', 'Imposto', 'Custo_Var', 'Despesa_Fixa'], p=[0.35, 0.1, 0.15, 0.4])
        if tipo_macro == 'Receita':
            tipo, categoria, valor = 'Receita', np.random.choice(categorias_receita), np.random.normal(15000, 4000)
        elif tipo_macro == 'Imposto':
            tipo, categoria, valor = 'Despesa', np.random.choice(categorias_impostos), np.random.normal(1500, 300)
        elif tipo_macro == 'Custo_Var':
            tipo, categoria, valor = 'Despesa', np.random.choice(categorias_custos_var), np.random.normal(2000, 800)
        else:
            tipo, categoria, valor = 'Despesa', np.random.choice(categorias_despesas_fixas), np.random.normal(3000, 1000)
            
        dados.append({
            'Data': np.random.choice(datas), 'Tipo': tipo, 'Categoria': categoria,
            'Descrição': f'Ref. {categoria}', 'Pessoa': np.random.choice(['Tech Corp', 'Global Retail', 'Fornecedor Premium', 'Agência XPTO', 'Cliente Alpha']),
            'Valor': abs(valor), 'Status': np.random.choice(['Pago/Recebido', 'Pendente'], p=[0.85, 0.15]),
            'Empresa': 'Cliente Demonstração S.A.'
        })
    return pd.DataFrame(dados)