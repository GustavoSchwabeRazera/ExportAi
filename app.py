import streamlit as st
import pandas as pd
import re
import base64
from pathlib import Path
from calculo import ler_csvs, buscar_ncms_por_termo, calcular_matriz

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="ExportAI — Inteligência em Comércio Exterior",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=".logo.png"
)

# ==========================================
# GESTÃO DE SESSÃO / ESTADO
# ==========================================
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False

if "pagina_login" not in st.session_state:
    st.session_state.pagina_login = "login"

# ==========================================
# ESTILIZACÃO CUSTOMIZADA (CSS)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .brand-header { display: flex; justify-content: center; align-items: center; margin-bottom: 20px; }
    .main-logo { width: 180px; height: auto; }
    .login-card {
        background: white; border: 1px solid #dfe5ea; border-radius: 12px;
        padding: 30px; box-shadow: 0 4px 18px rgba(10, 37, 64, 0.08); max-width: 500px; margin: 0 auto;
    }
    .hero-title { color: #0a2540; font-size: 28px; font-weight: 800; text-align: center; }
    .hero-subtitle { color: #5f6b76; font-size: 15px; text-align: center; margin-bottom: 25px; }
    .section-head { font-size: 20px; font-weight: 700; color: #111827; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# Helper para carregar imagens em base64
def get_base64_logo():
    for p in ["logo.png", "logo(1).png", "logo(3).png"]:
        path = Path(__file__).with_name(p)
        if path.exists():
            return base64.b64encode(path.read_bytes()).decode("utf-8")
    return None

logo_b64 = get_base64_logo()

# ==========================================
# TELA 1: LOGIN E CADASTRO
# ==========================================
if not st.session_state.usuario_logado:
    if logo_b64:
        st.markdown(f'<div class="brand-header"><img class="main-logo" src="data:image/png;base64,{logo_b64}"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="hero-title">Acesse o ExportAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Inteligência para expansão de mercados internacionais</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    if st.session_state.pagina_login == "login":
        st.subheader("Entrar")
        email = st.text_input("E-mail corporativo", key="log_email")
        senha = st.text_input("Senha", type="password", key="log_senha")
        
        if st.button("Entrar", type="primary", use_container_width=True):
            if email and senha:
                st.session_state.usuario_logado = True
                st.rerun()
            else:
                st.warning("Preencha todos os campos para continuar.")
                
        if st.button("Criar nova conta empresarial", use_container_width=True):
            st.session_state.pagina_login = "cadastro"
            st.rerun()
            
    else:
        st.subheader("Cadastro Empresarial")
        empresa = st.text_input("Nome da empresa *")
        cnpj = st.text_input("CNPJ *")
        email_cad = st.text_input("E-mail corporativo *")
        senha_cad = st.text_input("Senha *", type="password")
        
        if st.button("Finalizar Cadastro", type="primary", use_container_width=True):
            if empresa and cnpj and email_cad and senha_cad:
                st.success("Conta criada com sucesso!")
                st.session_state.pagina_login = "login"
                st.rerun()
            else:
                st.error("Preencha os campos obrigatórios.")
                
        if st.button("Já tenho uma conta", use_container_width=True):
            st.session_state.pagina_login = "login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# TELA 2: APLICAÇÃO PRINCIPAL (PÓS-LOGIN)
# ==========================================

# Carregamento de dados em Cache
@st.cache_data
def carregar_dados_sistema():
    return ler_csvs()

df_comex, df_globais, df_bens = carregar_dados_sistema()

# Barra Lateral
with st.sidebar:
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width: 100%; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.title("ExportAI")
    
    modulo = st.radio(
        "Selecione o Módulo",
        ["Módulo Básico (Mercados)", "Módulo Diagnóstico (Checklist)", "Módulo Vendas (Prospecção)"]
    )
    
    st.divider()
    if st.button("Sair / Logout", use_container_width=True):
        st.session_state.usuario_logado = False
        st.rerun()

# ------------------------------------------
# MÓDULO 1: BÁSICO (RADIOGRAFIA DE MERCADO)
# ------------------------------------------
if modulo == "Módulo Básico (Mercados)":
    st.title("🌎 Módulo Básico — Radiografia de Mercado")
    st.caption("Identifique os mercados globais mais promissores para seu produto através do NCM, SH4/SH6 ou nome.")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        termo_busca = st.text_input(
            "Pesquise por NCM (8 dígitos), SH4/SH6 (4 ou 6 dígitos) ou Nome do Produto:",
            placeholder="Ex: 39211900, 3921 ou Plástico"
        )
    
    with col2:
        exporta_ja = st.radio("Sua empresa já exporta?", ["Não", "Sim"], horizontal=True)

    if termo_busca:
        ncms_encontrados = buscar_ncms_por_termo(termo_busca, df_comex)
        
        if not ncms_encontrados:
            st.warning(f"Nenhum registro encontrado para a busca '{termo_busca}'.")
        else:
            st.info(f"Foram identificados **{len(ncms_encontrados)}** NCM(s) correspondentes.")
            
            if st.button("🚀 Executar Análise de Mercado", type="primary"):
                with st.spinner("Processando dados consolidados e matriz tarifária..."):
                    df_res = calcular_matriz(ncms_encontrados, df_comex, df_globais)
                
                if df_res.empty:
                    st.warning("Não há dados de exportação cruzados suficientes para a seleção.")
                else:
                    st.subheader("Top Mercados Indicados")
                    for idx, row in df_res.iterrows():
                        c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
                        c1.markdown(f"### #{idx+1}")
                        c2.markdown(f"**{row.get('Nome_Pais', 'País')}**")
                        c3.metric("Score ExportAI", f"{row.get('Score_Final', 0):.1f}/100")
                        c4.metric("Crescimento (5a)", f"{row.get('Crescimento_5_Anos', 0):.1f}%")
                        st.divider()

                    st.subheader("Comparativo Visual de Desempenho")
                    chart_data = df_res.set_index("Nome_Pais")[["Score_Final"]]
                    st.bar_chart(chart_data)

# ------------------------------------------
# MÓDULO 2: DIAGNÓSTICO DE PREPARAÇÃO
# ------------------------------------------
elif modulo == "Módulo Diagnóstico (Checklist)":
    st.title("📋 Módulo Diagnóstico — Prontidão Exportadora")
    st.caption("Checklist interativo para empresas iniciantes avaliarem seu grau de maturidade.")

    with st.form("checklist_exportacao"):
        st.markdown("**Capacidade Operacional e Financeira**")
        c1 = st.checkbox("Sua empresa tem capacidade fabril ociosa para atender novos pedidos?")
        c2 = st.checkbox("Possui certificações internacionais exigidas no seu setor?")
        
        st.markdown("**Adequação de Produto e Embalagem**")
        c3 = st.checkbox("A embalagem possui rótulo traduzido ou adaptável a exigências externas?")
        c4 = st.checkbox("O produto possui NCM/SH definido corretamente?")
        
        st.markdown("**Estratégia e Equipe**")
        c5 = st.checkbox("Existe equipe ou responsável com domínio de idiomas (ex: Inglês/Espanhol)?")
        
        calcular = st.form_submit_button("Analisar Maturidade")
        
        if calcular:
            pontos = sum([c1, c2, c3, c4, c5])
            porcentagem = (pontos / 5) * 100
            st.subheader(f"Nível de Prontidão: {porcentagem:.0f}%")
            if porcentagem >= 80:
                st.success("Sua empresa apresenta excelente maturidade para iniciar operações internacionais!")
            elif porcentagem >= 40:
                st.warning("Sua empresa tem potencial, mas precisa ajustar processos regulatórios e operacionais.")
            else:
                st.error("Recomendamos estruturar os pré-requisitos operacionais básicos antes de exportar.")

# ------------------------------------------
# MÓDULO 3: VENDAS E PROSPECÇÃO
# ------------------------------------------
elif modulo == "Módulo Vendas (Prospecção)":
    st.title("🎯 Módulo Vendas — Prospecção & Automação")
    st.caption("Identifique parceiros comerciais e gere cartas de apresentação automáticas.")

    col_p, col_i = st.columns(2)
    with col_p:
        pais_destino = st.selectbox("Selecione o País de Destino:", ["Argentina", "Estados Unidos", "Alemanha", "Chile", "México"])
    with col_i:
        idioma = st.selectbox("Idioma da Comunicação:", ["Inglês", "Espanhol", "Alemão"])

    st.subheader("Empresas e Parceiros em Destaque")
    df_parceiros = pd.DataFrame({
        "Empresa": ["Global Import Corp", "Mercado Sur Distribuidora", "EuroTrade Trading"],
        "País": ["Estados Unidos", "Argentina", "Alemanha"],
        "Porte": ["Grande", "Médio", "Grande"],
        "Contato Contatado": ["import@globalcorp.com", "contacto@mercadosur.ar", "supply@eurotrade.de"]
    })
    st.dataframe(df_parceiros[df_parceiros["País"] == pais_destino] if pais_destino in df_parceiros["País"].values else df_parceiros, use_container_width=True)

    st.divider()
    st.subheader("Gerador de Carta de Apresentação Automatizada")
    
    prod_nome = st.text_input("Nome do seu Produto:", "Produtos de Plástico Industrial")
    
    if st.button("Gerar E-mail de Apresentação"):
        if idioma == "Inglês":
            corpo = f"Subject: Commercial Proposal - {prod_nome}\n\nDear Partner,\n\nWe are a Brazilian manufacturer specialized in {prod_nome}. We noticed your strong market presence in {pais_destino} and would like to present our export catalog with competitive tariffs under international standards.\n\nBest regards,"
        elif idioma == "Espanhol":
            corpo = f"Asunto: Propuesta Comercial - {prod_nome}\n\nEstimados,\n\nSomos fabricantes en Brasil de {prod_nome}. Evaluando el mercado de {pais_destino}, nos gustaría presentar nuestro catálogo de exportación.\n\nSaludos cordiales,"
        else:
            corpo = f"Betreff: Geschäftsvorschlag - {prod_nome}\n\nSehr geehrte Damen und Herren,\n\nwir sind ein brasilianischer Hersteller von {prod_nome}. Wir möchten Ihnen unseren Exportkatalog für {pais_destino} vorstellen.\n\nMit freundlichen Grüßen,"
            
        st.text_area("Prévia do E-mail Gerado:", corpo, height=180)
        st.button("✉️ Enviar E-mail Automaticamente")

# ==========================================
# RODAPÉ
# ==========================================
st.markdown("---")
st.markdown('<div style="text-align:center; color:#9ca3af;">ExportAI © 2026 • Soluções Inteligentes em Comércio Exterior</div>', unsafe_allow_html=True)