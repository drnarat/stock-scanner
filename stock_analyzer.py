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
.login-sub{font-size:.78rem;color:#8892b0;margin-bottom:20px}
div.stButton>button{width:100%;background:linear-gradient(135deg,#6c63ff,#4f46e5);color:#fff;border:none;border-radius:12px;padding:14px;font-weight:700}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# ---------------------------------------------------------------
def init_session_state():
    defaults = {
        "logged_in": False, "st_inv": None, "st_mkt": None, "st_rt": None, 
        "st_equity": None, "account_no": "", "view": "login",
        "prefill_id": "", "prefill_secret": "",
        "prefill_code": "SANDBOX", "prefill_broker": "SANDBOX",
        "scan_results": {}, "detail_sym": None, "detail_mkt": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ---------------------------------------------------------------
# 3. CORE FUNCTIONS (Data & Logic)
# ---------------------------------------------------------------
def fetch_settrade(symbol, limit=200):
    """ดึงข้อมูล Candlestick โดยใช้ API ตัวใหม่ (st_mkt)"""
    if not st.session_state.st_mkt:
        return pd.DataFrame()
    raw = st.session_state.st_mkt.get_candlestick(symbol, interval="1d", limit=limit)
    df = pd.DataFrame(raw)
    df.columns = [str(c).lower() for c in df.columns]
    df.rename(columns={"last":"close","c":"close","o":"open","h":"high","l":"low","v":"volume","vol":"volume"}, inplace=True)
    return df[["open","high","low","close","volume"]].apply(pd.to_numeric, errors="coerce").dropna()

def get_data(symbol, mkt_key):
    """ฟังก์ชันกลางสำหรับดึงข้อมูลหุ้น"""
    info = {"source": "mock"}
    if st.session_state.logged_in and mkt_key == "SET":
        try:
            df = fetch_settrade(symbol)
            # ดึงราคา Real-time (st_rt)
            if st.session_state.st_rt:
                q = st.session_state.st_rt.get_quote_symbol(symbol)
                if q and ("last" in q or "close" in q):
                    df.iloc[-1, df.columns.get_loc("close")] = float(q.get("last", q.get("close")))
            info["source"] = "settrade"
            return df, info
        except Exception as e:
            info["err"] = str(e)
    # กรณีอื่นๆ เช่น yfinance (ใส่ Logic เดิมของคุณตรงนี้)
    return pd.DataFrame(), info

# ---------------------------------------------------------------
# 4. VIEW: LOGIN
# ---------------------------------------------------------------
def view_login():
    st.markdown('<div class="app-hdr"><h1>Stock Scanner Pro</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card"><h2>เชื่อมต่อ Settrade API</h2><div class="login-sub">ค้นหา API อัตโนมัติรองรับทั้ง Sandbox และ Real Account</div></div>', unsafe_allow_html=True)
    
    if st.button("ใช้ค่า SANDBOX", key="btn_login_sb"):
        st.session_state.prefill_id = "MPRZz1Hymo6nR50A"
        st.session_state.prefill_secret = "Te/3LKXBb+IM20T/ygcFAMWXjIgkadJ+o1cDstkjRDQ="
        st.rerun()

    with st.form("st_clean_login_form"):
        app_id = st.text_input("APP_ID", value=st.session_state.prefill_id)
        app_secret = st.text_input("APP_SECRET", value=st.session_state.prefill_secret, type="password")
        app_acct = st.text_input("ACCOUNT_NO (ถ้ามี)", placeholder="เช่น Narats-E")
        c1, c2 = st.columns(2)
        with c1: app_code = st.text_input("APP_CODE", value=st.session_state.prefill_code)
        with c2: broker_id = st.text_input("BROKER_ID", value=st.session_state.prefill_broker)
        submitted = st.form_submit_button("เชื่อมต่อ Settrade", use_container_width=True)

    if submitted:
        if not ST_OK: st.error("ไม่ได้ติดตั้ง settrade-v2")
        else:
            with st.spinner("กำลังเชื่อมต่อ..."):
                try:
                    inv = Investor(
                        app_id=app_id.strip(), app_secret=app_secret.strip(),
                        app_code=app_code.strip(), broker_id=broker_id.strip()
                    )
                    m_api, e_api, r_api = None, None, None
                    acct = app_acct.strip()

                    # Smart API Discovery
                    if hasattr(inv, 'Equity'):
                        try:
                            e_api = inv.Equity(acct) if acct else inv.Equity()
                            if hasattr(e_api, 'get_candlestick'): m_api = e_api
                        except: pass
                    if m_api is None:
                        for attr in ['MarketData', 'Market']:
                            if hasattr(inv, attr):
                                try: m_api = getattr(inv, attr)(); break
                                except: pass
                    for attr in ['RealtimeDataConnection', 'Realtime']:
                        if hasattr(inv, attr):
                            try: r_api = getattr(inv, attr)(); break
                            except: pass

                    if m_api:
                        st.session_state.update({
                            "logged_in": True, "st_inv": inv, "st_mkt": m_api,
                            "st_rt": r_api, "st_equity": e_api, "account_no": acct, "view": "scan"
                        })
                        st.success("✅ เชื่อมต่อสำเร็จ!")
                        st.rerun()
                    else:
                        st.error("ไม่สามารถเชื่อมต่อ Market Data ได้")
                except Exception as e:
                    st.error(f"Error: {e}")

# ---------------------------------------------------------------
# 5. ROUTER & VIEWS (เชื่อมต่อหน้าเดิม)
# ---------------------------------------------------------------
def view_scan():
    # โค้ดหน้าสแกนเดิมของคุณ
    st.markdown('<div class="app-hdr"><h1>หน้าสแกนหุ้น</h1></div>', unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.view = "login"
        st.rerun()
    st.info("กำลังเรียกใช้ฟังก์ชันสแกนหุ้นเดิมของคุณ...")
    # ที่นี่คือจุดที่คุณต้องวางเนื้อหาของฟังก์ชัน view_scan() เดิมที่มีอยู่

# ส่วนควบคุมการเปลี่ยนหน้า
if st.session_state.view == "login":
    view_login()
elif st.session_state.view == "scan":
    view_scan()
# เพิ่ม elif สำหรับ "manual" และ "detail" ตามฟังก์ชันเดิมของคุณ

st.markdown('<div style="text-align:center;padding:20px;color:#2a2a4a;font-size:.7rem;">Stock Scanner Pro - Clean Version</div>', unsafe_allow_html=True)
