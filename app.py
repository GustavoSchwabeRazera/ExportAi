import streamlit as st
import pandas as pd
from calculo import ler_csvs, calcular_matriz

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="ExportAI", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .main-title { font-size: 48px; font-weight: 800; color: #111827; text-align: center; margin-top: 30px; margin-bottom: 10px; }
    .subtitle { font-size: 20px; color: #6b7280; text-align: center; margin-bottom: 40px; }
    .section-title { font-size: 24px; font-weight: 700; color: #111827; margin-bottom: 10px; }
    .result-title { font-size: 30px; font-weight: 800; color: #111827; margin-bottom: 20px; }
    .footer { text-align: center; color: #9ca3af; margin-top: 60px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CACHE DE DADOS (STREAMLIT)
# ==========================================
@st.cache_data
def carregar_dados():
    try:
        return ler_csvs()
    except FileNotFoundError as e:
        st.error(f"Arquivo não encontrado: {e.filename}")
        return None, None

# ==========================================
# CABEÇALHO E INPUTS
# ==========================================
st.markdown('<div class="main-title">ExportAI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Encontre os mercados mais promissores para exportar seus produtos.</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="section-title">Comece sua análise</div>', unsafe_allow_html=True)
    ncm = st.text_input("Informe o código NCM", placeholder="Ex: 39211900")
    exporta = st.radio("Sua empresa já exporta?", ["Sim", "Não"], horizontal=True)
    if exporta == "Sim":
        st.multiselect("Países atuais", ["Argentina", "Chile", "Estados Unidos", "Alemanha", "México"])
    analisar = st.button("🚀 Executar análise", use_container_width=True)

# ==========================================
# EXECUÇÃO E RESULTADOS
# ==========================================
if analisar:
    if not ncm:
        st.warning("⚠️ Digite um NCM para realizar a análise.")
    else:
        df_comex, df_globais = carregar_dados()
        
        if df_comex is not None and df_globais is not None:
            with st.spinner("Analisando mercados e calculando matriz..."):
                df_resultado = calcular_matriz(ncm, df_comex, df_globais)
            
            if df_resultado.empty:
                st.warning(f"Nenhum dado cruzado encontrado para o NCM **{ncm}**. Verifique os arquivos.")
            else:
                st.success(f"Análise concluída para o NCM **{ncm}**.")
                st.divider()
                
                # Exibição dos cards
                st.markdown('<div class="result-title">🌎 Mercados mais promissores</div>', unsafe_allow_html=True)
                for i, row in df_resultado.iterrows():
                    c1, c2, c3, c4 = st.columns([0.5, 2, 1, 1.5])
                    with c1: st.markdown(f"### {i + 1}º")
                    with c2: st.markdown(f"### {row['Nome_Pais']}")
                    with c3: st.metric("Score ExportAI", f"{row['Score_Final']:.1f}")
                    with c4: st.metric("Crescimento (5 anos)", f"{row['Crescimento_5_Anos']:.1f}%")
                    st.divider()
                
                # Gráfico
                st.markdown("### Comparação do Score Final")
                chart_data = df_resultado.set_index("Nome_Pais")[["Score_Final"]]
                st.bar_chart(chart_data)
                
                # ==========================================
                # MEMÓRIA DE CÁLCULO E TABELA DE DADOS
                # ==========================================
                st.markdown("---")
                st.markdown("### 🔍 Metodologia e Dados")
                
                with st.expander("Como a pontuação é calculada?"):
                    st.markdown("""
                    Para criar uma pontuação justa, todos os valores são primeiramente **normalizados em uma escala de 0 a 1** (onde o melhor país recebe nota 1 e os demais notas proporcionais). Após isso, aplicamos os seguintes pesos:
                    
                    **Fase 1: Histórico de Mercado (Peso máximo: 0.6 ou 60%)**
                    * 20%: Volume financeiro já exportado pelo Brasil (FOB).
                    * 20%: Volume de importação global do país alvo.
                    * 20%: Crescimento da importação do país alvo nos últimos 5 anos.
                    
                    **Fase 2: Macroeconomia e Tarifas (Peso máximo: 0.4 ou 40%)**
                    * 10%: Score do Banco Mundial (*Ease of Doing Business* / Risco).
                    * 10%: Projeção de Crescimento do PIB do país.
                    * Até 20%: Acordos Comerciais com o Brasil (100% de isenção = +0.20 | 50% a 99% = +0.15 | < 50% = +0.10).
                    
                    A soma final é multiplicada por 100 para criar o *Score ExportAI* (0 a 100).
                    """)
                
                with st.expander("Ver Tabela de Dados da Matriz"):
                    st.write("Abaixo estão os dados reais utilizados e os cálculos intermediários gerados pelo sistema após o agrupamento:")
                    colunas_exibicao = [
                        'Nome_Pais', 'Valor_Exportado', 'Valor_Importado', 'Crescimento_5_Anos',
                        'WB_Score', 'WB_Projecao', 'Preferencia_Percentual', 'Score_Fase1', 'Score_Final'
                    ]
                    st.dataframe(df_resultado[colunas_exibicao].style.format({
                        'Valor_Exportado': '${:,.0f}',
                        'Valor_Importado': '${:,.0f}',
                        'Score_Fase1': '{:.3f}',
                        'Score_Final': '{:.1f}'
                    }))
                
                with st.expander("Ver Registros Brutos (Aparições do NCM)"):
                    st.write(f"Abaixo estão todas as linhas onde o NCM **{ncm}** apareceu originalmente na base de exportação do Brasil:")
                    
                    # Filtra a base original apenas com o NCM pesquisado
                    df_ncm_bruto = df_comex[df_comex['CO_NCM'] == int(ncm)]
                    
                    # Formata a visualização dos valores em Dólar e Quilos para ficar amigável
                    st.dataframe(df_ncm_bruto.style.format({
                        'VL_FOB': '${:,.0f}',
                        'KG_LIQUIDO': '{:,.0f} kg'
                    }))

st.markdown('<div class="footer">ExportAI • Inteligência para novos mercados</div>', unsafe_allow_html=True)