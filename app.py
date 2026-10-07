import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
from io import BytesIO
from supabase import create_client, Client

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
# PALETA
# -----------------------------------------------------------------------------
PALETA = {
    "fundo_principal":   "#0A0E14",
    "fundo_sidebar":     "#0D1219",
    "fundo_card":        "#131A23",
    "fundo_hover":       "#1B232E",
    "borda":             "#1F2937",
    "borda_acento":      "#3B82F6",
    "texto_principal":   "#E8EEF5",
    "texto_secundario":  "#8A95A5",
    "acento":            "#3B82F6",
    "acento_hover":      "#2563EB",
    "acento_glow":       "rgba(59,130,246,0.25)",
    "verde":             "#22C55E",
    "verde_bg":          "rgba(34,197,94,0.12)",
    "vermelho":          "#EF4444",
    "vermelho_bg":       "rgba(239,68,68,0.12)",
    "amarelo":           "#F59E0B",
    "amarelo_bg":        "rgba(245,158,11,0.12)",
    "roxo":              "#8B5CF6",
    "ciano":             "#06B6D4",
}

FONTES = {
    "titulo":     ("Segoe UI Semibold", 20),
    "subtitulo":  ("Segoe UI", 14),
    "corpo":      ("Segoe UI", 11),
    "numero":     ("Consolas", 30, "bold"),
    "legenda":    ("Segoe UI", 9),
}

st.markdown(f"""
<style>
    .stApp {{
        background:
            radial-gradient(circle at 15% 0%, rgba(59,130,246,0.06), transparent 45%),
            radial-gradient(circle at 85% 100%, rgba(139,92,246,0.05), transparent 45%),
            {PALETA["fundo_principal"]};
        color: {PALETA["texto_principal"]};
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }}
    html, body, [class*="css"] {{
        font-family: 'Segoe UI', 'Inter', sans-serif;
        color: {PALETA["texto_principal"]};
    }}
    h1 {{ color: {PALETA["texto_principal"]} !important; font-weight: 700 !important; letter-spacing: -0.5px !important; font-size: 30px !important; }}
    h2, h3 {{ color: {PALETA["texto_principal"]} !important; font-weight: 600 !important; letter-spacing: -0.3px !important; }}
    h4, h5 {{ color: {PALETA["texto_secundario"]} !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 1.2px; font-size: 11px !important; }}
    p, span, label {{ color: {PALETA["texto_principal"]}; }}
    [data-testid="stCaptionContainer"] {{ color: {PALETA["texto_secundario"]} !important; font-size: 12px !important; }}
    section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {PALETA["fundo_sidebar"]} 0%, {PALETA["fundo_principal"]} 100%); border-right: 1px solid {PALETA["borda"]}; }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{ color: {PALETA["texto_principal"]} !important; border-bottom: 1px solid {PALETA["borda"]}; padding-bottom: 10px; margin-bottom: 12px; }}
    section[data-testid="stSidebar"] hr {{ border-color: {PALETA["borda"]} !important; margin: 16px 0 !important; }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, {PALETA["fundo_card"]} 0%, {PALETA["fundo_sidebar"]} 100%);
        border: 1px solid {PALETA["borda"]}; border-radius: 14px;
        padding: 20px 22px !important; box-shadow: 0 4px 24px -8px rgba(0,0,0,0.5);
        transition: all 0.25s ease; position: relative; overflow: hidden;
    }}
    div[data-testid="stMetric"]::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, {PALETA["acento"]}, transparent); opacity: 0.6;
    }}
    div[data-testid="stMetric"]:hover {{
        border-color: {PALETA["borda_acento"]};
        box-shadow: 0 0 0 1px {PALETA["acento_glow"]}, 0 8px 32px -8px rgba(59,130,246,0.35);
        transform: translateY(-2px);
    }}
    div[data-testid="stMetric"] label {{ color: {PALETA["texto_secundario"]} !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{ color: {PALETA["texto_principal"]} !important; font-family: 'Consolas', 'JetBrains Mono', monospace !important; font-size: 26px !important; font-weight: 700 !important; letter-spacing: -0.5px; }}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{ font-size: 12px !important; font-weight: 600 !important; }}
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
        background: {PALETA["fundo_card"]} !important; color: {PALETA["texto_principal"]} !important;
        border: 1px solid {PALETA["borda"]} !important; border-radius: 10px !important;
        padding: 10px 18px !important; font-weight: 600 !important; font-size: 13px !important;
        transition: all 0.2s ease !important; box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
    .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {{
        background: {PALETA["acento"]} !important; border-color: {PALETA["acento"]} !important;
        color: #FFFFFF !important; box-shadow: 0 0 20px {PALETA["acento_glow"]}; transform: translateY(-1px);
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; background: {PALETA["fundo_card"]}; padding: 6px; border-radius: 12px; border: 1px solid {PALETA["borda"]}; flex-wrap: wrap; }}
    .stTabs [data-baseweb="tab"] {{ height: 40px; background: transparent !important; border-radius: 8px !important; color: {PALETA["texto_secundario"]} !important; font-weight: 600; font-size: 13px; padding: 0 16px; transition: all 0.2s ease; }}
    .stTabs [data-baseweb="tab"]:hover {{ color: {PALETA["texto_principal"]} !important; background: {PALETA["fundo_hover"]} !important; }}
    .stTabs [aria-selected="true"] {{ background: {PALETA["acento"]} !important; color: #FFFFFF !important; box-shadow: 0 0 16px {PALETA["acento_glow"]}; }}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}
    .stTextInput input, .stNumberInput input, .stDateInput input, div[data-baseweb="select"] > div {{
        background: {PALETA["fundo_principal"]} !important; color: {PALETA["texto_principal"]} !important;
        border: 1px solid {PALETA["borda"]} !important; border-radius: 10px !important; font-size: 13px !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, div[data-baseweb="select"] > div:focus-within {{
        border-color: {PALETA["acento"]} !important; box-shadow: 0 0 0 3px {PALETA["acento_glow"]} !important;
    }}
    label[data-testid="stWidgetLabel"] p {{ color: {PALETA["texto_secundario"]} !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }}
    div[data-testid="stExpander"] {{ background: {PALETA["fundo_card"]}; border: 1px solid {PALETA["borda"]} !important; border-radius: 12px !important; overflow: hidden; }}
    div[data-testid="stExpander"] summary {{ font-weight: 600 !important; color: {PALETA["texto_principal"]} !important; padding: 14px 18px !important; }}
    div[data-testid="stAlert"] {{ border-radius: 12px !important; border-left-width: 4px !important; font-size: 13px !important; padding: 12px 16px !important; }}
    div[data-testid="stAlert"][data-baseweb="notification"] {{ background: {PALETA["fundo_card"]} !important; }}
    .stDataFrame, div[data-testid="stTable"] {{ background: {PALETA["fundo_card"]} !important; border-radius: 12px !important; border: 1px solid {PALETA["borda"]} !important; overflow: hidden; }}
    div[data-testid="stTable"] table {{ background: {PALETA["fundo_card"]} !important; color: {PALETA["texto_principal"]} !important; border-collapse: collapse !important; }}
    div[data-testid="stTable"] thead tr th {{ background: {PALETA["fundo_sidebar"]} !important; color: {PALETA["texto_secundario"]} !important; text-transform: uppercase; letter-spacing: 1px; font-size: 11px !important; font-weight: 700 !important; border-bottom: 1px solid {PALETA["borda"]} !important; padding: 12px !important; }}
    div[data-testid="stTable"] tbody tr {{ border-bottom: 1px solid {PALETA["borda"]} !important; }}
    div[data-testid="stTable"] tbody tr:nth-child(even) {{ background: rgba(31, 41, 55, 0.25) !important; }}
    div[data-testid="stTable"] tbody td {{ color: {PALETA["texto_principal"]} !important; font-size: 13px !important; padding: 10px 12px !important; }}
    .stProgress > div > div > div > div {{ background: linear-gradient(90deg, {PALETA["acento"]}, {PALETA["ciano"]}) !important; border-radius: 999px !important; }}
    .stProgress > div > div > div {{ background: {PALETA["fundo_card"]} !important; border-radius: 999px !important; height: 8px !important; }}
    .stCheckbox label span, .stRadio label span {{ color: {PALETA["texto_principal"]} !important; font-size: 13px !important; }}
    hr {{ border: none !important; height: 1px !important; background: linear-gradient(90deg, transparent, {PALETA["borda"]}, transparent) !important; margin: 20px 0 !important; }}
    div[data-testid="stForm"] {{ background: {PALETA["fundo_card"]}; border: 1px solid {PALETA["borda"]}; border-radius: 14px; padding: 20px !important; }}
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {PALETA["fundo_principal"]}; }}
    ::-webkit-scrollbar-thumb {{ background: {PALETA["borda"]}; border-radius: 999px; }}
    .login-title {{ background: linear-gradient(90deg, {PALETA["acento"]}, {PALETA["ciano"]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSÃO
# -----------------------------------------------------------------------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
for i, m in enumerate(meses_nomes):
    key_nome = f"reserva_mes_{i+1}"
    if key_nome not in st.session_state:
        st.session_state[key_nome] = False

# -----------------------------------------------------------------------------
# LOGIN
# -----------------------------------------------------------------------------
if not st.session_state['autenticado']:
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-title" style="font-size:28px; font-weight:700; text-align:center; margin-bottom:10px;">🛡️ INVEST CONTROL PRO</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:14px; color:#8A95A5; text-align:center; margin-bottom:30px;">Sistema Integrado de Projeção Econômica & Acesso Seguro</div>', unsafe_allow_html=True)
        with st.form("form_login"):
            st.markdown("### Credenciais de Acesso")
            usuario = st.text_input("Usuário / Credencial", placeholder="Digite seu usuário...")
            senha = st.text_input("Senha de Acesso", type="password", placeholder="Digite sua senha...")
            st.markdown("---")
            btn_entrar = st.form_submit_button("Acessar Sistema", use_container_width=True)
            if btn_entrar:
                if usuario == "JOHN" and senha == "fgxv4VP0/*":
                    st.session_state['autenticado'] = True
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas.")
        st.info("💡 **Segurança Ativa:** Ambiente protegido.")
        st.stop()

# -----------------------------------------------------------------------------
# SUPABASE
# -----------------------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key) if url and key else None

supabase = init_supabase()

# =============================================================================
# FUNÇÕES — CDI
# =============================================================================
@st.cache_data(ttl=3600)
def obter_taxa_cdi_atual():
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4389/dados/ultimos/1?formato=json"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        dados = r.json()
        if dados and len(dados) > 0:
            return float(dados[-1]['valor'])
        return None
    except Exception:
        return None

@st.cache_data(ttl=3600)
def obter_historico_cdi(dias=30):
    try:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.4389/dados/ultimos/{dias}?formato=json"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        dados = r.json()
        if dados:
            df = pd.DataFrame(dados)
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
            df['valor'] = df['valor'].astype(float)
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def calcular_projecao_cdi(aporte_inicial, aporte_mensal, anos, percentual_cdi, cdi_anual):
    if percentual_cdi <= 0 or cdi_anual <= 0:
        return None
    cdi_mensal = (1 + cdi_anual / 100) ** (1 / 12) - 1
    taxa_mensal_efetiva = cdi_mensal * (percentual_cdi / 100)
    meses_total = anos * 12
    montante = float(aporte_inicial)
    total_investido = float(aporte_inicial)
    dados = []
    for mes in range(1, meses_total + 1):
        montante = montante * (1 + taxa_mensal_efetiva) + aporte_mensal
        total_investido += aporte_mensal
        if mes % 12 == 0:
            dados.append({
                "Ano": mes // 12,
                "Patrimônio Total": round(montante, 2),
                "Total Investido": round(total_investido, 2),
                "Juros Acumulados": round(montante - total_investido, 2),
            })
    return {
        "montante_final": round(montante, 2),
        "total_investido": round(total_investido, 2),
        "juros_totais": round(montante - total_investido, 2),
        "taxa_mensal_efetiva": round(taxa_mensal_efetiva * 100, 4),
        "dados_evolucao": pd.DataFrame(dados),
    }

def gerar_grafico_projecao_cdi(df_evolucao, aporte_inicial, aporte_mensal):
    df = df_evolucao.copy()
    df["Sem Rendimento"] = aporte_inicial + (df["Ano"] * 12 * aporte_mensal)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Ano"], y=df["Patrimônio Total"], mode="lines+markers",
        name="Com CDI", line=dict(color="#22C55E", width=3),
        fill="tozeroy", fillcolor="rgba(34,197,94,0.15)",
    ))
    fig.add_trace(go.Scatter(
        x=df["Ano"], y=df["Sem Rendimento"], mode="lines+markers",
        name="Sem Rendimento", line=dict(color="#EF4444", width=2, dash="dash"),
    ))
    fig.update_layout(
        paper_bgcolor="#151B23", plot_bgcolor="#151B23",
        font_color="#E6EDF3", xaxis_title="Anos", yaxis_title="Valor (R$)",
        legend_title="Cenário", margin=dict(l=20, r=20, t=30, b=20),
    )
    return fig

# =============================================================================
# FUNÇÕES DE DADOS
# =============================================================================
def _fmt_brl(v):
    try:
        return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def carregar_configuracoes():
    if supabase:
        try:
            res = supabase.table("configuracoes").select("*").eq("id", 1).execute()
            if res.data:
                return res.data[0]
        except: pass
    return {"aluguel_total": 1700.0, "salario_a": 2700.0, "salario_b": 2000.0,
            "vr_a": 700.0, "meta_reserva_mensal": 800.0,
            "aluguel_a_custom": 850.0, "aluguel_b_custom": 850.0, "usa_edicao_manual": False}

def salvar_configuracoes(aluguel, salario_a, salario_b, vr_a, meta_reserva, aluguel_a_custom, aluguel_b_custom, usa_edicao):
    if supabase:
        try:
            supabase.table("configuracoes").update({
                "aluguel_total": aluguel, "salario_a": salario_a, "salario_b": salario_b,
                "vr_a": vr_a, "meta_reserva_mensal": meta_reserva,
                "aluguel_a_custom": aluguel_a_custom, "aluguel_b_custom": aluguel_b_custom,
                "usa_edicao_manual": usa_edicao
            }).eq("id", 1).execute()
        except: pass

def carregar_gastos_fixos():
    if supabase:
        try:
            res = supabase.table("gastos_fixos").select("*").execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame([
        {"id": 1, "descricao": "Internet", "valor": 100.0},
        {"id": 2, "descricao": "Recarga celular", "valor": 30.0},
        {"id": 3, "descricao": "Corte de cabelo", "valor": 90.0},
        {"id": 4, "descricao": "Cartão de crédito", "valor": 49.0}
    ])

def adicionar_gasto_fixo(d, v):
    if supabase:
        try: supabase.table("gastos_fixos").insert({"descricao": d, "valor": v}).execute()
        except: pass

def remover_gasto_fixo(id_):
    if supabase:
        try: supabase.table("gastos_fixos").delete().eq("id", id_).execute()
        except: pass

def carregar_despesas_variaveis():
    if supabase:
        try:
            res = supabase.table("despesas_variaveis").select("*").order("data", desc=True).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['data'] = pd.to_datetime(df['data'])
                return df
        except: pass
    return pd.DataFrame(columns=["id", "data", "descricao", "categoria", "valor"])

def adicionar_despesa_variavel(data, descricao, categoria, valor):
    if supabase:
        try:
            data_formatada = str(data) if hasattr(data, "strftime") else data
            supabase.table("despesas_variaveis").insert({
                "data": data_formatada, "descricao": str(descricao).strip(),
                "categoria": str(categoria).strip(), "valor": float(valor)
            }).execute()
        except Exception as e:
            st.error(f"Erro: {e}")

def remover_despesa_variavel(id_):
    if supabase:
        try: supabase.table("despesas_variaveis").delete().eq("id", id_).execute()
        except: pass

def carregar_orcamento_mes(mes, ano):
    if supabase:
        try:
            res = supabase.table("orcamentos_mensais").select("*").eq("mes", mes).eq("ano", ano).execute()
            if res.data: return res.data[0]
            novo = {"mes": mes, "ano": ano, "orcamento": 0.0, "fechado": False}
            res_ins = supabase.table("orcamentos_mensais").insert(novo).execute()
            if res_ins.data: return res_ins.data[0]
        except: pass
    return {"mes": mes, "ano": ano, "orcamento": 0.0, "fechado": False}

def salvar_orcamento_mes(mes, ano, valor):
    if supabase:
        try:
            ex = supabase.table("orcamentos_mensais").select("id").eq("mes", mes).eq("ano", ano).execute()
            if ex.data:
                supabase.table("orcamentos_mensais").update({"orcamento": float(valor)}).eq("id", ex.data[0]["id"]).execute()
            else:
                supabase.table("orcamentos_mensais").insert({"mes": mes, "ano": ano, "orcamento": float(valor), "fechado": False}).execute()
        except: pass

def fechar_mes(mes, ano):
    if supabase:
        try: supabase.table("orcamentos_mensais").update({"fechado": True}).eq("mes", mes).eq("ano", ano).execute()
        except: pass

def carregar_despesas_por_mes(mes, ano):
    if supabase:
        try:
            res = supabase.table("despesas_variaveis").select("*").order("data", desc=True).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['data'] = pd.to_datetime(df['data'])
                return df[(df['data'].dt.month == mes) & (df['data'].dt.year == ano)]
        except: pass
    return pd.DataFrame(columns=["id", "data", "descricao", "categoria", "valor"])

def listar_meses_fechados():
    if supabase:
        try:
            res = supabase.table("orcamentos_mensais").select("*").order("ano", desc=True).order("mes", desc=True).execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "mes", "ano", "orcamento", "fechado"])

def salvar_simulacao_investimento(nome, aporte, anos, taxa, montante, investido, juros, cdi_taxa=None):
    if supabase:
        try:
            dados = {
                "nome": str(nome).strip(), "aporte_mensal": float(aporte),
                "anos": int(anos), "taxa_anual": float(taxa),
                "montante_final": float(montante), "total_investido": float(investido),
                "juros_totais": float(juros),
            }
            if cdi_taxa is not None:
                dados["cdi_taxa_utilizada"] = float(cdi_taxa)
            supabase.table("simulacoes_investimento").insert(dados).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar simulação: {e}")
            return False
    return False

def carregar_simulacoes_investimento():
    if supabase:
        try:
            res = supabase.table("simulacoes_investimento").select("*").order("criado_em", desc=True).execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "nome", "aporte_mensal", "anos", "taxa_anual",
                                  "montante_final", "total_investido", "juros_totais", "criado_em"])

def remover_simulacao_investimento(id_):
    if supabase:
        try: supabase.table("simulacoes_investimento").delete().eq("id", id_).execute()
        except: pass

# -----------------------------------------------------------------------------
# PDFs
# -----------------------------------------------------------------------------
def gerar_relatorio_pdf(df_fixos, df_variaveis, salario_a, salario_b, aluguel_a, aluguel_b):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TS', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#3B82F6'), spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle('HS', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1F2937'), spaceBefore=12, spaceAfter=6)
    normal_style = styles['Normal']

    story.append(Paragraph("<b>INVEST CONTROL PRO - RELATÓRIO FINANCEIRO</b>", title_style))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle('Sub', parent=normal_style, alignment=1, textColor=colors.HexColor('#8B949E'))))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>1. Resumo de Rendas</b>", heading_style))
    resumo_data = [["Descrição", "Valor (R$)"], ["Salário Pessoa A", f"R$ {salario_a:,.2f}"],
                   ["Salário Pessoa B", f"R$ {salario_b:,.2f}"],
                   ["Aluguel (A)", f"R$ {aluguel_a:,.2f}"], ["Aluguel (B)", f"R$ {aluguel_b:,.2f}"]]
    t_resumo = Table(resumo_data, colWidths=[250, 200])
    t_resumo.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
                                   ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
    story.append(t_resumo)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>2. Gastos Fixos</b>", heading_style))
    if not df_fixos.empty:
        fixos_data = [["Descrição", "Valor (R$)"]]
        for _, row in df_fixos.iterrows():
            fixos_data.append([str(row['descricao']), f"R$ {float(row['valor']):,.2f}"])
        t_fixos = Table(fixos_data, colWidths=[250, 200])
        t_fixos.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
                                     ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
        story.append(t_fixos)
    else:
        story.append(Paragraph("Nenhum gasto fixo.", normal_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>3. Despesas Variáveis</b>", heading_style))
    if not df_variaveis.empty:
        var_data = [["Data", "Descrição", "Categoria", "Valor (R$)"]]
        for _, row in df_variaveis.iterrows():
            data_str = row['data'].strftime('%d/%m/%Y') if pd.notnull(row['data']) else ""
            var_data.append([data_str, str(row['descricao']), str(row['categoria']), f"R$ {float(row['valor']):,.2f}"])
        t_vars = Table(var_data, colWidths=[80, 170, 110, 90])
        t_vars.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
        story.append(t_vars)
    else:
        story.append(Paragraph("Nenhuma despesa.", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_relatorio_mensal_pdf(mes, ano, df_mes, orcamento):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#3B82F6'), spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1F2937'), spaceBefore=12, spaceAfter=6)
    normal_style = styles['Normal']

    nome_mes = meses_nomes[mes - 1]
    story.append(Paragraph(f"<b>RELATÓRIO MENSAL — {nome_mes.upper()}/{ano}</b>", title_style))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle('S', parent=normal_style, alignment=1, textColor=colors.HexColor('#8B949E'))))
    story.append(Spacer(1, 15))

    total_gasto = df_mes["valor"].sum() if not df_mes.empty else 0.0
    saldo = orcamento - total_gasto
    pct = (total_gasto / orcamento * 100) if orcamento > 0 else 0

    resumo = [["Indicador", "Valor (R$)"], ["Orçamento", f"R$ {orcamento:,.2f}"],
              ["Total Gasto", f"R$ {total_gasto:,.2f}"], ["Saldo", f"R$ {saldo:,.2f}"],
              ["% Utilizado", f"{pct:.1f}%"]]
    t = Table(resumo, colWidths=[250, 200])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
                           ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Parâmetros Financeiros")
if st.sidebar.button("🔒 Sair / Bloquear", use_container_width=True):
    st.session_state['autenticado'] = False
    st.rerun()
st.sidebar.divider()

config = carregar_configuracoes()

st.sidebar.subheader("🔀 Cenário")
cenario = st.sidebar.radio("Cenário:", ["COM Participação de B", "SEM Participação de B"], index=0)
b_participa = (cenario == "COM Participação de B")

st.sidebar.divider()
st.sidebar.subheader("💵 Rendas e Custos")
aluguel_input = st.sidebar.number_input("Aluguel Total (R$)", value=float(config["aluguel_total"]), step=50.0)
salario_a_input = st.sidebar.number_input("Salário A (R$)", value=float(config["salario_a"]), step=100.0)
vr_a_input = st.sidebar.number_input("VR A (R$)", value=float(config["vr_a"]), step=50.0)
if b_participa:
    salario_b_input = st.sidebar.number_input("Salário B (R$)", value=float(config["salario_b"]), step=100.0)
else:
    salario_b_input = 0.0
    st.sidebar.warning("⚠️ B não participa.")
meta_reserva_input = st.sidebar.number_input("Meta Reserva (R$)", value=float(config["meta_reserva_mensal"]), step=50.0)

st.sidebar.divider()
st.sidebar.subheader("✏ Edição Manual")
edicao_manual = st.sidebar.checkbox("Habilitar edição manual", value=bool(config.get("usa_edicao_manual", False)))

aluguel_a_input = None
aluguel_b_input = None
val_a_db = float(config.get("aluguel_a_custom", aluguel_input * 0.5))
val_b_db = float(config.get("aluguel_b_custom", aluguel_input * 0.5))

if edicao_manual and b_participa:
    quem = st.sidebar.radio("Ajustar:", ["Pessoa A", "Pessoa B"], index=0)
    if quem == "Pessoa A":
        aluguel_a_input = st.sidebar.number_input("A (R$)", 0.0, float(aluguel_input), val_a_db, 25.0)
        aluguel_b_input = max(0.0, aluguel_input - aluguel_a_input)
        st.sidebar.info(f"B: R$ {aluguel_b_input:,.2f}")
    else:
        aluguel_b_input = st.sidebar.number_input("B (R$)", 0.0, float(aluguel_input), val_b_db, 25.0)
        aluguel_a_input = max(0.0, aluguel_input - aluguel_b_input)
        st.sidebar.info(f"A: R$ {aluguel_a_input:,.2f}")
else:
    aluguel_a_input = val_a_db
    aluguel_b_input = val_b_db

if st.sidebar.button("💾 Salvar Parâmetros"):
    a_save = aluguel_a_input if edicao_manual else aluguel_input * 0.5
    b_save = aluguel_b_input if edicao_manual else aluguel_input * 0.5
    salvar_configuracoes(aluguel_input, salario_a_input, salario_b_input, vr_a_input, meta_reserva_input, a_save, b_save, edicao_manual)
    st.sidebar.success("Salvo!"); st.rerun()

# -----------------------------------------------------------------------------
# ENGINE
# -----------------------------------------------------------------------------
if b_participa:
    if edicao_manual and aluguel_a_input is not None:
        aluguel_a, aluguel_b = aluguel_a_input, aluguel_b_input
        prop_a = aluguel_a / aluguel_input if aluguel_input > 0 else 0.5
        prop_b = aluguel_b / aluguel_input if aluguel_input > 0 else 0.5
    else:
        if (salario_a_input + salario_b_input) > 0:
            rt = salario_a_input + salario_b_input
            prop_a = salario_a_input / rt
            prop_b = salario_b_input / rt
            aluguel_a = aluguel_input * prop_a
            aluguel_b = aluguel_input * prop_b
        else:
            prop_a, prop_b = 1.0, 0.0
            aluguel_a, aluguel_b = aluguel_input, 0.0
else:
    prop_a, prop_b = 1.0, 0.0
    aluguel_a, aluguel_b = aluguel_input, 0.0

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
# CORPO
# -----------------------------------------------------------------------------
st.title("📊 Painel de Projeção Econômica & Controle")
st.caption(f"Cenário: **{cenario}** | VR: R$ {vr_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário A", f"+ R$ {salario_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col2.metric("Aluguel A", f"- R$ {aluguel_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col3.metric("Gastos Fixos", f"- R$ {total_fixos_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col4.metric("Reserva", f"- R$ {meta_reserva_efetiva:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📌 Planejamento", "💳 Gastos Diários", "⚙ Custos Fixos",
    "📈 Simulador & CDI", "📊 DRE", "📑 Relatórios PDF",
    "📅 Relatório Mensal", "✂️ Cortes", "🚀 Prosperidade"
])

# =========================================================
# TAB 1
# =========================================================
with tab1:
    st.subheader("🏠 Divisão do Aluguel")
    c1, c2, c3 = st.columns(3)
    c1.metric("Salário A", f"R$ {salario_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    c2.metric("Salário B", f"R$ {salario_b_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',') if b_participa else "R$ 0,00")
    c3.metric("Aluguel", f"R$ {aluguel_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    cv1, cv2 = st.columns(2)
    cv1.info(f"👤 A: R$ **{aluguel_a:,.2f}** ({prop_a*100:.1f}%)".replace('.', '#').replace(',', '.').replace('#', ','))
    if b_participa:
        cv2.success(f"👥 B: R$ **{aluguel_b:,.2f}** ({prop_b*100:.1f}%)".replace('.', '#').replace(',', '.').replace('#', ','))
    else:
        cv2.warning("⚠️ B sem participação.")
    st.divider()
    cl, cr = st.columns(2)
    with cl:
        st.subheader("💡 Distribuição")
        dc = {"Categoria": ["Aluguel", "Fixos", "Reserva", "Variável"],
              "Valor": [aluguel_a, total_outros_fixos_a, meta_reserva_efetiva, max(0.0, saldo_para_variaveis)]}
        fig = px.pie(pd.DataFrame(dc), names="Categoria", values="Valor", hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3")
        st.plotly_chart(fig, use_container_width=True)
    with cr:
        st.subheader("🛡 Reserva Anual")
        st.write(f"**Aporte:** R$ {meta_reserva_efetiva:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        st.write(f"**Meta Anual:** R$ {meta_reserva_efetiva * 12:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        cols_grid = st.columns(4)
        mc = 0
        for i, nm in enumerate(meses_nomes):
            with cols_grid[i % 4]:
                if st.checkbox(f"{i+1}. {nm}", key=f"reserva_mes_{i+1}"):
                    mc += 1
                    st.markdown("<span style='color:#22C55E; font-size:12px;'>● pago</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#F59E0B; font-size:12px;'>⏳ pend.</span>", unsafe_allow_html=True)
        pct = mc / 12.0
        st.progress(pct)
        st.markdown(f"**{mc}/12 meses ({pct*100:.1f}%)**")

# =========================================================
# TAB 2
# =========================================================
with tab2:
    st.subheader("🛒 Despesas Variáveis")
    c1, c2, c3 = st.columns(3)
    c1.metric("Orçamento", f"R$ {saldo_para_variaveis:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    c2.metric("Gasto", f"- R$ {total_gastos_variaveis:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    c3.metric("Saldo", f"{'+' if saldo_caixa_restante>=0 else '-'} R$ {abs(saldo_caixa_restante):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    st.divider()
    with st.expander("➕ Nova Despesa", expanded=True):
        with st.form("form_desp", clear_on_submit=True):
            fc1, fc2, fc3, fc4 = st.columns([2, 3, 2, 2])
            data_e = fc1.date_input("Data")
            desc_e = fc2.text_input("Descrição")
            cat_e = fc3.selectbox("Categoria", ["Lazer / Passeios", "Farmácia / Saúde", "Vestuário", "Imprevistos", "Outros"])
            val_e = fc4.number_input("Valor (R$)", min_value=0.01, step=10.0)
            if st.form_submit_button("Lançar"):
                if desc_e:
                    adicionar_despesa_variavel(data_e, desc_e, cat_e, val_e)
                    st.success("Lançado!"); st.rerun()
                else: st.error("Informe descrição.")
    if not df_variaveis.empty:
        for _, r in df_variaveis.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1])
            c1.write(r["data"].strftime("%d/%m/%Y"))
            c2.write(r["descricao"]); c3.write(r["categoria"])
            c4.write(f"- R$ {r['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
            if c5.button("🗑️", key=f"dv_{r['id']}"):
                remover_despesa_variavel(r["id"]); st.rerun()

# =========================================================
# TAB 3
# =========================================================
with tab3:
    st.subheader("📋 Custos Fixos")
    c1, c2 = st.columns([2, 1])
    with c1:
        if not df_gastos_fixos.empty:
            for _, r in df_gastos_fixos.iterrows():
                cf1, cf2, cf3 = st.columns([3, 2, 1])
                cf1.write(f"**{r['descricao']}**")
                cf2.write(f"- R$ {r['valor']:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
                if cf3.button("Excluir", key=f"df_{r['id']}"):
                    remover_gasto_fixo(r["id"]); st.rerun()
    with c2:
        st.write("#### Adicionar")
        with st.form("form_fix", clear_on_submit=True):
            desc_f = st.text_input("Descrição")
            val_f = st.number_input("Valor (R$)", min_value=0.01, step=10.0)
            if st.form_submit_button("Cadastrar"):
                if desc_f:
                    adicionar_gasto_fixo(desc_f, val_f); st.rerun()

# =========================================================
# TAB 4 — SIMULADOR + CDI
# =========================================================
with tab4:
    st.subheader("📈 Simulador de Investimento — Juros Compostos & CDI")
    st.markdown("Simule cenários com **taxa fixa** ou **atrelados ao CDI**, salve e compare.")

    cdi_atual = obter_taxa_cdi_atual()
    col_info1, col_info2 = st.columns([1, 3])
    with col_info1:
        st.metric("📊 CDI Atual (a.a.)", f"{cdi_atual:.2f}%" if cdi_atual else "—")
    with col_info2:
        if cdi_atual:
            st.success(f"CDI do Banco Central (SGS 4389). Atualizado a cada 1h.", icon="✅")
        else:
            st.warning("CDI indisponível. Informe manualmente abaixo.", icon="⚠️")
    st.divider()

    modo_taxa = st.radio(
        "Modalidade:",
        ["🎯 Taxa fixa (% ao ano)", "📊 Atrelado ao CDI (% do CDI)"],
        horizontal=True, key="modo_taxa_sim"
    )

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        aporte_sim = st.number_input("Aporte Mensal (R$)", value=float(meta_reserva_efetiva), step=50.0, key="aporte_sim")
        anos_sim = st.slider("Prazo (Anos)", 1, 30, 5, key="anos_sim")
    with col_s2:
        if modo_taxa.startswith("🎯"):
            taxa_anual_sim = st.slider("Rentabilidade (% a.a.)", 1.0, 25.0, 10.0, 0.5, key="taxa_sim")
            cdi_ref = None
            nome_sim = st.text_input("Nome para salvar", placeholder="Ex: Cenário conservador", key="nome_sim_fixa")
        else:
            cdi_manual = st.number_input("CDI considerada (% a.a.) — 0 = usar atual",
                                          min_value=0.0, max_value=30.0,
                                          value=float(cdi_atual) if cdi_atual else 13.65,
                                          step=0.25, key="cdi_manual")
            percentual_cdi_sim = st.slider("% do CDI contratado", 80, 150, 100, 5, key="pct_cdi_sim")
            cdi_ref = cdi_manual if cdi_manual > 0 else (cdi_atual if cdi_atual else 13.65)
            taxa_anual_sim = cdi_ref * (percentual_cdi_sim / 100)
            st.info(f"**Taxa efetiva: {taxa_anual_sim:.2f}% a.a.** (CDI {cdi_ref:.2f}% × {percentual_cdi_sim}%)")
            nome_sim = st.text_input("Nome para salvar", placeholder="Ex: CDB 110% CDI", key="nome_sim_cdi")

    taxa_mensal = (1 + taxa_anual_sim / 100) ** (1 / 12) - 1
    meses_total = anos_sim * 12
    lista_proj = []
    montante_atual = 0.0
    total_investido = 0.0
    for m in range(1, meses_total + 1):
        montante_atual = (montante_atual + aporte_sim) * (1 + taxa_mensal)
        total_investido += aporte_sim
        if m % 12 == 0:
            lista_proj.append({"Ano": m // 12, "Total Investido": total_investido,
                                "Patrimônio Total": montante_atual,
                                "Juros Acumulados": montante_atual - total_investido})

    if lista_proj:
        df_proj = pd.DataFrame(lista_proj)
        juros_totais = montante_atual - total_investido

        cr1, cr2, cr3 = st.columns(3)
        cr1.metric("Montante Final", f"+ R$ {montante_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        cr2.metric("Total Investido", f"R$ {total_investido:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        cr3.metric("Juros", f"+ R$ {juros_totais:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

        st.markdown("")
        cb1, cb2 = st.columns([1, 3])
        with cb1:
            if st.button("💾 Salvar simulação", use_container_width=True, key="btn_salvar_sim"):
                if not nome_sim.strip():
                    st.warning("Dê um nome à simulação.")
                else:
                    ok = salvar_simulacao_investimento(nome_sim, aporte_sim, anos_sim, taxa_anual_sim,
                                                        montante_atual, total_investido, juros_totais, cdi_taxa=cdi_ref)
                    if ok:
                        st.success(f"'{nome_sim}' salva!"); st.rerun()

        st.divider()
        if modo_taxa.startswith("📊") and cdi_atual:
            fig_invest = gerar_grafico_projecao_cdi(df_proj, 0.0, aporte_sim)
            st.plotly_chart(fig_invest, use_container_width=True)
        else:
            fig_invest = px.area(df_proj, x="Ano", y=["Patrimônio Total", "Total Investido"],
                                  title="Evolução Patrimonial")
            fig_invest.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3")
            st.plotly_chart(fig_invest, use_container_width=True)

    st.divider()

    if modo_taxa.startswith("📊") and cdi_atual:
        st.markdown("### 🎯 Comparativo de Produtos de Renda Fixa")
        produtos = [
            ("Poupança", 70, "#8A95A5"), ("Tesouro Selic", 100, "#3B82F6"),
            ("CDB 100% CDI", 100, "#06B6D4"), ("CDB 110% CDI", 110, "#22C55E"),
            ("LCI/LCA 90% CDI", 90, "#7C3AED"), ("CDB 120% CDI", 120, "#F59E0B"),
        ]
        resultados = []
        for nome_p, pct, cor in produtos:
            proj = calcular_projecao_cdi(0.0, aporte_sim, anos_sim, pct, cdi_ref)
            if proj:
                resultados.append({"Produto": nome_p, "Percentual do CDI": f"{pct}%",
                                    "Taxa Efetiva (% a.a.)": round(cdi_ref * pct / 100, 2),
                                    "Montante Final": proj["montante_final"],
                                    "Juros Totais": proj["juros_totais"], "_cor": cor})
        if resultados:
            df_prod = pd.DataFrame(resultados)
            df_show = df_prod.drop(columns=["_cor"]).copy()
            df_show["Montante Final"] = df_show["Montante Final"].apply(_fmt_brl)
            df_show["Juros Totais"] = df_show["Juros Totais"].apply(_fmt_brl)
            df_show["Taxa Efetiva (% a.a.)"] = df_show["Taxa Efetiva (% a.a.)"].apply(lambda v: f"{v:.2f}%")
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            fig_cmp = px.bar(df_prod, x="Produto", y="Montante Final",
                             color="Produto", color_discrete_sequence=[r["_cor"] for r in resultados],
                             title=f"Comparativo (CDI {cdi_ref:.2f}% a.a.)")
            fig_cmp.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                   font_color="#E6EDF3", showlegend=False, xaxis_tickangle=-25)
            st.plotly_chart(fig_cmp, use_container_width=True)

    st.divider()

    if cdi_atual:
        with st.expander("📉 Histórico do CDI (30 dias)"):
            df_hist_cdi = obter_historico_cdi(30)
            if not df_hist_cdi.empty:
                fig_cdi = px.line(df_hist_cdi, x="data", y="valor", markers=True,
                                   title="Taxa CDI — últimos 30 dias úteis")
                fig_cdi.update_traces(line_color="#22C55E")
                fig_cdi.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                       font_color="#E6EDF3", height=260)
                st.plotly_chart(fig_cdi, use_container_width=True)
                st.caption(f"Fonte: BCB SGS 4389 · Média: {df_hist_cdi['valor'].mean():.2f}% · "
                            f"Máx: {df_hist_cdi['valor'].max():.2f}% · Mín: {df_hist_cdi['valor'].min():.2f}%")

    st.divider()

    st.markdown("### 📂 Simulações Salvas")
    df_sims = carregar_simulacoes_investimento()

    if df_sims.empty:
        st.info("Nenhuma simulação salva. Ajuste e clique em **💾 Salvar simulação**.")
    else:
        melhor = df_sims.loc[df_sims["montante_final"].idxmax()]
        st.markdown(
            f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
            f"border-radius:12px;padding:14px 18px;margin-bottom:12px;'>"
            f"<b style='color:{PALETA['texto_principal']};'>📊 {len(df_sims)} simulações salvas</b> · "
            f"<span style='color:{PALETA['texto_secundario']};'>Melhor: "
            f"<b style='color:{PALETA['verde']};'>{melhor['nome']}</b> ({_fmt_brl(melhor['montante_final'])})</span></div>",
            unsafe_allow_html=True)

        cols_disp = ["nome", "aporte_mensal", "anos", "taxa_anual",
                      "montante_final", "total_investido", "juros_totais", "criado_em"]
        if "cdi_taxa_utilizada" in df_sims.columns:
            cols_disp.insert(-1, "cdi_taxa_utilizada")
        df_show = df_sims[cols_disp].copy()
        df_show["aporte_mensal"] = df_show["aporte_mensal"].apply(_fmt_brl)
        df_show["taxa_anual"] = df_show["taxa_anual"].apply(lambda v: f"{v:.2f}%")
        df_show["montante_final"] = df_show["montante_final"].apply(_fmt_brl)
        df_show["total_investido"] = df_show["total_investido"].apply(_fmt_brl)
        df_show["juros_totais"] = df_show["juros_totais"].apply(_fmt_brl)
        df_show["anos"] = df_show["anos"].apply(lambda v: f"{int(v)} anos")
        df_show["criado_em"] = pd.to_datetime(df_show["criado_em"]).dt.strftime("%d/%m/%Y %H:%M")
        if "cdi_taxa_utilizada" in df_show.columns:
            df_show["cdi_taxa_utilizada"] = df_show["cdi_taxa_utilizada"].apply(lambda v: f"{v:.2f}%" if pd.notnull(v) else "—")
            df_show.columns = ["Nome", "Aporte", "Prazo", "Taxa", "Montante", "Investido", "Juros", "CDI Base", "Data"]
        else:
            df_show.columns = ["Nome", "Aporte", "Prazo", "Taxa", "Montante", "Investido", "Juros", "Data"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)

        fig_cmp2 = px.bar(df_sims.sort_values("montante_final"), x="montante_final", y="nome",
                           orientation="h", color="montante_final",
                           color_continuous_scale=["#3B82F6", "#22C55E"],
                           labels={"montante_final": "Montante (R$)", "nome": ""})
        fig_cmp2.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                font_color="#E6EDF3", showlegend=False, coloraxis_showscale=False,
                                height=max(200, 60 * len(df_sims)))
        st.plotly_chart(fig_cmp2, use_container_width=True)

        st.markdown("#### 🗑️ Excluir")
        cols_del = st.columns(min(4, len(df_sims)))
        for i, (_, s) in enumerate(df_sims.iterrows()):
            with cols_del[i % 4]:
                if st.button(f"🗑️ {s['nome'][:20]}", key=f"del_sim_{s['id']}", use_container_width=True):
                    remover_simulacao_investimento(s["id"]); st.rerun()

# =========================================================
# TAB 5
# =========================================================
with tab5:
    st.subheader("📊 DRE Gerencial")
    receita = salario_a_input + vr_a_input
    lucro = receita - total_fixos_a - total_gastos_variaveis
    margem = (lucro / receita * 100) if receita > 0 else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Receita", f"+ R$ {receita:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    c2.metric("Lucro", f"{'+' if lucro>=0 else '-'} R$ {abs(lucro):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
               delta=f"{margem:.1f}%")
    runway = (meta_reserva_efetiva * 6) / total_fixos_a if total_fixos_a > 0 else 0
    c3.metric("Runway", f"{runway:.1f} meses")
    st.divider()
    dados = [
        ["Conta", "Valor (R$)", "% Receita"],
        ["(+) Receita Bruta", f"+ R$ {receita:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), "100.0%"],
        ["(-) Custos Fixos", f"- R$ {total_fixos_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
         f"{(total_fixos_a/receita)*100:.1f}%" if receita > 0 else "0%"],
        ["(-) Despesas Variáveis", f"- R$ {total_gastos_variaveis:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
         f"{(total_gastos_variaveis/receita)*100:.1f}%" if receita > 0 else "0%"],
        ["(=) LUCRO LÍQUIDO", f"{'+' if lucro>=0 else '-'} R$ {abs(lucro):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
         f"{margem:.1f}%"]
    ]
    st.table(pd.DataFrame(dados[1:], columns=dados[0]))

# =========================================================
# TAB 6
# =========================================================
with tab6:
    st.subheader("📑 Relatórios PDF")
    pdf_bytes = gerar_relatorio_pdf(df_gastos_fixos, df_variaveis, salario_a_input, salario_b_input, aluguel_a, aluguel_b)
    st.download_button("📥 Baixar Relatório Completo", data=pdf_bytes,
                        file_name=f"Relatorio_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf", use_container_width=True)

# =========================================================
# TAB 7
# =========================================================
with tab7:
    st.subheader("📅 Relatório Mensal")
    hoje = datetime.now()
    cm1, cm2, cm3 = st.columns(3)
    mes_sel = cm1.selectbox("Mês", list(range(1, 13)), index=hoje.month - 1,
                             format_func=lambda x: meses_nomes[x - 1])
    ano_sel = cm2.number_input("Ano", 2020, 2100, hoje.year)
    orc = carregar_orcamento_mes(mes_sel, ano_sel)
    orc_val = float(orc.get("orcamento", 0.0) or 0.0)
    cm3.success("🟢 Aberto") if not orc.get("fechado") else cm3.error("🔒 Fechado")
    st.divider()
    with st.expander("💼 Definir Orçamento", expanded=(orc_val == 0.0)):
        novo = st.number_input("Orçamento (R$)", 0.0, value=orc_val, step=50.0, key=f"orc_{mes_sel}_{ano_sel}")
        c1, c2 = st.columns(2)
        if c1.button("💾 Salvar"):
            salvar_orcamento_mes(mes_sel, ano_sel, novo); st.rerun()
        if c2.button("🔒 Fechar Mês"):
            fechar_mes(mes_sel, ano_sel); st.rerun()
    df_mes = carregar_despesas_por_mes(mes_sel, ano_sel)
    tg = df_mes["valor"].sum() if not df_mes.empty else 0.0
    pct = (tg / orc_val * 100) if orc_val > 0 else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Orçamento", _fmt_brl(orc_val))
    c2.metric("Gasto", _fmt_brl(tg))
    c3.metric("Saldo", _fmt_brl(orc_val - tg))
    c4.metric("% Uso", f"{pct:.1f}%")
    if orc_val > 0:
        st.progress(min(pct / 100, 1.0))
    st.divider()
    if not df_mes.empty:
        df_show = df_mes.copy()
        df_show["data"] = df_show["data"].dt.strftime("%d/%m/%Y")
        df_show = df_show[["data", "descricao", "categoria", "valor"]]
        df_show.columns = ["Data", "Descrição", "Categoria", "Valor"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    pdf_m = gerar_relatorio_mensal_pdf(mes_sel, ano_sel, df_mes, orc_val)
    st.download_button(f"📥 Relatório {meses_nomes[mes_sel-1]}", data=pdf_m,
                        file_name=f"Relatorio_{meses_nomes[mes_sel-1]}_{ano_sel}.pdf",
                        mime="application/pdf", use_container_width=True)

# =========================================================
# TAB 8 — CORTES
# =========================================================
with tab8:
    st.subheader("✂️ Cortes Inteligentes")
    receita_c = salario_a_input + vr_a_input

    BENCH = {"Lazer / Passeios": 8.0, "Farmácia / Saúde": 5.0, "Vestuário": 5.0,
             "Imprevistos": 10.0, "Outros": 5.0, "Internet": 3.0, "Recarga celular": 2.0,
             "Corte de cabelo": 2.0, "Cartão de crédito": 10.0, "Alimentação": 15.0,
             "Transporte": 10.0, "Moradia": 30.0}

    sug = []
    if not df_variaveis.empty:
        for cat, val in df_variaveis.groupby("categoria")["valor"].sum().items():
            peso = (val / receita_c) * 100 if receita_c > 0 else 0
            b = BENCH.get(cat, 8.0)
            if peso > b:
                ex = val - (receita_c * b / 100)
                cs = ex * 0.5
                sug.append({"categoria": f"💳 {cat}", "cat": cat, "tipo": "Variável",
                             "atual": val, "peso": round(peso, 2), "bench": b,
                             "corte": round(cs, 2), "eco_anual": round(cs * 12, 2)})
    if not df_gastos_fixos.empty:
        for cat, val in df_gastos_fixos.groupby("descricao")["valor"].sum().items():
            peso = (val / receita_c) * 100 if receita_c > 0 else 0
            b = BENCH.get(cat, 5.0)
            if peso > b:
                ex = val - (receita_c * b / 100)
                cs = ex * 0.4
                sug.append({"categoria": f"🔧 {cat}", "cat": cat, "tipo": "Fixo",
                             "atual": val, "peso": round(peso, 2), "bench": b,
                             "corte": round(cs, 2), "eco_anual": round(cs * 12, 2)})

    if sug:
        df_sug = pd.DataFrame(sug).sort_values("eco_anual", ascending=False).reset_index(drop=True)
        df_sug["prioridade"] = df_sug.index + 1
        tot_m = df_sug["corte"].sum()
        tot_a = df_sug["eco_anual"].sum()

        # Meta de poupança
        meta_ideal = receita_c * 0.20
        poup_atu = meta_reserva_efetiva
        falta = max(0, meta_ideal - poup_atu)
        c1, c2, c3 = st.columns(3)
        c1.metric("Meta Ideal (20%)", _fmt_brl(meta_ideal))
        c2.metric("Poupança Atual", _fmt_brl(poup_atu))
        c3.metric("Falta", _fmt_brl(falta), delta_color="inverse" if falta > 0 else "normal")
        st.divider()

        st.markdown("### 📊 Quanto reduzir por categoria")
        df_show = df_sug[["cat", "tipo", "atual", "bench", "peso", "corte", "eco_anual"]].copy()
        df_show.columns = ["Categoria", "Tipo", "Atual (R$)", "Benchmark (%)",
                            "Peso Atual (%)", "Corte (R$/mês)", "Economia (R$/ano)"]
        for col in ["Atual (R$)", "Corte (R$/mês)", "Economia (R$/ano)"]:
            df_show[col] = df_show[col].apply(_fmt_brl)
        df_show["Benchmark (%)"] = df_show["Benchmark (%)"].apply(lambda v: f"{v:.0f}%")
        df_show["Peso Atual (%)"] = df_show["Peso Atual (%)"].apply(lambda v: f"{v:.1f}%")
        st.dataframe(df_show, use_container_width=True, hide_index=True)

        st.markdown(
            f"<div style='background:{PALETA['fundo_card']};border-left:4px solid {PALETA['acento']};"
            f"border-radius:10px;padding:14px 18px;margin-top:10px;'>"
            f"<b style='color:{PALETA['texto_principal']};'>💡 Total a reduzir:</b> "
            f"<b style='color:{PALETA['verde']};font-size:16px;'>{_fmt_brl(tot_m)}/mês</b> "
            f"({_fmt_brl(tot_a)}/ano)</div>", unsafe_allow_html=True)

        st.divider()

        for _, s in df_sug.iterrows():
            cor = "#EF4444" if s['prioridade'] <= 2 else ("#F59E0B" if s['prioridade'] <= 4 else "#3B82F6")
            vi = receita_c * s['bench'] / 100
            rv = max(0, s['atual'] - vi)
            rp = (rv / s['atual'] * 100) if s['atual'] > 0 else 0
            st.markdown(
                f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
                f"border-left:4px solid {cor};border-radius:10px;padding:14px 18px;margin-bottom:10px;'>"
                f"<div style='display:flex;justify-content:space-between;'>"
                f"<b style='color:{cor};'>#{int(s['prioridade'])} — {s['categoria']}</b>"
                f"<b style='color:{PALETA['verde']};'>Reduzir: {_fmt_brl(rv)} ({rp:.1f}%)</b></div>"
                f"<div style='color:{PALETA['texto_secundario']};font-size:12px;margin-top:6px;'>"
                f"Atual: <b style='color:{PALETA['texto_principal']};'>{_fmt_brl(s['atual'])}</b> → "
                f"Ideal: <b>{_fmt_brl(vi)}</b> · Peso: <b style='color:{cor};'>{s['peso']}%</b> "
                f"(benchmark: {s['bench']}%)</div></div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📄 Exportar Plano")
        # PDF simplificado
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        story = []
        styles = getSampleStyleSheet()
        story.append(Paragraph("<b>PLANO DE CORTES INTELIGENTES</b>",
                                ParagraphStyle('T', parent=styles['Heading1'], fontSize=18,
                                               textColor=colors.HexColor('#3B82F6'), alignment=1)))
        story.append(Spacer(1, 15))
        data = [["#", "Categoria", "Atual", "Corte/mês", "Economia/ano"]]
        for _, s in df_sug.iterrows():
            data.append([str(int(s['prioridade'])), str(s['cat']),
                         f"R$ {s['atual']:,.2f}", f"R$ {s['corte']:,.2f}", f"R$ {s['eco_anual']:,.2f}"])
        tv = Table(data, colWidths=[25, 130, 100, 100, 120])
        tv.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36')),
                                ('FONTSIZE', (0, 0), (-1, -1), 9)]))
        story.append(tv)
        doc.build(story)
        buffer.seek(0)
        st.download_button("📥 Baixar Plano de Cortes em PDF", data=buffer.getvalue(),
                            file_name=f"Plano_Cortes_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf", use_container_width=True)
    else:
        st.success("🟢 Nenhuma categoria acima do benchmark saudável!")

# =========================================================
# TAB 9 — PROSPERIDADE
# =========================================================
with tab9:
    st.subheader("🚀 Painel de Prosperidade")

    secao = st.selectbox("Seção:",
        ["💎 Patrimônio (Net Worth)", "🔥 Calculadora FIRE",
         "🧠 Diagnóstico Financeiro", "🛡️ Checklist de Proteção"],
        key="secao_prosp")

    st.divider()

    if secao == "💎 Patrimônio (Net Worth)":
        st.markdown("### 💎 Patrimônio Líquido")
        total_ativos = meta_reserva_efetiva * 12
        st.metric("Patrimônio Estimado (Reserva Anual)", _fmt_brl(total_ativos))

    elif secao == "🔥 Calculadora FIRE":
        st.markdown("### 🔥 Independência Financeira")
        c1, c2 = st.columns(2)
        with c1:
            gasto_m = st.number_input("Gasto mensal (R$)", value=float(total_fixos_a + total_gastos_variaveis), step=100.0)
            pat_a = st.number_input("Patrimônio atual (R$)", value=0.0, step=1000.0)
        with c2:
            ap_m = st.number_input("Aporte mensal (R$)", value=float(meta_reserva_efetiva), step=100.0)
            taxa_r = st.slider("Taxa retirada (%)", 3.0, 6.0, 4.0, 0.5) / 100

        if gasto_m > 0:
            num_mag = (gasto_m * 12) / taxa_r
            falta_f = max(0, num_mag - pat_a)
            anos_f = None
            if ap_m > 0 and falta_f > 0:
                r = 0.07 / 12
                n = 0
                saldo = pat_a
                while saldo < num_mag and n < 1200:
                    saldo = saldo * (1 + r) + ap_m
                    n += 1
                anos_f = n / 12
            c1, c2, c3 = st.columns(3)
            c1.metric("💎 Número Mágico", _fmt_brl(num_mag))
            c2.metric("📉 Falta", _fmt_brl(falta_f))
            c3.metric("⏱️ Tempo", f"{anos_f:.1f} anos" if anos_f else "—")
            st.markdown(
                f"<div style='background:{PALETA['fundo_card']};border-left:4px solid {PALETA['roxo']};"
                f"border-radius:12px;padding:18px 22px;margin-top:16px;'>"
                f"<b style='color:{PALETA['texto_principal']};font-size:15px;'>"
                f"🎉 Com {_fmt_brl(num_mag)} investidos você retira {_fmt_brl(num_mag*taxa_r/12)}/mês para sempre.</b></div>",
                unsafe_allow_html=True)

    elif secao == "🧠 Diagnóstico Financeiro":
        st.markdown("### 🧠 Nota Financeira")
        receita = salario_a_input + vr_a_input
        if receita > 0:
            taxa_poup = (receita - total_fixos_a - total_gastos_variaveis) / receita
            meses_res = (meta_reserva_efetiva * 6) / total_fixos_a if total_fixos_a > 0 else 0
            pts_p = min(25, max(0, taxa_poup * 100))
            pts_r = min(25, max(0, (meses_res / 6) * 25))
            pts_d = 25
            pts_i = min(15, max(0, (taxa_poup * 100 / 30) * 15))
            pts_dv = 10
            nota = round(pts_p + pts_r + pts_d + pts_i + pts_dv, 1)
            cor = "#22C55E" if nota >= 80 else ("#F59E0B" if nota >= 60 else "#EF4444")
            st.markdown(
                f"<div style='background:{PALETA['fundo_card']};border:2px solid {cor};"
                f"border-radius:16px;padding:32px;text-align:center;'>"
                f"<div style='color:{PALETA['texto_secundario']};font-size:12px;letter-spacing:2px;'>SUA NOTA</div>"
                f"<div style='color:{cor};font-size:64px;font-weight:700;'>{nota:.0f}</div>"
                f"</div>", unsafe_allow_html=True)
            st.markdown("#### Detalhamento")
            for lbl, pts, mx in [("Taxa de poupança", pts_p, 25), ("Reserva", pts_r, 25),
                                   ("Controle de dívidas", pts_d, 25),
                                   ("Capacidade de investir", pts_i, 15),
                                   ("Diversificação", pts_dv, 10)]:
                st.markdown(f"**{lbl}:** {pts:.1f}/{mx}")
                st.progress(pts / mx)

    elif secao == "🛡️ Checklist de Proteção":
        st.markdown("### 🛡️ Checklist de Proteção")
        itens = ["Reserva de emergência (6 meses)", "Seguro de vida", "Plano de saúde",
                  "Previdência privada", "Seguro residencial/auto", "Testamento/inventário",
                  "Cofre digital/senhas"]
        feitos = 0
        for i, item in enumerate(itens):
            if st.checkbox(item, key=f"prot_{i}"):
                feitos += 1
        pct = (feitos / len(itens) * 100)
        st.progress(pct / 100)
        st.markdown(f"**Progresso:** {feitos}/{len(itens)} itens ({pct:.0f}%)")

# =============================================================================
# FIM
# =============================================================================
