import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ZF-Core V16.7 Predator - Full Console",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ZF-CORE V16.7-PREDATOR | FULL SYSTEM CONSOLE")
st.markdown("*Platform Eksekusi Taktis, Arsip, dan Self-Optimization Berbasis Zuhri Formalism*")
st.markdown("---")

# --- 2. SIDEBAR KONTROL PARAMETER ---
st.sidebar.header("🎛️ Panel Kontrol Taktis")
total_capital = st.sidebar.number_input("Total Modal Alokasi ($)", value=10000.0, step=500.0)
risk_profile = st.sidebar.selectbox("Profil Risiko Manifold", ["Konservatif", "Moderat", "Agresif"])

# Pengaturan Bobot EVO Adaptif (Simulasi State)
if 'evo_weights' not in st.session_state:
    st.session_state.evo_weights = {"w_drift": 0.6, "w_lambda": 0.4}

st.sidebar.markdown("---")
st.sidebar.subheader("🧬 ZF-Core EVO Status")
st.sidebar.text(f"Bobot Drift (w1): {st.session_state.evo_weights['w_drift']:.2f}")
st.sidebar.text(f"Bobot Lambda (w2): {st.session_state.evo_weights['w_lambda']:.2f}")

# --- 3. ENGINE MATEMATIKA & MANIFOLD SIMULASI ---
@st.cache_data(ttl=60)
def generate_market_manifold():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.utcnow(), periods=100, freq="min")
    closes = 1.1000 + np.cumsum(np.random.normal(0, 0.0003, 100))
    df = pd.DataFrame({
        'Timestamp': dates,
        'Close': closes,
        'High': closes + 0.0005,
        'Low': closes - 0.0005
    })
    return df

df_market = generate_market_manifold()

# Kalkulasi ZF-Score Berdasarkan Bobot EVO Aktif
w1 = st.session_state.evo_weights['w_drift']
w2 = st.session_state.evo_weights['w_lambda']

p_pure = df_market['Close'].rolling(window=20, min_periods=1).mean()
drift = np.abs(df_market['Close'] - p_pure) / p_pure
rolling_std = df_market['Close'].rolling(window=7, min_periods=1).std().fillna(0)
lambda_dyn = 1.0 * (1 + ((df_market['High'] - df_market['Low']) / df_market['Close'])) * (1 + rolling_std)

zf_score = 1 / (1 + np.exp(-10 * ((w1 * drift) + (w2 * (lambda_dyn / lambda_dyn.max())) - 0.5)))
df_market['ZF_Score'] = zf_score

latest = df_market.iloc[-1]
current_score = latest['ZF_Score']

# Evaluasi Status Determinan
if current_score > 0.99:
    status_level, action_text, badge_color = "FATAL", "CIRCUIT_BREAKER_ALL_STOP", "red"
elif current_score <= 0.84:
    status_level, action_text, badge_color = "OPTIMAL", "RESONANCE_RE_ENTRY", "green"
else:
    status_level, action_text, badge_color = "NORMAL", "SILENT_BACKGROUND_SCAN", "orange"

# --- 4. TAMPILAN METRIK UTAMA ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Harga Manifold", f"{latest['Close']:.5f}")
col2.metric("ZF-Score Predator", f"{current_score:.4f}")
col3.metric("Status Sistem", status_level)
col4.metric("Aksi Determinan", action_text)

st.markdown("---")

# --- 5. VISUALISASI GRAFIK MANIFOLD & ZF-SCORE ---
st.subheader("📈 Analisis Grafik Manifold & Resonansi ZF-Score")
tab1, tab2 = st.tabs(["Grafik Harga Penutupan", "Indikator ZF-Score"])

with tab1:
    st.line_chart(df_market.set_index('Timestamp')['Close'])
with tab2:
    st.line_chart(df_market.set_index('Timestamp')['ZF_Score'])

st.markdown("---")

# --- 6. ALOKASI MODAL & TIERED RISK CONTROL ---
st.subheader("🛡️ Protokol Alokasi Modal & Risiko Multi-Tier")

if status_level == "OPTIMAL":
    st.success("✨ Manifold dalam Kondisi Resonansi Optimal. Alokasi Modal Siap Dieksekusi:")
    t1, t2, t3 = st.columns(3)
    t1.info(f"**Tier 1 (30% Alokasi)**\n\n💵 ${total_capital * 0.30:,.2f}\n\n*Inisialisasi Posisi Awal*")
    t2.info(f"**Tier 2 (50% Alokasi)**\n\n💵 ${total_capital * 0.50:,.2f}\n\n*Penguatan Posisi Utama*")
    t3.info(f"**Tier 3 (20% Alokasi)**\n\n💵 ${total_capital * 0.20:,.2f}\n\n*Cadangan Akumulasi Taktis*")
elif status_level == "FATAL":
    st.error("🚨 PERINGATAN FATAL: Circuit Breaker Aktif! Seluruh aktivitas perdagangan ditangguhkan untuk melindungi aset dari distorsi ekstrem manifold.")
else:
    st.warning("⚠️ Status Normal / Pemindaian Latar Belakang. Menunggu konvergensi resonansi geometris berikutnya.")

st.markdown("---")

# --- 7. ARCHIVAL VAULT & EVO SELF-OPTIMIZATION LOG SIMULATION ---
st.subheader("🏛️ Archival Vault & ZF-Core EVO Log")

col_vault1, col_vault2 = st.columns(2)

with col_vault1:
    st.markdown("#### 📂 Arsip Sesi Terakhir (JSON Vault)")
    archive_data = {
        "timestamp": str(datetime.utcnow()),
        "manifold_price": float(latest['Close']),
        "zf_score": float(current_score),
        "status": status_level,
        "action": action_text,
        "allocated_capital": total_capital
    }
    st.json(archive_data)

with col_vault2:
    st.markdown("#### 🧬 Simulasi Penyesuaian Bobot Mandiri (EVO)")
    if st.button("Jalankan Siklus Self-Optimization EVO"):
        # Simulasi penyesuaian bobot adaptif
        st.session_state.evo_weights['w_drift'] = np.clip(w1 + np.random.normal(0, 0.02), 0.4, 0.8)
        st.session_state.evo_weights['w_lambda'] = 1.0 - st.session_state.evo_weights['w_drift']
        st.success("Berhasil! Bobot arsitektur ZF-Core telah dioptimalkan secara mandiri.")
        st.rerun()
    else:
        st.info("Sistem EVO berjalan sinkron dengan fluktuasi manifold secara real-time.")
