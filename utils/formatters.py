def formatar_moeda(valor: float) -> str:
    """Formata um valor numérico para o padrão monetário brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")