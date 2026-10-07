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
# BLOCO DE ESTILO SEPARADO - PALETA DARK PREMIUM & COMPONENTES [VISUAL]
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
    h1 {{
        color: {PALETA["texto_principal"]} !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        font-size: 30px !important;
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
        letter-spacing: 1.2px;
        font-size: 11px !important;
    }}
    p, span, label {{
        color: {PALETA["texto_principal"]};
    }}
    [data-testid="stCaptionContainer"] {{
        color: {PALETA["texto_secundario"]} !important;
        font-size: 12px !important;
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {PALETA["fundo_sidebar"]} 0%, {PALETA["fundo_principal"]} 100%);
        border-right: 1px solid {PALETA["borda"]};
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {PALETA["texto_principal"]} !important;
        border-bottom: 1px solid {PALETA["borda"]};
        padding-bottom: 10px;
        margin-bottom: 12px;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: {PALETA["borda"]} !important;
        margin: 16px 0 !important;
    }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, {PALETA["fundo_card"]} 0%, {PALETA["fundo_sidebar"]} 100%);
        border: 1px solid {PALETA["borda"]};
        border-radius: 14px;
        padding: 20px 22px !important;
        box-shadow: 0 4px 24px -8px rgba(0,0,0,0.5);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }}
    div[data-testid="stMetric"]::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, {PALETA["acento"]}, transparent);
        opacity: 0.6;
    }}
    div[data-testid="stMetric"]:hover {{
        border-color: {PALETA["borda_acento"]};
        box-shadow: 0 0 0 1px {PALETA["acento_glow"]}, 0 8px 32px -8px rgba(59,130,246,0.35);
        transform: translateY(-2px);
    }}
    div[data-testid="stMetric"] label {{
        color: {PALETA["texto_secundario"]} !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {PALETA["texto_principal"]} !important;
        font-family: 'Consolas', 'JetBrains Mono', monospace !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
        font-size: 12px !important;
        font-weight: 600 !important;
    }}
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {{
        background: {PALETA["fundo_card"]} !important;
        color: {PALETA["texto_principal"]} !important;
        border: 1px solid {PALETA["borda"]} !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background: {PALETA["acento"]} !important;
        border-color: {PALETA["acento"]} !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px {PALETA["acento_glow"]};
        transform: translateY(-1px);
    }}
    .stButton > button:active,
    .stFormSubmitButton > button:active {{
        transform: translateY(0);
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {PALETA["fundo_card"]};
        padding: 6px;
        border-radius: 12px;
        border: 1px solid {PALETA["borda"]};
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        background: transparent !important;
        border-radius: 8px !important;
        color: {PALETA["texto_secundario"]} !important;
        font-weight: 600;
        font-size: 13px;
        padding: 0 16px;
        transition: all 0.2s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: {PALETA["texto_principal"]} !important;
        background: {PALETA["fundo_hover"]} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: {PALETA["acento"]} !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 16px {PALETA["acento_glow"]};
    }}
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}
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
    }}
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus,
    div[data-baseweb="select"] > div:focus-within {{
        border-color: {PALETA["acento"]} !important;
        box-shadow: 0 0 0 3px {PALETA["acento_glow"]} !important;
    }}
    .stNumberInput button {{
        background: {PALETA["fundo_card"]} !important;
        border-color: {PALETA["borda"]} !important;
        color: {PALETA["texto_principal"]} !important;
    }}
    label[data-testid="stWidgetLabel"] p {{
        color: {PALETA["texto_secundario"]} !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }}
    div[data-testid="stExpander"] {{
        background: {PALETA["fundo_card"]};
        border: 1px solid {PALETA["borda"]} !important;
        border-radius: 12px !important;
        overflow: hidden;
    }}
    div[data-testid="stExpander"] summary {{
        font-weight: 600 !important;
        color: {PALETA["texto_principal"]} !important;
        padding: 14px 18px !important;
        transition: background 0.2s ease;
    }}
    div[data-testid="stExpander"] summary:hover {{
        background: {PALETA["fundo_hover"]};
    }}
    div[data-testid="stAlert"] {{
        border-radius: 12px !important;
        border-left-width: 4px !important;
        font-size: 13px !important;
        padding: 12px 16px !important;
    }}
    div[data-testid="stAlert"][data-baseweb="notification"] {{
        background: {PALETA["fundo_card"]} !important;
    }}
    .stDataFrame, div[data-testid="stTable"] {{
        background: {PALETA["fundo_card"]} !important;
        border-radius: 12px !important;
        border: 1px solid {PALETA["borda"]} !important;
        overflow: hidden;
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
        letter-spacing: 1px;
        font-size: 11px !important;
        font-weight: 700 !important;
        border-bottom: 1px solid {PALETA["borda"]} !important;
        padding: 12px !important;
    }}
    div[data-testid="stTable"] tbody tr {{
        border-bottom: 1px solid {PALETA["borda"]} !important;
    }}
    div[data-testid="stTable"] tbody tr:nth-child(even) {{
        background: rgba(31, 41, 55, 0.25) !important;
    }}
    div[data-testid="stTable"] tbody tr:hover {{
        background: {PALETA["fundo_hover"]} !important;
    }}
    div[data-testid="stTable"] tbody td {{
        color: {PALETA["texto_principal"]} !important;
        font-size: 13px !important;
        padding: 10px 12px !important;
    }}
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {PALETA["acento"]}, {PALETA["ciano"]}) !important;
        border-radius: 999px !important;
        box-shadow: 0 0 12px {PALETA["acento_glow"]};
    }}
    .stProgress > div > div > div {{
        background: {PALETA["fundo_card"]} !important;
        border-radius: 999px !important;
        height: 8px !important;
    }}
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
    hr {{
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, {PALETA["borda"]}, transparent) !important;
        margin: 20px 0 !important;
    }}
    div[data-testid="stForm"] {{
        background: {PALETA["fundo_card"]};
        border: 1px solid {PALETA["borda"]};
        border-radius: 14px;
        padding: 20px !important;
    }}
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {PALETA["fundo_principal"]}; }}
    ::-webkit-scrollbar-thumb {{
        background: {PALETA["borda"]};
        border-radius: 999px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: {PALETA["acento"]}; }}
    div[data-baseweb="tooltip"] {{
        background: {PALETA["fundo_card"]} !important;
        border: 1px solid {PALETA["borda"]} !important;
        border-radius: 8px !important;
        color: {PALETA["texto_principal"]} !important;
    }}
    .login-title {{
        background: linear-gradient(90deg, {PALETA["acento"]}, {PALETA["ciano"]});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
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
# TELA DE LOGIN
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
# FUNÇÕES — ORÇAMENTO E RELATÓRIO MENSAL
# -----------------------------------------------------------------------------
def carregar_orcamento_mes(mes, ano):
    if supabase:
        try:
            res = supabase.table("orcamentos_mensais").select("*") \
                .eq("mes", mes).eq("ano", ano).execute()
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
            existente = supabase.table("orcamentos_mensais").select("id") \
                .eq("mes", mes).eq("ano", ano).execute()
            if existente.data:
                supabase.table("orcamentos_mensais").update(
                    {"orcamento": float(valor_orcamento)}
                ).eq("id", existente.data[0]["id"]).execute()
            else:
                supabase.table("orcamentos_mensais").insert({
                    "mes": mes, "ano": ano,
                    "orcamento": float(valor_orcamento), "fechado": False
                }).execute()
        except Exception as e:
            st.error(f"Erro ao salvar orçamento: {e}")

def fechar_mes(mes, ano):
    if supabase:
        try:
            supabase.table("orcamentos_mensais").update({"fechado": True}) \
                .eq("mes", mes).eq("ano", ano).execute()
        except:
            pass

def carregar_despesas_por_mes(mes, ano):
    if supabase:
        try:
            res = supabase.table("despesas_variaveis").select("*") \
                .order("data", desc=True).execute()
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
            res = supabase.table("orcamentos_mensais").select("*") \
                .order("ano", desc=True).order("mes", desc=True).execute()
            if res.data:
                return pd.DataFrame(res.data)
        except:
            pass
    return pd.DataFrame(columns=["id", "mes", "ano", "orcamento", "fechado"])

def gerar_relatorio_mensal_pdf(mes, ano, df_mes, orcamento):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30,
                            leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18,
                                 textColor=colors.HexColor('#3B82F6'),
                                 spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12,
                                   textColor=colors.HexColor('#E6EDF3'),
                                   spaceBefore=12, spaceAfter=6)
    normal_style = styles['Normal']

    nome_mes = meses_nomes[mes - 1]
    story.append(Paragraph(f"<b>RELATÓRIO MENSAL — {nome_mes.upper()}/{ano}</b>", title_style))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                           ParagraphStyle('S', parent=normal_style, alignment=1,
                                          textColor=colors.HexColor('#8B949E'))))
    story.append(Spacer(1, 15))

    total_gasto = df_mes["valor"].sum() if not df_mes.empty else 0.0
    saldo = orcamento - total_gasto
    pct = (total_gasto / orcamento * 100) if orcamento > 0 else 0

    resumo = [
        ["Indicador", "Valor (R$)"],
        ["Orçamento do Mês", f"R$ {orcamento:,.2f}"],
        ["Total Gasto", f"R$ {total_gasto:,.2f}"],
        ["Saldo Restante", f"R$ {saldo:,.2f}"],
        ["% Utilizado", f"{pct:.1f}%"]
    ]
    t = Table(resumo, colWidths=[250, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Despesas Detalhadas do Mês</b>", heading_style))
    if not df_mes.empty:
        data = [["Data", "Descrição", "Categoria", "Valor (R$)"]]
        for _, row in df_mes.iterrows():
            data.append([
                row['data'].strftime('%d/%m/%Y'),
                str(row['descricao']), str(row['categoria']),
                f"R$ {float(row['valor']):,.2f}"
            ])
        tv = Table(data, colWidths=[80, 170, 110, 90])
        tv.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))
        ]))
        story.append(tv)
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Gastos por Categoria</b>", heading_style))
        cat = df_mes.groupby("categoria")["valor"].sum().reset_index()
        cat_data = [["Categoria", "Total (R$)"]]
        for _, r in cat.iterrows():
            cat_data.append([str(r['categoria']), f"R$ {float(r['valor']):,.2f}"])
        tc = Table(cat_data, colWidths=[250, 200])
        tc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))
        ]))
        story.append(tc)
    else:
        story.append(Paragraph("Nenhuma despesa registrada neste mês.", normal_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -----------------------------------------------------------------------------
# FUNÇÃO GERADORA DE RELATÓRIO PDF (GASTOS E PERDAS)
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

# =============================================================================
# >>> FUNÇÕES — CORTES INTELIGENTES DE GASTOS
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
        except:
            pass
    return pd.DataFrame(columns=["id", "categoria", "meta_reducao_pct", "ativo"])


def salvar_meta_corte(categoria, meta_reducao_pct):
    if supabase:
        try:
            existente = supabase.table("metas_corte").select("id") \
                .eq("categoria", categoria).execute()
            if existente.data:
                supabase.table("metas_corte").update({
                    "meta_reducao_pct": float(meta_reducao_pct),
                    "ativo": True,
                    "atualizado_em": datetime.now().isoformat()
                }).eq("categoria", categoria).execute()
            else:
                supabase.table("metas_corte").insert({
                    "categoria": categoria,
                    "meta_reducao_pct": float(meta_reducao_pct),
                    "ativo": True
                }).execute()
        except Exception as e:
            st.error(f"Erro ao salvar meta de corte: {e}")


def remover_meta_corte(categoria):
    if supabase:
        try:
            supabase.table("metas_corte").update({"ativo": False}) \
                .eq("categoria", categoria).execute()
        except:
            pass


def salvar_analise_corte(mes, ano, sugestoes):
    if supabase and sugestoes:
        try:
            supabase.table("analises_corte").insert([
                {
                    "mes": int(mes),
                    "ano": int(ano),
                    "categoria": s["categoria_limpa"],
                    "valor_atual": float(s["valor_atual"]),
                    "valor_sugerido": float(s["corte_sugerido"]),
                    "economia_potencial": float(s["economia_potencial"]),
                    "prioridade": int(s["prioridade"])
                }
                for s in sugestoes
            ]).execute()
        except Exception as e:
            st.warning(f"Não foi possível salvar histórico: {e}")


def carregar_historico_analises():
    if supabase:
        try:
            res = supabase.table("analises_corte").select("*") \
                .order("criado_em", desc=True).limit(100).execute()
            if res.data:
                return pd.DataFrame(res.data)
        except:
            pass
    return pd.DataFrame(columns=["id", "mes", "ano", "categoria", "valor_atual",
                                  "valor_sugerido", "economia_potencial",
                                  "prioridade", "criado_em"])


def _gerar_explicacao_corte(categoria, valor, peso, benchmark, excesso,
                             corte_sugerido, tipo, receita_bruta,
                             meta_reserva_mensal=0.0):
    """Gera uma explicação detalhada de por que cortar essa categoria."""
    tipo_txt = "despesa variável" if tipo == "Variável" else "custo fixo"
    excesso_pct = peso - benchmark
    valor_ideal = receita_bruta * benchmark / 100

    if excesso_pct >= 10:
        nivel, emoji = "CRÍTICO", "🚨"
        acao = ("Essa categoria está muito acima do recomendado e compromete "
                "seriamente seu equilíbrio financeiro. Precisa de revisão imediata.")
    elif excesso_pct >= 5:
        nivel, emoji = "ALTO", "⚠️"
        acao = ("Essa categoria precisa de atenção agora. Reduzir evita que o "
                "problema cresça nos próximos meses.")
    else:
        nivel, emoji = "MODERADO", "📌"
        acao = ("Categoria levemente acima do ideal. Pequenos ajustes já "
                "trazem resultado sem sacrificar sua qualidade de vida.")

    impacto_reserva = ""
    if meta_reserva_mensal > 0:
        pct_reserva = (corte_sugerido / meta_reserva_mensal) * 100
        impacto_reserva = (
            f" Esse valor equivale a <b>{pct_reserva:.0f}%</b> da sua meta "
            f"de reserva mensal (R$ {meta_reserva_mensal:,.2f})."
        )

    impacto_renda = (corte_sugerido / receita_bruta) * 100 if receita_bruta > 0 else 0

    explicacao = (
        f"{emoji} <b>Nível de prioridade: {nivel}</b><br><br>"
        f"Você está gastando <b>R$ {valor:,.2f}</b> em <b>{categoria}</b> "
        f"({tipo_txt}), o que representa <b>{peso:.1f}%</b> da sua renda bruta. "
        f"Para essa categoria, o recomendado é no máximo <b>{benchmark:.0f}%</b> "
        f"(ideal: R$ {valor_ideal:,.2f}). Ou seja, você está "
        f"<b>{excesso_pct:.1f} pontos percentuais acima do ideal</b>, "
        f"gerando um excesso de <b>R$ {excesso:,.2f} por mês</b>.<br><br>"
        f"<b>Por que cortar aqui?</b> {acao}<br><br>"
        f"<b>O que você ganha:</b> reduzindo <b>R$ {corte_sugerido:,.2f}/mês</b>, "
        f"você libera <b>R$ {corte_sugerido * 12:,.2f} por ano</b> — dinheiro "
        f"que pode ir para sua reserva de emergência, investimentos ou "
        f"quitação de dívidas.{impacto_reserva}<br><br>"
        f"<b>Impacto na sua renda:</b> esse corte representa "
        f"<b>{impacto_renda:.2f}%</b> da sua receita bruta mensal — "
        f"um ajuste real, mas possível, sem comprometer o essencial."
    )
    return explicacao


def analisar_cortes_inteligentes(df_variaveis, df_gastos_fixos, receita_bruta,
                                  meta_reserva_mensal=0.0):
    """Analisa as despesas e gera sugestões de corte priorizadas com explicações."""
    BENCHMARKS = {
        "Lazer / Passeios":  8.0,
        "Farmácia / Saúde":  5.0,
        "Vestuário":         5.0,
        "Imprevistos":      10.0,
        "Outros":            5.0,
        "Internet":          3.0,
        "Recarga celular":   2.0,
        "Corte de cabelo":   2.0,
        "Cartão de crédito":10.0,
        "Alimentação":      15.0,
        "Transporte":       10.0,
        "Moradia":          30.0,
    }

    if receita_bruta <= 0:
        return pd.DataFrame()

    sugestoes = []

    # --- DESPESAS VARIÁVEIS ---
    if df_variaveis is not None and not df_variaveis.empty:
        grp = df_variaveis.groupby("categoria")["valor"].sum().reset_index()
        for _, r in grp.iterrows():
            cat = str(r["categoria"])
            val = float(r["valor"])
            peso = (val / receita_bruta) * 100
            bench = BENCHMARKS.get(cat, 8.0)
            if peso > bench:
                excesso = val - (receita_bruta * bench / 100)
                corte_sug = excesso * 0.5
                explicacao = _gerar_explicacao_corte(
                    cat, val, peso, bench, excesso, corte_sug, "Variável",
                    receita_bruta, meta_reserva_mensal
                )
                sugestoes.append({
                    "categoria":           f"💳 {cat}",
                    "categoria_limpa":     cat,
                    "tipo":                "Variável",
                    "valor_atual":         val,
                    "peso_receita":        round(peso, 2),
                    "benchmark_saudavel":  bench,
                    "excesso":             round(excesso, 2),
                    "corte_sugerido":      round(corte_sug, 2),
                    "economia_potencial":  round(corte_sug * 12, 2),
                    "explicacao":          explicacao,
                })

    # --- GASTOS FIXOS ---
    if df_gastos_fixos is not None and not df_gastos_fixos.empty:
        grp_f = df_gastos_fixos.groupby("descricao")["valor"].sum().reset_index()
        for _, r in grp_f.iterrows():
            cat = str(r["descricao"])
            val = float(r["valor"])
            peso = (val / receita_bruta) * 100
            bench = BENCHMARKS.get(cat, 5.0)
            if peso > bench:
                excesso = val - (receita_bruta * bench / 100)
                corte_sug = excesso * 0.4
                explicacao = _gerar_explicacao_corte(
                    cat, val, peso, bench, excesso, corte_sug, "Fixo",
                    receita_bruta, meta_reserva_mensal
                )
                sugestoes.append({
                    "categoria":           f"🔧 {cat}",
                    "categoria_limpa":     cat,
                    "tipo":                "Fixo",
                    "valor_atual":         val,
                    "peso_receita":        round(peso, 2),
                    "benchmark_saudavel":  bench,
                    "excesso":             round(excesso, 2),
                    "corte_sugerido":      round(corte_sug, 2),
                    "economia_potencial":  round(corte_sug * 12, 2),
                    "explicacao":          explicacao,
                })

    if not sugestoes:
        return pd.DataFrame()

    df_sug = pd.DataFrame(sugestoes)
    df_sug = df_sug.sort_values("economia_potencial", ascending=False).reset_index(drop=True)
    df_sug["prioridade"] = df_sug.index + 1
    return df_sug


def gerar_pdf_plano_corte(df_sug, receita_bruta, economia_mensal, economia_anual):
    """Gera PDF executivo do plano de cortes COM explicações detalhadas."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30,
                            leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18,
                                 textColor=colors.HexColor('#3B82F6'),
                                 spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle('H', parent=styles['Heading2'], fontSize=12,
                                   textColor=colors.HexColor('#1F2937'),
                                   spaceBefore=12, spaceAfter=6)
    normal_style = styles['Normal']
    just_style = ParagraphStyle('J', parent=styles['Normal'], alignment=4,
                                 fontSize=10, leading=14)

    story.append(Paragraph("<b>INVEST CONTROL PRO - PLANO DE CORTES INTELIGENTES</b>", title_style))
    story.append(Paragraph(
        f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ParagraphStyle('S', parent=normal_style, alignment=1,
                       textColor=colors.HexColor('#8B949E'))
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>1. Resumo Executivo</b>", heading_style))
    resumo = [
        ["Indicador", "Valor"],
        ["Receita Bruta Considerada", f"R$ {receita_bruta:,.2f}"],
        ["Economia Mensal Potencial", f"R$ {economia_mensal:,.2f}"],
        ["Economia Anual Projetada", f"R$ {economia_anual:,.2f}"],
        ["Categorias com Excesso", f"{len(df_sug)}"]
    ]
    t_resumo = Table(resumo, colWidths=[250, 200])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#151B23')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#E6EDF3')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36'))
    ]))
    story.append(t_resumo)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>2. Ranking de Prioridades de Corte</b>", heading_style))
    data = [["#", "Categoria", "Tipo", "Atual (R$)", "Peso (%)",
             "Corte/mes (R$)", "Economia Anual (R$)"]]
    for _, s in df_sug.iterrows():
        data.append([
            str(int(s['prioridade'])),
            str(s['categoria']),
            str(s['tipo']),
            f"{s['valor_atual']:,.2f}",
            f"{s['peso_receita']}%",
            f"{s['corte_sugerido']:,.2f}",
            f"{s['economia_potencial']:,.2f}"
        ])
    tv = Table(data, colWidths=[22, 120, 55, 75, 55, 75, 95])
    tv.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EF4444')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#232B36')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT')
    ]))
    story.append(tv)
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>3. Justificativa Detalhada de Cada Corte</b>", heading_style))
    story.append(Paragraph(
        "Abaixo está o motivo de cada categoria ter sido sinalizada, "
        "quanto você economiza e o impacto esperado na sua renda.",
        just_style
    ))
    story.append(Spacer(1, 10))

    for _, s in df_sug.iterrows():
        texto_puro = s['explicacao']
        texto_puro = texto_puro.replace("<b>", "").replace("</b>", "")
        texto_puro = texto_puro.replace("<br><br>", " ").replace("<br>", " ")
        for emo in ["🚨", "⚠️", "📌"]:
            texto_puro = texto_puro.replace(emo, "")
        texto_puro = texto_puro.strip()

        story.append(Paragraph(
            f"<b>#{int(s['prioridade'])} - {s['categoria_limpa']} "
            f"({s['tipo']})</b>",
            ParagraphStyle('CatHead', parent=styles['Heading3'], fontSize=11,
                           textColor=colors.HexColor('#1F2937'), spaceAfter=4)
        ))
        story.append(Paragraph(texto_puro, just_style))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>4. Plano de Acao Recomendado (Top 5)</b>", heading_style))
    story.append(Paragraph(
        "Comece pelas categorias de maior prioridade. Aplicar os cortes "
        "sugeridos gera a economia anual indicada, que pode ser "
        "redirecionada para a reserva de emergencia ou investimentos.",
        just_style
    ))
    story.append(Spacer(1, 8))

    for _, s in df_sug.head(5).iterrows():
        nova_meta = s['valor_atual'] - s['corte_sugerido']
        story.append(Paragraph(
            f"<b>#{int(s['prioridade'])} - {s['categoria']}:</b> "
            f"Reduzir de <b>R$ {s['valor_atual']:,.2f}</b> para aproximadamente "
            f"<b>R$ {nova_meta:,.2f}</b> "
            f"(corte de R$ {s['corte_sugerido']:,.2f}/mes, "
            f"economia anual de R$ {s['economia_potencial']:,.2f})",
            just_style
        ))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# =============================================================================
# >>> FIM DAS FUNÇÕES DE CORTES
# =============================================================================

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📌 Planejamento & Cenários",
    "💳 Controle de Gastos Diários",
    "⚙ Gerenciar Custos Fixos",
    "📈 Simulador de Investimentos",
    "📊 DRE & Análise de Lucro",
    "📑 Relatórios PDF",
    "📅 Relatório Mensal",
    "✂️ Cortes Inteligentes"
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
        fig_pie.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3")
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
                    st.markdown("<span style='color:#22C55E; font-size:12px;'>● pago</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#F59E0B; font-size:12px;'>⏳ pendente</span>", unsafe_allow_html=True)

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
        fig_invest.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3")
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

with tab7:
    st.subheader("📅 Relatório Mensal & Orçamento por Mês")
    st.markdown("Cada mês possui seu **próprio orçamento**. As despesas são filtradas automaticamente pelo mês selecionado.")

    hoje = datetime.now()
    col_m1, col_m2, col_m3 = st.columns(3)
    mes_sel = col_m1.selectbox(
        "Mês de Referência",
        options=list(range(1, 13)),
        format_func=lambda x: meses_nomes[x - 1],
        index=hoje.month - 1
    )
    ano_sel = col_m2.number_input("Ano", min_value=2020, max_value=2100,
                                   value=hoje.year, step=1)

    orc_mes = carregar_orcamento_mes(mes_sel, ano_sel)
    orcamento_valor = float(orc_mes.get("orcamento", 0.0) or 0.0)
    mes_fechado = bool(orc_mes.get("fechado", False))

    if mes_fechado:
        col_m3.error("🔒 Mês Fechado")
    else:
        col_m3.success("🟢 Mês Aberto")

    st.divider()

    with st.expander("💼 Definir Orçamento do Mês Selecionado",
                     expanded=(orcamento_valor == 0.0)):
        novo_orc = st.number_input(
            "Orçamento (R$)", min_value=0.0,
            value=orcamento_valor, step=50.0,
            key=f"orc_{mes_sel}_{ano_sel}"
        )
        col_o1, col_o2 = st.columns(2)

        if col_o1.button("💾 Salvar Orçamento", use_container_width=True):
            salvar_orcamento_mes(mes_sel, ano_sel, novo_orc)
            st.success("Orçamento salvo!")
            st.rerun()

        if col_o2.button("🔒 Fechar Mês e Iniciar Novo Ciclo", use_container_width=True):
            fechar_mes(mes_sel, ano_sel)
            prox_mes = 1 if mes_sel == 12 else mes_sel + 1
            prox_ano = ano_sel + 1 if mes_sel == 12 else ano_sel
            carregar_orcamento_mes(prox_mes, prox_ano)
            st.success(f"Mês {meses_nomes[mes_sel-1]}/{ano_sel} fechado! "
                       f"Novo ciclo aberto em {meses_nomes[prox_mes-1]}/{prox_ano}.")
            st.rerun()

    df_mes = carregar_despesas_por_mes(mes_sel, ano_sel)
    total_gasto_mes = df_mes["valor"].sum() if not df_mes.empty else 0.0
    saldo_mes = orcamento_valor - total_gasto_mes
    pct_uso = (total_gasto_mes / orcamento_valor * 100) if orcamento_valor > 0 else 0.0

    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("Orçamento do Mês",
               f"R$ {orcamento_valor:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    cm2.metric("Total Gasto",
               f"- R$ {total_gasto_mes:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    cm3.metric("Saldo Restante",
               f"{'+' if saldo_mes >= 0 else '-'} R$ {abs(saldo_mes):,.2f}".replace('.', '#').replace(',', '.').replace('#', ','),
               delta_color="normal" if saldo_mes >= 0 else "inverse")
    cm4.metric("% Utilizado", f"{pct_uso:.1f}%")

    if orcamento_valor > 0:
        st.progress(min(pct_uso / 100, 1.0))
        if pct_uso >= 100:
            st.error(f"🚨 Orçamento estourado! Você ultrapassou em R$ {abs(saldo_mes):,.2f}")
        elif pct_uso >= 80:
            st.warning(f"⚠️ Atenção: você já utilizou {pct_uso:.1f}% do orçamento.")
        else:
            st.success(f"✅ Você está dentro do orçamento ({pct_uso:.1f}% utilizado).")

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### 📊 Gastos por Categoria (Mês Selecionado)")
        if not df_mes.empty:
            df_cat = df_mes.groupby("categoria")["valor"].sum().reset_index()
            fig_cat = px.bar(df_cat, x="categoria", y="valor", color="categoria",
                             color_discrete_sequence=px.colors.qualitative.Set2)
            fig_cat.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                   font_color="#E6EDF3", showlegend=False)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Sem despesas no mês selecionado.")

    with col_g2:
        st.markdown("#### 📋 Detalhamento das Despesas")
        if not df_mes.empty:
            df_show = df_mes.copy()
            df_show["data"] = df_show["data"].dt.strftime("%d/%m/%Y")
            df_show = df_show[["data", "descricao", "categoria", "valor"]]
            df_show.columns = ["Data", "Descrição", "Categoria", "Valor (R$)"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma despesa lançada neste mês.")

    st.divider()
    st.markdown("#### 📥 Exportar Relatório Mensal")
    pdf_mes = gerar_relatorio_mensal_pdf(mes_sel, ano_sel, df_mes, orcamento_valor)
    st.download_button(
        label=f"📥 Baixar Relatório de {meses_nomes[mes_sel-1]}/{ano_sel} em PDF",
        data=pdf_mes,
        file_name=f"Relatorio_{meses_nomes[mes_sel-1]}_{ano_sel}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.divider()
    st.markdown("#### 🗂 Histórico de Meses (Fechados e Abertos)")
    df_hist = listar_meses_fechados()
    if not df_hist.empty:
        df_hist["Mês"] = df_hist["mes"].apply(lambda x: meses_nomes[int(x) - 1])
        df_hist = df_hist.rename(columns={
            "ano": "Ano",
            "orcamento": "Orçamento (R$)",
            "fechado": "Fechado"
        })
        df_hist["Fechado"] = df_hist["Fechado"].apply(
            lambda x: "🔒 Sim" if x else "🟢 Não"
        )
        st.dataframe(df_hist[["Mês", "Ano", "Orçamento (R$)", "Fechado"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum mês registrado ainda.")

# =============================================================================
# ABA — CORTES INTELIGENTES DE GASTOS
# =============================================================================
with tab8:
    st.subheader("✂️ Cortes Inteligentes — Onde você deve economizar")
    st.markdown(
        "Análise automática das suas despesas com base em **benchmarks saudáveis** por categoria. "
        "A prioridade é definida pelo **impacto anual** da economia potencial. "
        "Cada sugestão traz uma **explicação detalhada do porquê cortar**."
    )

    receita_bruta_corte = salario_a_input + vr_a_input
    df_sug = analisar_cortes_inteligentes(
        df_variaveis, df_gastos_fixos, receita_bruta_corte,
        meta_reserva_mensal=meta_reserva_efetiva
    )

    if df_sug.empty:
        st.success("🟢 Excelente! Nenhuma categoria está acima do benchmark saudável. Continue assim!")
    else:
        total_anual = df_sug["economia_potencial"].sum()
        total_mensal = df_sug["corte_sugerido"].sum()
        top_cat = df_sug.iloc[0]

        ck1, ck2, ck3 = st.columns(3)
        ck1.metric("💸 Economia Mensal Potencial", _fmt_brl(total_mensal))
        ck2.metric("💰 Economia Anual Projetada", _fmt_brl(total_anual))
        ck3.metric("🎯 Prioridade #1", top_cat["categoria"])

        st.divider()

        st.markdown("### 🏆 Ranking de Prioridades de Corte")
        st.caption("Ordenado por maior impacto anual. Expanda cada item para ver o motivo detalhado.")

        for _, s in df_sug.iterrows():
            cor = "#EF4444" if s["prioridade"] <= 2 else ("#F59E0B" if s["prioridade"] <= 4 else "#3B82F6")
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
                [{s['tipo']}]
            </span>
        </div>
        <div style="color:{PALETA['verde']}; font-weight:700; font-size:15px;">
            Economia anual: {_fmt_brl(s['economia_potencial'])}
        </div>
    </div>
    <div style="color:{PALETA['texto_secundario']}; font-size:12px; margin-top:6px;">
        Valor atual: <b style="color:{PALETA['texto_principal']};">{_fmt_brl(s['valor_atual'])}</b>
        &nbsp;|&nbsp; Peso na receita: <b style="color:{cor};">{s['peso_receita']}%</b>
        &nbsp;|&nbsp; Benchmark saudável: {s['benchmark_saudavel']}%
        &nbsp;|&nbsp; Corte sugerido: <b style="color:{PALETA['texto_principal']};">{_fmt_brl(s['corte_sugerido'])}/mês</b>
    </div>
</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)

            with st.expander(f"📖 Por que cortar em {s['categoria_limpa']}? (ver explicação)", expanded=False):
                st.markdown(
                    f"<div style='background:{PALETA['fundo_sidebar']};"
                    f"border:1px solid {PALETA['borda']};border-radius:10px;"
                    f"padding:16px 20px;color:{PALETA['texto_principal']};"
                    f"font-size:13px;line-height:1.6;'>"
                    f"{s['explicacao']}"
                    f"</div>",
                    unsafe_allow_html=True
                )

        st.divider()

        col_gc1, col_gc2 = st.columns(2)
        with col_gc1:
            st.markdown("#### 📊 Peso Atual vs. Benchmark Saudável")
            df_chart = df_sug[["categoria", "peso_receita", "benchmark_saudavel"]].melt(
                id_vars="categoria", var_name="Tipo", value_name="Percentual"
            )
            df_chart["Tipo"] = df_chart["Tipo"].map({
                "peso_receita": "Atual",
                "benchmark_saudavel": "Saudável"
            })
            fig_cmp = px.bar(df_chart, x="categoria", y="Percentual", color="Tipo",
                             barmode="group",
                             color_discrete_map={"Atual": "#EF4444", "Saudável": "#22C55E"})
            fig_cmp.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                   font_color="#E6EDF3", xaxis_tickangle=-25)
            st.plotly_chart(fig_cmp, use_container_width=True)

        with col_gc2:
            st.markdown("#### 💰 Economia Anual por Categoria")
            fig_eco = px.bar(df_sug.sort_values("economia_potencial"),
                             x="economia_potencial", y="categoria",
                             orientation="h",
                             color="economia_potencial",
                             color_continuous_scale=["#3B82F6", "#F59E0B", "#EF4444"])
            fig_eco.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23",
                                   font_color="#E6EDF3", showlegend=False,
                                   coloraxis_showscale=False)
            st.plotly_chart(fig_eco, use_container_width=True)

        st.divider()

        st.markdown("### 📈 Projeção de Economia Acumulada")
        st.caption("Evolução da economia mês a mês se os cortes sugeridos forem aplicados a partir do mês 1.")

        col_h1, col_h2 = st.columns([1, 1])
        with col_h1:
            horizonte = st.slider("Horizonte de Projeção (meses)",
                                  min_value=6, max_value=36, value=24, step=6)
        with col_h2:
            redirecionar = st.checkbox("Simular economia redirecionada para investimento (10% a.a.)",
                                        value=False)

        lista_eixo = list(range(1, horizonte + 1))
        economia_acumulada = []
        valor_total = 0.0

        if redirecionar:
            taxa_m = (1 + 0.10) ** (1 / 12) - 1
            saldo = 0.0
            for _ in lista_eixo:
                saldo = (saldo + total_mensal) * (1 + taxa_m)
                economia_acumulada.append(saldo)
            valor_total = saldo
        else:
            for m in lista_eixo:
                economia_acumulada.append(total_mensal * m)
            valor_total = total_mensal * horizonte

        df_proj_eco = pd.DataFrame({
            "Mês": lista_eixo,
            "Economia Acumulada": economia_acumulada,
        })

        fig_proj_eco = px.area(
            df_proj_eco, x="Mês", y="Economia Acumulada",
            title=f"Economia acumulada em {horizonte} meses"
                  + (" (com reinvestimento)" if redirecionar else "")
        )
        fig_proj_eco.update_traces(line_color="#22C55E",
                                    fillcolor="rgba(34,197,94,0.20)")
        fig_proj_eco.update_layout(
            paper_bgcolor="#151B23", plot_bgcolor="#151B23",
            font_color="#E6EDF3", showlegend=False
        )
        st.plotly_chart(fig_proj_eco, use_container_width=True)

        col_k1, col_k2, col_k3 = st.columns(3)
        col_k1.metric("💰 Economia total no período", _fmt_brl(valor_total))
        col_k2.metric("📅 Média mensal", _fmt_brl(valor_total / horizonte))
        col_k3.metric("📊 Horizonte", f"{horizonte} meses")

        st.divider()

        st.markdown("#### 📋 Detalhamento Completo das Sugestões")
        df_det = df_sug[["prioridade", "categoria", "tipo", "valor_atual",
                          "peso_receita", "benchmark_saudavel",
                          "corte_sugerido", "economia_potencial"]].copy()
        df_det.columns = ["#", "Categoria", "Tipo", "Valor Atual (R$)",
                          "Peso Receita (%)", "Benchmark (%)",
                          "Corte Sugerido (R$/mês)", "Economia Anual (R$)"]
        st.dataframe(df_det, use_container_width=True, hide_index=True)

        st.divider()

        st.markdown("### 📄 Exportar Plano de Corte")
        st.caption("O PDF inclui o ranking, o plano de ação e a explicação de cada corte.")

        pdf_corte = gerar_pdf_plano_corte(
            df_sug, receita_bruta_corte, total_mensal, total_anual
        )
        st.download_button(
            label="📥 Baixar Plano de Cortes em PDF (com explicações)",
            data=pdf_corte,
            file_name=f"Plano_Cortes_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dl_plano_corte"
        )

        st.divider()

        st.markdown("### 🎯 Definir Metas de Corte")
        st.caption("Escolha uma categoria e defina sua meta de redução.")

        with st.form("form_meta_corte", clear_on_submit=True):
            fm1, fm2 = st.columns([3, 2])
            cat_escolhida = fm1.selectbox(
                "Categoria",
                options=df_sug["categoria"].tolist()
            )
            meta_pct = fm2.number_input(
                "Meta de redução (%)", min_value=1.0, max_value=100.0,
                value=20.0, step=5.0
            )
            if st.form_submit_button("💾 Salvar Meta de Corte"):
                cat_limpa = cat_escolhida.split(" ", 1)[-1]
                salvar_meta_corte(cat_limpa, meta_pct)
                st.success(f"Meta de redução de {meta_pct:.0f}% salva para **{cat_limpa}**!")
                st.rerun()

        df_metas = carregar_metas_corte()
        if not df_metas.empty:
            st.markdown("#### 📌 Suas Metas de Corte Ativas")
            df_metas_show = df_metas[["categoria", "meta_reducao_pct"]].copy()
            df_metas_show.columns = ["Categoria", "Meta de Redução (%)"]
            st.dataframe(df_metas_show, use_container_width=True, hide_index=True)

            st.markdown("##### Remover metas:")
            cols_rem = st.columns(min(4, len(df_metas)))
            for i, (_, m) in enumerate(df_metas.iterrows()):
                with cols_rem[i % 4]:
                    if st.button(f"🗑️ {m['categoria']}",
                                 key=f"del_meta_{m['categoria']}"):
                        remover_meta_corte(m["categoria"])
                        st.rerun()

        st.divider()

        if st.button("📥 Salvar Análise Atual no Histórico", use_container_width=True):
            hoje_an = datetime.now()
            sugestoes_dict = df_sug.to_dict("records")
            salvar_analise_corte(hoje_an.month, hoje_an.year, sugestoes_dict)
            st.success("Análise salva no histórico do Supabase!")

    st.divider()

    st.markdown("### 📜 Histórico de Análises Salvas")
    df_hist_an = carregar_historico_analises()
    if not df_hist_an.empty:
        df_hist_show = df_hist_an[["mes", "ano", "categoria", "valor_atual",
                                    "valor_sugerido", "economia_potencial",
                                    "prioridade", "criado_em"]].head(30).copy()
        df_hist_show["mes"] = df_hist_show["mes"].apply(
            lambda x: meses_nomes[int(x) - 1] if 1 <= int(x) <= 12 else x
        )
        df_hist_show.columns = ["Mês", "Ano", "Categoria", "Valor Atual (R$)",
                                 "Corte Sugerido (R$)", "Economia Anual (R$)",
                                 "Prioridade", "Data Análise"]
        st.dataframe(df_hist_show, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma análise salva ainda.")

# =============================================================================
# FIM DO APLICATIVO
# =============================================================================
