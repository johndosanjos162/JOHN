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
        transition: all 0.2s ease;
    }}
    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, div[data-baseweb="select"] > div:focus-within {{
        border-color: {PALETA["acento"]} !important; box-shadow: 0 0 0 3px {PALETA["acento_glow"]} !important;
    }}
    label[data-testid="stWidgetLabel"] p {{ color: {PALETA["texto_secundario"]} !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }}
    div[data-testid="stExpander"] {{ background: {PALETA["fundo_card"]}; border: 1px solid {PALETA["borda"]} !important; border-radius: 12px !important; overflow: hidden; }}
    div[data-testid="stExpander"] summary {{ font-weight: 600 !important; color: {PALETA["texto_principal"]} !important; padding: 14px 18px !important; transition: background 0.2s ease; }}
    div[data-testid="stExpander"] summary:hover {{ background: {PALETA["fundo_hover"]}; }}
    div[data-testid="stAlert"] {{ border-radius: 12px !important; border-left-width: 4px !important; font-size: 13px !important; padding: 12px 16px !important; }}
    div[data-testid="stAlert"][data-baseweb="notification"] {{ background: {PALETA["fundo_card"]} !important; }}
    .stDataFrame, div[data-testid="stTable"] {{ background: {PALETA["fundo_card"]} !important; border-radius: 12px !important; border: 1px solid {PALETA["borda"]} !important; overflow: hidden; }}
    div[data-testid="stTable"] table {{ background: {PALETA["fundo_card"]} !important; color: {PALETA["texto_principal"]} !important; border-collapse: collapse !important; }}
    div[data-testid="stTable"] thead tr th {{ background: {PALETA["fundo_sidebar"]} !important; color: {PALETA["texto_secundario"]} !important; text-transform: uppercase; letter-spacing: 1px; font-size: 11px !important; font-weight: 700 !important; border-bottom: 1px solid {PALETA["borda"]} !important; padding: 12px !important; }}
    div[data-testid="stTable"] tbody tr {{ border-bottom: 1px solid {PALETA["borda"]} !important; }}
    div[data-testid="stTable"] tbody tr:nth-child(even) {{ background: rgba(31, 41, 55, 0.25) !important; }}
    div[data-testid="stTable"] tbody tr:hover {{ background: {PALETA["fundo_hover"]} !important; }}
    div[data-testid="stTable"] tbody td {{ color: {PALETA["texto_principal"]} !important; font-size: 13px !important; padding: 10px 12px !important; }}
    .stProgress > div > div > div > div {{ background: linear-gradient(90deg, {PALETA["acento"]}, {PALETA["ciano"]}) !important; border-radius: 999px !important; box-shadow: 0 0 12px {PALETA["acento_glow"]}; }}
    .stProgress > div > div > div {{ background: {PALETA["fundo_card"]} !important; border-radius: 999px !important; height: 8px !important; }}
    .stCheckbox label span, .stRadio label span {{ color: {PALETA["texto_principal"]} !important; font-size: 13px !important; }}
    .stCheckbox input:checked + div, .stRadio input:checked + div {{ background-color: {PALETA["acento"]} !important; border-color: {PALETA["acento"]} !important; }}
    hr {{ border: none !important; height: 1px !important; background: linear-gradient(90deg, transparent, {PALETA["borda"]}, transparent) !important; margin: 20px 0 !important; }}
    div[data-testid="stForm"] {{ background: {PALETA["fundo_card"]}; border: 1px solid {PALETA["borda"]}; border-radius: 14px; padding: 20px !important; }}
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {PALETA["fundo_principal"]}; }}
    ::-webkit-scrollbar-thumb {{ background: {PALETA["borda"]}; border-radius: 999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {PALETA["acento"]}; }}
    .login-title {{ background: linear-gradient(90deg, {PALETA["acento"]}, {PALETA["ciano"]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSÃO E MESES
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
# LOGIN
# -----------------------------------------------------------------------------
if not st.session_state['autenticado']:
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-title" style="font-size:28px; font-weight:700; text-align:center; margin-bottom:10px;">🛡️ INVEST CONTROL PRO</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle" style="font-size:14px; color:#8A95A5; text-align:center; margin-bottom:30px;">Sistema Integrado de Projeção Econômica & Acesso Seguro</div>', unsafe_allow_html=True)

        with st.form("form_login"):
            st.markdown("### Credenciais de Acesso")
            usuario = st.text_input("Usuário / Credencial", placeholder="Digite seu usuário...")
            senha = st.text_input("Senha de Acesso", type="password", placeholder="Digite sua senha...")
            st.markdown("---")
            btn_entrar = st.form_submit_button("Acessar Sistema", use_container_width=True)
            if btn_entrar:
                if usuario == "JOHN" and senha == "fgxv4VP0/*":
                    st.session_state['autenticado'] = True
                    st.success("Acesso autorizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas. Acesso restrito.")
        st.info("💡 **Segurança Ativa:** Ambiente protegido contra oscilações e acessos não autorizados.")
        st.stop()

# -----------------------------------------------------------------------------
# SUPABASE
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

# =============================================================================
# FUNÇÕES — CDI (Banco Central)
# =============================================================================
@st.cache_data(ttl=3600)
def obter_taxa_cdi_atual():
    """Busca a taxa CDI anualizada (base 252) mais recente via API do Banco Central (SGS 4389). Cache de 1h."""
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
    """Busca o histórico recente da taxa CDI (últimos N dias)."""
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
    """Calcula projeção de investimento atrelado ao CDI."""
    if percentual_cdi <= 0 or cdi_anual <= 0:
        return None
    cdi_mensal = (1 + cdi_anual / 100) ** (1/12) - 1
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
    """Gráfico comparativo: com CDI vs sem rendimento."""
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
        font_color="#E6EDF3", xaxis_title="Anos",
        yaxis_title="Valor (R$)", legend_title="Cenário",
        margin=dict(l=20, r=20, t=30, b=20),
    )
    return fig

# =============================================================================
# FUNÇÕES DE DADOS
# =============================================================================
def carregar_configuracoes():
    if supabase:
        try:
            res = supabase.table("configuracoes").select("*").eq("id", 1).execute()
            if res.data:
                return res.data[0]
        except:
            pass
    return {
        "aluguel_total": 1700.0, "salario_a": 2700.0, "salario_b": 2000.0,
        "vr_a": 700.0, "meta_reserva_mensal": 800.0,
        "aluguel_a_custom": 850.0, "aluguel_b_custom": 850.0,
        "usa_edicao_manual": False
    }

def salvar_configuracoes(aluguel, salario_a, salario_b, vr_a, meta_reserva, aluguel_a_custom, aluguel_b_custom, usa_edicao):
    if supabase:
        try:
            supabase.table("configuracoes").update({
                "aluguel_total": aluguel, "salario_a": salario_a, "salario_b": salario_b,
                "vr_a": vr_a, "meta_reserva_mensal": meta_reserva,
                "aluguel_a_custom": aluguel_a_custom, "aluguel_b_custom": aluguel_b_custom,
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
                "data": data_formatada, "descricao": str(descricao).strip(),
                "categoria": str(categoria).strip(), "valor": float(valor)
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
# ORÇAMENTO
# -----------------------------------------------------------------------------
def carregar_orcamento_mes(mes, ano):
    if supabase:
        try:
            res = supabase.table("orcamentos_mensais").select("*").eq("mes", mes).eq("ano", ano).execute()
            if res.data:
                return res.data[0]
            novo = {"mes": mes, "ano": ano, "orcamento": 0.0, "fechado": False}
            res_ins = supabase.table("orcamentos_mensais").insert(novo).execute()
            if res_ins.data:
                return res_ins.data[0]
        except Exception as e:
            st.warning(f"Erro ao carregar orçamento: {e}")
    return {"mes": mes, "ano": ano, "orcamento": 0.0, "fechado": False}

def salvar_orcamento_mes(mes, ano, valor_orcamento):
    if supabase:
        try:
            existente = supabase.table("orcamentos_mensais").select("id").eq("mes", mes).eq("ano", ano).execute()
            if existente.data:
                supabase.table("orcamentos_mensais").update({"orcamento": float(valor_orcamento)}).eq("id", existente.data[0]["id"]).execute()
            else:
                supabase.table("orcamentos_mensais").insert({"mes": mes, "ano": ano, "orcamento": float(valor_orcamento), "fechado": False}).execute()
        except Exception as e:
            st.error(f"Erro ao salvar orçamento: {e}")

def fechar_mes(mes, ano):
    if supabase:
        try:
            supabase.table("orcamentos_mensais").update({"fechado": True}).eq("mes", mes).eq("ano", ano).execute()
        except:
            pass

def carregar_despesas_por_mes(mes, ano):
    if supabase:
        try:
            res = supabase.table("despesas_variaveis").select("*").order("data", desc=True).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['data'] = pd.to_datetime(df['data'])
                df = df[(df['data'].dt.month == mes) & (df['data'].dt.year == ano)]
                return df
        except:
            pass
    return pd.DataFrame(columns=["id", "data", "descricao", "categoria", "valor"])

def listar_meses_fechados():
    if supabase:
        try:
            res = supabase.table("orcamentos_mensais").select("*").order("ano", desc=True).order("mes", desc=True).execute()
            if res.data:
                return pd.DataFrame(res.data)
        except:
            pass
    return pd.DataFrame(columns=["id", "mes", "ano", "orcamento", "fechado"])

# -----------------------------------------------------------------------------
# PDFs
# -----------------------------------------------------------------------------
def gerar_relatorio_mensal_pdf(mes, ano, df_mes, orcamento):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#3B82F6'), spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#E6EDF3'), spaceBefore=12, spaceAfter=6)
    normal_style = styles['Normal']

    nome_mes = meses_nomes[mes - 1]
    story.append(Paragraph(f"<b>RELATÓRIO MENSAL — {nome_mes.upper()}/{ano}</b>", title_style))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle('S', parent=normal_style, alignment=1, textColor=colors.HexColor('#8B949E'))))
    story.append(Spacer(1, 15))

    total_gasto = df_mes["valor"].sum() if not df_mes.empty else 0.0
    saldo = orcamento - total_gasto
    pct = (total_gasto / orcamento * 100) if orcamento > 0 else 0

    resumo = [["Indicador", "Valor (R$)"], ["Orçamento do Mês", f"R$ {orcamento:,.2f}"],
              ["Total Gasto", f"R$ {total_gasto:,.2f}"], ["Saldo Restante", f"R$ {saldo:,.2f}"],
              ["% Utilizado", f"{pct:.1f}%"]]
    t = Table(resumo, colWidths=[250, 200])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
                           ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Despesas Detalhadas do Mês</b>", heading_style))
    if not df_mes.empty:
        data = [["Data", "Descrição", "Categoria", "Valor (R$)"]]
        for _, row in df_mes.iterrows():
            data.append([row['data'].strftime('%d/%m/%Y'), str(row['descricao']),
                         str(row['categoria']), f"R$ {float(row['valor']):,.2f}"])
        tv = Table(data, colWidths=[80, 170, 110, 90])
        tv.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
        story.append(tv)
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Gastos por Categoria</b>", heading_style))
        cat = df_mes.groupby("categoria")["valor"].sum().reset_index()
        cat_data = [["Categoria", "Total (R$)"]]
        for _, r in cat.iterrows():
            cat_data.append([str(r['categoria']), f"R$ {float(r['valor']):,.2f}"])
        tc = Table(cat_data, colWidths=[250, 200])
        tc.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
        story.append(tc)
    else:
        story.append(Paragraph("Nenhuma despesa registrada neste mês.", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_relatorio_pdf(df_fixos, df_variaveis, salario_a, salario_b, aluguel_a, aluguel_b):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TS', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#3B82F6'), spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle('HS', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#E6EDF3'), spaceBefore=12, spaceAfter=6)
    normal_style = styles['Normal']

    story.append(Paragraph("<b>INVEST CONTROL PRO - RELATÓRIO FINANCEIRO</b>", title_style))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle('Sub', parent=normal_style, alignment=1, textColor=colors.HexColor('#8B949E'))))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>1. Resumo de Rendas e Contribuições</b>", heading_style))
    resumo_data = [["Descrição", "Valor (R$)"], ["Salário Pessoa A", f"R$ {salario_a:,.2f}"],
                   ["Salário Pessoa B", f"R$ {salario_b:,.2f}"],
                   ["Aluguel Proporcional (A)", f"R$ {aluguel_a:,.2f}"],
                   ["Aluguel Proporcional (B)", f"R$ {aluguel_b:,.2f}"]]
    t_resumo = Table(resumo_data, colWidths=[250, 200])
    t_resumo.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
                                   ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                                   ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
    story.append(t_resumo)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>2. Relatório de Custos e Gastos Fixos</b>", heading_style))
    if not df_fixos.empty:
        fixos_data = [["Descrição do Gasto", "Valor Mensal (R$)"]]
        for _, row in df_fixos.iterrows():
            fixos_data.append([str(row['descricao']), f"R$ {float(row['valor']):,.2f}"])
        t_fixos = Table(fixos_data, colWidths=[250, 200])
        t_fixos.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
                                     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                     ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
        story.append(t_fixos)
    else:
        story.append(Paragraph("Nenhum gasto fixo cadastrado.", normal_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>3. Relatório de Despesas Variáveis</b>", heading_style))
    if not df_variaveis.empty:
        var_data = [["Data", "Descrição", "Categoria", "Valor (R$)"]]
        for _, row in df_variaveis.iterrows():
            data_str = row['data'].strftime('%d/%m/%Y') if pd.notnull(row['data']) else ""
            var_data.append([data_str, str(row['descricao']), str(row['categoria']), f"R$ {float(row['valor']):,.2f}"])
        t_vars = Table(var_data, colWidths=[80, 170, 110, 90])
        t_vars.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
        story.append(t_vars)
    else:
        story.append(Paragraph("Nenhuma despesa variável registrada.", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# =============================================================================
# FUNÇÕES — CORTES
# =============================================================================
def _fmt_brl(v: float) -> str:
    try:
        return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def carregar_metas_corte():
    if supabase:
        try:
            res = supabase.table("metas_corte").select("*").eq("ativo", True).execute()
            if res.data:
                return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "categoria", "meta_reducao_pct", "ativo"])

def salvar_meta_corte(categoria, meta_reducao_pct):
    if supabase:
        try:
            existente = supabase.table("metas_corte").select("id").eq("categoria", categoria).execute()
            if existente.data:
                supabase.table("metas_corte").update({
                    "meta_reducao_pct": float(meta_reducao_pct), "ativo": True,
                    "atualizado_em": datetime.now().isoformat()
                }).eq("categoria", categoria).execute()
            else:
                supabase.table("metas_corte").insert({
                    "categoria": categoria, "meta_reducao_pct": float(meta_reducao_pct), "ativo": True
                }).execute()
        except Exception as e:
            st.error(f"Erro ao salvar meta de corte: {e}")

def remover_meta_corte(categoria):
    if supabase:
        try: supabase.table("metas_corte").update({"ativo": False}).eq("categoria", categoria).execute()
        except: pass

def salvar_analise_corte(mes, ano, sugestoes):
    if supabase and sugestoes:
        try:
            supabase.table("analises_corte").insert([{
                "mes": int(mes), "ano": int(ano), "categoria": s["categoria_limpa"],
                "valor_atual": float(s["valor_atual"]),
                "valor_sugerido": float(s["corte_sugerido"]),
                "economia_potencial": float(s["economia_potencial"]),
                "prioridade": int(s["prioridade"])
            } for s in sugestoes]).execute()
        except Exception as e:
            st.warning(f"Não foi possível salvar histórico: {e}")

def carregar_historico_analises():
    if supabase:
        try:
            res = supabase.table("analises_corte").select("*").order("criado_em", desc=True).limit(100).execute()
            if res.data:
                return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "mes", "ano", "categoria", "valor_atual",
                                  "valor_sugerido", "economia_potencial", "prioridade", "criado_em"])

def _gerar_explicacao_corte(categoria, valor, peso, benchmark, excesso,
                             corte_sugerido, tipo, receita_bruta, meta_reserva_mensal=0.0):
    tipo_txt = "despesa variável" if tipo == "Variável" else "custo fixo"
    excesso_pct = peso - benchmark
    valor_ideal = receita_bruta * benchmark / 100
    if excesso_pct >= 10:
        nivel, emoji = "CRÍTICO", "🚨"
        acao = "Essa categoria está muito acima do recomendado e compromete seriamente seu equilíbrio financeiro. Precisa de revisão imediata."
    elif excesso_pct >= 5:
        nivel, emoji = "ALTO", "⚠️"
        acao = "Essa categoria precisa de atenção agora. Reduzir evita que o problema cresça nos próximos meses."
    else:
        nivel, emoji = "MODERADO", "📌"
        acao = "Categoria levemente acima do ideal. Pequenos ajustes já trazem resultado sem sacrificar sua qualidade de vida."
    impacto_reserva = ""
    if meta_reserva_mensal > 0:
        pct_reserva = (corte_sugerido / meta_reserva_mensal) * 100
        impacto_reserva = f" Esse valor equivale a <b>{pct_reserva:.0f}%</b> da sua meta de reserva mensal (R$ {meta_reserva_mensal:,.2f})."
    impacto_renda = (corte_sugerido / receita_bruta) * 100 if receita_bruta > 0 else 0
    return (
        f"{emoji} <b>Nível de prioridade: {nivel}</b><br><br>"
        f"Você está gastando <b>R$ {valor:,.2f}</b> em <b>{categoria}</b> ({tipo_txt}), "
        f"o que representa <b>{peso:.1f}%</b> da sua renda bruta. Para essa categoria, "
        f"o recomendado é no máximo <b>{benchmark:.0f}%</b> (ideal: R$ {valor_ideal:,.2f}). "
        f"Ou seja, você está <b>{excesso_pct:.1f} pontos percentuais acima do ideal</b>, "
        f"gerando um excesso de <b>R$ {excesso:,.2f} por mês</b>.<br><br>"
        f"<b>Por que cortar aqui?</b> {acao}<br><br>"
        f"<b>O que você ganha:</b> reduzindo <b>R$ {corte_sugerido:,.2f}/mês</b>, você libera "
        f"<b>R$ {corte_sugerido * 12:,.2f} por ano</b> — dinheiro que pode ir para sua reserva "
        f"de emergência, investimentos ou quitação de dívidas.{impacto_reserva}<br><br>"
        f"<b>Impacto na sua renda:</b> esse corte representa <b>{impacto_renda:.2f}%</b> da sua "
        f"receita bruta mensal — um ajuste real, mas possível, sem comprometer o essencial."
    )

def analisar_cortes_inteligentes(df_variaveis, df_gastos_fixos, receita_bruta, meta_reserva_mensal=0.0):
    BENCHMARKS = {
        "Lazer / Passeios": 8.0, "Farmácia / Saúde": 5.0, "Vestuário": 5.0,
        "Imprevistos": 10.0, "Outros": 5.0, "Internet": 3.0, "Recarga celular": 2.0,
        "Corte de cabelo": 2.0, "Cartão de crédito": 10.0, "Alimentação": 15.0,
        "Transporte": 10.0, "Moradia": 30.0,
    }
    if receita_bruta <= 0:
        return pd.DataFrame()
    sugestoes = []
    if df_variaveis is not None and not df_variaveis.empty:
        grp = df_variaveis.groupby("categoria")["valor"].sum().reset_index()
        for _, r in grp.iterrows():
            cat, val = str(r["categoria"]), float(r["valor"])
            peso = (val / receita_bruta) * 100
            bench = BENCHMARKS.get(cat, 8.0)
            if peso > bench:
                excesso = val - (receita_bruta * bench / 100)
                corte_sug = excesso * 0.5
                sugestoes.append({
                    "categoria": f"💳 {cat}", "categoria_limpa": cat, "tipo": "Variável",
                    "valor_atual": val, "peso_receita": round(peso, 2),
                    "benchmark_saudavel": bench, "excesso": round(excesso, 2),
                    "corte_sugerido": round(corte_sug, 2),
                    "economia_potencial": round(corte_sug * 12, 2),
                    "explicacao": _gerar_explicacao_corte(cat, val, peso, bench, excesso, corte_sug, "Variável", receita_bruta, meta_reserva_mensal),
                })
    if df_gastos_fixos is not None and not df_gastos_fixos.empty:
        grp_f = df_gastos_fixos.groupby("descricao")["valor"].sum().reset_index()
        for _, r in grp_f.iterrows():
            cat, val = str(r["descricao"]), float(r["valor"])
            peso = (val / receita_bruta) * 100
            bench = BENCHMARKS.get(cat, 5.0)
            if peso > bench:
                excesso = val - (receita_bruta * bench / 100)
                corte_sug = excesso * 0.4
                sugestoes.append({
                    "categoria": f"🔧 {cat}", "categoria_limpa": cat, "tipo": "Fixo",
                    "valor_atual": val, "peso_receita": round(peso, 2),
                    "benchmark_saudavel": bench, "excesso": round(excesso, 2),
                    "corte_sugerido": round(corte_sug, 2),
                    "economia_potencial": round(corte_sug * 12, 2),
                    "explicacao": _gerar_explicacao_corte(cat, val, peso, bench, excesso, corte_sug, "Fixo", receita_bruta, meta_reserva_mensal),
                })
    if not sugestoes:
        return pd.DataFrame()
    df_sug = pd.DataFrame(sugestoes)
    df_sug = df_sug.sort_values("economia_potencial", ascending=False).reset_index(drop=True)
    df_sug["prioridade"] = df_sug.index + 1
    return df_sug

def calcular_meta_poupanca_ideal(receita_bruta, total_fixos, total_variaveis, meta_reserva_atual, taxa_ideal=0.20):
    if receita_bruta <= 0:
        return None
    meta_ideal_valor   = receita_bruta * taxa_ideal
    poupanca_atual     = max(0.0, meta_reserva_atual)
    falta_valor        = max(0.0, meta_ideal_valor - poupanca_atual)
    poupanca_atual_pct = (poupanca_atual / receita_bruta) * 100
    meta_ideal_pct     = taxa_ideal * 100
    falta_pct          = meta_ideal_pct - poupanca_atual_pct
    progresso          = min(1.0, poupanca_atual / meta_ideal_valor) if meta_ideal_valor > 0 else 0.0
    if progresso >= 1.0: status_cor, status_emoji, status_txt = "#22C55E", "🟢", "Meta atingida"
    elif progresso >= 0.5: status_cor, status_emoji, status_txt = "#F59E0B", "🟡", "No caminho"
    else: status_cor, status_emoji, status_txt = "#EF4444", "🔴", "Abaixo do ideal"
    return {
        "meta_ideal_valor": round(meta_ideal_valor, 2), "meta_ideal_pct": round(meta_ideal_pct, 1),
        "poupanca_atual": round(poupanca_atual, 2), "poupanca_atual_pct": round(poupanca_atual_pct, 1),
        "falta_valor": round(falta_valor, 2), "falta_pct": round(falta_pct, 1),
        "progresso": round(progresso, 3), "status_cor": status_cor,
        "status_emoji": status_emoji, "status_txt": status_txt,
    }

def calcular_poupanca_por_categoria(df_sug, receita_bruta):
    if df_sug.empty:
        return pd.DataFrame()
    linhas = []
    for _, s in df_sug.iterrows():
        valor_atual   = float(s["valor_atual"])
        valor_ideal   = receita_bruta * float(s["benchmark_saudavel"]) / 100
        reduzir_valor = max(0.0, valor_atual - valor_ideal)
        reduzir_pct   = (reduzir_valor / valor_atual * 100) if valor_atual > 0 else 0
        linhas.append({
            "Categoria": s["categoria_limpa"], "Tipo": s["tipo"],
            "Gasto Atual (R$)": round(valor_atual, 2), "Ideal (R$)": round(valor_ideal, 2),
            "Reduzir (R$)": round(reduzir_valor, 2), "Reduzir (%)": round(reduzir_pct, 1),
            "Peso Atual (%)": s["peso_receita"], "Peso Ideal (%)": s["benchmark_saudavel"],
        })
    return pd.DataFrame(linhas).sort_values("Reduzir (R$)", ascending=False).reset_index(drop=True)

ESFORCO_POR_CATEGORIA = {
    "Lazer / Passeios": "Fácil", "Vestuário": "Fácil", "Outros": "Fácil",
    "Recarga celular": "Fácil", "Corte de cabelo": "Médio",
    "Farmácia / Saúde": "Médio", "Imprevistos": "Médio",
    "Internet": "Médio", "Cartão de crédito": "Médio",
    "Alimentação": "Médio", "Transporte": "Médio", "Moradia": "Difícil",
}

def calcular_progresso_meta_corte(categoria_limpa, meta_pct, df_todas_despesas):
    if df_todas_despesas is None or df_todas_despesas.empty:
        return None
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    hoje = datetime.now()
    df_atual = df[(df['data'].dt.month == hoje.month) & (df['data'].dt.year == hoje.year)]
    df_passado = df[~((df['data'].dt.month == hoje.month) & (df['data'].dt.year == hoje.year))]
    if df_passado.empty: return None
    df_passado['mes_ano'] = df_passado['data'].dt.to_period('M')
    media_passado = df_passado[df_passado['categoria'] == categoria_limpa].groupby('mes_ano')['valor'].sum().mean()
    if pd.isna(media_passado) or media_passado <= 0: return None
    atual = df_atual[df_atual['categoria'] == categoria_limpa]['valor'].sum()
    alvo = media_passado * (1 - meta_pct / 100)
    if atual <= alvo: progresso = 1.0
    elif atual >= media_passado: progresso = 0.0
    else: progresso = (media_passado - atual) / (media_passado - alvo)
    return {"media_passado": round(media_passado, 2), "atual": round(atual, 2),
            "alvo": round(alvo, 2), "progresso": max(0.0, min(1.0, progresso)),
            "economia_atual": round(max(0, media_passado - atual), 2)}

def evolucao_mensal_categoria(categoria_limpa, df_todas_despesas, meses=6):
    if df_todas_despesas is None or df_todas_despesas.empty: return pd.DataFrame()
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    df = df[df['categoria'] == categoria_limpa]
    if df.empty: return pd.DataFrame()
    df['mes_ano'] = df['data'].dt.to_period('M').astype(str)
    serie = df.groupby('mes_ano')['valor'].sum().reset_index().sort_values('mes_ano')
    return serie.tail(meses)

def detectar_retrocesso(categoria_limpa, df_todas_despesas):
    if df_todas_despesas is None or df_todas_despesas.empty: return None
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    hoje = datetime.now()
    df_atual = df[(df['data'].dt.month == hoje.month) & (df['data'].dt.year == hoje.year)]
    mes_ant = (pd.Timestamp(hoje) - pd.DateOffset(months=1)).to_period('M')
    df_anterior = df[df['data'].dt.to_period('M') == mes_ant]
    val_atual = df_atual[df_atual['categoria'] == categoria_limpa]['valor'].sum()
    val_anterior = df_anterior[df_anterior['categoria'] == categoria_limpa]['valor'].sum()
    if val_anterior <= 0 or val_atual <= 0: return None
    variacao = ((val_atual - val_anterior) / val_anterior) * 100
    if variacao >= 15:
        return {"variacao": round(variacao, 1), "atual": round(val_atual, 2), "anterior": round(val_anterior, 2)}
    return None

def simular_corte(valor_atual, percentual):
    economia_mensal = valor_atual * (percentual / 100)
    return {"economia_mensal": round(economia_mensal, 2), "economia_anual": round(economia_mensal * 12, 2)}

def impacto_na_reserva(economia_mensal, meta_reserva, total_fixos):
    if total_fixos <= 0: return None
    return {"meses_extra_por_ano": round((economia_mensal * 12) / total_fixos, 2),
            "pct_meta_reserva": round((economia_mensal / meta_reserva * 100) if meta_reserva > 0 else 0, 1)}

def classificar_matriz_esforco(categoria_limpa, economia_anual, economia_max):
    esforco = ESFORCO_POR_CATEGORIA.get(categoria_limpa, "Médio")
    impacto = "Alto" if economia_max > 0 and economia_anual >= economia_max * 0.5 else "Baixo"
    quadrante = f"{esforco} × {impacto}"
    if quadrante == "Fácil × Alto": emoji, cor, acao = "🟢", "#22C55E", "ATAQUE PRIMEIRO — corte rápido e impactante"
    elif quadrante in ("Fácil × Baixo", "Médio × Alto"): emoji, cor, acao = "🟡", "#F59E0B", "VALE A PENA — planeje com calma"
    elif quadrante == "Difícil × Alto": emoji, cor, acao = "🔴", "#EF4444", "PRECISA PLANEJAR — mudança estrutural"
    else: emoji, cor, acao = "⚪", "#8A95A5", "BAIXA PRIORIDADE — corte cosmético"
    return {"esforco": esforco, "impacto": impacto, "quadrante": quadrante,
            "emoji": emoji, "cor": cor, "acao": acao}

def detectar_assinaturas(df_todas_despesas, min_ocorrencias=3):
    if df_todas_despesas is None or df_todas_despesas.empty: return pd.DataFrame()
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    resultado = []
    for desc, grupo in df.groupby('descricao'):
        if len(grupo) < min_ocorrencias: continue
        if grupo['data'].dt.to_period('M').nunique() < 2: continue
        valor_medio = grupo['valor'].mean()
        desvio = grupo['valor'].std() / valor_medio if valor_medio > 0 else 1
        if desvio < 0.3:
            resultado.append({"descricao": desc, "valor_medio": round(valor_medio, 2),
                              "ocorrencias": len(grupo),
                              "meses_presentes": grupo['data'].dt.to_period('M').nunique(),
                              "total_mensal": round(valor_medio, 2),
                              "total_anual": round(valor_medio * 12, 2)})
    if not resultado: return pd.DataFrame()
    return pd.DataFrame(resultado).sort_values("total_anual", ascending=False)

def detectar_gastos_invisiveis(df_todas_despesas, limite_valor=60.0, min_ocorrencias=3):
    if df_todas_despesas is None or df_todas_despesas.empty: return pd.DataFrame()
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    df['mes_ano'] = df['data'].dt.to_period('M')
    resultado = []
    for desc, grupo in df.groupby('descricao'):
        if len(grupo) < min_ocorrencias: continue
        valor_medio = grupo['valor'].mean()
        if valor_medio > limite_valor: continue
        meses = grupo['mes_ano'].nunique()
        if meses == 0: continue
        freq = len(grupo) / meses
        total_mensal = valor_medio * freq
        resultado.append({"descricao": desc, "valor_medio": round(valor_medio, 2),
                          "frequencia_mensal": round(freq, 1),
                          "total_mensal": round(total_mensal, 2),
                          "total_anual": round(total_mensal * 12, 2)})
    if not resultado: return pd.DataFrame()
    return pd.DataFrame(resultado).sort_values("total_anual", ascending=False)

def calcular_custo_hora(valor, salario_mensal, horas_mes=176):
    if salario_mensal <= 0: return 0.0
    return round(valor / (salario_mensal / horas_mes), 1)

def projetar_longo_prazo(valor_mensal, taxa_anual=0.10):
    taxa_m = (1 + taxa_anual) ** (1 / 12) - 1
    def _simular(anos):
        saldo = 0.0
        for _ in range(anos * 12):
            saldo = (saldo + valor_mensal) * (1 + taxa_m)
        return round(saldo, 2)
    return {"1_ano": _simular(1), "5_anos": _simular(5), "10_anos": _simular(10), "20_anos": _simular(20)}

def marcar_corte_concluido(categoria, valor_economia, mes, ano):
    if supabase:
        try:
            supabase.table("cortes_concluidos").insert({
                "categoria": categoria, "valor_economia": float(valor_economia),
                "mes": int(mes), "ano": int(ano), "concluido_em": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            st.error(f"Erro ao marcar corte concluído: {e}")

def carregar_cortes_concluidos():
    if supabase:
        try:
            res = supabase.table("cortes_concluidos").select("*").order("concluido_em", desc=True).execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "categoria", "valor_economia", "mes", "ano", "concluido_em"])

def remover_corte_concluido(corte_id):
    if supabase:
        try: supabase.table("cortes_concluidos").delete().eq("id", corte_id).execute()
        except: pass

def gerar_checklist_semanal(df_sug, df_concluidos):
    if df_sug.empty: return []
    concluidas = df_concluidos['categoria'].tolist() if not df_concluidos.empty else []
    return [{"categoria": s['categoria_limpa'], "acao": f"Reduzir gastos em {s['categoria_limpa']}",
             "economia": float(s['corte_sugerido'])} for _, s in df_sug.iterrows() if s['categoria_limpa'] not in concluidas]

def salvar_checklist_semanal(tarefas, semana_str):
    if not supabase or not tarefas: return
    try:
        supabase.table("checklist_semanal").insert([{
            "categoria": t["categoria"], "acao": t["acao"],
            "economia_estimada": t["economia"], "semana": semana_str, "concluida": False
        } for t in tarefas]).execute()
    except Exception as e:
        st.warning(f"Não foi possível salvar o checklist: {e}")

def carregar_checklist_semana(semana_str):
    if supabase:
        try:
            res = supabase.table("checklist_semanal").select("*").eq("semana", semana_str).execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "categoria", "acao", "economia_estimada", "concluida", "semana"])

def marcar_item_checklist(item_id, concluida=True):
    if supabase:
        try: supabase.table("checklist_semanal").update({"concluida": concluida}).eq("id", item_id).execute()
        except: pass

def gerar_pdf_plano_corte(df_sug, receita_bruta, economia_mensal, economia_anual):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#3B82F6'), spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1F2937'), spaceBefore=12, spaceAfter=6)
    normal_style = styles['Normal']
    just_style = ParagraphStyle('J', parent=styles['Normal'], alignment=4, fontSize=10, leading=14)

    story.append(Paragraph("<b>INVEST CONTROL PRO - PLANO DE CORTES INTELIGENTES</b>", title_style))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ParagraphStyle('S', parent=normal_style, alignment=1, textColor=colors.HexColor('#8B949E'))))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>1. Resumo Executivo</b>", heading_style))
    resumo = [["Indicador", "Valor"], ["Receita Bruta Considerada", f"R$ {receita_bruta:,.2f}"],
              ["Economia Mensal Potencial", f"R$ {economia_mensal:,.2f}"],
              ["Economia Anual Projetada", f"R$ {economia_anual:,.2f}"],
              ["Categorias com Excesso", f"{len(df_sug)}"]]
    t_resumo = Table(resumo, colWidths=[250, 200])
    t_resumo.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
                                   ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))]))
    story.append(t_resumo)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>2. Ranking de Prioridades de Corte</b>", heading_style))
    data = [["#", "Categoria", "Tipo", "Atual (R$)", "Peso (%)", "Corte/mes (R$)", "Economia Anual (R$)"]]
    for _, s in df_sug.iterrows():
        data.append([str(int(s['prioridade'])), str(s['categoria']), str(s['tipo']),
                     f"{s['valor_atual']:,.2f}", f"{s['peso_receita']}%",
                     f"{s['corte_sugerido']:,.2f}", f"{s['economia_potencial']:,.2f}"])
    tv = Table(data, colWidths=[22, 120, 55, 75, 55, 75, 95])
    tv.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36')),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
                            ('ALIGN', (3, 1), (-1, -1), 'RIGHT')]))
    story.append(tv)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>3. Justificativa Detalhada de Cada Corte</b>", heading_style))
    story.append(Paragraph("Abaixo está o motivo de cada categoria ter sido sinalizada.", just_style))
    story.append(Spacer(1, 10))
    for _, s in df_sug.iterrows():
        texto_puro = s['explicacao'].replace("<b>", "").replace("</b>", "").replace("<br><br>", " ").replace("<br>", " ")
        for emo in ["🚨", "⚠️", "📌"]:
            texto_puro = texto_puro.replace(emo, "")
        story.append(Paragraph(f"<b>#{int(s['prioridade'])} - {s['categoria_limpa']} ({s['tipo']})</b>",
                                ParagraphStyle('CH', parent=styles['Heading3'], fontSize=11, textColor=colors.HexColor('#1F2937'), spaceAfter=4)))
        story.append(Paragraph(texto_puro.strip(), just_style))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>4. Plano de Acao Recomendado (Top 5)</b>", heading_style))
    story.append(Spacer(1, 8))
    for _, s in df_sug.head(5).iterrows():
        nova_meta = s['valor_atual'] - s['corte_sugerido']
        story.append(Paragraph(f"<b>#{int(s['prioridade'])} - {s['categoria']}:</b> Reduzir de <b>R$ {s['valor_atual']:,.2f}</b> para aproximadamente <b>R$ {nova_meta:,.2f}</b>", just_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# =============================================================================
# FUNÇÕES — SIMULADOR DE INVESTIMENTO (com suporte a CDI)
# =============================================================================
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
                                  "montante_final", "total_investido", "juros_totais",
                                  "cdi_taxa_utilizada", "criado_em"])

def remover_simulacao_investimento(sim_id):
    if supabase:
        try: supabase.table("simulacoes_investimento").delete().eq("id", sim_id).execute()
        except: pass

# =============================================================================
# FUNÇÕES — PROSPERIDADE
# =============================================================================
def carregar_ativos():
    if supabase:
        try:
            res = supabase.table("ativos").select("*").order("valor", desc=True).execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "nome", "categoria", "valor"])

def adicionar_ativo(nome, categoria, valor):
    if supabase:
        try: supabase.table("ativos").insert({"nome": str(nome).strip(), "categoria": categoria, "valor": float(valor)}).execute()
        except Exception as e: st.error(f"Erro: {e}")

def remover_ativo(id_):
    if supabase:
        try: supabase.table("ativos").delete().eq("id", id_).execute()
        except: pass

def carregar_passivos():
    if supabase:
        try:
            res = supabase.table("passivos").select("*").order("valor_total", desc=True).execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "nome", "tipo", "valor_total", "parcelas_restantes", "juros_mensal"])

def adicionar_passivo(nome, tipo, valor, parcelas, juros):
    if supabase:
        try:
            supabase.table("passivos").insert({
                "nome": str(nome).strip(), "tipo": tipo, "valor_total": float(valor),
                "parcelas_restantes": int(parcelas), "juros_mensal": float(juros)
            }).execute()
        except Exception as e: st.error(f"Erro: {e}")

def remover_passivo(id_):
    if supabase:
        try: supabase.table("passivos").delete().eq("id", id_).execute()
        except: pass

def carregar_carteira():
    if supabase:
        try:
            res = supabase.table("carteira_invest").select("*").order("valor_atual", desc=True).execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "ativo", "classe", "valor_investido", "valor_atual", "data_aporte"])

def adicionar_investimento(ativo, classe, investido, atual, data_aporte):
    if supabase:
        try:
            supabase.table("carteira_invest").insert({
                "ativo": str(ativo).strip(), "classe": classe,
                "valor_investido": float(investido), "valor_atual": float(atual),
                "data_aporte": str(data_aporte)
            }).execute()
        except Exception as e: st.error(f"Erro: {e}")

def remover_investimento(id_):
    if supabase:
        try: supabase.table("carteira_invest").delete().eq("id", id_).execute()
        except: pass

def carregar_metas_financeiras():
    if supabase:
        try:
            res = supabase.table("metas_financeiras").select("*").order("prazo_anos").execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "nome", "valor_alvo", "valor_atual", "prazo_anos", "categoria"])

def adicionar_meta_financeira(nome, alvo, atual, prazo, categoria):
    if supabase:
        try:
            supabase.table("metas_financeiras").insert({
                "nome": str(nome).strip(), "valor_alvo": float(alvo),
                "valor_atual": float(atual), "prazo_anos": int(prazo), "categoria": categoria
            }).execute()
        except Exception as e: st.error(f"Erro: {e}")

def remover_meta_financeira(id_):
    if supabase:
        try: supabase.table("metas_financeiras").delete().eq("id", id_).execute()
        except: pass

def atualizar_valor_meta_financeira(id_, novo_valor):
    if supabase:
        try: supabase.table("metas_financeiras").update({"valor_atual": float(novo_valor)}).eq("id", id_).execute()
        except: pass

def carregar_rendas():
    if supabase:
        try:
            res = supabase.table("fontes_renda").select("*").order("ano", desc=True).order("mes", desc=True).execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "descricao", "valor", "mes", "ano", "tipo"])

def adicionar_renda(descricao, valor, mes, ano, tipo):
    if supabase:
        try:
            supabase.table("fontes_renda").insert({
                "descricao": str(descricao).strip(), "valor": float(valor),
                "mes": int(mes), "ano": int(ano), "tipo": tipo
            }).execute()
        except Exception as e: st.error(f"Erro: {e}")

def remover_renda(id_):
    if supabase:
        try: supabase.table("fontes_renda").delete().eq("id", id_).execute()
        except: pass

def carregar_protecoes():
    if supabase:
        try:
            res = supabase.table("protecoes").select("*").order("item").execute()
            if res.data: return pd.DataFrame(res.data)
        except: pass
    return pd.DataFrame(columns=["id", "item", "contratado", "observacao"])

def atualizar_protecao(item, contratado):
    if supabase:
        try:
            supabase.table("protecoes").update({
                "contratado": bool(contratado), "atualizado_em": datetime.now().isoformat()
            }).eq("item", item).execute()
        except: pass

def carregar_contas_pagar():
    if supabase:
        try:
            res = supabase.table("contas_pagar").select("*").order("vencimento").execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['vencimento'] = pd.to_datetime(df['vencimento'])
                return df
        except: pass
    return pd.DataFrame(columns=["id", "descricao", "valor", "vencimento", "pago", "categoria"])

def adicionar_conta_pagar(descricao, valor, vencimento, categoria):
    if supabase:
        try:
            supabase.table("contas_pagar").insert({
                "descricao": str(descricao).strip(), "valor": float(valor),
                "vencimento": str(vencimento), "categoria": categoria, "pago": False
            }).execute()
        except Exception as e: st.error(f"Erro: {e}")

def marcar_conta_paga(id_, pago=True):
    if supabase:
        try: supabase.table("contas_pagar").update({"pago": bool(pago)}).eq("id", id_).execute()
        except: pass

def remover_conta_pagar(id_):
    if supabase:
        try: supabase.table("contas_pagar").delete().eq("id", id_).execute()
        except: pass

def calcular_net_worth():
    ativos = carregar_ativos()
    passivos = carregar_passivos()
    total_a = ativos["valor"].sum() if not ativos.empty else 0.0
    total_p = passivos["valor_total"].sum() if not passivos.empty else 0.0
    return {"ativos": round(total_a, 2), "passivos": round(total_p, 2), "liquido": round(total_a - total_p, 2)}

def calcular_fire(gasto_mensal, patrimonio_atual=0.0, aporte_mensal=0.0, taxa_retirada=0.04, taxa_rendimento=0.07):
    if gasto_mensal <= 0: return None
    numero_magico = (gasto_mensal * 12) / taxa_retirada
    falta = max(0.0, numero_magico - patrimonio_atual)
    anos = None
    if aporte_mensal > 0 and falta > 0:
        r = taxa_rendimento / 12
        n_meses = 0
        saldo = patrimonio_atual
        while saldo < numero_magico and n_meses < 1200:
            saldo = saldo * (1 + r) + aporte_mensal
            n_meses += 1
        anos = n_meses / 12
    return {"numero_magico": round(numero_magico, 2), "falta": round(falta, 2),
            "anos_para_fire": round(anos, 1) if anos else None,
            "retirada_mensal_segura": round(numero_magico * taxa_retirada / 12, 2)}

def calcular_diagnostico_financeiro(receita_mensal, total_gastos, total_fixos, reserva_atual, ativos, passivos):
    if receita_mensal <= 0:
        return {"nota": 0, "detalhes": {}, "taxa_poupanca_pct": 0, "meses_reserva": 0}
    poupanca = receita_mensal - total_gastos
    taxa_poupanca = poupanca / receita_mensal
    pts_poupanca = min(25, max(0, taxa_poupanca * 100))
    meses_reserva = (reserva_atual / total_fixos) if total_fixos > 0 else 0
    pts_reserva = min(25, max(0, (meses_reserva / 6) * 25))
    pct_divida = passivos / (ativos + passivos) if (ativos + passivos) > 0 else 0
    pts_divida = max(0, 25 * (1 - pct_divida))
    pts_invest = min(15, max(0, (taxa_poupanca * 100 / 30) * 15))
    pts_divers = 10 if ativos > 0 else 0
    nota = round(pts_poupanca + pts_reserva + pts_divida + pts_invest + pts_divers, 1)
    return {"nota": nota,
            "detalhes": {"poupanca": round(pts_poupanca, 1), "reserva": round(pts_reserva, 1),
                         "divida": round(pts_divida, 1), "investimento": round(pts_invest, 1),
                         "diversificacao": round(pts_divers, 1)},
            "taxa_poupanca_pct": round(taxa_poupanca * 100, 1),
            "meses_reserva": round(meses_reserva, 1)}

def calcular_ordem_quitacao(passivos_df):
    if passivos_df.empty: return pd.DataFrame()
    df = passivos_df.copy()
    df["custo_juros_mensal"] = (df["valor_total"] * df["juros_mensal"] / 100).round(2)
    df = df.sort_values("juros_mensal", ascending=False).reset_index(drop=True)
    df["ordem"] = df.index + 1
    return df

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Parâmetros Financeiros")
if st.sidebar.button("🔒 Sair / Bloquear Tela", use_container_width=True):
    st.session_state['autenticado'] = False
    st.rerun()
st.sidebar.divider()

config = carregar_configuracoes()

st.sidebar.subheader("🔀 Simulação de Cenário")
cenario = st.sidebar.radio("Selecione o Cenário Ativo:",
                            options=["COM Participação de B", "SEM Participação de B (Contingência)"], index=0)
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
        aluguel_a_input = st.sidebar.number_input("Valor pago por A (R$)", min_value=0.0, max_value=float(aluguel_input), value=val_a_db, step=25.0)
        aluguel_b_input = max(0.0, aluguel_input - aluguel_a_input)
        st.sidebar.info(f"💡 Valor de B ajustado automaticamente: **R$ {aluguel_b_input:,.2f}**")
    else:
        aluguel_b_input = st.sidebar.number_input("Valor pago por B (R$)", min_value=0.0, max_value=float(aluguel_input), value=val_b_db, step=25.0)
        aluguel_a_input = max(0.0, aluguel_input - aluguel_b_input)
        st.sidebar.info(f"💡 Valor de A ajustado automaticamente: **R$ {aluguel_a_input:,.2f}**")
else:
    aluguel_a_input = val_a_db
    aluguel_b_input = val_b_db

if st.sidebar.button("💾 Salvar Parâmetros"):
    a_save = aluguel_a_input if edicao_manual else aluguel_input * 0.5
    b_save = aluguel_b_input if edicao_manual else aluguel_input * 0.5
    salvar_configuracoes(aluguel_input, salario_a_input, salario_b_input, vr_a_input, meta_reserva_input, a_save, b_save, edicao_manual)
    st.sidebar.success("Parâmetros salvos!")
    st.rerun()

# -----------------------------------------------------------------------------
# ENGINE DE CÁLCULO
# -----------------------------------------------------------------------------
if b_participa:
    if edicao_manual and aluguel_a_input is not None and aluguel_b_input is not None:
        aluguel_a, aluguel_b = aluguel_a_input, aluguel_b_input
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
# CORPO PRINCIPAL
# -----------------------------------------------------------------------------
st.title("📊 Painel de Projeção Econômica & Controle")
st.caption(f"Cenário Ativo: **{cenario}** | Alimentação protegida com VR de R$ {vr_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Líquido (A)", f"+ R$ {salario_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col2.metric("Sua Parte no Aluguel", f"- R$ {aluguel_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), delta=f"{prop_a*100:.1f}% do aluguel" if b_participa else "100% (Integral)")
col3.metric("Total Gastos Fixos (A)", f"- R$ {total_fixos_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col4.metric("Aporte Reserva Mensal", f"- R$ {meta_reserva_efetiva:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📌 Planejamento & Cenários", "💳 Controle de Gastos Diários",
    "⚙ Gerenciar Custos Fixos", "📈 Simulador de Investimentos",
    "📊 DRE & Análise de Lucro", "📑 Relatórios PDF",
    "📅 Relatório Mensal", "✂️ Cortes Inteligentes",
    "🚀 Prosperidade"
])

with tab1:
    st.subheader("🏠 Divisão e Proporcionalidade do Aluguel (A e B)")
    col_div1, col_div2, col_div3 = st.columns(3)
    col_div1.metric("Salário de A", f"+ R$ {salario_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_div2.metric("Salário de B", f"+ R$ {salario_b_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',') if b_participa else "R$ 0,00")
    col_div3.metric("Aluguel Total", f"R$ {aluguel_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_val1, col_val2 = st.columns(2)
    col_val1.info(f"👤 **Pessoa A vai pagar:** - R$ **{aluguel_a:,.2f}** ({prop_a*100:.1f}% do aluguel)".replace('.', '#').replace(',', '.').replace('#', ','))
    if b_participa:
        col_val2.success(f"👥 **Pessoa B vai pagar:** - R$ **{aluguel_b:,.2f}** ({prop_b*100:.1f}% do aluguel)".replace('.', '#').replace(',', '.').replace('#', ','))
    else:
        col_val2.warning("⚠️ **Pessoa B:** Sem participação (A assume 100%).")
    st.divider()
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("💡 Distribuição do Salário de A")
        dados_composicao = {"Categoria": ["Aluguel Proporcional", "Outros Custos Fixos", "Meta de Reserva", "Orçamento Variável Livre"],
                            "Valor": [aluguel_a, total_outros_fixos_a, meta_reserva_efetiva, max(0.0, saldo_para_variaveis)]}
        df_comp = pd.DataFrame(dados_composicao)
        fig_pie = px.pie(df_comp, names="Categoria", values="Valor", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_pie.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3")
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_right:
        st.subheader("🛡 Progresso Anual da Reserva")
        st.write(f"**Aporte Mensal:** R$ {meta_reserva_efetiva:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        st.write(f"**Meta Anual:** R$ {meta_reserva_efetiva * 12:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        st.markdown("##### 🗓️ Status dos Meses:")
        cols_grid = st.columns(4)
        meses_concluidos_count = 0
        for i, nome_mes in enumerate(meses_nomes):
            col_idx = i % 4
            with cols_grid[col_idx]:
                key_nome = f"reserva_mes_{i+1}"
                status = st.checkbox(f"{i+1}. {nome_mes}", key=key_nome)
                if status:
                    meses_concluidos_count += 1
                    st.markdown("<span style='color:#22C55E; font-size:12px;'>● pago</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#F59E0B; font-size:12px;'>⏳ pendente</span>", unsafe_allow_html=True)
        pct_concluido = meses_concluidos_count / 12.0
        montante_acumulado_real = meta_reserva_efetiva * meses_concluidos_count
        st.markdown("---")
        st.progress(pct_concluido)
        st.markdown(f"**Progresso:** {meses_concluidos_count} de 12 meses (**{pct_concluido * 100:.1f}%**)")
        st.write(f"Total depositado: **R$ {montante_acumulado_real:,.2f}**".replace('.', '#').replace(',', '.').replace('#', ','))

with tab2:
    st.subheader("🛒 Gerenciamento de Despesas Variáveis")
    col_lim1, col_lim2, col_lim3 = st.columns(3)
    col_lim1.metric("Orçamento Variável", f"R$ {saldo_para_variaveis:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_lim2.metric("Total Gasto", f"- R$ {total_gastos_variaveis:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_lim3.metric("Saldo Restante", f"{'+' if saldo_caixa_restante >=0 else '-'} R$ {abs(saldo_caixa_restante):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), delta_color="normal" if saldo_caixa_restante >= 0 else "inverse")
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
                    st.success("Despesa lançada!")
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
        st.write("#### Adicionar Gasto Fixo")
        with st.form("form_fixo", clear_on_submit=True):
            desc_fix = st.text_input("Descrição")
            val_fix = st.number_input("Valor Mensal (R$)", min_value=0.01, step=10.0)
            if st.form_submit_button("Cadastrar"):
                if desc_fix:
                    adicionar_gasto_fixo(desc_fix, val_fix)
                    st.rerun()

# =============================================================================
# TAB 4 — SIMULADOR DE INVESTIMENTO (Juros Compostos + CDI)
# =============================================================================
with tab4:
    st.subheader("📈 Simulador de Investimento — Juros Compostos & CDI")
    st.markdown("Simule cenários com **taxa fixa** ou **atrelados ao CDI**, salve no Supabase e compare estratégias.")

    # ---------- TAXA CDI ATUAL ----------
    cdi_atual = obter_taxa_cdi_atual()
    col_info1, col_info2 = st.columns([1, 3])
    with col_info1:
        if cdi_atual is not None:
            st.metric("📊 CDI Atual (a.a.)", f"{cdi_atual:.2f}%")
        else:
            st.metric("📊 CDI Atual (a.a.)", "—")
    with col_info2:
        if cdi_atual is not None:
            st.success(f"Taxa CDI obtida do Banco Central (SGS 4389). Atualizada automaticamente a cada 1h.", icon="✅")
        else:
            st.warning("Não foi possível consultar o CDI agora. Você pode informar manualmente abaixo.", icon="⚠️")

    st.divider()

    # ---------- ESCOLHA DO MODO ----------
    modo_taxa = st.radio(
        "Modalidade de rentabilidade:",
        ["🎯 Taxa fixa (% ao ano)", "📊 Atrelado ao CDI (% do CDI)"],
        horizontal=True,
        key="modo_taxa_sim"
    )

    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        aporte_sim = st.number_input("Aporte Mensal Utilizado (R$)",
                                       value=float(meta_reserva_efetiva), step=50.0,
                                       key="aporte_sim")
        anos_sim = st.slider("Horizonte de Tempo (Anos)", min_value=1, max_value=30,
                              value=5, key="anos_sim")
    with col_sim2:
        if modo_taxa.startswith("🎯"):
            taxa_anual_sim = st.slider("Rentabilidade Anual Estimada (% a.a.)",
                                        min_value=1.0, max_value=25.0, value=10.0, step=0.5,
                                        key="taxa_sim")
            cdi_ref = None
            nome_sim = st.text_input("Nome da simulação (para salvar)",
                                      placeholder="Ex: Cenário conservador 5 anos",
                                      key="nome_sim_fixa")
        else:
            cdi_manual = st.number_input(
                "CDI considerada (% a.a.) — 0 = usar a atual",
                min_value=0.0, max_value=30.0,
                value=float(cdi_atual) if cdi_atual else 13.65,
                step=0.25,
                key="cdi_manual"
            )
            percentual_cdi_sim = st.slider("% do CDI contratado", min_value=80, max_value=150,
                                             value=100, step=5, key="pct_cdi_sim")
            cdi_ref = cdi_manual if cdi_manual > 0 else (cdi_atual if cdi_atual else 13.65)
            taxa_anual_sim = cdi_ref * (percentual_cdi_sim / 100)
            st.info(f"**Taxa efetiva: {taxa_anual_sim:.2f}% a.a.** (base CDI {cdi_ref:.2f}% × {percentual_cdi_sim}%)")
            nome_sim = st.text_input("Nome da simulação (para salvar)",
                                      placeholder="Ex: CDB 110% CDI — 5 anos",
                                      key="nome_sim_cdi")

    # ---------- CÁLCULO ----------
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
                "Ano": m // 12, "Total Investido": total_investido,
                "Patrimônio Total": montante_atual,
                "Juros Acumulados": montante_atual - total_investido
            })

    if lista_projecao:
        df_proj = pd.DataFrame(lista_projecao)
        juros_totais = montante_atual - total_investido

        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Valor Total Acumulado",
                         f"+ R$ {montante_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        col_res2.metric("Total do Seu Bolso (Aporte)",
                         f"R$ {total_investido:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
        col_res3.metric("Rendimento (Juros)",
                         f"+ R$ {juros_totais:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

        st.markdown("")
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            if st.button("💾 Salvar esta simulação", use_container_width=True, key="btn_salvar_sim"):
                if not nome_sim.strip():
                    st.warning("Dê um nome à simulação antes de salvar.")
                else:
                    ok = salvar_simulacao_investimento(
                        nome_sim, aporte_sim, anos_sim, taxa_anual_sim,
                        montante_atual, total_investido, juros_totais,
                        cdi_taxa=cdi_ref
                    )
                    if ok:
                        st.success(f"Simulação '{nome_sim}' salva com sucesso!")
                        st.rerun()

        st.divider()
        if modo_taxa.startswith("📊") and cdi_atual is not None:
            # Gráfico comparativo especial para CDI
            fig_invest = gerar_grafico_projecao_cdi(df_proj, 0.0, aporte_sim)
            st.plotly_chart(fig_invest, use_container_width=True)
        else:
            fig_invest = px.area(df_proj, x="Ano", y=["Patrimônio Total", "Total Investido"],
                                  title="Evolução Patrimonial Projetada")
            fig_invest.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3")
            st.plotly_chart(fig_invest, use_container_width=True)

    st.divider()

    # =====================================================
    # ANÁLISE COMPARATIVA CDI (apenas no modo CDI)
    # =====================================================
    if modo_taxa.startswith("📊") and cdi_atual is not None:
        st.markdown("### 🎯 Comparativo de Produtos de Renda Fixa")
        st.caption("Veja quanto renderiam diferentes produtos atrelados ao CDI com os mesmos aportes.")

        produtos = [
            ("Poupança", 70, "#8A95A5"),
            ("Tesouro Selic", 100, "#3B82F6"),
            ("CDB 100% CDI", 100, "#06B6D4"),
            ("CDB 110% CDI", 110, "#22C55E"),
            ("LCI/LCA 90% CDI", 90, "#7C3AED"),
            ("CDB 120% CDI", 120, "#F59E0B"),
        ]

        resultados = []
        for nome_prod, pct, cor in produtos:
            proj = calcular_projecao_cdi(0.0, aporte_sim, anos_sim, pct, cdi_ref)
            if proj:
                resultados.append({
                    "Produto": nome_prod,
                    "Percentual do CDI": f"{pct}%",
                    "Taxa Efetiva (% a.a.)": round(cdi_ref * pct / 100, 2),
                    "Montante Final": proj["montante_final"],
                    "Juros Totais": proj["juros_totais"],
                    "_cor": cor,
                })

        if resultados:
            df_prod = pd.DataFrame(resultados)
            df_show = df_prod.drop(columns=["_cor"]).copy()
            df_show["Montante Final"] = df_show["Montante Final"].apply(_fmt_brl)
            df_show["Juros Totais"] = df_show["Juros Totais"].apply(_fmt_brl)
            df_show["Taxa Efetiva (% a.a.)"] = df_show["Taxa Efetiva (% a.a.)"].apply(lambda v: f"{v:.2f}%")
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            fig_cmp = px.bar(
                df_prod, x="Produto", y="Montante Final",
                color="Produto", color_discrete_sequence=[r["_cor"] for r in resultados],
                title=f"Comparativo de Produtos (CDI base {cdi_ref:.2f}% a.a.)"
            )
            fig_cmp.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                   font_color="#E6EDF3", showlegend=False, xaxis_tickangle=-25)
            st.plotly_chart(fig_cmp, use_container_width=True)

    st.divider()

    # =====================================================
    # HISTÓRICO DE CDI (últimos 30 dias)
    # =====================================================
    if cdi_atual is not None:
        with st.expander("📉 Ver histórico recente do CDI (Banco Central)"):
            df_hist_cdi = obter_historico_cdi(30)
            if not df_hist_cdi.empty:
                fig_cdi = px.line(df_hist_cdi, x="data", y="valor", markers=True,
                                   title="Taxa CDI (últimos 30 dias úteis)")
                fig_cdi.update_traces(line_color="#22C55E")
                fig_cdi.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                       font_color="#E6EDF3", height=260)
                st.plotly_chart(fig_cdi, use_container_width=True)
                st.caption(f"Fonte: Banco Central do Brasil — Série SGS 4389 · "
                            f"Média: {df_hist_cdi['valor'].mean():.2f}% · "
                            f"Máx: {df_hist_cdi['valor'].max():.2f}% · "
                            f"Mín: {df_hist_cdi['valor'].min():.2f}%")
            else:
                st.info("Não foi possível carregar o histórico do CDI.")

    st.divider()

    # =====================================================
    # SIMULAÇÕES SALVAS
    # =====================================================
    st.markdown("### 📂 Simulações Salvas")
    df_sims = carregar_simulacoes_investimento()

    if df_sims.empty:
        st.info("Nenhuma simulação salva ainda. Ajuste os parâmetros acima e clique em **💾 Salvar esta simulação**.")
    else:
        total_sims = len(df_sims)
        melhor = df_sims.loc[df_sims["montante_final"].idxmax()]
        st.markdown(
            f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
            f"border-radius:12px;padding:14px 18px;margin-bottom:12px;'>"
            f"<b style='color:{PALETA['texto_principal']};'>📊 {total_sims} simulações salvas</b> · "
            f"<span style='color:{PALETA['texto_secundario']};'>Melhor resultado: "
            f"<b style='color:{PALETA['verde']};'>{melhor['nome']}</b> com "
            f"R$ {melhor['montante_final']:,.2f}</span></div>",
            unsafe_allow_html=True
        )

        cols_disp = ["id", "nome", "aporte_mensal", "anos", "taxa_anual",
                      "montante_final", "total_investido", "juros_totais", "criado_em"]
        if "cdi_taxa_utilizada" in df_sims.columns:
            cols_disp.insert(-1, "cdi_taxa_utilizada")

        df_show = df_sims[cols_disp].copy()
        df_show["aporte_mensal"]  = df_show["aporte_mensal"].apply(lambda v: _fmt_brl(v))
        df_show["taxa_anual"]     = df_show["taxa_anual"].apply(lambda v: f"{v:.2f}%")
        df_show["montante_final"] = df_show["montante_final"].apply(lambda v: _fmt_brl(v))
        df_show["total_investido"]= df_show["total_investido"].apply(lambda v: _fmt_brl(v))
        df_show["juros_totais"]   = df_show["juros_totais"].apply(lambda v: _fmt_brl(v))
        df_show["anos"]           = df_show["anos"].apply(lambda v: f"{int(v)} anos")
        df_show["criado_em"]      = pd.to_datetime(df_show["criado_em"]).dt.strftime("%d/%m/%Y %H:%M")
        if "cdi_taxa_utilizada" in df_show.columns:
            df_show["cdi_taxa_utilizada"] = df_show["cdi_taxa_utilizada"].apply(
                lambda v: f"{v:.2f}%" if pd.notnull(v) else "—"
            )
            df_show.columns = ["ID", "Nome", "Aporte Mensal", "Prazo", "Taxa Anual",
                                "Montante Final", "Total Investido", "Juros",
                                "CDI Base", "Salvo em"]
        else:
            df_show.columns = ["ID", "Nome", "Aporte Mensal", "Prazo", "Taxa Anual",
                                "Montante Final", "Total Investido", "Juros", "Salvo em"]

        st.dataframe(df_show.drop(columns=["ID"]), use_container_width=True, hide_index=True)

        st.markdown("#### 📊 Comparação entre simulações salvas")
        fig_cmp = px.bar(df_sims.sort_values("montante_final", ascending=True),
                          x="montante_final", y="nome", orientation="h",
                          color="montante_final",
                          color_continuous_scale=["#3B82F6", "#22C55E"],
                          labels={"montante_final": "Montante Final (R$)", "nome": ""})
        fig_cmp.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                               font_color="#E6EDF3", showlegend=False,
                               coloraxis_showscale=False, height=max(200, 60 * len(df_sims)))
        st.plotly_chart(fig_cmp, use_container_width=True)

        st.markdown("#### 🗑️ Excluir simulação")
        cols_del = st.columns(min(4, len(df_sims)))
        for i, (_, s) in enumerate(df_sims.iterrows()):
            with cols_del[i % 4]:
                if st.button(f"🗑️ {s['nome'][:20]}", key=f"del_sim_{s['id']}", use_container_width=True):
                    remover_simulacao_investimento(s["id"])
                    st.success(f"Simulação '{s['nome']}' removida.")
                    st.rerun()

with tab5:
    st.subheader("📊 DRE Gerencial & Análise de Lucratividade")
    receita_bruta = salario_a_input + vr_a_input
    custos_fixos_dre = total_fixos_a
    despesas_var_dre = total_gastos_variaveis
    lucro_operacional = receita_bruta - custos_fixos_dre - despesas_var_dre
    margem_lucro = (lucro_operacional / receita_bruta) * 100 if receita_bruta > 0 else 0.0
    col_dre1, col_dre2, col_dre3 = st.columns(3)
    col_dre1.metric("Receita Bruta", f"+ R$ {receita_bruta:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_dre2.metric("Lucro Operacional", f"{'+' if lucro_operacional >=0 else '-'} R$ {abs(lucro_operacional):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), delta=f"{margem_lucro:.1f}% Margem")
    reserva_acumulada_teorica = meta_reserva_efetiva * 6
    runway_meses = reserva_acumulada_teorica / total_fixos_a if total_fixos_a > 0 else 0
    col_dre3.metric("Runway", f"{runway_meses:.1f} Meses", delta="Cobertura de Caixa")
    st.divider()
    dados_dre = [
        ["Conta / Indicador", "Valor (R$)", "% da Receita Bruta"],
        ["(+) Receita Bruta (Salário + VR)", f"+ R$ {receita_bruta:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), "100.0%"],
        ["(-) Custos Fixos", f"- R$ {custos_fixos_dre:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), f"{(custos_fixos_dre/receita_bruta)*100:.1f}%" if receita_bruta > 0 else "0.0%"],
        ["(-) Despesas Variáveis", f"- R$ {despesas_var_dre:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), f"{(despesas_var_dre/receita_bruta)*100:.1f}%" if receita_bruta > 0 else "0.0%"],
        ["(=) LUCRO LÍQUIDO", f"{'+' if lucro_operacional >=0 else '-'} R$ {abs(lucro_operacional):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), f"{margem_lucro:.1f}%"]
    ]
    df_dre_tabela = pd.DataFrame(dados_dre[1:], columns=dados_dre[0])
    st.table(df_dre_tabela)
    st.markdown("#### 🔍 Diagnóstico de Ladrões de Lucro")
    if not df_variaveis.empty:
        df_cat_analise = df_variaveis.groupby("categoria")["valor"].sum().reset_index()
        maior_gasto = df_cat_analise.loc[df_cat_analise["valor"].idxmax()]
        st.warning(f"⚠️ **Maior ralo de caixa:** **{maior_gasto['categoria']}** consumiu **R$ {maior_gasto['valor']:,.2f}**.".replace('.', '#').replace(',', '.').replace('#', ','))
    else:
        st.success("🟢 Nenhuma distorção crítica.")

with tab6:
    st.subheader("📑 Central de Relatórios em PDF")
    pdf_bytes = gerar_relatorio_pdf(df_gastos_fixos, df_variaveis, salario_a_input, salario_b_input, aluguel_a, aluguel_b)
    st.download_button(label="📥 Baixar Relatório Completo em PDF", data=pdf_bytes,
                        file_name=f"Relatorio_Financeiro_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf", use_container_width=True)

with tab7:
    st.subheader("📅 Relatório Mensal & Orçamento por Mês")
    hoje = datetime.now()
    col_m1, col_m2, col_m3 = st.columns(3)
    mes_sel = col_m1.selectbox("Mês de Referência", options=list(range(1, 13)),
                                format_func=lambda x: meses_nomes[x - 1], index=hoje.month - 1)
    ano_sel = col_m2.number_input("Ano", min_value=2020, max_value=2100, value=hoje.year, step=1)
    orc_mes = carregar_orcamento_mes(mes_sel, ano_sel)
    orcamento_valor = float(orc_mes.get("orcamento", 0.0) or 0.0)
    mes_fechado = bool(orc_mes.get("fechado", False))
    if mes_fechado: col_m3.error("🔒 Mês Fechado")
    else: col_m3.success("🟢 Mês Aberto")
    st.divider()
    with st.expander("💼 Definir Orçamento do Mês", expanded=(orcamento_valor == 0.0)):
        novo_orc = st.number_input("Orçamento (R$)", min_value=0.0, value=orcamento_valor, step=50.0, key=f"orc_{mes_sel}_{ano_sel}")
        col_o1, col_o2 = st.columns(2)
        if col_o1.button("💾 Salvar Orçamento", use_container_width=True):
            salvar_orcamento_mes(mes_sel, ano_sel, novo_orc)
            st.success("Orçamento salvo!"); st.rerun()
        if col_o2.button("🔒 Fechar Mês e Iniciar Novo Ciclo", use_container_width=True):
            fechar_mes(mes_sel, ano_sel)
            prox_mes = 1 if mes_sel == 12 else mes_sel + 1
            prox_ano = ano_sel + 1 if mes_sel == 12 else ano_sel
            carregar_orcamento_mes(prox_mes, prox_ano)
            st.success(f"Mês {meses_nomes[mes_sel-1]}/{ano_sel} fechado! Novo: {meses_nomes[prox_mes-1]}/{prox_ano}.")
            st.rerun()
    df_mes = carregar_despesas_por_mes(mes_sel, ano_sel)
    total_gasto_mes = df_mes["valor"].sum() if not df_mes.empty else 0.0
    saldo_mes = orcamento_valor - total_gasto_mes
    pct_uso = (total_gasto_mes / orcamento_valor * 100) if orcamento_valor > 0 else 0.0
    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("Orçamento", f"R$ {orcamento_valor:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    cm2.metric("Total Gasto", f"- R$ {total_gasto_mes:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    cm3.metric("Saldo Restante", f"{'+' if saldo_mes >= 0 else '-'} R$ {abs(saldo_mes):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','), delta_color="normal" if saldo_mes >= 0 else "inverse")
    cm4.metric("% Utilizado", f"{pct_uso:.1f}%")
    if orcamento_valor > 0:
        st.progress(min(pct_uso / 100, 1.0))
        if pct_uso >= 100: st.error(f"🚨 Orçamento estourado! Ultrapassou em R$ {abs(saldo_mes):,.2f}")
        elif pct_uso >= 80: st.warning(f"⚠️ {pct_uso:.1f}% do orçamento utilizado.")
        else: st.success(f"✅ Dentro do orçamento ({pct_uso:.1f}%).")
    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### 📊 Gastos por Categoria")
        if not df_mes.empty:
            df_cat = df_mes.groupby("categoria")["valor"].sum().reset_index()
            fig_cat = px.bar(df_cat, x="categoria", y="valor", color="categoria", color_discrete_sequence=px.colors.qualitative.Set2)
            fig_cat.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3", showlegend=False)
            st.plotly_chart(fig_cat, use_container_width=True)
        else: st.info("Sem despesas no mês.")
    with col_g2:
        st.markdown("#### 📋 Detalhamento")
        if not df_mes.empty:
            df_show = df_mes.copy()
            df_show["data"] = df_show["data"].dt.strftime("%d/%m/%Y")
            df_show = df_show[["data", "descricao", "categoria", "valor"]]
            df_show.columns = ["Data", "Descrição", "Categoria", "Valor (R$)"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else: st.info("Nenhuma despesa neste mês.")
    st.divider()
    st.markdown("#### 📥 Exportar Relatório Mensal")
    pdf_mes = gerar_relatorio_mensal_pdf(mes_sel, ano_sel, df_mes, orcamento_valor)
    st.download_button(label=f"📥 Baixar Relatório de {meses_nomes[mes_sel-1]}/{ano_sel} em PDF",
                        data=pdf_mes, file_name=f"Relatorio_{meses_nomes[mes_sel-1]}_{ano_sel}.pdf",
                        mime="application/pdf", use_container_width=True)
    st.divider()
    st.markdown("#### 🗂 Histórico de Meses")
    df_hist = listar_meses_fechados()
    if not df_hist.empty:
        df_hist["Mês"] = df_hist["mes"].apply(lambda x: meses_nomes[int(x) - 1])
        df_hist = df_hist.rename(columns={"ano": "Ano", "orcamento": "Orçamento (R$)", "fechado": "Fechado"})
        df_hist["Fechado"] = df_hist["Fechado"].apply(lambda x: "🔒 Sim" if x else "🟢 Não")
        st.dataframe(df_hist[["Mês", "Ano", "Orçamento (R$)", "Fechado"]], use_container_width=True, hide_index=True)
    else: st.info("Nenhum mês registrado ainda.")

# =============================================================================
# ABA 8 — CORTES
# =============================================================================
with tab8:
    st.subheader("✂️ Cortes Inteligentes — Onde você deve economizar")

    receita_bruta_corte = salario_a_input + vr_a_input
    df_sug = analisar_cortes_inteligentes(df_variaveis, df_gastos_fixos, receita_bruta_corte,
                                           meta_reserva_mensal=meta_reserva_efetiva)
    df_cortes_concluidos = carregar_cortes_concluidos()

    meta_poup = calcular_meta_poupanca_ideal(
        receita_bruta_corte, total_fixos_a, total_gastos_variaveis,
        meta_reserva_efetiva, taxa_ideal=0.20
    )

    if meta_poup:
        st.markdown("### 🎯 Meta Ideal de Poupança")
        st.caption("Padrão financeiro recomendado: poupar **20% da renda bruta** por mês.")
        mp1, mp2, mp3 = st.columns(3)
        mp1.metric("Meta Ideal (R$/mês)", _fmt_brl(meta_poup["meta_ideal_valor"]), delta=f"{meta_poup['meta_ideal_pct']}% da renda")
        mp2.metric("Poupança Atual (R$/mês)", _fmt_brl(meta_poup["poupanca_atual"]), delta=f"{meta_poup['poupanca_atual_pct']}% da renda")
        falta_delta = f"-{meta_poup['falta_pct']}% abaixo do ideal" if meta_poup["falta_valor"] > 0 else "Meta atingida"
        mp3.metric("Falta Poupar (R$/mês)", _fmt_brl(meta_poup["falta_valor"]), delta=falta_delta,
                    delta_color="inverse" if meta_poup["falta_valor"] > 0 else "normal")
        st.markdown(
            f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
            f"border-radius:12px;padding:16px 20px;margin:10px 0;'>"
            f"<div style='display:flex;justify-content:space-between;'>"
            f"<b style='color:{PALETA['texto_principal']};'>Progresso da Meta de Poupança</b>"
            f"<span style='color:{meta_poup['status_cor']};font-weight:700;'>"
            f"{meta_poup['status_emoji']} {meta_poup['status_txt']} — {int(meta_poup['progresso']*100)}%</span></div>"
            f"<div style='color:{PALETA['texto_secundario']};font-size:12px;margin-top:6px;'>"
            f"Você poupa hoje <b style='color:{PALETA['texto_principal']};'>{_fmt_brl(meta_poup['poupanca_atual'])}</b> "
            f"({meta_poup['poupanca_atual_pct']}%) · "
            f"Meta: <b style='color:{PALETA['texto_principal']};'>{_fmt_brl(meta_poup['meta_ideal_valor'])}</b> "
            f"({meta_poup['meta_ideal_pct']}%) · "
            f"Faltam: <b style='color:{meta_poup['status_cor']};'>{_fmt_brl(meta_poup['falta_valor'])}</b> "
            f"({meta_poup['falta_pct']}%)</div></div>",
            unsafe_allow_html=True
        )
        st.progress(meta_poup["progresso"])
        st.divider()

    if df_sug.empty:
        st.success("🟢 Nenhuma categoria está acima do benchmark saudável.")
    else:
        total_anual = df_sug["economia_potencial"].sum()
        total_mensal = df_sug["corte_sugerido"].sum()
        top_cat = df_sug.iloc[0]

        ck1, ck2, ck3 = st.columns(3)
        ck1.metric("💸 Economia Mensal", _fmt_brl(total_mensal))
        ck2.metric("💰 Economia Anual", _fmt_brl(total_anual))
        ck3.metric("🎯 Prioridade #1", top_cat["categoria"])
        st.divider()

        st.markdown("### 📊 Quanto reduzir em cada categoria (R$ e %)")
        df_por_cat = calcular_poupanca_por_categoria(df_sug, receita_bruta_corte)
        if not df_por_cat.empty:
            df_show = df_por_cat.copy()
            for col in ["Gasto Atual (R$)", "Ideal (R$)", "Reduzir (R$)"]:
                df_show[col] = df_show[col].apply(lambda v: _fmt_brl(v))
            df_show["Reduzir (%)"]    = df_show["Reduzir (%)"].apply(lambda v: f"{v:.1f}%")
            df_show["Peso Atual (%)"] = df_show["Peso Atual (%)"].apply(lambda v: f"{v:.1f}%")
            df_show["Peso Ideal (%)"] = df_show["Peso Ideal (%)"].apply(lambda v: f"{v:.1f}%")
            st.dataframe(df_show, use_container_width=True, hide_index=True)
            total_reduzir = df_por_cat["Reduzir (R$)"].sum()
            total_reduzir_pct = (total_reduzir / receita_bruta_corte * 100) if receita_bruta_corte > 0 else 0
            st.markdown(
                f"<div style='background:{PALETA['fundo_card']};border-left:4px solid {PALETA['acento']};"
                f"border-radius:10px;padding:14px 18px;margin-top:10px;'>"
                f"<b style='color:{PALETA['texto_principal']};'>💡 Total a reduzir:</b> "
                f"<b style='color:{PALETA['verde']};font-size:16px;'>{_fmt_brl(total_reduzir)}/mês</b> "
                f"<span style='color:{PALETA['texto_secundario']};'>"
                f"({total_reduzir_pct:.1f}% da renda) · {_fmt_brl(total_reduzir * 12)}/ano</span></div>",
                unsafe_allow_html=True
            )
        st.divider()

        st.markdown("### 🏆 Análise Detalhada por Categoria")
        economia_max = df_sug["economia_potencial"].max()

        for _, s in df_sug.iterrows():
            cor = "#EF4444" if s["prioridade"] <= 2 else ("#F59E0B" if s["prioridade"] <= 4 else "#3B82F6")
            ja_concluido = s["categoria_limpa"] in df_cortes_concluidos['categoria'].tolist() if not df_cortes_concluidos.empty else False
            valor_ideal = receita_bruta_corte * s['benchmark_saudavel'] / 100
            reduzir_valor = max(0.0, s['valor_atual'] - valor_ideal)
            reduzir_pct = (reduzir_valor / s['valor_atual'] * 100) if s['valor_atual'] > 0 else 0
            status_badge = " ✅ <span style='color:#22C55E;'>já concluído</span>" if ja_concluido else ""

            card_html = f"""
<div style="background:{PALETA['fundo_card']}; border:1px solid {PALETA['borda']};
            border-left:4px solid {cor}; border-radius:10px;
            padding:14px 18px; margin-bottom:10px;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <span style="color:{cor}; font-weight:700; font-size:14px;">
                #{int(s['prioridade'])} — {s['categoria']}
            </span>
            <span style="color:{PALETA['texto_secundario']}; font-size:11px; margin-left:8px;">
                [{s['tipo']}]{status_badge}
            </span>
        </div>
        <div style="color:{PALETA['verde']}; font-weight:700; font-size:15px;">
            Reduzir: {_fmt_brl(reduzir_valor)} ({reduzir_pct:.1f}%)
        </div>
    </div>
    <div style="color:{PALETA['texto_secundario']}; font-size:12px; margin-top:6px;">
        Atual: <b style="color:{PALETA['texto_principal']};">{_fmt_brl(s['valor_atual'])}</b>
        &nbsp;→&nbsp; Ideal: <b style="color:{PALETA['texto_principal']};">{_fmt_brl(valor_ideal)}</b>
        &nbsp;|&nbsp; Peso: <b style="color:{cor};">{s['peso_receita']}%</b>
        (benchmark: {s['benchmark_saudavel']}%)
    </div>
</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)

            with st.expander(f"📖 Análise completa de {s['categoria_limpa']}", expanded=False):
                st.markdown(
                    f"<div style='background:{PALETA['fundo_sidebar']};border:1px solid {PALETA['borda']};"
                    f"border-radius:10px;padding:16px 20px;color:{PALETA['texto_principal']};"
                    f"font-size:13px;line-height:1.6;margin-bottom:14px;'>{s['explicacao']}</div>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div style='background:{PALETA['fundo_sidebar']};border-left:3px solid {PALETA['verde']};"
                    f"border-radius:8px;padding:12px 16px;margin-bottom:14px;'>"
                    f"<b style='color:{PALETA['verde']};'>💰 Meta direta:</b> "
                    f"<b style='color:{PALETA['texto_principal']};'>{_fmt_brl(reduzir_valor)}/mês</b> "
                    f"<span style='color:{PALETA['texto_secundario']};'>= <b>{reduzir_pct:.1f}%</b> de redução · "
                    f"<b>{_fmt_brl(reduzir_valor*12)}/ano</b></span></div>",
                    unsafe_allow_html=True
                )
                matriz = classificar_matriz_esforco(s['categoria_limpa'], s['economia_potencial'], economia_max)
                st.markdown(
                    f"<div style='background:{PALETA['fundo_sidebar']};border-left:3px solid {matriz['cor']};"
                    f"border-radius:8px;padding:12px 16px;margin-bottom:14px;'>"
                    f"<b style='color:{matriz['cor']};'>{matriz['emoji']} Matriz Esforço × Impacto:</b> "
                    f"<span style='color:{PALETA['texto_principal']};'>{matriz['quadrante']}</span><br>"
                    f"<span style='color:{PALETA['texto_secundario']};font-size:12px;'>→ {matriz['acao']}</span>"
                    f"</div>", unsafe_allow_html=True
                )
                horas = calcular_custo_hora(s['valor_atual'], salario_a_input)
                st.markdown(
                    f"<div style='background:{PALETA['fundo_sidebar']};border:1px solid {PALETA['borda']};"
                    f"border-radius:8px;padding:12px 16px;margin-bottom:14px;color:{PALETA['texto_principal']};'>"
                    f"⏱️ <b>Horas de trabalho:</b> você gasta <b>{horas}h</b> em '{s['categoria_limpa']}'.</div>",
                    unsafe_allow_html=True
                )
                st.markdown("##### 🎛️ Simulador: e se eu cortar X%?")
                col_sim = st.columns([2, 3])
                with col_sim[0]:
                    pct_sim = st.slider("Percentual de corte", min_value=5, max_value=80,
                                         value=int(reduzir_pct) if reduzir_pct >= 5 else 30,
                                         step=5, key=f"slider_{s['categoria_limpa']}")
                sim = simular_corte(s['valor_atual'], pct_sim)
                with col_sim[1]:
                    st.markdown(
                        f"<div style='color:{PALETA['texto_principal']};padding-top:8px;'>"
                        f"💰 Economia mensal: <b style='color:{PALETA['verde']};'>{_fmt_brl(sim['economia_mensal'])}</b><br>"
                        f"📅 Economia anual: <b style='color:{PALETA['verde']};'>{_fmt_brl(sim['economia_anual'])}</b>"
                        f"</div>", unsafe_allow_html=True
                    )
                impacto = impacto_na_reserva(sim['economia_mensal'], meta_reserva_efetiva, total_fixos_a)
                if impacto:
                    st.markdown(
                        f"<div style='background:{PALETA['fundo_sidebar']};border-left:3px solid {PALETA['acento']};"
                        f"border-radius:8px;padding:12px 16px;margin-top:10px;color:{PALETA['texto_principal']};'>"
                        f"🛡️ <b>Impacto na reserva:</b> +<b>{impacto['meses_extra_por_ano']}</b> meses de runway/ano · "
                        f"<b>{impacto['pct_meta_reserva']}%</b> da meta mensal.</div>",
                        unsafe_allow_html=True
                    )
                proj = projetar_longo_prazo(sim['economia_mensal'], 0.10)
                st.markdown(
                    f"<div style='background:{PALETA['fundo_sidebar']};border-left:3px solid {PALETA['roxo']};"
                    f"border-radius:8px;padding:12px 16px;margin-top:10px;color:{PALETA['texto_principal']};'>"
                    f"📈 <b>Investindo a 10% a.a.:</b> 1a: <b>{_fmt_brl(proj['1_ano'])}</b> · "
                    f"5a: <b>{_fmt_brl(proj['5_anos'])}</b> · 10a: <b>{_fmt_brl(proj['10_anos'])}</b> · "
                    f"20a: <b style='color:{PALETA['verde']};'>{_fmt_brl(proj['20_anos'])}</b></div>",
                    unsafe_allow_html=True
                )
                evolucao = evolucao_mensal_categoria(s['categoria_limpa'], df_variaveis, meses=6)
                if not evolucao.empty and len(evolucao) >= 2:
                    fig_evo = px.line(evolucao, x="mes_ano", y="valor", markers=True,
                                       color_discrete_sequence=[PALETA['acento']])
                    fig_evo.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                           font_color="#E6EDF3", height=220,
                                           margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig_evo, use_container_width=True, key=f"evo_{s['categoria_limpa']}")
                retro = detectar_retrocesso(s['categoria_limpa'], df_variaveis)
                if retro:
                    st.warning(f"⚠️ '{s['categoria_limpa']}' subiu {retro['variacao']}% vs mês anterior.")
                st.markdown("---")
                if ja_concluido:
                    st.success("✅ Corte já marcado.")
                else:
                    if st.button(f"✅ Marcar '{s['categoria_limpa']}' como concluído",
                                 key=f"btn_concl_{s['categoria_limpa']}", use_container_width=True):
                        hoje_ = datetime.now()
                        marcar_corte_concluido(s['categoria_limpa'], reduzir_valor, hoje_.month, hoje_.year)
                        st.success("Corte registrado!")
                        st.rerun()

        st.divider()

        df_metas = carregar_metas_corte()
        if not df_metas.empty:
            st.markdown("### 📈 Progresso das Metas de Corte Ativas")
            for _, meta in df_metas.iterrows():
                prog = calcular_progresso_meta_corte(meta['categoria'], float(meta['meta_reducao_pct']), df_variaveis)
                if prog is None: continue
                pct = prog['progresso']
                if pct >= 0.75: cor_prog, label = "#22C55E", "🟢 No caminho"
                elif pct >= 0.40: cor_prog, label = "#F59E0B", "🟡 Atenção"
                else: cor_prog, label = "#EF4444", "🔴 Não está cortando"
                st.markdown(
                    f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
                    f"border-radius:10px;padding:14px 18px;margin-bottom:8px;'>"
                    f"<div style='display:flex;justify-content:space-between;'>"
                    f"<b style='color:{PALETA['texto_principal']};'>🎯 {meta['categoria']} (-{meta['meta_reducao_pct']}%)</b>"
                    f"<span style='color:{cor_prog};font-weight:600;'>{label} — {int(pct*100)}%</span></div>"
                    f"<div style='color:{PALETA['texto_secundario']};font-size:12px;margin-top:4px;'>"
                    f"Média: {_fmt_brl(prog['media_passado'])} · Atual: <b style='color:{PALETA['texto_principal']};'>{_fmt_brl(prog['atual'])}</b> · "
                    f"Alvo: {_fmt_brl(prog['alvo'])} · Economia: <b style='color:{PALETA['verde']};'>{_fmt_brl(prog['economia_atual'])}</b>"
                    f"</div></div>", unsafe_allow_html=True
                )
                st.progress(pct)
            st.divider()

        st.markdown("### 🔎 Assinaturas Recorrentes")
        assinaturas = detectar_assinaturas(df_variaveis)
        if assinaturas.empty: st.info("Nenhuma assinatura detectada.")
        else:
            total_ass_anual = assinaturas["total_anual"].sum()
            st.warning(f"💡 **Potencial:** {_fmt_brl(total_ass_anual)}/ano ({_fmt_brl(total_ass_anual/12)}/mês).")
            st.dataframe(assinaturas, use_container_width=True, hide_index=True)
        st.divider()

        st.markdown("### 👻 Gastos Invisíveis")
        invisiveis = detectar_gastos_invisiveis(df_variaveis, limite_valor=60)
        if invisiveis.empty: st.info("Nenhum gasto invisível detectado.")
        else:
            total_inv_anual = invisiveis["total_anual"].sum()
            st.warning(f"💡 Pequenos gastos somam {_fmt_brl(total_inv_anual)}/ano ({_fmt_brl(total_inv_anual/12)}/mês).")
            st.dataframe(invisiveis, use_container_width=True, hide_index=True)
        st.divider()

        st.markdown("### 📋 Checklist de Ações da Semana")
        hoje_sem = datetime.now()
        semana_str = f"{hoje_sem.year}-W{hoje_sem.isocalendar()[1]:02d}"
        if st.button("🔄 Gerar checklist desta semana", key="btn_checklist_final"):
            tarefas = gerar_checklist_semanal(df_sug, df_cortes_concluidos)
            if tarefas:
                salvar_checklist_semanal(tarefas, semana_str)
                st.success(f"Checklist criado com {len(tarefas)} tarefas!")
                st.rerun()
            else: st.info("Todas as sugestões já foram concluídas. 🎉")
        df_checklist = carregar_checklist_semana(semana_str)
        if not df_checklist.empty:
            concluidas = df_checklist[df_checklist['concluida'] == True]
            total = len(df_checklist)
            pct_concluido = len(concluidas) / total if total > 0 else 0
            st.progress(pct_concluido)
            st.markdown(f"**Progresso:** {len(concluidas)}/{total} tarefas (**{pct_concluido*100:.0f}%**)")
            for _, t in df_checklist.iterrows():
                c1, c2, c3 = st.columns([0.5, 4, 1.5])
                with c1:
                    marcada = st.checkbox("", value=bool(t['concluida']), key=f"chk_{t['id']}")
                with c2:
                    texto = f"~~{t['acao']}~~" if marcada else t['acao']
                    st.markdown(texto)
                with c3:
                    st.markdown(f"<span style='color:{PALETA['verde']};'>💰 {_fmt_brl(t['economia_estimada'])}</span>", unsafe_allow_html=True)
                if marcada != bool(t['concluida']):
                    marcar_item_checklist(t['id'], marcada)
                    st.rerun()
        st.divider()

        st.markdown("### 📈 Projeção de Economia Acumulada")
        col_h1, col_h2 = st.columns([1, 1])
        with col_h1:
            horizonte = st.slider("Horizonte (meses)", 6, 36, 24, 6, key="horizonte_proj_f")
        with col_h2:
            redirecionar = st.checkbox("Reinvestir a 10% a.a.", value=False, key="reinves_proj_f")
        lista_eixo = list(range(1, horizonte + 1))
        economia_acumulada = []
        valor_total = 0.0
        if redirecionar:
            taxa_m = (1 + 0.10) ** (1/12) - 1
            saldo = 0.0
            for _ in lista_eixo:
                saldo = (saldo + total_mensal) * (1 + taxa_m)
                economia_acumulada.append(saldo)
            valor_total = saldo
        else:
            for m in lista_eixo:
                economia_acumulada.append(total_mensal * m)
            valor_total = total_mensal * horizonte
        df_proj_eco = pd.DataFrame({"Mês": lista_eixo, "Economia Acumulada": economia_acumulada})
        fig_proj_eco = px.area(df_proj_eco, x="Mês", y="Economia Acumulada",
                                title=f"Economia acumulada em {horizonte} meses")
        fig_proj_eco.update_traces(line_color="#22C55E", fillcolor="rgba(34,197,94,0.20)")
        fig_proj_eco.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3", showlegend=False)
        st.plotly_chart(fig_proj_eco, use_container_width=True)
        col_k1, col_k2 = st.columns(2)
        col_k1.metric("💰 Total", _fmt_brl(valor_total))
        col_k2.metric("📅 Média mensal", _fmt_brl(valor_total / horizonte))
        st.divider()

        st.markdown("### 📄 Exportar Plano de Corte")
        pdf_corte = gerar_pdf_plano_corte(df_sug, receita_bruta_corte, total_mensal, total_anual)
        st.download_button("📥 Baixar PDF do Plano", data=pdf_corte,
                            file_name=f"Plano_Cortes_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf", use_container_width=True, key="dl_pdf_final")
        st.divider()

        st.markdown("### 🎯 Definir Metas de Corte")
        with st.form("form_meta_final", clear_on_submit=True):
            fm1, fm2 = st.columns([3, 2])
            cat_escolhida = fm1.selectbox("Categoria", options=df_sug["categoria"].tolist(), key="cat_mf")
            meta_pct = fm2.number_input("Meta de redução (%)", 1.0, 100.0, 20.0, 5.0, key="pct_mf")
            if st.form_submit_button("💾 Salvar Meta"):
                cat_limpa = cat_escolhida.split(" ", 1)[-1]
                salvar_meta_corte(cat_limpa, meta_pct)
                st.success(f"Meta salva!")
                st.rerun()
        if st.button("📥 Salvar Análise no Histórico", use_container_width=True, key="salv_hist_f"):
            hoje_an = datetime.now()
            salvar_analise_corte(hoje_an.month, hoje_an.year, df_sug.to_dict("records"))
            st.success("Análise salva!")

    st.divider()
    st.markdown("### ✅ Cortes Já Realizados")
    df_cc = carregar_cortes_concluidos()
    if not df_cc.empty:
        total_economia = df_cc['valor_economia'].sum()
        st.success(f"🎉 Você já economizou **{_fmt_brl(total_economia)}/mês** (**{_fmt_brl(total_economia*12)}/ano**)!")
        df_cc_show = df_cc[["categoria", "valor_economia", "mes", "ano", "concluido_em"]].copy()
        df_cc_show["mes"] = df_cc_show["mes"].apply(lambda x: meses_nomes[int(x)-1] if 1 <= int(x) <= 12 else x)
        df_cc_show.columns = ["Categoria", "Economia (R$/mês)", "Mês", "Ano", "Data"]
        st.dataframe(df_cc_show, use_container_width=True, hide_index=True)
        cols_undo = st.columns(min(4, len(df_cc)))
        for i, (_, c) in enumerate(df_cc.iterrows()):
            with cols_undo[i % 4]:
                if st.button(f"🗑️ {c['categoria']}", key=f"undo_f_{c['id']}"):
                    remover_corte_concluido(c['id'])
                    st.rerun()
    else: st.info("Nenhum corte marcado ainda.")

    st.divider()
    st.markdown("### 📜 Histórico de Análises Salvas")
    df_hist_an = carregar_historico_analises()
    if not df_hist_an.empty:
        df_hs = df_hist_an[["mes", "ano", "categoria", "valor_atual", "valor_sugerido",
                             "economia_potencial", "prioridade", "criado_em"]].head(30).copy()
        df_hs["mes"] = df_hs["mes"].apply(lambda x: meses_nomes[int(x)-1] if 1 <= int(x) <= 12 else x)
        df_hs.columns = ["Mês", "Ano", "Categoria", "Valor Atual (R$)", "Corte (R$)",
                         "Economia Anual (R$)", "Prioridade", "Data"]
        st.dataframe(df_hs, use_container_width=True, hide_index=True)
    else: st.info("Nenhuma análise salva ainda.")

# =============================================================================
# ABA 9 — PROSPERIDADE
# =============================================================================
with tab9:
    st.subheader("🚀 Painel de Prosperidade")
    st.caption("Patrimônio · Carteira · Metas · FIRE · Dívidas · Rendas · Diagnóstico · Proteção · Calendário")

    secao = st.selectbox(
        "Selecione a seção:",
        ["💎 Patrimônio (Net Worth)", "💼 Carteira de Investimentos",
         "🎯 Metas com Prazo", "🔥 Calculadora FIRE",
         "🚨 Dívidas & Quitação", "💰 Rendas Extras",
         "🧠 Diagnóstico Financeiro", "🛡️ Checklist de Proteção",
         "📅 Calendário Financeiro"],
        key="secao_prosperidade"
    )
    st.divider()

    if secao == "💎 Patrimônio (Net Worth)":
        st.markdown("### 💎 Patrimônio Líquido")
        st.caption("**Net Worth = Ativos − Passivos**. É o número mais importante da sua vida financeira.")
        nw = calcular_net_worth()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Ativos", _fmt_brl(nw["ativos"]))
        c2.metric("Total de Passivos", _fmt_brl(nw["passivos"]))
        c3.metric("Patrimônio Líquido", _fmt_brl(nw["liquido"]),
                   delta="✅ positivo" if nw["liquido"] >= 0 else "⚠️ negativo",
                   delta_color="normal" if nw["liquido"] >= 0 else "inverse")
        st.markdown("")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("#### ➕ Adicionar Ativo")
            with st.form("form_ativo", clear_on_submit=True):
                nome_ativo = st.text_input("Nome do ativo", placeholder="Ex: Conta Nubank")
                cat_ativo = st.selectbox("Categoria", ["Conta corrente", "Poupança", "Investimentos", "Imóvel", "Veículo", "Outros bens", "Cripto", "Outros"])
                valor_ativo = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
                if st.form_submit_button("Adicionar Ativo", use_container_width=True):
                    if nome_ativo.strip():
                        adicionar_ativo(nome_ativo, cat_ativo, valor_ativo)
                        st.success("Ativo adicionado!"); st.rerun()
                    else: st.warning("Informe o nome do ativo.")
        with col_p2:
            st.markdown("#### ➖ Adicionar Passivo (Dívida)")
            with st.form("form_passivo", clear_on_submit=True):
                nome_pass = st.text_input("Nome da dívida", placeholder="Ex: Cartão Nubank")
                tipo_pass = st.selectbox("Tipo", ["Cartão de crédito", "Empréstimo pessoal", "Financiamento", "Cheque especial", "Consignado", "Outros"])
                valor_pass = st.number_input("Valor total (R$)", min_value=0.0, step=100.0)
                parcelas_pass = st.number_input("Parcelas restantes", min_value=1, value=1, step=1)
                juros_pass = st.number_input("Juros mensal (%)", min_value=0.0, step=0.1, format="%.2f")
                if st.form_submit_button("Adicionar Passivo", use_container_width=True):
                    if nome_pass.strip() and valor_pass > 0:
                        adicionar_passivo(nome_pass, tipo_pass, valor_pass, parcelas_pass, juros_pass)
                        st.success("Passivo adicionado!"); st.rerun()
                    else: st.warning("Informe nome e valor.")
        st.divider()
        df_ativos = carregar_ativos()
        df_passivos = carregar_passivos()
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.markdown("#### 📋 Ativos cadastrados")
            if df_ativos.empty: st.info("Nenhum ativo cadastrado.")
            else:
                for _, a in df_ativos.iterrows():
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    c1.write(f"**{a['nome']}**"); c2.write(f"{a['categoria']}"); c3.write(_fmt_brl(a['valor']))
                    if c4.button("🗑️", key=f"del_ativo_{a['id']}"):
                        remover_ativo(a['id']); st.rerun()
        with col_l2:
            st.markdown("#### 📋 Passivos cadastrados")
            if df_passivos.empty: st.info("Nenhum passivo cadastrado.")
            else:
                for _, p in df_passivos.iterrows():
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    c1.write(f"**{p['nome']}**"); c2.write(f"{p['tipo']} ({p['juros_mensal']}%/mês)")
                    c3.write(_fmt_brl(p['valor_total']))
                    if c4.button("🗑️", key=f"del_pass_{p['id']}"):
                        remover_passivo(p['id']); st.rerun()
        if not df_ativos.empty or not df_passivos.empty:
            st.divider()
            st.markdown("#### 📊 Composição do Patrimônio")
            comp = []
            if not df_ativos.empty:
                for _, a in df_ativos.iterrows():
                    comp.append({"Tipo": "Ativo", "Item": a['nome'], "Valor": a['valor']})
            if not df_passivos.empty:
                for _, p in df_passivos.iterrows():
                    comp.append({"Tipo": "Passivo", "Item": p['nome'], "Valor": p['valor_total']})
            df_comp = pd.DataFrame(comp)
            fig = px.bar(df_comp, x="Item", y="Valor", color="Tipo",
                         color_discrete_map={"Ativo": "#22C55E", "Passivo": "#EF4444"}, barmode="group")
            fig.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                              font_color="#E6EDF3", xaxis_tickangle=-25)
            st.plotly_chart(fig, use_container_width=True)

    elif secao == "💼 Carteira de Investimentos":
        st.markdown("### 💼 Carteira de Investimentos")
        st.caption("Cadastre cada posição. Veja rentabilidade, alocação e rebalanceamento sugerido.")
        df_cart = carregar_carteira()
        if not df_cart.empty:
            total_inv = df_cart["valor_investido"].sum()
            total_atual = df_cart["valor_atual"].sum()
            rendimento = total_atual - total_inv
            rent_pct = (rendimento / total_inv * 100) if total_inv > 0 else 0
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Valor Investido", _fmt_brl(total_inv))
            c2.metric("Valor Atual", _fmt_brl(total_atual))
            c3.metric("Rendimento", _fmt_brl(rendimento), delta=f"{rent_pct:.2f}%",
                       delta_color="normal" if rendimento >= 0 else "inverse")
            c4.metric("Ativos", f"{len(df_cart)}")
        with st.expander("➕ Adicionar nova posição", expanded=df_cart.empty):
            with st.form("form_invest", clear_on_submit=True):
                at = st.text_input("Ativo", placeholder="Ex: Tesouro Selic 2029")
                cls = st.selectbox("Classe", ["Renda Fixa", "Ações", "FIIs", "ETFs", "Cripto", "Fundos", "Previdência", "Internacional", "Outros"])
                c_i1, c_i2 = st.columns(2)
                with c_i1: v_inv = st.number_input("Valor investido (R$)", min_value=0.0, step=100.0)
                with c_i2: v_at = st.number_input("Valor atual (R$)", min_value=0.0, step=100.0)
                data_ap = st.date_input("Data do aporte", value=datetime.now())
                if st.form_submit_button("Adicionar", use_container_width=True):
                    if at.strip() and v_inv > 0:
                        adicionar_investimento(at, cls, v_inv, v_at, data_ap)
                        st.success("Posição adicionada!"); st.rerun()
                    else: st.warning("Informe ativo e valor.")
        if not df_cart.empty:
            st.divider()
            st.markdown("#### 📊 Alocação por Classe")
            por_classe = df_cart.groupby("classe").agg(valor_atual=("valor_atual", "sum"), valor_investido=("valor_investido", "sum")).reset_index()
            por_classe["pct"] = (por_classe["valor_atual"] / por_classe["valor_atual"].sum() * 100).round(1)
            por_classe["rent_pct"] = ((por_classe["valor_atual"] - por_classe["valor_investido"]) / por_classe["valor_investido"].replace(0, 1) * 100).round(2)
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                fig_pie = px.pie(por_classe, names="classe", values="valor_atual", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
                fig_pie.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3")
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_g2:
                st.markdown("##### Rentabilidade por classe")
                df_show = por_classe.copy()
                df_show["valor_atual"] = df_show["valor_atual"].apply(_fmt_brl)
                df_show["pct"] = df_show["pct"].apply(lambda v: f"{v}%")
                df_show["rent_pct"] = df_show["rent_pct"].apply(lambda v: f"{v}%")
                df_show = df_show.rename(columns={"classe": "Classe", "valor_atual": "Valor", "pct": "% Carteira", "rent_pct": "Rentabilidade"})[["Classe", "Valor", "% Carteira", "Rentabilidade"]]
                st.dataframe(df_show, use_container_width=True, hide_index=True)
            st.divider()
            st.markdown("#### 🗑️ Posições cadastradas")
            for _, p in df_cart.iterrows():
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
                c1.write(f"**{p['ativo']}**"); c2.write(p['classe'])
                c3.write(_fmt_brl(p['valor_investido'])); c4.write(_fmt_brl(p['valor_atual']))
                if c5.button("🗑️", key=f"del_inv_{p['id']}"):
                    remover_investimento(p['id']); st.rerun()

    elif secao == "🎯 Metas com Prazo":
        st.markdown("### 🎯 Metas Financeiras com Prazo")
        st.caption("Curto (1 ano), médio (3–5) e longo prazo (10+). Cada meta mostra quanto aportar por mês.")
        df_metas = carregar_metas_financeiras()
        with st.expander("➕ Nova meta", expanded=df_metas.empty):
            with st.form("form_meta_fin", clear_on_submit=True):
                nome_m = st.text_input("Nome da meta", placeholder="Ex: Entrada do apartamento")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    alvo_m = st.number_input("Valor alvo (R$)", min_value=0.0, step=1000.0)
                    atual_m = st.number_input("Valor já guardado (R$)", min_value=0.0, step=100.0)
                with col_m2:
                    prazo_m = st.number_input("Prazo (anos)", min_value=1, max_value=50, value=3)
                    cat_m = st.selectbox("Categoria", ["Curto prazo", "Médio prazo", "Longo prazo", "Viagem", "Imóvel", "Veículo", "Educação", "Geral"])
                if st.form_submit_button("Adicionar Meta", use_container_width=True):
                    if nome_m.strip() and alvo_m > 0:
                        adicionar_meta_financeira(nome_m, alvo_m, atual_m, prazo_m, cat_m)
                        st.success("Meta criada!"); st.rerun()
                    else: st.warning("Informe nome e valor.")
        if not df_metas.empty:
            st.divider()
            for _, m in df_metas.iterrows():
                falta = max(0.0, m['valor_alvo'] - m['valor_atual'])
                pct = (m['valor_atual'] / m['valor_alvo'] * 100) if m['valor_alvo'] > 0 else 0
                meses_restantes = m['prazo_anos'] * 12
                aporte_necessario = falta / meses_restantes if meses_restantes > 0 else 0
                cor = "#22C55E" if pct >= 75 else ("#F59E0B" if pct >= 40 else "#EF4444")
                st.markdown(
                    f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
                    f"border-left:4px solid {cor};border-radius:12px;padding:16px 20px;margin-bottom:10px;'>"
                    f"<div style='display:flex;justify-content:space-between;'>"
                    f"<b style='color:{PALETA['texto_principal']};'>🎯 {m['nome']} "
                    f"<span style='color:{PALETA['texto_secundario']};font-size:11px;'>[{m['categoria']}]</span></b>"
                    f"<span style='color:{cor};font-weight:700;'>{pct:.1f}%</span></div>"
                    f"<div style='color:{PALETA['texto_secundario']};font-size:12px;margin-top:6px;'>"
                    f"Guardado: <b style='color:{PALETA['texto_principal']};'>{_fmt_brl(m['valor_atual'])}</b> / "
                    f"Alvo: <b>{_fmt_brl(m['valor_alvo'])}</b> · Prazo: <b>{m['prazo_anos']} anos</b> · "
                    f"Aporte mensal necessário: <b style='color:{PALETA['verde']};'>{_fmt_brl(aporte_necessario)}</b>"
                    f"</div></div>", unsafe_allow_html=True
                )
                st.progress(min(pct / 100, 1.0))
                c1, c2 = st.columns([3, 1])
                with c1:
                    novo_valor = st.number_input(f"Atualizar valor guardado de '{m['nome']}'",
                                                  min_value=0.0, value=float(m['valor_atual']),
                                                  step=100.0, key=f"meta_upd_{m['id']}")
                with c2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 Atualizar", key=f"btn_upd_{m['id']}", use_container_width=True):
                        atualizar_valor_meta_financeira(m['id'], novo_valor); st.rerun()
                    if st.button("🗑️ Excluir", key=f"del_meta_fin_{m['id']}", use_container_width=True):
                        remover_meta_financeira(m['id']); st.rerun()

    elif secao == "🔥 Calculadora FIRE":
        st.markdown("### 🔥 Independência Financeira (FIRE)")
        st.caption("Descubra **quanto você precisa acumular** para viver de renda para sempre.")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            gasto_m = st.number_input("Seu gasto mensal para viver (R$)", value=float(total_fixos_a + total_gastos_variaveis), step=100.0, key="fire_gasto")
            pat_a = st.number_input("Patrimônio atual (R$)", value=float(calcular_net_worth()["liquido"]), step=1000.0, key="fire_pat")
        with col_f2:
            ap_m = st.number_input("Aporte mensal (R$)", value=float(meta_reserva_efetiva), step=100.0, key="fire_ap")
            taxa_ret = st.slider("Taxa de retirada segura (%)", 3.0, 6.0, 4.0, 0.5, key="fire_taxa") / 100
        fire = calcular_fire(gasto_m, pat_a, ap_m, taxa_retirada=taxa_ret)
        if fire:
            st.markdown("")
            fm1, fm2, fm3 = st.columns(3)
            fm1.metric("💎 Número Mágico", _fmt_brl(fire["numero_magico"]), delta="quanto você precisa ter")
            fm2.metric("📉 Falta acumular", _fmt_brl(fire["falta"]))
            if fire["anos_para_fire"]:
                fm3.metric("⏱️ Tempo para FIRE", f"{fire['anos_para_fire']} anos", delta=f"com aporte de {_fmt_brl(ap_m)}/mês")
            else:
                fm3.metric("⏱️ Tempo para FIRE", "—", delta="aumente o aporte", delta_color="inverse")
            st.markdown(
                f"<div style='background:{PALETA['fundo_card']};border-left:4px solid {PALETA['roxo']};"
                f"border-radius:12px;padding:18px 22px;margin-top:16px;'>"
                f"<b style='color:{PALETA['texto_principal']};font-size:15px;'>"
                f"🎉 Com {_fmt_brl(fire['numero_magico'])} investidos, você pode retirar "
                f"{_fmt_brl(fire['retirada_mensal_segura'])}/mês para sempre — sem trabalhar.</b>"
                f"</div>", unsafe_allow_html=True
            )
            st.divider()
            st.markdown("#### 📈 Evolução até a Independência")
            if pat_a < fire["numero_magico"]:
                anos_max = min(40, int((fire["anos_para_fire"] or 30) + 5))
                dados = []
                saldo = pat_a
                r_m = 0.07 / 12
                for m in range(0, anos_max * 12 + 1):
                    if m % 12 == 0:
                        dados.append({"Ano": m // 12, "Patrimônio": saldo, "Meta": fire["numero_magico"]})
                    saldo = saldo * (1 + r_m) + ap_m
                df_fire = pd.DataFrame(dados)
                fig_fire = px.area(df_fire, x="Ano", y=["Patrimônio", "Meta"], color_discrete_sequence=["#22C55E", "#7C3AED"])
                fig_fire.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3")
                st.plotly_chart(fig_fire, use_container_width=True)

    elif secao == "🚨 Dívidas & Quitação":
        st.markdown("### 🚨 Análise de Dívidas")
        st.caption("Veja quanto você paga de juros e qual a melhor ordem para quitar.")
        df_pass = carregar_passivos()
        if df_pass.empty: st.success("🟢 Nenhuma dívida cadastrada. Continue assim!")
        else:
            total_divida = df_pass["valor_total"].sum()
            juros_mes = (df_pass["valor_total"] * df_pass["juros_mensal"] / 100).sum()
            juros_ano = juros_mes * 12
            c1, c2, c3 = st.columns(3)
            c1.metric("Total de Dívidas", _fmt_brl(total_divida))
            c2.metric("Juros/mês", _fmt_brl(juros_mes), delta_color="inverse")
            c3.metric("Juros/ano", _fmt_brl(juros_ano), delta="🔥 queima de caixa", delta_color="inverse")
            st.divider()
            st.markdown("#### 🎯 Ordem recomendada de quitação (método avalanche)")
            st.caption("Quite primeiro o que tem **maior juros**. Você economiza mais rápido.")
            df_ord = calcular_ordem_quitacao(df_pass)
            for _, p in df_ord.iterrows():
                cor = "#EF4444" if p['ordem'] == 1 else ("#F59E0B" if p['ordem'] <= 3 else "#3B82F6")
                st.markdown(
                    f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
                    f"border-left:4px solid {cor};border-radius:10px;padding:12px 16px;margin-bottom:8px;'>"
                    f"<b style='color:{cor};'>#{int(p['ordem'])}</b> · "
                    f"<b style='color:{PALETA['texto_principal']};'>{p['nome']}</b> "
                    f"<span style='color:{PALETA['texto_secundario']};font-size:12px;'>"
                    f"[{p['tipo']}] · {_fmt_brl(p['valor_total'])} · "
                    f"juros {p['juros_mensal']}%/mês · "
                    f"custo mensal {_fmt_brl(p['custo_juros_mensal'])}</span>"
                    f"</div>", unsafe_allow_html=True
                )

    elif secao == "💰 Rendas Extras":
        st.markdown("### 💰 Rendas e Fontes de Receita")
        st.caption("Cada real a mais vale mais que cada real economizado. Acompanhe suas fontes.")
        df_rend = carregar_rendas()
        hoje = datetime.now()
        with st.expander("➕ Adicionar renda", expanded=True):
            with st.form("form_renda", clear_on_submit=True):
                c1, c2, c3 = st.columns([3, 2, 2])
                desc_r = c1.text_input("Descrição", placeholder="Ex: Freelance UI")
                val_r = c2.number_input("Valor (R$)", min_value=0.0, step=100.0)
                tipo_r = c3.selectbox("Tipo", ["Salário", "Freelance", "Aluguel", "Dividendos", "Vendas", "Bico", "Outros"])
                c4, c5 = st.columns(2)
                mes_r = c4.selectbox("Mês", list(range(1, 13)), index=hoje.month - 1, format_func=lambda m: meses_nomes[m-1])
                ano_r = c5.number_input("Ano", min_value=2020, max_value=2100, value=hoje.year)
                if st.form_submit_button("Adicionar Renda", use_container_width=True):
                    if desc_r.strip() and val_r > 0:
                        adicionar_renda(desc_r, val_r, mes_r, ano_r, tipo_r)
                        st.success("Renda adicionada!"); st.rerun()
                    else: st.warning("Informe descrição e valor.")
        if not df_rend.empty:
            total_anual_rend = df_rend[df_rend["ano"] == hoje.year]["valor"].sum()
            total_mes_rend = df_rend[(df_rend["ano"] == hoje.year) & (df_rend["mes"] == hoje.month)]["valor"].sum()
            c1, c2 = st.columns(2)
            c1.metric(f"Rendas Extras de {meses_nomes[hoje.month-1]}", _fmt_brl(total_mes_rend))
            c2.metric(f"Rendas Extras em {hoje.year}", _fmt_brl(total_anual_rend))
            st.divider()
            st.markdown("#### 📊 Rendas por tipo")
            por_tipo = df_rend.groupby("tipo")["valor"].sum().reset_index()
            fig_rt = px.bar(por_tipo, x="tipo", y="valor", color="tipo", color_discrete_sequence=px.colors.qualitative.Set2)
            fig_rt.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3", showlegend=False)
            st.plotly_chart(fig_rt, use_container_width=True)
            st.markdown("#### 📋 Lançamentos")
            for _, r in df_rend.head(30).iterrows():
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 1])
                c1.write(f"**{r['descricao']}**"); c2.write(r['tipo'])
                c3.write(f"{meses_nomes[int(r['mes'])-1]}/{r['ano']}"); c4.write(_fmt_brl(r['valor']))
                if c5.button("🗑️", key=f"del_renda_{r['id']}"):
                    remover_renda(r['id']); st.rerun()

    elif secao == "🧠 Diagnóstico Financeiro":
        st.markdown("### 🧠 Diagnóstico Financeiro Pessoal")
        st.caption("Nota de 0 a 100 baseada em 5 critérios.")
        nw = calcular_net_worth()
        diagnostico = calcular_diagnostico_financeiro(
            receita_mensal=salario_a_input + vr_a_input,
            total_gastos=total_fixos_a + total_gastos_variaveis,
            total_fixos=total_fixos_a,
            reserva_atual=meta_reserva_efetiva * 6,
            ativos=nw["ativos"], passivos=nw["passivos"]
        )
        nota = diagnostico["nota"]
        if nota >= 80: cor_n, status_n = "#22C55E", "🟢 EXCELENTE"
        elif nota >= 60: cor_n, status_n = "#F59E0B", "🟡 BOM"
        elif nota >= 40: cor_n, status_n = "#F59E0B", "🟠 REGULAR"
        else: cor_n, status_n = "#EF4444", "🔴 CRÍTICO"
        st.markdown(
            f"<div style='background:{PALETA['fundo_card']};border:2px solid {cor_n};"
            f"border-radius:16px;padding:32px;text-align:center;margin:16px 0;'>"
            f"<div style='color:{PALETA['texto_secundario']};font-size:12px;letter-spacing:2px;'>SUA NOTA FINANCEIRA</div>"
            f"<div style='color:{cor_n};font-size:64px;font-weight:700;line-height:1.1;'>{nota:.0f}</div>"
            f"<div style='color:{cor_n};font-size:14px;font-weight:600;letter-spacing:1px;'>{status_n}</div>"
            f"</div>", unsafe_allow_html=True
        )
        st.markdown("#### Detalhamento por critério")
        det = diagnostico["detalhes"]
        for crit, pts in det.items():
            max_pts = {"poupanca": 25, "reserva": 25, "divida": 25, "investimento": 15, "diversificacao": 10}.get(crit, 25)
            pct = (pts / max_pts) if max_pts > 0 else 0
            cor_c = "#22C55E" if pct >= 0.7 else ("#F59E0B" if pct >= 0.4 else "#EF4444")
            label = {"poupanca": "Taxa de poupança", "reserva": "Reserva de emergência", "divida": "Controle de dívidas",
                     "investimento": "Capacidade de investir", "diversificacao": "Diversificação"}[crit]
            st.markdown(
                f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
                f"border-radius:10px;padding:12px 16px;margin-bottom:8px;'>"
                f"<div style='display:flex;justify-content:space-between;'>"
                f"<span style='color:{PALETA['texto_principal']};'>{label}</span>"
                f"<span style='color:{cor_c};font-weight:700;'>{pts:.1f} / {max_pts} pts</span>"
                f"</div></div>", unsafe_allow_html=True
            )
            st.progress(pct)
        st.markdown("#### 📊 Indicadores extras")
        st.write(f"- Taxa de poupança atual: **{diagnostico['taxa_poupanca_pct']}%**")
        st.write(f"- Meses de reserva: **{diagnostico['meses_reserva']}** (ideal: 6+)")

    elif secao == "🛡️ Checklist de Proteção":
        st.markdown("### 🛡️ Checklist de Proteção Financeira")
        st.caption("Itens essenciais para dormir tranquilo.")
        df_prot = carregar_protecoes()
        if df_prot.empty: st.info("Nenhum item no checklist.")
        else:
            total = len(df_prot)
            feitos = df_prot["contratado"].sum()
            pct = (feitos / total * 100) if total > 0 else 0
            st.markdown(
                f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
                f"border-radius:12px;padding:16px 20px;margin-bottom:16px;'>"
                f"<b style='color:{PALETA['texto_principal']};'>Progresso da proteção: "
                f"{int(feitos)}/{total} itens ({pct:.0f}%)</b></div>", unsafe_allow_html=True
            )
            st.progress(pct / 100)
            st.markdown("")
            for _, p in df_prot.iterrows():
                c1, c2 = st.columns([5, 1])
                with c1:
                    marcado = st.checkbox(f"**{p['item']}**", value=bool(p['contratado']), key=f"prot_{p['id']}")
                    if marcado != bool(p['contratado']):
                        atualizar_protecao(p['item'], marcado); st.rerun()

    elif secao == "📅 Calendário Financeiro":
        st.markdown("### 📅 Calendário Financeiro")
        st.caption("Todas as contas a pagar em um só lugar.")
        df_contas = carregar_contas_pagar()
        hoje_dt = datetime.now().date()
        with st.expander("➕ Adicionar conta", expanded=True):
            with st.form("form_conta", clear_on_submit=True):
                c1, c2, c3 = st.columns([3, 2, 2])
                desc_c = c1.text_input("Descrição", placeholder="Ex: Conta de luz")
                val_c = c2.number_input("Valor (R$)", min_value=0.0, step=10.0)
                cat_c = c3.selectbox("Categoria", ["Moradia", "Alimentação", "Transporte", "Saúde", "Educação", "Lazer", "Cartão", "Outros"])
                venc_c = st.date_input("Vencimento", value=datetime.now())
                if st.form_submit_button("Adicionar", use_container_width=True):
                    if desc_c.strip() and val_c > 0:
                        adicionar_conta_pagar(desc_c, val_c, venc_c, cat_c)
                        st.success("Conta adicionada!"); st.rerun()
                    else: st.warning("Informe descrição e valor.")
        if not df_contas.empty:
            pendentes = df_contas[df_contas["pago"] == False]
            total_pend = pendentes["valor"].sum()
            venc_hoje = pendentes[pendentes["vencimento"].dt.date == hoje_dt]
            venc_semana = pendentes[(pendentes["vencimento"].dt.date >= hoje_dt) & (pendentes["vencimento"].dt.date <= hoje_dt + pd.Timedelta(days=7))]
            vencidas = pendentes[pendentes["vencimento"].dt.date < hoje_dt]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Pendente", _fmt_brl(total_pend))
            c2.metric("Vencem hoje", f"{len(venc_hoje)}", delta=_fmt_brl(venc_hoje['valor'].sum()) if not venc_hoje.empty else "—")
            c3.metric("Próx. 7 dias", f"{len(venc_semana)}", delta=_fmt_brl(venc_semana['valor'].sum()) if not venc_semana.empty else "—")
            c4.metric("Vencidas", f"{len(vencidas)}", delta="⚠️ atenção", delta_color="inverse" if not vencidas.empty else "normal")
            if not vencidas.empty:
                st.error(f"⚠️ **{len(vencidas)} conta(s) vencida(s)** totalizando {_fmt_brl(vencidas['valor'].sum())}")
            st.divider()
            st.markdown("#### 📋 Contas cadastradas")
            for _, ct in df_contas.iterrows():
                venc_date = ct["vencimento"].date() if hasattr(ct["vencimento"], "date") else ct["vencimento"]
                dias = (venc_date - hoje_dt).days
                if ct["pago"]: cor, status = "#22C55E", "✅ pago"
                elif dias < 0: cor, status = "#EF4444", f"⚠️ vencida há {abs(dias)}d"
                elif dias == 0: cor, status = "#F59E0B", "⏰ vence hoje"
                elif dias <= 7: cor, status = "#F59E0B", f"⏳ em {dias}d"
                else: cor, status = "#3B82F6", f"📅 em {dias}d"
                c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 2, 1, 1])
                c1.write(f"**{ct['descricao']}**"); c2.write(ct['categoria'])
                c3.write(venc_date.strftime("%d/%m/%Y"))
                c4.write(f"<span style='color:{cor};'>{status}</span>", unsafe_allow_html=True)
                c5.write(_fmt_brl(ct['valor']))
                with c6:
                    if not ct["pago"]:
                        if st.button("✓", key=f"pago_{ct['id']}"):
                            marcar_conta_paga(ct['id'], True); st.rerun()
                    else:
                        if st.button("🗑️", key=f"del_conta_{ct['id']}"):
                            remover_conta_pagar(ct['id']); st.rerun()

# =============================================================================
# FIM DO APLICATIVO
# =============================================================================
