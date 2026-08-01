import sys
import subprocess

# Lista de bibliotecas necessárias para o InvestIA
packages = ["yfinance", "pandas", "numpy", "plotly", "scikit-learn"]

# Instala automaticamente no servidor da nuvem se não estiverem presentes
for package in packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Importações principais do aplicativo
import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifierimport streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier

# Configuração da Interface Streamlit
st.set_page_config(page_title="InvestIA - Análise Fundamentalista", page_icon="📈", layout="wide")
st.title("📈 InvestIA: Plataforma Inteligente de Análise e Planejamento Financeiro")
st.caption("Projeto Integrador - Curso Técnico em Inteligência Artificial (CETAM)")

# Barra Lateral: Parâmetros de Entrada
ticker_input = st.sidebar.text_input("Código do Ativo (ex: ITUB4, PETR4, VALE3):", "ITUB4").strip().upper()
ticker_symbol = ticker_input + ".SA" if not ticker_input.endswith(".SA") else ticker_input

aporte_inicial = st.sidebar.number_input("Aporte Inicial (R$):", value=1000, step=100)
aporte_mensal = st.sidebar.number_input("Aporte Mensal (R$):", value=200, step=50)
anos = st.sidebar.slider("Tempo de Investimento (Anos):", min_value=1, max_value=30, value=10)

# Motor de Classificação de IA (Random Forest)
def classificar_ativo_ia(pl, roe, dy):
    X_train = np.array([[8.0, 18.0, 7.0], [6.0, 22.0, 9.0], [25.0, 12.0, 1.5], [30.0, 25.0, 0.5], [-5.0, -2.0, 0.0]])
    y_train = np.array([1, 1, 2, 2, 0]) # 0: Alto Risco, 1: Sólido/Renda, 2: Crescimento
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(X_train, y_train)
    return clf.predict([[pl, roe, dy]])[0]

# Execução e Exibição de Resultados
try:
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    preco = info.get("currentPrice", info.get("regularMarketPrice", 0.0))
    pl = info.get("forwardPE", info.get("trailingPE", 10.0))
    roe = (info.get("returnOnEquity", 0.15) or 0.15) * 100
    dy = (info.get("dividendYield", 0.05) or 0.05) * 100

    st.header(f"{info.get('longName', ticker_input)} ({ticker_input})")
    st.metric("Cotação Atual", f"R$ {preco:.2f}")

    pred = classificar_ativo_ia(pl, roe, dy)
    st.info(f"Diagnóstico do Motor de IA: Classe {pred}")
except Exception as e:
    st.error(f"Erro ao carregar dados do ativo: {e}")
