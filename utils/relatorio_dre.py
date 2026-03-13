import base64
from datetime import datetime
from utils.formatters import formatar_moeda

def criar_download_relatorio_dre(empresa, df_dre, receitas, resultado, margem):
    """Gera o relatório HTML executivo da Demonstração do Resultado do Exercício."""
    
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    
    # Renderiza a tabela HTML
    tabela_dre = df_dre.to_html(index=False, classes='tabela-monacco', border=0)

    # Lógica do Diagnóstico Rápido
    if margem >= 15:
        cor_resultado = "#10B981" # Verde
        status = "SAUDÁVEL"
        diagnostico = "A operação gerou margens adequadas, indicando eficiência no controlo de custos e despesas operacionais."
    elif margem > 0:
        cor_resultado = "#F59E0B" # Amarelo
        status = "ALERTA (MARGEM BAIXA)"
        diagnostico = "A empresa obteve lucro, mas a margem está abaixo do ideal (15%). Recomenda-se revisão da estrutura de custos fixos ou precificação."
    else:
        cor_resultado = "#EF4444" # Vermelho
        status = "PREJUÍZO OPERACIONAL"
        diagnostico = "A operação consumiu caixa. As receitas não foram suficientes para cobrir as deduções, custos variáveis e despesas fixas."

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - DRE Gerencial</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;700&display=swap');
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1E293B; background-color: #F8FAFC; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-top: 8px solid #0F172A; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo-monacco {{ font-size: 28px; font-weight: 700; color: #0F172A; letter-spacing: 2px; }}
            .logo-monacco span {{ color: #C5A059; font-weight: 300; }}
            .info-cliente h1 {{ margin: 0; font-size: 22px; color: #334155; }}
            .info-cliente p {{ margin: 5px 0 0 0; color: #64748B; font-size: 14px; }}
            
            .resumo-box {{ background-color: #0F172A; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid {cor_resultado}; }}
            .resumo-box h2 {{ margin-top: 0; font-size: 18px; color: #C5A059; }}
            .resumo-box p {{ margin: 0; font-size: 14px; line-height: 1.6; color: #E2E8F0; }}
            
            .metricas-topo {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .kpi-card {{ flex: 1; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; background: #F8FAFC; text-align: center; }}
            .kpi-card h3 {{ margin: 0 0 5px 0; font-size: 13px; color: #64748B; text-transform: uppercase; }}
            .kpi-card .valor {{ font-size: 22px; font-weight: bold; color: #1E293B; }}
            
            h3.section-title {{ color: #0F172A; border-bottom: 2px solid #C5A059; padding-bottom: 5px; margin-top: 30px; font-size: 16px; }}
            
            .tabela-monacco {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
            .tabela-monacco th {{ background-color: #1E293B; color: white; padding: 12px; text-align: left !important; }}
            .tabela-monacco td {{ padding: 12px; border-bottom: 1px solid #E2E8F0; }}
            
            /* Formatação Específica para a DRE */
            .tabela-monacco td:nth-child(1) {{ width: 50%; font-weight: bold; color: #334155; }}
            .tabela-monacco td:nth-child(2) {{ width: 25%; text-align: right; }}
            .tabela-monacco td:nth-child(3) {{ width: 25%; text-align: right; color: #C5A059; font-weight: bold; }}
            
            /* Destacar linhas principais (1, 2, 3 e 4) e recuar as deduções */
            .tabela-monacco tr:nth-child(2) td:nth-child(1),
            .tabela-monacco tr:nth-child(4) td:nth-child(1),
            .tabela-monacco tr:nth-child(6) td:nth-child(1) {{ padding-left: 30px; font-weight: normal; color: #64748B; }}
            
            .tabela-monacco tr:last-child {{ background-color: #0F172A; }}
            .tabela-monacco tr:last-child td {{ color: white !important; font-size: 16px; font-weight: bold; }}
            
            .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 20px; }}
            @media print {{ body {{ background-color: white; padding: 0; }} .container {{ box-shadow: none; padding: 0; border: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-monacco">MONACCO <span>FINANCE</span></div>
                <div class="info-cliente">
                    <h1>DRE Gerencial Estruturada</h1>
                    <p>Unidade: <b>{empresa}</b> | Ref: {data_hoje}</p>
                </div>
            </div>
            
            <div class="metricas-topo">
                <div class="kpi-card">
                    <h3>Faturamento Bruto</h3>
                    <div class="valor">{formatar_moeda(receitas)}</div>
                </div>
                <div class="kpi-card" style="border-top: 3px solid {cor_resultado};">
                    <h3>Resultado Líquido (EBITDA)</h3>
                    <div class="valor" style="color: {cor_resultado};">{formatar_moeda(resultado)}</div>
                </div>
                <div class="kpi-card">
                    <h3>Margem Operacional</h3>
                    <div class="valor">{margem:.1f}%</div>
                </div>
            </div>
            
            <div class="resumo-box">
                <h2>📊 Síntese de Performance: {status}</h2>
                <p>{diagnostico} A demonstração abaixo evidencia a formação do seu resultado monetário, revelando o peso de cada rubrica sobre o faturamento total (Análise Vertical).</p>
            </div>
            
            <h3 class="section-title">Demonstrativo de Lucros e Perdas (P&L)</h3>
            {tabela_dre}
            
            <div class="footer">
                Documento gerado confidencialmente por Monacco Finance BPO.<br>
                Inteligência Analítica para Gestão de Resultados.
            </div>
        </div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    nome_ficheiro = f"DRE_Monacco_{empresa.replace(' ', '_')}.html"
    return f'<a href="data:text/html;base64,{b64}" download="{nome_ficheiro}" style="display: inline-block; padding: 10px 20px; background-color: #1E3A8A; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-family: sans-serif; transition: 0.3s; margin-bottom: 20px;">📑 Baixar DRE Gerencial (PDF)</a>'