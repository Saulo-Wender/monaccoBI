import base64
from datetime import datetime
from utils.formatters import formatar_moeda

def criar_download_relatorio_raiox(empresa, df_cc, melhor_cc, pior_cc):
    """Gera o relatório HTML de Margens por Centro de Custo/Unidade."""
    
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    
    tabela_cc = df_cc.to_html(index=False, classes='tabela-monacco', border=0) if not df_cc.empty else "<p>Nenhum dado disponível.</p>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - Raio-X de Margens</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;700&display=swap');
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1E293B; background-color: #F8FAFC; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-top: 8px solid #0F172A; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo-monacco {{ font-size: 28px; font-weight: 700; color: #0F172A; letter-spacing: 2px; }}
            .logo-monacco span {{ color: #C5A059; font-weight: 300; }}
            .info-cliente h1 {{ margin: 0; font-size: 22px; color: #334155; }}
            .info-cliente p {{ margin: 5px 0 0 0; color: #64748B; font-size: 14px; }}
            
            .resumo-box {{ background-color: #0F172A; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #8B5CF6; }}
            .resumo-box h2 {{ margin-top: 0; font-size: 18px; color: #A78BFA; }}
            .resumo-box p {{ margin: 0; font-size: 14px; line-height: 1.6; color: #E2E8F0; }}
            
            .grid {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ flex: 1; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; background: #F8FAFC; }}
            .card h3 {{ margin: 0 0 10px 0; font-size: 13px; color: #64748B; text-transform: uppercase; }}
            .card .nome {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #1E293B; }}
            
            .tabela-monacco {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
            .tabela-monacco th {{ background-color: #1E293B; color: white; padding: 12px; text-align: left; }}
            .tabela-monacco td {{ padding: 12px; border-bottom: 1px solid #E2E8F0; }}
            .tabela-monacco tr:nth-child(even) {{ background-color: #F8FAFC; }}
            .tabela-monacco td:nth-child(2), .tabela-monacco td:nth-child(3), .tabela-monacco td:nth-child(4) {{ text-align: right; }}
            .tabela-monacco td:nth-child(5) {{ text-align: right; font-weight: bold; }}
            
            .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 20px; }}
            @media print {{ body {{ background-color: white; padding: 0; }} .container {{ box-shadow: none; padding: 0; border: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-monacco">MONACCO <span>FINANCE</span></div>
                <div class="info-cliente">
                    <h1>Raio-X de Margens (Unidades de Negócio)</h1>
                    <p>Unidade: <b>{empresa}</b> | Ref: {data_hoje}</p>
                </div>
            </div>
            
            <div class="resumo-box">
                <h2>🔍 Auditoria de Rentabilidade Isolada</h2>
                <p>Análise de Unit Economics: Identificação de quais Centros de Custo (Unidades, Projetos ou Serviços) estão a subsidiar a operação e quais estão a atuar como drenos de capital.</p>
            </div>
            
            <div class="grid">
                <div class="card" style="border-top: 4px solid #10B981;">
                    <h3>🌟 Motor de Lucro (Vaca Leiteira)</h3>
                    <div class="nome">{melhor_cc['Nome']}</div>
                    <div style="color: #10B981; font-weight: bold; font-size: 18px;">Margem: {melhor_cc['Margem']}</div>
                    <div style="font-size: 12px; color: #64748B; margin-top: 5px;">Geração: {melhor_cc['Resultado']}</div>
                </div>
                
                <div class="card" style="border-top: 4px solid #EF4444;">
                    <h3>⚠️ Ralo de Capital (Ponto de Atenção)</h3>
                    <div class="nome">{pior_cc['Nome']}</div>
                    <div style="color: #EF4444; font-weight: bold; font-size: 18px;">Margem: {pior_cc['Margem']}</div>
                    <div style="font-size: 12px; color: #64748B; margin-top: 5px;">Resultado: {pior_cc['Resultado']}</div>
                </div>
            </div>
            
            <h3 style="color: #0F172A; border-bottom: 2px solid #C5A059; padding-bottom: 5px; margin-top: 30px;">Tabela Consolidada por Centro de Custo</h3>
            {tabela_cc}
            
            <div class="footer">
                Documento gerado confidencialmente por Monacco Finance BPO.<br>
                Uso Exclusivo Interno e de Consultoria.
            </div>
        </div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    nome_ficheiro = f"RaioX_Centros_Custo_{empresa.replace(' ', '_')}.html"
    return f'<a href="data:text/html;base64,{b64}" download="{nome_ficheiro}" style="display: inline-block; padding: 10px 20px; background-color: #8B5CF6; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-family: sans-serif; transition: 0.3s; margin-bottom: 20px;">🔬 Baixar Dossiê de Unidades (PDF)</a>'