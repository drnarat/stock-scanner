import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta

# ============================================================
# CONFIG
# ============================================================
APP_ID     = "MPRZz1Hymo6nR50A"
APP_SECRET = "Te/3LKXBb+IM20T/ygcFAMWXjIgkadJ+o1cDstkjRDQ="
APP_CODE   = "SANDBOX"
BROKER_ID  = "SANDBOX"
USE_MOCK   = True   # ← เปลี่ยนเป็น False เมื่อมี Settrade credential จริง

# ============================================================
# PAGE CONFIG — mobile-first
# ============================================================
st.set_page_config(
    page_title="📈 Stock Scanner Pro",
    page_icon="📈",
    layout="centered",          # centered ดีกว่า wide สำหรับมือถือ
    initial_sidebar_state="collapsed",
)

# ============================================================
# GLOBAL CSS — mobile-first design
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif;
    background: #0d0d14;
    color: #e2e8f0;
}

/* ---- HEADER ---- */
.app-header {
    background: linear-gradient(135deg, #12122a 0%, #1a1035 50%, #0f1f3a 100%);
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 16px;
    padding: 18px 16px 14px;
    text-align: center;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(108,99,255,0.2);
}
.app-header h1 { font-size: 1.4rem; font-weight: 700; color: #fff; letter-spacing: -0.3px; }
.app-header .sub { font-size: 0.75rem; color: #8892b0; margin-top: 4px; }
.live-dot {
    display: inline-block; width: 8px; height: 8px;
    background: #00b894; border-radius: 50%;
    margin-right: 5px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50% { opacity:0.4; transform:scale(1.3); }
}

/* ---- MARKET SELECTOR CARDS ---- */
.market-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 16px;
}
.market-card {
    background: #1a1a2e;
    border: 2px solid #2a2a4a;
    border-radius: 14px;
    padding: 14px 10px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
}
.market-card:active { transform: scale(0.96); }
.market-card.selected {
    border-color: #6c63ff;
    background: linear-gradient(135deg, #1e1b4b, #1a1a3a);
    box-shadow: 0 0 16px rgba(108,99,255,0.35);
}
.market-card .flag { font-size: 1.8rem; display: block; margin-bottom: 4px; }
.market-card .mname { font-size: 0.8rem; font-weight: 600; color: #e2e8f0; }
.market-card .mdesc { font-size: 0.68rem; color: #8892b0; margin-top: 2px; }

/* ---- PILL TABS (แทน st.tabs) ---- */
.pill-tabs {
    display: flex; gap: 8px; margin-bottom: 16px;
    overflow-x: auto; padding-bottom: 2px;
    -webkit-overflow-scrolling: touch;
}
.pill-tab {
    background: #1a1a2e; border: 1px solid #2a2a4a;
    border-radius: 20px; padding: 8px 16px;
    font-size: 0.8rem; font-weight: 600; cursor: pointer;
    white-space: nowrap; color: #8892b0;
    transition: all 0.2s; flex-shrink: 0;
}
.pill-tab.active {
    background: #6c63ff; border-color: #6c63ff; color: #fff;
    box-shadow: 0 2px 10px rgba(108,99,255,0.4);
}

/* ---- PARAM SECTION ---- */
.param-section {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 12px;
}
.param-title {
    font-size: 0.78rem; font-weight: 700; color: #6c63ff;
    text-transform: uppercase; letter-spacing: 1px;
    margin-bottom: 12px;
    display: flex; align-items: center; gap: 6px;
}

/* ---- STOCK CARD ---- */
.stock-card {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 10px;
    position: relative;
    transition: border-color 0.2s;
}
.stock-card.buy  { border-left: 4px solid #00b894; }
.stock-card.sell { border-left: 4px solid #d63031; }
.stock-card.watch{ border-left: 4px solid #fdcb6e; }
.stock-card.neutral { border-left: 4px solid #636e72; }

.sc-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.sc-symbol { font-size: 1.05rem; font-weight: 700; color: #fff; font-family: 'IBM Plex Mono', monospace; }
.sc-name { font-size: 0.72rem; color: #8892b0; margin-top: 2px; }
.sc-price { font-size: 1.05rem; font-weight: 700; color: #fff; text-align: right; font-family: 'IBM Plex Mono', monospace; }
.sc-change { font-size: 0.72rem; text-align: right; margin-top: 2px; font-weight: 600; }
.change-up { color: #00b894; }
.change-dn { color: #d63031; }

.sc-bars {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 6px; margin-top: 10px;
}
.sc-bar-item { text-align: center; }
.sc-bar-label { font-size: 0.62rem; color: #636e72; text-transform: uppercase; }
.sc-bar-val { font-size: 0.8rem; font-weight: 600; color: #e2e8f0; font-family: 'IBM Plex Mono', monospace; }

.sc-bottom { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.score-ring {
    width: 42px; height: 42px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace;
    flex-shrink: 0;
}
.score-h { background: rgba(0,184,148,0.2); border: 2px solid #00b894; color: #00b894; }
.score-m { background: rgba(253,203,110,0.2); border: 2px solid #fdcb6e; color: #fdcb6e; }
.score-l { background: rgba(214,48,49,0.2); border: 2px solid #d63031; color: #d63031; }

.signal-chip {
    font-size: 0.75rem; font-weight: 700; padding: 4px 10px;
    border-radius: 12px; display: inline-block;
}
.chip-buy     { background: rgba(0,184,148,0.15); color: #00b894; border: 1px solid #00b89460; }
.chip-sell    { background: rgba(214,48,49,0.15);  color: #d63031; border: 1px solid #d6303160; }
.chip-watch   { background: rgba(253,203,110,0.15);color: #fdcb6e; border: 1px solid #fdcb6e60; }
.chip-neutral { background: rgba(99,110,114,0.15); color: #636e72; border: 1px solid #63637260; }

.rr-badge { font-size: 0.7rem; color: #8892b0; }
.rr-val { color: #6c63ff; font-weight: 700; }

/* ---- TARGETS ROW ---- */
.target-row {
    display: grid; grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 6px; margin-top: 8px;
}
.tgt { background: #12122a; border-radius: 8px; padding: 7px 4px; text-align: center; }
.tgt-label { font-size: 0.6rem; color: #636e72; text-transform: uppercase; letter-spacing: 0.5px; }
.tgt-val { font-size: 0.78rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; margin-top: 2px; }
.tgt-entry { color: #6c63ff; } .tgt-t1 { color: #00b894; } .tgt-t2 { color: #00cec9; } .tgt-sl { color: #d63031; }

/* ---- DEEP ANALYSIS ---- */
.da-header {
    background: linear-gradient(135deg, #12122a, #1a1035);
    border: 1px solid rgba(108,99,255,0.4);
    border-radius: 14px; padding: 16px; margin-bottom: 14px;
}
.da-symbol { font-size: 1.5rem; font-weight: 700; color: #fff; font-family: 'IBM Plex Mono', monospace; }
.da-price  { font-size: 1.8rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; }
.da-market-tag {
    display: inline-block; font-size: 0.68rem; font-weight: 700;
    padding: 3px 8px; border-radius: 8px; margin-left: 8px;
    vertical-align: middle;
}
.tag-th { background: #1a3a1a; color: #00b894; border: 1px solid #00b89440; }
.tag-us { background: #1a1a3a; color: #6c63ff; border: 1px solid #6c63ff40; }
.tag-cn { background: #3a1a1a; color: #d63031; border: 1px solid #d6303140; }

.ind-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 8px; margin-bottom: 14px;
}
.ind-box {
    background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 10px;
    padding: 10px; display: flex; flex-direction: column; gap: 2px;
}
.ind-label { font-size: 0.65rem; color: #636e72; text-transform: uppercase; letter-spacing: 0.5px; }
.ind-val   { font-size: 0.95rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; }
.ind-status{ font-size: 0.65rem; margin-top: 1px; }
.bull { color: #00b894; } .bear { color: #d63031; } .neut { color: #fdcb6e; }

.signal-list { margin-bottom: 14px; }
.sig-item {
    border-radius: 10px; padding: 9px 12px; margin-bottom: 6px;
    font-size: 0.8rem; line-height: 1.5; border-left: 3px solid;
}
.sig-buy   { background: rgba(0,184,148,0.08); border-color: #00b894; color: #b2f5ea; }
.sig-sell  { background: rgba(214,48,49,0.08); border-color: #d63031;  color: #fed7d7; }
.sig-neut  { background: rgba(99,110,114,0.08); border-color: #636e72; color: #cbd5e0; }

.pivot-row {
    display: flex; gap: 6px; overflow-x: auto;
    padding-bottom: 4px; margin-bottom: 14px;
    -webkit-overflow-scrolling: touch;
}
.pvt-box {
    flex-shrink: 0; background: #1a1a2e; border-radius: 10px;
    padding: 8px 12px; text-align: center; min-width: 72px;
    border: 1px solid #2a2a4a;
}
.pvt-label { font-size: 0.6rem; color: #636e72; text-transform: uppercase; }
.pvt-val   { font-size: 0.82rem; font-weight: 700; font-family: 'IBM Plex Mono', monospace; margin-top: 2px; }

/* ---- MISC ---- */
.section-title {
    font-size: 0.72rem; font-weight: 700; color: #8892b0;
    text-transform: uppercase; letter-spacing: 1px;
    margin: 16px 0 10px; display: flex; align-items: center; gap: 6px;
}
.section-title::after {
    content: ''; flex: 1; height: 1px; background: #2a2a4a;
}
.empty-state {
    text-align: center; padding: 32px 16px;
    color: #636e72; font-size: 0.88rem; line-height: 1.8;
}
.update-bar {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 12px; background: #12122a; border-radius: 10px;
    font-size: 0.7rem; color: #636e72; margin-bottom: 12px;
}
.mock-badge {
    display: inline-flex; align-items: center; gap: 4px;
    background: rgba(253,203,110,0.1); border: 1px solid #fdcb6e40;
    color: #fdcb6e; font-size: 0.68rem; font-weight: 700;
    padding: 3px 8px; border-radius: 8px;
}

/* ---- streamlit overrides ---- */
div.stButton > button {
    width: 100%; background: linear-gradient(135deg, #6c63ff, #4f46e5);
    color: #fff; border: none; border-radius: 12px;
    padding: 14px; font-size: 0.95rem; font-weight: 700;
    font-family: 'Sarabun', sans-serif;
    box-shadow: 0 4px 16px rgba(108,99,255,0.35);
    transition: all 0.2s;
}
div.stButton > button:hover { opacity: 0.9; transform: translateY(-1px); }
div.stButton > button:active { transform: scale(0.97); }

div[data-testid="stSelectbox"] > label,
div[data-testid="stSlider"] > label,
div[data-testid="stExpander"] > div > div > p { color: #8892b0 !important; font-size: 0.82rem !important; }

.stSlider > div { padding: 0 !important; }

div[data-testid="stExpander"] {
    background: #1a1a2e; border: 1px solid #2a2a4a !important;
    border-radius: 12px !important; margin-bottom: 8px;
}

.stDataFrame { background: #1a1a2e !important; border-radius: 12px !important; }
.stDataFrame table { font-size: 0.78rem !important; }

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { background: #0d0d14 !important; }

div[data-testid="stSidebar"] { background: #12122a !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# STOCK UNIVERSE
# ============================================================
MARKETS = {
    "SET": {
        "label": "🇹🇭 SET", "flag": "🇹🇭", "name": "ตลาดหุ้นไทย",
        "desc": "SET50, SET100, mai", "currency": "฿", "tag_class": "tag-th",
        "stocks": [
            ("KBANK","กสิกรไทย"),("BBL","กรุงเทพ"),("SCB","ไทยพาณิชย์"),
            ("KTB","กรุงไทย"),("BAY","กรุงศรี"),("TISCO","ทิสโก้"),("KKP","เกียรตินาคิน"),
            ("PTT","ปตท."),("PTTEP","ปตท.สผ."),("GULF","กัลฟ์"),("GPSC","โกลบอลเพาเวอร์"),
            ("RATCH","ราช กรุ๊ป"),("BGRIM","บี.กริม"),("EGCO","เอ็กโก"),
            ("ADVANC","แอดวานซ์"),("TRUE","ทรู"),("INSET","อินเซ็ท"),
            ("MFEC","MFEC"),("BE8","บี8"),("INET","อินเทอร์เน็ต"),
            ("CPALL","ซีพีออลล์"),("CRC","เซ็นทรัล รีเทล"),("HMPRO","โฮมโปร"),
            ("MAKRO","แม็คโคร"),("BJC","บีเจซี"),
            ("CPF","ซีพีเอฟ"),("TU","ไทยยูเนี่ยน"),("GFPT","จีเอฟพีที"),("BTG","บีทาเก้น"),
            ("LH","แลนด์แอนด์เฮาส์"),("AP","เอพี"),("SIRI","แสนสิริ"),("QH","ควอลิตี้เฮ้าส์"),
            ("AOT","ท่าอากาศยาน"),("AAV","เอเชีย เอวิเอชั่น"),("CENTEL","เซ็นทารา"),
            ("MINT","ไมเนอร์"),("ERW","อีอาร์ดับบิ้ว"),
            ("BDMS","กรุงเทพดุสิต"),("BGH","กรุงเทพ"),("BCH","บางกอก"),("BH","กรุงเทพ เชน"),
            ("SCC","ปูนซิเมนต์ไทย"),("SCCC","ปูนซีเมนต์นครหลวง"),
            ("PTTGC","พีทีที โกลบอล"),("IRPC","IRPC"),
            ("MTC","เมืองไทย แคปปิตอล"),("TIDLOR","ไทยเดินทาง"),
            ("SAWAD","ศาวะดี"),("AEONTS","อิออน"),
        ],
    },
    "US": {
        "label": "🇺🇸 US Tech", "flag": "🇺🇸", "name": "หุ้นเทคโนโลยีสหรัฐ",
        "desc": "NASDAQ, NYSE Tech", "currency": "$", "tag_class": "tag-us",
        "stocks": [
            ("AAPL","Apple Inc."),("MSFT","Microsoft Corp."),("NVDA","NVIDIA Corp."),
            ("GOOGL","Alphabet Inc."),("META","Meta Platforms"),("AMZN","Amazon.com"),
            ("TSLA","Tesla Inc."),("AMD","Advanced Micro Devices"),("INTC","Intel Corp."),
            ("AVGO","Broadcom Inc."),("QCOM","Qualcomm"),("MU","Micron Technology"),
            ("AMAT","Applied Materials"),("LRCX","Lam Research"),("SNPS","Synopsys"),
            ("ORCL","Oracle Corp."),("CRM","Salesforce"),("ADBE","Adobe Inc."),
            ("NOW","ServiceNow"),("PLTR","Palantir"),
        ],
    },
    "CN": {
        "label": "🇨🇳 CN Tech", "flag": "🇨🇳", "name": "หุ้นเทคโนโลยีจีน",
        "desc": "NYSE/NASDAQ ADR", "currency": "$", "tag_class": "tag-cn",
        "stocks": [
            ("BABA","Alibaba Group"),("JD","JD.com"),("BIDU","Baidu Inc."),
            ("NTES","NetEase"),("PDD","Pinduoduo"),("TCOM","Trip.com"),
            ("NIO","NIO Inc."),("XPEV","XPeng Inc."),("LI","Li Auto"),
            ("BILI","Bilibili"),("IQ","iQIYI"),("WB","Weibo Corp."),
            ("FUTU","Futu Holdings"),("TIGR","UP Fintech"),("LKNCY","Luckin Coffee"),
        ],
    },
}

# ============================================================
# DATA / INDICATOR FUNCTIONS
# ============================================================
def gen_candles(symbol, n=120):
    np.random.seed(abs(hash(symbol)) % 99999)
    base = np.random.uniform(8, 600)
    closes = [base]
    for _ in range(n - 1):
        closes.append(max(closes[-1] * (1 + np.random.normal(0, 0.014)), 0.5))
    closes = np.array(closes)
    highs  = closes * np.random.uniform(1.001, 1.025, n)
    lows   = closes * np.random.uniform(0.975, 0.999, n)
    vols   = np.random.uniform(3e5, 8e6, n).astype(int)
    return pd.DataFrame({"last": closes, "high": highs, "low": lows, "volume": vols})

def gen_quote(symbol):
    np.random.seed(abs(hash(symbol + str(datetime.now().hour))) % 99999)
    p = np.random.uniform(8, 600)
    chg = np.random.normal(0, 1.8)
    return {"last": round(p,2), "changePercent": round(chg/p*100,2), "volume": int(np.random.uniform(3e5,8e6))}

def sma(s, n): return s.rolling(n).mean()
def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rsi(s, n=14):
    d = s.diff(); g = d.clip(lower=0).rolling(n).mean(); l = (-d.clip(upper=0)).rolling(n).mean()
    return 100 - 100/(1 + g/(l+1e-9))

def macd(s, f=12, sl=26, sg=9):
    ml = ema(s,f) - ema(s,sl); sig = ema(ml,sg); return ml, sig, ml-sig

def bbands(s, n=20, k=2):
    m = sma(s,n); std = s.rolling(n).std()
    up, lo = m+k*std, m-k*std
    pct = (s - lo)/(up - lo + 1e-9)
    return up, m, lo, pct

def stoch(h, l, c, kp=14, dp=3):
    ll = l.rolling(kp).min(); hh = h.rolling(kp).max()
    k = 100*(c-ll)/(hh-ll+1e-9); return k, k.rolling(dp).mean()

def atr(h, l, c, n=14):
    tr = pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def cci(h, l, c, n=20):
    tp = (h+l+c)/3; m = tp.rolling(n).mean()
    mad = tp.rolling(n).apply(lambda x: np.abs(x-x.mean()).mean())
    return (tp - m)/(0.015*mad + 1e-9)

def williams_r(h, l, c, n=14):
    return -100*(h.rolling(n).max()-c)/(h.rolling(n).max()-l.rolling(n).min()+1e-9)

def mfi(h, l, c, v, n=14):
    tp = (h+l+c)/3; mf = tp*v
    pos = mf.where(tp>tp.shift(),0).rolling(n).sum()
    neg = mf.where(tp<tp.shift(),0).rolling(n).sum()
    return 100 - 100/(1 + pos/(neg+1e-9))

def adx(h, l, c, n=14):
    tr = pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    dmp = (h-h.shift()).clip(lower=0); dmm = (l.shift()-l).clip(lower=0)
    dmp = dmp.where(dmp>dmm,0); dmm = dmm.where(dmm>dmp,0)
    atr14 = tr.rolling(n).mean()
    dip = 100*dmp.rolling(n).mean()/(atr14+1e-9)
    dim = 100*dmm.rolling(n).mean()/(atr14+1e-9)
    dx = 100*(dip-dim).abs()/(dip+dim+1e-9)
    return dx.rolling(n).mean(), dip, dim

def vwap(h, l, c, v):
    tp = (h+l+c)/3; return (tp*v).cumsum()/(v.cumsum()+1e-9)

def compute_indicators(df, p):
    c, h, l, v = df["last"], df["high"], df["low"], df["volume"]
    I = {}
    I["sma20"]  = sma(c, p["sma_s"]).iloc[-1]
    I["sma50"]  = sma(c, p["sma_m"]).iloc[-1]
    I["sma200"] = sma(c, p["sma_l"]).iloc[-1]
    I["ema12"]  = ema(c, p["ema_f"]).iloc[-1]
    I["ema26"]  = ema(c, p["ema_s"]).iloc[-1]
    I["rsi"]    = rsi(c, p["rsi_p"]).iloc[-1]
    ml, ms, mh  = macd(c, p["macd_f"], p["macd_s"], p["macd_sg"])
    I["macd"]   = ml.iloc[-1]; I["macd_sig"] = ms.iloc[-1]; I["macd_h"] = mh.iloc[-1]
    bbu,bbm,bbl,bbp = bbands(c, p["bb_p"], p["bb_k"])
    I["bbu"]=bbu.iloc[-1]; I["bbm"]=bbm.iloc[-1]; I["bbl"]=bbl.iloc[-1]; I["bbp"]=bbp.iloc[-1]
    I["atr"]    = atr(h, l, c, p["atr_p"]).iloc[-1]
    sk, sd = stoch(h, l, c, p["stoch_k"], p["stoch_d"])
    I["sk"]=sk.iloc[-1]; I["sd"]=sd.iloc[-1]
    I["cci"]    = cci(h,l,c, p["cci_p"]).iloc[-1]
    I["wr"]     = williams_r(h,l,c, p["wr_p"]).iloc[-1]
    I["mfi"]    = mfi(h,l,c,v, p["mfi_p"]).iloc[-1]
    adx_v,dip,dim = adx(h,l,c, p["adx_p"])
    I["adx"]=adx_v.iloc[-1]; I["dip"]=dip.iloc[-1]; I["dim"]=dim.iloc[-1]
    I["vwap"]   = vwap(h,l,c,v).iloc[-1]
    I["vol_avg"]= v.rolling(20).mean().iloc[-1]
    I["vol_r"]  = v.iloc[-1]/(I["vol_avg"]+1)
    I["price"]  = c.iloc[-1]
    I["chg"]    = (c.iloc[-1]/c.iloc[-2]-1)*100
    I["52wh"]   = h.rolling(min(252,len(h))).max().iloc[-1]
    I["52wl"]   = l.rolling(min(252,len(l))).min().iloc[-1]
    pivot = (h.iloc[-1]+l.iloc[-1]+c.iloc[-1])/3
    rnge  = h.iloc[-1]-l.iloc[-1]
    I["pivot"]=pivot; I["r1"]=2*pivot-l.iloc[-1]; I["r2"]=pivot+rnge
    I["s1"]=2*pivot-h.iloc[-1]; I["s2"]=pivot-rnge
    return I

def score(I, p):
    ob, os_ = p["rsi_ob"], p["rsi_os"]
    bs, ss, ns = [], [], []; sc = 50

    rsi_v = I["rsi"]
    if rsi_v < os_:    sc+=8;  bs.append(f"RSI {rsi_v:.1f} < {os_} → Oversold โซนซื้อ")
    elif rsi_v > ob:   sc-=8;  ss.append(f"RSI {rsi_v:.1f} > {ob} → Overbought โซนขาย")
    else:                       ns.append(f"RSI {rsi_v:.1f} อยู่ในโซนปกติ")

    if I["macd"] > I["macd_sig"] and I["macd_h"] > 0:
        sc+=7; bs.append("MACD ตัดขึ้น Signal → โมเมนตัมขาขึ้น")
    elif I["macd"] < I["macd_sig"] and I["macd_h"] < 0:
        sc-=7; ss.append("MACD ตัดลง Signal → โมเมนตัมขาลง")

    pr = I["price"]
    if pr > I["sma20"] > I["sma50"]:   sc+=6; bs.append("ราคา > SMA20 > SMA50 → uptrend")
    elif pr < I["sma20"] < I["sma50"]: sc-=6; ss.append("ราคา < SMA20 < SMA50 → downtrend")
    if pr > I["sma200"]: sc+=4; bs.append("ราคา > SMA200 → เหนือค่าเฉลี่ยระยะยาว")
    else:                 sc-=4; ss.append("ราคา < SMA200 → ต่ำกว่าค่าเฉลี่ยระยะยาว")

    bbp = I["bbp"]
    if bbp < 0.15:   sc+=6; bs.append(f"BB% = {bbp:.2f} ใกล้ Lower Band → oversold")
    elif bbp > 0.85: sc-=5; ss.append(f"BB% = {bbp:.2f} ใกล้ Upper Band → overbought")

    sk, sd = I["sk"], I["sd"]
    if sk < 20 and sk > sd: sc+=5; bs.append(f"Stochastic %K {sk:.1f} ตัดขึ้น %D ในโซน oversold")
    elif sk > 80 and sk < sd: sc-=5; ss.append(f"Stochastic %K {sk:.1f} ตัดลง %D ในโซน overbought")

    cci_v = I["cci"]
    if cci_v < -100: sc+=4; bs.append(f"CCI {cci_v:.1f} < -100 → oversold")
    elif cci_v > 100: sc-=4; ss.append(f"CCI {cci_v:.1f} > 100 → overbought")

    wr_v = I["wr"]
    if wr_v < -80:  sc+=4; bs.append(f"Williams %R {wr_v:.1f} < -80 → oversold")
    elif wr_v > -20: sc-=4; ss.append(f"Williams %R {wr_v:.1f} > -20 → overbought")

    adx_v = I["adx"]
    if adx_v > 25:
        if I["dip"] > I["dim"]: sc+=5; bs.append(f"ADX {adx_v:.1f} > 25 + DI+ > DI- → uptrend แข็งแกร่ง")
        else:                    sc-=5; ss.append(f"ADX {adx_v:.1f} > 25 + DI- > DI+ → downtrend แข็งแกร่ง")
    else: ns.append(f"ADX {adx_v:.1f} < 25 → ไม่มีแนวโน้มชัดเจน")

    mfi_v = I["mfi"]
    if mfi_v < 20:  sc+=4; bs.append(f"MFI {mfi_v:.1f} < 20 → เงินไหลออกมาก (โอกาสดีดกลับ)")
    elif mfi_v > 80: sc-=4; ss.append(f"MFI {mfi_v:.1f} > 80 → เงินไหลเข้าเกิน (ระวังแรงขาย)")

    vr = I["vol_r"]
    if vr > 1.5: sc+=3; bs.append(f"Volume สูง {vr:.1f}x ค่าเฉลี่ย → มีนัยสำคัญ")
    elif vr < 0.5: ns.append(f"Volume ต่ำ {vr:.1f}x → ระวังสัญญาณหลอก")

    if pr > I["vwap"]: sc+=3; bs.append("ราคา > VWAP → แรงซื้อจากสถาบัน")
    else:               sc-=3; ss.append("ราคา < VWAP → แรงขายจากสถาบัน")

    sc = max(0, min(100, sc))
    if sc >= 65:   rec, cls = "🟢 ซื้อ", "buy"
    elif sc <= 35: rec, cls = "🔴 ขาย", "sell"
    elif sc >= 55: rec, cls = "🟡 เฝ้าระวัง", "watch"
    else:          rec, cls = "⚪ ถือ", "neutral"

    at = I["atr"]
    entry = round(pr * 0.985, 2)
    t1    = round(pr + at * 2.0, 2)
    t2    = round(pr + at * 3.5, 2)
    sl    = round(pr - at * 1.5, 2)
    up    = round((t1/pr-1)*100, 1)
    dn    = round((pr/sl-1)*100, 1) if sl > 0 else 1
    rr    = round(up/dn, 2) if dn > 0 else 0

    return dict(sc=sc, rec=rec, cls=cls, bs=bs, ss=ss, ns=ns,
                entry=entry, t1=t1, t2=t2, sl=sl, up=up, dn=dn, rr=rr)

def scan_market(market_key, params, progress_cb=None):
    mkt = MARKETS[market_key]
    rows = []
    stocks = mkt["stocks"]
    for i, (sym, name) in enumerate(stocks):
        try:
            df = gen_candles(sym)
            I  = compute_indicators(df, params)
            S  = score(I, params)
            rows.append(dict(
                Symbol=sym, Name=name, Market=market_key,
                Price=round(I["price"],2), Change=round(I["chg"],2),
                RSI=round(I["rsi"],1), ADX=round(I["adx"],1),
                BB=round(I["bbp"],2), VR=round(I["vol_r"],2),
                Score=S["sc"], Signal=S["rec"], SigCls=S["cls"],
                Entry=S["entry"], T1=S["t1"], T2=S["t2"], SL=S["sl"],
                RR=S["rr"], _I=I, _S=S,
            ))
        except: pass
        if progress_cb: progress_cb((i+1)/len(stocks))
    return pd.DataFrame(rows)

# ============================================================
# SESSION STATE INIT
# ============================================================
for k, v in [("market", None), ("scan_results", {}), ("view", "scan"),
             ("detail_sym", None), ("detail_mkt", None)]:
    if k not in st.session_state: st.session_state[k] = v

# ============================================================
# HEADER
# ============================================================
mock_html = '<span class="mock-badge">⚠️ MOCK DATA</span>' if USE_MOCK else \
            '<span class="mock-badge" style="background:rgba(0,184,148,0.1);border-color:#00b89440;color:#00b894;">⚡ LIVE</span>'

st.markdown(f"""
<div class="app-header">
    <h1>📈 Stock Scanner Pro</h1>
    <div class="sub">
        <span class="live-dot"></span>
        15+ Indicators · AI Scoring · ครอบคลุม 3 ตลาด &nbsp;{mock_html}
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# DEFAULT PARAMS (hidden — expandable)
# ============================================================
with st.expander("⚙️ ตั้งค่า Parameters (แตะเพื่อขยาย)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        sma_s  = st.slider("SMA สั้น",  5,  50, 20, key="sma_s")
        sma_m  = st.slider("SMA กลาง", 20, 100, 50, key="sma_m")
        sma_l  = st.slider("SMA ยาว", 100, 300,200, key="sma_l")
        ema_f  = st.slider("EMA Fast",  5,  20, 12, key="ema_f")
        ema_sv = st.slider("EMA Slow", 15,  50, 26, key="ema_sv")
        rsi_p  = st.slider("RSI Period", 7, 21, 14, key="rsi_p")
        rsi_ob = st.slider("RSI Overbought", 60, 85, 70, key="rsi_ob")
        rsi_os = st.slider("RSI Oversold",  15, 40, 30, key="rsi_os")
    with col2:
        macd_f  = st.slider("MACD Fast",   8, 20, 12, key="macd_f")
        macd_s  = st.slider("MACD Slow",  20, 40, 26, key="macd_s")
        macd_sg = st.slider("MACD Signal", 5, 15,  9, key="macd_sg")
        bb_p    = st.slider("BB Period",  10, 30, 20, key="bb_p")
        bb_k    = st.slider("BB Std Dev", 1, 3, 2,    key="bb_k")
        stoch_k = st.slider("Stoch %K",   5, 21, 14,  key="stoch_k")
        stoch_d = st.slider("Stoch %D",   2,  7,  3,  key="stoch_d")
        adx_p   = st.slider("ADX Period", 7, 21, 14,  key="adx_p")

    col3, col4 = st.columns(2)
    with col3:
        atr_p  = st.slider("ATR Period",  7, 21, 14, key="atr_p")
        cci_p  = st.slider("CCI Period", 10, 30, 20, key="cci_p")
        wr_p   = st.slider("Williams %R",  7, 21, 14, key="wr_p")
        mfi_p  = st.slider("MFI Period",   7, 21, 14, key="mfi_p")
    with col4:
        min_score = st.slider("คะแนนขั้นต่ำ",    0, 100, 60, key="min_score")
        min_rr    = st.slider("R/R ขั้นต่ำ",    0.5, 5.0, 1.5, step=0.5, key="min_rr")
        min_adx   = st.slider("ADX ขั้นต่ำ",    0, 40, 18, key="min_adx")
        sig_opts  = st.multiselect("สัญญาณที่ต้องการ",
            ["🟢 ซื้อ","🟡 เฝ้าระวัง","⚪ ถือ","🔴 ขาย"],
            default=["🟢 ซื้อ","🟡 เฝ้าระวัง"], key="sig_opts")

params = dict(
    sma_s=st.session_state.sma_s, sma_m=st.session_state.sma_m, sma_l=st.session_state.sma_l,
    ema_f=st.session_state.ema_f, ema_s=st.session_state.ema_sv,
    rsi_p=st.session_state.rsi_p, rsi_ob=st.session_state.rsi_ob, rsi_os=st.session_state.rsi_os,
    macd_f=st.session_state.macd_f, macd_s=st.session_state.macd_s, macd_sg=st.session_state.macd_sg,
    bb_p=st.session_state.bb_p, bb_k=st.session_state.bb_k,
    stoch_k=st.session_state.stoch_k, stoch_d=st.session_state.stoch_d,
    atr_p=st.session_state.atr_p, cci_p=st.session_state.cci_p,
    wr_p=st.session_state.wr_p, mfi_p=st.session_state.mfi_p, adx_p=st.session_state.adx_p,
)

# ============================================================
# VIEW ROUTER
# ============================================================
if st.session_state.view == "detail":
    # ---- DEEP ANALYSIS VIEW ----
    sym = st.session_state.detail_sym
    mkt_key = st.session_state.detail_mkt
    mkt = MARKETS[mkt_key]
    cur = mkt["currency"]

    if st.button("← กลับรายการหุ้น"):
        st.session_state.view = "scan"
        st.rerun()

    # Load/compute
    cached = st.session_state.scan_results.get(mkt_key)
    if cached is not None and sym in cached["Symbol"].values:
        row = cached[cached["Symbol"] == sym].iloc[0]
        I, S = row["_I"], row["_S"]
    else:
        with st.spinner(f"กำลังวิเคราะห์ {sym}..."):
            df = gen_candles(sym)
            I  = compute_indicators(df, params)
            S  = score(I, params)

    pr = I["price"]
    tag_cls = mkt["tag_class"]
    score_cls = "score-h" if S["sc"]>=65 else "score-m" if S["sc"]>=45 else "score-l"
    chg_cls = "change-up" if I["chg"]>=0 else "change-dn"
    chip_cls = f"chip-{S['cls']}"

    st.markdown(f"""
    <div class="da-header">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
            <div>
                <span class="da-symbol">{sym}</span>
                <span class="da-market-tag {tag_cls}">{mkt['flag']} {mkt_key}</span><br>
                <span style="font-size:0.78rem;color:#8892b0;">{dict(MARKETS[mkt_key]["stocks"]).get(sym,'')}</span>
            </div>
            <div class="score-ring {score_cls}" style="width:52px;height:52px;font-size:1rem;">{S['sc']}</div>
        </div>
        <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:8px;">
            <div>
                <div class="da-price">{cur}{pr:.2f}</div>
                <span class="sc-change {chg_cls}">{'+' if I['chg']>=0 else ''}{I['chg']:.2f}% วันนี้</span>
            </div>
            <div style="text-align:right;">
                <div><span class="signal-chip {chip_cls}">{S['rec']}</span></div>
                <div style="font-size:0.72rem;color:#8892b0;margin-top:4px;">
                    R/R = <span style="color:#6c63ff;font-weight:700;">1:{S['rr']:.2f}</span>
                    &nbsp;·&nbsp; ↑{S['up']}% / ↓{S['dn']}%
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Targets
    st.markdown('<div class="section-title">🎯 เป้าหมายราคา</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="target-row">
        <div class="tgt"><div class="tgt-label">จุดซื้อ</div><div class="tgt-val tgt-entry">{cur}{S['entry']:.2f}</div></div>
        <div class="tgt"><div class="tgt-label">เป้า 1</div><div class="tgt-val tgt-t1">{cur}{S['t1']:.2f}</div></div>
        <div class="tgt"><div class="tgt-label">เป้า 2</div><div class="tgt-val tgt-t2">{cur}{S['t2']:.2f}</div></div>
        <div class="tgt"><div class="tgt-label">Stop Loss</div><div class="tgt-val tgt-sl">{cur}{S['sl']:.2f}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Indicators grid
    st.markdown('<div class="section-title">📊 Indicators</div>', unsafe_allow_html=True)

    def ind_cls(is_bull, is_bear):
        return "bull" if is_bull else "bear" if is_bear else "neut"
    def ind_lbl(is_bull, is_bear):
        return "▲ Bullish" if is_bull else "▼ Bearish" if is_bear else "→ Neutral"

    rsi_b = I["rsi"] < params["rsi_os"]; rsi_s = I["rsi"] > params["rsi_ob"]
    macd_b = I["macd"] > I["macd_sig"]; macd_s = I["macd"] < I["macd_sig"]
    bb_b = I["bbp"] < 0.2; bb_s = I["bbp"] > 0.8
    stoch_b = I["sk"] < 20 and I["sk"] > I["sd"]; stoch_s = I["sk"] > 80 and I["sk"] < I["sd"]
    cci_b = I["cci"] < -100; cci_s = I["cci"] > 100
    wr_b = I["wr"] < -80; wr_s = I["wr"] > -20
    mfi_b = I["mfi"] < 20; mfi_s = I["mfi"] > 80
    adx_up = I["adx"] > 25 and I["dip"] > I["dim"]; adx_dn = I["adx"] > 25 and I["dim"] > I["dip"]
    ma_b = I["price"] > I["sma20"] > I["sma50"]; ma_s = I["price"] < I["sma20"] < I["sma50"]
    vwap_b = I["price"] > I["vwap"]; vwap_s = I["price"] < I["vwap"]

    inds_html = '<div class="ind-grid">'
    indicators = [
        ("RSI", f"{I['rsi']:.1f}", rsi_b, rsi_s),
        ("MACD Hist", f"{I['macd_h']:.4f}", macd_b, macd_s),
        ("Bollinger %B", f"{I['bbp']:.2f}", bb_b, bb_s),
        ("Stochastic %K", f"{I['sk']:.1f}", stoch_b, stoch_s),
        ("CCI", f"{I['cci']:.1f}", cci_b, cci_s),
        ("Williams %R", f"{I['wr']:.1f}", wr_b, wr_s),
        ("MFI", f"{I['mfi']:.1f}", mfi_b, mfi_s),
        ("ADX", f"{I['adx']:.1f}", adx_up, adx_dn),
        ("MA Trend", "Up" if ma_b else "Down" if ma_s else "Flat", ma_b, ma_s),
        ("VWAP", f"{cur}{I['vwap']:.2f}", vwap_b, vwap_s),
        ("ATR", f"{cur}{I['atr']:.2f}", False, False),
        ("Vol Ratio", f"{I['vol_r']:.2f}x", I["vol_r"]>1.5, I["vol_r"]<0.5),
    ]
    for lbl, val, is_b, is_s in indicators:
        cls_ = ind_cls(is_b, is_s); lbl_ = ind_lbl(is_b, is_s)
        inds_html += f'<div class="ind-box"><div class="ind-label">{lbl}</div><div class="ind-val {cls_}">{val}</div><div class="ind-status {cls_}">{lbl_}</div></div>'
    inds_html += '</div>'
    st.markdown(inds_html, unsafe_allow_html=True)

    # Signal reasons
    if S["bs"]:
        st.markdown('<div class="section-title">🟢 สัญญาณซื้อ</div>', unsafe_allow_html=True)
        for sig in S["bs"]:
            st.markdown(f'<div class="sig-item sig-buy">✅ {sig}</div>', unsafe_allow_html=True)

    if S["ss"]:
        st.markdown('<div class="section-title">🔴 สัญญาณขาย</div>', unsafe_allow_html=True)
        for sig in S["ss"]:
            st.markdown(f'<div class="sig-item sig-sell">❌ {sig}</div>', unsafe_allow_html=True)

    if S["ns"]:
        st.markdown('<div class="section-title">⚪ ข้อมูลกลาง</div>', unsafe_allow_html=True)
        for sig in S["ns"]:
            st.markdown(f'<div class="sig-item sig-neut">ℹ️ {sig}</div>', unsafe_allow_html=True)

    # Pivot Points
    st.markdown('<div class="section-title">📐 Pivot Points</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="pivot-row">
        <div class="pvt-box"><div class="pvt-label">R2</div><div class="pvt-val" style="color:#ff7675;">{cur}{I['r2']:.2f}</div></div>
        <div class="pvt-box"><div class="pvt-label">R1</div><div class="pvt-val" style="color:#fab1a0;">{cur}{I['r1']:.2f}</div></div>
        <div class="pvt-box"><div class="pvt-label">PIVOT</div><div class="pvt-val" style="color:#74b9ff;">{cur}{I['pivot']:.2f}</div></div>
        <div class="pvt-box"><div class="pvt-label">S1</div><div class="pvt-val" style="color:#55efc4;">{cur}{I['s1']:.2f}</div></div>
        <div class="pvt-box"><div class="pvt-label">S2</div><div class="pvt-val" style="color:#00cec9;">{cur}{I['s2']:.2f}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # 52W Range
    pct_52 = (I["price"]/I["52wh"])*100
    st.markdown('<div class="section-title">📅 52-Week Range</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#1a1a2e;border-radius:10px;padding:12px;">
        <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#8892b0;margin-bottom:6px;">
            <span>52W Low: {cur}{I['52wl']:.2f}</span>
            <span>ตำแหน่งปัจจุบัน {pct_52:.1f}%</span>
            <span>52W High: {cur}{I['52wh']:.2f}</span>
        </div>
        <div style="background:#2a2a4a;border-radius:4px;height:6px;position:relative;">
            <div style="position:absolute;left:0;top:0;height:6px;width:{pct_52}%;
                background:linear-gradient(90deg,#6c63ff,#00b894);border-radius:4px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="update-bar"><span>อัปเดต: {datetime.now().strftime("%H:%M:%S")}</span><span>{"⚡ Settrade Live" if not USE_MOCK else "🔶 Mock Data"}</span></div>', unsafe_allow_html=True)

else:
    # ---- SCAN VIEW ----

    # STEP 1: Market Selector
    st.markdown('<div class="section-title">1️⃣ เลือกตลาดหุ้น</div>', unsafe_allow_html=True)

    mkt_cols = st.columns(3)
    for i, (mkt_key, mkt_data) in enumerate(MARKETS.items()):
        with mkt_cols[i]:
            selected = st.session_state.market == mkt_key
            btn_label = f"{mkt_data['flag']}\n{mkt_key}\n{mkt_data['desc']}"
            # Use button, highlight selected
            btn_style = "background:linear-gradient(135deg,#1e1b4b,#1a1a3a);border:2px solid #6c63ff;" if selected else ""
            if st.button(
                f"{mkt_data['flag']} **{mkt_key}**\n{mkt_data['desc']}",
                key=f"mkt_{mkt_key}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.market = mkt_key
                st.session_state.view = "scan"
                st.rerun()

    # Show selected market info
    if st.session_state.market:
        mkt_key = st.session_state.market
        mkt = MARKETS[mkt_key]
        cur = mkt["currency"]
        n_stocks = len(mkt["stocks"])
        st.markdown(f"""
        <div style="background:#12122a;border:1px solid rgba(108,99,255,0.3);border-radius:10px;
            padding:10px 14px;margin:8px 0 14px;display:flex;justify-content:space-between;align-items:center;">
            <span style="color:#e2e8f0;font-size:0.85rem;">
                {mkt['flag']} <strong>{mkt['name']}</strong> · {n_stocks} หุ้น · สกุลเงิน {cur}
            </span>
            <span style="font-size:0.72rem;color:#8892b0;">แตะ ▶ เพื่อสแกน</span>
        </div>
        """, unsafe_allow_html=True)

        # Filter options
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filt_sig = st.multiselect(
                "สัญญาณ", ["🟢 ซื้อ","🟡 เฝ้าระวัง","⚪ ถือ","🔴 ขาย"],
                default=["🟢 ซื้อ","🟡 เฝ้าระวัง"], key="filt_sig", label_visibility="collapsed",
                placeholder="เลือกสัญญาณ"
            )
        with col_f2:
            sort_by = st.selectbox("เรียงตาม", ["Score ↓","RSI ↑","Change% ↓","ADX ↓"],
                key="sort_by", label_visibility="collapsed")

        # SCAN BUTTON
        st.markdown('<div class="section-title">2️⃣ เริ่มสแกน</div>', unsafe_allow_html=True)
        scan_btn = st.button(f"🔍 สแกน {mkt['flag']} {mkt_key} ({n_stocks} หุ้น)", use_container_width=True)

        if scan_btn:
            prog = st.progress(0)
            with st.spinner(f"กำลังสแกน {mkt_key}..."):
                df_res = scan_market(mkt_key, params, lambda v: prog.progress(v))
            prog.empty()
            st.session_state.scan_results[mkt_key] = df_res

        # RESULTS
        df_res = st.session_state.scan_results.get(mkt_key)
        if df_res is not None and len(df_res) > 0:
            # Filter
            sig_f = filt_sig if filt_sig else ["🟢 ซื้อ","🟡 เฝ้าระวัง","⚪ ถือ","🔴 ขาย"]
            df_f = df_res[
                (df_res["Score"] >= st.session_state.get("min_score", 60)) &
                (df_res["RR"]    >= st.session_state.get("min_rr", 1.5)) &
                (df_res["ADX"]   >= st.session_state.get("min_adx", 18)) &
                (df_res["Signal"].isin(sig_f))
            ].copy()

            sort_map = {"Score ↓":"Score","RSI ↑":"RSI","Change% ↓":"Change","ADX ↓":"ADX"}
            sort_asc = {"Score ↓":False,"RSI ↑":True,"Change% ↓":False,"ADX ↓":False}
            col_s = sort_map.get(sort_by,"Score")
            df_f = df_f.sort_values(col_s, ascending=sort_asc.get(sort_by,False))

            # Summary row
            buy_n = len(df_res[df_res["SigCls"]=="buy"])
            sell_n = len(df_res[df_res["SigCls"]=="sell"])
            watch_n = len(df_res[df_res["SigCls"]=="watch"])
            avg_sc = df_res["Score"].mean()

            st.markdown(f"""
            <div class="update-bar">
                <span>พบ <strong style="color:#e2e8f0;">{len(df_f)}</strong> / {len(df_res)} หุ้น</span>
                <span>🟢{buy_n} 🟡{watch_n} 🔴{sell_n} · avg {avg_sc:.0f}pt</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-title">3️⃣ ผลการสแกน — แตะหุ้นเพื่อวิเคราะห์เจาะลึก</div>', unsafe_allow_html=True)

            if len(df_f) == 0:
                st.markdown('<div class="empty-state">ไม่มีหุ้นผ่านเงื่อนไข<br>ลองปรับ Parameters ด้านบน</div>', unsafe_allow_html=True)
            else:
                for _, row in df_f.iterrows():
                    chg_cls = "change-up" if row["Change"] >= 0 else "change-dn"
                    chip_cls = f"chip-{row['SigCls']}"
                    score_cls = "score-h" if row["Score"]>=65 else "score-m" if row["Score"]>=45 else "score-l"
                    chg_sym = "+" if row["Change"] >= 0 else ""

                    st.markdown(f"""
                    <div class="stock-card {row['SigCls']}">
                        <div class="sc-top">
                            <div>
                                <div class="sc-symbol">{row['Symbol']}</div>
                                <div class="sc-name">{row['Name']}</div>
                            </div>
                            <div>
                                <div class="sc-price">{cur}{row['Price']:.2f}</div>
                                <div class="sc-change {chg_cls}">{chg_sym}{row['Change']:.2f}%</div>
                            </div>
                        </div>
                        <div class="sc-bars">
                            <div class="sc-bar-item">
                                <div class="sc-bar-label">RSI</div>
                                <div class="sc-bar-val {'bull' if row['RSI']<params['rsi_os'] else 'bear' if row['RSI']>params['rsi_ob'] else ''}">{row['RSI']:.0f}</div>
                            </div>
                            <div class="sc-bar-item">
                                <div class="sc-bar-label">ADX</div>
                                <div class="sc-bar-val">{row['ADX']:.0f}</div>
                            </div>
                            <div class="sc-bar-item">
                                <div class="sc-bar-label">BB%</div>
                                <div class="sc-bar-val {'bull' if row['BB']<0.2 else 'bear' if row['BB']>0.8 else ''}">{row['BB']:.2f}</div>
                            </div>
                            <div class="sc-bar-item">
                                <div class="sc-bar-label">Vol</div>
                                <div class="sc-bar-val {'bull' if row['VR']>1.5 else ''}">{row['VR']:.1f}x</div>
                            </div>
                        </div>
                        <div class="target-row" style="margin-top:8px;">
                            <div class="tgt"><div class="tgt-label">ซื้อ</div><div class="tgt-val tgt-entry" style="font-size:0.72rem;">{cur}{row['Entry']:.2f}</div></div>
                            <div class="tgt"><div class="tgt-label">เป้า 1</div><div class="tgt-val tgt-t1" style="font-size:0.72rem;">{cur}{row['T1']:.2f}</div></div>
                            <div class="tgt"><div class="tgt-label">เป้า 2</div><div class="tgt-val tgt-t2" style="font-size:0.72rem;">{cur}{row['T2']:.2f}</div></div>
                            <div class="tgt"><div class="tgt-label">SL</div><div class="tgt-val tgt-sl" style="font-size:0.72rem;">{cur}{row['SL']:.2f}</div></div>
                        </div>
                        <div class="sc-bottom">
                            <div>
                                <span class="signal-chip {chip_cls}">{row['Signal']}</span>
                                <span class="rr-badge" style="margin-left:8px;">R/R <span class="rr-val">1:{row['RR']:.2f}</span></span>
                            </div>
                            <div class="score-ring {score_cls}">{row['Score']:.0f}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"🔍 วิเคราะห์ {row['Symbol']} เจาะลึก", key=f"btn_{row['Symbol']}_{mkt_key}", use_container_width=True):
                        st.session_state.detail_sym = row["Symbol"]
                        st.session_state.detail_mkt = mkt_key
                        st.session_state.view = "detail"
                        st.rerun()

    else:
        st.markdown("""
        <div class="empty-state">
            👆 เลือกตลาดหุ้นที่ต้องการสแกน<br>
            <span style="font-size:0.75rem;">SET · US Tech · CN Tech</span>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;padding:20px 0 10px;color:#2a2a4a;font-size:0.7rem;">
⚠️ ใช้เพื่อการศึกษาเท่านั้น · ไม่ใช่คำแนะนำการลงทุน
</div>
""", unsafe_allow_html=True)
