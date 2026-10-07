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
    # FUNDOS EM CAMADAS
    "fundo_principal":   "#0A0E14",
    "fundo_sidebar":     "#0D1219",
    "fundo_card":        "#131A23",
    "fundo_hover":       "#1B232E",
    "borda":             "#1F2937",
    "borda_acento":      "#3B82F6",

    # TEXTO
    "texto_principal":   "#E8EEF5",
    "texto_secundario":  "#8A95A5",

    # ACENTO
    "acento":            "#3B82F6",
    "acento_hover":      "#2563EB",
    "acento_glow":       "rgba(59,130,246,0.25)",

    # SEMÂNTICA FINANCEIRA
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
            radial-gradient(circle at 12% 0%, rgba(59,130,246,0.08), transparent 42%),
            radial-gradient(circle at 88% 100%, rgba(139,92,246,0.06), transparent 42%),
            radial-gradient(circle at 50% 50%, rgba(6,182,212,0.03), transparent 60%),
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
        background: linear-gradient(90deg, {PALETA["texto_principal"]} 60%, {PALETA["acento"]});
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
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, {PALETA["fundo_card"]} 0%, {PALETA["fundo_sidebar"]} 100%);
        border: 1px solid {PALETA["borda"]};
        border-radius: 14px;
        padding: 20px 22px !important;
        box-shadow: 0 4px 24px -8px rgba(0,0,0,0.5);
    }}
    div[data-testid="stMetric"] label {{
        color: {PALETA["texto_secundario"]} !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {PALETA["texto_principal"]} !important;
        font-family: 'Consolas', 'JetBrains Mono', monospace !important;
        font-size: 26px !important;
        font-weight: 700 !important;
    }}
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
        background: {PALETA["fundo_card"]} !important;
        color: {PALETA["texto_principal"]} !important;
        border: 1px solid {PALETA["borda"]} !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        background: {PALETA["acento"]} !important;
        border-color: {PALETA["acento"]} !important;
        color: #FFFFFF !important;
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
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {PALETA["acento"]}, {PALETA["ciano"]}) !important;
        color: #FFFFFF !important;
    }}
    .login-title {{
        background: linear-gradient(90deg, {PALETA["acento"]}, {PALETA["ciano"]}, {PALETA["roxo"]});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1.5px;
    }}
    .login-card {{
        background: linear-gradient(145deg, {PALETA["fundo_card"]} 0%, {PALETA["fundo_sidebar"]} 100%);
        border: 1px solid {PALETA["borda"]};
        border-radius: 20px;
        padding: 36px 32px;
        box-shadow: 0 24px 60px -20px rgba(0,0,0,0.6);
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
        st.markdown('<div class="login-title" style="font-size:32px; font-weight:800; text-align:center; margin-bottom:8px; letter-spacing:2px;">🛡️ INVEST CONTROL PRO</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px; color:#8A95A5; text-align:center; margin-bottom:24px;">Sistema Integrado de Projeção Econômica & Acesso Seguro</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
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
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

# -----------------------------------------------------------------------------
# CONEXÃO COM O SUPABASE
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
# FUNÇÕES DE BANCO DE DADOS
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
        "aluguel_total": 1700.0, "salario_a": 2700.0, "salario_b": 2000.0,
        "vr_a": 700.0, "meta_reserva_mensal": 800.0,
        "aluguel_a_custom": 850.0, "aluguel_b_custom": 850.0, "usa_edicao_manual": False
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
                if 'ano_mes' not in df.columns:
                    df['ano_mes'] = df['data'].dt.strftime('%Y-%m')
                return df
        except:
            pass
    return pd.DataFrame(columns=["id", "data", "descricao", "categoria", "valor", "ano_mes"])

def adicionar_despesa_variavel(data, descricao, categoria, valor):
    ano_mes_str = pd.to_datetime(data).strftime('%Y-%m')
    if supabase:
        try:
            data_formatada = str(data) if hasattr(data, "strftime") else data
            supabase.table("despesas_variaveis").insert({
                "data": data_formatada, "descricao": str(descricao).strip(),
                "categoria": str(categoria).strip(), "valor": float(valor),
                "ano_mes": ano_mes_str
            }).execute()
        except Exception as e:
            st.error(f"Erro ao salvar no banco de dados: {e}")

def remover_despesa_variavel(despesa_id):
    if supabase:
        try:
            supabase.table("despesas_variaveis").delete().eq("id", despesa_id).execute()
        except:
            pass

def obter_ou_criar_orcamento_mensal(ano_mes: str, valor_padrao: float = 1000.0):
    if supabase:
        try:
            res = supabase.table("orcamentos_mensais").select("*").eq("ano_mes", ano_mes).execute()
            if res.data:
                return res.data[0]
            else:
                novo = {"ano_mes": ano_mes, "orcamento_limite": float(valor_padrao), "status": "ativo"}
                supabase.table("orcamentos_mensais").insert(novo).execute()
                return novo
        except:
            pass
    return {"ano_mes": ano_mes, "orcamento_limite": float(valor_padrao), "status": "ativo"}

def atualizar_orcamento_mensal(ano_mes: str, novo_limite: float):
    if supabase:
        try:
            supabase.table("orcamentos_mensais").update({"orcamento_limite": float(novo_limite)}).eq("ano_mes", ano_mes).execute()
        except:
            pass

def verificar_e_fechar_meses_anteriores(orcamento_padrao: float):
    mes_atual = datetime.now().strftime('%Y-%m')
    if supabase:
        try:
            res = supabase.table("orcamentos_mensais").select("*").eq("status", "ativo").lt("ano_mes", mes_atual).execute()
            if res.data:
                for row in res.data:
                    m_ant = row["ano_mes"]
                    limite_ant = float(row["orcamento_limite"])
                    resp_esp = supabase.table("despesas_variaveis").select("valor, categoria").eq("ano_mes", m_ant).execute()
                    df_ant = pd.DataFrame(resp_esp.data) if resp_esp.data else pd.DataFrame(columns=["valor", "categoria"])
                    total_gasto = df_ant["valor"].sum() if not df_ant.empty else 0.0
                    status_fin = "Dentro do Orçamento" if total_gasto <= limite_ant else "Acima do Orçamento"
                    resumo_cat = df_ant.groupby("categoria")["valor"].sum().to_dict() if not df_ant.empty else {}
                    
                    supabase.table("relatorios_fechados").upsert({
                        "ano_mes": m_ant,
                        "orcamento_total": limite_ant,
                        "gasto_total": total_gasto,
                        "status_final": status_fin,
                        "detalhes_categorias": resumo_cat,
                        "fechado_em": datetime.now().isoformat()
                    }, on_conflict="ano_mes").execute()
                    
                    supabase.table("orcamentos_mensais").update({"status": "fechado"}).eq("ano_mes", m_ant).execute()
        except:
            pass

def listar_relatorios_fechados():
    if supabase:
        try:
            res = supabase.table("relatorios_fechados").select("*").order("ano_mes", desc=True).execute()
            if res.data:
                return res.data
        except:
            pass
    return []

config_inicial = carregar_configuracoes()
verificar_e_fechar_meses_anteriores(float(config_inicial.get("meta_reserva_mensal", 1000.0)))

def gerar_relatorio_pdf(df_fixos, df_variaveis, salario_a, salario_b, aluguel_a, aluguel_b):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#3B82F6'), spaceAfter=12, alignment=1)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#E6EDF3'), spaceBefore=12, spaceAfter=6)
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
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>3. Relatório de Despesas Variáveis</b>", heading_style))
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

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Parâmetros Financeiros")
if st.sidebar.button("🔒 Sair / Bloquear Tela", use_container_width=True):
    st.session_state['autenticado'] = False
    st.rerun()

st.sidebar.divider()
config = carregar_configuracoes()

cenario = st.sidebar.radio("Selecione o Cenário Ativo:", options=["COM Participação de B", "SEM Participação de B (Contingência)"], index=0)
b_participa = (cenario == "COM Participação de B")

st.sidebar.divider()
aluguel_input = st.sidebar.number_input("Valor do Aluguel Total (R$)", value=float(config["aluguel_total"]), step=50.0)
salario_a_input = st.sidebar.number_input("Salário Pessoa A (R$)", value=float(config["salario_a"]), step=100.0)
vr_a_input = st.sidebar.number_input("Vale Refeição (VR) A (R$)", value=float(config["vr_a"]), step=50.0)
salario_b_input = st.sidebar.number_input("Salário Pessoa B (R$)", value=float(config["salario_b"]), step=100.0) if b_participa else 0.0
meta_reserva_input = st.sidebar.number_input("Meta de Reserva Mensal (R$)", value=float(config["meta_reserva_mensal"]), step=50.0)

edicao_manual = st.sidebar.checkbox("Habilitar edição manual customizada", value=bool(config.get("usa_edicao_manual", False)))
val_a_db = float(config.get("aluguel_a_custom", aluguel_input * 0.5))
val_b_db = float(config.get("aluguel_b_custom", aluguel_input * 0.5))

aluguel_a_input, aluguel_b_input = val_a_db, val_b_db
if edicao_manual and b_participa:
    quem_edita = st.sidebar.radio("Quem ajustar?", options=["Pessoa A", "Pessoa B"], index=0)
    if quem_edita == "Pessoa A":
        aluguel_a_input = st.sidebar.number_input("Valor pago por A (R$)", min_value=0.0, max_value=float(aluguel_input), value=val_a_db, step=25.0)
        aluguel_b_input = max(0.0, aluguel_input - aluguel_a_input)
    else:
        aluguel_b_input = st.sidebar.number_input("Valor pago por B (R$)", min_value=0.0, max_value=float(aluguel_input), value=val_b_db, step=25.0)
        aluguel_a_input = max(0.0, aluguel_input - aluguel_b_input)

if st.sidebar.button("💾 Salvar Parâmetros"):
    a_save = aluguel_a_input if edicao_manual else aluguel_input * 0.5
    b_save = aluguel_b_input if edicao_manual else aluguel_input * 0.5
    salvar_configuracoes(aluguel_input, salario_a_input, salario_b_input, vr_a_input, meta_reserva_input, a_save, b_save, edicao_manual)
    st.sidebar.success("Parâmetros salvos!")
    st.rerun()

# -----------------------------------------------------------------------------
# CÁLCULOS E SELEÇÃO DO MÊS CORRENTE
# -----------------------------------------------------------------------------
if b_participa:
    if edicao_manual:
        aluguel_a, aluguel_b = aluguel_a_input, aluguel_b_input
        prop_a = aluguel_a / aluguel_input if aluguel_input > 0 else 0.5
    else:
        renda_total = salario_a_input + salario_b_input
        prop_a = salario_a_input / renda_total if renda_total > 0 else 1.0
        aluguel_a = aluguel_input * prop_a
        aluguel_b = aluguel_input * (1 - prop_a)
else:
    prop_a = 1.0
    aluguel_a, aluguel_b = aluguel_input, 0.0

df_gastos_fixos = carregar_gastos_fixos()
total_outros_fixos_a = df_gastos_fixos["valor"].sum() if not df_gastos_fixos.empty else 0.0
total_fixos_a = aluguel_a + total_outros_fixos_a

saldo_livre_bruto = salario_a_input - total_fixos_a
meta_reserva_efetiva = meta_reserva_input if b_participa else min(meta_reserva_input, max(0.0, saldo_livre_bruto - 100))
saldo_para_variaveis_geral = saldo_livre_bruto - meta_reserva_efetiva

ano_mes_atual = datetime.now().strftime('%Y-%m')
orcamento_obj_atual = obter_ou_criar_orcamento_mensal(ano_mes_atual, saldo_para_variaveis_geral)

df_variaveis_todas = carregar_despesas_variaveis()
df_variaveis_mes_atual = df_variaveis_todas[df_variaveis_todas['ano_mes'] == ano_mes_atual] if not df_variaveis_todas.empty else pd.DataFrame()
total_gastos_mes_atual = df_variaveis_mes_atual["valor"].sum() if not df_variaveis_mes_atual.empty else 0.0

orcamento_limite_atual = float(orcamento_obj_atual["orcamento_limite"])
saldo_caixa_restante = orcamento_limite_atual - total_gastos_mes_atual

# -----------------------------------------------------------------------------
# CORPO PRINCIPAL
# -----------------------------------------------------------------------------
st.title("📊 Painel de Projeção Econômica & Relatórios Mensais")
st.caption(f"Cenário Ativo: **{cenario}** | Mês Referência: **{ano_mes_atual}**")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Líquido (A)", f"+ R$ {salario_a_input:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col2.metric("Sua Parte no Aluguel", f"- R$ {aluguel_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col3.metric("Total Gastos Fixos (A)", f"- R$ {total_fixos_a:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
col4.metric("Aporte Reserva Mensal", f"- R$ {meta_reserva_efetiva:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

st.divider()

# ABAS DO APLICATIVO (COM A NOVA ABA DE CORTE DE GASTOS)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📌 Planejamento", 
    "💳 Gastos Diários", 
    "⚙ Custos Fixos", 
    "📈 Simulador",
    "📊 DRE & Lucro",
    "📅 Relatório Mensal",
    "✂️ IA de Corte de Gastos",
    "📑 Relatórios PDF"
])

with tab1:
    st.subheader("🏠 Divisão e Proporcionalidade do Aluguel")
    c_d1, c_d2 = st.columns(2)
    c_d1.info(f"👤 **Pessoa A:** R$ {aluguel_a:,.2f}")
    if b_participa: c_d2.success(f"👥 **Pessoa B:** R$ {aluguel_b:,.2f}")
    
    st.markdown("##### 🗓️ Progresso Anual da Reserva de Emergência")
    cols_grid = st.columns(4)
    meses_concluidos_count = sum(1 for i in range(12) if st.checkbox(f"{i+1}. {meses_nomes[i]}", key=f"reserva_mes_{i+1}"))
    pct_concluido = meses_concluidos_count / 12.0
    st.progress(pct_concluido)
    st.write(f"**Progresso:** {meses_concluidos_count}/12 meses (**{pct_concluido*100:.1f}%**)")

with tab2:
    st.subheader("🛒 Despesas Variáveis do Mês Corrente")
    col_lim1, col_lim2, col_lim3 = st.columns(3)
    col_lim1.metric("Orçamento do Mês", f"R$ {orcamento_limite_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_lim2.metric("Total Já Gasto", f"- R$ {total_gastos_mes_atual:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    col_lim3.metric("Saldo Restante", f"R$ {saldo_caixa_restante:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))
    
    with st.form("form_despesa", clear_on_submit=True):
        f1, f2, f3, f4 = st.columns([2, 3, 2, 2])
        d_exp = f1.date_input("Data")
        desc_exp = f2.text_input("Descrição")
        cat_exp = f3.selectbox("Categoria", ["Lazer / Passeios", "Farmácia / Saúde", "Vestuário", "Imprevistos", "Outros"])
        val_exp = f4.number_input("Valor (R$)", min_value=0.01, step=10.0)
        if st.form_submit_button("Lançar Despesa"):
            if desc_exp:
                adicionar_despesa_variavel(d_exp, desc_exp, cat_exp, val_exp)
                st.success("Lançado com sucesso no mês correspondente à data!")
                st.rerun()

    if not df_variaveis_mes_atual.empty:
        for _, row in df_variaveis_mes_atual.iterrows():
            rc1, rc2, rc3, rc4, rc5 = st.columns([2, 3, 2, 2, 1])
            rc1.write(row["data"].strftime("%d/%m/%Y"))
            rc2.write(row["descricao"])
            rc3.write(row["categoria"])
            rc4.write(f"R$ {row['valor']:,.2f}")
            if rc5.button("🗑️", key=f"del_v_{row['id']}"):
                remover_despesa_variavel(row["id"])
                st.rerun()

with tab3:
    st.subheader("📋 Custos Fixos")
    cf1, cf2 = st.columns([2, 1])
    with cf1:
        if not df_gastos_fixos.empty:
            for _, row in df_gastos_fixos.iterrows():
                fc1, fc2, fc3 = st.columns([3, 2, 1])
                fc1.write(row['descricao'])
                fc2.write(f"R$ {row['valor']:,.2f}")
                if fc3.button("Excluir", key=f"del_f_{row['id']}"):
                    remover_gasto_fixo(row['id'])
                    st.rerun()
    with cf2:
        with st.form("form_fixo", clear_on_submit=True):
            dfix = st.text_input("Descrição")
            vfix = st.number_input("Valor", min_value=0.01)
            if st.form_submit_button("Adicionar"):
                if dfix:
                    adicionar_gasto_fixo(dfix, vfix)
                    st.rerun()

with tab4:
    st.subheader("📈 Simulador de Juros Compostos")
    s_ap = st.number_input("Aporte", value=float(meta_reserva_efetiva), step=50.0)
    s_anos = st.slider("Anos", 1, 30, 5)
    s_tx = st.slider("Taxa Anual (%)", 1.0, 20.0, 10.0)
    montante = sum((s_ap * 12) * ((1 + s_tx/100) ** a) for a in range(s_anos))
    st.metric("Patrimônio Projetado", f"R$ {montante:,.2f}")

with tab5:
    st.subheader("📊 DRE & Análise de Lucro")
    rec_b = salario_a_input + vr_a_input
    lucro_op = rec_b - total_fixos_a - total_gastos_mes_atual
    st.metric("Lucro Líquido Operacional", f"R$ {lucro_op:,.2f}")

with tab6:
    st.subheader("📅 Relatório Mensal & Orçamento por Período")
    col_mo1, col_mo2 = st.columns(2)
    with col_mo1:
        st.markdown(f"#### Orçamento Vigente ({ano_mes_atual})")
        novo_limite_input = st.number_input("Definir Limite Orçamentário deste Mês (R$)", value=float(orcamento_limite_atual), step=50.0)
        if st.button("Atualizar Orçamento do Mês"):
            atualizar_orcamento_mensal(ano_mes_atual, novo_limite_input)
            st.success("Orçamento atualizado!")
            st.rerun()
    with col_mo2:
        st.markdown("#### Resumo do Ciclo")
        st.write(f"**Total Gasto:** R$ {total_gastos_mes_atual:,.2f}")
        st.write(f"**Status:** {'🟢 Dentro do Orçamento' if saldo_caixa_restante >= 0 else '🔴 Acima do Orçamento'}")

    st.divider()
    st.markdown("#### 📂 Histórico de Relatórios Mensais Fechados")
    relatorios_anteriores = listar_relatorios_fechados()
    if relatorios_anteriores:
        for rel in relatorios_anteriores:
            with st.expander(f"Mês: {rel['ano_mes']} | Status: {rel['status_final']} | Gasto: R$ {rel['gasto_total']:,.2f}"):
                st.write(f"**Orçamento Limite:** R$ {rel['orcamento_total']:,.2f}")
                st.write(f"**Total Gasto:** R$ {rel['gasto_total']:,.2f}")
    else:
        st.info("Nenhum relatório fechado anterior.")

# --- NOVA ABA 7: INTELIGÊNCIA DE CORTE DE GASTOS ---
with tab7:
    st.subheader("✂️ IA de Corte de Gastos & Otimização de Caixa")
    st.markdown("Análise automática das suas despesas do mês atual para identificar os maiores ralos de dinheiro e indicar onde realizar cortes estratégicos.")

    if not df_variaveis_mes_atual.empty:
        # Agrupa gastos por categoria no mês atual
        df_cortes = df_variaveis_mes_atual.groupby("categoria")["valor"].sum().reset_index()
        df_cortes = df_cortes.sort_values(by="valor", ascending=False)
        
        maior_gasto_cat = df_cortes.iloc[0]["categoria"]
        maior_gasto_val = df_cortes.iloc[0]["valor"]
        
        st.warning(f"🚨 **Principal Ralo de Caixa Detectado:** A categoria **{maior_gasto_cat}** é a que está drenando mais recursos neste mês, acumulando **R$ {maior_gasto_val:,.2f}** ({ (maior_gasto_val/total_gastos_mes_atual)*100:.1f}% do total gasto).")
        
        st.divider()
        st.markdown("#### 💡 Simulação de Cenários de Corte de Gastos")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        
        corte_10 = maior_gasto_val * 0.10
        corte_15 = maior_gasto_val * 0.15
        corte_20 = maior_gasto_val * 0.20
        
        col_c1.metric("Corte de 10% em " + maior_gasto_cat, f"Economia: R$ {corte_10:,.2f}", delta=f"Novo Total: R$ {maior_gasto_val - corte_10:,.2f}")
        col_c2.metric("Corte de 15% em " + maior_gasto_cat, f"Economia: R$ {corte_15:,.2f}", delta=f"Novo Total: R$ {maior_gasto_val - corte_15:,.2f}")
        col_c3.metric("Corte de 20% em " + maior_gasto_cat, f"Economia: R$ {corte_20:,.2f}", delta=f"Novo Total: R$ {maior_gasto_val - corte_20:,.2f}")

        st.markdown("---")
        st.markdown("#### 📋 Detalhamento de Impacto por Categoria")
        
        # Exibe tabela formatada com sugestões de corte por categoria
        tabela_sugestoes = []
        for _, row in df_cortes.iterrows():
            cat = row["categoria"]
            val = row["valor"]
            tabela_sugestoes.append({
                "Categoria": cat,
                "Gasto Atual": f"R$ {val:,.2f}",
                "Sugestão Corte (10%)": f"Economia de R$ {val * 0.10:,.2f}",
                "Sugestão Corte (20%)": f"Economia de R$ {val * 0.20:,.2f}"
            })
        
        st.table(pd.DataFrame(tabela_sugestoes))
        
        if saldo_caixa_restante < 0:
            st.error(f"⚠️ **Atenção:** Você está estourado em R$ {abs(saldo_caixa_restante):,.2f} neste mês. Para equilibrar as contas, você precisa reduzir pelo menos esse valor das categorias acima.")
        else:
            st.success("🟢 Seu orçamento está equilibrado. Aplicar cortes nestas categorias aumentará diretamente o seu potencial de investimento e reserva!")
            
    else:
        st.info("🟢 Nenhuma despesa variável lançada no mês atual para gerar recomendações de corte.")

with tab8:
    st.subheader("📑 Relatórios PDF")
    pdf_bytes = gerar_relatorio_pdf(df_gastos_fixos, df_variaveis_mes_atual, salario_a_input, salario_b_input, aluguel_a, aluguel_b)
    st.download_button(
        label="📥 Baixar Relatório em PDF",
        data=pdf_bytes,
        file_name=f"Relatorio_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
