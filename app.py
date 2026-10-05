import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client

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
# ESTILIZAÇÃO CSS CUSTOMIZADA (TELA DE LOGIN E DESIGN PREMIUM)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .login-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        color: #f8fafc;
        border: 1px solid #334155;
    }
    .login-title {
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 10px;
        text-align: center;
    }
    .login-subtitle {
        font-size: 14px;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONTROLE DE SESSÃO DE AUTENTICAÇÃO
# -----------------------------------------------------------------------------
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Inicialização do estado dos 12 meses da meta de reserva (Chaves booleanas)
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
# TELA DE LOGIN COM PROJEÇÃO ECONÔMICA (EXCLUSIVAMENTE CREDENCIAIS)
# -----------------------------------------------------------------------------
if not st.session_state['autenticado']:
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    
    with col_l2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="login-title">🛡️ INVEST CONTROL PRO</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sistema Integrado de Projeção Econômica & Acesso Seguro</div>', unsafe_allow_html=True)
        
        with st.form("form_login"):
            st.markdown("### Credenciais de Acesso")
            usuario = st.text_input("Usuário / Credencial", placeholder="Digite seu usuário...")
            senha = st.text_input("Senha de Acesso", type="password", placeholder="Digite sua senha...")
            
            st.markdown("---")
            btn_entrar = st.form_submit_button("Acessar Sistema", use_container_width=True)
            
            if btn_entrar:
                # Validação de credenciais estritas
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
        "meta_reserva_mensal": 800.0
    }

def salvar_configuracoes(aluguel, salario_a, salario_b, vr_a, meta_reserva):
    if supabase:
        try:
            supabase.table("configuracoes").update({
                "aluguel_total": aluguel,
                "salario_a": salario_a,
                "salario_b": salario_b,
                "vr_a": vr_a,
                "meta_reserva_mensal": meta_reserva
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

# Opção de edição manual interativa do aluguel
st.sidebar.divider()
st.sidebar.subheader("✏ Edição Dinâmica do Aluguel")
edicao_manual = st.sidebar.checkbox("Habilitar edição manual customizada", value=False)

aluguel_a_input = None
aluguel_b_input = None

if edicao_manual and b_participa:
    quem_edita = st.sidebar.radio("Quem você deseja ajustar?", options=["Pessoa A", "Pessoa B"], index=0)
    
    if quem_edita == "Pessoa A":
        aluguel_a_input = st.sidebar.number_input(
            "Valor pago por A (R$)", 
            min_value=0.0, 
            max_value=float(aluguel_input), 
            value=float(aluguel_input * 0.5), 
            step=25.0
        )
        aluguel_b_input = max(0.0, aluguel_input - aluguel_a_input)
        st.sidebar.info(f"💡 Valor de B ajustado automaticamente: **R$ {aluguel_b_input:,.2f}**")
    else:
        aluguel_b_input = st.sidebar.number_input(
            "Valor pago por B (R$)", 
            min_value=0.0, 
            max_value=float(aluguel_input), 
            value=float(aluguel_input * 0.5), 
            step=25.0
        )
        aluguel_a_input = max(0.0, aluguel_input - aluguel_b_input)
        st.sidebar.info(f"💡 Valor de A ajustado automaticamente: **R$ {aluguel_a_input:,.2f}**")

if st.sidebar.button("💾 Salvar Parâmetros"):
    salvar_configuracoes(aluguel_input, salario_a_input, salario_b_input, vr_a_input, meta_reserva_input)
    st.sidebar.success("Parâmetros atualizados!")
    st.rerun()

# --- NOVO RECURSO: EXPORTAÇÃO RÁPIDA DE DADOS NA SIDEBAR ---
st.sidebar.divider()
st.sidebar.subheader("📥 Exportação de Dados")
df_vars_export = carregar_despesas_variaveis()
if not df_vars_export.empty:
    csv_data = df_vars_export.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📄 Baixar Despesas (CSV)",
        data=csv_data,
        file_name=f"despesas_invest_control_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# ENGINE DE CÁLCULO FINANCEIRO E PROPORÇÃO DINÂMICA
# -----------------------------------------------------------------------------
if b_participa:
    if edicao_manual and aluguel_a_input is not None and aluguel_b_input is not None:
        aluguel_a = aluguel_a_input
        aluguel_b = aluguel_b_input
        if aluguel_input > 0:
            prop_a = aluguel_a / aluguel_input
            prop_b = aluguel_b / aluguel_input
        else:
            prop_a, prop_b = 0.5, 0.5
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
st.caption(f"Cenário Ativo: **{cenario}** | Alimentação protegida com VR de R$ {vr_a_input:.2f}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Líquido (A)", f"R$ {salario_a_input:,.2f}")
col2.metric("Sua Parte no Aluguel", f"R$ {aluguel_a:,.2f}", delta=f"{prop_a*100:.1f}% do aluguel" if b_participa else "100% (Integral)")
col3.metric("Total Gastos Fixos (A)", f"R$ {total_fixos_a:,.2f}")
col4.metric("Aporte Reserva Mensal", f"R$ {meta_reserva_efetiva:,.2f}")

st.divider()

# --- ADIÇÃO DA NOVA ABA DE SIMULAÇÃO DE INVESTIMENTOS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📌 Planejamento & Cenários", 
    "💳 Controle de Gastos Diários", 
    "⚙ Gerenciar Custos Fixos", 
    "📈 Simulador de Investimentos"
])

with tab1:
    st.subheader("🏠 Divisão e Proporcionalidade do Aluguel (A e B)")
    col_div1, col_div2, col_div3 = st.columns(3)
    col_div1.metric("Salário de A", f"R$ {salario_a_input:,.2f}")
    col_div2.metric("Salário de B", f"R$ {salario_b_input:,.2f}" if b_participa else "R$ 0,00")
    col_div3.metric("Aluguel Total", f"R$ {aluguel_input:,.2f}")

    col_val1, col_val2 = st.columns(2)
    col_val1.info(f"👤 **Pessoa A vai pagar:** R$ **{aluguel_a:,.2f}** ({prop_a*100:.1f}% do valor total do aluguel)")
    if b_participa:
        col_val2.success(f"👥 **Pessoa B vai pagar:** R$ **{aluguel_b:,.2f}** ({prop_b*100:.1f}% do valor total do aluguel)")
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
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("🛡 Progresso Anual da Reserva de Emergência (12 Meses)")
        meta_6_meses = total_fixos_a * 6
        st.write(f"**Aporte Mensal Previsto:** R$ {meta_reserva_efetiva:,.2f}")
        st.write(f"**Meta Anual Acumulada (12 Meses de Aporte):** R$ {meta_reserva_efetiva * 12:,.2f}")
        
        st.markdown("##### 🗓️ Clique nos meses concluídos:")
        
        cols_grid = st.columns(4)
        meses_concluidos_count = 0
        
        for i, nome_mes in enumerate(meses_nomes):
            col_idx = i % 4
            with cols_grid[col_idx]:
                key_nome = f"reserva_mes_{i+1}"
                status = st.checkbox(f"{i+1}. {nome_mes}", key=key_nome)
                if status:
                    meses_concluidos_count += 1
                    
        pct_concluido = meses_concluidos_count / 12.0
        montante_acumulado_real = meta_reserva_efetiva * meses_concluidos_count
        
        st.markdown("---")
        st.progress(pct_concluido)
        st.markdown(f"**Progresso Anual:** {meses_concluidos_count} de 12 meses concluídos (**{pct_concluido * 100:.1f}%**)")
        st.write(f"Montante total depositado e confirmado: **R$ {montante_acumulado_real:,.2f}**")
        
        if not b_participa:
            st.warning("⚠️ **Atenção no Cenário Contingência:** Como você está assumindo o aluguel sozinho, o aporte foi reajustado para proteger seu caixa.")

with tab2:
    st.subheader("🛒 Gerenciamento de Despesas Variáveis do Mês")
    col_lim1, col_lim2, col_lim3 = st.columns(3)
    col_lim1.metric("Orçamento Variável Disponível", f"R$ {saldo_para_variaveis:,.2f}")
    col_lim2.metric("Total Já Gasto no Mês", f"R$ {total_gastos_variaveis:,.2f}")
    col_lim3.metric("Saldo do Caixa Restante", f"R$ {saldo_caixa_restante:,.2f}", delta_color="normal" if saldo_caixa_restante >= 0 else "inverse")
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
    
    # --- NOVO RECURSO: ANÁLISE DE GASTOS POR CATEGORIA (GRÁFICO) ---
    if not df_variaveis.empty:
        st.markdown("---")
        st.markdown("##### 📊 Gastos Variáveis por Categoria")
        df_cat = df_variaveis.groupby("categoria")["valor"].sum().reset_index()
        fig_cat = px.bar(df_cat, x="categoria", y="valor", text_auto=".2f", color="categoria", title="Distribuição de Despesas por Categoria")
        fig_cat.update_layout(showlegend=False, xaxis_title="Categoria", yaxis_title="Valor Gasto (R$)")
        st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown("---")

    if not df_variaveis.empty:
        for idx, row in df_variaveis.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1])
            c1.write(row["data"].strftime("%d/%m/%Y"))
            c2.write(row["descricao"])
            c3.write(row["categoria"])
            c4.write(f"R$ {row['valor']:,.2f}")
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
                cf2.write(f"R$ {row['valor']:,.2f}")
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

# --- NOVO RECURSO: ABA DE SIMULADOR DE JUROS COMPOSTOS E PATRIMÔNIO ---
with tab4:
    st.subheader("📈 Simulador de Crescimento Patrimonial (Juros Compostos)")
    st.caption("Projete o acúmulo da sua reserva de emergência e investimentos ao longo dos anos com base no aporte mensal.")

    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        aporte_sim = st.number_input("Aporte Mensal Utilizado (R$)", value=float(meta_reserva_efetiva), step=50.0)
        anos_sim = st.slider("Horizonte de Tempo (Anos)", min_value=1, max_value=30, value=5)
    with col_sim2:
        taxa_anual_sim = st.slider("Rentabilidade Anual Estimada (%)", min_value=1.0, max_value=20.0, value=10.0, step=0.5)

    # Cálculo dos juros compostos mês a mês
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
        col_res1.metric("Valor Total Acumulado", f"R$ {montante_atual:,.2f}")
        col_res2.metric("Total do Seu Bolso (Aporte)", f"R$ {total_investido:,.2f}")
        col_res3.metric("Rendimento (Juros)", f"R$ {(montante_atual - total_investido):,.2f}")

        st.divider()

        fig_invest = px.area(
            df_proj, 
            x="Ano", 
            y=["Patrimônio Total", "Total Investido"],
            labels={"value": "Valor em Reais (R$)", "variable": "Legenda"},
            title="Evolução Patrimonial Projetada"
        )
        st.plotly_chart(fig_invest, use_container_width=True)
