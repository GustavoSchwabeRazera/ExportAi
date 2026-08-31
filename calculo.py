import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler

def ler_csvs():
    """
    Lê os arquivos reais fornecidos, aplicando tratamentos de encoding e separadores.
    """
    try:
        df_comex = pd.read_csv('exportabra2020-2026.csv', sep=',', dtype={'CO_NCM': str, 'CO_PAIS': str})
    except Exception:
        df_comex = pd.DataFrame()

    try:
        df_globais = pd.read_csv('dados_globais.csv', sep=';', dtype={'CO_PAIS': str})
    except Exception:
        df_globais = pd.DataFrame()

    try:
        df_bens = pd.read_csv('Importacao_Bens.csv', sep=',', dtype={'CO_NCM': str})
    except Exception:
        df_bens = pd.DataFrame()

    # Normalização dos NCMs na base (garante preenchimento com zeros à esquerda)
    if not df_comex.empty and 'CO_NCM' in df_comex.columns:
        df_comex['CO_NCM'] = df_comex['CO_NCM'].astype(str).str.zfill(8)
    
    if not df_bens.empty and 'CO_NCM' in df_bens.columns:
        df_bens['CO_NCM'] = df_bens['CO_NCM'].astype(str).str.zfill(8)

    return df_comex, df_globais, df_bens


def limpar_ncm(termo):
    """
    Remove pontos, traços, espaços ou qualquer caractere que não seja dígito.
    Ex: '3921.19.00' -> '39211900'
    """
    if not termo:
        return ""
    return re.sub(r"\D", "", str(termo))


def buscar_ncms_por_termo(termo_busca, df_comex):
    """
    Permite busca por NCM de 8 dígitos, SH4 (4 dígitos), SH6 (6 dígitos) ou Nome/Descrição.
    Aplica Regex para remover pontos e pontuações do input de busca.
    """
    if df_comex.empty or not termo_busca:
        return []

    termo_limpo = termo_busca.strip()
    
    # Aplica tratamento com Regex para obter apenas os números
    apenas_numeros = limpar_ncm(termo_limpo)
    
    # Se contiver números (código NCM completo ou parcial SH4/SH6)
    if apenas_numeros:
        ncms_unicos = df_comex['CO_NCM'].unique()
        correspondencias = [ncm for ncm in ncms_unicos if ncm.startswith(apenas_numeros)]
        if correspondencias:
            return correspondencias
    
    # Busca por descrição/nome do produto caso não seja um código ou não encontre via número
    if 'NO_NCM_POR' in df_comex.columns:
        filtro_nome = df_comex['NO_NCM_POR'].astype(str).str.contains(termo_limpo, case=False, na=False)
        return df_comex[filtro_nome]['CO_NCM'].unique().tolist()
    
    return []


def calcular_matriz(lista_ncms, df_comex, df_globais):
    """
    Calcula a pontuação (Score ExportAI) com base na lista de NCMs filtrados.
    """
    if df_comex.empty or not lista_ncms:
        return pd.DataFrame()

    # Filtra pelos NCMs identificados
    df_ncm = df_comex[df_comex['CO_NCM'].isin(lista_ncms)].copy()
    
    if df_ncm.empty:
        return pd.DataFrame()
        
    # Agrupa volume exportado por País
    if 'VL_FOB' in df_ncm.columns:
        df_ncm['VL_FOB'] = pd.to_numeric(df_ncm['VL_FOB'], errors='coerce').fillna(0)
        df_export = df_ncm.groupby('CO_PAIS', as_index=False)['VL_FOB'].sum()
        df_export = df_export.rename(columns={'VL_FOB': 'Valor_Exportado'})
    else:
        df_export = pd.DataFrame(columns=['CO_PAIS', 'Valor_Exportado'])

    # Cruzamento com dados globais
    df = pd.merge(df_export, df_globais, on='CO_PAIS', how='inner')
    
    if df.empty:
        return pd.DataFrame()

    # Garantia de colunas necessárias
    colunas_obrigatorias = ['Valor_Exportado', 'Valor_Importado', 'Crescimento_5_Anos', 'WB_Score', 'WB_Projecao', 'Preferencia_Percentual']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = 0.0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    scaler = MinMaxScaler()
    
    # Normalização
    df[['Export_Norm', 'Import_Norm', 'Cresc_Norm']] = scaler.fit_transform(
        df[['Valor_Exportado', 'Valor_Importado', 'Crescimento_5_Anos']]
    )
    
    # Score parcial de Mercado (Fase 1 - Peso máximo: 0.6)
    df['Score_Fase1'] = (df['Export_Norm'] * 0.2) + (df['Import_Norm'] * 0.2) + (df['Cresc_Norm'] * 0.2)
    
    top_10 = df.nlargest(10, 'Score_Fase1').copy()
    
    if len(top_10) > 0:
        top_10[['WB_Score_Norm', 'WB_Proj_Norm']] = scaler.fit_transform(
            top_10[['WB_Score', 'WB_Projecao']]
        )
    else:
        top_10['WB_Score_Norm'] = 0.0
        top_10['WB_Proj_Norm'] = 0.0

    # Função de pontuação por Acordos Comerciais
    def peso_acordo(pref):
        if pref >= 100: return 0.20
        elif pref >= 50: return 0.15
        elif pref > 0: return 0.10
        return 0.0
        
    top_10['Score_Acordo'] = top_10['Preferencia_Percentual'].apply(peso_acordo)
    
    # Score Final (0 a 100)
    top_10['Score_Final'] = (
        top_10['Score_Fase1'] + 
        (top_10['WB_Score_Norm'] * 0.1) + 
        (top_10['WB_Proj_Norm'] * 0.1) + 
        top_10['Score_Acordo']
    ) * 100 
    
    return top_10.sort_values(by='Score_Final', ascending=False).reset_index(drop=True)