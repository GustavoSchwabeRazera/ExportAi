import streamlit as st
import pandas as pd
import requests

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="ExportAI",
   
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS
# ==========================================

st.markdown("""
<style>

    .stApp {
        background-color: #f8fafc;
    }

    .main-title {
        font-size: 48px;
        font-weight: 800;
        color: #111827;
        text-align: center;
        margin-top: 30px;
        margin-bottom: 10px;
    }

    .subtitle {
        font-size: 20px;
        color: #6b7280;
        text-align: center;
        margin-bottom: 40px;
    }

    .card {
        background-color: white;
        padding: 30px;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 10px;
    }

    .result-title {
        font-size: 30px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 20px;
    }

    .country-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
    }

    .country-name {
        font-size: 20px;
        font-weight: 700;
    }

    .score {
        font-size: 26px;
        font-weight: 800;
    }

    .footer {
        text-align: center;
        color: #9ca3af;
        margin-top: 60px;
    }

</style>
""", unsafe_allow_html=True)

# ==========================================
# CABEÇALHO
# ==========================================
#st.image('.\logo.png',width="stretch",)
st.markdown(
    '<div class="main-title">ExportAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Encontre os mercados mais promissores para exportar seus produtos.'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# ENTRADA DO USUÁRIO
# ==========================================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    

    st.markdown(
        '<div class="section-title">Comece sua análise</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Informe o código NCM do produto que sua empresa deseja exportar."
    )

    ncm = st.text_input(
        "NCM",
        placeholder="Ex: 62034200"
    )

    st.write("")

    exporta = st.radio(
        "Sua empresa já exporta?",
        ["Sim", "Não"],
        horizontal=True
    )

    paises_exportacao = []

    if exporta == "Sim":

        st.write("Para quais países sua empresa já exporta?")

        paises_exportacao = st.multiselect(
            "Países atuais",
            [
                "Argentina",
                "Chile",
                "Estados Unidos",
                "Alemanha",
                "México",
                "Canadá",
                "Espanha",
                "França"
            ]
        )

    st.write("")

    analisar = st.button(
        "🚀 Executar análise",
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# RESULTADO
# ==========================================

if analisar:

    if not ncm:

        st.warning("Digite um NCM para realizar a análise.")

    else:

        st.success(
            f"Análise iniciada para o NCM **{ncm}**."
        )

        st.divider()

        st.markdown(
            '<div class="result-title">'
            '🌎 Mercados mais promissores'
            '</div>',
            unsafe_allow_html=True
        )

        # --------------------------------------
        # DADOS TEMPORÁRIOS
        # --------------------------------------
        # Depois vamos substituir isso pelos
        # dados reais do banco/API.

        resultados = [
            {
                "pais": "🇩🇪 Alemanha",
                "score": 87.4,
                "crescimento": 12.2,
                "importacoes": 450000000
            },
            {
                "pais": "🇨🇦 Canadá",
                "score": 83.1,
                "crescimento": 9.7,
                "importacoes": 320000000
            },
            {
                "pais": "🇲🇽 México",
                "score": 81.9,
                "crescimento": 8.4,
                "importacoes": 280000000
            },
            {
                "pais": "🇪🇸 Espanha",
                "score": 78.3,
                "crescimento": 7.1,
                "importacoes": 230000000
            },
            {
                "pais": "🇨🇱 Chile",
                "score": 76.8,
                "crescimento": 6.8,
                "importacoes": 190000000
            }
        ]

        # --------------------------------------
        # CARDS DOS PAÍSES
        # --------------------------------------

        for i, resultado in enumerate(resultados):

            col1, col2, col3, col4 = st.columns(
                [0.5, 2, 1, 1.5]
            )

            with col1:
                st.markdown(
                    f"### {i + 1}º"
                )

            with col2:
                st.markdown(
                    f"### {resultado['pais']}"
                )

            with col3:
                st.metric(
                    "Score",
                    resultado["score"]
                )

            with col4:
                st.metric(
                    "Crescimento",
                    f"{resultado['crescimento']}%"
                )

            st.divider()

        # --------------------------------------
        # GRÁFICO
        # --------------------------------------

        st.markdown("### Comparação dos mercados")

        df = pd.DataFrame(resultados)

        chart_data = df.set_index("pais")[["score"]]

        st.bar_chart(chart_data)

# ==========================================
# RODAPÉ
# ==========================================

st.markdown(
    '<div class="footer">'
    'ExportAI • Inteligência para novos mercados'
    '</div>',
    unsafe_allow_html=True
)