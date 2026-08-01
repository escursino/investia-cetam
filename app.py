import sys
import subprocess

# Lista de dependências necessárias para o InvestIA
packages = ["yfinance", "pandas", "numpy", "plotly", "scikit-learn"]

# Auto-instalação no servidor em nuvem caso alguma biblioteca falhe
for package in packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Importações das bibliotecas principais
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# Configuração da página
st.set_page_config(
    page_title="InvestIA - Plataforma de Inteligência Financeira",
    page_icon="📈",
    layout="wide"
)

# Estilização básica da interface
st.title("📈 InvestIA - Plataforma de Análise e Planejamento Financeiro")
st.markdown("---")

# Barra Lateral (Sidebar) - Controles e Parâmetros
st.sidebar.header("⚙️ Configurações do Analista")

ticker_input = st.sidebar.text_input("Código do Ativo (B3):", value="PETR4.SA")
if not ticker_input.endswith(".SA") and not ticker_input.startswith("^"):
    ticker_input_formatted = f"{ticker_input.upper()}.SA"
else:
    ticker_input_formatted = ticker_input.upper()

prazo_meses = st.sidebar.slider("Prazo de Investimento (Meses):", min_value=12, max_value=360, value=120, step=12)
aporte_mensal = st.sidebar.number_input("Aporte Mensal Estimado (R$):", min_value=100, max_value=50000, value=500, step=100)

# Estrutura Principal de Abas
aba1, aba2, aba3 = st.tabs(["📊 Análise do Ativo & IA", "💰 Simulação Patrimonial", "ℹ️ Sobre o Projeto"])

# ----------------------------------------------------
# ABA 1: Análise de Mercado e Modelo de Machine Learning
# ----------------------------------------------------
with aba1:
    st.subheader(f"Análise Técnica e Diagnóstico de IA: {ticker_input_formatted}")
    
    try:
        with st.spinner("Buscando dados históricos do ativo..."):
            dados = yf.download(ticker_input_formatted, period="2y", progress=False)
            
        if dados.empty:
            st.error(f"Não foram encontrados dados para o código '{ticker_input_formatted}'. Verifique a digitação.")
        else:
            # Cálculo de Indicadores
            dados['Retorno'] = dados['Close'].pct_change()
            dados['MA_20'] = dados['Close'].rolling(window=20).mean()
            dados['MA_50'] = dados['Close'].rolling(window=50).mean()
            dados['Alvo'] = np.where(dados['Close'].shift(-5) > dados['Close'], 1, 0)
            
            # Gráfico de Preços e Médias Móveis
            fig_preco = go.Figure()
            fig_preco.add_trace(go.Scatter(x=dados.index, y=dados['Close'].values.flatten(), mode='lines', name='Preço de Fechamento'))
            fig_preco.add_trace(go.Scatter(x=dados.index, y=dados['MA_20'].values.flatten(), mode='lines', name='Média Móvel 20 dias', line=dict(dash='dash')))
            fig_preco.add_trace(go.Scatter(x=dados.index, y=dados['MA_50'].values.flatten(), mode='lines', name='Média Móvel 50 dias', line=dict(dash='dot')))
            
            fig_preco.update_layout(
                title=f"Histórico de Preços e Tendências ({ticker_input_formatted})",
                xaxis_title="Data",
                yaxis_title="Preço (R$)",
                template="plotly_white"
            )
            st.plotly_chart(fig_preco, use_container_width=True)
            
            # Modelo de IA (Random Forest Classifier)
            dados_clean = dados.dropna()
            features = ['Retorno', 'MA_20', 'MA_50']
            
            X = dados_clean[features]
            y = dados_clean['Alvo']
            
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Predição para os próximos dias
            ultima_linha = X.iloc[[-1]]
            predicao = model.predict(ultima_linha)[0]
            probabilidade = model.predict_proba(ultima_linha)[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Último Fechamento Cotado", 
                    value=f"R$ {dados['Close'].iloc[-1].item():.2f}"
                )
            with col2:
                tendencia_texto = "ALTA 🚀" if predicao == 1 else "QUEDA / NEUTRO 📉"
                confianca = probabilidade[1] if predicao == 1 else probabilidade[0]
                st.metric(
                    label="Tendência Prevista pela IA (Curto Prazo)", 
                    value=tendencia_texto,
                    delta=f"Confiança do Modelo: {confianca * 100:.1f}%"
                )

    except Exception as e:
        st.error(f"Erro ao processar os dados do ativo: {str(e)}")

# ----------------------------------------------------
# ABA 2: Planejamento Financeiro e Juros Compostos
# ----------------------------------------------------
with aba2:
    st.subheader("Simulador de Acumulação Patrimonial")
    
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        taxa_anual = st.number_input("Taxa de Juros Anual Esperada (%):", min_value=1.0, max_value=30.0, value=10.0, step=0.5)
    with col_sim2:
        patrimonio_inicial = st.number_input("Aporte Inicial (R$):", min_value=0, max_value=1000000, value=1000, step=500)
        
    taxa_mensal = (1 + (taxa_anual / 100)) ** (1/12) - 1
    
    meses = np.arange(1, prazo_meses + 1)
    patrimonio = []
    total_investido = []
    
    saldo = patrimonio_inicial
    investido = patrimonio_inicial
    
    for m in meses:
        saldo = saldo * (1 + taxa_mensal) + aporte_mensal
        investido += aporte_mensal
        patrimonio.append(saldo)
        total_investido.append(investido)
        
    df_simulacao = pd.DataFrame({
        'Mês': meses,
        'Patrimônio Total': patrimonio,
        'Total Investido': total_investido
    })
    
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(x=df_simulacao['Mês'], y=df_simulacao['Patrimônio Total'], mode='lines', name='Patrimônio Bruto', fill='tozeroy'))
    fig_sim.add_trace(go.Scatter(x=df_simulacao['Mês'], y=df_simulacao['Total Investido'], mode='lines', name='Total Aplicado do Bolso', line=dict(dash='dash')))
    
    fig_sim.update_layout(
        title=f"Projeção em {prazo_meses} Meses (Rendimentos vs Aportes)",
        xaxis_title="Período (Meses)",
        yaxis_title="Montante (R$)",
        template="plotly_white"
    )
    st.plotly_chart(fig_sim, use_container_width=True)
    
    res1, res2 = st.columns(2)
    res1.success(f"**Valor Total Acumulado:** R$ {patrimonio[-1]:,.2f}")
    res2.info(f"**Total do Próprio Bolso:** R$ {total_investido[-1]:,.2f}")

# ----------------------------------------------------
# ABA 3: Informações do Projeto
# ----------------------------------------------------
with aba3:
    st.subheader("Sobre a Plataforma InvestIA")
    st.markdown("""
    Esta aplicação foi desenvolvida como parte de projeto técnico focado em **Inteligência Artificial aplicada ao Mercado Financeiro e Análise de Dados**.
    
    **Funcionalidades:**
    - Coleta automatizada de cotações da B3 via integração de dados.
    - Classificação de tendência com **Random Forest (Machine Learning)**.
    - Algoritmo simulador de curva de juros compostos para planejamento financeiro de longo prazo.
    """)
