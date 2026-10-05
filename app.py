import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO
from supabase import create_client, Client

# Importações do ReportLab para geração do PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Invest Control Pro - Sistema de Gestão Financeira",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# BLOCO DE ESTILO SEPARADO - PALETA DARK PREMIUM [VISUAL]
# -----------------------------------------------------------------------------
PALETA = {
    "fundo_principal":   "#070A0F",
    "fundo_sidebar":     "#0B1018",
    "fundo_card":        "#111823",
    "fundo_card2":       "#0E141D",
    "fundo_hover":       "#182230",
    "borda":             "#1E2937",
    "borda_acento":      "#3B82F6",

    "texto_principal":   "#EAF0F7",
    "texto_secundario":  "#8B96A7",
    "texto_fraco":       "#4A5563",

    "acento":            "#3B82F6",
    "acento_hover":      "#2563EB",
    "acento_glow":       "rgba(59,130,246,0.35)",
    "acento_glow_soft":  "rgba(59,130,246,0.15)",

    "verde":             "#22C55E",
    "verde_bg":          "rgba(34,197,94,0.14)",
    "vermelho":          "#EF4444",
    "vermelho_bg":       "rgba(239,68,68,0.14)",
    "amarelo":           "#F59E0B",
    "amarelo_bg":        "rgba(245,158,11,0.14)",
    "roxo":              "#8B5CF6",
    "ciano":             "#06B6D4",
}

st.markdown(f"""
<style>
    /* ============================================================
       [VISUAL] RESET E BASE
       ============================================================ */
    .stApp {{
        background:
            radial-gradient(ellipse 80% 50% at 20% 0%, rgba(59,130,246,0.10), transparent 60%),
            radial-gradient(ellipse 80% 50% at 80% 100%, rgba(139,92,246,0.08), transparent 60%),
            linear-gradient(180deg, {PALETA["fundo_principal"]} 0%, #05070B 100%);
        color: {PALETA["texto_principal"]};
        font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    }}
    html, body, [class*="css"] {{
        font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
        color: {PALETA["texto_principal"]};
    }}
    .main .block-container {{
        padding: 1.5rem 2.2rem 3rem 2.2rem;
        max-width: 1500px;
    }}

    /* ============================================================
       [VISUAL] TÍTULOS E CABEÇALHOS
       ============================================================ */
    h1 {{
        color: {PALETA["texto_principal"]} !important;
        font-weight: 700 !important;
        letter-spacing: -0.6px !important;
        font-size: 30px !important;
        background: linear-gradient(90deg, #FFFFFF 0%, #B8C4D6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    h2, h3 {{
        color: {PALETA["texto_principal"]} !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px !important;
    }}
    h4, h5 {{
        color: {PALETA["texto_secundario"]} !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1.3px;
        font-size: 11px !important;
    }}
    p, span, label {{ color: {PALETA["texto_principal"]}; }}
    [data-testid="stCaptionContainer"] {{
        color: {PALETA["texto_secundario"]} !important;
        font-size: 12px !important;
    }}

    /* ============================================================
       [VISUAL] SIDEBAR PREMIUM
       ============================================================ */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {PALETA["fundo_sidebar"]} 0%, {PALETA["fundo_principal"]} 100%);
        border-right: 1px solid {PALETA["borda"]};
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {PALETA["texto_principal"]} !important;
        border-bottom: 1px solid {PALETA["borda"]};
        padding-bottom: 10px;
        margin-bottom: 12px;
        letter-spacing: 0.3px;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: {PALETA["borda"]} !important;
        margin: 18px 0 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        text-align: left !important;
        justify-content: flex-start !important;
    }}

    /* ============================================================
       [VISUAL] METRIC CARDS — PAINÉIS DE VALORES
       ============================================================ */
    div[data-testid="stMetric"] {{
        background:
            linear-gradient(145deg, {PALETA["fundo_card"]} 0%, {PALETA["fundo_card2"]} 100%);
        border: 1px solid {PALETA["borda"]};
        border-radius: 16px;
        padding: 20px 22px !important;
        box-shadow:
            0 8px 24px -12px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(255,255,255,0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    div[data-testid="stMetric"]::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, {PALETA["acento"]}, {PALETA["ciano"]}, transparent);
        opacity: 0.7;
    }}
    div[data-testid="stMetric"]::after {{
        content: '';
        position: absolute;
        top: -50%; right: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, {PALETA["acento_glow_soft"]} 0%, transparent 60%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }}
    div[data-testid="stMetric"]:hover {{
        border-color: {PALETA["borda_acento"]};
        box-shadow:
            0 0 0 1px {PALETA["acento_glow"]},
            0 12px 40px -12px rgba(59,130,246,0.45);
        transform: translateY(-3px);
    }}
    div[data-testid="stMetric"]:hover::after {{ opacity: 1; }}
    div[data-testid="stMetric"] label {{
        color: {PALETA["texto_secundario"]} !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {PALETA["texto_principal"]} !important;
        font-family: 'Consolas', 'JetBrains Mono', 'Roboto Mono', monospace !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
        font-size: 12px !important;
        font-weight: 600 !important;
    }}

    /* ============================================================
       [VISUAL] BOTÕES — NEON ELEGANTE
       ============================================================ */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {{
        background: linear-gradient(145deg, {PALETA["fundo_card"]} 0%, {PALETA["fundo_card2"]} 100%) !important;
        color: {PALETA["texto_principal"]} !important;
        border: 1px solid {PALETA["borda"]} !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        letter-spacing: 0.2px;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }}
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background: linear-gradient(145deg, {PALETA["acento"]} 0%, {PALETA["acento_hover"]} 100%) !important;
        border-color: {PALETA["acento"]} !important;
        color: #FFFFFF !important;
        box-shadow:
            0 0 22px {PALETA["acento_glow"]},
            0 6px 18px rgba(0,0,0,0.35);
        transform: translateY(-2px);
    }}
    .stButton > button:active,
    .stFormSubmitButton > button:active {{
        transform: translateY(0);
        box-shadow: 0 0 12px {PALETA["acento_glow"]};
    }}

    /* ============================================================
       [VISUAL] ABAS (TABS)
       ============================================================ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {PALETA["fundo_card"]};
        padding: 6px;
        border-radius: 14px;
        border: 1px solid {PALETA["borda"]};
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 42px;
        background: transparent !important;
        border-radius: 9px !important;
        color: {PALETA["texto_secundario"]} !important;
        font-weight: 600;
        font-size: 13px;
        padding: 0 18px;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.2px;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {PALETA["texto_principal"]} !important;
        background: {PALETA["fundo_hover"]} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(145deg, {PALETA["acento"]} 0%, {PALETA["acento_hover"]} 100%) !important;
        color: #FFFFFF !important;
        box-shadow:
            0 0 18px {PALETA["acento_glow"]},
            inset 0 1px 0 rgba(255,255,255,0.15);
    }}
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

    /* ============================================================
       [VISUAL] INPUTS
       ============================================================ */
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    div[data-baseweb="select"] > div {{
        background: {PALETA["fundo_principal"]} !important;
        color: {PALETA["texto_principal"]} !important;
        border: 1px solid {PALETA["borda"]} !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        transition: all 0.2s ease;
        padding: 10px 12px !important;
    }}
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {{
        color: {PALETA["texto_fraco"]} !important;
    }}
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus,
    div[data-baseweb="select"] > div:focus-within {{
        border-color: {PALETA["acento"]} !important;
        box-shadow: 0 0 0 3px {PALETA["acento_glow_soft"]} !important;
        outline: none !important;
    }}
    .stNumberInput button {{
        background: {PALETA["fundo_card"]} !important;
        border-color: {PALETA["borda"]} !important;
        color: {PALETA["texto_principal"]} !important;
    }}
    .stNumberInput button:hover {{
        background: {PALETA["acento"]} !important;
        color: white !important;
    }}
    label[data-testid="stWidgetLabel"] p {{
        color: {PALETA["texto_secundario"]} !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.9px;
        font-weight: 600;
    }}

    /* ============================================================
       [VISUAL] EXPANDER
       ============================================================ */
    div[data-testid="stExpander"] {{
        background: {PALETA["fundo_card"]};
        border: 1px solid {PALETA["borda"]} !important;
        border-radius: 14px !important;
        overflow: hidden;
        box-shadow: 0 4px 16px -8px rgba(0,0,0,0.4);
    }}
    div[data-testid="stExpander"] summary {{
        font-weight: 600 !important;
        color: {PALETA["texto_principal"]} !important;
        padding: 14px 20px !important;
        transition: background 0.2s ease;
    }}
    div[data-testid="stExpander"] summary:hover {{
        background: {PALETA["fundo_hover"]};
    }}

    /* ============================================================
       [VISUAL] ALERTAS
       ============================================================ */
    div[data-testid="stAlert"] {{
        border-radius: 12px !important;
        border-left-width: 4px !important;
        font-size: 13px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 16px -8px rgba(0,0,0,0.4);
    }}
    div[data-testid="stAlert"][data-baseweb="notification"] {{
        background: {PALETA["fundo_card"]} !important;
    }}

    /* ============================================================
       [VISUAL] TABELAS E DATAFRAMES
       ============================================================ */
    .stDataFrame, div[data-testid="stTable"] {{
        background: {PALETA["fundo_card"]} !important;
        border-radius: 14px !important;
        border: 1px solid {PALETA["borda"]} !important;
        overflow: hidden;
        box-shadow: 0 4px 16px -8px rgba(0,0,0,0.4);
    }}
    div[data-testid="stTable"] table {{
        background: {PALETA["fundo_card"]} !important;
        color: {PALETA["texto_principal"]} !important;
        border-collapse: collapse !important;
    }}
    div[data-testid="stTable"] thead tr th {{
        background: {PALETA["fundo_sidebar"]} !important;
        color: {PALETA["texto_secundario"]} !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-size: 11px !important;
        font-weight: 700 !important;
        border-bottom: 1px solid {PALETA["borda"]} !important;
        padding: 14px !important;
    }}
    div[data-testid="stTable"] tbody tr {{
        border-bottom: 1px solid {PALETA["borda"]} !important;
        transition: background 0.15s ease;
    }}
    div[data-testid="stTable"] tbody tr:nth-child(even) {{
        background: rgba(31, 41, 55, 0.2) !important;
    }}
    div[data-testid="stTable"] tbody tr:hover {{
        background: {PALETA["fundo_hover"]} !important;
    }}
    div[data-testid="stTable"] tbody td {{
        color: {PALETA["texto_principal"]} !important;
        font-size: 13px !important;
        padding: 12px 14px !important;
    }}

    /* ============================================================
       [VISUAL] PROGRESS BAR
       ============================================================ */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {PALETA["acento"]} 0%, {PALETA["ciano"]} 100%) !important;
        border-radius: 999px !important;
        box-shadow: 0 0 14px {PALETA["acento_glow"]};
    }}
    .stProgress > div > div > div {{
        background: {PALETA["fundo_card"]} !important;
        border-radius: 999px !important;
        height: 10px !important;
    }}

    /* ============================================================
       [VISUAL] CHECKBOX E RADIO
       ============================================================ */
    .stCheckbox label span,
    .stRadio label span {{
        color: {PALETA["texto_principal"]} !important;
        font-size: 13px !important;
    }}
    .stCheckbox input:checked + div,
    .stRadio input:checked + div {{
        background-color: {PALETA["acento"]} !important;
        border-color: {PALETA["acento"]} !important;
    }}

    /* ============================================================
       [VISUAL] DIVISORES E FORMULÁRIOS
       ============================================================ */
    hr {{
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, {PALETA["borda"]}, transparent) !important;
        margin: 24px 0 !important;
    }}
    div[data-testid="stForm"] {{
        background:
            linear-gradient(145deg, {PALETA["fundo_card"]} 0%, {PALETA["fundo_card2"]} 100%);
        border: 1px solid {PALETA["borda"]};
        border-radius: 16px;
        padding: 24px !important;
        box-shadow:
            0 8px 24px -12px rgba(0,0,0,0.5),
            inset 0 1px 0 rgba(255,255,255,0.02);
    }}

    /* ============================================================
       [VISUAL] SCROLLBAR
       ============================================================ */
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{
        background: {PALETA["fundo_principal"]};
        border-radius: 999px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {PALETA["borda"]} 0%, #2A3546 100%);
        border-radius: 999px;
        border: 2px solid {PALETA["fundo_principal"]};
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {PALETA["acento"]};
    }}

    /* ============================================================
       [VISUAL] TOOLTIP
       ============================================================ */
    div[data-baseweb="tooltip"] {{
        background: {PALETA["fundo_card"]} !important;
        border: 1px solid {PALETA["borda"]} !important;
        border-radius: 8px !important;
        color: {PALETA["texto_principal"]} !important;
        box-shadow: 0 8px 24px -8px rgba(0,0,0,0.6);
    }}

    /* ============================================================
       [VISUAL] LOGIN — TÍTULO COM GRADIENTE PREMIUM
       ============================================================ */
    .login-title {{
        background: linear-gradient(90deg, {PALETA["acento"]} 0%, {PALETA["ciano"]} 50%, {PALETA["roxo"]} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1.5px;
        font-weight: 800;
        filter: drop-shadow(0 0 20px {PALETA["acento_glow"]});
    }}
    .login-subtitle {{
        font-size: 14px;
        color: {PALETA["texto_secundario"]};
        text-align: center;
        margin-bottom: 30px;
        letter-spacing: 0.5px;
    }}

    /* ============================================================
       [VISUAL] BADGES DE STATUS
       ============================================================ */
    .badge-status {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
        margin-top: 4px;
    }}
    .badge-ok {{
        background: {PALETA["verde_bg"]};
        color: {PALETA["verde"]};
        border: 1px solid rgba(34,197,94,0.3);
    }}
    .badge-pendente {{
        background: {PALETA["amarelo_bg"]};
        color: {PALETA["amarelo"]};
        border: 1px solid rgba(245,158,11,0.3);
    }}

    /* ============================================================
       [VISUAL] GLOBAL — REMOVE MENU STREAMLIT
       ============================================================ */
    #MainMenu, footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{
        background: transparent;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONTROLE DE SESSÃO DE AUTENTICAÇÃO
# -----------------------------------------------------------------------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

meses_nomes = [
    "Janeiro", "Fevereiro", "Março", "Abril", 
    "Maio", "Junho", "Julho", "Agosto", 
    "Setembro", "Outubro", "Novembro", "Dezembro"
]
for i, m in enumerate(meses_nomes):
    key_nome = f"reserva_mes_{i+1}"
    if key_nome not in st.session_state:
        st.session_state[key_nome] = False

# -----------------------------------------------------------------------------
# TELA DE LOGIN  [VISUAL]
# -----------------------------------------------------------------------------
if not st.session_state['autenticado']:
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="login-title" style="font-size:32px; text-align:center; margin-bottom:12px;">🛡️ INVEST CONTROL PRO</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="login-subtitle">Sistema Integrado de Projeção Econômica & Acesso Seguro</div>',
            unsafe_allow_html=True
        )
        
        with st.form("form_login"):
            st.markdown("### Credenciais de Acesso")
            usuario = st.text_input("Usuário / Credencial", placeholder="Digite seu usuário...")
            senha = st.text_input("Senha de Acesso", type="password", placeholder="Digite sua senha...")
            
            st.markdown("---")
            btn_entrar = st.form_submit_button("Acessar Sistema", use_container_width=True)
            
            if btn_entrar:
                if usuario == "admin" and senha == "admin123":
                    st.session_state['autenticado'] = True
                    st.success("Acesso autorizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas. Acesso restrito.")
                
        st.info("💡 **Segurança Ativa:** Ambiente protegido contra oscilações e acessos não autorizados.")
        st.stop()

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO E CONEXÃO COM O SUPABASE (PÓS-LOGIN)
# -----------------------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    
    if not url or not key:
        url = st.sidebar.text_input("Supabase URL", type="default")
        key = st.sidebar.text_input("Supabase API Key (Anon)", type="password")
        if not url or not key:
            return None
    return create_client(url, key) if url and key else None

supabase = init_supabase()

# -----------------------------------------------------------------------------
# FUNÇÕES DE MANIPULAÇÃO DE DADOS (SUPABASE & FALLBACK)
# -----------------------------------------------------------------------------
def carregar_configuracoes():
    if supabase:
        try:
            res = supabase.table("configuracoes").select("*").eq("id", 1).execute()
            if res.data:
                return res.data[0]
        except:
            pass
    return {
        "aluguel_total": 1700.0,
        "salario_a": 2700.0,
        "salario_b": 2000.0,
        "vr_a": 700.0,
        "meta_reserva_mensal": 800.0,
        "aluguel_a_custom": 850.0,
        "aluguel_b_custom": 850.0,
        "usa_edicao_manual": False
    }

def salvar_configuracoes(aluguel, salario_a, salario_b, vr_a, meta_reserva, aluguel_a_custom, aluguel_b_custom, usa_edicao):
    if supabase:
        try:
            supabase.table("configuracoes").update({
                "aluguel_total": aluguel,
                "salario_a": salario_a,
                "salario_b": salario_b,
                "vr_a": vr_a,
                "meta_reserva_mensal": meta_reserva,
                "aluguel_a_custom": aluguel_a_custom,
                "aluguel_b_custom": aluguel_b_custom,
                "usa_edicao_manual": usa_edicao
            }).eq("id", 1).execute()
        except:
            pass

def carregar_gastos_fixos():
    if supabase:
        try:
            res = supabase.table("gastos_fixos").select("*").execute()
            if res.data:
                return pd.DataFrame(res.data)
        except:
            pass
    return pd.DataFrame([
        {"id": 1, "descricao": "Internet", "valor": 100.0},
        {"id": 2, "descricao": "Recarga celular", "valor": 30.0},
        {"id": 3, "descricao": "Corte de cabelo", "valor": 90.0},
        {"id": 4, "descricao": "Cartão de crédito", "valor": 49.0}
    ])

def adicionar_gasto_fixo(descricao, valor):
    if supabase:
        try:
            supabase.table("gastos_fixos").insert({"descricao": descricao, "valor": valor}).execute()
        except:
            pass

def remover_gasto_fixo(gasto_id):
    if supabase:
        try:
            supabase.table("gastos_fixos").delete().eq("id", gasto_id).execute()
        except:
            pass

def carregar_despesas_variaveis():
    if supabase:
        try:
            res = supabase.table("despesas_variaveis").select("*").order("data", desc=True).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['data'] = pd.to_datetime(df['data'])
                return df
        except:
            pass
    return pd.DataFrame(columns=["id", "data", "descricao", "categoria", "valor"])

def adicionar_despesa_variavel(data, descricao, categoria, valor):
    if supabase:
        try:
            data_formatada = str(data) if hasattr(data, "strftime") else data
            supabase.table("despesas_variaveis").insert({
                "data": data_formatada,
                "descricao": str(descricao).strip(),
                "categoria": str(categoria).strip(),
                "valor": float(valor)
            }).execute()
        except Exception as e:
            st.error(f"Erro ao salvar no banco de dados: {e}")

def remover_despesa_variavel(despesa_id):
    if supabase:
        try:
            supabase.table("despesas_variaveis").delete().eq("id", despesa_id).execute()
        except:
            pass

# -----------------------------------------------------------------------------
# FUNÇÃO GERADORA DE RELATÓRIO PDF
# -----------------------------------------------------------------------------
def gerar_relatorio_pdf(df_fixos, df_variaveis, salario_a, salario_b, aluguel_a, aluguel_b):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#3B82F6'), spaceAfter=12, alignment=1
    )
    heading_style = ParagraphStyle(
        'HeadingStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#E6EDF3'), spaceBefore=12, spaceAfter=6
    )
    normal_style = styles['Normal']

    story.append(Paragraph("<b>INVEST CONTROL PRO - RELATÓRIO FINANCEIRO</b>", title_style))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle('Sub', parent=normal_style, alignment=1, textColor=colors.HexColor('#8B949E'))))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>1. Resumo de Rendas e Contribuições</b>", heading_style))
    resumo_data = [
        ["Descrição", "Valor (R$)"],
        ["Salário Pessoa A", f"R$ {salario_a:,.2f}"],
        ["Salário Pessoa B", f"R$ {salario_b:,.2f}"],
        ["Aluguel Proporcional (A)", f"R$ {aluguel_a:,.2f}"],
        ["Aluguel Proporcional (B)", f"R$ {aluguel_b:,.2f}"]
    ]
    t_resumo = Table(resumo_data, colWidths=[250, 200])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))
    ]))
    story.append(t_resumo)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>2. Relatório de Custos e Gastos Fixos</b>", heading_style))
    if not df_fixos.empty:
        fixos_data = [["Descrição do Gasto", "Valor Mensal (R$)"]]
        for _, row in df_fixos.iterrows():
            fixos_data.append([str(row['descricao']), f"R$ {float(row['valor']):,.2f}"])
        t_fixos = Table(fixos_data, colWidths=[250, 200])
        t_fixos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))
        ]))
        story.append(t_fixos)
    else:
        story.append(Paragraph("Nenhum gasto fixo cadastrado.", normal_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>3. Relatório de Despesas Variáveis (Perdas e Saídas de Caixa)</b>", heading_style))
    if not df_variaveis.empty:
        var_data = [["Data", "Descrição", "Categoria", "Valor (R$)"]]
        for _, row in df_variaveis.iterrows():
            data_str = row['data'].strftime('%d/%m/%Y') if pd.notnull(row['data']) else ""
            var_data.append([data_str, str(row['descricao']), str(row['categoria']), f"R$ {float(row['valor']):,.2f}"])
        t_vars = Table(var_data, colWidths=[80, 170, 110, 90])
        t_vars.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))
        ]))
        story.append(t_vars)
    else:
        story.append(Paragraph("Nenhuma despesa variável registrada.", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -----------------------------------------------------------------------------
# INTERFACE DO USUÁRIO - SIDEBAR (CONFIGURAÇÕES E LOGOUT)
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Parâmetros Financeiros")

if st.sidebar.button("🔒 Sair / Bloquear Tela", use_container_width=True):
    st.session_state['autenticado'] = False
    st.rerun()

st.sidebar.divider()

config = carregar_configuracoes()

st.sidebar.subheader("🔀 Simulação de Cenário")
cenario = st.sidebar.radio(
    "Selecione o Cenário Ativo:",
    options=["COM Participação de B", "SEM Participação de B (Contingência)"],
    index=0
)
b_participa = (cenario == "COM Participação de B")

st.sidebar.divider()
st.sidebar.subheader("💵 Rendas e Custos Base")

aluguel_input = st.sidebar.number_input("Valor do Aluguel Total (R$)", value=float(config["aluguel_total"]), step=50.0)
salario_a_input = st.sidebar.number_input("Salário Pessoa A (R$)", value=float(config["salario_a"]), step=100.0)
vr_a_input = st.sidebar.number_input("Vale Refeição (VR) A (R$)", value=float(config["vr_a"]), step=50.0)

if b_participa:
    salario_b_input = st.sidebar.number_input("Salário Pessoa B (R$)", value=float(config["salario_b"]), step=100.0)
else:
    salario_b_input = 0.0
    st.sidebar.warning("⚠️ Cenário Contingência: B não está participando.")

meta_reserva_input = st.sidebar.number_input("Meta de Reserva Mensal (R$)", value=float(config["meta_reserva_mensal"]), step=50.0)

st.sidebar.divider()
st.sidebar.subheader("✏ Edição Dinâmica do Aluguel")
edicao_manual_default = bool(config.get("usa_edicao_manual", False))
edicao_manual = st.sidebar.checkbox("Habilitar edição manual customizada", value=edicao_manual_default)

aluguel_a_input = None
aluguel_b_input = None

val_a_db = float(config.get("aluguel_a_custom", aluguel_input * 0.5))
val_b_db = float(config.get("aluguel_b_custom", aluguel_input * 0.5))

if edicao_manual and b_participa:
    quem_edita = st.sidebar.radio("Quem você deseja ajustar?", options=["Pessoa A", "Pessoa B"], index=0)
    
    if quem_edita == "Pessoa A":
        aluguel_a_input = st.sidebar.number_input(
            "Valor pago por A (R$)", 
            min_value=0.0, 
            max_value=float(aluguel_input), 
            value=val_a_db, 
            step=25.0
        )
        aluguel_b_input = max(0.0, aluguel_input - aluguel_a_input)
        st.sidebar.info(f"💡 Valor de B ajustado automaticamente: **R$ {aluguel_b_input:,.2f}**")
    else:
        aluguel_b_input = st.sidebar.number_input(
            "Valor pago por B (R$)", 
            min_value=0.0, 
            max_value=float(aluguel_input), 
            value=val_b_db, 
            step=25.0
        )
        aluguel_a_input = max(0.0, aluguel_input - aluguel_b_input)
        st.sidebar.info(f"💡 Valor de A ajustado automaticamente: **R$ {aluguel_a_input:,.2f}**")
else:
    aluguel_a_input = val_a_db
    aluguel_b_input = val_b_db

if st.sidebar.button("💾 Salvar Parâmetros"):
    a_save = aluguel_a_input if edicao_manual else aluguel_input * 0.5
    b_save = aluguel_b_input if edicao_manual else aluguel_input * 0.5
    salvar_configuracoes(aluguel_input, salario_a_input, salario_b_input, vr_a_input, meta_reserva_input, a_save, b_save, edicao_manual)
    st.sidebar.success("Parâmetros e aluguel customizado salvos no Supabase!")
    st.rerun()

# -----------------------------------------------------------------------------
# ENGINE DE CÁLCULO FINANCEIRO E PROPORÇÃO DINÂMICA
# -----------------------------------------------------------------------------
if b_participa:
    if edicao_manual and aluguel_a_input is not None and aluguel_b_input is not None:
        aluguel_a = aluguel_a_input
        aluguel_b = aluguel_b_input
        prop_a = aluguel_a / aluguel_input if aluguel_input > 0 else 0.5
        prop_b = aluguel_b / aluguel_input if aluguel_input > 0 else 0.5
    else:
        if (salario_a_input + salario_b_input) > 0:
            renda_total = salario_a_input + salario_b_input
            prop_a = salario_a_input / renda_total
            prop_b = salario_b_input / renda_total
            aluguel_a = aluguel_input * prop_a
            aluguel_b = aluguel_input * prop_b
        else:
            prop_a, prop_b = 1.0, 0.0
            aluguel_a, aluguel_b = aluguel_input, 0.0
else:
    prop_a = 1.0
    prop_b = 0.0
    aluguel_a = aluguel_input
    aluguel_b = 0.0

df_gastos_fixos = carregar_gastos_fixos()
total_outros_fixos_a = df_gastos_fixos["valor"].sum() if not df_gastos_fixos.empty else 0.0
total_fixos_a = aluguel_a + total_outros_fixos_a

saldo_livre_bruto = salario_a_input - total_fixos_a
meta_reserva_efetiva = meta_reserva_input if b_participa else min(meta_reserva_input, max(0.0, saldo_livre_bruto - 100))
saldo_para_variaveis = saldo_livre_bruto - meta_reserva_efetiva

df_variaveis = carregar_despesas_variaveis()
total_gastos_variaveis = df_variaveis["valor"].sum() if not df_variaveis.empty else 0.0
saldo_caixa_restante = saldo_para_variaveis - total_gastos_variaveis

# -----------------------------------------------------------------------------
# CORPO PRINCIPAL DO APLICATIVO
# -----------------------------------------------------------------------------
st.title("📊 Painel de Projeção Econômica & Controle")
st.caption(f"Cenário Ativo: **{cenario}** | Alimentação protegida com VR de R$ {vr_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Líquido (A)", f"+ R$ {salario_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col2.metric("Sua Parte no Aluguel", f"- R$ {aluguel_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), delta=f"{prop_a*100:.1f}% do aluguel" if b_participa else "100% (Integral)")
col3.metric("Total Gastos Fixos (A)", f"- R$ {total_fixos_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col4.metric("Aporte Reserva Mensal", f"- R$ {meta_reserva_efetiva:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

st.divider()

# ABAS DO APLICATIVO
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📌 Planejamento & Cenários", 
    "💳 Controle de Gastos Diários", 
    "⚙ Gerenciar Custos Fixos", 
    "📈 Simulador de Investimentos",
    "📊 DRE & Análise de Lucro",
    "📑 Relatórios PDF"
])

with tab1:
    st.subheader("🏠 Divisão e Proporcionalidade do Aluguel (A e B)")
    col_div1, col_div2, col_div3 = st.columns(3)
    col_div1.metric("Salário de A", f"+ R$ {salario_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_div2.metric("Salário de B", f"+ R$ {salario_b_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',') if b_participa else "R$ 0,00")
    col_div3.metric("Aluguel Total", f"R$ {aluguel_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

    col_val1, col_val2 = st.columns(2)
    col_val1.info(f"👤 **Pessoa A vai pagar:** - R$ **{aluguel_a:,.2f}** ({prop_a*100:.1f}% do valor total do aluguel)".replace('.', '#').replace(',', '.').replace('#', ','))
    if b_participa:
        col_val2.success(f"👥 **Pessoa B vai pagar:** - R$ **{aluguel_b:,.2f}** ({prop_b*100:.1f}% do valor total do aluguel)".replace('.', '#').replace(',', '.').replace('#', ','))
    else:
        col_val2.warning("⚠️ **Pessoa B:** Sem participação neste cenário (A assume 100%).")

    st.divider()

    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("💡 Distribuição do Salário de A")
        dados_composicao = {
            "Categoria": ["Aluguel Proporcional", "Outros Custos Fixos", "Meta de Reserva", "Orçamento Variável Livre"],
            "Valor": [aluguel_a, total_outros_fixos_a, meta_reserva_efetiva, max(0.0, saldo_para_variaveis)]
        }
        df_comp = pd.DataFrame(dados_composicao)
        fig_pie = px.pie(df_comp, names="Categoria", values="Valor", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_pie.update_layout(
            paper_bgcolor="#111823",
            plot_bgcolor="#111823",
            font_color="#EAF0F7",
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("🛡 Progresso Anual da Reserva de Emergência (12 Meses)")
        st.write(f"**Aporte Mensal Previsto:** R$ {meta_reserva_efetiva:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        st.write(f"**Meta Anual Acumulada (12 Meses de Aporte):** R$ {meta_reserva_efetiva * 12:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        
        st.markdown("##### 🗓️ Status de Pagamento dos Meses:")
        cols_grid = st.columns(4)
        meses_concluidos_count = 0
        
        for i, nome_mes in enumerate(meses_nomes):
            col_idx = i % 4
            with cols_grid[col_idx]:
                key_nome = f"reserva_mes_{i+1}"
                status = st.checkbox(f"{i+1}. {nome_mes}", key=key_nome)
                if status:
                    meses_concluidos_count += 1
                    st.markdown('<span class="badge-status badge-ok">● pago</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="badge-status badge-pendente">⏳ pendente</span>', unsafe_allow_html=True)
                    
        pct_concluido = meses_concluidos_count / 12.0
        montante_acumulado_real = meta_reserva_efetiva * meses_concluidos_count
        
        st.markdown("---")
        st.progress(pct_concluido)
        st.markdown(f"**Progresso Anual:** {meses_concluidos_count} de 12 meses concluídos (**{pct_concluido * 100:.1f}%**)")
        st.write(f"Montante total depositado e confirmado: **R$ {montante_acumulado_real:,.2f}**".replace('.', '#').replace(',', '.').replace('#', ','))

with tab2:
    st.subheader("🛒 Gerenciamento de Despesas Variáveis do Mês")
    col_lim1, col_lim2, col_lim3 = st.columns(3)
    col_lim1.metric("Orçamento Variável Disponível", f"R$ {saldo_para_variaveis:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_lim2.metric("Total Já Gasto no Mês", f"- R$ {total_gastos_variaveis:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_lim3.metric("Saldo do Caixa Restante", f"{'+' if saldo_caixa_restante >=0 else '-'} R$ {abs(saldo_caixa_restante):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), delta_color="normal" if saldo_caixa_restante >= 0 else "inverse")
    st.divider()
    
    with st.expander("➕ Lançar Nova Despesa Variável", expanded=True):
        with st.form("form_despesa", clear_on_submit=True):
            f_col1, f_col2, f_col3, f_col4 = st.columns([2, 3, 2, 2])
            data_exp = f_col1.date_input("Data")
            desc_exp = f_col2.text_input("Descrição")
            cat_exp = f_col3.selectbox("Categoria", ["Lazer / Passeios", "Farmácia / Saúde", "Vestuário", "Imprevistos", "Outros"])
            val_exp = f_col4.number_input("Valor (R$)", min_value=0.01, step=10.0)
            if st.form_submit_button("Lançar Despesa"):
                if desc_exp:
                    adicionar_despesa_variavel(data_exp, desc_exp, cat_exp, val_exp)
                    st.success("Despesa lançada com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe uma descrição.")
    
    if not df_variaveis.empty:
        for idx, row in df_variaveis.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1])
            c1.write(row["data"].strftime("%d/%m/%Y"))
            c2.write(row["descricao"])
            c3.write(row["categoria"])
            c4.write(f"- R$ {row['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
            if c5.button("🗑️", key=f"del_var_{row['id']}"):
                remover_despesa_variavel(row["id"])
                st.rerun()

with tab3:
    st.subheader("📋 Tabela de Custos Fixos de A")
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        if not df_gastos_fixos.empty:
            for idx, row in df_gastos_fixos.iterrows():
                cf1, cf2, cf3 = st.columns([3, 2, 1])
                cf1.write(f"**{row['descricao']}**")
                cf2.write(f"- R$ {row['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
                if cf3.button("Excluir", key=f"del_fix_{row['id']}"):
                    remover_gasto_fixo(row["id"])
                    st.rerun()
    with col_f2:
        st.write("#### Adicionar Novo Gasto Fixo")
        with st.form("form_fixo", clear_on_submit=True):
            desc_fix = st.text_input("Descrição do Gasto")
            val_fix = st.number_input("Valor Mensal (R$)", min_value=0.01, step=10.0)
            if st.form_submit_button("Cadastrar Gasto Fixo"):
                if desc_fix:
                    adicionar_gasto_fixo(desc_fix, val_fix)
                    st.rerun()

with tab4:
    st.subheader("📈 Simulador de Crescimento Patrimonial (Juros Compostos)")
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        aporte_sim = st.number_input("Aporte Mensal Utilizado (R$)", value=float(meta_reserva_efetiva), step=50.0)
        anos_sim = st.slider("Horizonte de Tempo (Anos)", min_value=1, max_value=30, value=5)
    with col_sim2:
        taxa_anual_sim = st.slider("Rentabilidade Anual Estimada (%)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)

    taxa_mensal = (1 + taxa_anual_sim / 100) ** (1 / 12) - 1
    meses_total = anos_sim * 12
    
    lista_projecao = []
    montante_atual = 0.0
    total_investido = 0.0

    for m in range(1, meses_total + 1):
        montante_atual = (montante_atual + aporte_sim) * (1 + taxa_mensal)
        total_investido += aporte_sim
        if m % 12 == 0:
            lista_projecao.append({
                "Ano": m // 12,
                "Total Investido": total_investido,
                "Patrimônio Total": montante_atual,
                "Juros Acumulados": montante_atual - total_investido
            })

    if lista_projecao:
        df_proj = pd.DataFrame(lista_projecao)
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Valor Total Acumulado", f"+ R$ {montante_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        col_res2.metric("Total do Seu Bolso (Aporte)", f"R$ {total_investido:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        col_res3.metric("Rendimento (Juros)", f"+ R$ {(montante_atual - total_investido):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        st.divider()
        fig_invest = px.area(df_proj, x="Ano", y=["Patrimônio Total", "Total Investido"], title="Evolução Patrimonial Projetada")
        fig_invest.update_layout(
            paper_bgcolor="#111823",
            plot_bgcolor="#111823",
            font_color="#EAF0F7",
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_invest, use_container_width=True)

with tab5:
    st.subheader("📊 DRE Gerencial & Análise de Lucratividade")
    st.markdown("Demonstração financeira estruturada para avaliar o seu **Lucro Operacional Líquido** e a **Margem de Lucro** mensal.")

    receita_bruta = salario_a_input + vr_a_input
    custos_fixos_dre = total_fixos_a
    despesas_var_dre = total_gastos_variaveis
    lucro_operacional = receita_bruta - custos_fixos_dre - despesas_var_dre
    margem_lucro = (lucro_operacional / receita_bruta) * 100 if receita_bruta > 0 else 0.0

    col_dre1, col_dre2, col_dre3 = st.columns(3)
    col_dre1.metric("Receita Bruta Total (Salário + VR)", f"+ R$ {receita_bruta:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_dre2.metric("Lucro Líquido Operacional", f"{'+' if lucro_operacional >=0 else '-'} R$ {abs(lucro_operacional):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), delta=f"{margem_lucro:.1f}% Margem")
    
    reserva_acumulada_teorica = meta_reserva_efetiva * 6
    runway_meses = reserva_acumulada_teorica / total_fixos_a if total_fixos_a > 0 else 0
    col_dre3.metric("Runway de Segurança", f"{runway_meses:.1f} Meses", delta="Cobertura de Caixa")

    st.divider()

    dados_dre = [
        ["Conta / Indicador", "Valor (R$)", "% da Receita Bruta"],
        ["(+) Receita Bruta (Salário + VR)", f"+ R$ {receita_bruta:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), "100.0%"],
        ["(-) Custos Fixos (Aluguel + Fixos)", f"- R$ {custos_fixos_dre:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), f"{(custos_fixos_dre/receita_bruta)*100:.1f}%" if receita_bruta > 0 else "0.0%"],
        ["(-) Despesas Variáveis / Saídas", f"- R$ {despesas_var_dre:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), f"{(despesas_var_dre/receita_bruta)*100:.1f}%" if receita_bruta > 0 else "0.0%"],
        ["(=) LUCRO LÍQUIDO OPERACIONAL", f"{'+' if lucro_operacional >=0 else '-'} R$ {abs(lucro_operacional):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), f"{margem_lucro:.1f}%"]
    ]
    
    df_dre_tabela = pd.DataFrame(dados_dre[1:], columns=dados_dre[0])
    st.table(df_dre_tabela)

    st.markdown("#### 🔍 Diagnóstico de Oportunidade & Ladrões de Lucro")
    if not df_variaveis.empty:
        df_cat_analise = df_variaveis.groupby("categoria")["valor"].sum().reset_index()
        maior_gasto = df_cat_analise.loc[df_cat_analise["valor"].idxmax()]
        st.warning(f"⚠️ **Atenção ao maior ralo de caixa:** A categoria **{maior_gasto['categoria']}** consumiu **R$ {maior_gasto['valor']:,.2f}** do seu orçamento variável, impactando diretamente o seu potencial de lucro.".replace('.', '#').replace(',', '.').replace('#', ','))
    else:
        st.success("🟢 Nenhuma distorção crítica identificada nas despesas variáveis até o momento.")

with tab6:
    st.subheader("📑 Central de Relatórios em PDF")
    st.markdown("Gere relatórios executivos em PDF com divisão exata entre **Gastos Fixos** e **Despesas Variáveis / Perdas**.")
    
    pdf_bytes = gerar_relatorio_pdf(df_gastos_fixos, df_variaveis, salario_a_input, salario_b_input, aluguel_a, aluguel_b)
    
    st.download_button(
        label="📥 Baixar Relatório Completo em PDF (Gastos e Perdas Divididos)",
        data=pdf_bytes,
        file_name=f"Relatorio_Financeiro_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
