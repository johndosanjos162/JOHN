# ============================================================
#  💰 FINANCE PRO — Design de Ponta (Visual apenas)
#  Biblioteca: CustomTkinter
#  Este arquivo é 100% VISUAL. Nenhuma lógica de negócio aqui.
# ============================================================

import customtkinter as ctk
from tkinter import ttk
import tkinter as tk

# ------------------------------------------------------------
# 🎨 TEMA GLOBAL  [VISUAL]
# ------------------------------------------------------------
PALETA = {
    "fundo":         "#0B0F14",
    "sidebar":       "#0F141A",
    "card":          "#151B23",
    "elevado":       "#1C242E",
    "borda":         "#232B36",
    "texto":         "#E8EEF5",
    "texto_sub":     "#8A95A5",
    "texto_fraco":   "#4A5563",
    "positivo":      "#22C55E",
    "positivo_bg":   "#0F2A1A",
    "negativo":      "#EF4444",
    "negativo_bg":   "#2A0F12",
    "alerta":        "#F59E0B",
    "alerta_bg":     "#2A1F0A",
    "acento":        "#3B82F6",
    "acento_hover":  "#2563EB",
    "roxo":          "#7C3AED",
    "ciano":         "#06B6D4",
}

FONTES = {
    "logo":       ("Segoe UI Semibold", 22),
    "titulo":     ("Segoe UI Semibold", 16),
    "subtitulo":  ("Segoe UI", 13),
    "corpo":      ("Segoe UI", 12),
    "label":      ("Segoe UI", 11),
    "legenda":    ("Segoe UI", 10),
    "valor_g":    ("Consolas", 28, "bold"),
    "valor_m":    ("Consolas", 18, "bold"),
    "valor_p":    ("Consolas", 12),
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


# ============================================================
# 🧩 COMPONENTES REUTILIZÁVEIS  [VISUAL]
# ============================================================

def card_metrica(parent, titulo, valor, delta, cor_delta, icone="💵"):
    """Card de métrica estilizado."""
    card = ctk.CTkFrame(
        parent, fg_color=PALETA["card"],
        border_color=PALETA["borda"], border_width=1,
        corner_radius=14,
    )
    topo = ctk.CTkFrame(card, fg_color="transparent")
    topo.pack(fill="x", padx=20, pady=(18, 4))

    ctk.CTkLabel(
        topo, text=f"{icone}  {titulo.upper()}",
        font=FONTES["label"], text_color=PALETA["texto_sub"],
    ).pack(side="left")

    ctk.CTkLabel(
        card, text=valor,
        font=FONTES["valor_g"], text_color=PALETA["texto"],
    ).pack(anchor="w", padx=20)

    ctk.CTkLabel(
        card, text=delta,
        font=FONTES["legenda"], text_color=cor_delta,
    ).pack(anchor="w", padx=20, pady=(0, 18))

    return card


def botao_primario(parent, texto, comando=None, **kw):
    return ctk.CTkButton(
        parent, text=texto, command=comando,
        fg_color=PALETA["acento"], hover_color=PALETA["acento_hover"],
        text_color="#FFFFFF", font=("Segoe UI Semibold", 12),
        corner_radius=8, height=40, **kw,
    )


def botao_secundario(parent, texto, comando=None, **kw):
    return ctk.CTkButton(
        parent, text=texto, command=comando,
        fg_color=PALETA["elevado"], hover_color=PALETA["borda"],
        text_color=PALETA["texto"], border_color=PALETA["borda"],
        border_width=1, font=("Segoe UI", 12),
        corner_radius=8, height=36, **kw,
    )


def botao_perigo(parent, texto, comando=None, **kw):
    return ctk.CTkButton(
        parent, text=texto, command=comando,
        fg_color=PALETA["negativo"], hover_color="#DC2626",
        text_color="#FFFFFF", font=("Segoe UI Semibold", 12),
        corner_radius=8, height=40, **kw,
    )


def input_estilizado(parent, placeholder="", senha=False):
    entry = ctk.CTkEntry(
        parent, placeholder_text=placeholder,
        fg_color=PALETA["fundo"], border_color=PALETA["borda"],
        border_width=1, text_color=PALETA["texto"],
        placeholder_text_color=PALETA["texto_fraco"],
        font=FONTES["corpo"], corner_radius=8, height=42,
        show="•" if senha else "",
    )
    # Foco: borda azul
    entry.bind("<FocusIn>",  lambda e: entry.configure(border_color=PALETA["acento"]))
    entry.bind("<FocusOut>", lambda e: entry.configure(border_color=PALETA["borda"]))
    return entry


def progress_bar(parent, titulo, valor_atual, valor_total, cor=PALETA["acento"]):
    """Progress bar com título, valores e porcentagem."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    topo = ctk.CTkFrame(frame, fg_color="transparent")
    topo.pack(fill="x")

    ctk.CTkLabel(
        topo, text=titulo, font=FONTES["label"],
        text_color=PALETA["texto_sub"],
    ).pack(side="left")

    pct = int((valor_atual / valor_total) * 100) if valor_total else 0
    ctk.CTkLabel(
        topo, text=f"R$ {valor_atual:,.0f} / R$ {valor_total:,.0f}".replace(",", "."),
        font=FONTES["legenda"], text_color=PALETA["texto"],
    ).pack(side="right")

    barra = ctk.CTkProgressBar(
        frame, progress_color=cor, fg_color=PALETA["elevado"],
        corner_radius=999, height=10,
    )
    barra.pack(fill="x", pady=(8, 2))
    barra.set(valor_atual / valor_total if valor_total else 0)

    ctk.CTkLabel(
        frame, text=f"{pct}%", font=FONTES["legenda"],
        text_color=PALETA["texto_sub"],
    ).pack(anchor="e")

    return frame


def badge(parent, texto, tipo="sucesso"):
    cores = {
        "sucesso": (PALETA["positivo_bg"], PALETA["positivo"], "●"),
        "alerta":  (PALETA["alerta_bg"],   PALETA["alerta"],   "⏳"),
        "erro":    (PALETA["negativo_bg"], PALETA["negativo"], "⚠"),
        "neutro":  (PALETA["elevado"],     PALETA["texto_sub"],"○"),
    }
    bg, fg, ico = cores[tipo]
    return ctk.CTkLabel(
        parent, text=f"  {ico}  {texto}  ",
        fg_color=bg, text_color=fg,
        corner_radius=999, font=("Segoe UI", 10),
    )


# ============================================================
# 🔐 TELA DE LOGIN  [VISUAL]
# ============================================================

class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Pro — Login")
        self.geometry("1100x700")
        self.configure(fg_color=PALETA["fundo"])
        self._centralizar(1100, 700)
        self._construir()

    def _centralizar(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _construir(self):
        # Container central
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        ctk.CTkLabel(
            container, text="💰  FINANCE PRO",
            font=FONTES["logo"], text_color=PALETA["texto"],
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            container, text="Controle seus salários e rendas com precisão",
            font=FONTES["subtitulo"], text_color=PALETA["texto_sub"],
        ).pack(pady=(0, 28))

        # Card do formulário
        card = ctk.CTkFrame(
            container, fg_color=PALETA["card"],
            border_color=PALETA["borda"], border_width=1,
            corner_radius=16, width=420, height=420,
        )
        card.pack()
        card.pack_propagate(False)

        # E-mail
        ctk.CTkLabel(
            card, text="E-MAIL OU USUÁRIO", font=FONTES["label"],
            text_color=PALETA["texto_sub"],
        ).pack(anchor="w", padx=36, pady=(36, 6))

        self.entry_email = input_estilizado(card, "seu@email.com")
        self.entry_email.pack(fill="x", padx=36)

        # Senha
        ctk.CTkLabel(
            card, text="SENHA", font=FONTES["label"],
            text_color=PALETA["texto_sub"],
        ).pack(anchor="w", padx=36, pady=(18, 6))

        self.entry_senha = input_estilizado(card, "••••••••", senha=True)
        self.entry_senha.pack(fill="x", padx=36)

        # Lembrar / Esqueci
        linha = ctk.CTkFrame(card, fg_color="transparent")
        linha.pack(fill="x", padx=36, pady=(14, 0))

        ctk.CTkCheckBox(
            linha, text="Lembrar-me",
            font=FONTES["legenda"], text_color=PALETA["texto_sub"],
            fg_color=PALETA["acento"], hover_color=PALETA["acento_hover"],
            border_color=PALETA["borda"], corner_radius=4,
            checkbox_width=16, checkbox_height=16,
        ).pack(side="left")

        ctk.CTkLabel(
            linha, text="Esqueci a senha",
            font=FONTES["legenda"], text_color=PALETA["acento"],
            cursor="hand2",
        ).pack(side="right")

        # Botão entrar
        botao_primario(card, "ENTRAR", self._login).pack(
            fill="x", padx=36, pady=(24, 8)
        )

        ctk.CTkLabel(
            card, text="Não tem conta?  Criar agora →",
            font=FONTES["legenda"], text_color=PALETA["texto_sub"],
            cursor="hand2",
        ).pack(pady=(0, 36))

        # Rodapé
        ctk.CTkLabel(
            container, text="v1.0.0  •  © 2026 Finance Pro",
            font=FONTES["legenda"], text_color=PALETA["texto_fraco"],
        ).pack(pady=(20, 0))

    # ⚠️ AQUI você plugaria sua lógica real de autenticação
    def _login(self):
        self.destroy()
        AppPrincipal().mainloop()


# ============================================================
# 📊 APP PRINCIPAL  [VISUAL]
# ============================================================

class AppPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Pro")
        self.geometry("1300x780")
        self.configure(fg_color=PALETA["fundo"])
        self._centralizar(1300, 780)
        self._construir()

    def _centralizar(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _construir(self):
        # ---------- SIDEBAR ----------
        sidebar = ctk.CTkFrame(
            self, fg_color=PALETA["sidebar"],
            corner_radius=0, width=230,
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar, text="💰  FINANCE",
            font=FONTES["logo"], text_color=PALETA["texto"],
        ).pack(anchor="w", padx=24, pady=(28, 32))

        itens = [
            ("📊  Dashboard",     True),
            ("💼  Salários",      False),
            ("📈  Rendas",        False),
            ("💸  Despesas",      False),
            ("📋  DRE",           False),
            ("🎯  Metas",         False),
            ("⚙️  Configurações", False),
        ]
        for texto, ativo in itens:
            self._item_sidebar(sidebar, texto, ativo)

        # Rodapé sidebar
        rodape = ctk.CTkFrame(sidebar, fg_color="transparent")
        rodape.pack(side="bottom", fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            rodape, text="● conectado",
            font=FONTES["legenda"], text_color=PALETA["positivo"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            rodape, text="v1.0.0",
            font=FONTES["legenda"], text_color=PALETA["texto_fraco"],
        ).pack(anchor="w")

        # ---------- ÁREA PRINCIPAL ----------
        area = ctk.CTkFrame(self, fg_color="transparent")
        area.pack(side="left", fill="both", expand=True, padx=24, pady=20)

        # Topbar
        topbar = ctk.CTkFrame(area, fg_color="transparent")
        topbar.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            topbar, text="Dashboard",
            font=("Segoe UI Semibold", 24), text_color=PALETA["texto"],
        ).pack(side="left")

        ctk.CTkLabel(
            topbar, text="outubro 2026  •  bem-vindo de volta",
            font=FONTES["legenda"], text_color=PALETA["texto_sub"],
        ).pack(side="left", padx=(16, 0), pady=(10, 0))

        botao_secundario(topbar, "＋  Nova transação").pack(side="right")

        # ---------- CARDS DE MÉTRICA ----------
        linha_cards = ctk.CTkFrame(area, fg_color="transparent")
        linha_cards.pack(fill="x", pady=(0, 20))

        card_metrica(
            linha_cards, "Entradas do mês", "R$ 6.200,00",
            "▲ +5,2% vs mês anterior", PALETA["positivo"], "💵",
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        card_metrica(
            linha_cards, "Saídas do mês", "R$ 3.079,55",
            "▼ -2,1% vs mês anterior", PALETA["negativo"], "💸",
        ).pack(side="left", expand=True, fill="x", padx=8)

        card_metrica(
            linha_cards, "Saldo atual", "R$ 3.120,45",
            "▲ +18% vs mês anterior", PALETA["positivo"], "🏦",
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

        # ---------- ABAS ----------
        abas = ctk.CTkTabview(
            area, fg_color=PALETA["card"],
            segmented_button_fg_color=PALETA["elevado"],
            segmented_button_selected_color=PALETA["acento"],
            segmented_button_selected_hover_color=PALETA["acento_hover"],
            segmented_button_unselected_color=PALETA["elevado"],
            segmented_button_unselected_hover_color=PALETA["borda"],
            text_color=PALETA["texto"],
            border_color=PALETA["borda"], border_width=1,
            corner_radius=14,
        )
        abas.pack(fill="both", expand=True)

        aba_dre   = abas.add("📋  DRE")
        aba_meta  = abas.add("🎯  Metas")
        aba_input = abas.add("＋  Nova")

        self._aba_dre(aba_dre)
        self._aba_metas(aba_meta)
        self._aba_nova(aba_input)

    # ---------- ITEM SIDEBAR [VISUAL] ----------
    def _item_sidebar(self, parent, texto, ativo):
        bg = PALETA["elevado"] if ativo else "transparent"
        fg = PALETA["acento"]  if ativo else PALETA["texto_sub"]
        lbl = ctk.CTkLabel(
            parent, text=texto, font=FONTES["corpo"],
            text_color=fg, fg_color=bg,
            anchor="w", height=40, corner_radius=8,
        )
        lbl.pack(fill="x", padx=14, pady=2)

    # ---------- ABA DRE [VISUAL] ----------
    def _aba_dre(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            wrap, text="DEMONSTRATIVO DE RESULTADO (DRE)",
            font=FONTES["label"], text_color=PALETA["texto_sub"],
        ).pack(anchor="w", pady=(0, 12))

        # Container da tabela com scrollbar customizada
        tabela_wrap = ctk.CTkFrame(
            wrap, fg_color=PALETA["fundo"],
            border_color=PALETA["borda"], border_width=1,
            corner_radius=12,
        )
        tabela_wrap.pack(fill="both", expand=True)

        # Scrollbar customizada (CustomTkinter)
        scroll = ctk.CTkScrollableFrame(
            tabela_wrap, fg_color=PALETA["fundo"],
            scrollbar_button_color=PALETA["borda"],
            scrollbar_button_hover_color=PALETA["acento"],
            corner_radius=12,
        )
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        # Cabeçalho
        cabecalho = ["DATA", "DESCRIÇÃO", "CATEGORIA", "VALOR", "STATUS"]
        larguras = [1, 3, 2, 2, 2]

        head = ctk.CTkFrame(scroll, fg_color=PALETA["elevado"], corner_radius=8)
        head.pack(fill="x", pady=(0, 4))
        for i, col in enumerate(cabecalho):
            ctk.CTkLabel(
                head, text=col, font=("Segoe UI Semibold", 10),
                text_color=PALETA["texto_sub"],
            ).grid(row=0, column=i, sticky="ew",
                   padx=14, pady=12)
            head.grid_columnconfigure(i, weight=larguras[i])

        # Dados de exemplo
        dados = [
            ("05/10", "Salário mensal",  "Renda",    "+ 5.400,00", "sucesso"),
            ("07/10", "Aluguel",         "Moradia",  "− 1.200,00", "sucesso"),
            ("10/10", "Energia elétrica","Casa",     "−   180,00", "alerta"),
            ("12/10", "Freelance UI",    "Renda",    "+   800,00", "sucesso"),
            ("15/10", "Supermercado",    "Alimentação","−  620,00","sucesso"),
            ("18/10", "Internet",        "Casa",     "−   120,00", "sucesso"),
            ("20/10", "Cartão crédito",  "Financeiro","−  959,55", "erro"),
            ("22/10", "Investimento",    "Aporte",   "→   500,00", "neutro"),
        ]

        for i, (data, desc, cat, valor, tipo) in enumerate(dados):
            linha_bg = PALETA["fundo"] if i % 2 == 0 else "#0F141A"
            linha = ctk.CTkFrame(scroll, fg_color=linha_bg, corner_radius=6)
            linha.pack(fill="x", pady=1)

            ctk.CTkLabel(linha, text=data, font=FONTES["legenda"],
                         text_color=PALETA["texto_sub"]).grid(row=0, column=0, sticky="ew", padx=14, pady=10)
            ctk.CTkLabel(linha, text=desc, font=FONTES["corpo"],
                         text_color=PALETA["texto"], anchor="w").grid(row=0, column=1, sticky="ew", padx=14)
            ctk.CTkLabel(linha, text=cat, font=FONTES["legenda"],
                         text_color=PALETA["texto_sub"], anchor="w").grid(row=0, column=2, sticky="ew", padx=14)

            cor_valor = PALETA["positivo"] if "+" in valor else (
                PALETA["negativo"] if "−" in valor else PALETA["texto_sub"]
            )
            ctk.CTkLabel(linha, text=valor, font=FONTES["valor_p"],
                         text_color=cor_valor, anchor="e").grid(row=0, column=3, sticky="ew", padx=14)

            badge(linha, {"sucesso":"pago","alerta":"pendente",
                          "erro":"vencido","neutro":"agendado"}[tipo], tipo
            ).grid(row=0, column=4, sticky="ew", padx=14)

            for c, w in enumerate(larguras):
                linha.grid_columnconfigure(c, weight=w)

    # ---------- ABA METAS [VISUAL] ----------
    def _aba_metas(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            wrap, text="METAS FINANCEIRAS",
            font=FONTES["label"], text_color=PALETA["texto_sub"],
        ).pack(anchor="w", pady=(0, 16))

        metas = [
            ("🎯  Reserva de emergência", 3400, 5000, PALETA["acento"]),
            ("✈️  Viagem de férias",      1800, 5000, PALETA["ciano"]),
            ("🏠  Entrada do apartamento", 12000, 30000, PALETA["roxo"]),
            ("🚗  Troca do carro",         800, 15000, PALETA["alerta"]),
        ]

        for titulo, atual, total, cor in metas:
            box = ctk.CTkFrame(
                wrap, fg_color=PALETA["card"],
                border_color=PALETA["borda"], border_width=1,
                corner_radius=12,
            )
            box.pack(fill="x", pady=6)
            progress_bar(box, titulo, atual, total, cor).pack(
                fill="x", padx=20, pady=16
            )

    # ---------- ABA NOVA [VISUAL] ----------
    def _aba_nova(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            wrap, text="NOVA TRANSAÇÃO",
            font=FONTES["label"], text_color=PALETA["texto_sub"],
        ).pack(anchor="w", pady=(0, 16))

        form = ctk.CTkFrame(
            wrap, fg_color=PALETA["card"],
            border_color=PALETA["borda"], border_width=1,
            corner_radius=12,
        )
        form.pack(fill="x")

        # Descrição
        ctk.CTkLabel(form, text="DESCRIÇÃO", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(
            anchor="w", padx=24, pady=(24, 6))
        input_estilizado(form, "Ex: Salário, Aluguel...").pack(
            fill="x", padx=24)

        # Valor + Data lado a lado
        linha = ctk.CTkFrame(form, fg_color="transparent")
        linha.pack(fill="x", padx=24, pady=(16, 0))

        col_esq = ctk.CTkFrame(linha, fg_color="transparent")
        col_esq.pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkLabel(col_esq, text="VALOR (R$)", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w")
        input_estilizado(col_esq, "0,00").pack(fill="x", pady=(6, 0))

        col_dir = ctk.CTkFrame(linha, fg_color="transparent")
        col_dir.pack(side="left", expand=True, fill="x", padx=(8, 0))
        ctk.CTkLabel(col_dir, text="DATA", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(anchor="w")
        input_estilizado(col_dir, "dd/mm/aaaa").pack(fill="x", pady=(6, 0))

        # Categoria
        ctk.CTkLabel(form, text="CATEGORIA", font=FONTES["label"],
                     text_color=PALETA["texto_sub"]).pack(
            anchor="w", padx=24, pady=(16, 6))
        ctk.CTkOptionMenu(
            form, values=["Renda", "Moradia", "Alimentação", "Transporte",
                          "Lazer", "Financeiro", "Outros"],
            fg_color=PALETA["fundo"], button_color=PALETA["elevado"],
            button_hover_color=PALETA["borda"], text_color=PALETA["texto"],
            dropdown_fg_color=PALETA["elevado"],
            dropdown_hover_color=PALETA["borda"],
            dropdown_text_color=PALETA["texto"],
            font=FONTES["corpo"], corner_radius=8, height=42,
        ).pack(fill="x", padx=24)

        # Botões
        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.pack(fill="x", padx=24, pady=24)
        botao_perigo(botoes, "Cancelar").pack(side="right", padx=(8, 0))
        botao_primario(botoes, "💾  Salvar transação").pack(side="right")


# ============================================================
# 🚀 EXECUÇÃO
# ============================================================
if __name__ == "__main__":
    TelaLogin().mainloop()
