import pandas as pd

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Prepara o DataFrame para ser baixado como CSV pelo usuário."""
    return df.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')