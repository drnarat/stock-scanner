"""
╔══════════════════════════════════════════════════════════════╗
║         AI Stock Scanner Pro — v3 Real-time Edition          ║
║  Settrade API + Deep Analysis + Mobile-first UI              ║
╚══════════════════════════════════════════════════════════════╝

วิธีติดตั้ง:
    pip install streamlit pandas numpy settrade-v2 requests

วิธีรัน:
    streamlit run stock_analyzer_v3.py --server.address=0.0.0.0 --server.port=8501

ข้อมูล Credential ขอได้ที่:
    https://developer.settrade.com → สร้าง App → ได้ APP_ID + APP_SECRET
"""

import streamlit as st
import pandas as pd
import numpy as np
import time, json, traceback
from datetime import datetime, timedelta

# ─── ลอง import settrade_v2 ────────────────────────────────────
try:
    from settrade_v2 import Investor
    SETTRADE_AVAILABLE = True
except ImportError:
    SETTRADE_AVAILABLE = False

# ─── ลอง import yfinance (fallback สำหรับหุ้นต่างประเทศ) ───────
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="📈 Stock Scanner Pro",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;background:#0d0d14;color:#e2e8f0}
footer{visibility:hidden} #MainMenu{visibility:hidden}
header[data-testid="stHeader"]{background:#0d0d14!important}
div[data-testid="stSidebar"]{background:#12122a!important}

/* ── APP HEADER ── */
.app-header{background:linear-gradient(135deg,#12122a,#1a1035,#0f1f3a);border:1px solid rgba(108,99,255,.3);border-radius:16px;padding:18px 16px 14px;text-align:center;margin-bottom:16px;box-shadow:0 4px 24px rgba(108,99,255,.2)}
.app-header h1{font-size:1.4rem;font-weight:700;color:#fff}
.app-header .sub{font-size:.75rem;color:#8892b0;margin-top:4px}
.live-dot{display:inline-block;width:8px;height:8px;background:#00b894;border-radius:50%;margin-right:5px;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.3)}}

/* ── LOGIN CARD ── */
.login-card{background:linear-gradient(135deg,#12122a,#1a1a2e);border:1px solid rgba(108,99,255,.35);border-radius:20px;padding:24px 20px;margin:8px 0 20px}
.login-card h2{font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:4px}
.login-card .login-sub{font-size:.78rem;color:#8892b0;margin-bottom:20px;line-height:1.6}
.info-box{background:rgba(108,99,255,.08);border:1px solid rgba(108,99,255,.25);border-radius:10px;padding:12px;margin-bottom:16px;font-size:.78rem;color:#a8b2d8;line-height:1.7}
.info-box a{color:#6c63ff;text-decoration:none}
.warn-box{background:rgba(253,203,110,.08);border:1px solid rgba(253,203,110,.3);border-radius:10px;padding:10px 12px;margin-bottom:14px;font-size:.75rem;color:#fdcb6e;line-height:1.6}
.success-box{background:rgba(0,184,148,.1);border:1px solid rgba(0,184,148,.4);border-radius:10px;padding:12px;font-size:.82rem;color:#00b894;line-height:1.6}
.error-box{background:rgba(214,48,49,.1);border:1px solid rgba(214,48,49,.4);border-radius:10px;padding:12px;font-size:.82rem;color:#ff7675;line-height:1.6}

/* ── SECTION TITLE ── */
.section-title{font-size:.72rem;font-weight:700;color:#8892b0;text-transform:uppercase;letter-spacing:1px;margin:16px 0 10px;display:flex;align-items:center;gap:6px}
.section-title::after{content:'';flex:1;height:1px;background:#2a2a4a}

/* ── MARKET BUTTON ── */
.mkt-label{text-align:center;padding:2px 0 6px}
.mkt-flag{font-size:1.6rem;display:block}
.mkt-name{font-size:.75rem;font-weight:700;color:#e2e8f0}
.mkt-desc{font-size:.65rem;color:#8892b0}

/* ── STOCK CARD ── */
.stock-card{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:14px;padding:14px;margin-bottom:10px;position:relative}
.stock-card.buy {border-left:4px solid #00b894}
.stock-card.sell{border-left:4px solid #d63031}
.stock-card.watch{border-left:4px solid #fdcb6e}
.stock-card.neutral{border-left:4px solid #636e72}
.sc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.sc-symbol{font-size:1.05rem;font-weight:700;color:#fff;font-family:'IBM Plex Mono',monospace}
.sc-name{font-size:.72rem;color:#8892b0;margin-top:2px}
.sc-price{font-size:1.05rem;font-weight:700;color:#fff;text-align:right;font-family:'IBM Plex Mono',monospace}
.sc-change{font-size:.72rem;text-align:right;margin-top:2px;font-weight:600}
.change-up{color:#00b894} .change-dn{color:#d63031}
.sc-bars{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:10px}
.sc-bar-item{text-align:center}
.sc-bar-label{font-size:.62rem;color:#636e72;text-transform:uppercase}
.sc-bar-val{font-size:.8rem;font-weight:600;color:#e2e8f0;font-family:'IBM Plex Mono',monospace}
.sc-bottom{display:flex;justify-content:space-between;align-items:center;margin-top:10px}
.score-ring{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.85rem;font-weight:700;font-family:'IBM Plex Mono',monospace;flex-shrink:0}
.score-h{background:rgba(0,184,148,.2);border:2px solid #00b894;color:#00b894}
.score-m{background:rgba(253,203,110,.2);border:2px solid #fdcb6e;color:#fdcb6e}
.score-l{background:rgba(214,48,49,.2);border:2px solid #d63031;color:#d63031}
.signal-chip{font-size:.75rem;font-weight:700;padding:4px 10px;border-radius:12px;display:inline-block}
.chip-buy{background:rgba(0,184,148,.15);color:#00b894;border:1px solid #00b89460}
.chip-sell{background:rgba(214,48,49,.15);color:#d63031;border:1px solid #d6303160}
.chip-watch{background:rgba(253,203,110,.15);color:#fdcb6e;border:1px solid #fdcb6e60}
.chip-neutral{background:rgba(99,110,114,.15);color:#636e72;border:1px solid #63637260}
.target-row{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;margin-top:8px}
.tgt{background:#12122a;border-radius:8px;padding:7px 4px;text-align:center}
.tgt-label{font-size:.6rem;color:#636e72;text-transform:uppercase;letter-spacing:.5px}
.tgt-val{font-size:.78rem;font-weight:700;font-family:'IBM Plex Mono',monospace;margin-top:2px}
.tgt-entry{color:#6c63ff} .tgt-t1{color:#00b894} .tgt-t2{color:#00cec9} .tgt-sl{color:#d63031}

/* ── DEEP ANALYSIS ── */
.da-header{background:linear-gradient(135deg,#12122a,#1a1035);border:1px solid rgba(108,99,255,.4);border-radius:14px;padding:16px;margin-bottom:14px}
.da-symbol{font-size:1.5rem;font-weight:700;color:#fff;font-family:'IBM Plex Mono',monospace}
.da-price{font-size:1.8rem;font-weight:700;font-family:'IBM Plex Mono',monospace}
.da-market-tag{display:inline-block;font-size:.68rem;font-weight:700;padding:3px 8px;border-radius:8px;margin-left:8px;vertical-align:middle}
.tag-th{background:#1a3a1a;color:#00b894;border:1px solid #00b89440}
.tag-us{background:#1a1a3a;color:#6c63ff;border:1px solid #6c63ff40}
.tag-cn{background:#3a1a1a;color:#d63031;border:1px solid #d6303140}
.tag-manual{background:#2a1a3a;color:#a29bfe;border:1px solid #a29bfe40}
.ind-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.ind-box{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:10px;padding:10px;display:flex;flex-direction:column;gap:2px}
.ind-label{font-size:.65rem;color:#636e72;text-transform:uppercase;letter-spacing:.5px}
.ind-val{font-size:.95rem;font-weight:700;font-family:'IBM Plex Mono',monospace}
.ind-status{font-size:.65rem;margin-top:1px}
.bull{color:#00b894} .bear{color:#d63031} .neut{color:#fdcb6e}
.sig-item{border-radius:10px;padding:9px 12px;margin-bottom:6px;font-size:.8rem;line-height:1.5;border-left:3px solid}
.sig-buy{background:rgba(0,184,148,.08);border-color:#00b894;color:#b2f5ea}
.sig-sell{background:rgba(214,48,49,.08);border-color:#d63031;color:#fed7d7}
.sig-neut{background:rgba(99,110,114,.08);border-color:#636e72;color:#cbd5e0}
.pivot-row{display:flex;gap:6px;overflow-x:auto;padding-bottom:4px;margin-bottom:14px;-webkit-overflow-scrolling:touch}
.pvt-box{flex-shrink:0;background:#1a1a2e;border-radius:10px;padding:8px 12px;text-align:center;min-width:72px;border:1px solid #2a2a4a}
.pvt-label{font-size:.6rem;color:#636e72;text-transform:uppercase}
.pvt-val{font-size:.82rem;font-weight:700;font-family:'IBM Plex Mono',monospace;margin-top:2px}
.fundamental-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.fund-box{background:#1a1a2e;border:1px solid #2a2a4a;border-radius:10px;padding:10px}
.fund-label{font-size:.65rem;color:#636e72;text-transform:uppercase;letter-spacing:.5px}
.fund-val{font-size:1rem;font-weight:700;font-family:'IBM Plex Mono',monospace;color:#e2e8f0;margin-top:2px}
.fund-desc{font-size:.65rem;color:#8892b0;margin-top:2px}
.update-bar{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#12122a;border-radius:10px;font-size:.7rem;color:#636e72;margin-bottom:12px}

/* ── BUTTONS ── */
div.stButton>button{width:100%;background:linear-gradient(135deg,#6c63ff,#4f46e5);color:#fff;border:none;border-radius:12px;padding:14px;font-size:.95rem;font-weight:700;font-family:'Sarabun',sans-serif;box-shadow:0 4px 16px rgba(108,99,255,.35);transition:all .2s}
div.stButton>button:hover{opacity:.9;transform:translateY(-1px)}
div.stButton>button:active{transform:scale(.97)}
div[data-testid="stTextInput"]>div>div>input{background:#1a1a2e!important;border:1px solid #2a2a4a!important;border-radius:10px!important;color:#e2e8f0!important;font-family:'IBM Plex Mono',monospace!important}
div[data-testid="stSelectbox"]>label,div[data-testid="stSlider"]>label{color:#8892b0!important;font-size:.82rem!important}
div[data-testid="stExpander"]{background:#1a1a2e;border:1px solid #2a2a4a!important;border-radius:12px!important;margin-bottom:8px}
div[data-testid="stTabs"]>div>div[role="tablist"]>button{color:#8892b0!important;font-size:.82rem!important}
div[data-testid="stTabs"]>div>div[role="tablist"]>button[aria-selected="true"]{color:#e2e8f0!important;border-bottom-color:#6c63ff!important}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# STOCK UNIVERSE
# ══════════════════════════════════════════════════════════════
MARKETS = {
    "SET": {
        "flag":"🇹🇭","name":"ตลาดหุ้นไทย","desc":"SET50/100/mai","currency":"฿","tag":"tag-th",
        "stocks":[
            ("KBANK","กสิกรไทย"),("BBL","กรุงเทพ"),("SCB","ไทยพาณิชย์"),
            ("KTB","กรุงไทย"),("BAY","กรุงศรี"),("TISCO","ทิสโก้"),("KKP","เกียรตินาคิน"),
            ("PTT","ปตท."),("PTTEP","ปตท.สผ."),("GULF","กัลฟ์"),("GPSC","โกลบอลเพาเวอร์"),
            ("RATCH","ราช กรุ๊ป"),("BGRIM","บี.กริม"),("EGCO","เอ็กโก"),
            ("ADVANC","แอดวานซ์"),("TRUE","ทรู"),("MFEC","MFEC"),("BE8","บี8"),
            ("CPALL","ซีพีออลล์"),("CRC","เซ็นทรัล รีเทล"),("HMPRO","โฮมโปร"),
            ("MAKRO","แม็คโคร"),("BJC","บีเจซี"),
            ("CPF","ซีพีเอฟ"),("TU","ไทยยูเนี่ยน"),("GFPT","จีเอฟพีที"),("BTG","บีทาเก้น"),
            ("LH","แลนด์แอนด์เฮาส์"),("AP","เอพี"),("SIRI","แสนสิริ"),("QH","ควอลิตี้เฮ้าส์"),
            ("AOT","ท่าอากาศยาน"),("AAV","เอเชีย เอวิเอชั่น"),("CENTEL","เซ็นทารา"),
            ("MINT","ไมเนอร์"),("ERW","อีอาร์ดับบิ้ว"),
            ("BDMS","กรุงเทพดุสิต"),("BGH","กรุงเทพ"),("BCH","บางกอก"),
            ("SCC","ปูนซิเมนต์ไทย"),("PTTGC","พีทีที โกลบอล"),("IRPC","IRPC"),
            ("MTC","เมืองไทย แคปปิตอล"),("TIDLOR","ไทยเดินทาง"),("SAWAD","ศาวะดี"),
        ],
    },
    "US": {
        "flag":"🇺🇸","name":"US Tech","desc":"NASDAQ/NYSE","currency":"$","tag":"tag-us",
        "stocks":[
            ("AAPL","Apple"),("MSFT","Microsoft"),("NVDA","NVIDIA"),("GOOGL","Alphabet"),
            ("META","Meta"),("AMZN","Amazon"),("TSLA","Tesla"),("AMD","AMD"),
            ("INTC","Intel"),("AVGO","Broadcom"),("QCOM","Qualcomm"),("MU","Micron"),
            ("AMAT","Applied Materials"),("CRM","Salesforce"),("ADBE","Adobe"),
            ("NOW","ServiceNow"),("PLTR","Palantir"),("ORCL","Oracle"),
        ],
    },
    "CN": {
        "flag":"🇨🇳","name":"CN Tech","desc":"NYSE/NASDAQ ADR","currency":"$","tag":"tag-cn",
        "stocks":[
            ("BABA","Alibaba"),("JD","JD.com"),("BIDU","Baidu"),("NTES","NetEase"),
            ("PDD","Pinduoduo"),("TCOM","Trip.com"),("NIO","NIO"),("XPEV","XPeng"),
            ("LI","Li Auto"),("BILI","Bilibili"),("WB","Weibo"),("FUTU","Futu"),
        ],
    },
}

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
defaults = dict(
    logged_in=False, market_api=None, realtime_api=None,
    app_id="", app_secret="", app_code="", broker_id="",
    market=None, scan_results={}, view="login",
    detail_sym=None, detail_mkt=None,
)
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
# TECHNICAL INDICATOR FUNCTIONS
# ══════════════════════════════════════════════════════════════
def _sma(s,n): return s.rolling(n).mean()
def _ema(s,n): return s.ewm(span=n,adjust=False).mean()

def _rsi(s,n=14):
    d=s.diff(); g=d.clip(lower=0).rolling(n).mean(); l=(-d.clip(upper=0)).rolling(n).mean()
    return 100-100/(1+g/(l+1e-9))

def _macd(s,f=12,sl=26,sg=9):
    ml=_ema(s,f)-_ema(s,sl); sig=_ema(ml,sg); return ml,sig,ml-sig

def _bbands(s,n=20,k=2):
    m=_sma(s,n); std=s.rolling(n).std()
    up,lo=m+k*std,m-k*std; pct=(s-lo)/(up-lo+1e-9)
    return up,m,lo,pct

def _stoch(h,l,c,kp=14,dp=3):
    ll=l.rolling(kp).min(); hh=h.rolling(kp).max()
    k=100*(c-ll)/(hh-ll+1e-9); return k,k.rolling(dp).mean()

def _atr(h,l,c,n=14):
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def _cci(h,l,c,n=20):
    tp=(h+l+c)/3; m=tp.rolling(n).mean()
    mad=tp.rolling(n).apply(lambda x:np.abs(x-x.mean()).mean())
    return (tp-m)/(0.015*mad+1e-9)

def _wr(h,l,c,n=14):
    return -100*(h.rolling(n).max()-c)/(h.rolling(n).max()-l.rolling(n).min()+1e-9)

def _mfi(h,l,c,v,n=14):
    tp=(h+l+c)/3; mf=tp*v
    pos=mf.where(tp>tp.shift(),0).rolling(n).sum()
    neg=mf.where(tp<tp.shift(),0).rolling(n).sum()
    return 100-100/(1+pos/(neg+1e-9))

def _adx(h,l,c,n=14):
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    dmp=(h-h.shift()).clip(lower=0); dmm=(l.shift()-l).clip(lower=0)
    dmp=dmp.where(dmp>dmm,0); dmm=dmm.where(dmm>dmp,0)
    atr14=tr.rolling(n).mean()
    dip=100*dmp.rolling(n).mean()/(atr14+1e-9)
    dim=100*dmm.rolling(n).mean()/(atr14+1e-9)
    dx=100*(dip-dim).abs()/(dip+dim+1e-9)
    return dx.rolling(n).mean(),dip,dim

def _obv(c,v):
    return (v*np.sign(c.diff()).fillna(0)).cumsum()

def _vwap(h,l,c,v):
    tp=(h+l+c)/3; return (tp*v).cumsum()/(v.cumsum()+1e-9)

def _ichimoku(h,l,n1=9,n2=26,n3=52):
    conv=(h.rolling(n1).max()+l.rolling(n1).min())/2
    base=(h.rolling(n2).max()+l.rolling(n2).min())/2
    span_a=((conv+base)/2).shift(n2)
    span_b=((h.rolling(n3).max()+l.rolling(n3).min())/2).shift(n2)
    return conv,base,span_a,span_b

def compute_all(df, p):
    """คำนวณ indicator ทั้งหมด — คืน dict ของค่าล่าสุด"""
    c,h,l,v = df["close"],df["high"],df["low"],df["volume"]
    I={}
    # Moving Averages
    for n,k in [(p["sma_s"],"sma_s"),(p["sma_m"],"sma_m"),(p["sma_l"],"sma_l")]:
        I[f"sma{n}"] = _sma(c,n).iloc[-1]
    I["ema_f"] = _ema(c,p["ema_f"]).iloc[-1]
    I["ema_s"] = _ema(c,p["ema_s"]).iloc[-1]
    # RSI
    I["rsi"] = _rsi(c,p["rsi_p"]).iloc[-1]
    # MACD
    ml,ms,mh = _macd(c,p["macd_f"],p["macd_s"],p["macd_sg"])
    I["macd"],I["macd_sig"],I["macd_h"] = ml.iloc[-1],ms.iloc[-1],mh.iloc[-1]
    # Bollinger
    bbu,bbm,bbl,bbp = _bbands(c,p["bb_p"],p["bb_k"])
    I["bbu"],I["bbm"],I["bbl"],I["bbp"] = bbu.iloc[-1],bbm.iloc[-1],bbl.iloc[-1],bbp.iloc[-1]
    I["bb_width"] = ((bbu-bbl)/bbm*100).iloc[-1]
    # Stochastic
    sk,sd = _stoch(h,l,c,p["stoch_k"],p["stoch_d"])
    I["sk"],I["sd"] = sk.iloc[-1],sd.iloc[-1]
    # ATR
    I["atr"] = _atr(h,l,c,p["atr_p"]).iloc[-1]
    I["atr_pct"] = I["atr"]/c.iloc[-1]*100
    # CCI, Williams %R
    I["cci"] = _cci(h,l,c,p["cci_p"]).iloc[-1]
    I["wr"]  = _wr(h,l,c,p["wr_p"]).iloc[-1]
    # MFI
    I["mfi"] = _mfi(h,l,c,v,p["mfi_p"]).iloc[-1]
    # ADX
    adx_v,dip,dim = _adx(h,l,c,p["adx_p"])
    I["adx"],I["dip"],I["dim"] = adx_v.iloc[-1],dip.iloc[-1],dim.iloc[-1]
    # OBV trend
    obv = _obv(c,v)
    I["obv_trend"] = "up" if obv.iloc[-1]>obv.iloc[-5] else "down"
    # VWAP
    I["vwap"] = _vwap(h,l,c,v).iloc[-1]
    # Volume
    I["vol_avg"] = v.rolling(20).mean().iloc[-1]
    I["vol_r"]   = v.iloc[-1]/(I["vol_avg"]+1)
    # Ichimoku
    conv,base,sa,sb = _ichimoku(h,l)
    I["ichi_conv"],I["ichi_base"] = conv.iloc[-1],base.iloc[-1]
    I["ichi_sa"],I["ichi_sb"]     = sa.iloc[-1],sb.iloc[-1]
    # Price & Change
    I["price"]  = c.iloc[-1]
    I["open"]   = df["open"].iloc[-1]
    I["high_d"] = h.iloc[-1]
    I["low_d"]  = l.iloc[-1]
    I["chg"]    = (c.iloc[-1]/c.iloc[-2]-1)*100
    I["chg_5d"] = (c.iloc[-1]/c.iloc[-5]-1)*100
    I["chg_20d"]= (c.iloc[-1]/c.iloc[-20]-1)*100
    I["52wh"]   = h.rolling(min(252,len(h))).max().iloc[-1]
    I["52wl"]   = l.rolling(min(252,len(l))).min().iloc[-1]
    # Pivot
    pv=(h.iloc[-1]+l.iloc[-1]+c.iloc[-1])/3; rng=h.iloc[-1]-l.iloc[-1]
    I["pivot"]=pv; I["r1"]=2*pv-l.iloc[-1]; I["r2"]=pv+rng
    I["s1"]=2*pv-h.iloc[-1]; I["s2"]=pv-rng
    # Price vs key levels
    I["price_sma_s"] = I["price"]/I[f"sma{p['sma_s']}"]-1
    I["price_sma_m"] = I["price"]/I[f"sma{p['sma_m']}"]-1
    I["price_sma_l"] = I["price"]/I[f"sma{p['sma_l']}"]-1
    return I

def score_and_signal(I, p):
    ob,os_=p["rsi_ob"],p["rsi_os"]
    bs,ss,ns=[],[],[]; sc=50

    r=I["rsi"]
    if r<os_:   sc+=8;  bs.append(f"RSI {r:.1f} < {os_} → Oversold โซนซื้อ")
    elif r>ob:  sc-=8;  ss.append(f"RSI {r:.1f} > {ob} → Overbought โซนขาย")
    else:               ns.append(f"RSI {r:.1f} อยู่ในโซนปกติ")

    if I["macd"]>I["macd_sig"] and I["macd_h"]>0:  sc+=7;bs.append("MACD ตัดขึ้น Signal → โมเมนตัมขาขึ้น")
    elif I["macd"]<I["macd_sig"] and I["macd_h"]<0: sc-=7;ss.append("MACD ตัดลง Signal → โมเมนตัมขาลง")

    pr=I["price"]
    sma_s_v=I[f"sma{p['sma_s']}"]; sma_m_v=I[f"sma{p['sma_m']}"]; sma_l_v=I[f"sma{p['sma_l']}"]
    if pr>sma_s_v>sma_m_v:  sc+=6;bs.append(f"ราคา > SMA{p['sma_s']} > SMA{p['sma_m']} → uptrend")
    elif pr<sma_s_v<sma_m_v:sc-=6;ss.append(f"ราคา < SMA{p['sma_s']} < SMA{p['sma_m']} → downtrend")
    if pr>sma_l_v: sc+=4;bs.append(f"ราคา > SMA{p['sma_l']} → เหนือค่าเฉลี่ยระยะยาว")
    else:          sc-=4;ss.append(f"ราคา < SMA{p['sma_l']} → ต่ำกว่าค่าเฉลี่ยระยะยาว")

    if I["bbp"]<0.15:  sc+=6;bs.append(f"BB% {I['bbp']:.2f} ใกล้ Lower → oversold")
    elif I["bbp"]>0.85:sc-=5;ss.append(f"BB% {I['bbp']:.2f} ใกล้ Upper → overbought")
    if pr>I["bbu"]: sc+=3;bs.append("Breakout เหนือ BB Upper → momentum")

    sk,sd=I["sk"],I["sd"]
    if sk<20 and sk>sd: sc+=5;bs.append(f"Stoch %K {sk:.1f} ตัดขึ้น %D ในโซน oversold")
    elif sk>80 and sk<sd:sc-=5;ss.append(f"Stoch %K {sk:.1f} ตัดลง %D ในโซน overbought")

    cci_v=I["cci"]
    if cci_v<-100: sc+=4;bs.append(f"CCI {cci_v:.1f} < -100 → oversold")
    elif cci_v>100:sc-=4;ss.append(f"CCI {cci_v:.1f} > 100 → overbought")

    wr_v=I["wr"]
    if wr_v<-80:  sc+=4;bs.append(f"Williams %R {wr_v:.1f} < -80 → oversold")
    elif wr_v>-20:sc-=4;ss.append(f"Williams %R {wr_v:.1f} > -20 → overbought")

    adx_v=I["adx"]
    if adx_v>25:
        if I["dip"]>I["dim"]: sc+=5;bs.append(f"ADX {adx_v:.1f} + DI+>DI- → uptrend แข็งแกร่ง")
        else:                  sc-=5;ss.append(f"ADX {adx_v:.1f} + DI->DI+ → downtrend แข็งแกร่ง")
    else: ns.append(f"ADX {adx_v:.1f} < 25 → sideways ไม่มีแนวโน้มชัด")

    mfi_v=I["mfi"]
    if mfi_v<20:  sc+=4;bs.append(f"MFI {mfi_v:.1f} < 20 → เงินไหลออกมาก (โอกาสดีดกลับ)")
    elif mfi_v>80:sc-=4;ss.append(f"MFI {mfi_v:.1f} > 80 → เงินไหลเข้าเกิน (ระวังแรงขาย)")

    if I["obv_trend"]=="up":  sc+=3;bs.append("OBV เป็นขาขึ้น → แรงซื้อสะสม")
    else:                      sc-=2;ss.append("OBV เป็นขาลง → แรงขายสะสม")

    if pr>I["vwap"]: sc+=3;bs.append("ราคา > VWAP → แรงซื้อจากสถาบัน")
    else:             sc-=3;ss.append("ราคา < VWAP → แรงขายจากสถาบัน")

    if I["vol_r"]>1.5: sc+=3;bs.append(f"Volume {I['vol_r']:.1f}x ค่าเฉลี่ย → มีนัยสำคัญ")
    elif I["vol_r"]<0.5:ns.append(f"Volume {I['vol_r']:.1f}x → ต่ำ ระวังสัญญาณหลอก")

    # Ichimoku
    if pr>I["ichi_sa"] and pr>I["ichi_sb"]:
        sc+=4;bs.append("ราคาอยู่เหนือ Ichimoku Cloud → bullish")
    elif pr<I["ichi_sa"] and pr<I["ichi_sb"]:
        sc-=4;ss.append("ราคาอยู่ใต้ Ichimoku Cloud → bearish")

    sc=max(0,min(100,sc))
    if sc>=65:   rec,cls="🟢 ซื้อ","buy"
    elif sc<=35: rec,cls="🔴 ขาย","sell"
    elif sc>=55: rec,cls="🟡 เฝ้าระวัง","watch"
    else:        rec,cls="⚪ ถือ","neutral"

    at=I["atr"]
    entry=round(pr*0.985,2); t1=round(pr+at*2,2); t2=round(pr+at*3.5,2); sl=round(pr-at*1.5,2)
    up=round((t1/pr-1)*100,1) if pr>0 else 0
    dn=round((pr/sl-1)*100,1) if sl>0 else 1
    rr=round(up/dn,2) if dn>0 else 0

    return dict(sc=sc,rec=rec,cls=cls,bs=bs,ss=ss,ns=ns,entry=entry,t1=t1,t2=t2,sl=sl,up=up,dn=dn,rr=rr)

# ══════════════════════════════════════════════════════════════
# DATA FETCHING  (Settrade API / yfinance fallback)
# ══════════════════════════════════════════════════════════════
def fetch_candles_settrade(symbol, market_api, limit=200):
    """ดึงข้อมูลราคาย้อนหลังจาก Settrade API"""
    raw = market_api.get_candlestick(symbol, interval="1d", limit=limit)
    df  = pd.DataFrame(raw)
    # Settrade อาจใช้คอลัมน์ต่างกัน — normalize
    col_map = {"last":"close","c":"close","o":"open","h":"high","l":"low","v":"volume",
               "close":"close","open":"open","high":"high","low":"low","volume":"volume"}
    df.rename(columns={c:col_map.get(c,c) for c in df.columns}, inplace=True)
    for col in ["close","open","high","low","volume"]:
        if col not in df.columns:
            if col=="open":   df["open"]   = df["close"]
            elif col=="high": df["high"]   = df["close"]
            elif col=="low":  df["low"]    = df["close"]
            elif col=="volume":df["volume"]= pd.Series([1e6]*len(df))
    df = df[["open","high","low","close","volume"]].apply(pd.to_numeric, errors="coerce").dropna()
    return df

def fetch_quote_settrade(symbol, realtime_api):
    """ดึง real-time quote จาก Settrade"""
    q = realtime_api.get_quote_symbol(symbol)
    return q

def fetch_candles_yfinance(symbol, period="1y"):
    """ดึงข้อมูลจาก yfinance (สำหรับหุ้นต่างประเทศ หรือ fallback)"""
    if not YFINANCE_AVAILABLE:
        raise RuntimeError("yfinance ไม่ได้ติดตั้ง: pip install yfinance")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    df = df[["Open","High","Low","Close","Volume"]].copy()
    df.columns = ["open","high","low","close","volume"]
    df = df.dropna()
    return df, ticker.info

def fetch_candles_mock(symbol, n=200):
    """Mock data — ใช้เมื่อ API ยังไม่พร้อม"""
    np.random.seed(abs(hash(symbol))%99999)
    base=np.random.uniform(8,600)
    c=[base]
    for _ in range(n-1): c.append(max(c[-1]*(1+np.random.normal(0,.014)),.5))
    c=np.array(c)
    h=c*np.random.uniform(1.001,1.025,n); l=c*np.random.uniform(.975,.999,n)
    v=np.random.uniform(3e5,8e6,n).astype(int)
    return pd.DataFrame({"open":c,"high":h,"low":l,"close":c,"volume":v})

def get_data(symbol, mkt_key, use_settrade=True, p=None):
    """หา data อัตโนมัติ — ลอง Settrade ก่อน แล้ว fallback yfinance → mock"""
    info = {}
    mkt_api = st.session_state.market_api
    rt_api  = st.session_state.realtime_api

    if use_settrade and mkt_key=="SET" and mkt_api and rt_api:
        try:
            df    = fetch_candles_settrade(symbol, mkt_api)
            quote = fetch_quote_settrade(symbol, rt_api)
            # อัปเดตราคาล่าสุดจาก real-time quote
            if quote and "last" in quote:
                df.iloc[-1, df.columns.get_loc("close")] = float(quote["last"])
            info["source"] = "settrade_live"
            return df, info
        except Exception as e:
            info["settrade_err"] = str(e)

    # yfinance fallback (ใช้ได้กับ US/CN และ .BK สำหรับไทย)
    yf_sym = symbol+".BK" if mkt_key=="SET" else symbol
    if YFINANCE_AVAILABLE:
        try:
            df, yf_info = fetch_candles_yfinance(yf_sym)
            info["source"] = "yfinance"
            info["yf"] = yf_info
            return df, info
        except Exception as e:
            info["yf_err"] = str(e)

    # Mock fallback
    df = fetch_candles_mock(symbol)
    info["source"] = "mock"
    return df, info

# ══════════════════════════════════════════════════════════════
# DEFAULT PARAMS
# ══════════════════════════════════════════════════════════════
DEFAULT_PARAMS = dict(
    sma_s=20,sma_m=50,sma_l=200,ema_f=12,ema_s=26,
    rsi_p=14,rsi_ob=70,rsi_os=30,
    macd_f=12,macd_s=26,macd_sg=9,
    bb_p=20,bb_k=2,stoch_k=14,stoch_d=3,
    atr_p=14,cci_p=20,wr_p=14,mfi_p=14,adx_p=14,
    min_score=60,min_rr=1.5,min_adx=18,
)

def get_params():
    return {k: st.session_state.get(f"p_{k}", v) for k,v in DEFAULT_PARAMS.items()}

# ══════════════════════════════════════════════════════════════
# SHARED UI COMPONENTS
# ══════════════════════════════════════════════════════════════
def render_header():
    src_badge = ""
    if st.session_state.logged_in:
        src_badge = '<span style="background:rgba(0,184,148,.15);border:1px solid #00b89450;color:#00b894;font-size:.65rem;font-weight:700;padding:3px 8px;border-radius:8px;">⚡ Settrade Connected</span>'
    else:
        src_badge = '<span style="background:rgba(253,203,110,.1);border:1px solid #fdcb6e40;color:#fdcb6e;font-size:.65rem;font-weight:700;padding:3px 8px;border-radius:8px;">🔶 ยังไม่ได้ Login</span>'
    st.markdown(f"""
    <div class="app-header">
        <h1>📈 Stock Scanner Pro</h1>
        <div class="sub">
            <span class="live-dot"></span>Real-time · 15+ Indicators · 3 ตลาด &nbsp;{src_badge}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_param_expander():
    with st.expander("⚙️ ตั้งค่า Parameters", expanded=False):
        c1,c2=st.columns(2)
        with c1:
            st.slider("SMA สั้น",5,50,DEFAULT_PARAMS["sma_s"],key="p_sma_s")
            st.slider("SMA กลาง",20,100,DEFAULT_PARAMS["sma_m"],key="p_sma_m")
            st.slider("SMA ยาว",100,300,DEFAULT_PARAMS["sma_l"],key="p_sma_l")
            st.slider("EMA Fast",5,20,DEFAULT_PARAMS["ema_f"],key="p_ema_f")
            st.slider("EMA Slow",15,50,DEFAULT_PARAMS["ema_s"],key="p_ema_s")
            st.slider("RSI Period",7,21,DEFAULT_PARAMS["rsi_p"],key="p_rsi_p")
            st.slider("RSI Overbought",60,85,DEFAULT_PARAMS["rsi_ob"],key="p_rsi_ob")
            st.slider("RSI Oversold",15,40,DEFAULT_PARAMS["rsi_os"],key="p_rsi_os")
        with c2:
            st.slider("MACD Fast",8,20,DEFAULT_PARAMS["macd_f"],key="p_macd_f")
            st.slider("MACD Slow",20,40,DEFAULT_PARAMS["macd_s"],key="p_macd_s")
            st.slider("MACD Signal",5,15,DEFAULT_PARAMS["macd_sg"],key="p_macd_sg")
            st.slider("BB Period",10,30,DEFAULT_PARAMS["bb_p"],key="p_bb_p")
            st.slider("BB Std Dev",1,3,DEFAULT_PARAMS["bb_k"],key="p_bb_k")
            st.slider("Stoch %K",5,21,DEFAULT_PARAMS["stoch_k"],key="p_stoch_k")
            st.slider("Stoch %D",2,7,DEFAULT_PARAMS["stoch_d"],key="p_stoch_d")
            st.slider("ADX Period",7,21,DEFAULT_PARAMS["adx_p"],key="p_adx_p")
        c3,c4=st.columns(2)
        with c3:
            st.slider("ATR Period",7,21,DEFAULT_PARAMS["atr_p"],key="p_atr_p")
            st.slider("CCI Period",10,30,DEFAULT_PARAMS["cci_p"],key="p_cci_p")
            st.slider("Williams %R",7,21,DEFAULT_PARAMS["wr_p"],key="p_wr_p")
            st.slider("MFI Period",7,21,DEFAULT_PARAMS["mfi_p"],key="p_mfi_p")
        with c4:
            st.slider("คะแนนขั้นต่ำ",0,100,DEFAULT_PARAMS["min_score"],key="p_min_score")
            st.slider("R/R ขั้นต่ำ",0.5,5.0,float(DEFAULT_PARAMS["min_rr"]),step=0.5,key="p_min_rr")
            st.slider("ADX ขั้นต่ำ",0,40,DEFAULT_PARAMS["min_adx"],key="p_min_adx")

def render_deep_analysis(sym, mkt_key, I, S, info, yf_info=None):
    """แสดงผลวิเคราะห์เจาะลึก"""
    p = get_params()
    mkt  = MARKETS.get(mkt_key, {"flag":"🔍","name":"Custom","currency":"","tag":"tag-manual"})
    cur  = mkt["currency"]
    tag  = mkt.get("tag","tag-manual")
    pr   = I["price"]
    sc   = S["sc"]
    score_cls = "score-h" if sc>=65 else "score-m" if sc>=45 else "score-l"
    chip_cls  = f"chip-{S['cls']}"
    chg_cls   = "change-up" if I["chg"]>=0 else "change-dn"
    src_icon  = "⚡" if info.get("source")=="settrade_live" else "📡" if info.get("source")=="yfinance" else "🔶"
    src_label = {"settrade_live":"Settrade Live","yfinance":"Yahoo Finance","mock":"Mock Data"}.get(info.get("source","mock"),"")

    # Header card
    name_str = dict(mkt.get("stocks",[])).get(sym, sym)
    st.markdown(f"""
    <div class="da-header">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
        <div>
          <span class="da-symbol">{sym}</span>
          <span class="da-market-tag {tag}">{mkt['flag']} {mkt_key}</span>
          <div style="font-size:.72rem;color:#8892b0;margin-top:4px;">{name_str}</div>
        </div>
        <div class="score-ring {score_cls}" style="width:54px;height:54px;font-size:1.05rem;">{sc}</div>
      </div>
      <div style="margin-top:14px;display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:8px;">
        <div>
          <div class="da-price" style="color:{'#00b894' if I['chg']>=0 else '#d63031'}">{cur}{pr:,.2f}</div>
          <span class="sc-change {chg_cls}">{'+' if I['chg']>=0 else ''}{I['chg']:.2f}% วันนี้</span>
          &nbsp;<span style="color:#8892b0;font-size:.7rem;">{'+' if I['chg_5d']>=0 else ''}{I['chg_5d']:.1f}% 5วัน &nbsp; {'+' if I['chg_20d']>=0 else ''}{I['chg_20d']:.1f}% 20วัน</span>
        </div>
        <div style="text-align:right;">
          <div><span class="signal-chip {chip_cls}">{S['rec']}</span></div>
          <div style="font-size:.7rem;color:#8892b0;margin-top:5px;">R/R <span style="color:#6c63ff;font-weight:700;">1:{S['rr']:.2f}</span> &nbsp;↑{S['up']}% / ↓{S['dn']}%</div>
        </div>
      </div>
      <div style="margin-top:10px;font-size:.68rem;color:#636e72;">{src_icon} {src_label} · {datetime.now().strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

    # OHLCV row
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:12px;">
      <div class="tgt"><div class="tgt-label">เปิด</div><div class="tgt-val" style="color:#e2e8f0;">{cur}{I['open']:,.2f}</div></div>
      <div class="tgt"><div class="tgt-label">สูงสุด</div><div class="tgt-val tgt-t1">{cur}{I['high_d']:,.2f}</div></div>
      <div class="tgt"><div class="tgt-label">ต่ำสุด</div><div class="tgt-val tgt-sl">{cur}{I['low_d']:,.2f}</div></div>
      <div class="tgt"><div class="tgt-label">Vol Ratio</div><div class="tgt-val {'tgt-t1' if I['vol_r']>1.5 else ''}">{I['vol_r']:.1f}x</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Tab: เทคนิค / พื้นฐาน / เป้าหมาย / สัญญาณ
    tab_tech, tab_target, tab_sig, tab_fund = st.tabs(["📊 Technical","🎯 เป้าหมาย","🧠 สัญญาณ","📋 พื้นฐาน"])

    # ── TAB: TECHNICAL ──────────────────────────────────────
    with tab_tech:
        # Indicator grid
        def ib(lbl, val, is_b, is_s, sfx=""):
            cls_ = "bull" if is_b else "bear" if is_s else "neut"
            arrow = "▲ Bullish" if is_b else "▼ Bearish" if is_s else "→ Neutral"
            return f'<div class="ind-box"><div class="ind-label">{lbl}</div><div class="ind-val {cls_}">{val}{sfx}</div><div class="ind-status {cls_}">{arrow}</div></div>'

        sma_s_v=I[f"sma{p['sma_s']}"]; sma_m_v=I[f"sma{p['sma_m']}"]; sma_l_v=I[f"sma{p['sma_l']}"]
        ma_b=pr>sma_s_v>sma_m_v; ma_s=pr<sma_s_v<sma_m_v
        ichi_b=pr>I["ichi_sa"] and pr>I["ichi_sb"]
        ichi_s=pr<I["ichi_sa"] and pr<I["ichi_sb"]

        rows_html = [
            ib("RSI",f"{I['rsi']:.1f}",I["rsi"]<p["rsi_os"],I["rsi"]>p["rsi_ob"]),
            ib("MACD Hist",f"{I['macd_h']:.4f}",I["macd"]>I["macd_sig"],I["macd"]<I["macd_sig"]),
            ib(f"SMA{p['sma_s']}/{p['sma_m']}","Up" if ma_b else "Dn" if ma_s else "Flat",ma_b,ma_s),
            ib(f"SMA{p['sma_l']}",f"{cur}{sma_l_v:,.1f}",pr>sma_l_v,pr<sma_l_v),
            ib("BB %B",f"{I['bbp']:.2f}",I["bbp"]<0.2,I["bbp"]>0.8),
            ib("BB Width",f"{I['bb_width']:.1f}%",False,False),
            ib("Stoch %K",f"{I['sk']:.1f}",I["sk"]<20 and I["sk"]>I["sd"],I["sk"]>80 and I["sk"]<I["sd"]),
            ib("CCI",f"{I['cci']:.1f}",I["cci"]<-100,I["cci"]>100),
            ib("Williams %R",f"{I['wr']:.1f}",I["wr"]<-80,I["wr"]>-20),
            ib("MFI",f"{I['mfi']:.1f}",I["mfi"]<20,I["mfi"]>80),
            ib("ADX",f"{I['adx']:.1f}",I["adx"]>25 and I["dip"]>I["dim"],I["adx"]>25 and I["dim"]>I["dip"]),
            ib("OBV","Up" if I["obv_trend"]=="up" else "Down",I["obv_trend"]=="up",I["obv_trend"]=="down"),
            ib("VWAP",f"{cur}{I['vwap']:,.2f}",pr>I["vwap"],pr<I["vwap"]),
            ib("Ichimoku","Bullish" if ichi_b else "Bearish" if ichi_s else "In Cloud",ichi_b,ichi_s),
            ib("Vol Ratio",f"{I['vol_r']:.2f}x",I["vol_r"]>1.5,I["vol_r"]<0.5),
            ib("ATR",f"{cur}{I['atr']:.2f}",False,False),
        ]
        grid_html = '<div class="ind-grid">'+"".join(rows_html)+'</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

        # Pivot Points
        st.markdown('<div class="section-title">📐 Pivot Points</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="pivot-row">
          <div class="pvt-box"><div class="pvt-label">R2</div><div class="pvt-val" style="color:#ff7675;">{cur}{I['r2']:,.2f}</div></div>
          <div class="pvt-box"><div class="pvt-label">R1</div><div class="pvt-val" style="color:#fab1a0;">{cur}{I['r1']:,.2f}</div></div>
          <div class="pvt-box"><div class="pvt-label">PIVOT</div><div class="pvt-val" style="color:#74b9ff;">{cur}{I['pivot']:,.2f}</div></div>
          <div class="pvt-box"><div class="pvt-label">S1</div><div class="pvt-val" style="color:#55efc4;">{cur}{I['s1']:,.2f}</div></div>
          <div class="pvt-box"><div class="pvt-label">S2</div><div class="pvt-val" style="color:#00cec9;">{cur}{I['s2']:,.2f}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Ichimoku
        st.markdown('<div class="section-title">☁️ Ichimoku</div>', unsafe_allow_html=True)
        ichi_color = "#00b894" if ichi_b else "#d63031" if ichi_s else "#fdcb6e"
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:12px;">
          <div class="tgt"><div class="tgt-label">Tenkan (9)</div><div class="tgt-val" style="color:#74b9ff;">{cur}{I['ichi_conv']:,.2f}</div></div>
          <div class="tgt"><div class="tgt-label">Kijun (26)</div><div class="tgt-val" style="color:#fab1a0;">{cur}{I['ichi_base']:,.2f}</div></div>
          <div class="tgt"><div class="tgt-label">Span A</div><div class="tgt-val" style="color:#00b894;">{cur}{I['ichi_sa']:,.2f}</div></div>
          <div class="tgt"><div class="tgt-label">Span B</div><div class="tgt-val" style="color:#d63031;">{cur}{I['ichi_sb']:,.2f}</div></div>
        </div>
        <div style="background:{ichi_color}18;border:1px solid {ichi_color}50;border-radius:10px;padding:10px;text-align:center;font-size:.82rem;color:{ichi_color};font-weight:700;">
          {'☁️ ราคาอยู่เหนือ Cloud → Bullish' if ichi_b else '☁️ ราคาอยู่ใต้ Cloud → Bearish' if ichi_s else '☁️ ราคาอยู่ใน Cloud → Neutral'}
        </div>
        """, unsafe_allow_html=True)

        # 52W Range bar
        pct_52 = min(100, max(0, (pr-I["52wl"])/(I["52wh"]-I["52wl"]+1e-9)*100))
        st.markdown('<div class="section-title">📅 52-Week Range</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#1a1a2e;border-radius:10px;padding:12px;">
          <div style="display:flex;justify-content:space-between;font-size:.7rem;color:#8892b0;margin-bottom:6px;">
            <span>Low: {cur}{I['52wl']:,.2f}</span>
            <span style="color:#e2e8f0;font-weight:600;">{pct_52:.0f}% จากต่ำสุด</span>
            <span>High: {cur}{I['52wh']:,.2f}</span>
          </div>
          <div style="background:#2a2a4a;border-radius:4px;height:8px;position:relative;">
            <div style="position:absolute;left:0;top:0;height:8px;width:{pct_52}%;background:linear-gradient(90deg,#6c63ff,#00b894);border-radius:4px;"></div>
            <div style="position:absolute;top:-3px;left:{pct_52}%;transform:translateX(-50%);width:14px;height:14px;background:#fff;border-radius:50%;border:2px solid #6c63ff;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB: เป้าหมาย ───────────────────────────────────────
    with tab_target:
        st.markdown(f"""
        <div style="background:rgba(108,99,255,.08);border:1px solid rgba(108,99,255,.25);border-radius:14px;padding:16px;margin-bottom:14px;text-align:center;">
          <div style="font-size:.72rem;color:#8892b0;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">คะแนนรวม</div>
          <div style="font-size:2.5rem;font-weight:700;color:{'#00b894' if sc>=65 else '#fdcb6e' if sc>=45 else '#d63031'};font-family:'IBM Plex Mono',monospace;">{sc}<span style="font-size:1rem;color:#636e72;">/100</span></div>
          <div style="margin-top:8px;"><span class="signal-chip {chip_cls}" style="font-size:.85rem;padding:6px 16px;">{S['rec']}</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">🎯 ราคาเป้าหมาย</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="target-row" style="grid-template-columns:1fr 1fr;gap:10px;">
          <div class="tgt" style="padding:14px;">
            <div class="tgt-label">📍 จุดซื้อที่ดี</div>
            <div class="tgt-val tgt-entry" style="font-size:1.1rem;margin-top:6px;">{cur}{S['entry']:,.2f}</div>
            <div style="font-size:.65rem;color:#8892b0;margin-top:4px;">-1.5% จากราคาปัจจุบัน</div>
          </div>
          <div class="tgt" style="padding:14px;">
            <div class="tgt-label">🛑 Stop Loss</div>
            <div class="tgt-val tgt-sl" style="font-size:1.1rem;margin-top:6px;">{cur}{S['sl']:,.2f}</div>
            <div style="font-size:.65rem;color:#8892b0;margin-top:4px;">-{S['dn']:.1f}% / ATR×1.5</div>
          </div>
          <div class="tgt" style="padding:14px;">
            <div class="tgt-label">🎯 เป้าหมาย 1</div>
            <div class="tgt-val tgt-t1" style="font-size:1.1rem;margin-top:6px;">{cur}{S['t1']:,.2f}</div>
            <div style="font-size:.65rem;color:#8892b0;margin-top:4px;">+{S['up']:.1f}% / ATR×2.0</div>
          </div>
          <div class="tgt" style="padding:14px;">
            <div class="tgt-label">🚀 เป้าหมาย 2</div>
            <div class="tgt-val tgt-t2" style="font-size:1.1rem;margin-top:6px;">{cur}{S['t2']:,.2f}</div>
            <div style="font-size:.65rem;color:#8892b0;margin-top:4px;">+{round((S['t2']/pr-1)*100,1):.1f}% / ATR×3.5</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        rr_color="#00b894" if S["rr"]>=2 else "#fdcb6e" if S["rr"]>=1.5 else "#d63031"
        st.markdown(f"""
        <div style="background:{rr_color}12;border:1px solid {rr_color}40;border-radius:12px;padding:14px;margin-top:12px;text-align:center;">
          <div style="font-size:.72rem;color:#8892b0;text-transform:uppercase;letter-spacing:1px;">Risk / Reward Ratio</div>
          <div style="font-size:2rem;font-weight:700;color:{rr_color};font-family:'IBM Plex Mono',monospace;margin:6px 0;">1 : {S['rr']:.2f}</div>
          <div style="font-size:.78rem;color:#8892b0;">
            Upside <span style="color:#00b894;font-weight:700;">+{S['up']:.1f}%</span> &nbsp;vs&nbsp;
            Downside <span style="color:#d63031;font-weight:700;">-{S['dn']:.1f}%</span>
          </div>
          <div style="font-size:.7rem;color:{rr_color};margin-top:6px;">
            {'✅ R/R ดีมาก เหมาะสมในการเข้าซื้อ' if S['rr']>=2 else '⚠️ R/R พอได้ ควรรอจุดที่ดีกว่า' if S['rr']>=1.5 else '❌ R/R ต่ำ ความเสี่ยงสูงกว่าผลตอบแทน'}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Price distances
        st.markdown('<div class="section-title">📏 ระยะห่างจากค่าเฉลี่ย</div>', unsafe_allow_html=True)
        for sma_key, label in [(p['sma_s'],f"SMA{p['sma_s']}"),(p['sma_m'],f"SMA{p['sma_m']}"),(p['sma_l'],f"SMA{p['sma_l']}")]:
            sma_v = I.get(f"sma{sma_key}", pr)
            dist  = (pr/sma_v-1)*100
            bar_w = min(abs(dist)*3, 100)
            bar_c = "#00b894" if dist>0 else "#d63031"
            st.markdown(f"""
            <div style="background:#1a1a2e;border-radius:10px;padding:10px 12px;margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;font-size:.78rem;margin-bottom:5px;">
                <span style="color:#8892b0;">{label}</span>
                <span style="color:{bar_c};font-weight:700;font-family:'IBM Plex Mono',monospace;">{'+' if dist>=0 else ''}{dist:.1f}%</span>
              </div>
              <div style="background:#2a2a4a;border-radius:4px;height:4px;">
                <div style="height:4px;width:{bar_w}%;background:{bar_c};border-radius:4px;{'margin-left:auto;' if dist<0 else ''}"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB: สัญญาณ ─────────────────────────────────────────
    with tab_sig:
        buy_n  = len(S["bs"]); sell_n = len(S["ss"]); neut_n = len(S["ns"])
        total_n = buy_n+sell_n+neut_n if buy_n+sell_n+neut_n>0 else 1
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px;">
          <div style="background:rgba(0,184,148,.1);border:1px solid #00b89440;border-radius:10px;padding:10px;text-align:center;">
            <div style="font-size:1.4rem;font-weight:700;color:#00b894;">{buy_n}</div>
            <div style="font-size:.68rem;color:#8892b0;">ซื้อ</div>
          </div>
          <div style="background:rgba(99,110,114,.1);border:1px solid #63637240;border-radius:10px;padding:10px;text-align:center;">
            <div style="font-size:1.4rem;font-weight:700;color:#636e72;">{neut_n}</div>
            <div style="font-size:.68rem;color:#8892b0;">กลาง</div>
          </div>
          <div style="background:rgba(214,48,49,.1);border:1px solid #d6303140;border-radius:10px;padding:10px;text-align:center;">
            <div style="font-size:1.4rem;font-weight:700;color:#d63031;">{sell_n}</div>
            <div style="font-size:.68rem;color:#8892b0;">ขาย</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

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

    # ── TAB: พื้นฐาน (Fundamental) ─────────────────────────
    with tab_fund:
        if yf_info and isinstance(yf_info, dict) and yf_info.get("regularMarketPrice"):
            yi = yf_info
            def fv(key, fmt="{}", fallback="N/A"):
                v=yi.get(key); return fmt.format(v) if v is not None else fallback
            st.markdown(f"""
            <div class="fundamental-grid">
              <div class="fund-box"><div class="fund-label">P/E Ratio (TTM)</div><div class="fund-val">{fv('trailingPE','{:.2f}')}</div><div class="fund-desc">ราคาต่อกำไร</div></div>
              <div class="fund-box"><div class="fund-label">Forward P/E</div><div class="fund-val">{fv('forwardPE','{:.2f}')}</div><div class="fund-desc">P/E คาดการณ์</div></div>
              <div class="fund-box"><div class="fund-label">P/B Ratio</div><div class="fund-val">{fv('priceToBook','{:.2f}')}</div><div class="fund-desc">ราคาต่อมูลค่าบัญชี</div></div>
              <div class="fund-box"><div class="fund-label">ROE</div><div class="fund-val">{fv('returnOnEquity','{:.1%}')}</div><div class="fund-desc">ผลตอบแทนผู้ถือหุ้น</div></div>
              <div class="fund-box"><div class="fund-label">EPS (TTM)</div><div class="fund-val">{fv('trailingEps','{:.2f}')}</div><div class="fund-desc">กำไรต่อหุ้น</div></div>
              <div class="fund-box"><div class="fund-label">Dividend Yield</div><div class="fund-val">{fv('dividendYield','{:.2%}')}</div><div class="fund-desc">อัตราปันผล</div></div>
              <div class="fund-box"><div class="fund-label">Market Cap</div><div class="fund-val" style="font-size:.82rem;">{fv('marketCap','{:,.0f}')}</div><div class="fund-desc">มูลค่าตลาด</div></div>
              <div class="fund-box"><div class="fund-label">Beta</div><div class="fund-val">{fv('beta','{:.2f}')}</div><div class="fund-desc">ความผันผวนเทียบตลาด</div></div>
              <div class="fund-box"><div class="fund-label">Revenue Growth</div><div class="fund-val">{fv('revenueGrowth','{:.1%}')}</div><div class="fund-desc">การเติบโตรายได้</div></div>
              <div class="fund-box"><div class="fund-label">Profit Margin</div><div class="fund-val">{fv('profitMargins','{:.1%}')}</div><div class="fund-desc">อัตรากำไร</div></div>
              <div class="fund-box"><div class="fund-label">Debt/Equity</div><div class="fund-val">{fv('debtToEquity','{:.2f}')}</div><div class="fund-desc">หนี้สินต่อทุน</div></div>
              <div class="fund-box"><div class="fund-label">Current Ratio</div><div class="fund-val">{fv('currentRatio','{:.2f}')}</div><div class="fund-desc">สภาพคล่อง</div></div>
            </div>
            <div style="background:#1a1a2e;border-radius:10px;padding:12px;font-size:.78rem;color:#8892b0;line-height:1.7;">
              <span style="color:#e2e8f0;font-weight:600;">Business:</span> {yi.get('longBusinessSummary','N/A')[:300]}...
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warn-box">
              ⚠️ ข้อมูลพื้นฐานต้องการ <strong>yfinance</strong><br>
              ติดตั้งด้วย: <code>pip install yfinance</code><br>
              แล้ว restart โปรแกรม — ข้อมูลจะแสดงสำหรับหุ้น US/CN โดยอัตโนมัติ<br>
              สำหรับหุ้นไทย ข้อมูลพื้นฐานจาก SET.or.th ต้องใช้ Settrade API
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# VIEW: LOGIN
# ══════════════════════════════════════════════════════════════
def view_login():
    render_header()
    st.markdown("""
    <div class="login-card">
      <h2>🔐 เข้าสู่ระบบ Settrade API</h2>
      <div class="login-sub">
        กรอกข้อมูล credential จาก Settrade Developer Portal<br>
        เพื่อดึงข้อมูลหุ้นแบบ Real-time
      </div>
      <div class="info-box">
        📋 <strong>วิธีขอ API Key:</strong><br>
        1. ไปที่ <a href="https://developer.settrade.com" target="_blank">developer.settrade.com</a><br>
        2. Login ด้วยบัญชีนักลงทุน → สร้าง Application ใหม่<br>
        3. คัดลอก <strong>APP_ID</strong> และ <strong>APP_SECRET</strong> มาใส่ด้านล่าง<br>
        4. ใส่ <strong>APP_CODE</strong> (ชื่อ App ที่ตั้ง) และ <strong>BROKER_ID</strong> (รหัสโบรกเกอร์)
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        app_id     = st.text_input("APP_ID *",     placeholder="เช่น MPRZz1Hymo6nR50A",       type="default")
        app_secret = st.text_input("APP_SECRET *",  placeholder="เช่น Te/3LKXBb+IM20T/...",    type="password")
        app_code   = st.text_input("APP_CODE *",    placeholder="ชื่อ App ที่ตั้งใน Settrade",  value="SANDBOX")
        broker_id  = st.text_input("BROKER_ID *",   placeholder="รหัสโบรกเกอร์ เช่น SANDBOX",  value="SANDBOX")
        submitted  = st.form_submit_button("🔐 เข้าสู่ระบบ Settrade", use_container_width=True)

    if submitted:
        if not app_id or not app_secret or not app_code or not broker_id:
            st.markdown('<div class="error-box">❌ กรุณากรอกข้อมูลให้ครบทุกช่อง</div>', unsafe_allow_html=True)
        elif not SETTRADE_AVAILABLE:
            st.markdown('<div class="error-box">❌ ไม่พบ library settrade_v2<br>รัน: <code>pip install settrade-v2</code> แล้ว restart</div>', unsafe_allow_html=True)
        else:
            with st.spinner("กำลังเชื่อมต่อ Settrade..."):
                try:
                    investor = Investor(app_id=app_id.strip(), app_secret=app_secret.strip(),
                                       app_code=app_code.strip(), broker_id=broker_id.strip())
                    mkt_api = investor.Market()
                    rt_api  = investor.Realtime()
                    # ทดสอบ connection
                    test = mkt_api.get_candlestick("PTT", interval="1d", limit=5)
                    if test:
                        st.session_state.update(dict(
                            logged_in=True, market_api=mkt_api, realtime_api=rt_api,
                            app_id=app_id, app_secret=app_secret,
                            app_code=app_code, broker_id=broker_id,
                            view="scan",
                        ))
                        st.success("✅ เชื่อมต่อ Settrade สำเร็จ!")
                        time.sleep(0.8)
                        st.rerun()
                    else:
                        raise ValueError("API ไม่ตอบสนอง")
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ เชื่อมต่อไม่สำเร็จ<br><small>{str(e)}</small></div>', unsafe_allow_html=True)

    st.markdown("---")
    col_skip, col_yf = st.columns(2)
    with col_skip:
        if st.button("🔶 ใช้ Mock Data (ทดสอบ)", use_container_width=True):
            st.session_state.update(dict(logged_in=False, view="scan"))
            st.rerun()
    with col_yf:
        yf_status = "✅ ติดตั้งแล้ว" if YFINANCE_AVAILABLE else "❌ ยังไม่ติดตั้ง"
        st.markdown(f'<div style="text-align:center;font-size:.72rem;color:#8892b0;padding:8px;">Yahoo Finance: {yf_status}</div>', unsafe_allow_html=True)

    st.markdown('<div class="warn-box">⚠️ APP_SECRET เป็นข้อมูลลับ — อย่าแชร์หรือบันทึกในที่สาธารณะ</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# VIEW: SCAN
# ══════════════════════════════════════════════════════════════
def view_scan():
    render_header()
    render_param_expander()
    p = get_params()

    # Nav bar
    col_n1, col_n2 = st.columns([3,1])
    with col_n2:
        if st.button("🔍 วิเคราะห์หุ้น", use_container_width=True):
            st.session_state.view = "manual"
            st.rerun()

    # Market selector
    st.markdown('<div class="section-title">1️⃣ เลือกตลาดหุ้น</div>', unsafe_allow_html=True)
    mkt_cols = st.columns(3)
    for i, (mkt_key, mkt_data) in enumerate(MARKETS.items()):
        with mkt_cols[i]:
            is_sel = st.session_state.market == mkt_key
            if st.button(
                f"{mkt_data['flag']} **{mkt_key}**\n{mkt_data['desc']}",
                key=f"mkt_{mkt_key}",
                use_container_width=True,
                type="primary" if is_sel else "secondary",
            ):
                st.session_state.market = mkt_key
                st.rerun()

    mkt_key = st.session_state.market
    if not mkt_key:
        st.markdown('<div style="text-align:center;padding:32px;color:#636e72;font-size:.88rem;">👆 เลือกตลาดก่อน แล้วกดสแกน</div>', unsafe_allow_html=True)
        return

    mkt  = MARKETS[mkt_key]
    cur  = mkt["currency"]
    n    = len(mkt["stocks"])
    use_live = st.session_state.logged_in and mkt_key == "SET"

    src_tag = "⚡ Settrade Real-time" if use_live else ("📡 Yahoo Finance" if YFINANCE_AVAILABLE else "🔶 Mock")
    st.markdown(f"""
    <div style="background:#12122a;border:1px solid rgba(108,99,255,.3);border-radius:10px;padding:10px 14px;margin:8px 0 14px;display:flex;justify-content:space-between;align-items:center;">
      <span style="color:#e2e8f0;font-size:.85rem;">{mkt['flag']} <strong>{mkt['name']}</strong> · {n} หุ้น · {cur}</span>
      <span style="font-size:.68rem;color:#8892b0;">{src_tag}</span>
    </div>
    """, unsafe_allow_html=True)

    # Filter row
    c1,c2 = st.columns(2)
    with c1:
        filt_sig = st.multiselect("สัญญาณ",["🟢 ซื้อ","🟡 เฝ้าระวัง","⚪ ถือ","🔴 ขาย"],
            default=["🟢 ซื้อ","🟡 เฝ้าระวัง"],key="filt_sig",label_visibility="collapsed",placeholder="เลือกสัญญาณ")
    with c2:
        sort_by = st.selectbox("เรียงตาม",["Score ↓","RSI ↑","Change% ↓","ADX ↓"],
            key="sort_by",label_visibility="collapsed")

    st.markdown('<div class="section-title">2️⃣ สแกน</div>', unsafe_allow_html=True)
    if st.button(f"🔍 สแกน {mkt['flag']} {mkt_key} ({n} หุ้น)", use_container_width=True):
        results = []
        prog = st.progress(0)
        status_txt = st.empty()
        for i,(sym,name) in enumerate(mkt["stocks"]):
            status_txt.markdown(f'<div style="text-align:center;font-size:.75rem;color:#8892b0;">สแกน {sym} ... ({i+1}/{n})</div>', unsafe_allow_html=True)
            try:
                df, info = get_data(sym, mkt_key, use_settrade=use_live, p=p)
                I = compute_all(df, p)
                S = score_and_signal(I, p)
                results.append(dict(Symbol=sym,Name=name,Market=mkt_key,
                    Price=round(I["price"],2),Change=round(I["chg"],2),
                    RSI=round(I["rsi"],1),ADX=round(I["adx"],1),
                    BB=round(I["bbp"],2),VR=round(I["vol_r"],2),
                    Score=S["sc"],Signal=S["rec"],SigCls=S["cls"],
                    Entry=S["entry"],T1=S["t1"],T2=S["t2"],SL=S["sl"],RR=S["rr"],
                    _I=I,_S=S,_info=info,
                ))
            except Exception: pass
            prog.progress((i+1)/n)
        prog.empty(); status_txt.empty()
        st.session_state.scan_results[mkt_key] = pd.DataFrame(results)

    # Results
    df_res = st.session_state.scan_results.get(mkt_key)
    if df_res is None or len(df_res)==0:
        return

    sigs = filt_sig or ["🟢 ซื้อ","🟡 เฝ้าระวัง","⚪ ถือ","🔴 ขาย"]
    df_f = df_res[
        (df_res["Score"] >= p["min_score"]) &
        (df_res["RR"]    >= p["min_rr"]) &
        (df_res["ADX"]   >= p["min_adx"]) &
        (df_res["Signal"].isin(sigs))
    ].copy()

    sm={"Score ↓":"Score","RSI ↑":"RSI","Change% ↓":"Change","ADX ↓":"ADX"}
    sa={"Score ↓":False,"RSI ↑":True,"Change% ↓":False,"ADX ↓":False}
    df_f=df_f.sort_values(sm.get(sort_by,"Score"),ascending=sa.get(sort_by,False))

    buy_n=len(df_res[df_res["SigCls"]=="buy"]); sell_n=len(df_res[df_res["SigCls"]=="sell"])
    watch_n=len(df_res[df_res["SigCls"]=="watch"]); avg_sc=df_res["Score"].mean()
    st.markdown(f"""
    <div class="update-bar">
      <span>พบ <strong style="color:#e2e8f0;">{len(df_f)}</strong> / {len(df_res)} หุ้น</span>
      <span>🟢{buy_n} 🟡{watch_n} 🔴{sell_n} · avg {avg_sc:.0f}pt</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">3️⃣ ผลการสแกน — แตะ "วิเคราะห์เจาะลึก" ใต้แต่ละหุ้น</div>', unsafe_allow_html=True)

    if len(df_f)==0:
        st.markdown('<div style="text-align:center;padding:32px;color:#636e72;">ไม่มีหุ้นผ่านเงื่อนไข ลองปรับ Parameters</div>', unsafe_allow_html=True)
        return

    for _,row in df_f.iterrows():
        chg_cls="change-up" if row["Change"]>=0 else "change-dn"
        chip_cls=f"chip-{row['SigCls']}"; score_cls="score-h" if row["Score"]>=65 else "score-m" if row["Score"]>=45 else "score-l"
        chg_sym="+" if row["Change"]>=0 else ""
        rsi_c="bull" if row["RSI"]<p["rsi_os"] else "bear" if row["RSI"]>p["rsi_ob"] else ""
        bb_c="bull" if row["BB"]<0.2 else "bear" if row["BB"]>0.8 else ""
        vr_c="bull" if row["VR"]>1.5 else ""
        st.markdown(f"""
        <div class="stock-card {row['SigCls']}">
          <div class="sc-top">
            <div><div class="sc-symbol">{row['Symbol']}</div><div class="sc-name">{row['Name']}</div></div>
            <div><div class="sc-price">{cur}{row['Price']:,.2f}</div><div class="sc-change {chg_cls}">{chg_sym}{row['Change']:.2f}%</div></div>
          </div>
          <div class="sc-bars">
            <div class="sc-bar-item"><div class="sc-bar-label">RSI</div><div class="sc-bar-val {rsi_c}">{row['RSI']:.0f}</div></div>
            <div class="sc-bar-item"><div class="sc-bar-label">ADX</div><div class="sc-bar-val">{row['ADX']:.0f}</div></div>
            <div class="sc-bar-item"><div class="sc-bar-label">BB%</div><div class="sc-bar-val {bb_c}">{row['BB']:.2f}</div></div>
            <div class="sc-bar-item"><div class="sc-bar-label">Vol</div><div class="sc-bar-val {vr_c}">{row['VR']:.1f}x</div></div>
          </div>
          <div class="target-row">
            <div class="tgt"><div class="tgt-label">ซื้อ</div><div class="tgt-val tgt-entry">{cur}{row['Entry']:,.2f}</div></div>
            <div class="tgt"><div class="tgt-label">เป้า 1</div><div class="tgt-val tgt-t1">{cur}{row['T1']:,.2f}</div></div>
            <div class="tgt"><div class="tgt-label">เป้า 2</div><div class="tgt-val tgt-t2">{cur}{row['T2']:,.2f}</div></div>
            <div class="tgt"><div class="tgt-label">SL</div><div class="tgt-val tgt-sl">{cur}{row['SL']:,.2f}</div></div>
          </div>
          <div class="sc-bottom">
            <div><span class="signal-chip {chip_cls}">{row['Signal']}</span>
              <span style="font-size:.7rem;color:#8892b0;margin-left:8px;">R/R <span style="color:#6c63ff;font-weight:700;">1:{row['RR']:.2f}</span></span>
            </div>
            <div class="score-ring {score_cls}">{row['Score']:.0f}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🔍 วิเคราะห์ {row['Symbol']} เจาะลึก", key=f"da_{row['Symbol']}_{mkt_key}", use_container_width=True):
            st.session_state.update(dict(detail_sym=row["Symbol"],detail_mkt=mkt_key,view="detail"))
            st.rerun()

# ══════════════════════════════════════════════════════════════
# VIEW: MANUAL — วิเคราะห์หุ้นรายตัว (พิมพ์ชื่อ)
# ══════════════════════════════════════════════════════════════
def view_manual():
    render_header()
    if st.button("← กลับหน้าสแกน"):
        st.session_state.view = "scan"; st.rerun()

    st.markdown('<div class="section-title">🔍 วิเคราะห์หุ้นรายตัว</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
      พิมพ์ชื่อย่อหุ้น (Ticker) แล้วเลือกตลาด<br>
      🇹🇭 หุ้นไทย: <strong>ADVANC, KBANK, PTT</strong><br>
      🇺🇸 US: <strong>AAPL, NVDA, TSLA</strong><br>
      🇨🇳 CN: <strong>BABA, NIO, BIDU</strong>
    </div>
    """, unsafe_allow_html=True)

    with st.form("manual_form"):
        sym_input = st.text_input("ชื่อหุ้น (Ticker) *", placeholder="เช่น ADVANC, KBANK, AAPL, BABA",
                                   max_chars=10)
        mkt_sel   = st.selectbox("ตลาด *", ["SET 🇹🇭","US 🇺🇸","CN 🇨🇳"],
                                  help="เลือกให้ตรงเพื่อกำหนดสกุลเงินและวิธีดึงข้อมูล")
        submitted = st.form_submit_button("🔍 วิเคราะห์เจาะลึก", use_container_width=True)

    if submitted and sym_input.strip():
        sym = sym_input.strip().upper()
        mkt_map = {"SET 🇹🇭":"SET","US 🇺🇸":"US","CN 🇨🇳":"CN"}
        mkt_key = mkt_map[mkt_sel]
        p = get_params()
        use_live = st.session_state.logged_in and mkt_key=="SET"

        with st.spinner(f"กำลังดึงข้อมูล {sym}..."):
            try:
                df, info = get_data(sym, mkt_key, use_settrade=use_live, p=p)
                I = compute_all(df, p)
                S = score_and_signal(I, p)
                yf_inf = info.get("yf") if info.get("source")=="yfinance" else None

                # แสดงผล
                render_param_expander()
                render_deep_analysis(sym, mkt_key, I, S, info, yf_info=yf_inf)

                src_msg = {"settrade_live":"⚡ Settrade Real-time","yfinance":"📡 Yahoo Finance","mock":"🔶 Mock Data"}.get(info.get("source","mock"),"")
                st.markdown(f'<div class="update-bar"><span>แหล่งข้อมูล: {src_msg}</span><span>{datetime.now().strftime("%H:%M:%S")}</span></div>', unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f'<div class="error-box">❌ ดึงข้อมูลไม่ได้<br><small>{sym} — {str(e)}</small></div>', unsafe_allow_html=True)
                st.markdown('<div class="warn-box">💡 ลองตรวจสอบ Ticker ให้ถูกต้อง หรือเปลี่ยนตลาดที่เลือก</div>', unsafe_allow_html=True)

    render_param_expander()

# ══════════════════════════════════════════════════════════════
# VIEW: DETAIL — วิเคราะห์เจาะลึกจากผลสแกน
# ══════════════════════════════════════════════════════════════
def view_detail():
    render_header()
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("← กลับรายการหุ้น", use_container_width=True):
            st.session_state.view = "scan"; st.rerun()
    with col_b2:
        if st.button("🔍 วิเคราะห์หุ้นอื่น", use_container_width=True):
            st.session_state.view = "manual"; st.rerun()

    sym     = st.session_state.detail_sym
    mkt_key = st.session_state.detail_mkt
    p = get_params()
    use_live = st.session_state.logged_in and mkt_key=="SET"

    cached = st.session_state.scan_results.get(mkt_key)
    if cached is not None and sym in cached["Symbol"].values:
        row  = cached[cached["Symbol"]==sym].iloc[0]
        I,S  = row["_I"],row["_S"]
        info = row.get("_info",{"source":"mock"})
        yf_inf = None
        # ลอง fetch yfinance เพิ่มเพื่อข้อมูลพื้นฐาน
        if YFINANCE_AVAILABLE and mkt_key!="SET":
            try:
                _,yf_inf_dict = fetch_candles_yfinance(sym)
                yf_inf = yf_inf_dict
            except: pass
    else:
        with st.spinner(f"กำลังดึงข้อมูล {sym}..."):
            df, info = get_data(sym, mkt_key, use_settrade=use_live, p=p)
            I = compute_all(df, p)
            S = score_and_signal(I, p)
            yf_inf = info.get("yf")

    render_param_expander()
    render_deep_analysis(sym, mkt_key, I, S, info, yf_info=yf_inf)

# ══════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════
view = st.session_state.view

if view == "login":
    view_login()
elif view == "scan":
    view_scan()
elif view == "manual":
    view_manual()
elif view == "detail":
    view_detail()

# Footer
st.markdown("""
<div style="text-align:center;padding:20px 0 10px;color:#2a2a4a;font-size:.68rem;line-height:1.8;">
  ⚠️ ใช้เพื่อการศึกษาเท่านั้น · ไม่ใช่คำแนะนำการลงทุน<br>
  การลงทุนมีความเสี่ยง ผู้ลงทุนควรศึกษาข้อมูลก่อนตัดสินใจ
</div>
""", unsafe_allow_html=True)
