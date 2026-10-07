import streamlit as st
import pandas as pd
import plotly.express as px
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
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; background: {PALETA["fundo_card"]}; padding: 6px; border-radius: 12px; border: 1px solid {PALETA["borda"]}; }}
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
# ORÇAMENTO E RELATÓRIO MENSAL
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
# FUNÇÕES — CORTES INTELIGENTES (base)
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
        try:
            supabase.table("metas_corte").update({"ativo": False}).eq("categoria", categoria).execute()
        except:
            pass

def salvar_analise_corte(mes, ano, sugestoes):
    if supabase and sugestoes:
        try:
            supabase.table("analises_corte").insert([{
                "mes": int(mes), "ano": int(ano),
                "categoria": s["categoria_limpa"],
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
        except:
            pass
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

# =============================================================================
# NOVA FUNÇÃO — META IDEAL DE POUPANÇA
# =============================================================================
def calcular_meta_poupanca_ideal(receita_bruta, total_fixos, total_variaveis,
                                  meta_reserva_atual, taxa_ideal=0.20):
    if receita_bruta <= 0:
        return None
    meta_ideal_valor   = receita_bruta * taxa_ideal
    poupanca_atual     = max(0.0, meta_reserva_atual)
    falta_valor        = max(0.0, meta_ideal_valor - poupanca_atual)
    poupanca_atual_pct = (poupanca_atual / receita_bruta) * 100
    meta_ideal_pct     = taxa_ideal * 100
    falta_pct          = meta_ideal_pct - poupanca_atual_pct
    progresso          = min(1.0, poupanca_atual / meta_ideal_valor) if meta_ideal_valor > 0 else 0.0

    if progresso >= 1.0:
        status_cor, status_emoji, status_txt = "#22C55E", "🟢", "Meta atingida"
    elif progresso >= 0.5:
        status_cor, status_emoji, status_txt = "#F59E0B", "🟡", "No caminho"
    else:
        status_cor, status_emoji, status_txt = "#EF4444", "🔴", "Abaixo do ideal"

    return {
        "meta_ideal_valor":   round(meta_ideal_valor, 2),
        "meta_ideal_pct":     round(meta_ideal_pct, 1),
        "poupanca_atual":     round(poupanca_atual, 2),
        "poupanca_atual_pct": round(poupanca_atual_pct, 1),
        "falta_valor":        round(falta_valor, 2),
        "falta_pct":          round(falta_pct, 1),
        "progresso":          round(progresso, 3),
        "status_cor":         status_cor,
        "status_emoji":       status_emoji,
        "status_txt":         status_txt,
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
            "Categoria":        s["categoria_limpa"],
            "Tipo":             s["tipo"],
            "Gasto Atual (R$)": round(valor_atual, 2),
            "Ideal (R$)":       round(valor_ideal, 2),
            "Reduzir (R$)":     round(reduzir_valor, 2),
            "Reduzir (%)":      round(reduzir_pct, 1),
            "Peso Atual (%)":   s["peso_receita"],
            "Peso Ideal (%)":   s["benchmark_saudavel"],
        })
    return pd.DataFrame(linhas).sort_values("Reduzir (R$)", ascending=False).reset_index(drop=True)

# =============================================================================
# FUNÇÕES — 13 AÇÕES DE CORTE
# =============================================================================
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
    df_atual   = df[(df['data'].dt.month == hoje.month) & (df['data'].dt.year == hoje.year)]
    df_passado = df[~((df['data'].dt.month == hoje.month) & (df['data'].dt.year == hoje.year))]
    if df_passado.empty:
        return None
    df_passado['mes_ano'] = df_passado['data'].dt.to_period('M')
    media_passado = df_passado[df_passado['categoria'] == categoria_limpa].groupby('mes_ano')['valor'].sum().mean()
    if pd.isna(media_passado) or media_passado <= 0:
        return None
    atual = df_atual[df_atual['categoria'] == categoria_limpa]['valor'].sum()
    alvo  = media_passado * (1 - meta_pct / 100)
    if atual <= alvo:
        progresso = 1.0
    elif atual >= media_passado:
        progresso = 0.0
    else:
        progresso = (media_passado - atual) / (media_passado - alvo)
    return {"media_passado": round(media_passado, 2), "atual": round(atual, 2),
            "alvo": round(alvo, 2), "progresso": max(0.0, min(1.0, progresso)),
            "economia_atual": round(max(0, media_passado - atual), 2)}

def evolucao_mensal_categoria(categoria_limpa, df_todas_despesas, meses=6):
    if df_todas_despesas is None or df_todas_despesas.empty:
        return pd.DataFrame()
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    df = df[df['categoria'] == categoria_limpa]
    if df.empty:
        return pd.DataFrame()
    df['mes_ano'] = df['data'].dt.to_period('M').astype(str)
    serie = df.groupby('mes_ano')['valor'].sum().reset_index().sort_values('mes_ano')
    return serie.tail(meses)

def detectar_retrocesso(categoria_limpa, df_todas_despesas):
    if df_todas_despesas is None or df_todas_despesas.empty:
        return None
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    hoje = datetime.now()
    df_atual = df[(df['data'].dt.month == hoje.month) & (df['data'].dt.year == hoje.year)]
    mes_ant = (pd.Timestamp(hoje) - pd.DateOffset(months=1)).to_period('M')
    df_anterior = df[df['data'].dt.to_period('M') == mes_ant]
    val_atual    = df_atual[df_atual['categoria'] == categoria_limpa]['valor'].sum()
    val_anterior = df_anterior[df_anterior['categoria'] == categoria_limpa]['valor'].sum()
    if val_anterior <= 0 or val_atual <= 0:
        return None
    variacao = ((val_atual - val_anterior) / val_anterior) * 100
    if variacao >= 15:
        return {"variacao": round(variacao, 1), "atual": round(val_atual, 2), "anterior": round(val_anterior, 2)}
    return None

def simular_corte(valor_atual, percentual):
    economia_mensal = valor_atual * (percentual / 100)
    return {"economia_mensal": round(economia_mensal, 2),
            "economia_anual":  round(economia_mensal * 12, 2)}

def impacto_na_reserva(economia_mensal, meta_reserva, total_fixos):
    if total_fixos <= 0:
        return None
    meses_extra_por_ano = (economia_mensal * 12) / total_fixos
    pct_meta_reserva = (economia_mensal / meta_reserva * 100) if meta_reserva > 0 else 0
    return {"meses_extra_por_ano": round(meses_extra_por_ano, 2),
            "pct_meta_reserva": round(pct_meta_reserva, 1)}

def classificar_matriz_esforco(categoria_limpa, economia_anual, economia_max):
    esforco = ESFORCO_POR_CATEGORIA.get(categoria_limpa, "Médio")
    impacto = "Alto" if economia_max > 0 and economia_anual >= economia_max * 0.5 else "Baixo"
    quadrante = f"{esforco} × {impacto}"
    if quadrante == "Fácil × Alto":
        emoji, cor, acao = "🟢", "#22C55E", "ATAQUE PRIMEIRO — corte rápido e impactante"
    elif quadrante in ("Fácil × Baixo", "Médio × Alto"):
        emoji, cor, acao = "🟡", "#F59E0B", "VALE A PENA — planeje com calma"
    elif quadrante == "Difícil × Alto":
        emoji, cor, acao = "🔴", "#EF4444", "PRECISA PLANEJAR — mudança estrutural"
    else:
        emoji, cor, acao = "⚪", "#8A95A5", "BAIXA PRIORIDADE — corte cosmético"
    return {"esforco": esforco, "impacto": impacto, "quadrante": quadrante,
            "emoji": emoji, "cor": cor, "acao": acao}

def detectar_assinaturas(df_todas_despesas, min_ocorrencias=3):
    if df_todas_despesas is None or df_todas_despesas.empty:
        return pd.DataFrame()
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    resultado = []
    for desc, grupo in df.groupby('descricao'):
        if len(grupo) < min_ocorrencias:
            continue
        if grupo['data'].dt.to_period('M').nunique() < 2:
            continue
        valor_medio = grupo['valor'].mean()
        desvio = grupo['valor'].std() / valor_medio if valor_medio > 0 else 1
        if desvio < 0.3:
            resultado.append({"descricao": desc, "valor_medio": round(valor_medio, 2),
                              "ocorrencias": len(grupo),
                              "meses_presentes": grupo['data'].dt.to_period('M').nunique(),
                              "total_mensal": round(valor_medio, 2),
                              "total_anual": round(valor_medio * 12, 2)})
    if not resultado:
        return pd.DataFrame()
    return pd.DataFrame(resultado).sort_values("total_anual", ascending=False)

def detectar_gastos_invisiveis(df_todas_despesas, limite_valor=60.0, min_ocorrencias=3):
    if df_todas_despesas is None or df_todas_despesas.empty:
        return pd.DataFrame()
    df = df_todas_despesas.copy()
    df['data'] = pd.to_datetime(df['data'])
    df['mes_ano'] = df['data'].dt.to_period('M')
    resultado = []
    for desc, grupo in df.groupby('descricao'):
        if len(grupo) < min_ocorrencias:
            continue
        valor_medio = grupo['valor'].mean()
        if valor_medio > limite_valor:
            continue
        meses = grupo['mes_ano'].nunique()
        if meses == 0:
            continue
        freq = len(grupo) / meses
        total_mensal = valor_medio * freq
        resultado.append({"descricao": desc, "valor_medio": round(valor_medio, 2),
                          "frequencia_mensal": round(freq, 1),
                          "total_mensal": round(total_mensal, 2),
                          "total_anual": round(total_mensal * 12, 2)})
    if not resultado:
        return pd.DataFrame()
    return pd.DataFrame(resultado).sort_values("total_anual", ascending=False)

def calcular_custo_hora(valor, salario_mensal, horas_mes=176):
    if salario_mensal <= 0:
        return 0.0
    return round(valor / (salario_mensal / horas_mes), 1)

def projetar_longo_prazo(valor_mensal, taxa_anual=0.10):
    taxa_m = (1 + taxa_anual) ** (1 / 12) - 1
    def _simular(anos):
        saldo = 0.0
        for _ in range(anos * 12):
            saldo = (saldo + valor_mensal) * (1 + taxa_m)
        return round(saldo, 2)
    return {"1_ano": _simular(1), "5_anos": _simular(5),
            "10_anos": _simular(10), "20_anos": _simular(20)}

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
            if res.data:
                return pd.DataFrame(res.data)
        except:
            pass
    return pd.DataFrame(columns=["id", "categoria", "valor_economia", "mes", "ano", "concluido_em"])

def remover_corte_concluido(corte_id):
    if supabase:
        try:
            supabase.table("cortes_concluidos").delete().eq("id", corte_id).execute()
        except:
            pass

def gerar_checklist_semanal(df_sug, df_concluidos):
    if df_sug.empty:
        return []
    concluidas = df_concluidos['categoria'].tolist() if not df_concluidos.empty else []
    return [{"categoria": s['categoria_limpa'],
             "acao": f"Reduzir gastos em {s['categoria_limpa']}",
             "economia": float(s['corte_sugerido'])}
            for _, s in df_sug.iterrows() if s['categoria_limpa'] not in concluidas]

def salvar_checklist_semanal(tarefas, semana_str):
    if not supabase or not tarefas:
        return
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
            if res.data:
                return pd.DataFrame(res.data)
        except:
            pass
    return pd.DataFrame(columns=["id", "categoria", "acao", "economia_estimada", "concluida", "semana"])

def marcar_item_checklist(item_id, concluida=True):
    if supabase:
        try:
            supabase.table("checklist_semanal").update({"concluida": concluida}).eq("id", item_id).execute()
        except:
            pass

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
# FUNÇÕES — PERSISTÊNCIA DO SIMULADOR DE INVESTIMENTO
# =============================================================================
def salvar_simulacao_investimento(nome, aporte, anos, taxa,
                                    montante, investido, juros):
    if supabase:
        try:
            supabase.table("simulacoes_investimento").insert({
                "nome":             str(nome).strip(),
                "aporte_mensal":    float(aporte),
                "anos":             int(anos),
                "taxa_anual":       float(taxa),
                "montante_final":   float(montante),
                "total_investido":  float(investido),
                "juros_totais":     float(juros),
            }).execute()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar simulação: {e}")
            return False
    else:
        st.warning("Supabase não conectado — a simulação não foi salva.")
        return False

def carregar_simulacoes_investimento():
    if supabase:
        try:
            res = supabase.table("simulacoes_investimento").select("*") \
                .order("criado_em", desc=True).execute()
            if res.data:
                return pd.DataFrame(res.data)
        except:
            pass
    return pd.DataFrame(columns=["id", "nome", "aporte_mensal", "anos",
                                  "taxa_anual", "montante_final",
                                  "total_investido", "juros_totais", "criado_em"])

def remover_simulacao_investimento(sim_id):
    if supabase:
        try:
            supabase.table("simulacoes_investimento").delete().eq("id", sim_id).execute()
        except:
            pass

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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📌 Planejamento & Cenários", "💳 Controle de Gastos Diários",
    "⚙ Gerenciar Custos Fixos", "📈 Simulador de Investimentos",
    "📊 DRE & Análise de Lucro", "📑 Relatórios PDF",
    "📅 Relatório Mensal", "✂️ Cortes Inteligentes"
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
# TAB 4 — SIMULADOR DE INVESTIMENTO COM PERSISTÊNCIA
# =============================================================================
with tab4:
    st.subheader("📈 Simulador de Crescimento Patrimonial (Juros Compostos)")
    st.markdown("Simule cenários, **salve no Supabase** e compare diferentes estratégias de investimento.")

    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        aporte_sim = st.number_input("Aporte Mensal Utilizado (R$)",
                                       value=float(meta_reserva_efetiva), step=50.0,
                                       key="aporte_sim")
        anos_sim = st.slider("Horizonte de Tempo (Anos)", min_value=1, max_value=30,
                              value=5, key="anos_sim")
    with col_sim2:
        taxa_anual_sim = st.slider("Rentabilidade Anual Estimada (%)", min_value=1.0,
                                     max_value=20.0, value=10.0, step=0.5,
                                     key="taxa_sim")
        nome_sim = st.text_input("Nome da simulação (para salvar)",
                                  placeholder="Ex: Cenário conservador 5 anos",
                                  key="nome_sim")

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
            if st.button("💾 Salvar esta simulação", use_container_width=True,
                          key="btn_salvar_sim"):
                if not nome_sim.strip():
                    st.warning("Dê um nome à simulação antes de salvar.")
                else:
                    ok = salvar_simulacao_investimento(
                        nome_sim, aporte_sim, anos_sim, taxa_anual_sim,
                        montante_atual, total_investido, juros_totais
                    )
                    if ok:
                        st.success(f"Simulação '{nome_sim}' salva com sucesso!")
                        st.rerun()

        st.divider()
        fig_invest = px.area(df_proj, x="Ano",
                              y=["Patrimônio Total", "Total Investido"],
                              title="Evolução Patrimonial Projetada")
        fig_invest.update_layout(paper_bgcolor="#151B23",
                                  plot_bgcolor="#151B23",
                                  font_color="#E6EDF3")
        st.plotly_chart(fig_invest, use_container_width=True)

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

        df_show = df_sims[["id", "nome", "aporte_mensal", "anos", "taxa_anual",
                            "montante_final", "total_investido", "juros_totais",
                            "criado_em"]].copy()
        df_show["aporte_mensal"]  = df_show["aporte_mensal"].apply(lambda v: _fmt_brl(v))
        df_show["taxa_anual"]     = df_show["taxa_anual"].apply(lambda v: f"{v:.2f}%")
        df_show["montante_final"] = df_show["montante_final"].apply(lambda v: _fmt_brl(v))
        df_show["total_investido"]= df_show["total_investido"].apply(lambda v: _fmt_brl(v))
        df_show["juros_totais"]   = df_show["juros_totais"].apply(lambda v: _fmt_brl(v))
        df_show["anos"]           = df_show["anos"].apply(lambda v: f"{int(v)} anos")
        df_show["criado_em"]      = pd.to_datetime(df_show["criado_em"]).dt.strftime("%d/%m/%Y %H:%M")
        df_show.columns = ["ID", "Nome", "Aporte Mensal", "Prazo", "Taxa Anual",
                            "Montante Final", "Total Investido", "Juros",
                            "Salvo em"]
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
                if st.button(f"🗑️ {s['nome'][:20]}", key=f"del_sim_{s['id']}",
                              use_container_width=True):
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
    if mes_fechado:
        col_m3.error("🔒 Mês Fechado")
    else:
        col_m3.success("🟢 Mês Aberto")
    st.divider()
    with st.expander("💼 Definir Orçamento do Mês", expanded=(orcamento_valor == 0.0)):
        novo_orc = st.number_input("Orçamento (R$)", min_value=0.0, value=orcamento_valor, step=50.0, key=f"orc_{mes_sel}_{ano_sel}")
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
        if pct_uso >= 100:
            st.error(f"🚨 Orçamento estourado! Ultrapassou em R$ {abs(saldo_mes):,.2f}")
        elif pct_uso >= 80:
            st.warning(f"⚠️ {pct_uso:.1f}% do orçamento utilizado.")
        else:
            st.success(f"✅ Dentro do orçamento ({pct_uso:.1f}%).")
    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("#### 📊 Gastos por Categoria")
        if not df_mes.empty:
            df_cat = df_mes.groupby("categoria")["valor"].sum().reset_index()
            fig_cat = px.bar(df_cat, x="categoria", y="valor", color="categoria", color_discrete_sequence=px.colors.qualitative.Set2)
            fig_cat.update_layout(paper_bgcolor="#151B23", plot_bgcolor="#151B23", font_color="#E6EDF3", showlegend=False)
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Sem despesas no mês.")
    with col_g2:
        st.markdown("#### 📋 Detalhamento")
        if not df_mes.empty:
            df_show = df_mes.copy()
            df_show["data"] = df_show["data"].dt.strftime("%d/%m/%Y")
            df_show = df_show[["data", "descricao", "categoria", "valor"]]
            df_show.columns = ["Data", "Descrição", "Categoria", "Valor (R$)"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma despesa neste mês.")
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
    else:
        st.info("Nenhum mês registrado ainda.")

# =============================================================================
# ABA 8 — CORTES INTELIGENTES
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
        mp1.metric("Meta Ideal (R$/mês)", _fmt_brl(meta_poup["meta_ideal_valor"]),
                    delta=f"{meta_poup['meta_ideal_pct']}% da renda")
        mp2.metric("Poupança Atual (R$/mês)", _fmt_brl(meta_poup["poupanca_atual"]),
                    delta=f"{meta_poup['poupanca_atual_pct']}% da renda")
        falta_delta = f"-{meta_poup['falta_pct']}% abaixo do ideal" if meta_poup["falta_valor"] > 0 else "Meta atingida"
        mp3.metric("Falta Poupar (R$/mês)", _fmt_brl(meta_poup["falta_valor"]),
                    delta=falta_delta,
                    delta_color="inverse" if meta_poup["falta_valor"] > 0 else "normal")

        st.markdown(
            f"<div style='background:{PALETA['fundo_card']};border:1px solid {PALETA['borda']};"
            f"border-radius:12px;padding:16px 20px;margin:10px 0;'>"
            f"<div style='display:flex;justify-content:space-between;'>"
            f"<b style='color:{PALETA['texto_principal']};'>Progresso da Meta de Poupança</b>"
            f"<span style='color:{meta_poup['status_cor']};font-weight:700;'>"
            f"{meta_poup['status_emoji']} {meta_poup['status_txt']} — "
            f"{int(meta_poup['progresso']*100)}%</span></div>"
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
        st.caption("Cada linha mostra o valor e o percentual exato a reduzir.")

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
                    st.warning(f"⚠️ '{s['categoria_limpa']}' subiu {retro['variacao']}% vs mês anterior ({_fmt_brl(retro['anterior'])} → {_fmt_brl(retro['atual'])}).")

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
                if prog is None:
                    continue
                pct = prog['progresso']
                if pct >= 0.75:
                    cor_prog, label = "#22C55E", "🟢 No caminho"
                elif pct >= 0.40:
                    cor_prog, label = "#F59E0B", "🟡 Atenção"
                else:
                    cor_prog, label = "#EF4444", "🔴 Não está cortando"
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
        if assinaturas.empty:
            st.info("Nenhuma assinatura detectada.")
        else:
            total_ass_anual = assinaturas["total_anual"].sum()
            st.warning(f"💡 **Potencial:** {_fmt_brl(total_ass_anual)}/ano ({_fmt_brl(total_ass_anual/12)}/mês).")
            st.dataframe(assinaturas, use_container_width=True, hide_index=True)
        st.divider()

        st.markdown("### 👻 Gastos Invisíveis")
        invisiveis = detectar_gastos_invisiveis(df_variaveis, limite_valor=60)
        if invisiveis.empty:
            st.info("Nenhum gasto invisível detectado.")
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
            else:
                st.info("Todas as sugestões já foram concluídas. 🎉")
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
    else:
        st.info("Nenhum corte marcado ainda.")

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
    else:
        st.info("Nenhuma análise salva ainda.")

# =============================================================================
# FIM DO APLICATIVO
# =============================================================================
