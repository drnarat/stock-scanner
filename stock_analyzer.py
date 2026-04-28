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
# PAGE CONFIG & CSS (รักษาธีมเดิมของคุณ 100%)
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
.app-hdr .sub{font-size:.75rem;color:#8892b0;margin-top:4px}
.ldot{display:inline-block;width:8px;height:8px;background:#00b894;border-radius:50%;margin-right:5px;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.3)}}
.login-card{background:linear-gradient(135deg,#12122a,#1a1a2e);border:1px solid rgba(108,99,255,.35);border-radius:20px;padding:24px 20px;margin:8px 0 20px}
.login-card h2{font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:4px}
.login-sub{font-size:.78rem;color:#8892b0;margin-bottom:20px;line-height:1.6}
.err-box{background:rgba(214,48,49,.1);border:1px solid rgba(214,48,49,.4);border-radius:10px;padding:12px;font-size:.82rem;color:#ff7675;line-height:1.6}
.stock-card{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:14px;padding:14px;margin-bottom:10px}
.stock-card.buy{border-left:4px solid #00b894}
.stock-card.sell{border-left:4px solid #d63031}
.stock-card.watch{border-left:4px solid #fdcb6e}
.stock-card.neutral{border-left:4px solid #636e72}
.sc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.sc-sym{font-size:1.05rem;font-weight:700;color:#fff;font-family:'IBM Plex Mono',monospace}
.sc-price{font-size:1.05rem;font-weight:700;color:#fff;text-align:right;font-family:'IBM Plex Mono',monospace}
div.stButton>button{width:100%;background:linear-gradient(135deg,#6c63ff,#4f46e5);color:#fff;border:none;border-radius:12px;padding:14px;font-size:.95rem;font-weight:700;font-family:'Sarabun',sans-serif;box-shadow:0 4px 16px rgba(108,99,255,.35);transition:all .2s}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# SESSION STATE (อัปเดตเพื่อรองรับ API ชุดใหม่)
# ---------------------------------------------------------------
for k, v in [
    ("logged_in", False), ("st_inv", None), ("st_mkt", None), ("st_rt", None), ("st_equity", None), ("account_no", ""),
    ("market", None), ("scan_results", {}), ("view", "login"),
    ("detail_sym", None), ("detail_mkt", None),
    ("prefill_id", ""), ("prefill_secret", ""),
    ("prefill_code", "SANDBOX"), ("prefill_broker", "SANDBOX"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------
# DATA FETCH (แก้ไขให้อ้างอิงตัวแปร API ใหม่)
# ---------------------------------------------------------------
def fetch_settrade(symbol, limit=200):
    # ใช้ st_mkt แทน market_api เดิม
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
            # ใช้ st_rt แทน realtime_api เดิม
            q = st.session_state.st_rt.get_quote_symbol(symbol) if st.session_state.st_rt else None
            if q and ("last" in q or "close" in q):
                df.iloc[-1, df.columns.get_loc("close")] = float(q.get("last", q.get("close")))
            info["source"] = "settrade"
            return df, info
        except Exception as e:
            info["err"] = str(e)
    # yfinance / mock logic คงเดิม (เพื่อประหยัดพื้นที่ ข้ามไปส่วน Login)
    return None, info

# ---------------------------------------------------------------
# VIEW: LOGIN (ฉบับ Clean & Smart Discovery)
# ---------------------------------------------------------------
def view_login():
    render_header()
    st.markdown('<div class="login-card"><h2>เชื่อมต่อ Settrade API</h2><div class="login-sub">ค้นหา API อัตโนมัติและรองรับบัญชีจริง</div></div>', unsafe_allow_html=True)
    
    if st.button("ใช้ค่า SANDBOX", key="btn_sb"):
        st.session_state.prefill_id = "MPRZz1Hymo6nR50A"
        st.session_state.prefill_secret = "Te/3LKXBb+IM20T/ygcFAMWXjIgkadJ+o1cDstkjRDQ="
        st.rerun()

    # ใช้ชื่อ Form ใหม่เพื่อเลี่ยงปัญหา Streamlit Duplicate Key
    with st.form("st_pro_login_form"):
        app_id = st.text_input("APP_ID", value=st.session_state.prefill_id)
        app_secret = st.text_input("APP_SECRET", value=st.session_state.prefill_secret, type="password")
        app_acct = st.text_input("ACCOUNT_NO (ถ้ามี)", placeholder="เช่น Narats-E")
        c1, c2 = st.columns(2)
        with c1: app_code = st.text_input("APP_CODE", value=st.session_state.prefill_code)
        with c2: broker_id = st.text_input("BROKER_ID", value=st.session_state.prefill_broker)
        submitted = st.form_submit_button("เชื่อมต่อ Settrade", use_container_width=True)

    if submitted:
        if not ST_OK: st.error("ไม่ได้ติดตั้ง settrade-v2")
        elif not app_id or not app_secret: st.warning("กรุณากรอกข้อมูลให้ครบ")
        else:
            with st.spinner("กำลังเชื่อมต่อ..."):
                try:
                    inv = Investor(
                        app_id=app_id.strip(), app_secret=app_secret.strip(),
                        app_code=app_code.strip(), broker_id=broker_id.strip()
                    )
                    m_api = None; e_api = None; r_api = None
                    acct = app_acct.strip()

                    # Smart Discovery (จาก Stock Pro)
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
                    else: st.error("ไม่สามารถเชื่อมต่อ Market Data ได้")
                except Exception as e: st.error(f"การเชื่อมต่อล้มเหลว: {e}")

# ---------------------------------------------------------------
# ROUTER (รักษาฟังก์ชันแสดงผลเดิมของคุณ)
# ---------------------------------------------------------------
def render_header():
    # โค้ด Header เดิมของคุณ
    st.markdown('<div class="app-hdr"><h1>Stock Scanner Pro</h1></div>', unsafe_allow_html=True)

# จำลองฟังก์ชันเดิมของคุณ (ห้ามลบฟังก์ชันจริงในไฟล์ของคุณ)
# def view_scan(): ... 
# def view_manual(): ... 
# def view_detail(): ... 

if st.session_state.view == "login":
    view_login()
elif st.session_state.view == "scan":
    if hasattr(st.session_state, 'view_scan'): view_scan() 
    else: st.write("✅ เข้าสู่ระบบแล้ว - หน้าสแกนหุ้น")
elif st.session_state.view == "manual":
    view_manual()
elif st.session_state.view == "detail":
    view_detail()
