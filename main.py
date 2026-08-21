import pandas as pd
import requests
import dados as dados




def calcular_ranking(df):
    df['Score'] = ''
    return df.sort_values(by='Score', ascending=False).reset_index(drop=True)
    pass

def gerar_resumo(ncm, pais_vencedor):
    pass