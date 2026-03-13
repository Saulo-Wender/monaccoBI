import base64
from datetime import datetime
from utils.formatters import formatar_moeda

def criar_download_relatorio_desempenho(empresa, pe, margem_seguranca, runway_meses, conversao, receitas, despesas_fixas, saldo_banco, recebiveis, ebitda, caixa_gerado):
    """Gera o relatório HTML exclusivo de Desempenho e Sobrevivência."""
    
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    
    # Diagnósticos Automáticos
    diag_pe = f"A empresa precisa faturar <b>{formatar_moeda(pe)}</b> para atingir o zero a zero. O faturamento atual foi de {formatar_moeda(receitas)}."
    
    cor_ms = "#10B981" if margem_seguranca > 20 else ("#F59E0B" if margem_seguranca > 0 else "#EF4444")
    diag_ms = f"A receita pode cair até <b>{margem_seguranca:.1f}%</b> antes da operação começar a dar prejuízo." if margem_seguranca > 0 else "A operação está a operar no vermelho. Não há margem de segurança."
    
    cor_runway = "#10B981" if runway_meses >= 3 else ("#F59E0B" if runway_meses >= 1 else "#EF4444")
    diag_runway = f"Com o saldo atual e contas a receber, a empresa sobrevive <b>{runway_meses:.1f} meses</b> se o faturamento for a zero."
    
    cor_conv = "#10B981" if conversao >= 80 else ("#F59E0B" if conversao >= 40 else "#EF4444")
    if ebitda <= 0:
        diag_conv = "A operação não gerou lucro (EBITDA negativo), impossibilitando a conversão em caixa."
    else:
        diag_conv = f"De cada R$ 100 de lucro (EBITDA), a empresa conseguiu transformar <b>R$ {conversao:.1f}</b> em saldo de caixa real."

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - Desempenho</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;700&display=swap');
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1E293B; background-color: #F8FAFC; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-top: 8px solid #0F172A; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo-monacco {{ font-size: 28px; font-weight: 700; color: #0F172A; letter-spacing: 2px; }}
            .logo-monacco span {{ color: #C5A059; font-weight: 300; }}
            .info-cliente h1 {{ margin: 0; font-size: 22px; color: #334155; }}
            .info-cliente p {{ margin: 5px 0 0 0; color: #64748B; font-size: 14px; }}
            
            .resumo-box {{ background-color: #0F172A; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #38BDF8; }}
            .resumo-box h2 {{ margin-top: 0; font-size: 18px; color: #38BDF8; }}
            .resumo-box p {{ margin: 0; font-size: 14px; line-height: 1.6; color: #E2E8F0; }}
            
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
            .card {{ padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; background: #F8FAFC; border-top: 4px solid #1E293B; }}
            .card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #64748B; text-transform: uppercase; }}
            .card .valor {{ font-size: 26px; font-weight: bold; margin-bottom: 10px; color: #1E293B; }}
            .card p {{ font-size: 13px; color: #475569; margin: 0; line-height: 1.4; }}
            
            .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 20px; }}
            @media print {{ body {{ background-color: white; padding: 0; }} .container {{ box-shadow: none; padding: 0; border: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-monacco">MONACCO <span>FINANCE</span></div>
                <div class="info-cliente">
                    <h1>Desempenho e Sobrevivência</h1>
                    <p>Unidade: <b>{empresa}</b> | Ref: {data_hoje}</p>
                </div>
            </div>
            
            <div class="resumo-box">
                <h2>🔍 Diagnóstico de Eficiência e Risco</h2>
                <p>Este relatório apresenta os 4 indicadores vitais de sobrevivência do negócio. A meta é garantir que a operação tem fôlego financeiro (runway) para suportar imprevistos e que o lucro contábil se transforma em dinheiro real na conta bancária.</p>
            </div>
            
            <div class="grid">
                <div class="card" style="border-top-color: #1E3A8A;">
                    <h3>Ponto de Equilíbrio (Break-Even)</h3>
                    <div class="valor">{formatar_moeda(pe)}</div>
                    <p>{diag_pe}</p>
                </div>
                
                <div class="card" style="border-top-color: {cor_ms};">
                    <h3>Margem de Segurança</h3>
                    <div class="valor" style="color: {cor_ms};">{margem_seguranca:.1f}%</div>
                    <p>{diag_ms}</p>
                </div>
                
                <div class="card" style="border-top-color: {cor_runway};">
                    <h3>Índice de Sobrevivência (Runway)</h3>
                    <div class="valor" style="color: {cor_runway};">{runway_meses:.1f} <span style="font-size: 16px;">meses</span></div>
                    <p>{diag_runway}</p>
                </div>
                
                <div class="card" style="border-top-color: {cor_conv};">
                    <h3>Conversão de Lucro em Caixa</h3>
                    <div class="valor" style="color: {cor_conv};">{conversao:.1f}%</div>
                    <p>{diag_conv}</p>
                </div>
            </div>
            
            <div class="footer">
                Documento gerado confidencialmente por Monacco Finance BPO.<br>
                Inteligência Analítica para Gestão de Resultados.
            </div>
        </div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    nome_ficheiro = f"Desempenho_Monacco_{empresa.replace(' ', '_')}.html"
    return f'<a href="data:text/html;base64,{b64}" download="{nome_ficheiro}" style="display: inline-block; padding: 10px 20px; background-color: #38BDF8; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-family: sans-serif; transition: 0.3s; margin-bottom: 20px;">🚀 Baixar Relatório de Desempenho (PDF)</a>'