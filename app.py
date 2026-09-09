%%writefile app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="ZF-Core Predator", layout="wide")

st.title("⚡ ZF-CORE V16.7-PREDATOR | LIVE WEB CONSOLE")
st.markdown("*Sistem Pemantauan Manifold & Protokol Eksekusi Taktis*")
st.markdown("---")

# Simulasi Data
np.random.seed()
dates = pd.date_range(end=datetime.utcnow(), periods=60, freq="min")
closes = 1.1000 + np.cumsum(np.random.normal(0, 0.0003, 60))
df = pd.DataFrame({'Timestamp': dates, 'Close': closes, 'High': closes + 0.0004, 'Low': closes - 0.0004})

p_pure = df['Close'].rolling(window=20, min_periods=1).mean()
drift = np.abs(df['Close'] - p_pure) / p_pure
rolling_std = df['Close'].rolling(window=7, min_periods=1).std().fillna(0)
lambda_dyn = 1.0 * (1 + ((df['High'] - df['Low']) / df['Close'])) * (1 + rolling_std)
zf_score = 1 / (1 + np.exp(-10 * ((0.6 * drift) + (0.4 * (lambda_dyn / lambda_dyn.max())) - 0.5)))

score = zf_score.iloc[-1]
status_level = "OPTIMAL" if score <= 0.84 else ("FATAL" if score > 0.99 else "NORMAL")
action_text = "RESONANCE_RE_ENTRY" if status_level == "OPTIMAL" else "SILENT_BACKGROUND_SCAN"

# Tampilan Menggunakan Markdown Murni (Menghindari Error Dynamic Import Component)
st.markdown(f"### 📊 Ringkasan Metrik Terkini")
st.markdown(f"""
- **Harga Manifold:** `{df['Close'].iloc[-1]:.5f}`
- **ZF-Score Predator:** `{score:.4f}`
- **Status Sistem:** **{status_level}**
- **Aksi Determinan:** `{action_text}`
""")

st.markdown("---")
st.subheader("📈 Grafik Tren Pergerakan Manifold")
st.line_chart(df.set_index('Timestamp')['Close'])
