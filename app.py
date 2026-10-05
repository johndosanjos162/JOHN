# ============================================================
#  💰 FINANCE PRO — App completo com design de ponta
#  Visual + Funcionalidades integradas
#  Biblioteca: CustomTkinter + SQLite
# ============================================================

import customtkinter as ctk
import sqlite3
import os
from datetime import datetime
from tkinter import messagebox

# ------------------------------------------------------------
# 🎨 TEMA GLOBAL
# ------------------------------------------------------------
PALETA = {
    "fundo":        "#0B0F14", "sidebar":     "#0F141A",
    "card":         "#151B23", "elevado":     "#1C242E",
    "borda":        "#232B36", "texto":       "#E8EEF5",
    "texto_sub":    "#8A95A5", "texto_fraco": "#4A5563",
    "positivo":     "#22C55E", "positivo_bg": "#0F2A1A",
    "negativo":     "#EF4444", "negativo_bg": "#2A0F12",
    "alerta":       "#F59E0B", "alerta_bg":   "#2A1F0A",
    "acento":       "#3B82F6", "acento_hover":"#2563EB",
    "roxo":         "#7C3AED", "ciano":       "#06B6D4",
}

FONTES = {
    "logo":     ("Segoe UI Semibold", 22),
    "titulo":   ("Segoe UI Semibold", 24),
    "subtitulo":("Segoe UI", 13),
    "corpo":    ("Segoe UI", 12),
    "label":    ("Segoe UI", 11),
    "legenda":  ("Segoe UI", 10),
    "valor_g":  ("Consolas", 26, "bold"),
    "valor_m":  ("Consolas", 16, "bold"),
    "valor_p":  ("Consolas", 12),
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def brl(v):
    """Formata valor em Real brasileiro."""
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ============================================================
# 🗄️ BANCO DE DADOS
# ============================================================
class Banco:
    def __init__(self, path="finance.db"):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self._criar()
        self._seed()

    def _criar(self):
        self.cursor.executescript("""
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
        self.conn.commit()

    def _seed(self):
        self.cursor.execute("SELECT COUNT(*) FROM usuarios")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO usuarios (email, senha) VALUES (?, ?)",
                ("admin@finance.com", "123456"))
            uid = self.cursor.lastrowid

            self.cursor.executemany("""
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
            ])

            self.cursor.executemany("""
                INSERT INTO metas (usuario_id, titulo, atual, total, cor)
                VALUES (?, ?, ?, ?, ?)
            """, [
                (uid, "Reserva de emergência",  3400.0,  5000.0, "#3B82F6"),
                (uid, "Viagem de férias",       1800.0,  5000.0, "#06B6D4"),
                (uid, "Entrada do apartamento", 12000.0, 30000.0, "#7C3AED"),
            ])
            self.conn.commit()

    def login(self, email, senha):
        self.cursor.execute(
            "SELECT id, email FROM usuarios WHERE email=? AND senha=?",
            (email, senha))
        return self.cursor.fetchone()

    def listar_transacoes(self, uid):
        self.cursor.execute("""
            SELECT data, descricao, categoria, valor, tipo, status
            FROM transacoes WHERE usuario_id=? ORDER BY data DESC
        """, (uid,))
        return self.cursor.fetchall()

    def adicionar_transacao(self, uid, data, descricao, categoria,
                            valor, tipo, status="pago"):
        self.cursor.execute("""
            INSERT INTO transacoes
            (usuario_id, data, descricao, categoria, valor, tipo, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (uid, data, descricao, categoria, valor, tipo, status))
        self.conn.commit()

    def resumo(self, uid):
        self.cursor.execute("""
            SELECT
              COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor END), 0),
              COALESCE(SUM(CASE WHEN tipo='saida'   THEN valor END), 0)
            FROM transacoes WHERE usuario_id=?
        """, (uid,))
        ent, sai = self.cursor.fetchone()
        return ent, sai, ent - sai

    def listar_metas(self, uid):
        self.cursor.execute("""
            SELECT titulo, atual, total, cor FROM metas WHERE usuario_id=?
        """, (uid,))
        return self.cursor.fetchall()


# ============================================================
# 🧩 COMPONENTES REUTILIZÁVEIS
# ============================================================
def card_metrica(parent, titulo, valor, delta, cor_delta, icone="💵"):
    card = ctk.CTkFrame(parent, fg_color=PALETA["card"],
                        border_color=PALETA["borda"], border_width=1,
                        corner_radius=14)
    topo = ctk.CTkFrame(card, fg_color="transparent")
    topo.pack(fill="x", padx=20, pady=(18, 4))
    ctk.CTkLabel(topo, text=f"{icone}  {titulo.upper()}",
                 font=FONTES["label"], text_color=PALETA["texto_sub"]).pack(side="left")
    ctk.CTkLabel(card, text=valor, font=FONTES["valor_g"],
                 text_color=PALETA["texto"]).pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=delta, font=FONTES["legenda"],
                 text_color=cor_delta).pack(anchor="w", padx=20, pady=(0, 18))
    return card


def botao_primario(parent, texto, comando=None, **kw):
    return ctk.CTkButton(parent, text=texto, command=comando,
                         fg_color=PALETA["acento"], hover_color=PALETA["acento_hover"],
                         text_color="#FFFFFF", font=("Segoe UI Semibold", 12),
                         corner_radius=8, height=40, **kw)


def botao_secundario(parent, texto, comando=None, **kw):
    return ctk.CTkButton(parent, text=texto, command=comando,
                         fg_color=PALETA["elevado"], hover_color=PALETA["borda"],
                         text_color=PALETA["texto"], border_color=PALETA["borda"],
                         border_width=1, font=("Segoe UI", 12),
                         corner_radius=8, height=36, **kw)


def botao_perigo(parent, texto, comando=None, **kw):
    return ctk.CTkButton(parent, text=texto, command=comando,
                         fg_color=PALETA["negativo"], hover_color="#DC2626",
                         text_color="#FFFFFF", font=("Segoe UI Semibold", 12),
                         corner_radius=8, height=40, **kw)


def input_estilizado(parent, placeholder="", senha=False):
    entry = ctk.CTkEntry(parent, placeholder_text=placeholder,
                         fg_color=PALETA["fundo"], border_color=PALETA["borda"],
                         border_width=1, text_color=PALETA["texto"],
                         placeholder_text_color=PALETA["texto_fraco"],
                         font=FONTES["corpo"], corner_radius=8, height=42,
                         show="•" if senha else "")
    entry.bind("<FocusIn>",  lambda e: entry.configure(border_color=PALETA["acento"]))
    entry.bind("<FocusOut>", lambda e: entry.configure(border_color=PALETA["borda"]))
    return entry


def progress_bar(parent, titulo, atual, total, cor=PALETA["acento"]):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    topo = ctk.CTkFrame(frame, fg_color="transparent")
    topo.pack(fill="x")
    ctk.CTkLabel(topo, text=titulo, font=FONTES["label"],
                 text_color=PALETA["texto"]).pack(side="left")
    pct = int((atual / total) * 100) if total else 0
    ctk.CTkLabel(topo, text=f"{brl(atual)} / {brl(total)}",
                 font=FONTES["legenda"], text_color=PALETA["texto_sub"]).pack(side="right")
    barra = ctk.CTkProgressBar(frame, progress_color=cor,
                               fg_color=PALETA["elevado"],
                               corner_radius=999, height=10)
    barra.pack(fill="x", pady=(8, 4))
    barra.set(atual / total if total else 0)
    ctk.CTkLabel(frame, text=f"{pct}%", font=FONTES["legenda"],
                 text_color=PALETA["texto_sub"]).pack(anchor="e")
    return frame


def badge(parent, texto, tipo="sucesso"):
    cores = {
        "sucesso": (PALETA["positivo_bg"], PALETA["positivo"], "●"),
        "alerta":  (PALETA["alerta_bg"],   PALETA["alerta"],   "⏳"),
        "erro":    (PALETA["negativo_bg"], PALETA["negativo"], "⚠"),
        "neutro":  (PALETA["elevado"],     PALETA["texto_sub"],"○"),
    }
    bg, fg, ico = cores.get(tipo, cores["neutro"])
    return ctk.CTkLabel(parent, text=f"  {ico}  {texto}  ",
                        fg_color=bg, text_color=fg,
                        corner_radius=999, font=("Segoe UI", 10))


# ============================================================
# 🔐 TELA DE LOGIN
# ============================================================
class TelaLogin(ctk.CTk):
    def __init__(self, banco):
        super().__init__()
        self.banco = banco
        self.title("Finance Pro — Login")
        self.geometry("1100x700")
        self.configure(fg_color=PALETA["fundo"])
        self._centralizar(1100, 700)
        self._construir()

    def _centralizar(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _construir(self):
        cont = ctk.CTkFrame(self, fg_color="transparent")
        cont.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(cont, text="💰  FINANCE PRO", font=FONTES["logo"],
                     text_color=PALETA["texto"]).pack(pady=(0, 4))
        ctk.CTkLabel(cont, text="Controle seus salários e rendas com precisão",
                     font=FONTES["subtitulo"], text_color=PALETA["texto_sub"]).pack(pady=(0, 28))

        card = ctk.CTkFrame(cont, fg_color=PALETA["card"],
                            border_color=PALETA["borda"], border_width=1,
                            corner_radius=16, width=420, height=440)
        card.pack()
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="E-MAIL", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w", padx=36, pady=(36, 6))
        self.entry_email = input_estilizado(card, "admin@finance.com")
        self.entry_email.pack(fill="x", padx=36)
        self.entry_email.insert(0, "admin@finance.com")

        ctk.CTkLabel(card, text="SENHA", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w", padx=36, pady=(18, 6))
        self.entry_senha = input_estilizado(card, "••••••••", senha=True)
        self.entry_senha.pack(fill="x", padx=36)
        self.entry_senha.insert(0, "123456")

        linha = ctk.CTkFrame(card, fg_color="transparent")
        linha.pack(fill="x", padx=36, pady=(14, 0))
        ctk.CTkCheckBox(linha, text="Lembrar-me", font=FONTES["legenda"],
                        text_color=PALETA["texto_sub"],
                        fg_color=PALETA["acento"], hover_color=PALETA["acento_hover"],
                        border_color=PALETA["borda"], corner_radius=4,
                        checkbox_width=16, checkbox_height=16).pack(side="left")
        ctk.CTkLabel(linha, text="Esqueci a senha", font=FONTES["legenda"],
                     text_color=PALETA["acento"], cursor="hand2").pack(side="right")

        botao_primario(card, "ENTRAR", self._login).pack(fill="x", padx=36, pady=(24, 8))

        ctk.CTkLabel(card, text="Não tem conta?  Criar agora →",
                     font=FONTES["legenda"], text_color=PALETA["texto_sub"],
                     cursor="hand2").pack(pady=(0, 36))

        ctk.CTkLabel(cont, text="v1.0.0  •  © 2026 Finance Pro",
                     font=FONTES["legenda"],
                     text_color=PALETA["texto_fraco"]).pack(pady=(20, 0))

        self.entry_senha.bind("<Return>", lambda e: self._login())

    def _login(self):
        email = self.entry_email.get().strip()
        senha = self.entry_senha.get().strip()
        user = self.banco.login(email, senha)
        if user:
            uid = user[0]
            self.destroy()
            AppPrincipal(self.banco, uid).mainloop()
        else:
            messagebox.showerror("Erro", "E-mail ou senha inválidos")


# ============================================================
# 📊 APP PRINCIPAL
# ============================================================
class AppPrincipal(ctk.CTk):
    def __init__(self, banco, uid):
        super().__init__()
        self.banco = banco
        self.uid = uid
        self.title("Finance Pro")
        self.geometry("1300x780")
        self.configure(fg_color=PALETA["fundo"])
        self._centralizar(1300, 780)
        self._construir()

    def _centralizar(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _construir(self):
        # SIDEBAR
        sidebar = ctk.CTkFrame(self, fg_color=PALETA["sidebar"],
                               corner_radius=0, width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="💰  FINANCE", font=FONTES["logo"],
                     text_color=PALETA["texto"]).pack(anchor="w", padx=24, pady=(28, 32))

        itens = [("📊  Dashboard", True), ("💼  Salários", False),
                 ("📈  Rendas", False), ("💸  Despesas", False),
                 ("📋  DRE", False), ("🎯  Metas", False),
                 ("⚙️  Configurações", False)]
        for txt, ativo in itens:
            bg = PALETA["elevado"] if ativo else "transparent"
            fg = PALETA["acento"] if ativo else PALETA["texto_sub"]
            ctk.CTkLabel(sidebar, text=txt, font=FONTES["corpo"],
                         text_color=fg, fg_color=bg, anchor="w",
                         height=40, corner_radius=8).pack(fill="x", padx=14, pady=2)

        rodape = ctk.CTkFrame(sidebar, fg_color="transparent")
        rodape.pack(side="bottom", fill="x", padx=20, pady=20)
        ctk.CTkLabel(rodape, text="● conectado", font=FONTES["legenda"],
                     text_color=PALETA["positivo"]).pack(anchor="w")
        ctk.CTkLabel(rodape, text="v1.0.0", font=FONTES["legenda"],
                     text_color=PALETA["texto_fraco"]).pack(anchor="w")

        # ÁREA PRINCIPAL
        self.area = ctk.CTkFrame(self, fg_color="transparent")
        self.area.pack(side="left", fill="both", expand=True, padx=24, pady=20)

        topbar = ctk.CTkFrame(self.area, fg_color="transparent")
        topbar.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(topbar, text="Dashboard", font=FONTES["titulo"],
                     text_color=PALETA["texto"]).pack(side="left")
        ctk.CTkLabel(topbar, text="outubro 2026  •  bem-vindo de volta",
                     font=FONTES["legenda"],
                     text_color=PALETA["texto_sub"]).pack(side="left", padx=(16, 0), pady=(10, 0))
        botao_secundario(topbar, "🔄  Atualizar",
                         self._refresh).pack(side="right")

        self._construir_conteudo()

    def _construir_conteudo(self):
        # CARDS DE MÉTRICA
        ent, sai, saldo = self.banco.resumo(self.uid)
        linha_cards = ctk.CTkFrame(self.area, fg_color="transparent")
        linha_cards.pack(fill="x", pady=(0, 20))

        card_metrica(linha_cards, "Entradas do mês", brl(ent),
                     "▲ receitas registradas", PALETA["positivo"], "💵"
                     ).pack(side="left", expand=True, fill="x", padx=(0, 8))
        card_metrica(linha_cards, "Saídas do mês", brl(sai),
                     "▼ despesas do período", PALETA["negativo"], "💸"
                     ).pack(side="left", expand=True, fill="x", padx=8)
        cor_saldo = PALETA["positivo"] if saldo >= 0 else PALETA["negativo"]
        card_metrica(linha_cards, "Saldo atual", brl(saldo),
                     "saldo disponível", cor_saldo, "🏦"
                     ).pack(side="left", expand=True, fill="x", padx=(8, 0))

        # ABAS
        abas = ctk.CTkTabview(
            self.area, fg_color=PALETA["card"],
            segmented_button_fg_color=PALETA["elevado"],
            segmented_button_selected_color=PALETA["acento"],
            segmented_button_selected_hover_color=PALETA["acento_hover"],
            segmented_button_unselected_color=PALETA["elevado"],
            segmented_button_unselected_hover_color=PALETA["borda"],
            text_color=PALETA["texto"],
            border_color=PALETA["borda"], border_width=1,
            corner_radius=14)
        abas.pack(fill="both", expand=True)

        self._aba_dre(abas.add("📋  DRE"))
        self._aba_metas(abas.add("🎯  Metas"))
        self._aba_nova(abas.add("＋  Nova"))

    def _refresh(self):
        for w in self.area.winfo_children():
            w.destroy()
        self._construir()

    # ---------- ABA DRE ----------
    def _aba_dre(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(wrap, text="DEMONSTRATIVO DE RESULTADO (DRE)",
                     font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w", pady=(0, 12))

        tabela_wrap = ctk.CTkFrame(wrap, fg_color=PALETA["fundo"],
                                   border_color=PALETA["borda"], border_width=1,
                                   corner_radius=12)
        tabela_wrap.pack(fill="both", expand=True)

        scroll = ctk.CTkScrollableFrame(
            tabela_wrap, fg_color=PALETA["fundo"],
            scrollbar_button_color=PALETA["borda"],
            scrollbar_button_hover_color=PALETA["acento"],
            corner_radius=12)
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        cabecalho = ["DATA", "DESCRIÇÃO", "CATEGORIA", "VALOR", "STATUS"]
        pesos = [1, 3, 2, 2, 2]

        head = ctk.CTkFrame(scroll, fg_color=PALETA["elevado"], corner_radius=8)
        head.pack(fill="x", pady=(0, 4))
        for i, col in enumerate(cabecalho):
            ctk.CTkLabel(head, text=col, font=("Segoe UI Semibold", 10),
                         text_color=PALETA["texto_sub"]).grid(
                row=0, column=i, sticky="ew", padx=14, pady=12)
            head.grid_columnconfigure(i, weight=pesos[i])

        for i, (data, desc, cat, valor, tipo, status) in enumerate(
                self.banco.listar_transacoes(self.uid)):
            bg = PALETA["fundo"] if i % 2 == 0 else "#0F141A"
            linha = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=6)
            linha.pack(fill="x", pady=1)

            try:
                data_br = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m")
            except Exception:
                data_br = data

            ctk.CTkLabel(linha, text=data_br, font=FONTES["legenda"],
                         text_color=PALETA["texto_sub"]).grid(
                row=0, column=0, sticky="ew", padx=14, pady=10)
            ctk.CTkLabel(linha, text=desc, font=FONTES["corpo"],
                         text_color=PALETA["texto"], anchor="w").grid(
                row=0, column=1, sticky="ew", padx=14)
            ctk.CTkLabel(linha, text=cat, font=FONTES["legenda"],
                         text_color=PALETA["texto_sub"], anchor="w").grid(
                row=0, column=2, sticky="ew", padx=14)

            sinal = "+" if tipo == "entrada" else "−"
            cor_valor = PALETA["positivo"] if tipo == "entrada" else PALETA["negativo"]
            ctk.CTkLabel(linha, text=f"{sinal} {valor:,.2f}".replace(",", "X")
                                      .replace(".", ",").replace("X", "."),
                         font=FONTES["valor_p"], text_color=cor_valor,
                         anchor="e").grid(row=0, column=3, sticky="ew", padx=14)

            badge(linha, status, status if status in
                  ("sucesso", "alerta", "erro") else
                  {"pago": "sucesso", "pendente": "alerta",
                   "vencido": "erro"}.get(status, "neutro")
                  ).grid(row=0, column=4, sticky="ew", padx=14)

            for c, w in enumerate(pesos):
                linha.grid_columnconfigure(c, weight=w)

    # ---------- ABA METAS ----------
    def _aba_metas(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(wrap, text="METAS FINANCEIRAS", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w", pady=(0, 16))

        for titulo, atual, total, cor in self.banco.listar_metas(self.uid):
            box = ctk.CTkFrame(wrap, fg_color=PALETA["card"],
                               border_color=PALETA["borda"], border_width=1,
                               corner_radius=12)
            box.pack(fill="x", pady=6)
            progress_bar(box, f"🎯  {titulo}", atual, total, cor).pack(
                fill="x", padx=20, pady=16)

    # ---------- ABA NOVA ----------
    def _aba_nova(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(wrap, text="NOVA TRANSAÇÃO", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w", pady=(0, 16))

        form = ctk.CTkFrame(wrap, fg_color=PALETA["card"],
                            border_color=PALETA["borda"], border_width=1,
                            corner_radius=12)
        form.pack(fill="x")

        ctk.CTkLabel(form, text="DESCRIÇÃO", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(
            anchor="w", padx=24, pady=(24, 6))
        self.in_desc = input_estilizado(form, "Ex: Salário, Aluguel...")
        self.in_desc.pack(fill="x", padx=24)

        linha = ctk.CTkFrame(form, fg_color="transparent")
        linha.pack(fill="x", padx=24, pady=(16, 0))

        col_e = ctk.CTkFrame(linha, fg_color="transparent")
        col_e.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkLabel(col_e, text="VALOR (R$)", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w")
        self.in_valor = input_estilizado(col_e, "0,00")
        self.in_valor.pack(fill="x", pady=(6, 0))

        col_d = ctk.CTkFrame(linha, fg_color="transparent")
        col_d.pack(side="left", expand=True, fill="x", padx=(8, 0))
        ctk.CTkLabel(col_d, text="DATA (dd/mm/aaaa)", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w")
        self.in_data = input_estilizado(col_d, datetime.now().strftime("%d/%m/%Y"))
        self.in_data.pack(fill="x", pady=(6, 0))
        self.in_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        linha2 = ctk.CTkFrame(form, fg_color="transparent")
        linha2.pack(fill="x", padx=24, pady=(16, 0))

        col_c = ctk.CTkFrame(linha2, fg_color="transparent")
        col_c.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkLabel(col_c, text="CATEGORIA", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w")
        self.in_cat = ctk.CTkOptionMenu(
            col_c,
            values=["Renda", "Moradia", "Alimentação", "Transporte",
                    "Lazer", "Financeiro", "Outros"],
            fg_color=PALETA["fundo"], button_color=PALETA["elevado"],
            button_hover_color=PALETA["borda"], text_color=PALETA["texto"],
            dropdown_fg_color=PALETA["elevado"],
            dropdown_hover_color=PALETA["borda"],
            dropdown_text_color=PALETA["texto"],
            font=FONTES["corpo"], corner_radius=8, height=42)
        self.in_cat.pack(fill="x", pady=(6, 0))

        col_t = ctk.CTkFrame(linha2, fg_color="transparent")
        col_t.pack(side="left", expand=True, fill="x", padx=(8, 0))
        ctk.CTkLabel(col_t, text="TIPO", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w")
        self.in_tipo = ctk.CTkOptionMenu(
            col_t, values=["entrada", "saida"],
            fg_color=PALETA["fundo"], button_color=PALETA["elevado"],
            button_hover_color=PALETA["borda"], text_color=PALETA["texto"],
            dropdown_fg_color=PALETA["elevado"],
            dropdown_hover_color=PALETA["borda"],
            dropdown_text_color=PALETA["texto"],
            font=FONTES["corpo"], corner_radius=8, height=42)
        self.in_tipo.pack(fill="x", pady=(6, 0))

        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.pack(fill="x", padx=24, pady=24)
        botao_perigo(botoes, "Limpar", self._limpar_form).pack(side="right", padx=(8, 0))
        botao_primario(botoes, "💾  Salvar transação",
                       self._salvar).pack(side="right")

    def _limpar_form(self):
        for e in (self.in_desc, self.in_valor, self.in_data):
            e.delete(0, "end")
        self.in_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

    def _salvar(self):
        desc = self.in_desc.get().strip()
        valor_s = self.in_valor.get().strip().replace(".", "").replace(",", ".")
        data_s = self.in_data.get().strip()
        cat = self.in_cat.get()
        tipo = self.in_tipo.get()

        if not desc:
            messagebox.showwarning("Aviso", "Informe a descrição.")
            return
        try:
            valor = float(valor_s)
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Use 0,00")
            return
        try:
            data_iso = datetime.strptime(data_s, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use dd/mm/aaaa")
            return

        self.banco.adicionar_transacao(self.uid, data_iso, desc, cat, valor, tipo)
        messagebox.showinfo("Sucesso", "Transação salva com sucesso!")
        self._refresh()


# ============================================================
# 🚀 EXECUÇÃO
# ============================================================
if __name__ == "__main__":
    banco = Banco()
    TelaLogin(banco).mainloop()
