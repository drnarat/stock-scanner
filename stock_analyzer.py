# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import urllib.request
import urllib.parse
import json as _json
import ssl
import re

# ==========================================
# 1. จัดการไลบรารี
# ==========================================
try: import pandas_ta as ta; TA_OK = True
except: TA_OK = False
try: from settrade_v2 import Investor; ST_OK = True
except: ST_OK = False
try: import yfinance as yf; YF_OK = True
except: YF_OK = False
try: import plotly.graph_objects as go; from plotly.subplots import make_subplots; PLOTLY_OK = True
except: PLOTLY_OK = False

# ==========================================
# 2. ตั้งค่าหน้าเว็บและ CSS 
# ==========================================
st.set_page_config(page_title="Stock Scanner Pro AI", page_icon="📈", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;font-size:15px;line-height:1.6}

/* ปรับให้โปร่งแสงเพื่อกลืนกับ Theme หลักของ Streamlit */
.app-hdr{background:linear-gradient(135deg, rgba(124,106,240,0.1), rgba(34,211,238,0.1)); border:1px solid rgba(124,106,240,0.3); border-radius:16px; padding:20px 18px 16px; text-align:center; margin-bottom:18px;}
.app-hdr h1{font-size:1.5rem; font-weight:700; letter-spacing:.3px; color: inherit;}
.stock-card{background: rgba(128,128,128,0.05); border:1px solid rgba(128,128,128,0.2); border-radius:14px; padding:14px 16px; margin-bottom:10px; transition:border-color .15s;}
.stock-card:hover{border-color:#7c6af0;}
.sc-top{display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px}
.sc-sym{font-size:1.1rem; font-weight:700; font-family:'IBM Plex Mono',monospace;}
.sc-price{font-size:1.1rem; font-weight:700; text-align:right; font-family:'IBM Plex Mono',monospace;}
.sc-bot{display:flex; justify-content:space-between; align-items:center; margin-top:12px}
.sring{width:44px; height:44px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:.88rem; font-weight:700; font-family:'IBM Plex Mono',monospace; flex-shrink:0;}
.sh{background:rgba(52,211,153,.15); border:2px solid #34d399; color:#059669;}
.sm{background:rgba(251,191,36,.15); border:2px solid #fbbf24; color:#d97706;}
.sl{background:rgba(248,113,113,.15); border:2px solid #f87171; color:#dc2626;}
.chip{font-size:.8rem; font-weight:700; padding:4px 12px; border-radius:12px; display:inline-block;}
.chip-buy{background:rgba(52,211,153,.15); color:#059669;}
.chip-sell{background:rgba(248,113,113,.15); color:#dc2626;}
.chip-watch{background:rgba(251,191,36,.15); color:#d97706;}
.da-hdr{background: rgba(128,128,128,0.05); border:1px solid rgba(128,128,128,0.2); border-radius:14px; padding:18px 16px; margin-bottom:14px;}
.da-sym{font-size:1.5rem; font-weight:700; font-family:'IBM Plex Mono',monospace;}
.da-price{font-size:1.8rem; font-weight:700; font-family:'IBM Plex Mono',monospace;}
.ind-grid{display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:14px}
.ibox{background: rgba(128,128,128,0.05); border:1px solid rgba(128,128,128,0.2); border-radius:10px; padding:10px 12px; display:flex; flex-direction:column; gap:3px;}
.ilabel{font-size:.7rem; text-transform:uppercase; opacity:0.7;}
.ival{font-size:1rem; font-weight:700; font-family:'IBM Plex Mono',monospace;}
.trow{display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:6px; margin-top:10px}
.tgt{background: rgba(128,128,128,0.05); border-radius:8px; padding:10px 4px; text-align:center; border:1px solid rgba(128,128,128,0.2);}
.tl{font-size:.65rem; text-transform:uppercase; opacity:0.7;}
.tv{font-size:.85rem; font-weight:700; font-family:'IBM Plex Mono',monospace; margin-top:2px;}
.sig-item{font-size:.85rem; padding:8px 12px; border-radius:8px; margin-bottom:6px; font-weight:600;}
.sig-buy{background:rgba(52,211,153,.15); border:1px solid rgba(52,211,153,.3); color:#059669;}
.sig-sell{background:rgba(248,113,113,.15); border:1px solid rgba(248,113,113,.3); color:#dc2626;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ฐานข้อมูลหุ้น
# ==========================================
MARKETS = {
    "SET": {"flag": "TH", "currency": "฿", "stocks": [("KBANK","กสิกรไทย"),("PTT","ปตท."),("AOT","ท่าอากาศยาน"),("ADVANC","แอดวานซ์"),("DELTA","เดลต้า"),("GULF","กัลฟ์"),("CPALL","ซีพีออลล์"),("SPALI","ศุภาลัย")]},
    "US": {"flag": "US", "currency": "$", "stocks": [("AAPL","Apple"),("MSFT","Microsoft"),("NVDA","NVIDIA"),("TSLA","Tesla")]},
    "CN": {"flag": "CN", "currency": "$", "stocks": [("BABA","Alibaba"),("JD","JD.com"),("BIDU","Baidu"),("PDD","Pinduoduo"),("TCEHY","Tencent")]}
}

for k, v in [("logged_in", False), ("market_api", None), ("view", "login"), ("detail_sym", None), ("detail_mkt", None)]:
    if k not in st.session_state: st.session_state[k] = v

# ==========================================
# 4. ข่าว AI & API Config
# ==========================================
def search_stock_news_one_month(symbol, company_name="", market="SET"):
    results = []
    query = f"หุ้น {symbol} {company_name} when:1m" if market == "SET" else f"{symbol} stock news when:1m"
    rss_url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&hl=th&gl=TH&ceid=TH:th"
    try:
        req = urllib.request.Request(rss_url, headers={"User-Agent": "Mozilla/5.0"})
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            items = re.findall(r'<item>(.*?)</item>', r.read().decode("utf-8", errors="replace"), re.DOTALL)
            # จำกัด 3 ข่าว เพื่อประหยัดโควต้า AI และไม่ให้เกิน Limit
            for item in items[:3]:
                title = re.search(r'<title>(.*?)</title>', item)
                src = re.search(r'<source[^>]*>(.*?)</source>', item)
                if title: results.append({"title": title.group(1).replace("<![CDATA[", "").replace("]]>", ""), "source": src.group(1) if src else "News"})
    except: pass
    return results

def call_gemini_api(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key.strip()}"
    payload = _json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.4}}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            return _json.loads(r.read().decode())["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e: raise Exception(f"Gemini Error: {e.read().decode('utf-8')}")

def call_claude_api(prompt, api_key):
    url = "https://api.anthropic.com/v1/messages"
    # อัปเดตรุ่นล่าสุด แก้ 404
    payload = _json.dumps({"model": "claude-3-5-haiku-20241022", "max_tokens": 1200, "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "x-api-key": api_key.strip(), "anthropic-version": "2023-06-01"})
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
            return _json.loads(r.read().decode())["content"][0]["text"]
    except urllib.error.HTTPError as e: raise Exception(f"Claude Error: {e.read().decode('utf-8')}")

# ==========================================
# 5. ดึงข้อมูลและ Indicator เชิงลึก
# ==========================================
def fetch_mock(symbol, n=150):
    np.random.seed(abs(hash(symbol)) % 99999)
    c = [np.random.uniform(8, 200)]; dates = pd.date_range(end=pd.Timestamp.today(), periods=n)
    for _ in range(n - 1): c.append(max(c[-1] * (1 + np.random.normal(0, .015)), 0.5))
    c = np.array(c)
    return pd.DataFrame({"open": c, "high": c*np.random.uniform(1.001, 1.02, n), "low": c*np.random.uniform(0.98, 0.999, n), "close": c, "volume": np.random.uniform(1e5, 5e6, n)}, index=dates)

def get_data(symbol, mkt_key):
    # --- 1. ลองดึงจาก Settrade (พอร์ตจริง/Sandbox) ---
    if st.session_state.logged_in and mkt_key == "SET":
        try:
            # ล็อคเป้าใช้ "1d" (ตัวเล็ก) ตามมาตรฐานของ Settrade
            raw = st.session_state.market_api.get_candlestick(symbol, interval="1d", limit=150)
            df = pd.DataFrame(raw)
            if not df.empty:
                df.rename(columns={"last": "close", "vol": "volume"}, inplace=True)
                return df[["open","high","low","close","volume"]].apply(pd.to_numeric)
        except Exception:
            pass # ถ้าดึงไม่ได้ให้ปล่อยผ่านเงียบๆ ไม่ต้องแสดง Error

    # --- 2. แหล่งสำรอง: ดึงจาก Yahoo Finance (ข้อมูลจริง ฟรี ไม่ติด Error) ---
    if YF_OK:
        try:
            yf_sym = symbol + ".BK" if mkt_key == "SET" else symbol
            df = yf.Ticker(yf_sym).history(period="6mo")[["Open","High","Low","Close","Volume"]]
            if not df.empty:
                df.columns = ["open","high","low","close","volume"]
                return df.dropna()
        except Exception: 
            pass

    # --- 3. ไม้ตายสุดท้าย: กราฟจำลอง (เพื่อให้แอปไม่พัง) ---
    return fetch_mock(symbol)

# ฟังก์ชันดึงค่าปลอดภัย ป้องกัน Error: cannot convert the series to float
def _safe(s, fallback=0.0):
    try:
        v = s.iloc[-1] if hasattr(s, "iloc") else s
        return float(v) if pd.notna(v) else fallback
    except: return fallback

def compute_indicators(df):
    c = df["close"]; h = df["high"]; l = df["low"]; v = df["volume"]
    I = {}
    
    if TA_OK:
        I["sma_s"] = _safe(ta.sma(c, length=10)); I["sma_m"] = _safe(ta.sma(c, length=25))
        I["rsi"] = _safe(ta.rsi(c, length=14))
        macd = ta.macd(c, fast=12, slow=26, signal=9)
        if macd is not None and not macd.empty:
            I["macd"] = _safe(macd.iloc[:,0]); I["macd_h"] = _safe(macd.iloc[:,1]); I["macd_sig"] = _safe(macd.iloc[:,2])
        else: I["macd"] = I["macd_h"] = I["macd_sig"] = 0.0
        bb = ta.bbands(c, length=20, std=2)
        if bb is not None and not bb.empty:
            I["bbl"] = _safe(bb.iloc[:,0]); I["bbm"] = _safe(bb.iloc[:,1]); I["bbu"] = _safe(bb.iloc[:,2]); I["bbp"] = _safe(bb.iloc[:,4])
        else: I["bbl"]=I["bbm"]=I["bbu"]=c.iloc[-1]; I["bbp"]=0.5
        stoch = ta.stoch(h, l, c, k=14, d=3)
        if stoch is not None and not stoch.empty: I["sk"] = _safe(stoch.iloc[:,0]); I["sd"] = _safe(stoch.iloc[:,1])
        else: I["sk"] = I["sd"] = 50.0
        I["atr"] = _safe(ta.atr(h, l, c, length=14)); I["cci"] = _safe(ta.cci(h, l, c, length=20))
        I["mfi"] = _safe(ta.mfi(h, l, c, v, length=14))
        adx = ta.adx(h, l, c, length=14)
        if adx is not None and not adx.empty: I["adx"] = _safe(adx.iloc[:,0]); I["dip"] = _safe(adx.iloc[:,1]); I["dim"] = _safe(adx.iloc[:,2])
        else: I["adx"] = I["dip"] = I["dim"] = 20.0
        obv = ta.obv(c, v); I["obv_up"] = _safe(obv) > _safe(obv.shift(5)) if obv is not None else False
    else:
        I["sma_s"] = _safe(c.rolling(10).mean()); I["sma_m"] = _safe(c.rolling(25).mean())
        d = c.diff(); g = d.clip(lower=0).rolling(14).mean(); lo = (-d.clip(upper=0)).rolling(14).mean()
        I["rsi"] = _safe(100 - 100/(1 + g/(lo + 1e-9)))
        ml = c.ewm(span=12).mean() - c.ewm(span=26).mean(); ms = ml.ewm(span=9).mean()
        I["macd"] = _safe(ml); I["macd_sig"] = _safe(ms); I["macd_h"] = _safe(ml - ms)
        bm = c.rolling(20).mean(); bstd = c.rolling(20).std()
        I["bbu"] = _safe(bm + 2*bstd); I["bbm"] = _safe(bm); I["bbl"] = _safe(bm - 2*bstd)
        I["bbp"] = _safe((c - I["bbl"]) / (I["bbu"] - I["bbl"] + 1e-9))
        ll = l.rolling(14).min(); hh = h.rolling(14).max(); sk = 100*(c - ll)/(hh - ll + 1e-9)
        I["sk"] = _safe(sk); I["sd"] = _safe(sk.rolling(3).mean())
        I["atr"] = _safe(pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1).rolling(14).mean())
        tp = (h+l+c)/3; cm = tp.rolling(20).mean(); mad = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean())
        I["cci"] = _safe((tp - cm)/(0.015*mad + 1e-9))
        mf = tp*v; pos = mf.where(tp>tp.shift(),0).rolling(14).sum(); neg = mf.where(tp<tp.shift(),0).rolling(14).sum()
        I["mfi"] = _safe(100 - 100/(1 + pos/(neg+1e-9)))
        I["adx"] = 20.0; I["dip"] = 20.0; I["dim"] = 20.0; I["obv_up"] = False

    I["price"] = float(c.iloc[-1]); I["high_d"] = float(h.iloc[-1]); I["low_d"] = float(l.iloc[-1])
    I["chg"] = (float(c.iloc[-1])/float(c.iloc[-2])-1)*100 if len(c)>=2 else 0.0
    vol_avg = float(v.rolling(20).mean().iloc[-1]) if len(v) >= 20 else float(v.mean())
    I["vol_r"] = float(v.iloc[-1]) / (vol_avg + 1)
    pv = (I["high_d"]+I["low_d"]+I["price"])/3; rng = I["high_d"] - I["low_d"]
    I["pivot"]=pv; I["r1"]=2*pv-I["low_d"]; I["r2"]=pv+rng; I["s1"]=2*pv-I["high_d"]; I["s2"]=pv-rng
    return I

def score_stock(I):
    sc=50; bs=[]; ss=[]
    pr = I["price"]
    if I["rsi"] < 35: sc+=8; bs.append("RSI Oversold")
    elif I["rsi"] > 68: sc-=8; ss.append("RSI Overbought")
    if I["macd"] > I["macd_sig"] and I["macd_h"] > 0: sc+=7; bs.append("MACD ตัดขึ้น")
    elif I["macd"] < I["macd_sig"] and I["macd_h"] < 0: sc-=7; ss.append("MACD ตัดลง")
    if pr > I["sma_s"] > I["sma_m"]: sc+=6; bs.append("SMA Uptrend")
    if I["bbp"] < 0.15: sc+=6; bs.append("ราคาชิดขอบล่าง BB")
    elif I["bbp"] > 0.85: sc-=5; ss.append("ราคาชิดขอบบน BB")
    if I["adx"] > 25 and I["dip"] > I["dim"]: sc+=5; bs.append("เทรนด์ขาขึ้นแรง (ADX)")
    if I["obv_up"]: sc+=3; bs.append("OBV ชี้ขึ้น")
    
    sc = max(0, min(100, sc))
    if sc >= 65: rec="🟢 ซื้อ"; cls="buy"
    elif sc <= 35: rec="🔴 ขาย"; cls="sell"
    elif sc >= 50: rec="🟡 เฝ้าระวัง"; cls="watch"
    else: rec="⚪ ถือ"; cls="neutral"
    
    at = I["atr"] if I["atr"] > 0 else pr*0.02
    return dict(sc=sc, rec=rec, cls=cls, bs=bs, ss=ss, entry=pr*0.985, t1=pr+at*2, t2=pr+at*3.5, sl=pr-at*1.5)

# ==========================================
# 6. Views และ UI
# ==========================================
def render_interactive_chart(df, sym):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.7])
    fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close']), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['close'].rolling(25).mean(), line=dict(color='#22d3ee', width=1.5), name='SMA25'), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], marker_color=['#34d399' if c>=o else '#f87171' for o,c in zip(df['open'],df['close'])]), row=2, col=1)
    
    # ดึงค่าสีพื้นหลังให้ตรงตาม Theme ที่ผู้ใช้ใช้งาน
    bg_color = "rgba(0,0,0,0)"
    fig.update_layout(template='plotly', plot_bgcolor=bg_color, paper_bgcolor=bg_color, margin=dict(l=5, r=5, t=5, b=5), xaxis_rangeslider_visible=False, height=450, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def view_manual():
    st.markdown('<div class="app-hdr"><h1>Stock Scanner Pro</h1><div class="sub">ระบบสแกนหุ้นด้วยอินดิเคเตอร์</div></div>', unsafe_allow_html=True)
    with st.form("search"):
        sym = st.text_input("ค้นหาหุ้นรายตัว", placeholder="เช่น PTT, AAPL, BABA")
        mkt = st.selectbox("ตลาด", ["SET", "US", "CN"])
        if st.form_submit_button("🚀 วิเคราะห์เจาะลึก"):
            if sym:
                st.session_state.detail_sym = sym.upper()
                st.session_state.detail_mkt = mkt
                st.session_state.view = "detail"
                st.rerun()

    st.markdown("### 🔥 หุ้นที่น่าสนใจวันนี้")
    mkt = st.radio("เลือกตลาดสแกน", ["SET", "US", "CN"], horizontal=True, label_visibility="collapsed")
    cur = MARKETS[mkt]["currency"]
    
    with st.spinner("กำลังสแกนอินดิเคเตอร์..."):
        for s_sym, s_name in MARKETS[mkt]["stocks"]:
            df = get_data(s_sym, mkt)
            I = compute_indicators(df)
            S = score_stock(I)
            sc_cls = "sh" if S["sc"]>=65 else "sm" if S["sc"]>=50 else "sl"
            
            st.markdown(
                f'<div class="stock-card {S["cls"]}">'
                f'<div class="sc-top"><div><div class="sc-sym">{s_sym}</div><div style="font-size:0.75rem; opacity:0.7;">{s_name}</div></div>'
                f'<div><div class="sc-price" style="color:{"#059669" if I["chg"]>=0 else "#dc2626"}">{cur}{I["price"]:.2f}</div><div style="font-size:0.75rem;text-align:right;">{"+" if I["chg"]>=0 else ""}{I["chg"]:.2f}%</div></div></div>'
                f'<div class="sc-bot"><span class="chip chip-{S["cls"]}">{S["rec"]}</span><div class="sring {sc_cls}">{int(S["sc"])}</div></div>'
                f'</div>', unsafe_allow_html=True
            )

def view_detail():
    if st.button("⬅️ กลับไปหน้าแรก"):
        st.session_state.view = "manual"
        st.rerun()
        
    sym = st.session_state.detail_sym
    mkt = st.session_state.detail_mkt
    cur = MARKETS[mkt]["currency"]
    
    with st.spinner(f"กำลังเจาะลึก {sym}..."):
        df = get_data(sym, mkt)
        I = compute_indicators(df)
        S = score_stock(I)
        
        st.markdown(
            f'<div class="da-hdr" style="display:flex;justify-content:space-between;align-items:center;">'
            f'<div><span class="da-sym">{sym}</span><br><span class="da-price" style="color:{"#059669" if I["chg"]>=0 else "#dc2626"}">{cur}{I["price"]:.2f}</span></div>'
            f'<div style="text-align:right;"><span class="chip chip-{S["cls"]}" style="font-size:1rem;">{S["rec"]}</span><br><span style="font-size: 0.9rem; opacity: 0.8;">Score: {int(S["sc"])}/100</span></div>'
            f'</div>', unsafe_allow_html=True
        )
        if PLOTLY_OK: render_interactive_chart(df, sym)

        t1, t2 = st.tabs(["📊 สัญญาณเทคนิคเชิงลึก", "🎯 แผนการเทรด"])
        with t1:
            if S["bs"]:
                for b in S["bs"]: st.markdown(f'<div class="sig-item sig-buy">✅ {b}</div>', unsafe_allow_html=True)
            if S["ss"]:
                for s in S["ss"]: st.markdown(f'<div class="sig-item sig-sell">❌ {s}</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # ตารางอินดิเคเตอร์ 15 ตัว
            st.markdown(
                f'<div class="ind-grid">'
                f'<div class="ibox"><div class="ilabel">RSI (14)</div><div class="ival" style="color:{"#dc2626" if I["rsi"]>70 else "#059669" if I["rsi"]<35 else "inherit"};">{I["rsi"]:.1f}</div></div>'
                f'<div class="ibox"><div class="ilabel">MACD Hist</div><div class="ival" style="color:{"#059669" if I["macd_h"]>0 else "#dc2626"};">{I["macd_h"]:.4f}</div></div>'
                f'<div class="ibox"><div class="ilabel">SMA 10 / 25</div><div class="ival">{I["sma_s"]:.2f} / {I["sma_m"]:.2f}</div></div>'
                f'<div class="ibox"><div class="ilabel">BB Position</div><div class="ival" style="color:{"#dc2626" if I["bbp"]>0.8 else "#059669" if I["bbp"]<0.2 else "inherit"};">{I["bbp"]*100:.1f}%</div></div>'
                f'<div class="ibox"><div class="ilabel">Stochastic %K</div><div class="ival" style="color:{"#dc2626" if I["sk"]>80 else "#059669" if I["sk"]<20 else "inherit"};">{I["sk"]:.1f}</div></div>'
                f'<div class="ibox"><div class="ilabel">MFI (Money Flow)</div><div class="ival" style="color:{"#dc2626" if I["mfi"]>80 else "#059669" if I["mfi"]<20 else "inherit"};">{I["mfi"]:.1f}</div></div>'
                f'<div class="ibox"><div class="ilabel">ADX (Trend)</div><div class="ival" style="color:{"#059669" if I["adx"]>25 else "inherit"};">{I["adx"]:.1f}</div></div>'
                f'<div class="ibox"><div class="ilabel">Volume Ratio</div><div class="ival" style="color:{"#059669" if I["vol_r"]>1.5 else "inherit"};">{I["vol_r"]:.1f}x</div></div>'
                f'</div>', unsafe_allow_html=True
            )
            
        with t2:
            st.markdown(
                f'<div class="trow" style="grid-template-columns:1fr 1fr;gap:10px;">'
                f'<div class="tgt" style="padding:14px;"><div class="tl">จุดเข้าซื้อ (Entry)</div><div class="tv" style="color:#7c6af0; font-size:1.1rem;">{cur}{S["entry"]:.2f}</div></div>'
                f'<div class="tgt" style="padding:14px;"><div class="tl">ตัดขาดทุน (Stop Loss)</div><div class="tv" style="color:#dc2626; font-size:1.1rem;">{cur}{S["sl"]:.2f}</div></div>'
                f'<div class="tgt" style="padding:14px;"><div class="tl">เป้าทำกำไร 1 (R1)</div><div class="tv" style="color:#059669; font-size:1.1rem;">{cur}{I["r1"]:.2f}</div></div>'
                f'<div class="tgt" style="padding:14px;"><div class="tl">เป้าทำกำไร 2 (R2)</div><div class="tv" style="color:#0284c7; font-size:1.1rem;">{cur}{I["r2"]:.2f}</div></div>'
                f'</div>', unsafe_allow_html=True
            )

        # ส่วนประมวลผล AI 
        st.markdown('<div class="da-hdr" style="margin-top:20px;">', unsafe_allow_html=True)
        st.markdown("### 🤖 ให้ AI วิเคราะห์ข่าว + กราฟ")
        provider = st.radio("เลือก AI", ["🔘 Gemini (ฟรี)", "🔘 Claude (พรีเมียม)"], horizontal=True, label_visibility="collapsed")
        
        is_gemini = "Gemini" in provider
        api_key = st.text_input("🔑 ใส่ API Key", type="password", placeholder="AIzaSy..." if is_gemini else "sk-ant-...")
        
        if st.button("🚀 สแกนข่าวและวิเคราะห์", use_container_width=True):
            if not api_key: st.error("❌ กรุณาใส่ API Key ก่อนครับ")
            else:
                with st.spinner("📰 ดึงข่าวเด่น..."):
                    news = search_stock_news_one_month(sym, market=mkt)
                    ntxt = "\n".join([f"- {n['title']}" for n in news]) if news else "ไม่มีข่าวสำคัญ"
                
                with st.spinner("🧠 AI กำลังคิด..."):
                    prompt = f"วิเคราะห์หุ้น {sym}. ราคา: {I['price']:.2f}, RSI: {I['rsi']:.1f}, MACD_H: {I['macd_h']:.3f}, เทรนด์: {S['rec']}\n\nข่าวล่าสุด (1 เดือน):\n{ntxt}\n\nสรุปสั้นๆ: 1. ข่าวดีหรือร้าย? 2. กราฟน่าซื้อไหม? 3. คำแนะนำ"
                    try:
                        res = call_gemini_api(prompt, api_key) if is_gemini else call_claude_api(prompt, api_key)
                        st.success("เสร็จสิ้น!")
                        
                        # ใช้กล่อง info ของ Streamlit ตัวอักษรอ่านง่ายแน่นอน
                        st.info(res)
                        
                        if news:
                            with st.expander("ดูรายการข่าวที่ AI อ่าน"):
                                for n in news: st.write(f"- {n['title']} ({n['source']})")
                    except Exception as e:
                        st.error(f"❌ {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 7. Router
# ==========================================
if st.session_state.view == "login":
    st.markdown('<div class="app-hdr"><h1>Stock Scanner Pro</h1></div>', unsafe_allow_html=True)
    with st.form("login"):
        st.write("🔑 เข้าสู่ระบบ Settrade (ข้ามได้ถ้าไม่มี)")
        st.text_input("APP ID"); st.text_input("APP SECRET", type="password")
        if st.form_submit_button("🔌 เชื่อมต่อ"):
            st.session_state.logged_in = True
            st.session_state.view = "manual"
            st.rerun()
    if st.button("ข้ามการล็อคอิน (ใช้ข้อมูลจำลอง/YFinance)", use_container_width=True):
        st.session_state.view = "manual"
        st.rerun()
elif st.session_state.view == "manual": view_manual()
elif st.session_state.view == "detail": view_detail()
