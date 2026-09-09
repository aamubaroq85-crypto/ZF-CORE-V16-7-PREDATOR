import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
import requests

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="ZF-Core V16.7 Predator - Live & Telegram",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ZF-CORE V16.7-PREDATOR | LIVE YFINANCE & TELEGRAM")
st.markdown("*Platform Eksekusi Taktis dengan Live Market Feed & Notifikasi Otomatis*")
st.markdown("---")

# --- 2. KONFIGURASI TELEGRAM (OPSIONAL/DIAMANKAN) ---
#8996672173:AAHV3UJ2Na9eRaQ1VK2n_RW3MMLmZVAMZEc atau menggunakan st.sidebar / st.secrets
st.sidebar.header("🤖 Konfigurasi Telegram Bot")
telegram_token = st.sidebar.text_input("Bot Token Telegram", type="password", value="")
telegram_chat_id = st.sidebar.text_input("Chat ID Telegram", value="")

def send_telegram_alert(message):
    if telegram_token and telegram_chat_id:
        try:
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            payload = {
                "chat_id": telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            pass # Mencegah error crash jika koneksi telegram terputus

# --- 3. SIDEBAR KONTROL & PEMILIHAN ASET ---
st.sidebar.markdown("---")
st.sidebar.header("🎛️ Panel Kontrol Live API")
ticker_symbol = st.sidebar.selectbox(
    "Pilih Aset / Simbol Pasar", 
    ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "GC=F", "BTC-USD"]
)
total_capital = st.sidebar.number_input("Total Modal Alokasi ($)", value=10000.0, step=500.0)

# Pengaturan Bobot EVO Adaptif
if 'evo_weights' not in st.session_state:
    st.session_state.evo_weights = {"w_drift": 0.6, "w_lambda": 0.4}

st.sidebar.markdown("---")
st.sidebar.subheader("🧬 ZF-Core EVO Status")
st.sidebar.text(f"Bobot Drift (w1): {st.session_state.evo_weights['w_drift']:.2f}")
st.sidebar.text(f"Bobot Lambda (w2): {st.session_state.evo_weights['w_lambda']:.2f}")

# --- 4. PENGAMBILAN DATA LIVE DARI YFINANCE ---
@st.cache_data(ttl=300)
def fetch_live_data(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="15m", progress=False)
        if data.empty:
            data = yf.download(symbol, period="1d", interval="1m", progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        data = data.dropna()
        return data
    except Exception as e:
        return None

df_market = fetch_live_data(ticker_symbol)

if df_market is None or df_market.empty:
    st.error(f"Gagal mengambil data untuk simbol {ticker_symbol}. Periksa koneksi atau pilih simbol lain.")
    st.stop()

df_market = df_market.reset_index()
time_col = 'Datetime' if 'Datetime' in df_market.columns else 'Date'

# --- 5. ENGINE MATEMATIKA & ZF-SCORE ---
w1 = st.session_state.evo_weights['w_drift']
w2 = st.session_state.evo_weights['w_lambda']

p_pure = df_market['Close'].rolling(window=20, min_periods=1).mean()
drift = np.abs(df_market['Close'] - p_pure) / p_pure
rolling_std = df_market['Close'].rolling(window=7, min_periods=1).std().fillna(0)
lambda_dyn = 1.0 * (1 + ((df_market['High'] - df_market['Low']) / df_market['Close'])) * (1 + rolling_std)

max_lambda = lambda_dyn.max()
if max_lambda == 0 or pd.isna(max_lambda):
    max_lambda = 1.0

zf_score = 1 / (1 + np.exp(-10 * ((w1 * drift) + (w2 * (lambda_dyn / max_lambda)) - 0.5)))
df_market['ZF_Score'] = zf_score

latest = df_market.iloc[-1]
current_score = float(latest['ZF_Score'])
current_price = float(latest['Close'])

# Evaluasi Status Determinan
if current_score > 0.99:
    status_level, action_text = "FATAL", "CIRCUIT_BREAKER_ALL_STOP"
elif current_score <= 0.84:
    status_level, action_text = "OPTIMAL", "RESONANCE_RE_ENTRY"
else:
    status_level, action_text = "NORMAL", "SILENT_BACKGROUND_SCAN"

# Tombol Kirim Alert Manual ke Telegram
if st.sidebar.button("🚀 Kirim Sinyal ke Telegram"):
    alert_msg = (
        f"⚡ *ZF-CORE PREDATOR ALERT*\n\n"
        f"📊 Simbol: `{ticker_symbol}`\n"
        f"💵 Harga Live: `{current_price:.5f}`\n"
        f"🎯 ZF-Score: `{current_score:.4f}`\n"
        f"🛡️ Status: *{status_level}*\n"
        f"⚙️ Aksi: `{action_text}`\n"
        f"🕒 Waktu: `{datetime.utcnow()} UTC`"
    )
    send_telegram_alert(alert_msg)
    st.sidebar.success("Notifikasi berhasil dikirim ke Telegram!")

# --- 6. TAMPILAN METRIK UTAMA ---
col1, col2, col3, col4 = st.columns(4)
col1.metric(f"Harga Live ({ticker_symbol})", f"{current_price:.5f}")
col2.metric("ZF-Score Predator", f"{current_score:.4f}")
col3.metric("Status Sistem", status_level)
col4.metric("Aksi Determinan", action_text)

st.markdown("---")

# --- 7. VISUALISASI GRAFIK PASAR ---
st.subheader(f"📈 Grafik Manifold & Resonansi ZF-Score: {ticker_symbol}")
tab1, tab2 = st.tabs(["Grafik Harga Penutupan", "Indikator ZF-Score"])

with tab1:
    st.line_chart(df_market.set_index(time_col)['Close'])
with tab2:
    st.line_chart(df_market.set_index(time_col)['ZF_Score'])

st.markdown("---")

# --- 8. ALOKASI MODAL & RISIKO ---
st.subheader("🛡️ Protokol Alokasi Modal & Risiko Multi-Tier")

if status_level == "OPTIMAL":
    st.success("✨ Manifold dalam Kondisi Resonansi Optimal Berdasarkan Data Pasar Nyata:")
    t1, t2, t3 = st.columns(3)
    t1.info(f"**Tier 1 (30%)**\n\n💵 ${total_capital * 0.30:,.2f}\n\n*Inisialisasi Posisi Awal*")
    t2.info(f"**Tier 2 (50%)**\n\n💵 ${total_capital * 0.50:,.2f}\n\n*Penguatan Posisi Utama*")
    t3.info(f"**Tier 3 (20%)**\n\n💵 ${total_capital * 0.20:,.2f}\n\n*Cadangan Akumulasi Taktis*")
elif status_level == "FATAL":
    st.error("🚨 PERINGATAN FATAL: Circuit Breaker Aktif! Pasar menunjukkan distorsi ekstrem.")
else:
    st.warning("⚠️ Status Normal / Pemindaian Latar Belakang. Menunggu konvergensi resonansi berikutnya.")

st.markdown("---")

# --- 9. ARCHIVAL VAULT ---
st.subheader("🏛️ Archival Vault (Live Session Log)")
archive_data = {
    "timestamp": str(datetime.utcnow()),
    "symbol": ticker_symbol,
    "live_price": current_price,
    "zf_score": current_score,
    "status": status_level,
    "action": action_text,
    "allocated_capital": total_capital
}
st.json(archive_data)

