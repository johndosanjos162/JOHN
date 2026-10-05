import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Configuração inicial da página
st.set_page_config(
    page_title="Invest Control Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para blocos modernos e cards destacados
st.markdown("""
    <style>
        .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
        .sub-header { font-size: 1.1rem; color: #64748B; margin-bottom: 1.5rem; }
        .card-container {
            background-color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💼 Invest Control Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema Avançado de Gestão Financeira, Projeções e Controle de Portfólio</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# SIMULAÇÃO DE DADOS & ESTADO DA APLICAÇÃO (Supabase Ready)
# -------------------------------------------------------------
if 'transacoes' not in st.session_state:
    st.session_state['transacoes'] = pd.DataFrame([
        {"Data": "2026-10-01", "Tipo": "Receita", "Categoria": "Salário", "Valor": 8500.00, "Descrição": "Salário Líquido"},
        {"Data": "2026-10-03", "Tipo": "Despesa", "Categoria": "Moradia", "Valor": 2200.00, "Descrição": "Aluguel"},
        {"Data": "2026-10-04", "Tipo": "Despesa", "Categoria": "Alimentação", "Valor": 1200.00, "Descrição": "Supermercado"},
        {"Data": "2026-10-05", "Tipo": "Despesa", "Categoria": "Transporte", "Valor": 450.00, "Descrição": "Combustível"},
        {"Data": "2026-10-05", "Tipo": "Despesa", "Categoria": "Lazer", "Valor": 600.00, "Descrição": "Restaurantes e Passeios"},
        {"Data": "2026-10-05", "Tipo": "Despesa", "Categoria": "Saúde", "Valor": 300.00, "Descrição": "Farmácia e Convênio"}
    ])

df_trans = st.session_state['transacoes']
df_trans['Data'] = pd.to_datetime(df_trans['Data'])

# -------------------------------------------------------------
# MENU LATERAL EM BLOCOS (Navegação Limpa e Organizada)
# -------------------------------------------------------------
st.sidebar.markdown("### 🎛️ Navegação de Módulos")
menu_opcao = st.sidebar.radio(
    "Selecione a Funcionalidade:",
    [
        "📊 Dashboard Geral & Lançamentos",
        "📈 Projeção de Fluxo (12 Meses)",
        "🚨 Health Score & Alertas",
        "🏷️ Curva ABC de Gastos",
        "🔄 Simulador 'E Se...?'",
        "📑 Relatórios & Exportação"
    ]
)

receita_total = df_trans[df_trans['Tipo'] == 'Receita']['Valor'].sum()
despesa_total = df_trans[df_trans['Tipo'] == 'Despesa']['Valor'].sum()
saldo_atual = receita_total - despesa_total

# =============================================================
# MÓDULO 1: DASHBOARD GERAL & LANÇAMENTOS
# =============================================================
if menu_opcao == "📊 Dashboard Geral & Lançamentos":
    st.markdown("### 📊 Visão Geral do Mês Atual")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Receitas Totais", f"R$ {receita_total:,.2f}", delta="Estável")
    col2.metric("Despesas Totais", f"R$ {despesa_total:,.2f}", delta="-4% vs mês ant.", delta_color="inverse")
    col3.metric("Saldo Líquido", f"R$ {saldo_atual:,.2f}", delta=f"{(saldo_atual/receita_total)*100:.1f}% guardado" if receita_total > 0 else "0%")
    
    st.markdown("---")
    st.markdown("### ➕ Lançamento Rápido de Transações")
    with st.form("form_transacao", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            t_tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        with c2:
            t_cat = st.selectbox("Categoria", ["Salário", "Moradia", "Alimentação", "Transporte", "Lazer", "Saúde", "Investimentos", "Outros"])
        with c3:
            t_val = st.number_input("Valor (R$)", min_value=0.0, step=50.0)
        with c4:
            t_desc = st.text_input("Descrição")
            
        submitted = st.form_submit_button("Adicionar Transação")
        if submitted and t_val > 0:
            nova_linha = {"Data": pd.Timestamp.today().strftime('%Y-%m-%d'), "Tipo": t_tipo, "Categoria": t_cat, "Valor": t_val, "Descrição": t_desc}
            st.session_state['transacoes'] = pd.concat([df_trans, pd.DataFrame([nova_linha])], ignore_index=True)
            st.success("Transação adicionada com sucesso!")
            st.rerun()

# =============================================================
# MÓDULO 2: PROJEÇÃO DE FLUXO DE CAIXA (12 MESES)
# =============================================================
elif menu_opcao == "📈 Projeção de Fluxo (12 Meses)":
    st.markdown("### 📈 Projeção Preditiva de Fluxo de Caixa (Próximos 12 Meses)")
    st.markdown("Simulação baseada na sua média atual de receitas líquidas e despesas fixas/variáveis.")
    
    meses_futuros = pd.date_range(start=pd.Timestamp.today(), periods=12, freq='ME').strftime('%b/%Y')
    proj_receita = [receita_total] * 12
    proj_despesa = [despesa_total] * 12
    proj_saldo_acumulado = np.cumsum([r - d for r, d in zip(proj_receita, proj_despesa)]) + saldo_atual
    
    df_proj = pd.DataFrame({
        "Mês": meses_futuros,
        "Receita Projetada": proj_receita,
        "Despesa Projetada": proj_despesa,
        "Saldo Acumulado": proj_saldo_acumulado
    })
    
    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(x=df_proj["Mês"], y=df_proj["Receita Projetada"], name="Receitas", marker_color="#10B981"))
    fig_proj.add_trace(go.Bar(x=df_proj["Mês"], y=df_proj["Despesa Projetada"], name="Despesas", marker_color="#EF4444"))
    fig_proj.add_trace(go.Scatter(x=df_proj["Mês"], y=df_proj["Saldo Acumulado"], name="Patrimônio Acumulado", mode='lines+markers', line=dict(color="#3B82F6", width=3)))
    
    fig_proj.update_layout(barmode='group', template='plotly_white', height=450, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_proj, use_container_width=True)

# =============================================================
# MÓDULO 3: HEALTH SCORE & ALERTAS DINÂMICOS
# =============================================================
elif menu_opcao == "🚨 Health Score & Alertas":
    st.markdown("### 🚨 Painel de Saúde Financeira & Indicadores")
    
    taxa_poupanca = (saldo_atual / receita_total) * 100 if receita_total > 0 else 0
    gasto_fixo_pct = (df_trans[df_trans['Categoria'].isin(['Moradia', 'Saúde'])]['Valor'].sum() / receita_total) * 100 if receita_total > 0 else 0
    
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.metric("Taxa de Poupança Atual", f"{taxa_poupanca:.1f}%", delta="Ideal: > 20%")
        if taxa_poupanca >= 20: st.success("🟢 Excelente capacidade de investimento.")
        else: st.warning("⚠️ Abaixo do recomendado para expansão de patrimônio.")
            
    with col_h2:
        st.metric("Comprometimento com Fixos", f"{gasto_fixo_pct:.1f}%", delta="Ideal: < 50%")
        if gasto_fixo_pct <= 50: st.success("🟢 Estrutura de custos enxuta.")
        else: st.error("🔴 Custos fixos elevados comprometem a flexibilidade.")
            
    with col_h3:
        status_geral = "Saudável 🛡️️" if taxa_poupanca >= 15 and gasto_fixo_pct <= 60 else "Requer Atenção ⚠️"
        st.metric("Health Score Geral", status_geral)
        st.info("Indicador calculado com base nas normativas de equilíbrio orçamentário.")

# =============================================================
# MÓDULO 4: CURVA ABC DE GASTOS
# =============================================================
elif menu_opcao == "🏷️ Curva ABC de Gastos":
    st.markdown("### 🏷️ Análise de Curva ABC & Distribuição de Despesas")
    st.markdown("Identifique rapidamente quais categorias concentram o maior volume do seu orçamento.")
    
    df_despesas = df_trans[df_trans['Tipo'] == 'Despesa'].groupby('Categoria')['Valor'].sum().reset_index()
    df_despesas = df_despesas.sort_values(by='Valor', ascending=False)
    
    if not df_despesas.empty:
        fig_pareto = px.bar(df_despesas, x='Categoria', y='Valor', text='Valor', title="Maiores Centros de Custo", color='Valor', color_continuous_scale='Blues')
        fig_pareto.update_traces(texttemplate='R$ %{text:.2f}', textposition='outside')
        fig_pareto.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig_pareto, use_container_width=True)
    else:
        st.info("Nenhuma despesa registrada no período para análise.")

# =============================================================
# MÓDULO 5: SIMULADOR DE CENÁRIOS
# =============================================================
elif menu_opcao == "🔄 Simulador 'E Se...?'":
    st.markdown("### 🔄 Simulador Dinâmico de Cenários")
    st.markdown("Teste variações hipotéticas de ganhos e corte de gastos sem alterar os dados oficiais do banco.")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sim_aumento_salario = st.slider("Variação Percentual na Receita (%)", -20, 50, 0)
        sim_corte_gastos = st.slider("Corte nos Gastos Variáveis (%)", 0, 50, 0)
    
    with col_s2:
        nova_receita = receita_total * (1 + sim_aumento_salario / 100)
        nova_despesa = despesa_total * (1 - sim_corte_gastos / 100)
        novo_saldo = nova_receita - nova_despesa
        
        st.markdown("### Resultado da Simulação:")
        st.markdown(f"**Nova Receita:** R$ {nova_receita:,.2f}")
        st.markdown(f"**Nova Despesa:** R$ {nova_despesa:,.2f}")
        st.markdown(f"**Novo Saldo Mensal:** <span style='color:green; font-size:1.2rem; font-weight:bold;'>R$ {novo_saldo:,.2f}</span>", unsafe_allow_html=True)

# =============================================================
# MÓDULO 6: RELATÓRIOS & EXPORTAÇÃO
# =============================================================
elif menu_opcao == "📑 Relatórios & Exportação":
    st.markdown("### 📑 Central de Relatórios e Exportação")
    st.markdown("Gere relatórios consolidados do seu fluxo financeiro para auditoria e arquivos pessoais.")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("#### Exportar Dados em Excel (.xlsx)")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_trans.to_excel(writer, index=False, sheet_name='Transacoes')
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Baixar Relatório em Excel",
            data=excel_data,
            file_name="Invest_Control_Pro_Relatorio.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    with col_e2:
        st.markdown("#### Resumo Executivo em Texto / Markdown")
        resumo_texto = f"""# RELATÓRIO FINANCEIRO - INVEST CONTROL PRO
Data de Emissão: {pd.Timestamp.today().strftime('%d/%m/%Y')}
- Receitas Totais: R$ {receita_total:,.2f}
- Despesas Totais: R$ {despesa_total:,.2f}
- Saldo Líquido: R$ {saldo_atual:,.2f}
"""
        st.text_area("Pré-visualização do Relatório", resumo_texto, height=150)
