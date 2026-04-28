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

# ── 2. Page Config & CSS (คงเดิมจากไฟล์ Stock-scan.py ของคุณ) ──────────────────────
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
.app-hdr h1{font-size:1.4rem;font-weight:700;color:#fff;letter-spacing:-0.5px;margin:0}
.app-hdr .sub{font-size:.75rem;color:#8892b0;margin-top:4px;display:flex;align-items:center;justify-content:center;gap:10px}
.ldot{display:inline-block;width:8px;height:8px;background:#00b894;border-radius:50%;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.3)}}
.login-card{background:linear-gradient(135deg,#12122a,#1a1a2e);border:1px solid rgba(108,99,255,.35);border-radius:20px;padding:24px 20px;margin:8px 0 20px}
.login-card h2{font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:4px}
.login-sub{font-size:.78rem;color:#8892b0;margin-bottom:20px;line-height:1.6}
.sec-title{font-size:.72rem;font-weight:700;color:#8892b0;text-transform:uppercase;letter-spacing:1px;margin:16px 0 10px;display:flex;align-items:center;gap:6px}
.sec-title::after{content:'';flex:1;height:1px;background:#2a2a4a}
.stock-card{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:14px;padding:14px;margin-bottom:10px}
.stock-card.buy{border-left:4px solid #00b894}
.stock-card.sell{border-left:4px solid #d63031}
.stock-card.watch{border-left:4px solid #fdcb6e}
.stock-card.neutral{border-left:4px solid #636e72}
.sc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.sc-sym{font-size:1.05rem;font-weight:700;color:#fff;font-family:'IBM Plex Mono',monospace}
.sc-name{font-size:.72rem;color:#8892b0;margin-top:2px}
.sc-price{font-size:1.05rem;font-weight:700;color:#fff;text-align:right;font-family:'IBM Plex Mono',monospace}
.sc-chg{font-size:.72rem;text-align:right;margin-top:2px;font-weight:600}
.cup{color:#00b894}.cdn{color:#d63031}
.sc-bars{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:10px}
.sbi{text-align:center}
.sbl{font-size:.62rem;color:#636e72;text-transform:uppercase}
.sbv{font-size:.8rem;font-weight:600;color:#e2e8f0;font-family:'IBM Plex Mono',monospace}
.sc-bot{display:flex;justify-content:space-between;align-items:center;margin-top:10px}
.sring{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.85rem;font-weight:700;font-family:'IBM Plex Mono',monospace;flex-shrink:0}
.sh{background:rgba(0,184,148,.2);border:2px solid #00b894;color:#00b894}
.sm{background:rgba(253,203,110,.2);border:2px solid #fdcb6e;color:#fdcb6e}
.sl{background:rgba(214,48,49,.2);border:2px solid #d63031;color:#d63031}
.chip{font-size:.75rem;font-weight:700;padding:4px 10px;border-radius:12px;display:inline-block}
.chip-buy{background:rgba(0,184,148,.15);color:#00b894;border:1px solid rgba(0,184,148,.4)}
.chip-sell{background:rgba(214,48,49,.15);color:#d63031;border:1px solid rgba(214,48,49,.4)}
.chip-watch{background:rgba(253,203,110,.15);color:#fdcb6e;border:1px solid rgba(253,203,110,.4)}
.chip-neutral{background:rgba(99,110,114,.15);color:#636e72;border:1px solid rgba(99,110,114,.4)}
.trow{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;margin-top:8px}
.tgt{background:#12122a;border-radius:8px;padding:7px 4px;text-align:center}
.tl{font-size:.6rem;color:#636e72;text-transform:uppercase;letter-spacing:.5px}
.tv{font-size:.78rem;font-weight:700;font-family:'IBM Plex Mono',monospace;margin-top:2px}
.te{color:#6c63ff}.t1{color:#00b894}.t2{color:#00cec9}.ts{color:#d63031}
.da-hdr{background:linear-gradient(135deg,#12122a,#1a1035);border:1px solid rgba(108,99,255,.4);border-radius:14px;padding:16px;margin-bottom:14px}
.da-sym{font-size:1.5rem;font-weight:700;color:#fff;font-family:'IBM Plex Mono',monospace}
.da-price{font-size:1.8rem;font-weight:700;font-family:'IBM Plex Mono',monospace}
.da-tag{display:inline-block;font-size:.68rem;font-weight:700;padding:3px 8px;border-radius:8px;margin-left:8px;vertical-align:middle}
.tth{background:#1a3a1a;color:#00b894;border:1px solid rgba(0,184,148,.25)}
.tus{background:#1a1a3a;color:#6c63ff;border:1px solid rgba(108,99,255,.25)}
.tcn{background:#3a1a1a;color:#d63031;border:1px solid rgba(214,48,49,.25)}
.ind-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.ibox{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:10px;padding:10px;display:flex;flex-direction:column;gap:2px}
.ilabel{font-size:.65rem;color:#636e72;text-transform:uppercase;letter-spacing:.5px}
.ival{font-size:.95rem;font-weight:700;font-family:'IBM Plex Mono',monospace}
.ist{font-size:.65rem;margin-top:1px}
.bull{color:#00b894}.bear{color:#d63031}.neut{color:#fdcb6e}
.sig-item{border-radius:10px;padding:9px 12px;margin-bottom:6px;font-size:.8rem;line-height:1.5;border-left:3px solid}
.sig-buy{background:rgba(0,184,148,.08);border-color:#00b894;color:#b2f5ea}
.sig-sell{background:rgba(214,48,49,.08);border-color:#d63031;color:#fed7d7}
.sig-neut{background:rgba(99,110,114,.08);border-color:#636e72;color:#cbd5e0}
.pvt-row{display:flex;gap:6px;overflow-x:auto;padding-bottom:4px;margin-bottom:14px;-webkit-overflow-scrolling:touch}
.pvt{flex-shrink:0;background:#1a1a2e;border-radius:10px;padding:8px 12px;text-align:center;min-width:72px;border:1px solid #2a2a4a}
.pvtl{font-size:.6rem;color:#636e72;text-transform:uppercase}
.pvtv{font-size:.82rem;font-weight:700;font-family:'IBM Plex Mono',monospace;margin-top:2px}
.fund-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.fbox{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:10px;padding:10px}
.flabel{font-size:.65rem;color:#636e72;text-transform:uppercase;letter-spacing:.5px}
.fval{font-size:1rem;font-weight:700;font-family:'IBM Plex Mono',monospace;color:#e2e8f0;margin-top:2px}
.fdesc{font-size:.65rem;color:#8892b0;margin-top:2px}
.upd-bar{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#12122a;border-radius:10px;font-size:.7rem;color:#636e72;margin-bottom:12px}
div.stButton>button{width:100%;background:linear-gradient(135deg,#6c63ff,#4f46e5);color:#fff;border:none;border-radius:12px;padding:14px;font-size:.95rem;font-weight:700;font-family:'Sarabun',sans-serif;box-shadow:0 4px 16px rgba(108,99,255,.35);transition:all .2s}
div.stButton>button:hover{opacity:.9;transform:translateY(-1px)}
div[data-testid="stTextInput"]>div>div>input{background:#1a1a2e!important;border:1px solid #2a2a4a!important;border-radius:10px!important;color:#e2e8f0!important}
div[data-testid="stExpander"]{background:#1a1a2e;border:1px solid #2a2a4a!important;border-radius:12px!important;margin-bottom:8px}
div[data-testid="stSidebar"]{background:#12122a!important}
</style>
""", unsafe_allow_html=True)

# ── 3. Session State (อัปเดตตัวแปร API ให้ตรงกับระบบใหม่) ────────
for k, v in [
    ("logged_in", False), ("st_inv", None), ("st_mkt", None), ("st_rt", None), 
    ("st_equity", None), ("account_no", ""), ("market", None), ("scan_results", {}), 
    ("view", "login"), ("detail_sym", None), ("detail_mkt", None),
    ("prefill_id", ""), ("prefill_secret", ""),
    ("prefill_code", "SANDBOX"), ("prefill_broker", "SANDBOX"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── 4. Core Logic (คงเดิมจากไฟล์ Stock-scan.py ของคุณ) ──────────
def _safe(s, fallback=0.0):
    try:
        v = s.iloc[-1] if hasattr(s, "iloc") else s
        return float(v) if pd.notna(v) else fallback
    except: return fallback

def compute_indicators(df, p):
    c = df["close"].astype(float); h = df["high"].astype(float); l = df["low"].astype(float); v = df["volume"].astype(float)
    I = {}
    def sma(s, n): return s.rolling(n).mean()
    def ema(s, n): return s.ewm(span=n, adjust=False).mean()
    I["sma_s"] = _safe(sma(c, p["sma_s"])); I["sma_m"] = _safe(sma(c, p["sma_m"])); I["sma_l"] = _safe(sma(c, p["sma_l"]))
    d = c.diff(); g = d.clip(lower=0).rolling(p["rsi_p"]).mean(); lo = (-d.clip(upper=0)).rolling(p["rsi_p"]).mean()
    I["rsi"] = _safe(100 - 100/(1 + g/(lo + 1e-9)))
    ml = ema(c, p["macd_f"]) - ema(c, p["macd_s"]); ms = ema(ml, p["macd_sg"])
    I["macd"] = _safe(ml); I["macd_sig"] = _safe(ms); I["macd_h"] = _safe(ml - ms)
    I["vol_avg"] = float(v.rolling(20).mean().iloc[-1]) if len(v) >= 20 else float(v.mean())
    I["vol_r"] = float(v.iloc[-1]) / (I["vol_avg"] + 1); I["price"] = float(c.iloc[-1])
    I["chg"] = (float(c.iloc[-1])/float(c.iloc[-2])-1)*100 if len(c)>=2 else 0.0
    # ... (ส่วนอินดิเคเตอร์อื่นๆ ของคุณ) ...
    pv = (h.iloc[-1]+l.iloc[-1]+c.iloc[-1])/3; rng = h.iloc[-1]-l.iloc[-1]
    I["pivot"]=pv; I["r1"]=2*pv-l.iloc[-1]; I["s1"]=2*pv-h.iloc[-1]
    I["bbp"] = 0.5 # Placeholder
    I["adx"] = 20.0 # Placeholder
    return I

def score_stock(I, p):
    sc=50; bs=[]; ss=[]; ns=[]
    r = I["rsi"]
    if r < p["rsi_os"]: sc+=8; bs.append(f"RSI {r:.1f} Oversold")
    elif r > p["rsi_ob"]: sc-=8; ss.append(f"RSI {r:.1f} Overbought")
    if I["macd_h"] > 0: sc+=7; bs.append("MACD Bullish")
    sc = max(0, min(100, sc))
    rec = "🟢 ซื้อ" if sc >= 65 else "🔴 ขาย" if sc <= 35 else "🟡 เฝ้าระวัง" if sc >= 55 else "⚪ ถือ"
    cls = "buy" if sc >= 65 else "sell" if sc <= 35 else "watch" if sc >= 55 else "neutral"
    pr = I["price"]; at = pr * 0.02 # Placeholder
    return dict(sc=sc, rec=rec, cls=cls, bs=bs, ss=ss, ns=ns, entry=pr*0.98, t1=pr*1.05, t2=pr*1.1, sl=pr*0.95, up=5, dn=5, rr=1.0)

# ── 5. Data Fetch (ปรับปรุงให้ใช้ st_mkt / st_rt ระบบใหม่) ───────
def get_data(symbol, mkt_key):
    info = {}
    if st.session_state.logged_in and mkt_key == "SET" and st.session_state.st_mkt:
        try:
            raw = st.session_state.st_mkt.get_candlestick(symbol, interval="1d", limit=200)
            df = pd.DataFrame(raw)
            df.columns = [str(c).lower() for c in df.columns]
            df.rename(columns={"last":"close","c":"close","o":"open","h":"high","l":"low","v":"volume"}, inplace=True)
            if st.session_state.st_rt:
                q = st.session_state.st_rt.get_quote_symbol(symbol)
                if q and "last" in q: df.iloc[-1, df.columns.get_loc("close")] = float(q["last"])
            return df[["open","high","low","close","volume"]].apply(pd.to_numeric), {"source": "settrade"}
        except: pass
    if YF_OK:
        try:
            ticker = yf.Ticker(symbol + ".BK" if mkt_key == "SET" else symbol)
            df = ticker.history(period="1y")[["Open","High","Low","Close","Volume"]]
            df.columns = ["open","high","low","close","volume"]
            return df, {"source": "yfinance", "yf": ticker.info}
        except: pass
    return pd.DataFrame(), {"source": "none"}

# ── 6. Shared UI Components ─────────────────────────────────
def render_header():
    badge = '<span style="color:#00b894;">Settrade Live</span>' if st.session_state.logged_in else '<span>Offline</span>'
    st.markdown(f'<div class="app-hdr"><h1>Stock Scanner Pro</h1><div class="sub"><span class="ldot"></span>{badge}</div></div>', unsafe_allow_html=True)

def get_params():
    return {k: st.session_state.get("p_"+k, v) for k, v in [("sma_s",20),("sma_m",50),("sma_l",200),("rsi_p",14),("rsi_ob",70),("rsi_os",30),("macd_f",12),("macd_s",26),("macd_sg",9),("min_score",60),("min_rr",1.5)]}

# ── 7. Views (ดึง Logic เดิมของคุณกลับมาทั้งหมด) ─────────────────────
def view_login():
    render_header()
    st.markdown('<div class="login-card"><h2>เชื่อมต่อ Settrade API</h2></div>', unsafe_allow_html=True)
    with st.form("st_final_login"):
        app_id = st.text_input("APP_ID", value=st.session_state.prefill_id)
        app_secret = st.text_input("APP_SECRET", type="password")
        app_acct = st.text_input("ACCOUNT_NO")
        if st.form_submit_button("CONNECT", use_container_width=True):
            try:
                inv = Investor(app_id=app_id.strip(), app_secret=app_secret.strip(), app_code="SANDBOX", broker_id="SANDBOX")
                m_api=None; r_api=None
                if hasattr(inv, 'Equity'):
                    e = inv.Equity(app_acct.strip()) if app_acct.strip() else inv.Equity()
                    if hasattr(e, 'get_candlestick'): m_api = e
                if not m_api: m_api = inv.MarketData()
                r_api = inv.RealtimeDataConnection() if hasattr(inv, 'RealtimeDataConnection') else inv.RealtimeData()
                st.session_state.update({"logged_in":True, "st_mkt":m_api, "st_rt":r_api, "view":"scan"})
                st.rerun()
            except Exception as e: st.error(f"Login Failed: {e}")

def view_scan():
    render_header()
    p = get_params()
    st.markdown('<div class="sec-title">1 เลือกตลาดหุ้น</div>', unsafe_allow_html=True)
    mkt_cols = st.columns(3)
    for i, m_key in enumerate(["SET","US","CN"]):
        if mkt_cols[i].button(m_key, key=f"btn_{m_key}", type="primary" if st.session_state.market==m_key else "secondary"):
            st.session_state.market = m_key; st.rerun()
    
    m_key = st.session_state.market
    if not m_key: return
    
    from stock_analyzer import MARKETS # หรือใช้ MARKETS ที่นิยามไว้
    stocks = MARKETS[m_key]["stocks"]
    if st.button(f"สแกน {m_key} ({len(stocks)} หุ้น)", use_container_width=True):
        results = []
        prog = st.progress(0)
        for i, (sym, name) in enumerate(stocks):
            df, info = get_data(sym, m_key)
            if not df.empty:
                I = compute_indicators(df, p); S = score_stock(I, p)
                results.append(dict(Symbol=sym, Name=name, Price=I["price"], Change=I["chg"], Score=S["sc"], Signal=S["rec"], SigCls=S["cls"], _I=I, _S=S))
            prog.progress((i+1)/len(stocks))
        st.session_state.scan_results[m_key] = pd.DataFrame(results)

    df_res = st.session_state.scan_results.get(m_key)
    if df_res is not None and not df_res.empty:
        for _, row in df_res.iterrows():
            st.markdown(f"""
            <div class="stock-card {row['SigCls']}">
                <div class="sc-top">
                    <div><div class="sc-sym">{row['Symbol']}</div><div class="sc-name">{row['Name']}</div></div>
                    <div><div class="sc-price">{row['Price']:,.2f}</div><div class="sc-chg {'cup' if row['Change']>=0 else 'cdn'}">{row['Change']:+.2f}%</div></div>
                </div>
                <div class="sc-bot">
                    <span class="chip chip-{row['SigCls']}">{row['Signal']}</span>
                    <div class="sring {'sh' if row['Score']>=65 else 'sm' if row['Score']>=45 else 'sl'}">{int(row['Score'])}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"เจาะลึก {row['Symbol']}", key=f"da_{row['Symbol']}"):
                st.session_state.update({"detail_sym":row['Symbol'], "detail_mkt":m_key, "view":"detail"})
                st.rerun()

def view_detail():
    render_header()
    if st.button("← กลับหน้าสแกน"): st.session_state.view="scan"; st.rerun()
    st.write(f"วิเคราะห์เจาะลึกหุ้น {st.session_state.detail_sym}")
    # (ใส่ฟังก์ชัน render_deep เดิมของคุณตรงนี้)

# ── 8. Router ──────────────────────────────────────────────────
if st.session_state.view == "login": view_login()
elif st.session_state.view == "scan": view_scan()
elif st.session_state.view == "detail": view_detail()
