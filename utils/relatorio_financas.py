import base64
from datetime import datetime
from utils.formatters import formatar_moeda

def criar_download_relatorio_financas(empresa, receitas, impostos, custos, fixas, ebitda, qtd_vendas, ticket_medio):
    """Gera o relatório HTML de Finanças Corporativas e Eficiência com o Funil."""
    
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    
    if receitas > 0:
        p_imp = (impostos / receitas) * 100
        p_cus = (custos / receitas) * 100
        p_fix = (fixas / receitas) * 100
        p_lucro = (ebitda / receitas) * 100
    else:
        p_imp = p_cus = p_fix = p_lucro = 0

    v_apos_imp = receitas - impostos
    v_apos_cus = v_apos_imp - custos

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - Eficiência Corporativa</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Helvetica+Neue:wght@300;400;700&display=swap');
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1E293B; background-color: #F8FAFC; margin: 0; padding: 40px; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 40px; border-top: 8px solid #0F172A; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo-monacco {{ font-size: 28px; font-weight: 700; color: #0F172A; letter-spacing: 2px; }}
            .logo-monacco span {{ color: #C5A059; font-weight: 300; }}
            .info-cliente h1 {{ margin: 0; font-size: 22px; color: #334155; }}
            .info-cliente p {{ margin: 5px 0 0 0; color: #64748B; font-size: 14px; }}
            
            .resumo-box {{ background-color: #0F172A; color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; border-left: 5px solid #F59E0B; }}
            .resumo-box h2 {{ margin-top: 0; font-size: 18px; color: #FBBF24; }}
            .resumo-box p {{ margin: 0; font-size: 14px; line-height: 1.6; color: #E2E8F0; }}
            
            .flex-container {{ display: flex; gap: 30px; margin-bottom: 40px; }}
            
            /* Coluna da Decomposição */
            .col-half {{ flex: 1; }}
            .bar-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }}
            .bar-label {{ width: 140px; font-weight: bold; color: #475569; font-size: 12px; }}
            .bar-container {{ flex: 1; background-color: #E2E8F0; border-radius: 20px; height: 20px; overflow: hidden; position: relative; }}
            .bar-fill {{ height: 100%; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: bold; font-size: 11px; }}
            .bar-value {{ width: 80px; text-align: right; font-weight: bold; color: #1E293B; font-size: 12px; }}
            
            /* Coluna do Funil */
            .funnel-container {{ display: flex; flex-direction: column; align-items: center; gap: 8px; margin-top: 10px; }}
            .funnel-step {{ padding: 10px; color: white; text-align: center; border-radius: 4px; font-weight: bold; font-size: 13px; display: flex; justify-content: space-between; align-items: center; box-sizing: border-box; }}
            .f-title {{ font-size: 11px; font-weight: normal; opacity: 0.9; text-transform: uppercase; }}
            
            h3.section-title {{ color: #0F172A; border-bottom: 2px solid #C5A059; padding-bottom: 5px; margin-bottom: 20px; font-size: 16px; }}
            
            .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 20px; }}
            @media print {{ body {{ background-color: white; padding: 0; }} .container {{ box-shadow: none; padding: 0; border: none; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-monacco">MONACCO <span>FINANCE</span></div>
                <div class="info-cliente">
                    <h1>Eficiência Corporativa</h1>
                    <p>Unidade: <b>{empresa}</b> | Ref: {data_hoje}</p>
                </div>
            </div>
            
            <div class="resumo-box">
                <h2>📊 Dinâmica de Geração de Valor</h2>
                <p>Esta análise demonstra como o faturamento é consumido pela estrutura do negócio (Erosão do Faturamento) e como o dinheiro é distribuído (A cada R$ 100) até se transformar em Lucro.</p>
            </div>
            
            <div class="flex-container">
                <div class="col-half">
                    <h3 class="section-title">Funil de Absorção de Caixa</h3>
                    <div class="funnel-container">
                        <div class="funnel-step" style="width: 100%; background-color: #38BDF8;">
                            <span class="f-title">Faturamento</span> <span>{formatar_moeda(receitas)} (100%)</span>
                        </div>
                        <div class="funnel-step" style="width: 85%; background-color: #F59E0B;">
                            <span class="f-title">Após Impostos</span> <span>{formatar_moeda(v_apos_imp)} ({(v_apos_imp/receitas*100) if receitas > 0 else 0:.1f}%)</span>
                        </div>
                        <div class="funnel-step" style="width: 70%; background-color: #8B5CF6;">
                            <span class="f-title">Margem Contrib.</span> <span>{formatar_moeda(v_apos_cus)} ({(v_apos_cus/receitas*100) if receitas > 0 else 0:.1f}%)</span>
                        </div>
                        <div class="funnel-step" style="width: 55%; background-color: {'#10B981' if ebitda > 0 else '#EF4444'};">
                            <span class="f-title">Lucro Líquido</span> <span>{formatar_moeda(ebitda)} ({p_lucro:.1f}%)</span>
                        </div>
                    </div>
                </div>
                
                <div class="col-half">
                    <h3 class="section-title">Decomposição (R$ 100)</h3>
                    <div class="bar-row">
                        <div class="bar-label">Impostos</div>
                        <div class="bar-container"><div class="bar-fill" style="width: {p_imp}%; background-color: #F59E0B;"></div></div>
                        <div class="bar-value">R$ {p_imp:.2f}</div>
                    </div>
                    <div class="bar-row">
                        <div class="bar-label">Custos Var.</div>
                        <div class="bar-container"><div class="bar-fill" style="width: {p_cus}%; background-color: #EF4444;"></div></div>
                        <div class="bar-value">R$ {p_cus:.2f}</div>
                    </div>
                    <div class="bar-row">
                        <div class="bar-label">Desp. Fixas</div>
                        <div class="bar-container"><div class="bar-fill" style="width: {p_fix}%; background-color: #64748B;"></div></div>
                        <div class="bar-value">R$ {p_fix:.2f}</div>
                    </div>
                    <div class="bar-row">
                        <div class="bar-label">Lucro (EBITDA)</div>
                        <div class="bar-container"><div class="bar-fill" style="width: {p_lucro if p_lucro > 0 else 0}%; background-color: {'#10B981' if p_lucro > 0 else '#EF4444'};"></div></div>
                        <div class="bar-value" style="color: {'#10B981' if p_lucro > 0 else '#EF4444'};">R$ {p_lucro:.2f}</div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                Documento gerado confidencialmente por Monacco Finance BPO.<br>
                Uso Exclusivo Interno e de Consultoria.
            </div>
        </div>
    </body>
    </html>
    """
    
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    nome_ficheiro = f"Financas_Corporativas_{empresa.replace(' ', '_')}.html"
    return f'<a href="data:text/html;base64,{b64}" download="{nome_ficheiro}" style="display: inline-block; padding: 10px 20px; background-color: #0F172A; color: #C5A059; text-decoration: none; border-radius: 5px; font-weight: bold; border: 1px solid #C5A059; transition: 0.3s; margin-bottom: 20px;">📊 Baixar Relatório de Eficiência (PDF)</a>'