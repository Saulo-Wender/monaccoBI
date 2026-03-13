import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.formatters import formatar_moeda
from utils.relatorio_radar import criar_download_relatorio_radar

def render(df_full):
    st.markdown("### 🚨 Radar de Inadimplência e Risco de Caixa", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-bottom: 1rem;'>Análise preditiva de obrigações, identificação de atrasos e projeção de saldo futuro.</p>", unsafe_allow_html=True)

    if df_full.empty or 'Status' not in df_full.columns:
        st.info("Por favor, faça o upload das planilhas de Previsão (Pendentes) na barra lateral para utilizar o Radar.")
        return

    df_pendente = df_full[df_full['Status'] == 'Pendente'].copy()

    if df_pendente.empty:
        st.success("🎉 Excelente notícia! Não há contas pendentes ou em atraso registadas no momento.")
        return

    # Entrada do Saldo Real para Calibração
    st.markdown("<div style='background-color: #0F172A; padding: 15px; border-radius: 8px; border-left: 4px solid #38BDF8; margin-bottom: 20px;'>", unsafe_allow_html=True)
    saldo_banco = st.number_input("💰 Calibragem da Projeção: Qual é o Saldo Atual Real na conta bancária da empresa? (R$)", value=0.0, step=100.0)
    st.markdown("</div>", unsafe_allow_html=True)

    if 'Vencimento' not in df_pendente.columns:
        if 'Data' in df_pendente.columns:
            df_pendente['Vencimento'] = df_pendente['Data']
        else:
            st.warning("⚠️ Os dados importados não contêm informações de data para calcular os vencimentos.")
            return

    hoje = pd.Timestamp(datetime.today().date())
    df_pendente['Vencimento'] = pd.to_datetime(df_pendente['Vencimento'], errors='coerce')
    df_pendente['Condicao'] = df_pendente['Vencimento'].apply(
        lambda x: "Atrasado" if pd.notnull(x) and x < hoje else "A Vencer"
    )

    rec_pend = df_pendente[df_pendente['Tipo'] == 'Receita']
    desp_pend = df_pendente[df_pendente['Tipo'] == 'Despesa']

    # CÁLCULOS FINANCEIROS ATRASOS
    rec_atrasada = rec_pend[rec_pend['Condicao'] == 'Atrasado']['Valor'].sum()
    rec_futura = rec_pend[rec_pend['Condicao'] == 'A Vencer']['Valor'].sum()
    desp_atrasada = desp_pend[desp_pend['Condicao'] == 'Atrasado']['Valor'].sum()
    desp_futura = desp_pend[desp_pend['Condicao'] == 'A Vencer']['Valor'].sum()

    qtd_rec_atrasada = len(rec_pend[rec_pend['Condicao'] == 'Atrasado'])
    qtd_rec_futura = len(rec_pend[rec_pend['Condicao'] == 'A Vencer'])
    qtd_desp_atrasada = len(desp_pend[desp_pend['Condicao'] == 'Atrasado'])
    qtd_desp_futura = len(desp_pend[desp_pend['Condicao'] == 'A Vencer'])

    df_devedores = rec_pend[rec_pend['Condicao'] == 'Atrasado'].groupby('Pessoa')['Valor'].sum().reset_index().sort_values(by='Valor', ascending=False).head(5)
    if not df_devedores.empty:
        df_devedores.rename(columns={'Pessoa': 'Cliente / Empresa', 'Valor': 'Montante Retido'}, inplace=True)
        df_devedores_print = df_devedores.copy()
        df_devedores_print['Montante Retido'] = df_devedores_print['Montante Retido'].apply(formatar_moeda)
    else:
        df_devedores_print = pd.DataFrame()

    df_credores = desp_pend[desp_pend['Condicao'] == 'Atrasado'].groupby('Pessoa')['Valor'].sum().reset_index().sort_values(by='Valor', ascending=False).head(5)
    if not df_credores.empty:
        df_credores.rename(columns={'Pessoa': 'Fornecedor / Entidade', 'Valor': 'Montante Devido'}, inplace=True)
        df_credores_print = df_credores.copy()
        df_credores_print['Montante Devido'] = df_credores_print['Montante Devido'].apply(formatar_moeda)
    else:
        df_credores_print = pd.DataFrame()

    # =========================================================
    # MOTOR DA PROJEÇÃO DE CAIXA (Cálculo antes do PDF)
    # =========================================================
    df_projecao = df_pendente.copy()
    hoje_data = hoje.date()
    df_projecao['Data_Base'] = df_projecao['Vencimento'].dt.date
    df_projecao.loc[df_projecao['Data_Base'] < hoje_data, 'Data_Base'] = hoje_data
    
    status_projecao = "Saudavel"
    dia_critico = None
    valor_critico = 0
    df_fluxo = pd.DataFrame()
    
    if not df_projecao.empty:
        df_agrupado = df_projecao.groupby(['Data_Base', 'Tipo'])['Valor'].sum().unstack(fill_value=0).reset_index()
        if 'Receita' not in df_agrupado.columns: df_agrupado['Receita'] = 0
        if 'Despesa' not in df_agrupado.columns: df_agrupado['Despesa'] = 0
        
        datas_futuras = pd.date_range(start=hoje_data, periods=30).date
        df_calendario = pd.DataFrame({'Data_Base': datas_futuras})
        
        df_fluxo = pd.merge(df_calendario, df_agrupado, on='Data_Base', how='left').fillna(0)
        df_fluxo['Movimento_Liquido'] = df_fluxo['Receita'] - df_fluxo['Despesa']
        df_fluxo['Saldo_Acumulado'] = df_fluxo['Movimento_Liquido'].cumsum() + saldo_banco
        
        dias_negativos = df_fluxo[df_fluxo['Saldo_Acumulado'] < 0]
        if not dias_negativos.empty:
            status_projecao = "Ruptura"
            dia_critico = dias_negativos.iloc[0]['Data_Base'].strftime('%d/%m/%Y')
            valor_critico = dias_negativos.iloc[0]['Saldo_Acumulado']

    # --- BOTÃO DE EXPORTAÇÃO (AGORA CAPTURA O ALERTA) ---
    empresa_nome = df_full['Empresa'].iloc[0] if 'Empresa' in df_full.columns else "Cliente Monacco"
    link_download = criar_download_relatorio_radar(
        empresa_nome, rec_atrasada, qtd_rec_atrasada, rec_futura, qtd_rec_futura, 
        desp_atrasada, qtd_desp_atrasada, desp_futura, qtd_desp_futura, 
        df_devedores_print, df_credores_print, 
        saldo_banco, status_projecao, dia_critico, valor_critico
    )
    st.markdown(link_download, unsafe_allow_html=True)
    st.markdown("---")
    # ---------------------------------------------------

    # RENDERIZAÇÃO GRÁFICA DA PROJEÇÃO
    st.markdown("### 📉 Projeção de Caixa (Próximos 30 Dias)")
    if not df_fluxo.empty:
        fig_proj = go.Figure()
        fig_proj.add_hline(y=0, line_dash="dash", line_color="#EF4444", line_width=2, annotation_text="Limite Zero (Vale da Morte)", annotation_position="top left", annotation_font_color="#EF4444")
        
        cores_linha = ['#10B981' if saldo >= 0 else '#EF4444' for saldo in df_fluxo['Saldo_Acumulado']]
        
        fig_proj.add_trace(go.Scatter(
            x=df_fluxo['Data_Base'], 
            y=df_fluxo['Saldo_Acumulado'],
            fill='tozeroy',
            fillcolor='rgba(56, 189, 248, 0.1)',
            mode='lines+markers',
            line=dict(color='#38BDF8', width=3),
            marker=dict(size=6, color=cores_linha),
            name='Saldo Projetado',
            hovertemplate='<b>%{x}</b><br>Saldo Estimado: R$ %{y:,.2f}<extra></extra>'
        ))
        
        fig_proj.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(family="Helvetica Neue", color="#E2E8F0"),
            margin=dict(t=20, b=10, l=10, r=10),
            hovermode="x unified",
            yaxis=dict(showgrid=True, gridcolor='rgba(148, 163, 184, 0.2)', title="Saldo em Caixa (R$)")
        )
        st.plotly_chart(fig_proj, use_container_width=True)
        
        if status_projecao == "Ruptura":
            st.error(f"🚨 **ALERTA DE RUPTURA DE CAIXA:** Se as previsões se confirmarem, o saldo da empresa ficará **negativo** ({formatar_moeda(valor_critico)}) no dia **{dia_critico}**. Ação imediata é necessária.")
        else:
            st.success("✅ **FLUXO SAUDÁVEL:** O saldo projetado para os próximos 30 dias mantém-se positivo.")

    # Painel de Impacto Financeiro (Atrasos)
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🟢 Entradas a Receber (Clientes)")
        st.metric("Valores em Atraso (Inadimplência)", formatar_moeda(rec_atrasada), delta=f"{qtd_rec_atrasada} títulos | Atenção - Cobrar" if rec_atrasada > 0 else "0 títulos | Recebimentos em Dia", delta_color="inverse")
        st.metric("Fluxo Futuro Seguro (A Vencer)", formatar_moeda(rec_futura), delta=f"{qtd_rec_futura} títulos programados", delta_color="normal")

    with col2:
        st.markdown("#### 🔴 Saídas a Pagar (Fornecedores)")
        st.metric("Passivo em Atraso (Risco de Multa)", formatar_moeda(desp_atrasada), delta=f"{qtd_desp_atrasada} faturas | Risco Legal" if desp_atrasada > 0 else "0 faturas | Pagamentos em Dia", delta_color="inverse")
        st.metric("Obrigações Futuras (A Vencer)", formatar_moeda(desp_futura), delta=f"{qtd_desp_futura} faturas previstas", delta_color="off")

    st.markdown("---")
    st.markdown("### Top Inadimplentes e Credores (Lista de Foco)")

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.error(f"**Top 5 Clientes em Atraso**")
        if not df_devedores_print.empty:
            st.dataframe(df_devedores_print, hide_index=True, use_container_width=True)
        else:
            st.info("Nenhum cliente está em atraso com pagamentos.")

    with col_t2:
        st.warning(f"**Top 5 Contas Atrasadas**")
        if not df_credores_print.empty:
            st.dataframe(df_credores_print, hide_index=True, use_container_width=True)
        else:
            st.info("A empresa não possui obrigações em atraso.")