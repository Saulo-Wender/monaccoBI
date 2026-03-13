import base64
from datetime import datetime
from utils.formatters import formatar_moeda

def criar_download_relatorio_radar(empresa, rec_atrasada, qtd_rec_atrasada, rec_futura, qtd_rec_futura, desp_atrasada, qtd_desp_atrasada, desp_futura, qtd_desp_futura, df_devedores, df_credores, saldo_atual, status_projecao, data_critica=None, valor_critico=0):
    """Gera o relatório HTML exclusivo do Radar de Caixa com Projeção."""
    
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    
    tabela_devedores = df_devedores.to_html(index=False, classes='tabela-monacco', border=0) if not df_devedores.empty else "<p>Nenhum cliente em atraso.</p>"
    tabela_credores = df_credores.to_html(index=False, classes='tabela-monacco', border=0) if not df_credores.empty else "<p>Nenhuma obrigação em atraso.</p>"

    # Bloco de alerta dinâmico para o "Vale da Morte"
    if status_projecao == "Ruptura":
        cor_alerta = "#EF4444" # Vermelho
        titulo_alerta = "🚨 ALERTA CRÍTICO: RUPTURA DE CAIXA IMINENTE"
        texto_alerta = f"Baseado no saldo bancário atual ({formatar_moeda(saldo_atual)}) e nas obrigações pendentes, o fluxo de caixa ficará <b>NEGATIVO ({formatar_moeda(valor_critico)}) no dia {data_critica}</b>. Ações imediatas de antecipação de recebíveis, injeção de capital ou postergação de pagamentos são obrigatórias."
    else:
        cor_alerta = "#10B981" # Verde
        titulo_alerta = "✅ PROJEÇÃO 30 DIAS: FLUXO SAUDÁVEL"
        texto_alerta = f"Baseado no saldo bancário atual ({formatar_moeda(saldo_atual)}), as projeções indicam que a operação tem liquidez para cobrir as obrigações dos próximos 30 dias sem risco de ruptura iminente."

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - Radar de Caixa</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;700&display=swap');
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1E293B; background-color: #F8FAFC; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-top: 8px solid #0F172A; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo-monacco {{ font-size: 28px; font-weight: 700; color: #0F172A; letter-spacing: 2px; }}
            .logo-monacco span {{ color: #C5A059; font-weight: 300; }}
            .info-cliente h1 {{ margin: 0; font-size: 22px; color: #334155; }}
            .info-cliente p {{ margin: 5px 0 0 0; color: #64748B; font-size: 14px; }}
            
            .alerta-projecao {{ background-color: {cor_alerta}15; border: 2px solid {cor_alerta}; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
            .alerta-projecao h2 {{ margin: 0 0 10px 0; font-size: 16px; color: {cor_alerta}; text-transform: uppercase; }}
            .alerta-projecao p {{ margin: 0; font-size: 15px; color: #1E293B; line-height: 1.5; }}
            
            .grid {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ flex: 1; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; background: #F8FAFC; }}
            .card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #64748B; text-transform: uppercase; }}
            .card .valor {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
            .card .qtd {{ font-size: 13px; color: #94A3B8; font-weight: bold; }}
            
            .text-red {{ color: #EF4444; }}
            .text-green {{ color: #10B981; }}
            
            h3.section-title {{ color: #0F172A; border-bottom: 2px solid #C5A059; padding-bottom: 5px; margin-top: 40px; }}
            
            .tabela-monacco {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
            .tabela-monacco th {{ background-color: #1E293B; color: white; padding: 12px; text-align: left; }}
            .tabela-monacco td {{ padding: 12px; border-bottom: 1px solid #E2E8F0; }}
            .tabela-monacco tr:nth-child(even) {{ background-color: #F8FAFC; }}
            
            .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 20px; }}
            
            @media print {{ body {{ background-color: white; padding: 0; }} .container {{ box-shadow: none; padding: 0; border: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-monacco">MONACCO <span>FINANCE</span></div>
                <div class="info-cliente">
                    <h1>Radar de Caixa</h1>
                    <p>Unidade: <b>{empresa}</b> | Ref: {data_hoje}</p>
                </div>
            </div>
            
            <div class="alerta-projecao">
                <h2>{titulo_alerta}</h2>
                <p>{texto_alerta}</p>
            </div>
            
            <div class="grid">
                <div class="card" style="border-top: 4px solid #10B981;">
                    <h3>Entradas a Receber</h3>
                    <div class="valor text-red">{formatar_moeda(rec_atrasada)} <span style="font-size: 12px;">em atraso</span></div>
                    <div class="qtd">{qtd_rec_atrasada} títulos pendentes</div>
                    <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 15px 0;">
                    <div class="valor text-green">{formatar_moeda(rec_futura)} <span style="font-size: 12px;">a vencer</span></div>
                    <div class="qtd">{qtd_rec_futura} títulos programados</div>
                </div>
                
                <div class="card" style="border-top: 4px solid #EF4444;">
                    <h3>Saídas a Pagar</h3>
                    <div class="valor text-red">{formatar_moeda(desp_atrasada)} <span style="font-size: 12px;">em atraso</span></div>
                    <div class="qtd">{qtd_desp_atrasada} obrigações vencidas</div>
                    <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 15px 0;">
                    <div class="valor" style="color: #64748B;">{formatar_moeda(desp_futura)} <span style="font-size: 12px;">a vencer</span></div>
                    <div class="qtd">{qtd_desp_futura} obrigações futuras</div>
                </div>
            </div>
            
            <h3 class="section-title">🔴 Top 5 Clientes Devedores (Ações de Cobrança Sugeridas)</h3>
            {tabela_devedores}
            
            <h3 class="section-title">🟠 Top 5 Obrigações Atrasadas (Risco de Bloqueio/Multa)</h3>
            {tabela_credores}
            
            <div class="footer">
                Documento gerado confidencialmente por Monacco Finance BPO.<br>
                Inteligência Analítica para Gestão de Resultados.
            </div>
        </div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    nome_ficheiro = f"Radar_Caixa_Monacco_{empresa.replace(' ', '_')}.html"
    return f'<a href="data:text/html;base64,{b64}" download="{nome_ficheiro}" style="display: inline-block; padding: 10px 20px; background-color: #C5A059; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-family: sans-serif; transition: 0.3s; margin-bottom: 20px;">🚨 Baixar Relatório de Radar (PDF)</a>'