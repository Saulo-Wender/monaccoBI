import base64
from datetime import datetime
from utils.formatters import formatar_moeda

def criar_download_relatorio_abc(empresa, qtd_cli_a, qtd_cli_total, perc_cli_a, df_clientes_a, qtd_forn_a, qtd_forn_total, perc_forn_a, df_forn_a):
    """Gera o relatório HTML exclusivo da Inteligência ABC com cabeçalhos alinhados à esquerda."""
    
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    
    tabela_clientes = df_clientes_a.to_html(index=False, classes='tabela-monacco', border=0) if not df_clientes_a.empty else "<p>Nenhum dado comercial suficiente.</p>"
    tabela_fornecedores = df_forn_a.to_html(index=False, classes='tabela-monacco', border=0) if not df_forn_a.empty else "<p>Nenhum dado de saída suficiente.</p>"

    if perc_cli_a <= 20:
        diag_comercial = f"<span style='color:#EF4444; font-weight:bold;'>ALTO RISCO:</span> Apenas {qtd_cli_a} cliente(s) ({perc_cli_a:.1f}% da base) geram 80% da receita. A perda de um cliente pode comprometer a operação."
    elif perc_cli_a <= 40:
        diag_comercial = f"<span style='color:#F59E0B; font-weight:bold;'>RISCO MODERADO:</span> {qtd_cli_a} cliente(s) ({perc_cli_a:.1f}% da base) sustentam 80% do negócio. Recomendada maior diversificação."
    else:
        diag_comercial = f"<span style='color:#10B981; font-weight:bold;'>CARTEIRA SAUDÁVEL:</span> {qtd_cli_a} cliente(s) ({perc_cli_a:.1f}% da base) formam o núcleo de 80%, demonstrando estabilidade."

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - Inteligência ABC</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;700&display=swap');
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1E293B; background-color: #F8FAFC; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-top: 8px solid #0F172A; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo-monacco {{ font-size: 28px; font-weight: 700; color: #0F172A; letter-spacing: 2px; }}
            .logo-monacco span {{ color: #C5A059; font-weight: 300; }}
            .info-cliente h1 {{ margin: 0; font-size: 22px; color: #334155; }}
            .info-cliente p {{ margin: 5px 0 0 0; color: #64748B; font-size: 14px; }}
            
            .resumo-box {{ background-color: #0F172A; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #1E3A8A; }}
            .resumo-box h2 {{ margin-top: 0; font-size: 18px; color: #60A5FA; }}
            .resumo-box p {{ margin: 0; font-size: 14px; line-height: 1.6; color: #E2E8F0; }}
            
            h3.section-title {{ color: #0F172A; border-bottom: 2px solid #C5A059; padding-bottom: 5px; margin-top: 35px; font-size: 16px; }}
            
            .tabela-monacco {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
            
            /* CORREÇÃO DO ALINHAMENTO: Força todos os títulos de coluna para a esquerda */
            .tabela-monacco th {{ background-color: #1E293B; color: white; padding: 12px; text-align: left !important; }}
            
            .tabela-monacco td {{ padding: 12px; border-bottom: 1px solid #E2E8F0; }}
            .tabela-monacco tr:nth-child(even) {{ background-color: #F8FAFC; }}
            
            /* Mantém os números formatados à direita nas linhas de dados, mas os títulos das colunas na esquerda */
            .tabela-monacco td:nth-child(2) {{ width: 25%; text-align: right; font-weight: bold; }}
            .tabela-monacco td:nth-child(3) {{ width: 15%; text-align: right; }}
            .tabela-monacco td:nth-child(4) {{ width: 15%; text-align: right; color: #C5A059; font-weight: bold; }}
            
            .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 20px; }}
            @media print {{ body {{ background-color: white; padding: 0; }} .container {{ box-shadow: none; padding: 0; border: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-monacco">MONACCO <span>FINANCE</span></div>
                <div class="info-cliente">
                    <h1>Risco de Concentração</h1>
                    <p>Unidade: <b>{empresa}</b> | Ref: {data_hoje}</p>
                </div>
            </div>
            
            <div class="resumo-box">
                <h2>🔍 Diagnóstico Estratégico de Carteira</h2>
                <p style="margin-bottom: 10px;">O Princípio de Pareto (Curva ABC) revela as dependências críticas do seu caixa.</p>
                <p><b>Receitas:</b> {diag_comercial}</p>
                <p style="margin-top: 10px;"><b>Despesas:</b> {qtd_forn_a} fornecedor(es) ou centros de custo ({perc_forn_a:.1f}% da base) absorvem 80% de todo o escoamento financeiro da operação.</p>
            </div>
            
            <h3 class="section-title">🟢 Clientes Classe A (Sustentam 80% do Faturamento)</h3>
            {tabela_clientes}
            
            <h3 class="section-title" style="margin-top: 40px;">🔴 Maiores Escoamentos (Consomem 80% do Caixa)</h3>
            {tabela_fornecedores}
            
            <div class="footer">
                Documento gerado confidencialmente por Monacco Finance BPO.<br>
                Inteligência Analítica para Gestão de Resultados.
            </div>
        </div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    nome_ficheiro = f"Analise_ABC_Monacco_{empresa.replace(' ', '_')}.html"
    return f'<a href="data:text/html;base64,{b64}" download="{nome_ficheiro}" style="display: inline-block; padding: 10px 20px; background-color: #1E3A8A; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-family: sans-serif; transition: 0.3s; margin-bottom: 20px;">🔍 Baixar Relatório de Risco ABC (PDF)</a>'