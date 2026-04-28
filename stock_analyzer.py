# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

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
# PAGE CONFIG
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Stock Scanner Pro",
    page_icon=":chart_with_upwards_trend:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------
# CSS (คงเดิม)
# ---------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;background:#0d0d1a;color:#e2e8f0}
.stApp{background:radial-gradient(circle at 50% 0%, #1a1a3a 0%, #0d0d1a 100%)}
[data-testid="stHeader"]{background:transparent}
.main-header{text-align:center;padding:2rem 0 1rem;background:linear-gradient(90deg, #6366f1, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.5rem;letter-spacing:-1px}
.login-card{background:rgba(30,30,60,0.6);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:30px;backdrop-filter:blur(10px);margin-bottom:20px}
.login-card h2{margin-bottom:10px;font-weight:700;color:#fff}
.login-sub{color:#94a3b8;font-size:0.9rem;margin-bottom:20px}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# SESSION STATE (แก้ไข: เพิ่ม st_inv, st_mkt, st_rt, st_equity)
# ---------------------------------------------------------------
for k, v in [
    ("logged_in", False), ("st_inv", None), ("st_mkt", None), ("st_rt", None), 
    ("st_equity", None), ("account_no", ""),
    ("market", None), ("scan_results", {}), ("view", "login"),
    ("detail_sym", None), ("detail_mkt", None),
    ("prefill_id", ""), ("prefill_secret", ""),
    ("prefill_code", "SANDBOX"), ("prefill_broker", "SANDBOX"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------
# HELPERS & DATA FETCHING (แก้ไข: เปลี่ยนชื่อตัวแปร API)
# ---------------------------------------------------------------
def fetch_settrade(symbol, limit=100):
    if not st.session_state.st_mkt: return None
    try:
        # ใช้ st_mkt ที่ได้จากการ discovery ในขั้นตอน login
        raw = st.session_state.st_mkt.get_candlestick(symbol, interval="1d", limit=limit)
        df = pd.DataFrame(raw)
        df['time'] = pd.to_datetime(df['last_sequence'])
        df.rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'}, inplace=True)
        return df.sort_values('time').reset_index(drop=True)
    except Exception as e:
        st.error(f"Settrade Error ({symbol}): {e}")
        return None

def fetch_yfinance(symbol):
    if not YF_OK: return None, None
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="6mo")
        return df, t.info
    except Exception: return None, None

def get_data(symbol, market_key="SET"):
    if market_key == "SET" and st.session_state.logged_in:
        df = fetch_settrade(symbol)
        q = None
        if st.session_state.st_rt:
            try: q = st.session_state.st_rt.get_quote_symbol(symbol)
            except: pass
        return df, {"source": "settrade", "quote": q}
    else:
        df, info = fetch_yfinance(symbol)
        return df, {"source": "yfinance", "yf": info}

# ---------------------------------------------------------------
# LOGIN VIEW (แก้ไข: ยกโครงสร้าง Discovery มาจาก Stock Pro)
# ---------------------------------------------------------------
def render_header():
    st.markdown('<h1 class="main-header">STOCK SCANNER PRO</h1>', unsafe_allow_html=True)

def view_login():
    render_header()
    
    st_ok = "OK" if ST_OK else "ยังไม่ติดตั้ง"
    st.info(f"สถานะ Library: settrade-v2 ({st_ok})")

    st.markdown("""
    <div class="login-card">
        <h2>เชื่อมต่อ Settrade API</h2>
        <div class="login-sub">กรอก credential เพื่อใช้งานข้อมูล Real-time</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        app_id = st.text_input("APP_ID", value=st.session_state.prefill_id)
        app_secret = st.text_input("APP_SECRET", value=st.session_state.prefill_secret, type="password")
        app_acct = st.text_input("ACCOUNT_NO (ถ้ามี)", placeholder="เช่น Narats-E")
        c1, c2 = st.columns(2)
        with c1: app_code = st.text_input("APP_CODE", value=st.session_state.prefill_code)
        with c2: broker_id = st.text_input("BROKER_ID", value=st.session_state.prefill_broker)
        submitted = st.form_submit_button("เชื่อมต่อ Settrade", use_container_width=True)

    if submitted:
        if not ST_OK:
            st.error("กรุณาติดตั้ง settrade-v2 ก่อน")
        elif not app_id or not app_secret:
            st.warning("กรุณากรอก APP_ID และ APP_SECRET")
        else:
            with st.spinner("กำลังเชื่อมต่อ Settrade..."):
                try:
                    inv = Investor(
                        app_id=app_id.strip(),
                        app_secret=app_secret.strip(),
                        app_code=app_code.strip() if app_code.strip() else "SANDBOX",
                        broker_id=broker_id.strip() if broker_id.strip() else "SANDBOX",
                    )
                    
                    # --- Discovery Logic (เหมือน Stock Pro) ---
                    m_api = None; e_api = None; r_api = None
                    acct = app_acct.strip()

                    # 1. ลองดึงจาก Equity API (ดีที่สุด)
                    if hasattr(inv, 'Equity'):
                        try:
                            e_api = inv.Equity(acct) if acct else inv.Equity()
                            if hasattr(e_api, 'get_candlestick'): m_api = e_api
                        except: pass
                    
                    # 2. ถ้ายังไม่มี m_api ให้ลอง MarketData
                    if m_api is None:
                        for attr in ['MarketData', 'Market']:
                            if hasattr(inv, attr):
                                try:
                                    m_api = getattr(inv, attr)()
                                    break
                                except: pass

                    # 3. ดึง Realtime API
                    for attr in ['RealtimeDataConnection', 'Realtime']:
                        if hasattr(inv, attr):
                            try:
                                r_api = getattr(inv, attr)()
                                break
                            except: pass

                    if m_api:
                        st.session_state.update({
                            "logged_in": True,
                            "st_inv": inv,
                            "st_mkt": m_api,
                            "st_rt": r_api,
                            "st_equity": e_api,
                            "account_no": acct,
                            "view": "scan"
                        })
                        st.success("✅ เชื่อมต่อสำเร็จ!")
                        st.rerun()
                    else:
                        st.error("ไม่สามารถดึงข้อมูล Market Data ได้")
                except Exception as e:
                    st.error(f"การเชื่อมต่อล้มเหลว: {e}")

    if st.button("ข้ามไปใช้ข้อมูลจำลอง (Mock Data)"):
        st.session_state.view = "scan"
        st.rerun()

# (ส่วนอื่นๆ ของโปรแกรม เช่น compute_indicators, score_stock ให้คงเดิมตามไฟล์ Stock-scan.py ของคุณ)
# ---------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------
if st.session_state.view == "login":
    view_login()
else:
    # ใส่ส่วน Logic การ Scan หุ้นของคุณที่นี่
    st.write("เข้าสู่ระบบสำเร็จ กำลังแสดงหน้า Scan...")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.view = "login"
        st.rerun()
