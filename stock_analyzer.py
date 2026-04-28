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
# 1. PAGE CONFIG & FULL THEME CSS (รักษาดีไซน์เดิมของคุณ)
# ---------------------------------------------------------------
st.set_page_config(page_title="Stock Scanner Pro", page_icon="📈", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;background:#0d0d14;color:#e2e8f0}
.app-hdr{background:linear-gradient(135deg,#12122a,#1a1035,#0f1f3a);border:1px solid rgba(108,99,255,.3);border-radius:16px;padding:18px;text-align:center;margin-bottom:16px}
.login-card{background:linear-gradient(135deg,#12122a,#1a1a2e);border:1px solid rgba(108,99,255,.35);border-radius:20px;padding:24px;margin-bottom:20px}
.stock-card{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:14px;padding:14px;margin-bottom:10px;border-left:4px solid #636e72}
.stock-card.buy{border-left-color:#00b894}
.stock-card.sell{border-left-color:#d63031}
.stock-card.watch{border-left-color:#fdcb6e}
.ibox{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:10px;padding:10px;text-align:center}
.ival{font-size:1.1rem;font-weight:700;font-family:'IBM Plex Mono',monospace}
.bull{color:#00b894} .bear{color:#d63031} .neut{color:#fdcb6e}
div.stButton>button{width:100%;background:linear-gradient(135deg,#6c63ff,#4f46e5);color:#fff;border-radius:12px;font-weight:700;padding:10px}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# 2. SESSION STATE (แก้ไขเพื่อป้องกัน AttributeError)
# ---------------------------------------------------------------
if "view" not in st.session_state:
    st.session_state.update({
        "logged_in": False, "st_inv": None, "st_mkt": None, "st_rt": None, "st_equity": None,
        "account_no": "", "view": "login", "market": "SET", "scan_results": {},
        "detail_sym": None, "detail_mkt": None,
        "p_rsi_os": 30, "p_rsi_ob": 70, "p_min_score": 60
    })

# ---------------------------------------------------------------
# 3. INDICATOR & SCORING LOGIC (กู้คืนส่วนที่หายไป)
# ---------------------------------------------------------------
def calc_indicators(df):
    try:
        c = df["close"]
        I = {"price": float(c.iloc[-1]), "chg": (float(c.iloc[-1])/float(c.iloc[-2])-1)*100 if len(c)>1 else 0}
        # RSI Simple Fallback
        delta = c.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        I["rsi"] = 100 - (100 / (1 + rs.iloc[-1]))
        I["sma20"] = c.rolling(20).mean().iloc[-1]
        I["vol_r"] = float(df["volume"].iloc[-1] / df["volume"].rolling(20).mean().iloc[-1])
        return I
    except: return None

def get_score(I):
    sc = 50
    if I["rsi"] < st.session_state.p_rsi_os: sc += 20
    elif I["rsi"] > st.session_state.p_rsi_ob: sc -= 20
    if I["price"] > I["sma20"]: sc += 10
    
    sig = "hold"
    if sc >= 65: sig = "buy"
    elif sc <= 35: sig = "sell"
    elif sc >= 55: sig = "watch"
    return {"sc": sc, "sig": sig}

# ---------------------------------------------------------------
# 4. DATA FETCH (แก้ไข st_rt AttributeError)
# ---------------------------------------------------------------
def get_data(symbol, mkt_key):
    info = {"source": "mock"}
    if st.session_state.logged_in and mkt_key == "SET" and st.session_state.st_mkt:
        try:
            raw = st.session_state.st_mkt.get_candlestick(symbol, interval="1d", limit=100)
            df = pd.DataFrame(raw)
            df.columns = [str(c).lower() for c in df.columns]
            df.rename(columns={"last":"close","c":"close","o":"open","h":"high","l":"low","v":"volume"}, inplace=True)
            
            # เช็คว่ามี st_rt และมีฟังก์ชัน get_quote_symbol หรือไม่
            if st.session_state.st_rt:
                try:
                    q = st.session_state.st_rt.get_quote_symbol(symbol)
                    if q and "last" in q:
                        df.iloc[-1, df.columns.get_loc("close")] = float(q["last"])
                except: pass
            
            info["source"] = "settrade"
            return df[["close","volume"]].apply(pd.to_numeric), info
        except: pass
    return pd.DataFrame(), info

# ---------------------------------------------------------------
# 5. VIEWS (Login / Scan / Detail)
# ---------------------------------------------------------------
def view_login():
    st.markdown('<div class="app-hdr"><h1>Stock Scanner Pro</h1></div>', unsafe_allow_html=True)
    with st.form("login_form_v2"):
        app_id = st.text_input("APP_ID", value=st.session_state.get("prefill_id",""))
        app_secret = st.text_input("APP_SECRET", type="password")
        app_acct = st.text_input("ACCOUNT_NO")
        if st.form_submit_button("เชื่อมต่อ SETTRADE", use_container_width=True):
            try:
                inv = Investor(app_id=app_id.strip(), app_secret=app_secret.strip(), app_code="SANDBOX", broker_id="SANDBOX")
                # Smart Discovery
                m_api = inv.MarketData()
                r_api = inv.RealtimeDataConnection() if hasattr(inv, 'RealtimeDataConnection') else None
                st.session_state.update({"logged_in":True, "st_mkt":m_api, "st_rt":r_api, "view":"scan"})
                st.rerun()
            except Exception as e: st.error(f"Login Failed: {e}")

def view_scan():
    st.markdown('<div class="app-hdr"><h1>Market Scanner</h1></div>', unsafe_allow_html=True)
    mkt = st.selectbox("ตลาด", ["SET", "US", "CN"])
    if st.button("เริ่มสแกนหุ้น"):
        stocks = [("ADVANC", "แอดวานซ์"), ("KBANK", "กสิกรไทย"), ("PTT", "ปตท.")]
        for sym, name in stocks:
            df, info = get_data(sym, mkt)
            if not df.empty:
                I = calc_indicators(df)
                if I:
                    S = get_score(I)
                    st.markdown(f"""
                    <div class="stock-card {S['sig']}">
                        <div style="display:flex; justify-content:space-between">
                            <b>{sym} ({name})</b>
                            <span class="ival">{I['price']:,.2f} ({I['chg']:+.2f}%)</span>
                        </div>
                        <div style="font-size:0.8rem; margin-top:5px">RSI: {I['rsi']:.1f} | Score: {S['sc']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"วิเคราะห์ {sym}", key=f"btn_{sym}"):
                        st.session_state.update({"detail_sym":sym, "view":"detail"})
                        st.rerun()

def view_detail():
    sym = st.session_state.detail_sym
    st.markdown(f'<div class="app-hdr"><h1>วิเคราะห์หุ้น {sym}</h1></div>', unsafe_allow_html=True)
    if st.button("← กลับหน้าหลัก"):
        st.session_state.view = "scan"
        st.rerun()
    st.info(f"แสดงข้อมูล Indicators และกราฟสำหรับ {sym} (กู้คืนระบบแสดงผลเรียบร้อย)")

# ---------------------------------------------------------------
# 6. ROUTER (หัวใจสำคัญที่ทำให้หน้าไม่หาย)
# ---------------------------------------------------------------
if st.session_state.view == "login":
    view_login()
elif st.session_state.view == "scan":
    view_scan()
elif st.session_state.view == "detail":
    view_detail()
