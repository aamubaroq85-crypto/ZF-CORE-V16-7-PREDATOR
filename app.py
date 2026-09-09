import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Konfigurasi Halaman Dashboard
st.set_page_config(
    page_title="ZF-Core V16.7 Predator Dashboard",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ZF-CORE V16.7-PREDATOR | LIVE WEB CONSOLE")
st.markdown("*Sistem Pemantauan Manifold & Protokol Eksekusi Taktis Berbasis Zuhri Formalism*")
st.markdown("---")

# Sidebar untuk Kontrol Parameter
st.sidebar.header("Pengaturan Simulasi")
total_capital = st.sidebar.number_input("Total Modal ($)", value=10000, step=500)
refresh_btn = st.sidebar.button("Jalankan Pemindaian Ulang")

# Simulasi Data Manifold Terkini
np.random.seed()
dates = pd.date_range(end=datetime.utcnow(), periods=60, freq="min")
closes = 1.1000 + np.cumsum(np.random.normal(0, 0.0003, 60))
df = pd.DataFrame({
    'Timestamp': dates,
    'Close': closes,
    'High': closes + 0.0004,
    'Low': closes - 0.0004
})

# Kalkulasi Matematika ZF-Score
p_pure = df['Close'].rolling(window=20, min_periods=1).mean()
drift = np.abs(df['Close'] - p_pure) / p_pure
rolling_std = df['Close'].rolling(window=7, min_periods=1).std().fillna(0)
lambda_dyn = 1.0 * (1 + ((df['High'] - df['Low']) / df['Close'])) * (1 + rolling_std)
zf_score = 1 / (1 + np.exp(-10 * ((0.6 * drift) + (0.4 * (lambda_dyn / lambda_dyn.max())) - 0.5)))

df['ZF_Score'] = zf_score
latest = df.iloc[-1]
score = latest['ZF_Score']

# Evaluasi Risiko
if score > 0.99:
    status_level, action_text = "FATAL", "CIRCUIT_BREAKER_ALL_STOP"
    status_color = "red"
elif score <= 0.84:
    status_level, action_text = "OPTIMAL", "RESONANCE_RE_ENTRY"
    status_color = "green"
else:
    status_level, action_text = "NORMAL", "SILENT_BACKGROUND_SCAN"
    status_color = "orange"

# Tampilan Metrik Utama (Metrics Cards)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Harga Manifold", f"{latest['Close']:.5f}")
col2.metric("ZF-Score Predator", f"{score:.4f}")
col3.metric("Status Sistem", status_level)
col4.metric("Aksi Determinan", action_text)

st.markdown("---")

# Grafik Pergerakan ZF-Score & Harga
st.sub_header("📈 Grafik Tren ZF-Score Real-Time")
chart_data = pd.DataFrame({
    'ZF-Score': df['ZF_Score'].values,
    'Harga Penutupan': df['Close'].values
}, index=df['Timestamp'])
st.line_chart(chart_data)

# Alokasi Modal Jika Optimal
if status_level == "OPTIMAL":
    st.success("✨ Status Manifold Optimal: Alokasi Modal Multi-Tier Siap Dieksekusi!")
    t1, t2, t3 = st.columns(3)
    t1.info(f"**Tier 1 (30%)**\n\n ${total_capital * 0.30:,.2f}")
    t2.info(f"**Tier 2 (50%)**\n\n ${total_capital * 0.50:,.2f}")
    t3.info(f"**Tier 3 (20%)**\n\n ${total_capital * 0.20:,.2f}")
else:
    st.warning("⚠️ Sistem dalam status pengawasan ketat. Eksekusi ditangguhkan.")
