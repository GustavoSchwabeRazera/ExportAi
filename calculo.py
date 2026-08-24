import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def ler_csvs():
    """Lê os arquivos reais fornecidos pelo usuário."""
    # Lê a base do Siscomex separada por VÍRGULA (,)
    df_comex = pd.read_csv('exportacoes_2020.csv', sep=',') 
    
    # Lê a base global separada por PONTO-E-VÍRGULA (;)
    df_globais = pd.read_csv('dados_globais.csv', sep=';')
    
    return df_comex, df_globais

def calcular_matriz(ncm, df_comex, df_globais):
    """Executa o cruzamento e cálculo da pontuação."""
    df_ncm = df_comex[df_comex['CO_NCM'] == int(ncm)]
    
    if df_ncm.empty:
        return pd.DataFrame()
        
    df_export = df_ncm.groupby('CO_PAIS', as_index=False)['VL_FOB'].sum()
    df_export = df_export.rename(columns={'VL_FOB': 'Valor_Exportado'})
    
    df = pd.merge(df_export, df_globais, on='CO_PAIS', how='inner')
    
    if df.empty:
        return pd.DataFrame()

    scaler = MinMaxScaler()
    df[['Export_Norm', 'Import_Norm', 'Cresc_Norm']] = scaler.fit_transform(
        df[['Valor_Exportado', 'Valor_Importado', 'Crescimento_5_Anos']]
    )
    
    # Score parcial de Mercado (Peso máximo: 0.6)
    df['Score_Fase1'] = (df['Export_Norm'] * 0.2) + (df['Import_Norm'] * 0.2) + (df['Cresc_Norm'] * 0.2)
    
    top_10 = df.nlargest(10, 'Score_Fase1').copy()
    
    top_10[['WB_Score_Norm', 'WB_Proj_Norm']] = scaler.fit_transform(
        top_10[['WB_Score', 'WB_Projecao']]
    )
    
    # Regra dos Acordos Comerciais
    def peso_acordo(pref):
        if pref >= 100: return 0.20
        elif pref >= 50: return 0.15
        elif pref > 0: return 0.10
        return 0.0
        
    top_10['Score_Acordo'] = top_10['Preferencia_Percentual'].apply(peso_acordo)
    
    # Score Final (Peso máximo: 1.0 -> convertido para 100)
    top_10['Score_Final'] = (
        top_10['Score_Fase1'] + 
        (top_10['WB_Score_Norm'] * 0.1) + 
        (top_10['WB_Proj_Norm'] * 0.1) + 
        top_10['Score_Acordo']
    ) * 100 
    
    return top_10.sort_values(by='Score_Final', ascending=False).reset_index(drop=True)
