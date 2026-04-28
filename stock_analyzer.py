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
# CSS (แก้ไขจุดที่ String ตกหล่นให้แล้ว)
# ---------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;background:#0d0d14;color:#e2e8f0}
footer{visibility:hidden}#MainMenu{visibility:hidden}
header[data-testid="stHeader"]{background:#0d0d14!important}
.app-hdr{background:linear-gradient(135deg,#12122a,#1a1035,#0f1f3a);border:1px solid rgba(108,99,255,.3);border-radius:16px;padding:18px 16px 14px;text-align:center;margin-bottom:16px}
.app-hdr h1{font-size:1.4rem;font-weight:700;color:#fff}
.app-hdr .sub{font-size:.75rem;color:#8892b0;margin-top:4px}
.ldot{display:inline-block;width:8px;height:8px;background:#00b894;border-radius:50%;margin-right:5px;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.3)}}
.login-card{background:linear-gradient(135deg,#12122a,#1a1a2e);border:1px solid rgba(108,99,255,.35);border-radius:20px;padding:24px 20px;margin:8px 0 20px}
.login-card h2{font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:4px}
.login-sub{font-size:.78rem;color:#8892b0;margin-bottom:20px;line-height:1.6}
.err-box{background:rgba(214,48,49,.1);border:1px solid rgba(214,48,49,.4);border-radius:10px;padding:12px;font-size:.82rem;color:#ff7675;line-height:1.6}
div.stButton>button{width:100%;background:linear-gradient(135deg,#6c63ff,#4f46e5);color:#fff;border:none;border-radius:12px;padding:14px;font-size:.95rem;font-weight:700;font-family:'Sarabun',sans-serif;box-shadow:0 4px 16px rgba(108,99,255,.35);transition:all .2s}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# SESSION STATE (แก้ไขโครงสร้างตาม Stock Pro)
# ---------------------------------------------------------------
for k, v in [
    ("logged_in", False), ("st_inv", None), ("st_mkt", None), ("st_rt", None), 
    ("st_equity", None), ("account_no", ""), ("market", None), ("scan_results", {}), 
    ("view", "login"), ("detail_sym", None), ("detail_mkt", None),
    ("prefill_id", ""), ("prefill_secret", ""),
    ("prefill_code", "SANDBOX"), ("prefill_broker", "SANDBOX"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------
# DATA FETCH (แก้ไขให้ดึงจาก st_mkt / st_rt ตัวใหม่)
# ---------------------------------------------------------------
def fetch_settrade(symbol, limit=200):
    # เรียกผ่าน st_mkt ที่ดึงมาตอน Login
    raw = st.session_state.st_mkt.get_candlestick(symbol, interval="1d", limit=limit)
    df = pd.DataFrame(raw)
    df.columns = [str(c).lower() for c in df.columns]
    rename = {"last":"close","c":"close","o":"open","h":"high","l":"low","v":"volume","vol":"volume"}
    df.rename(columns=rename, inplace=True)
    df = df[["open","high","low","close","volume"]].apply(pd.to_numeric, errors="coerce").dropna()
    return df

def get_data(symbol, mkt_key):
    info = {}
    if st.session_state.logged_in and mkt_key == "SET":
        try:
            df = fetch_settrade(symbol)
            # เรียก Real-time Quote ผ่าน st_rt
            q = st.session_state.st_rt.get_quote_symbol(symbol) if st.session_state.st_rt else None
            if q and ("last" in q or "close" in q):
                df.iloc[-1, df.columns.get_loc("close")] = float(q.get("last", q.get("close")))
            info["source"] = "settrade"
            return df, info
        except Exception as e:
            info["err"] = str(e)
    # ... (ส่วน yfinance และ mock คงเดิม) ...
    return None, info

# ---------------------------------------------------------------
# VIEW: LOGIN (ฉบับแก้ไขเลียนแบบ Stock Pro)
# ---------------------------------------------------------------
def view_login():
    st.markdown('<div class="app-hdr"><h1>Stock Scanner Pro</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card"><h2>เชื่อมต่อ Settrade API</h2><div class="login-sub">ระบบจะค้นหา API Discovery อัตโนมัติเหมือน Stock Pro</div></div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        app_id = st.text_input("APP_ID", value=st.session_state.prefill_id)
        app_secret = st.text_input("APP_SECRET", value=st.session_state.prefill_secret, type="password")
        app_acct = st.text_input("ACCOUNT_NO (ถ้ามี)", placeholder="เช่น Narats-E")
        c1, c2 = st.columns(2)
        with c1: app_code = st.text_input("APP_CODE", value="SANDBOX")
        with c2: broker_id = st.text_input("BROKER_ID", value="SANDBOX")
        submitted = st.form_submit_button("เชื่อมต่อ Settrade")

    if submitted:
        if not ST_OK: st.error("ไม่ได้ติดตั้ง settrade-v2")
        else:
            with st.spinner("กำลังเชื่อมต่อ..."):
                try:
                    inv = Investor(
                        app_id=app_id.strip(), app_secret=app_secret.strip(),
                        app_code=app_code.strip(), broker_id=broker_id.strip()
                    )
                    m_api = None; e_api = None; r_api = None
                    acct = app_acct.strip()

                    # Logic การค้นหา API (จาก Stock Pro)
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
                        st.session_state.update({"logged_in":True, "st_inv":inv, "st_mkt":m_api, 
                                               "st_rt":r_api, "st_equity":e_api, "view":"scan"})
                        st.success("✅ เชื่อมต่อสำเร็จ!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ---------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------
if st.session_state.view == "login":
    view_login()
elif st.session_state.view == "scan":
    # เรียกฟังก์ชันสแกนเดิมของคุณ
    st.write("Login สำเร็จ - เข้าสู่หน้าสแกน")
