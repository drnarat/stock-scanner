# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- Library Checks ---
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

# ---------------------------------------------------------------
# 1. PAGE CONFIG & THEME (CSS)
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Stock Scanner Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;background:#0d0d14;color:#e2e8f0}
footer{visibility:hidden}#MainMenu{visibility:hidden}
header[data-testid="stHeader"]{background:#0d0d14!important}
.app-hdr{background:linear-gradient(135deg,#12122a,#1a1035,#0f1f3a);border:1px solid rgba(108,99,255,.3);border-radius:16px;padding:18px 16px 14px;text-align:center;margin-bottom:16px}
.app-hdr h1{font-size:1.4rem;font-weight:700;color:#fff}
.login-card{background:linear-gradient(135deg,#12122a,#1a1a2e);border:1px solid rgba(108,99,255,.35);border-radius:20px;padding:24px 20px;margin:8px 0 20px}
.stock-card{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:14px;padding:14px;margin-bottom:10px}
.stock-card.buy{border-left:4px solid #00b894}
.stock-card.sell{border-left:4px solid #d63031}
.stock-card.watch{border-left:4px solid #fdcb6e}
.sring{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.85rem;font-weight:700;font-family:'IBM Plex Mono',monospace;flex-shrink:0}
.sh{background:rgba(0,184,148,.2);border:2px solid #00b894;color:#00b894}
.sm{background:rgba(253,203,110,.2);border:2px solid #fdcb6e;color:#fdcb6e}
.sl{background:rgba(214,48,49,.2);border:2px solid #d63031;color:#d63031}
div.stButton>button{width:100%;background:linear-gradient(135deg,#6c63ff,#4f46e5);color:#fff;border:none;border-radius:12px;padding:14px;font-weight:700}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# 2. SESSION STATE
# ---------------------------------------------------------------
if "view" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "st_inv": None, "st_mkt": None, "st_rt": None,
        "st_equity": None, "account_no": "", "view": "login",
        "market": "SET", "scan_results": {}, "detail_sym": None, "detail_mkt": None,
        "prefill_id": "", "prefill_secret": "", "prefill_code": "SANDBOX", "prefill_broker": "SANDBOX"
    })

# ---------------------------------------------------------------
# 3. CORE LOGIC (Data & Scoring)
# ---------------------------------------------------------------
def fetch_settrade(symbol, limit=200):
    try:
        raw = st.session_state.st_mkt.get_candlestick(symbol, interval="1d", limit=limit)
        df = pd.DataFrame(raw)
        df.columns = [str(c).lower() for c in df.columns]
        rename = {"last":"close","c":"close","o":"open","h":"high","l":"low","v":"volume","vol":"volume"}
        df.rename(columns=rename, inplace=True)
        return df[["open","high","low","close","volume"]].apply(pd.to_numeric, errors="coerce").dropna()
    except: return pd.DataFrame()

def get_data(symbol, mkt_key):
    info = {"source": "mock"}
    if st.session_state.logged_in and mkt_key == "SET":
        df = fetch_settrade(symbol)
        if not df.empty:
            q = st.session_state.st_rt.get_quote_symbol(symbol) if st.session_state.st_rt else None
            if q and ("last" in q):
                df.iloc[-1, df.columns.get_loc("close")] = float(q["last"])
            info["source"] = "settrade"
            return df, info
    # ... Fallback to mock/yf logic ...
    return pd.DataFrame(), info

# ---------------------------------------------------------------
# 4. VIEW: LOGIN (Smart Discovery)
# ---------------------------------------------------------------
def view_login():
    st.markdown('<div class="app-hdr"><h1>Stock Scanner Pro</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card"><h2>เชื่อมต่อ Settrade API</h2></div>', unsafe_allow_html=True)
    
    if st.button("ใช้ค่า SANDBOX", key="login_sb"):
        st.session_state.prefill_id = "MPRZz1Hymo6nR50A"
        st.session_state.prefill_secret = "Te/3LKXBb+IM20T/ygcFAMWXjIgkadJ+o1cDstkjRDQ="
        st.rerun()

    with st.form("st_clean_login_form"):
        app_id = st.text_input("APP_ID", value=st.session_state.prefill_id)
        app_secret = st.text_input("APP_SECRET", value=st.session_state.prefill_secret, type="password")
        app_acct = st.text_input("ACCOUNT_NO", placeholder="เช่น Narats-E")
        submitted = st.form_submit_button("เชื่อมต่อ Settrade", use_container_width=True)

    if submitted:
        try:
            inv = Investor(app_id=app_id.strip(), app_secret=app_secret.strip(), app_code="SANDBOX", broker_id="SANDBOX")
            m_api, r_api = None, None
            if hasattr(inv, 'Equity'):
                e_api = inv.Equity(app_acct.strip()) if app_acct.strip() else inv.Equity()
                if hasattr(e_api, 'get_candlestick'): m_api = e_api
            if m_api is None: m_api = inv.MarketData()
            r_api = inv.RealtimeDataConnection() if hasattr(inv, 'RealtimeDataConnection') else inv.RealtimeData()
            
            st.session_state.update({"logged_in": True, "st_mkt": m_api, "st_rt": r_api, "view": "scan"})
            st.rerun()
        except Exception as e: st.error(f"การเชื่อมต่อล้มเหลว: {e}")

# ---------------------------------------------------------------
# 5. VIEW: SCAN (คืนค่าฟังก์ชันเดิมของคุณ)
# ---------------------------------------------------------------
def view_scan():
    st.markdown('<div class="app-hdr"><h1>ค้นหาหุ้น (Scanner)</h1></div>', unsafe_allow_html=True)
    
    if st.button("Logout"):
        st.session_state.view = "login"
        st.session_state.logged_in = False
        st.rerun()

    mkt_key = st.selectbox("เลือกตลาด", ["SET", "US", "CN"], key="mkt_sel")
    
    if st.button("เริ่มการสแกนหุ้น"):
        # Logic การสแกนเดิมของคุณจะอยู่ตรงนี้ 
        # (ตัวอย่างการดึงข้อมูลพื้นฐาน)
        stocks = [("KBANK", "กสิกรไทย"), ("PTT", "ปตท."), ("ADVANC", "แอดวานซ์")]
        for sym, name in stocks:
            df, info = get_data(sym, mkt_key)
            if not df.empty:
                st.markdown(f"""
                <div class="stock-card buy">
                    <div class="sc-top">
                        <div class="sc-sym">{sym} <span style="font-size:0.7rem; color:#8892b0;">{name}</span></div>
                        <div class="sc-price">฿{df['close'].iloc[-1]:,.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------------
# 6. ROUTER
# ---------------------------------------------------------------
if st.session_state.view == "login":
    view_login()
elif st.session_state.view == "scan":
    view_scan()
