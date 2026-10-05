# ============================================================
#  💰 FINANCE PRO — Streamlit Cloud + Relatório PDF/Excel Mensal
#  Copie, cole e rode. Login: admin@finance.com / 123456
# ============================================================

import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime, date
from fpdf import FPDF

# ------------------------------------------------------------
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------------------
st.set_page_config(
    page_title="Finance Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# 🎨 PALETA
# ------------------------------------------------------------
PALETA = {
    "fundo":        "#0B0F14", "card":         "#151B23",
    "elevado":      "#1C242E", "borda":        "#232B36",
    "texto":        "#E8EEF5", "texto_sub":    "#8A95A5",
    "texto_fraco":  "#4A5563",
    "positivo":     "#22C55E", "positivo_bg":  "#0F2A1A",
    "negativo":     "#EF4444", "negativo_bg":  "#2A0F12",
    "alerta":       "#F59E0B", "alerta_bg":    "#2A1F0A",
    "acento":       "#3B82F6", "acento_hover": "#2563EB",
    "roxo":         "#7C3AED", "ciano":        "#06B6D4",
}

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _sanitize(txt) -> str:
    return str(txt).encode("latin-1", "replace").decode("latin-1")


# ------------------------------------------------------------
# 🎨 CSS GLOBAL
# ------------------------------------------------------------
def aplicar_css():
    st.markdown(f"""
    <style>
        .stApp {{ background: {PALETA['fundo']}; }}
        .block-container {{ padding: 1.5rem 2rem 2rem 2rem; max-width: 1400px; }}
        section[data-testid="stSidebar"] {{
            background: #0F141A;
            border-right: 1px solid {PALETA['borda']};
        }}
        section[data-testid="stSidebar"] * {{ color: {PALETA['texto']} !important; }}
        h1, h2, h3 {{ color: {PALETA['texto']}; }}
        .stTextInput input, .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] > div,
        .stDateInput input {{
            background: {PALETA['fundo']} !important;
            border: 1px solid {PALETA['borda']} !important;
            color: {PALETA['texto']} !important;
            border-radius: 8px !important;
        }}
        .stTextInput input:focus, .stNumberInput input:focus {{
            border-color: {PALETA['acento']} !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
        }}
        .stButton > button, .stDownloadButton > button {{
            background: {PALETA['acento']};
            color: white; border: none; border-radius: 8px;
            height: 42px; font-weight: 600; width: 100%;
            transition: 0.15s;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background: {PALETA['acento_hover']};
            box-shadow: 0 0 12px rgba(59,130,246,0.5);
        }}
        div[data-testid="stMetric"] {{
            background: {PALETA['card']};
            border: 1px solid {PALETA['borda']};
            border-radius: 14px;
            padding: 18px 20px;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {PALETA['texto_sub']} !important;
            font-size: 11px !important; letter-spacing: 1px;
        }}
        div[data-testid="stMetricValue"] {{
            color: {PALETA['texto']} !important;
            font-family: 'Consolas', monospace !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background: {PALETA['card']};
            border: 1px solid {PALETA['borda']};
            border-radius: 12px; padding: 6px; gap: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent; color: {PALETA['texto_sub']};
            border-radius: 8px; padding: 8px 16px; font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            background: {PALETA['acento']} !important;
            color: white !important;
        }}
        .stProgress > div > div > div > div {{ background: {PALETA['acento']}; }}
        .stProgress > div > div > div {{ background: {PALETA['elevado']}; }}
        .stDataFrame {{
            background: {PALETA['card']};
            border-radius: 12px;
            border: 1px solid {PALETA['borda']};
        }}
        .card {{
            background: {PALETA['card']};
            border: 1px solid {PALETA['borda']};
            border-radius: 14px; padding: 20px; margin-bottom: 12px;
        }}
        .card-title {{
            color: {PALETA['texto_sub']}; font-size: 11px;
            letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;
        }}
        .card-value {{
            color: {PALETA['texto']}; font-family: 'Consolas', monospace;
            font-size: 28px; font-weight: 700;
        }}
        .card-delta-pos {{ color: {PALETA['positivo']}; font-size: 12px; }}
        .card-delta-neg {{ color: {PALETA['negativo']}; font-size: 12px; }}
        .badge {{
            display: inline-block; padding: 3px 10px; border-radius: 999px;
            font-size: 10px; font-weight: 600;
        }}
        .badge-ok  {{ background:{PALETA['positivo_bg']}; color:{PALETA['positivo']}; }}
        .badge-wa  {{ background:{PALETA['alerta_bg']};   color:{PALETA['alerta']};   }}
        .badge-er  {{ background:{PALETA['negativo_bg']}; color:{PALETA['negativo']}; }}
        .badge-nu  {{ background:{PALETA['elevado']};     color:{PALETA['texto_sub']}; }}
        .logo {{ color: {PALETA['texto']}; font-size: 22px;
                 font-weight: 700; letter-spacing: 1px; }}
        .logo span {{ color: {PALETA['acento']}; }}
        #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


aplicar_css()


# ============================================================
# 🗄️ BANCO DE DADOS
# ============================================================
@st.cache_resource
def get_conn():
    conn = sqlite3.connect("finance.db", check_same_thread=False)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL,
            status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            atual REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL,
            cor TEXT NOT NULL DEFAULT '#3B82F6'
        );
    """)
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)",
                    ("admin@finance.com", "123456"))
        uid = cur.lastrowid
        cur.executemany("""
            INSERT INTO transacoes
            (usuario_id, data, descricao, categoria, valor, tipo, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (uid, "2026-10-05", "Salário mensal",   "Renda",       5400.00, "entrada", "pago"),
            (uid, "2026-10-07", "Aluguel",          "Moradia",     1200.00, "saida",   "pago"),
            (uid, "2026-10-10", "Energia elétrica", "Casa",         180.00, "saida",   "pendente"),
            (uid, "2026-10-12", "Freelance UI",     "Renda",        800.00, "entrada", "pago"),
            (uid, "2026-10-15", "Supermercado",     "Alimentação",  620.00, "saida",   "pago"),
            (uid, "2026-10-20", "Cartão crédito",   "Financeiro",   959.55, "saida",   "vencido"),
            (uid, "2026-09-05", "Salário mensal",   "Renda",       5400.00, "entrada", "pago"),
            (uid, "2026-09-08", "Aluguel",          "Moradia",     1200.00, "saida",   "pago"),
            (uid, "2026-09-14", "Supermercado",     "Alimentação",  580.00, "saida",   "pago"),
            (uid, "2026-09-22", "Internet",         "Casa",         120.00, "saida",   "pago"),
        ])
        cur.executemany("""
            INSERT INTO metas (usuario_id, titulo, atual, total, cor)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (uid, "Reserva de emergência",  3400.0,  5000.0, "#3B82F6"),
            (uid, "Viagem de férias",       1800.0,  5000.0, "#06B6D4"),
            (uid, "Entrada do apartamento", 12000.0, 30000.0, "#7C3AED"),
        ])
        conn.commit()
    return conn


# ------------------------------------------------------------
# 🧠 FUNÇÕES DE DADOS
# ------------------------------------------------------------
def login(email, senha):
    cur = get_conn().cursor()
    cur.execute("SELECT id, email FROM usuarios WHERE email=? AND senha=?", (email, senha))
    return cur.fetchone()


def resumo(uid):
    cur = get_conn().cursor()
    cur.execute("""
        SELECT
          COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor END), 0),
          COALESCE(SUM(CASE WHEN tipo='saida'   THEN valor END), 0)
        FROM transacoes WHERE usuario_id=?
    """, (uid,))
    ent, sai = cur.fetchone()
    return ent, sai, ent - sai


def listar_transacoes(uid):
    return pd.read_sql_query("""
        SELECT data, descricao AS Descrição, categoria AS Categoria,
               valor, tipo, status
        FROM transacoes WHERE usuario_id=?
        ORDER BY data DESC
    """, get_conn(), params=(uid,))


def listar_transacoes_mes(uid, ano, mes):
    return pd.read_sql_query("""
        SELECT data, descricao, categoria, valor, tipo, status
        FROM transacoes
        WHERE usuario_id=?
          AND strftime('%Y', data) = ?
          AND strftime('%m', data) = ?
        ORDER BY data ASC
    """, get_conn(), params=(uid, str(ano), f"{mes:02d}"))


def adicionar_transacao(uid, data, descricao, categoria, valor, tipo, status="pago"):
    conn = get_conn()
    conn.execute("""
        INSERT INTO transacoes
        (usuario_id, data, descricao, categoria, valor, tipo, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (uid, data, descricao, categoria, valor, tipo, status))
    conn.commit()


def listar_metas(uid):
    return pd.read_sql_query(
        "SELECT titulo, atual, total, cor FROM metas WHERE usuario_id=?",
        get_conn(), params=(uid,))


# ============================================================
# 📄 GERADOR DE PDF MENSAL
# ============================================================
def gerar_pdf_mensal(uid, ano, mes):
    df = listar_transacoes_mes(uid, ano, mes)
    mes_nome = MESES[mes - 1]

    entradas = df[df["tipo"] == "entrada"]["valor"].sum() if not df.empty else 0.0
    saidas   = df[df["tipo"] == "saida"]["valor"].sum()   if not df.empty else 0.0
    saldo    = entradas - saidas

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Header
    pdf.set_fill_color(11, 15, 20)
    pdf.rect(0, 0, 210, 35, "F")
    pdf.set_text_color(232, 238, 245)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(15, 10)
    pdf.cell(0, 8, "FINANCE PRO", 0, 1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(138, 149, 165)
    pdf.set_xy(15, 21)
    pdf.cell(0, 6, _sanitize(f"Relatorio Mensal de Gastos  |  {mes_nome} / {ano}"))

    # Resumo
    pdf.set_y(48)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "RESUMO DO MES", 0, 1)
    pdf.ln(2)

    y0 = pdf.get_y()
    box_w, box_h = 60, 24

    def bloco(x, titulo, valor, cor_rgb):
        pdf.set_fill_color(*cor_rgb[1])
        pdf.rect(x, y0, box_w, box_h, "F")
        pdf.set_xy(x, y0 + 3)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(box_w, 4, titulo, 0, 1, "C")
        pdf.set_x(x)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*cor_rgb[0])
        pdf.cell(box_w, 8, _sanitize(brl(valor)), 0, 1, "C")

    bloco(15,  "ENTRADAS", entradas, ((22, 163, 74),  (240, 253, 244)))
    bloco(75,  "SAIDAS",   saidas,   ((220, 38, 38),  (254, 242, 242)))
    bloco(135, "SALDO",    saldo,    ((37, 99, 235),  (239, 246, 255)))

    pdf.set_y(y0 + box_h + 8)

    # Tabela
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "DETALHAMENTO", 0, 1)
    pdf.ln(2)

    col_w   = [23, 72, 35, 35, 15]
    headers = ["DATA", "DESCRICAO", "CATEGORIA", "VALOR", "STATUS"]

    pdf.set_fill_color(28, 36, 46)
    pdf.set_text_color(232, 238, 245)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_x(15)
    for i, h in enumerate(headers):
        align = "R" if h == "VALOR" else "L"
        pdf.cell(col_w[i], 9, h, 0, 0, align, True)
    pdf.ln()

    if df.empty:
        pdf.set_text_color(120, 120, 120)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_x(15)
        pdf.cell(0, 12, "Nenhuma transacao registrada neste mes.", 0, 1)
    else:
        pdf.set_font("Helvetica", "", 9)
        for i, r in enumerate(df.itertuples(index=False)):
            if i % 2 == 0:
                pdf.set_fill_color(248, 250, 252)
            else:
                pdf.set_fill_color(255, 255, 255)

            try:
                data_br = datetime.strptime(r.data, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                data_br = r.data

            sinal = "+" if r.tipo == "entrada" else "-"
            valor_txt = f"{sinal} " + f"{r.valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            cor_valor = (34, 163, 74) if r.tipo == "entrada" else (220, 38, 38)

            pdf.set_text_color(60, 60, 60)
            pdf.set_x(15)
            pdf.cell(col_w[0], 8, _sanitize(data_br), 0, 0, "L", True)
            pdf.cell(col_w[1], 8, _sanitize(r.descricao[:42]), 0, 0, "L", True)
            pdf.cell(col_w[2], 8, _sanitize(r.categoria[:18]), 0, 0, "L", True)

            pdf.set_text_color(*cor_valor)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(col_w[3], 8, _sanitize(valor_txt), 0, 0, "R", True)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(col_w[4], 8, _sanitize(r.status.upper()[:8]), 0, 0, "R", True)
            pdf.ln()

        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.set_x(15)
        pdf.cell(col_w[0] + col_w[1] + col_w[2], 9, "TOTAL DE GASTOS DO MES", 0, 0, "R")
        pdf.set_text_color(220, 38, 38)
        pdf.set_x(145)
        pdf.cell(col_w[3] + col_w[4], 9,
                 _sanitize("R$ " + f"{saidas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
                 0, 1, "R")

    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(138, 149, 165)
    pdf.cell(0, 6,
             _sanitize(f"Gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}  -  Finance Pro"),
             0, 0, "C")

    return bytes(pdf.output())


# ============================================================
# 📊 GERADOR DE EXCEL MENSAL
# ============================================================
def gerar_excel_mensal(uid, ano, mes):
    df = listar_transacoes_mes(uid, ano, mes)
    if df.empty:
        df = pd.DataFrame(columns=["data", "descricao", "categoria", "valor", "tipo", "status"])

    df_vis = df.copy()
    df_vis["data"] = df_vis["data"].apply(
        lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") if d else d)
    df_vis.columns = ["Data", "Descrição", "Categoria", "Valor", "Tipo", "Status"]

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_vis.to_excel(writer, index=False, sheet_name=f"{MESES[mes-1]}_{ano}")
    buf.seek(0)
    return buf.getvalue()


# ============================================================
# 🔐 TELA DE LOGIN
# ============================================================
def tela_login():
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center; padding:40px 0 20px 0;">
            <div class="logo" style="font-size:32px;">💰 FINANCE <span>PRO</span></div>
            <div style="color:{PALETA['texto_sub']}; font-size:13px; margin-top:6px;">
                Controle seus salários e rendas com precisão
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        email = st.text_input("E-MAIL", value="admin@finance.com")
        senha = st.text_input("SENHA", value="123456", type="password")
        st.checkbox("Lembrar-me")

        if st.button("ENTRAR", use_container_width=True):
            user = login(email, senha)
            if user:
                st.session_state["uid"] = user[0]
                st.session_state["email"] = user[1]
                st.rerun()
            else:
                st.error("E-mail ou senha inválidos")
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# 📊 CARDS DE MÉTRICA
# ============================================================
def card_metricas():
    ent, sai, saldo = resumo(st.session_state["uid"])
    cor = PALETA["positivo"] if saldo >= 0 else PALETA["negativo"]
    seta = "▲" if saldo >= 0 else "▼"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">💵 ENTRADAS DO MÊS</div>
            <div class="card-value" style="color:{PALETA['positivo']};">{brl(ent)}</div>
            <div class="card-delta-pos">▲ receitas registradas</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">💸 SAÍDAS DO MÊS</div>
            <div class="card-value" style="color:{PALETA['negativo']};">{brl(sai)}</div>
            <div class="card-delta-neg">▼ despesas do período</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🏦 SALDO ATUAL</div>
            <div class="card-value" style="color:{cor};">{brl(saldo)}</div>
            <div class="card-delta-{'pos' if saldo>=0 else 'neg'}">{seta} saldo disponível</div>
        </div>""", unsafe_allow_html=True)


# ============================================================
# 📋 ABA DRE
# ============================================================
def aba_dre():
    st.markdown('<div class="card-title" style="padding-top:8px;">📋 DEMONSTRATIVO DE RESULTADO (DRE)</div>',
                unsafe_allow_html=True)
    df = listar_transacoes(st.session_state["uid"])
    if df.empty:
        st.info("Nenhuma transação registrada ainda.")
        return

    df_vis = df.copy()
    df_vis["Data"] = df_vis["data"].apply(
        lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") if d else d)
    df_vis = df_vis.drop(columns=["data"])
    df_vis["Valor"] = df_vis.apply(
        lambda r: ("+ " if r["tipo"] == "entrada" else "− ")
                  + f"{r['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        axis=1)
    df_vis = df_vis.drop(columns=["valor", "tipo"])

    st.dataframe(df_vis[["Data", "Descrição", "Categoria", "Valor", "status"]],
                 use_container_width=True, hide_index=True, height=380)

    st.markdown("""
    <div style="margin-top:10px;">
        <span class="badge badge-ok">● pago</span>
        <span class="badge badge-wa">⏳ pendente</span>
        <span class="badge badge-er">⚠ vencido</span>
        <span class="badge badge-nu">○ agendado</span>
    </div>""", unsafe_allow_html=True)


# ============================================================
# 🎯 ABA METAS
# ============================================================
def aba_metas():
    st.markdown('<div class="card-title" style="padding-top:8px;">🎯 METAS FINANCEIRAS</div>',
                unsafe_allow_html=True)
    metas = listar_metas(st.session_state["uid"])
    if metas.empty:
        st.info("Nenhuma meta cadastrada.")
        return
    for _, m in metas.iterrows():
        pct = (m["atual"] / m["total"]) if m["total"] else 0
        st.markdown(f"""
        <div class="card" style="padding:16px 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="color:{PALETA['texto']}; font-size:13px;">🎯 {m['titulo']}</div>
                <div style="color:{PALETA['texto_sub']}; font-size:12px;
                            font-family:Consolas,monospace;">
                    {brl(m['atual'])} / {brl(m['total'])}
                </div>
            </div>
            <div style="color:{PALETA['texto_sub']}; font-size:11px; text-align:right;
                        margin-top:4px;">{int(pct*100)}%</div>
        </div>""", unsafe_allow_html=True)
        st.progress(min(pct, 1.0))


# ============================================================
# ＋ ABA NOVA TRANSAÇÃO
# ============================================================
def aba_nova():
    st.markdown('<div class="card-title" style="padding-top:8px;">＋ NOVA TRANSAÇÃO</div>',
                unsafe_allow_html=True)
    with st.form("form_transacao", clear_on_submit=True):
        descricao = st.text_input("DESCRIÇÃO", placeholder="Ex: Salário, Aluguel...")
        c1, c2 = st.columns(2)
        with c1:
            valor = st.number_input("VALOR (R$)", min_value=0.0, step=10.0, format="%.2f")
        with c2:
            data = st.date_input("DATA", value=date.today())
        c3, c4 = st.columns(2)
        with c3:
            categoria = st.selectbox("CATEGORIA",
                ["Renda", "Moradia", "Alimentação", "Transporte",
                 "Lazer", "Financeiro", "Outros"])
        with c4:
            tipo = st.selectbox("TIPO", ["entrada", "saida"])

        enviar = st.form_submit_button("💾  SALVAR TRANSAÇÃO", use_container_width=True)
        if enviar:
            if not descricao.strip():
                st.warning("Informe a descrição.")
            elif valor <= 0:
                st.warning("Valor deve ser maior que zero.")
            else:
                adicionar_transacao(st.session_state["uid"],
                                    data.strftime("%Y-%m-%d"),
                                    descricao.strip(), categoria,
                                    float(valor), tipo)
                st.success("Transação salva com sucesso!")
                st.rerun()


# ============================================================
# 📄 ABA RELATÓRIO MENSAL
# ============================================================
def aba_relatorio():
    st.markdown('<div class="card-title" style="padding-top:8px;">📄 RELATÓRIO MENSAL DE GASTOS</div>',
                unsafe_allow_html=True)

    hoje = date.today()
    c1, c2 = st.columns(2)
    with c1:
        mes = st.selectbox("MÊS", list(range(1, 13)),
                           index=hoje.month - 1,
                           format_func=lambda m: MESES[m - 1])
    with c2:
        anos_disponiveis = list(range(hoje.year - 3, hoje.year + 2))
        ano = st.selectbox("ANO", anos_disponiveis,
                           index=anos_disponiveis.index(hoje.year)
                           if hoje.year in anos_disponiveis else 0)

    df = listar_transacoes_mes(st.session_state["uid"], ano, mes)

    entradas = df[df["tipo"] == "entrada"]["valor"].sum() if not df.empty else 0.0
    saidas   = df[df["tipo"] == "saida"]["valor"].sum()   if not df.empty else 0.0
    saldo    = entradas - saidas

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("💵 ENTRADAS DO MÊS", brl(entradas))
    m2.metric("💸 GASTOS DO MÊS",   brl(saidas))
    m3.metric("🏦 SALDO DO MÊS",    brl(saldo))

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">TRANSAÇÕES DE {MESES[mes-1].upper()} / {ano}</div>',
                unsafe_allow_html=True)

    if df.empty:
        st.info(f"Nenhuma transação registrada em {MESES[mes-1]} / {ano}.")
    else:
        df_vis = df.copy()
        df_vis["data"] = df_vis["data"].apply(
            lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y") if d else d)
        df_vis["valor"] = df_vis.apply(
            lambda r: ("+ " if r["tipo"] == "entrada" else "− ")
                      + f"{r['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            axis=1)
        df_vis = df_vis.drop(columns=["tipo"])
        df_vis.columns = ["Data", "Descrição", "Categoria", "Valor", "Status"]
        st.dataframe(df_vis, use_container_width=True,
                     hide_index=True, height=320)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="card-title">EXPORTAR RELATÓRIO</div>',
                unsafe_allow_html=True)

    b1, b2 = st.columns(2)

    with b1:
        if st.button("📄  Gerar PDF do mês", use_container_width=True, key="btn_gerar_pdf"):
            pdf_bytes = gerar_pdf_mensal(st.session_state["uid"], ano, mes)
            st.session_state["pdf_bytes"] = pdf_bytes
            st.session_state["pdf_nome"]  = f"relatorio_{ano}_{mes:02d}.pdf"

        if "pdf_bytes" in st.session_state:
            st.download_button(
                "⬇️  Baixar PDF gerado",
                data=st.session_state["pdf_bytes"],
                file_name=st.session_state["pdf_nome"],
                mime="application/pdf",
                use_container_width=True,
                key="dl_pdf",
            )

    with b2:
        excel_bytes = gerar_excel_mensal(st.session_state["uid"], ano, mes)
        st.download_button(
            "📊  Baixar planilha Excel do mês",
            data=excel_bytes,
            file_name=f"gastos_{ano}_{mes:02d}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="dl_xlsx",
        )

    if df.empty:
        st.warning("Não há dados para exportar neste mês.")


# ============================================================
# 🖥️ APP PRINCIPAL
# ============================================================
def app_principal():
    with st.sidebar:
        st.markdown('<div class="logo">💰 FINANCE <span>PRO</span></div>',
                    unsafe_allow_html=True)
        st.markdown("---")
        st.radio("Menu",
                 ["📊 Dashboard", "💼 Salários", "📈 Rendas",
                  "💸 Despesas", "📋 DRE", "🎯 Metas",
                  "📄 Relatórios", "⚙️ Configurações"],
                 label_visibility="collapsed")
        st.markdown("---")
        st.markdown(f"""
        <div style="color:{PALETA['positivo']}; font-size:12px;">● conectado</div>
        <div style="color:#4A5563; font-size:11px;">{st.session_state.get('email','')}</div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    ct, cb = st.columns([4, 1])
    with ct:
        st.markdown(f"""
        <div style="color:{PALETA['texto']}; font-size:26px; font-weight:700;">
            Dashboard
        </div>
        <div style="color:{PALETA['texto_sub']}; font-size:12px; margin-top:-8px;">
            {datetime.now().strftime('%B de %Y')}  •  bem-vindo de volta
        </div>""", unsafe_allow_html=True)
    with cb:
        if st.button("🔄  Atualizar", use_container_width=True):
            st.rerun()

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    card_metricas()
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋  DRE", "🎯  Metas", "＋  Nova", "📄  Relatório"]
    )
    with tab1: aba_dre()
    with tab2: aba_metas()
    with tab3: aba_nova()
    with tab4: aba_relatorio()


# ============================================================
# 🚀 ROTEADOR
# ============================================================
if "uid" not in st.session_state:
    tela_login()
else:
    app_principal()
