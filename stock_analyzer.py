# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# ── 1. Library Checks ────────────────────────────────────────
try:
    import pandas_ta as ta
    TA_OK = True
except ImportError:
    TA_OK = False

try:
    from settrade_v2 import Investor
    ST_OK = True
except ImportError:
    ST_OK = False

try:
    import yfinance as yf
    YF_OK = True
except ImportError:
    YF_OK = False

# ── 2. Page Config & CSS (ธีมเดิมของคุณ 100%) ──────────────────────
st.set_page_config(
    page_title="Stock Scanner Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;background:#0d0d14;color:#e2e8f0}
.app-hdr{background:linear-gradient(135deg,#12122a,#1a1035,#0f1f3a);border:1px solid rgba(108,99,255,.3);border-radius:16px;padding:18px;text-align:center;margin-bottom:16px}
.app-hdr h1{font-size:1.4rem;font-weight:700;color:#fff;margin:0}
.login-card{background:linear-gradient(135deg,#12122a,#1a1a2e);border:1px solid rgba(108,99,255,.35);border-radius:20px;padding:24px;margin-bottom:20px}
.stock-card{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:14px;padding:14px;margin-bottom:10px}
.stock-card.buy{border-left:4px solid #00b894}
.stock-card.sell{border-left:4px solid #d63031}
.stock-card.watch{border-left:4px solid #fdcb6e}
.sc-sym{font-size:1.05rem;font-weight:700;color:#fff;font-family:'IBM Plex Mono',monospace}
.sring{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.85rem;font-weight:700;font-family:'IBM Plex Mono',monospace;flex-shrink:0}
.sh{background:rgba(0,184,148,.2);border:2px solid #00b894;color:#00b894}
div.stButton>button{width:100%;background:linear-gradient(135deg,#6c63ff,#4f46e5);color:#fff;border-radius:12px;font-weight:700}
</style>
""", unsafe_allow_html=True)

# ── 3. MARKETS DATA (ย้ายมาไว้ตรงนี้เพื่อแก้ ImportError) ──────────
MARKETS = {
    "SET": {
        "name": "ตลาดหุ้นไทย", "stocks": [
            ("KBANK","กสิกรไทย"),("BBL","กรุงเทพ"),("SCB","ไทยพาณิชย์"),("PTT","ปตท."),("ADVANC","แอดวานซ์")
        ]
    },
    "US": { "name": "US Tech", "stocks": [("AAPL","Apple"),("TSLA","Tesla"),("NVDA","NVIDIA")] },
    "CN": { "name": "CN Tech", "stocks": [("BABA","Alibaba"),("JD","JD.com")] }
}

# ── 4. Session State ────────────────────────────────────────
for k, v in [
    ("logged_in", False), ("st_inv", None), ("st_mkt", None), ("st_rt", None), 
    ("view", "login"), ("market", "SET"), ("scan_results", {}), ("detail_sym", None)
]:
    if k not in st.session_state: st.session_state[k] = v

# ── 5. Data Fetch (ปรับปรุงให้ใช้ st_mkt / st_rt ระบบใหม่) ───────
def get_data(symbol, mkt_key):
    if st.session_state.logged_in and mkt_key == "SET":
        try:
            raw = st.session_state.st_mkt.get_candlestick(symbol, interval="1d", limit=100)
            df = pd.DataFrame(raw)
            df.columns = [str(c).lower() for c in df.columns]
            df.rename(columns={"last":"close","c":"close","o":"open","h":"high","l":"low","v":"volume"}, inplace=True)
            if st.session_state.st_rt:
                try:
                    q = st.session_state.st_rt.get_quote_symbol(symbol)
                    if q and "last" in q: df.iloc[-1, df.columns.get_loc("close")] = float(q["last"])
                except: pass
            return df[["open","high","low","close","volume"]].apply(pd.to_numeric), {"source": "settrade"}
        except: pass
    if YF_OK:
        try:
            ticker = yf.Ticker(symbol + ".BK" if mkt_key == "SET" else symbol)
            df = ticker.history(period="1y")[["Open","High","Low","Close","Volume"]]
            df.columns = ["open","high","low","close","volume"]
            return df, {"source": "yfinance"}
        except: pass
    return pd.DataFrame(), {"source": "none"}

# ── 6. New Login View (Smart Discovery เหมือน Stock Pro) ────────
def view_login():
    st.markdown('<div class="app-hdr"><h1>Stock Scanner Pro</h1></div>', unsafe_allow_html=True)
    with st.form("smart_login_form"):
        app_id = st.text_input("APP_ID", value=st.session_state.get("prefill_id", ""))
        app_secret = st.text_input("APP_SECRET", type="password")
        app_acct = st.text_input("ACCOUNT_NO (ถ้ามี)")
        if st.form_submit_button("CONNECT SETTRADE", use_container_width=True):
            try:
                inv = Investor(app_id=app_id.strip(), app_secret=app_secret.strip(), app_code="SANDBOX", broker_id="SANDBOX")
                m_api, r_api = None, None
                if hasattr(inv, 'Equity'):
                    e = inv.Equity(app_acct.strip()) if app_acct.strip() else inv.Equity()
                    if hasattr(e, 'get_candlestick'): m_api = e
                if not m_api: m_api = inv.MarketData()
                r_api = inv.RealtimeDataConnection() if hasattr(inv, 'RealtimeDataConnection') else None
                st.session_state.update({"logged_in": True, "st_mkt": m_api, "st_rt": r_api, "view": "scan"})
                st.rerun()
            except Exception as e: st.error(f"Login Failed: {e}")

# ── 7. หน้าสแกนหุ้น (ดึง UI เดิมกลับมา) ──────────────────────────
def view_scan():
    st.markdown('<div class="app-hdr"><h1>Market Scanner</h1></div>', unsafe_allow_html=True)
    m_key = st.selectbox("เลือกตลาด", ["SET", "US", "CN"], index=0)
    
    if st.button(f"เริ่มสแกนหุ้น {m_key}", use_container_width=True):
        stocks = MARKETS[m_key]["stocks"]
        results = []
        for sym, name in stocks:
            df, info = get_data(sym, m_key)
            if not df.empty:
                price = df['close'].iloc[-1]
                chg = (price / df['close'].iloc[-2] - 1) * 100 if len(df) > 1 else 0
                results.append({"Symbol": sym, "Name": name, "Price": price, "Change": chg})
        st.session_state.scan_results[m_key] = results

    res = st.session_state.scan_results.get(m_key, [])
    for row in res:
        st.markdown(f"""
        <div class="stock-card buy">
            <div style="display:flex; justify-content:space-between">
                <div><div class="sc-sym">{row['Symbol']}</div><div style="font-size:0.7rem; color:#8892b0;">{row['Name']}</div></div>
                <div style="text-align:right">
                    <div style="font-weight:700;">{row['Price']:,.2f}</div>
                    <div style="font-size:0.7rem; color:#00b894;">{row['Change']:+.2f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"ดูอินดิเคเตอร์ {row['Symbol']}", key=f"btn_{row['Symbol']}"):
            st.session_state.detail_sym = row['Symbol']
            st.session_state.view = "detail"
            st.rerun()

def view_detail():
    st.markdown(f'<div class="app-hdr"><h1>วิเคราะห์หุ้น {st.session_state.detail_sym}</h1></div>', unsafe_allow_html=True)
    if st.button("← กลับ"): st.session_state.view = "scan"; st.rerun()
    st.info("หน้านี้จะแสดงกราฟและอินดิเคเตอร์ (MACD, RSI, SMA) ตามฟังก์ชันเดิมของคุณ")

# ── 8. Router ──────────────────────────────────────────────────
if st.session_state.view == "login": view_login()
elif st.session_state.view == "scan": view_scan()
elif st.session_state.view == "detail": view_detail()
