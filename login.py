import streamlit as st
import base64
import re
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================
st.set_page_config(
    page_title="ExportAI — Acesso",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# ESTILO — inspirado em plataformas profissionais como LinkedIn,
# mas com identidade visual própria do ExportAI.
# ============================================================
st.markdown("""
<style>
    #MainMenu, footer, header {
        visibility: hidden;
    }

    .stApp {
        background: #f3f6f8;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 35px;
        padding-bottom: 40px;
    }

    /* Logo */
    .brand {
        text-align: center;
        margin-bottom: 18px;
    }

    .brand img {
        width: 220px;
        max-width: 80%;
        height: auto;
    }

    /* Cabeçalho */
    .hero {
        text-align: center;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: #0a2540;
        font-size: 30px;
        font-weight: 750;
        margin: 0 0 7px 0;
        letter-spacing: -0.5px;
    }

    .hero p {
        color: #5f6b76;
        font-size: 15px;
        margin: 0;
    }

    /* Card principal */
    .login-card {
        background: white;
        border: 1px solid #dfe5ea;
        border-radius: 12px;
        padding: 30px 34px 25px 34px;
        box-shadow: 0 4px 18px rgba(10, 37, 64, 0.08);
    }

    .card-title {
        color: #172b4d;
        font-size: 23px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .card-subtitle {
        color: #697586;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {
        border-radius: 7px;
    }

    label {
        color: #26364a !important;
        font-weight: 600 !important;
    }

    /* Botões */
    .stButton > button {
        border-radius: 7px;
        min-height: 44px;
        font-weight: 700;
        border: 1px solid #0a66c2;
    }

    /* Botão principal */
    div.stButton > button[kind="primary"] {
        background: #0a66c2;
        color: white;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #004182;
        border-color: #004182;
        color: white;
    }

    /* Separador */
    .separator {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 20px 0;
        color: #7b8794;
        font-size: 13px;
    }

    .separator::before,
    .separator::after {
        content: "";
        height: 1px;
        background: #dfe5ea;
        flex: 1;
    }

    /* Cadastro */
    .section-label {
        color: #0a2540;
        font-size: 16px;
        font-weight: 750;
        margin-top: 14px;
        margin-bottom: 8px;
    }

    .required {
        color: #c62828;
    }

    .terms {
        color: #687585;
        font-size: 12px;
        line-height: 1.5;
        margin: 12px 0;
    }

    .footer {
        text-align: center;
        color: #8a96a3;
        font-size: 12px;
        margin-top: 22px;
    }

    /* Responsivo */
    @media (max-width: 700px) {
        .block-container {
            padding-left: 14px;
            padding-right: 14px;
            padding-top: 20px;
        }

        .login-card {
            padding: 22px 18px;
        }

        .hero h1 {
            font-size: 25px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOGO
# ============================================================
def carregar_logo():
    candidatos = [
        Path(__file__).with_name("logo.png"),
        Path(__file__).with_name("logo(3).png"),
    ]

    for caminho in candidatos:
        if caminho.exists():
            return base64.b64encode(caminho.read_bytes()).decode("utf-8")

    return None


logo_base64 = carregar_logo()

if logo_base64:
    st.markdown(
        f"""
        <div class="brand">
            <img src="data:image/png;base64,{logo_base64}" alt="ExportAI">
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# ESTADO
# ============================================================
if "pagina_login" not in st.session_state:
    st.session_state.pagina_login = "login"

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False

if "cadastro_concluido" not in st.session_state:
    st.session_state.cadastro_concluido = False


# ============================================================
# TELA APÓS LOGIN
# ============================================================
if st.session_state.usuario_logado:
    st.success("Login realizado com sucesso!")

    st.markdown(
        """
        <div class="hero">
            <h1>Bem-vindo ao ExportAI</h1>
            <p>Inteligência para encontrar os mercados mais promissores para sua empresa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Esta área pode ser conectada diretamente à tela de análise de NCM/SH4 "
        "do seu projeto atual."
    )

    if st.button("Sair", use_container_width=True):
        st.session_state.usuario_logado = False
        st.session_state.pagina_login = "login"
        st.rerun()

    st.stop()


# ============================================================
# CABEÇALHO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <h1>Encontre novos mercados para sua empresa</h1>
        <p>Acesse o ExportAI e transforme dados de comércio exterior em oportunidades.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CARD
# ============================================================
st.markdown('<div class="login-card">', unsafe_allow_html=True)

if st.session_state.pagina_login == "login":

    st.markdown(
        """
        <div class="card-title">Entrar</div>
        <div class="card-subtitle">
            Use seu e-mail corporativo para acessar sua conta.
        </div>
        """,
        unsafe_allow_html=True,
    )

    email = st.text_input(
        "E-mail corporativo",
        placeholder="nome@empresa.com.br",
        key="login_email",
    )

    senha = st.text_input(
        "Senha",
        type="password",
        placeholder="Digite sua senha",
        key="login_senha",
    )

    col_esq, col_dir = st.columns([1, 1])

    with col_dir:
        st.markdown(
            "<div style='text-align:right; margin-top:5px; color:#0a66c2; "
            "font-size:13px;'>Esqueci minha senha</div>",
            unsafe_allow_html=True,
        )

    if st.button("Entrar", type="primary", use_container_width=True):
        email_ok = bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))

        if not email.strip():
            st.warning("Informe seu e-mail.")
        elif not email_ok:
            st.warning("Informe um e-mail válido.")
        elif not senha:
            st.warning("Informe sua senha.")
        else:
            # Aqui entra a autenticação real com banco de dados.
            st.session_state.usuario_logado = True
            st.rerun()

    st.markdown('<div class="separator">ou</div>', unsafe_allow_html=True)

    if st.button("Criar conta da empresa", use_container_width=True):
        st.session_state.pagina_login = "cadastro"
        st.rerun()

else:

    st.markdown(
        """
        <div class="card-title">Crie sua conta empresarial</div>
        <div class="card-subtitle">
            Cadastre sua empresa para receber análises personalizadas de exportação.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # DADOS DA EMPRESA
    # --------------------------------------------------------
    st.markdown('<div class="section-label">Dados da empresa</div>', unsafe_allow_html=True)

    empresa = st.text_input(
        "Nome da empresa *",
        placeholder="Ex.: Exportadora Brasil Ltda.",
        key="cad_empresa",
    )

    c1, c2 = st.columns(2)

    with c1:
        cnpj = st.text_input(
            "CNPJ *",
            placeholder="00.000.000/0001-00",
            key="cad_cnpj",
        )

    with c2:
        porte = st.selectbox(
            "Porte da empresa *",
            [
                "Selecione",
                "MEI",
                "Microempresa",
                "Empresa de Pequeno Porte",
                "Média empresa",
                "Grande empresa",
            ],
            key="cad_porte",
        )

    setor = st.selectbox(
        "Setor / segmento de atuação *",
        [
            "Selecione",
            "Agronegócio",
            "Alimentos e bebidas",
            "Automotivo",
            "Máquinas e equipamentos",
            "Químico e petroquímico",
            "Eletrônicos e tecnologia",
            "Têxtil e vestuário",
            "Farmacêutico",
            "Mineração e metais",
            "Madeira e móveis",
            "Plásticos",
            "Construção",
            "Outro",
        ],
        key="cad_setor",
    )

    descricao = st.text_area(
        "O que sua empresa vende?",
        placeholder="Descreva brevemente os principais produtos ou serviços.",
        height=90,
        key="cad_descricao",
    )

    # --------------------------------------------------------
    # DADOS DO RESPONSÁVEL
    # --------------------------------------------------------
    st.markdown(
        '<div class="section-label">Dados do responsável</div>',
        unsafe_allow_html=True,
    )

    nome = st.text_input(
        "Nome completo *",
        placeholder="Nome e sobrenome",
        key="cad_nome",
    )

    c1, c2 = st.columns(2)

    with c1:
        funcao = st.selectbox(
            "Função na empresa *",
            [
                "Selecione",
                "Sócio / Proprietário",
                "Diretor",
                "Gerente",
                "Coordenador",
                "Analista",
                "Comercial / Vendas",
                "Comércio Exterior",
                "Compras",
                "Financeiro",
                "Outro",
            ],
            key="cad_funcao",
        )

    with c2:
        telefone = st.text_input(
            "Telefone / WhatsApp *",
            placeholder="(11) 99999-9999",
            key="cad_telefone",
        )

    email = st.text_input(
        "E-mail corporativo *",
        placeholder="nome@empresa.com.br",
        key="cad_email",
    )

    # --------------------------------------------------------
    # ACESSO
    # --------------------------------------------------------
    st.markdown(
        '<div class="section-label">Dados de acesso</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        senha = st.text_input(
            "Criar senha *",
            type="password",
            placeholder="Mínimo de 8 caracteres",
            key="cad_senha",
        )

    with c2:
        confirmar = st.text_input(
            "Confirmar senha *",
            type="password",
            placeholder="Repita sua senha",
            key="cad_confirmar",
        )

    # --------------------------------------------------------
    # PERFIL DE EXPORTAÇÃO
    # --------------------------------------------------------
    st.markdown(
        '<div class="section-label">Perfil de exportação</div>',
        unsafe_allow_html=True,
    )

    exporta = st.radio(
        "Sua empresa já exporta?",
        ["Sim", "Não", "Está começando a exportar"],
        horizontal=True,
        key="cad_exporta",
    )

    if exporta == "Sim":
        st.multiselect(
            "Principais mercados atuais",
            [
                "Argentina",
                "Chile",
                "Estados Unidos",
                "México",
                "Alemanha",
                "China",
                "Uruguai",
                "Paraguai",
                "Colômbia",
                "Peru",
                "Outro",
            ],
            key="cad_paises",
        )

    objetivo = st.multiselect(
        "O que você busca no ExportAI?",
        [
            "Encontrar novos países para exportar",
            "Comparar mercados",
            "Descobrir oportunidades para meus produtos",
            "Analisar NCM/SH4",
            "Avaliar crescimento de mercados",
            "Planejar minha primeira exportação",
        ],
        key="cad_objetivos",
    )

    aceite = st.checkbox(
        "Li e concordo com os Termos de Uso e a Política de Privacidade.",
        key="cad_aceite",
    )

    st.markdown(
        """
        <div class="terms">
            Seus dados empresariais serão utilizados para criar seu perfil
            e personalizar as análises e recomendações do ExportAI.
            Os campos marcados com * são obrigatórios.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Criar minha conta", type="primary", use_container_width=True):

        cnpj_limpo = re.sub(r"\D", "", cnpj)
        email_ok = bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))

        erros = []

        if not empresa.strip():
            erros.append("Informe o nome da empresa.")
        if len(cnpj_limpo) != 14:
            erros.append("Informe um CNPJ válido com 14 dígitos.")
        if porte == "Selecione":
            erros.append("Selecione o porte da empresa.")
        if setor == "Selecione":
            erros.append("Selecione o setor da empresa.")
        if not nome.strip():
            erros.append("Informe o nome do responsável.")
        if funcao == "Selecione":
            erros.append("Selecione a função do responsável.")
        if not telefone.strip():
            erros.append("Informe o telefone.")
        if not email_ok:
            erros.append("Informe um e-mail corporativo válido.")
        if len(senha) < 8:
            erros.append("A senha deve ter pelo menos 8 caracteres.")
        if senha != confirmar:
            erros.append("As senhas não coincidem.")
        if not aceite:
            erros.append("Você precisa aceitar os Termos de Uso e a Política de Privacidade.")

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            # Aqui entra o INSERT no banco de dados.
            st.session_state.cadastro_concluido = True
            st.session_state.pagina_login = "login"
            st.success("Conta criada com sucesso! Agora você já pode entrar.")
            st.rerun()

    if st.button("Já tenho uma conta", use_container_width=True):
        st.session_state.pagina_login = "login"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer">
        ExportAI • Inteligência para novos mercados<br>
        © 2026 ExportAI
    </div>
    """,
    unsafe_allow_html=True,
)
