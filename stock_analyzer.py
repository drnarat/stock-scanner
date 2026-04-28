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
    import urllib.request, urllib.parse, json as _json
    WEB_OK = True
except ImportError:
    WEB_OK = False

try:
    import urllib.request as _urllib_req
    HTTP_OK = True
except ImportError:
    HTTP_OK = False

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
# CSS — Warm Dark Theme (สบายตา ไม่จ้าเกิน contrast พอดี)
# ---------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

/* ── รากฐาน: พื้นหลัง warm-dark ไม่ใช่ cold-purple ── */
:root{
  --bg0:#18181c;       /* พื้นหลังหลัก */
  --bg1:#222228;       /* card พื้น */
  --bg2:#2a2a32;       /* card เข้มขึ้น */
  --bg3:#32323c;       /* hover / ขอบ */
  --bdr:#3a3a46;       /* border ทั่วไป */
  --txt:#dde1e7;       /* ข้อความหลัก — อ่านง่ายบน dark */
  --txt2:#9ca3af;      /* ข้อความรอง */
  --txt3:#6b7280;      /* placeholder / muted */
  --acc:#7c6af0;       /* accent purple อ่อนลง */
  --grn:#34d399;       /* ซื้อ/บวก — emerald สดแต่ไม่แสบตา */
  --red:#f87171;       /* ขาย/ลบ — rose อ่อน */
  --yel:#fbbf24;       /* watch — amber */
  --cyn:#22d3ee;       /* เป้า 2 — cyan */
}

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Sarabun',sans-serif;background:var(--bg0);color:var(--txt);font-size:15px;line-height:1.6}
footer{visibility:hidden}#MainMenu{visibility:hidden}
header[data-testid="stHeader"]{background:var(--bg0)!important}

/* ── Header ── */
.app-hdr{
  background:linear-gradient(135deg,#1e1e26,#23202e,#1a2030);
  border:1px solid rgba(124,106,240,.25);
  border-radius:16px;padding:20px 18px 16px;
  text-align:center;margin-bottom:18px;
}
.app-hdr h1{font-size:1.45rem;font-weight:700;color:#f0f0f5;letter-spacing:.3px}
.app-hdr .sub{font-size:.78rem;color:var(--txt2);margin-top:5px}
.ldot{display:inline-block;width:8px;height:8px;background:var(--grn);border-radius:50%;margin-right:5px;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(1.4)}}

/* ── Login card ── */
.login-card{
  background:linear-gradient(135deg,var(--bg1),var(--bg2));
  border:1px solid var(--bdr);border-radius:18px;
  padding:22px 20px;margin:8px 0 18px;
}
.login-card h2{font-size:1.1rem;font-weight:700;color:#f0f0f5;margin-bottom:4px}
.login-sub{font-size:.8rem;color:var(--txt2);margin-bottom:18px;line-height:1.7}

/* ── Info / Warn / Err boxes ── */
.info-box{
  background:rgba(124,106,240,.07);border:1px solid rgba(124,106,240,.2);
  border-radius:10px;padding:12px 14px;margin-bottom:14px;
  font-size:.8rem;color:#c4cde8;line-height:1.75;
}
.warn-box{
  background:rgba(251,191,36,.07);border:1px solid rgba(251,191,36,.25);
  border-radius:10px;padding:10px 14px;margin-bottom:12px;
  font-size:.78rem;color:var(--yel);line-height:1.65;
}
.err-box{
  background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.35);
  border-radius:10px;padding:12px 14px;
  font-size:.82rem;color:#fca5a5;line-height:1.65;
}

/* ── Section title ── */
.sec-title{
  font-size:.72rem;font-weight:700;color:var(--txt3);
  text-transform:uppercase;letter-spacing:1.2px;
  margin:18px 0 10px;display:flex;align-items:center;gap:8px;
}
.sec-title::after{content:'';flex:1;height:1px;background:var(--bdr)}

/* ── Stock cards ── */
.stock-card{
  background:var(--bg1);border:1px solid var(--bdr);
  border-radius:14px;padding:14px 16px;margin-bottom:10px;
  transition:border-color .15s;
}
.stock-card:hover{border-color:var(--acc)}
.stock-card.buy   {border-left:4px solid var(--grn)}
.stock-card.sell  {border-left:4px solid var(--red)}
.stock-card.watch {border-left:4px solid var(--yel)}
.stock-card.neutral{border-left:4px solid var(--txt3)}

.sc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}
.sc-sym{font-size:1.05rem;font-weight:700;color:#f0f0f5;font-family:'IBM Plex Mono',monospace}
.sc-name{font-size:.73rem;color:var(--txt2);margin-top:2px}
.sc-price{font-size:1.05rem;font-weight:700;color:#f0f0f5;text-align:right;font-family:'IBM Plex Mono',monospace}
.sc-chg{font-size:.73rem;text-align:right;margin-top:2px;font-weight:600}
.cup{color:var(--grn)}.cdn{color:var(--red)}

.sc-bars{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:10px}
.sbi{text-align:center;background:var(--bg2);border-radius:8px;padding:6px 4px}
.sbl{font-size:.62rem;color:var(--txt3);text-transform:uppercase;letter-spacing:.5px}
.sbv{font-size:.82rem;font-weight:600;color:var(--txt);font-family:'IBM Plex Mono',monospace;margin-top:2px}

.sc-bot{display:flex;justify-content:space-between;align-items:center;margin-top:12px}
.sring{
  width:44px;height:44px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:.88rem;font-weight:700;font-family:'IBM Plex Mono',monospace;flex-shrink:0;
}
.sh{background:rgba(52,211,153,.12);border:2px solid var(--grn);color:var(--grn)}
.sm{background:rgba(251,191,36,.12);border:2px solid var(--yel);color:var(--yel)}
.sl{background:rgba(248,113,113,.12);border:2px solid var(--red);color:var(--red)}

/* ── Signal chips ── */
.chip{font-size:.76rem;font-weight:700;padding:4px 11px;border-radius:12px;display:inline-block}
.chip-buy    {background:rgba(52,211,153,.12);color:var(--grn);border:1px solid rgba(52,211,153,.3)}
.chip-sell   {background:rgba(248,113,113,.12);color:var(--red);border:1px solid rgba(248,113,113,.3)}
.chip-watch  {background:rgba(251,191,36,.12);color:var(--yel);border:1px solid rgba(251,191,36,.3)}
.chip-neutral{background:rgba(107,114,128,.12);color:var(--txt3);border:1px solid rgba(107,114,128,.3)}

/* ── Target/SL row ── */
.trow{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;margin-top:10px}
.tgt{background:var(--bg2);border-radius:8px;padding:7px 4px;text-align:center}
.tl{font-size:.62rem;color:var(--txt3);text-transform:uppercase;letter-spacing:.5px}
.tv{font-size:.8rem;font-weight:700;font-family:'IBM Plex Mono',monospace;margin-top:2px;color:var(--txt)}
.te{color:var(--acc)}.t1{color:var(--grn)}.t2{color:var(--cyn)}.ts{color:var(--red)}

/* ── Deep analysis header ── */
.da-hdr{
  background:linear-gradient(135deg,var(--bg1),#1e2030);
  border:1px solid rgba(124,106,240,.3);border-radius:14px;
  padding:18px 16px;margin-bottom:14px;
}
.da-sym{font-size:1.5rem;font-weight:700;color:#f0f0f5;font-family:'IBM Plex Mono',monospace}
.da-price{font-size:1.8rem;font-weight:700;font-family:'IBM Plex Mono',monospace}
.da-tag{display:inline-block;font-size:.68rem;font-weight:700;padding:3px 9px;border-radius:8px;margin-left:8px;vertical-align:middle}
.tth{background:rgba(52,211,153,.1);color:var(--grn);border:1px solid rgba(52,211,153,.2)}
.tus{background:rgba(124,106,240,.1);color:var(--acc);border:1px solid rgba(124,106,240,.2)}
.tcn{background:rgba(248,113,113,.1);color:var(--red);border:1px solid rgba(248,113,113,.2)}

/* ── Indicator grid ── */
.ind-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.ibox{
  background:var(--bg2);border:1px solid var(--bdr);
  border-radius:10px;padding:10px 12px;display:flex;flex-direction:column;gap:3px;
}
.ilabel{font-size:.65rem;color:var(--txt3);text-transform:uppercase;letter-spacing:.5px}
.ival{font-size:.95rem;font-weight:700;font-family:'IBM Plex Mono',monospace}
.ist{font-size:.66rem;margin-top:1px}
.bull{color:var(--grn)}.bear{color:var(--red)}.neut{color:var(--yel)}

/* ── Signal items ── */
.sig-item{border-radius:10px;padding:9px 14px;margin-bottom:6px;font-size:.8rem;line-height:1.55;border-left:3px solid}
.sig-buy {background:rgba(52,211,153,.06);border-color:var(--grn);color:#a7f3d0}
.sig-sell{background:rgba(248,113,113,.06);border-color:var(--red);color:#fecaca}
.sig-neut{background:rgba(107,114,128,.06);border-color:var(--txt3);color:var(--txt2)}

/* ── Pivot row ── */
.pvt-row{display:flex;gap:6px;overflow-x:auto;padding-bottom:4px;margin-bottom:14px;-webkit-overflow-scrolling:touch}
.pvt{flex-shrink:0;background:var(--bg2);border-radius:10px;padding:8px 13px;text-align:center;min-width:72px;border:1px solid var(--bdr)}
.pvtl{font-size:.6rem;color:var(--txt3);text-transform:uppercase}
.pvtv{font-size:.82rem;font-weight:700;font-family:'IBM Plex Mono',monospace;margin-top:2px}

/* ── Fundamental grid ── */
.fund-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.fbox{background:var(--bg2);border:1px solid var(--bdr);border-radius:10px;padding:10px 12px}
.flabel{font-size:.65rem;color:var(--txt3);text-transform:uppercase;letter-spacing:.5px}
.fval{font-size:1rem;font-weight:700;font-family:'IBM Plex Mono',monospace;color:var(--txt);margin-top:2px}
.fdesc{font-size:.65rem;color:var(--txt2);margin-top:2px}

/* ── Update bar ── */
.upd-bar{
  display:flex;justify-content:space-between;align-items:center;
  padding:8px 14px;background:var(--bg2);border-radius:10px;
  font-size:.72rem;color:var(--txt3);margin-bottom:12px;
}

/* ── Buttons ── */
div.stButton>button{
  width:100%;
  background:linear-gradient(135deg,#6d60e0,#4e46c8);
  color:#f0f0f5;border:none;border-radius:12px;
  padding:13px;font-size:.95rem;font-weight:700;
  font-family:'Sarabun',sans-serif;
  box-shadow:0 3px 12px rgba(110,96,224,.3);
  transition:all .18s;
}
div.stButton>button:hover{opacity:.88;transform:translateY(-1px)}

/* ── Inputs ── */
div[data-testid="stTextInput"]>div>div>input{
  background:var(--bg2)!important;border:1px solid var(--bdr)!important;
  border-radius:10px!important;color:var(--txt)!important;
  font-size:.88rem!important;
}
div[data-testid="stTextInput"]>div>div>input::placeholder{color:var(--txt3)!important}
div[data-testid="stTextInput"]>div>div>input:focus{border-color:var(--acc)!important}

/* ── Expander ── */
div[data-testid="stExpander"]{
  background:var(--bg1);border:1px solid var(--bdr)!important;
  border-radius:12px!important;margin-bottom:8px;
}

/* ── Sidebar ── */
div[data-testid="stSidebar"]{background:var(--bg1)!important}

/* ── Tabs ── */
div[data-testid="stTabs"] button[role="tab"]{color:var(--txt2)!important;font-size:.85rem!important}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{color:var(--acc)!important;border-bottom-color:var(--acc)!important}

/* ── Slider ── */
div[data-testid="stSlider"] div[data-testid="stTickBarMin"],
div[data-testid="stSlider"] div[data-testid="stTickBarMax"]{color:var(--txt3)!important}

/* ── AI Analysis panel ── */
.ai-panel{
  background:linear-gradient(135deg,#1c1c24,#1e2030);
  border:1px solid rgba(124,106,240,.3);border-radius:16px;
  padding:18px 16px;margin-bottom:14px;
}
.ai-panel-hdr{
  display:flex;align-items:center;gap:10px;margin-bottom:12px;
}
.ai-badge{
  font-size:.68rem;font-weight:700;padding:3px 9px;border-radius:8px;
}
.ai-claude{background:rgba(207,134,104,.15);color:#d4896a;border:1px solid rgba(207,134,104,.3)}
.ai-gemini{background:rgba(66,133,244,.15);color:#6fa8f5;border:1px solid rgba(66,133,244,.3)}
.ai-result{
  font-size:.85rem;color:var(--txt);line-height:1.85;
  white-space:pre-wrap;word-break:break-word;
}
.ai-result h3{font-size:.9rem;font-weight:700;color:#f0f0f5;margin:12px 0 5px}
.ai-result strong{color:#f0f0f5}
.ai-result ul{padding-left:16px;margin:4px 0}
.ai-result li{margin-bottom:3px}
.news-item{
  background:var(--bg2);border:1px solid var(--bdr);border-radius:10px;
  padding:10px 14px;margin-bottom:7px;
}
.news-title{font-size:.82rem;color:var(--txt);font-weight:600;line-height:1.4}
.news-meta{font-size:.68rem;color:var(--txt3);margin-top:4px}
.news-src{color:var(--acc);font-weight:600}
.ai-provider-sel{
  display:flex;gap:8px;margin-bottom:14px;
}
.ai-prov-btn{
  flex:1;padding:10px 8px;border-radius:10px;border:1px solid var(--bdr);
  background:var(--bg2);color:var(--txt2);font-size:.8rem;font-weight:600;
  text-align:center;cursor:pointer;transition:all .15s;
}
.ai-prov-btn.active-claude{background:rgba(207,134,104,.1);border-color:rgba(207,134,104,.4);color:#d4896a}
.ai-prov-btn.active-gemini{background:rgba(66,133,244,.1);border-color:rgba(66,133,244,.4);color:#6fa8f5}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# STOCK UNIVERSE
# ---------------------------------------------------------------
MARKETS = {
    "SET": {
        "flag": "TH", "name": "ตลาดหุ้นไทย", "desc": "SET50/100/mai",
        "currency": "฿", "tag": "tth",
        "stocks": [
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
        "flag": "US", "name": "US Tech", "desc": "NASDAQ/NYSE",
        "currency": "$", "tag": "tus",
        "stocks": [
            ("AAPL","Apple"),("MSFT","Microsoft"),("NVDA","NVIDIA"),("GOOGL","Alphabet"),
            ("META","Meta"),("AMZN","Amazon"),("TSLA","Tesla"),("AMD","AMD"),
            ("INTC","Intel"),("AVGO","Broadcom"),("QCOM","Qualcomm"),("MU","Micron"),
            ("AMAT","Applied Materials"),("CRM","Salesforce"),("ADBE","Adobe"),
            ("NOW","ServiceNow"),("PLTR","Palantir"),("ORCL","Oracle"),
        ],
    },
    "CN": {
        "flag": "CN", "name": "CN Tech", "desc": "NYSE/NASDAQ ADR",
        "currency": "$", "tag": "tcn",
        "stocks": [
            ("BABA","Alibaba"),("JD","JD.com"),("BIDU","Baidu"),("NTES","NetEase"),
            ("PDD","Pinduoduo"),("TCOM","Trip.com"),("NIO","NIO"),("XPEV","XPeng"),
            ("LI","Li Auto"),("BILI","Bilibili"),("WB","Weibo"),("FUTU","Futu"),
        ],
    },
}

# ---------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------
for k, v in [
    ("logged_in", False), ("market_api", None), ("realtime_api", None),
    ("market", None), ("scan_results", {}), ("view", "login"),
    ("detail_sym", None), ("detail_mkt", None),
    ("prefill_id", ""), ("prefill_secret", ""),
    ("prefill_code", "SANDBOX"), ("prefill_broker", "SANDBOX"),
    ("ai_provider", "claude"),
    ("ai_analysis_cache", {}),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------
# INDICATORS
# ---------------------------------------------------------------
def _safe(s, fallback=0.0):
    try:
        v = s.iloc[-1] if hasattr(s, "iloc") else s
        return float(v) if pd.notna(v) else fallback
    except Exception:
        return fallback

def compute_indicators(df, p):
    c = df["close"].astype(float)
    h = df["high"].astype(float)
    l = df["low"].astype(float)
    v = df["volume"].astype(float)
    I = {}

    if TA_OK:
        I["sma_s"] = _safe(ta.sma(c, length=p["sma_s"]))
        I["sma_m"] = _safe(ta.sma(c, length=p["sma_m"]))
        I["sma_l"] = _safe(ta.sma(c, length=p["sma_l"]))
        I["rsi"]   = _safe(ta.rsi(c, length=p["rsi_p"]))
        macd_df = ta.macd(c, fast=p["macd_f"], slow=p["macd_s"], signal=p["macd_sg"])
        if macd_df is not None and not macd_df.empty:
            cols = macd_df.columns.tolist()
            I["macd"]  = _safe(macd_df[cols[0]])
            I["macd_h"] = _safe(macd_df[cols[1]])
            I["macd_sig"] = _safe(macd_df[cols[2]])
        else:
            I["macd"] = I["macd_h"] = I["macd_sig"] = 0.0
        bb = ta.bbands(c, length=p["bb_p"], std=p["bb_k"])
        if bb is not None and not bb.empty:
            bc = bb.columns.tolist()
            I["bbl"] = _safe(bb[bc[0]]); I["bbm"] = _safe(bb[bc[1]]); I["bbu"] = _safe(bb[bc[2]])
            I["bbp"] = _safe(bb[bc[4]])
            I["bb_width"] = ((I["bbu"] - I["bbl"]) / (I["bbm"] + 1e-9)) * 100
        else:
            I["bbl"] = I["bbm"] = I["bbu"] = c.iloc[-1]; I["bbp"] = 0.5; I["bb_width"] = 0.0
        stoch = ta.stoch(h, l, c, k=p["stoch_k"], d=p["stoch_d"])
        if stoch is not None and not stoch.empty:
            sc2 = stoch.columns.tolist()
            I["sk"] = _safe(stoch[sc2[0]]); I["sd"] = _safe(stoch[sc2[1]])
        else:
            I["sk"] = I["sd"] = 50.0
        I["atr"] = _safe(ta.atr(h, l, c, length=p["atr_p"]))
        I["cci"] = _safe(ta.cci(h, l, c, length=p["cci_p"]))
        I["wr"]  = _safe(ta.willr(h, l, c, length=p["wr_p"]))
        I["mfi"] = _safe(ta.mfi(h, l, c, v, length=p["mfi_p"]))
        adx_df = ta.adx(h, l, c, length=p["adx_p"])
        if adx_df is not None and not adx_df.empty:
            ac = adx_df.columns.tolist()
            I["adx"] = _safe(adx_df[ac[0]]); I["dip"] = _safe(adx_df[ac[1]]); I["dim"] = _safe(adx_df[ac[2]])
        else:
            I["adx"] = I["dip"] = I["dim"] = 20.0
        obv = ta.obv(c, v)
        I["obv_up"] = _safe(obv) > _safe(obv.shift(5))
        try:
            vwap_s = ta.vwap(h, l, c, v)
            I["vwap"] = _safe(vwap_s) if vwap_s is not None else float(c.iloc[-1])
        except Exception:
            I["vwap"] = float(c.iloc[-1])
        try:
            ichi = ta.ichimoku(h, l, c)
            if ichi and len(ichi) >= 2:
                idf = ichi[0]; ic = idf.columns.tolist()
                I["ichi_conv"] = _safe(idf[ic[0]]); I["ichi_base"] = _safe(idf[ic[1]])
                sdf = ichi[1]; sc3 = sdf.columns.tolist()
                I["ichi_sa"] = _safe(sdf[sc3[0]]) if sc3 else float(c.iloc[-1])
                I["ichi_sb"] = _safe(sdf[sc3[1]]) if len(sc3) > 1 else float(c.iloc[-1])
            else:
                raise ValueError("empty")
        except Exception:
            I["ichi_conv"] = I["ichi_base"] = I["ichi_sa"] = I["ichi_sb"] = float(c.iloc[-1])
    else:
        # numpy fallback
        def sma(s, n): return s.rolling(n).mean()
        def ema(s, n): return s.ewm(span=n, adjust=False).mean()
        I["sma_s"] = _safe(sma(c, p["sma_s"])); I["sma_m"] = _safe(sma(c, p["sma_m"])); I["sma_l"] = _safe(sma(c, p["sma_l"]))
        d = c.diff(); g = d.clip(lower=0).rolling(p["rsi_p"]).mean(); lo = (-d.clip(upper=0)).rolling(p["rsi_p"]).mean()
        I["rsi"] = _safe(100 - 100/(1 + g/(lo + 1e-9)))
        ml = ema(c, p["macd_f"]) - ema(c, p["macd_s"]); ms = ema(ml, p["macd_sg"])
        I["macd"] = _safe(ml); I["macd_sig"] = _safe(ms); I["macd_h"] = _safe(ml - ms)
        bm = sma(c, p["bb_p"]); bstd = c.rolling(p["bb_p"]).std()
        I["bbu"] = _safe(bm + p["bb_k"]*bstd); I["bbm"] = _safe(bm); I["bbl"] = _safe(bm - p["bb_k"]*bstd)
        I["bbp"] = _safe((c - (bm - p["bb_k"]*bstd)) / (2*p["bb_k"]*bstd + 1e-9))
        I["bb_width"] = (I["bbu"] - I["bbl"]) / (I["bbm"] + 1e-9) * 100
        ll = l.rolling(p["stoch_k"]).min(); hh = h.rolling(p["stoch_k"]).max()
        sk = 100*(c - ll)/(hh - ll + 1e-9)
        I["sk"] = _safe(sk); I["sd"] = _safe(sk.rolling(p["stoch_d"]).mean())
        tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
        I["atr"] = _safe(tr.rolling(p["atr_p"]).mean())
        tp = (h+l+c)/3; cm = tp.rolling(p["cci_p"]).mean()
        mad = tp.rolling(p["cci_p"]).apply(lambda x: np.abs(x - x.mean()).mean())
        I["cci"] = _safe((tp - cm)/(0.015*mad + 1e-9))
        I["wr"] = _safe(-100*(h.rolling(p["wr_p"]).max()-c)/(h.rolling(p["wr_p"]).max()-l.rolling(p["wr_p"]).min()+1e-9))
        mtp = (h+l+c)/3; mf = mtp*v
        pos = mf.where(mtp>mtp.shift(),0).rolling(p["mfi_p"]).sum()
        neg = mf.where(mtp<mtp.shift(),0).rolling(p["mfi_p"]).sum()
        I["mfi"] = _safe(100 - 100/(1 + pos/(neg+1e-9)))
        dmp = (h-h.shift()).clip(lower=0); dmm = (l.shift()-l).clip(lower=0)
        dmp2 = dmp.where(dmp>dmm,0); dmm2 = dmm.where(dmm>dmp,0)
        atr14 = tr.rolling(p["adx_p"]).mean()
        dip = 100*dmp2.rolling(p["adx_p"]).mean()/(atr14+1e-9)
        dim = 100*dmm2.rolling(p["adx_p"]).mean()/(atr14+1e-9)
        I["adx"] = _safe((100*(dip-dim).abs()/(dip+dim+1e-9)).rolling(p["adx_p"]).mean())
        I["dip"] = _safe(dip); I["dim"] = _safe(dim)
        obv = (v*np.sign(c.diff()).fillna(0)).cumsum()
        I["obv_up"] = float(obv.iloc[-1]) > float(obv.iloc[-5])
        I["vwap"] = _safe((tp*v).cumsum()/(v.cumsum()+1e-9))
        conv = (h.rolling(9).max()+l.rolling(9).min())/2
        base = (h.rolling(26).max()+l.rolling(26).min())/2
        I["ichi_conv"] = _safe(conv); I["ichi_base"] = _safe(base)
        I["ichi_sa"] = _safe(((conv+base)/2).shift(26))
        I["ichi_sb"] = _safe(((h.rolling(52).max()+l.rolling(52).min())/2).shift(26))

    I["vol_avg"] = float(v.rolling(20).mean().iloc[-1]) if len(v) >= 20 else float(v.mean())
    I["vol_r"] = float(v.iloc[-1]) / (I["vol_avg"] + 1)
    I["price"] = float(c.iloc[-1])
    I["open"]  = float(df["open"].iloc[-1]) if "open" in df.columns else I["price"]
    I["high_d"] = float(h.iloc[-1]); I["low_d"] = float(l.iloc[-1])
    I["chg"]   = (float(c.iloc[-1])/float(c.iloc[-2])-1)*100 if len(c)>=2 else 0.0
    I["chg_5d"] = (float(c.iloc[-1])/float(c.iloc[-5])-1)*100 if len(c)>=5 else 0.0
    I["chg_20d"] = (float(c.iloc[-1])/float(c.iloc[-20])-1)*100 if len(c)>=20 else 0.0
    I["52wh"] = float(h.rolling(min(252,len(h))).max().iloc[-1])
    I["52wl"] = float(l.rolling(min(252,len(l))).min().iloc[-1])
    pv = (I["high_d"]+I["low_d"]+I["price"])/3
    rng = I["high_d"] - I["low_d"]
    I["pivot"]=pv; I["r1"]=2*pv-I["low_d"]; I["r2"]=pv+rng
    I["s1"]=2*pv-I["high_d"]; I["s2"]=pv-rng
    for k2 in list(I.keys()):
        if isinstance(I[k2], float) and (np.isnan(I[k2]) or np.isinf(I[k2])):
            I[k2] = 0.0
    return I

def score_stock(I, p):
    ob = p["rsi_ob"]; os = p["rsi_os"]
    bs=[]; ss=[]; ns=[]; sc=50
    r = I["rsi"]
    if r < os:    sc+=8; bs.append("RSI " + str(round(r,1)) + " < " + str(os) + " Oversold")
    elif r > ob:  sc-=8; ss.append("RSI " + str(round(r,1)) + " > " + str(ob) + " Overbought")
    else:         ns.append("RSI " + str(round(r,1)) + " ปกติ")
    if I["macd"] > I["macd_sig"] and I["macd_h"] > 0:
        sc+=7; bs.append("MACD ตัดขึ้น Signal")
    elif I["macd"] < I["macd_sig"] and I["macd_h"] < 0:
        sc-=7; ss.append("MACD ตัดลง Signal")
    pr = I["price"]
    if pr > I["sma_s"] > I["sma_m"]: sc+=6; bs.append("ราคา > SMA" + str(p["sma_s"]) + " > SMA" + str(p["sma_m"]) + " uptrend")
    elif pr < I["sma_s"] < I["sma_m"]: sc-=6; ss.append("ราคา < SMA" + str(p["sma_s"]) + " < SMA" + str(p["sma_m"]) + " downtrend")
    if pr > I["sma_l"]: sc+=4; bs.append("ราคา > SMA" + str(p["sma_l"]) + " เหนือค่าเฉลี่ยระยะยาว")
    else: sc-=4; ss.append("ราคา < SMA" + str(p["sma_l"]) + " ต่ำกว่าค่าเฉลี่ยระยะยาว")
    if I["bbp"] < 0.15: sc+=6; bs.append("BB% " + str(round(I["bbp"],2)) + " ใกล้ Lower Band")
    elif I["bbp"] > 0.85: sc-=5; ss.append("BB% " + str(round(I["bbp"],2)) + " ใกล้ Upper Band")
    sk = I["sk"]; sd = I["sd"]
    if sk < 20 and sk > sd: sc+=5; bs.append("Stoch %K=" + str(round(sk,1)) + " ตัดขึ้นใน oversold")
    elif sk > 80 and sk < sd: sc-=5; ss.append("Stoch %K=" + str(round(sk,1)) + " ตัดลงใน overbought")
    if I["cci"] < -100: sc+=4; bs.append("CCI " + str(round(I["cci"],1)) + " < -100 oversold")
    elif I["cci"] > 100: sc-=4; ss.append("CCI " + str(round(I["cci"],1)) + " > 100 overbought")
    if I["wr"] < -80: sc+=4; bs.append("Williams %R " + str(round(I["wr"],1)) + " oversold")
    elif I["wr"] > -20: sc-=4; ss.append("Williams %R " + str(round(I["wr"],1)) + " overbought")
    if I["adx"] > 25:
        if I["dip"] > I["dim"]: sc+=5; bs.append("ADX " + str(round(I["adx"],1)) + " + DI+ > DI- uptrend")
        else: sc-=5; ss.append("ADX " + str(round(I["adx"],1)) + " + DI- > DI+ downtrend")
    else: ns.append("ADX " + str(round(I["adx"],1)) + " < 25 sideways")
    if I["mfi"] < 20: sc+=4; bs.append("MFI " + str(round(I["mfi"],1)) + " เงินไหลออกมาก")
    elif I["mfi"] > 80: sc-=4; ss.append("MFI " + str(round(I["mfi"],1)) + " เงินไหลเข้าเกิน")
    if I["obv_up"]: sc+=3; bs.append("OBV ขาขึ้น")
    else: sc-=2; ss.append("OBV ขาลง")
    if pr > I["vwap"]: sc+=3; bs.append("ราคา > VWAP")
    else: sc-=3; ss.append("ราคา < VWAP")
    if I["vol_r"] > 1.5: sc+=3; bs.append("Volume " + str(round(I["vol_r"],1)) + "x")
    elif I["vol_r"] < 0.5: ns.append("Volume ต่ำ " + str(round(I["vol_r"],1)) + "x")
    if pr > I["ichi_sa"] and pr > I["ichi_sb"]: sc+=4; bs.append("เหนือ Ichimoku Cloud")
    elif pr < I["ichi_sa"] and pr < I["ichi_sb"]: sc-=4; ss.append("ใต้ Ichimoku Cloud")
    sc = max(0, min(100, sc))
    if sc >= 65:   rec="🟢 ซื้อ"; cls="buy"
    elif sc <= 35: rec="🔴 ขาย"; cls="sell"
    elif sc >= 55: rec="🟡 เฝ้าระวัง"; cls="watch"
    else:          rec="⚪ ถือ"; cls="neutral"
    at = I["atr"]
    entry = round(pr*0.985, 2); t1 = round(pr+at*2, 2); t2 = round(pr+at*3.5, 2); sl = round(pr-at*1.5, 2)
    up = round((t1/pr-1)*100, 1) if pr > 0 else 0
    dn = round((pr/sl-1)*100, 1) if sl > 0 else 1
    rr = round(up/dn, 2) if dn > 0 else 0
    return dict(sc=sc, rec=rec, cls=cls, bs=bs, ss=ss, ns=ns,
                entry=entry, t1=t1, t2=t2, sl=sl, up=up, dn=dn, rr=rr)

# ---------------------------------------------------------------
# DATA FETCH
# ---------------------------------------------------------------
def fetch_settrade(symbol, limit=200):
    raw = st.session_state.market_api.get_candlestick(symbol, interval="1d", limit=limit)
    df = pd.DataFrame(raw)
    rename = {"last":"close","c":"close","o":"open","h":"high","l":"low","v":"volume","vol":"volume"}
    df.rename(columns={col: rename.get(col, col) for col in df.columns}, inplace=True)
    if "close" not in df.columns:
        for alt in ["Close","CLOSE","price","Price"]:
            if alt in df.columns:
                df["close"] = df[alt]; break
    for col, alt in [("open","close"),("high","close"),("low","close"),("volume",None)]:
        if col not in df.columns:
            df[col] = df[alt] if alt else 1000000
    df = df[["open","high","low","close","volume"]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(df) < 30:
        raise ValueError("ข้อมูลน้อยเกินไป")
    return df

def fetch_yfinance(symbol, period="1y"):
    if not YF_OK:
        raise RuntimeError("yfinance ไม่ได้ติดตั้ง")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)[["Open","High","Low","Close","Volume"]].copy()
    df.columns = ["open","high","low","close","volume"]
    return df.dropna(), ticker.info

def fetch_mock(symbol, n=200):
    np.random.seed(abs(hash(symbol)) % 99999)
    base = np.random.uniform(8, 600)
    c = [base]
    for _ in range(n-1):
        c.append(max(c[-1]*(1+np.random.normal(0,.014)), 0.5))
    c = np.array(c)
    h = c*np.random.uniform(1.001,1.025,n); lo = c*np.random.uniform(.975,.999,n)
    v = np.random.uniform(3e5,8e6,n).astype(int)
    return pd.DataFrame({"open":c,"high":h,"low":lo,"close":c,"volume":v})

def get_data(symbol, mkt_key):
    info = {}
    use_live = st.session_state.logged_in and mkt_key == "SET"
    if use_live:
        try:
            df = fetch_settrade(symbol)
            # get_quote_symbol อาจไม่มีใน v1.x หรือ realtime_api = market_api
            try:
                rt = st.session_state.realtime_api
                if rt is not None and hasattr(rt, "get_quote_symbol"):
                    q = rt.get_quote_symbol(symbol)
                    if q and "last" in q:
                        df.iloc[-1, df.columns.get_loc("close")] = float(q["last"])
            except Exception:
                pass  # ราคา realtime ไม่ได้ก็ใช้ candlestick ปกติ
            info["source"] = "settrade"
            return df, info
        except Exception as e:
            info["err"] = str(e)
    yf_sym = symbol + ".BK" if mkt_key == "SET" else symbol
    if YF_OK:
        try:
            df, yf_info = fetch_yfinance(yf_sym)
            info["source"] = "yfinance"; info["yf"] = yf_info
            return df, info
        except Exception:
            pass
    df = fetch_mock(symbol)
    info["source"] = "mock"
    return df, info

# ---------------------------------------------------------------
# DEFAULT PARAMS
# ---------------------------------------------------------------
DEF = dict(
    # ── Moving Averages ──────────────────────────────────────────
    # SET: ใช้ 10/25/75 เพราะหุ้นไทยมี noise สูงกว่า US
    # 10 วัน = momentum สั้น, 25 วัน = swing mid-term, 75 วัน = trend กลาง
    sma_s=10, sma_m=25, sma_l=75, ema_f=12, ema_s=26,

    # ── RSI ─────────────────────────────────────────────────────
    # Period 14 มาตรฐาน; Oversold ปรับเป็น 35 (ไทยไม่ค่อยลงถึง 30)
    # Overbought ปรับเป็น 68 (ไทยพีกก่อน 70 แล้วหมุน)
    rsi_p=14, rsi_ob=68, rsi_os=35,

    # ── MACD ────────────────────────────────────────────────────
    # มาตรฐาน 12/26/9 ดีอยู่แล้ว
    macd_f=12, macd_s=26, macd_sg=9,

    # ── Bollinger Bands ─────────────────────────────────────────
    # Period 20, Std 2.0 มาตรฐาน
    bb_p=20, bb_k=2,

    # ── Stochastic ──────────────────────────────────────────────
    # %K=14, %D=3 มาตรฐาน
    stoch_k=14, stoch_d=3,

    # ── อื่นๆ ───────────────────────────────────────────────────
    atr_p=14, cci_p=20, wr_p=14, mfi_p=14, adx_p=14,

    # ── Filter ──────────────────────────────────────────────────
    # ลด min_score จาก 60 → 55 เพื่อให้เห็นหุ้นมากขึ้น
    # ลด min_rr จาก 1.5 → 1.2 เพราะ SET Spread กว้างกว่า US
    # ลด min_adx จาก 18 → 15 เพื่อจับ early trend
    min_score=55, min_rr=1.2, min_adx=15,
)

def get_params():
    return {k: st.session_state.get("p_"+k, v) for k, v in DEF.items()}

# ---------------------------------------------------------------
# WEB SEARCH (DuckDuckGo Instant Answer API — ไม่ต้องการ key)
# ---------------------------------------------------------------
import urllib.request as _ureq
import urllib.parse as _uparse
import json as _json_mod
import ssl as _ssl

def _http_get(url, headers=None, timeout=12):
    """ดึง URL แล้ว return text — raise ถ้าล้มเหลว"""
    req = _ureq.Request(url, headers=headers or {
        "User-Agent": "Mozilla/5.0 StockScannerBot/1.0"
    })
    ctx = _ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = _ssl.CERT_NONE
    with _ureq.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

def search_stock_news(symbol, company_name="", market="SET"):
    """
    ดึงข่าวหุ้น 1 เดือน ผ่าน DuckDuckGo Instant + RSS feeds
    คืน list ของ dict {title, url, source, date}
    """
    results = []
    # ── คำค้นหา ──────────────────────────────────────────────
    if market == "SET":
        query = f"{symbol} {company_name} หุ้น ราคา ผลประกอบการ 2025"
        query_en = f"{symbol}.BK stock Thailand SET 2025"
    else:
        query = f"{symbol} {company_name} stock news earnings 2025"
        query_en = query

    # ── DuckDuckGo Instant Answer API ────────────────────────
    for q in [query, query_en]:
        try:
            url = "https://api.duckduckgo.com/?q=" + _uparse.quote(q) + "&format=json&no_redirect=1&no_html=1"
            raw = _http_get(url, timeout=8)
            data = _json_mod.loads(raw)
            # RelatedTopics
            for topic in data.get("RelatedTopics", [])[:5]:
                text = topic.get("Text","")
                href = topic.get("FirstURL","")
                if text and len(text) > 20:
                    results.append({
                        "title": text[:120],
                        "url": href,
                        "source": "DuckDuckGo",
                        "date": "",
                    })
            # Abstract
            if data.get("AbstractText"):
                results.append({
                    "title": data["AbstractText"][:200],
                    "url": data.get("AbstractURL",""),
                    "source": data.get("AbstractSource","Web"),
                    "date": "",
                })
        except Exception:
            pass

    # ── Google News RSS (ไม่ต้องการ key) ─────────────────────
    rss_queries = [query, query_en] if market != "SET" else [query]
    for q in rss_queries:
        try:
            rss_url = "https://news.google.com/rss/search?q=" + _uparse.quote(q) + "&hl=th&gl=TH&ceid=TH:th"
            raw = _http_get(rss_url, timeout=8)
            # parse RSS items ด้วย regex เล็กน้อย (ไม่ใช้ xml library)
            import re as _re
            items = _re.findall(r'<item>(.*?)</item>', raw, _re.DOTALL)
            for item in items[:8]:
                title_m = _re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                link_m  = _re.search(r'<link>(.*?)</link>', item)
                date_m  = _re.search(r'<pubDate>(.*?)</pubDate>', item)
                src_m   = _re.search(r'<source[^>]*>(.*?)</source>', item)
                if title_m:
                    results.append({
                        "title": title_m.group(1)[:150],
                        "url":   link_m.group(1) if link_m else "",
                        "source": src_m.group(1) if src_m else "Google News",
                        "date":  date_m.group(1)[:16] if date_m else "",
                    })
        except Exception:
            pass

    # ── SET market specific: Investory / Finnomena RSS ────────
    if market == "SET":
        for rss_url in [
            f"https://www.set.or.th/th/market/news-and-alert/newsdetails?symbol={symbol}",
        ]:
            pass  # SET ต้องการ browser — skip

    # deduplicate
    seen = set()
    uniq = []
    for r in results:
        key = r["title"][:60]
        if key not in seen:
            seen.add(key); uniq.append(r)
    return uniq[:12]


def fetch_stock_context_text(symbol, company_name, market, I, S, mkt_key):
    """
    สร้าง context string สำหรับส่งให้ AI
    รวม: indicator data + ข่าวจาก web
    """
    # ── ข้อมูล technical สรุป ──────────────────────────────
    score = S["sc"]; rec = S["rec"]
    tech_summary = f"""
=== ข้อมูล Technical Analysis: {symbol} ({company_name}) ===
ตลาด: {mkt_key} | คะแนน: {score}/100 | สัญญาณ: {rec}

ราคา: {I['price']:.2f} | เปลี่ยนแปลงวันนี้: {I['chg']:+.2f}%
เปลี่ยนแปลง 5 วัน: {I['chg_5d']:+.1f}% | 20 วัน: {I['chg_20d']:+.1f}%

RSI(14): {I['rsi']:.1f} | MACD Histogram: {I['macd_h']:.4f}
ADX: {I['adx']:.1f} | DI+: {I['dip']:.1f} | DI-: {I['dim']:.1f}
BB%B: {I['bbp']:.2f} | Stoch %K: {I['sk']:.1f}
Volume Ratio: {I['vol_r']:.1f}x | MFI: {I['mfi']:.1f}

SMA สั้น: {I['sma_s']:.2f} | SMA กลาง: {I['sma_m']:.2f} | SMA ยาว: {I['sma_l']:.2f}
ATR: {I['atr']:.2f} | VWAP: {I['vwap']:.2f}

เป้าซื้อ: {S['entry']:.2f} | เป้า 1: {S['t1']:.2f} | เป้า 2: {S['t2']:.2f} | Stop Loss: {S['sl']:.2f}
R/R: 1:{S['rr']:.2f}

สัญญาณซื้อ: {', '.join(S['bs'][:4]) or 'ไม่มี'}
สัญญาณขาย: {', '.join(S['ss'][:4]) or 'ไม่มี'}
"""
    # ── ดึงข่าว ────────────────────────────────────────────
    news_items = []
    try:
        news_items = search_stock_news(symbol, company_name, mkt_key)
    except Exception:
        pass

    news_text = "\n=== ข่าวล่าสุด 1 เดือน ===\n"
    if news_items:
        for i, n in enumerate(news_items[:8], 1):
            news_text += f"{i}. [{n['source']}] {n['title']}\n"
    else:
        news_text += "(ไม่สามารถดึงข่าวได้ ใช้ข้อมูล technical เป็นหลัก)\n"

    return tech_summary + news_text, news_items


# ---------------------------------------------------------------
# AI ANALYSIS — Claude API
# ---------------------------------------------------------------
def call_claude_api(prompt, api_key):
    url = "https://api.anthropic.com/v1/messages"
    payload = _json_mod.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 1200,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = _ureq.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    })
    ctx = _ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = _ssl.CERT_NONE
    with _ureq.urlopen(req, timeout=30, context=ctx) as r:
        data = _json_mod.loads(r.read().decode())
    return data["content"][0]["text"]


# ---------------------------------------------------------------
# AI ANALYSIS — Gemini API
# ---------------------------------------------------------------
def call_gemini_api(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = _json_mod.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 1200, "temperature": 0.4}
    }).encode("utf-8")
    req = _ureq.Request(url, data=payload, headers={"Content-Type": "application/json"})
    ctx = _ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = _ssl.CERT_NONE
    with _ureq.urlopen(req, timeout=30, context=ctx) as r:
        data = _json_mod.loads(r.read().decode())
    return data["candidates"][0]["content"]["parts"][0]["text"]


def build_ai_prompt(symbol, company_name, market, context_text):
    return f"""คุณคือนักวิเคราะห์หุ้นมืออาชีพ วิเคราะห์หุ้น {symbol} ({company_name}) ตลาด {market}

{context_text}

กรุณาวิเคราะห์เป็นภาษาไทย ครอบคลุม:

### 📊 สรุปภาพรวม
วิเคราะห์แนวโน้มราคาและ technical signals ที่สำคัญ

### 📰 ผลกระทบจากข่าว
สรุปข่าวที่เกี่ยวข้องและผลกระทบต่อราคาหุ้น

### 🎯 จุดซื้อ-ขาย แนะนำ
- จุดซื้อที่เหมาะสม
- เป้าหมายราคา
- จุด Stop Loss
- Risk/Reward ratio

### ⚠️ ความเสี่ยง
ปัจจัยเสี่ยงสำคัญที่ควรระวัง

### 💡 สรุปคำแนะนำ
ประโยคสั้นๆ สำหรับนักลงทุน swing trade

⚡ หมายเหตุ: นี่คือการวิเคราะห์เพื่อการศึกษาเท่านั้น ไม่ใช่คำแนะนำการลงทุน"""


# ---------------------------------------------------------------
# RENDER AI SETTINGS SIDEBAR (เรียกจาก login view)
# ---------------------------------------------------------------
def render_ai_settings_sidebar():
    """Sidebar แสดงแค่ข้อมูล AI สถานะ — key ใส่ใน tab โดยตรง"""
    with st.sidebar:
        st.markdown("### 🤖 AI วิเคราะห์หุ้น")
        provider = st.session_state.get("ai_provider", "claude")
        has_claude = bool(st.session_state.get("aikey_claude", "").strip())
        has_gemini = bool(st.session_state.get("aikey_gemini", "").strip())

        st.markdown(
            f'<div style="font-size:.78rem;color:var(--txt2);line-height:1.9;">'
            f'🟠 Claude: <strong style="color:{"var(--grn)" if has_claude else "var(--red)"};">'
            f'{"✓ พร้อม" if has_claude else "ยังไม่ได้ใส่ Key"}</strong><br>'
            f'🔵 Gemini: <strong style="color:{"var(--grn)" if has_gemini else "var(--red)"};">'
            f'{"✓ พร้อม" if has_gemini else "ยังไม่ได้ใส่ Key"}</strong><br>'
            f'ใช้งาน: <strong style="color:var(--acc);">'
            f'{"Claude" if provider == "claude" else "Gemini"}</strong>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        cache_count = len(st.session_state.get("ai_analysis_cache", {}))
        st.markdown(
            f'<div style="font-size:.75rem;color:var(--txt3);">Cache: {cache_count} รายการ</div>',
            unsafe_allow_html=True,
        )
        if st.button("🗑 ล้าง Cache AI", use_container_width=True, key="sb_clear_cache"):
            st.session_state.ai_analysis_cache = {}
            st.rerun()


# ---------------------------------------------------------------
# RENDER AI ANALYSIS TAB
# ---------------------------------------------------------------
def render_ai_tab(sym, company_name, mkt_key, I, S):
    """แสดง tab AI Analysis — ไม่มี rerun เมื่อเปลี่ยน provider"""

    sym_safe = "".join(c for c in sym if c.isalnum())

    # ── 1. Provider Selector — ใช้ radio แทนปุ่ม เพื่อไม่ต้อง rerun ──
    st.markdown('<div class="sec-title">🤖 เลือก AI Provider</div>', unsafe_allow_html=True)
    provider = st.radio(
        "AI Provider",
        options=["claude", "gemini"],
        format_func=lambda x: "🟠 Claude (Anthropic)" if x == "claude" else "🔵 Gemini (Google)",
        index=0 if st.session_state.get("ai_provider", "claude") == "claude" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="ai_radio_" + sym_safe,
    )
    # sync provider กลับ session state (radio ทำได้ตรงๆ เพราะ key ไม่ conflict)
    st.session_state["ai_provider"] = provider

    # ── 2. API Key — แต่ละ provider มี widget key ถาวรของตัวเอง ──────
    st.markdown('<div class="sec-title">🔑 API Key</div>', unsafe_allow_html=True)

    # render ทั้งสองช่อง แต่ซ่อนช่องที่ไม่ใช้ด้วย CSS display:none
    # วิธีนี้ทำให้ Streamlit ยัง track ค่าทั้งสองไว้ใน session_state เสมอ
    # แม้ user สลับ provider แล้วกลับมา key ก็ยังอยู่
    if provider == "claude":
        api_key = st.text_input(
            "Claude API Key",
            type="password",
            placeholder="sk-ant-api03-...   ·   รับได้ที่ console.anthropic.com",
            key="aikey_claude",   # key ถาวร ไม่ผูกกับ sym
            help="รับ API Key ฟรีที่ console.anthropic.com → API Keys",
        ).strip()
        provider_label = "Claude Opus"
        badge_cls  = "ai-claude"
        key_link   = "console.anthropic.com"
        key_color  = "#d4896a"
    else:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...   ·   รับได้ฟรีที่ aistudio.google.com (ไม่ต้องใส่บัตรเครดิต)",
            key="aikey_gemini",   # key ถาวร
            help="รับ API Key ฟรีที่ aistudio.google.com → Get API Key",
        ).strip()
        provider_label = "Gemini 2.0 Flash"
        badge_cls  = "ai-gemini"
        key_link   = "aistudio.google.com"
        key_color  = "#6fa8f5"

    if not api_key:
        st.markdown(
            f'<div class="warn-box">'
            f'🔑 ใส่ API Key แล้วกดวิเคราะห์ · '
            f'รับฟรีที่ <strong style="color:{key_color};">{key_link}</strong>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── 3. Cache check ────────────────────────────────────────
    cache_key = f"{sym}_{mkt_key}_{provider}"
    cached    = st.session_state.ai_analysis_cache.get(cache_key)

    if cached:
        age_sec = int((datetime.now() - cached["ts"]).total_seconds())
        age_str = f"{age_sec // 60} นาที" if age_sec >= 60 else f"{age_sec} วินาที"
        st.markdown(
            f'<div style="font-size:.72rem;color:var(--txt3);margin:8px 0 4px;">'
            f'📋 ผลล่าสุด · <span class="ai-badge {badge_cls}">{provider_label}</span>'
            f' · {age_str}ที่แล้ว</div>',
            unsafe_allow_html=True,
        )
        if cached.get("news"):
            with st.expander(f"📰 ข่าวที่ใช้วิเคราะห์ ({len(cached['news'])} รายการ)", expanded=False):
                for n in cached["news"]:
                    st.markdown(
                        f'<div class="news-item">'
                        f'<div class="news-title">{n["title"]}</div>'
                        f'<div class="news-meta">'
                        f'<span class="news-src" style="color:{key_color};">{n["source"]}</span>'
                        + (f' · {n["date"]}' if n.get("date") else "")
                        + f'</div></div>',
                        unsafe_allow_html=True,
                    )
        st.markdown('<div class="sec-title">🧠 ผลวิเคราะห์</div>', unsafe_allow_html=True)
        st.markdown(cached["text"])
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 วิเคราะห์ใหม่", use_container_width=True,
                         key="ai_refresh_" + sym_safe, disabled=not api_key):
                del st.session_state.ai_analysis_cache[cache_key]
                st.rerun()
        with col_r2:
            if st.button("🗑 ล้าง Cache ทั้งหมด", use_container_width=True,
                         key="ai_clearall_" + sym_safe):
                st.session_state.ai_analysis_cache = {}
                st.rerun()
        return

    # ── 4. ปุ่มวิเคราะห์ ─────────────────────────────────────
    st.markdown(
        '<div class="info-box" style="margin-top:8px;">'
        '🌐 ค้นหาข่าว 1 เดือนล่าสุดจากอินเทอร์เน็ต แล้วให้ AI วิเคราะห์ร่วมกับ Technical Indicators'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        f"🚀 วิเคราะห์ {sym} ด้วย {provider_label}",
        use_container_width=True,
        disabled=not api_key,
        key="ai_run_" + sym_safe + "_" + provider,
    ):
        news_items = []
        with st.spinner(f"🌐 กำลังค้นหาข่าว {sym}..."):
            try:
                context_text, news_items = fetch_stock_context_text(
                    sym, company_name, mkt_key, I, S, mkt_key)
            except Exception:
                context_text = (
                    f"Technical: ราคา {I['price']:.2f} "
                    f"RSI {I['rsi']:.1f} คะแนน {S['sc']}/100"
                )

        with st.spinner(f"🤖 {provider_label} กำลังวิเคราะห์..."):
            try:
                prompt = build_ai_prompt(sym, company_name, mkt_key, context_text)
                result_text = (call_claude_api(prompt, api_key)
                               if provider == "claude"
                               else call_gemini_api(prompt, api_key))
                st.session_state.ai_analysis_cache[cache_key] = {
                    "ts":   datetime.now(),
                    "text": result_text,
                    "news": news_items,
                }
                st.rerun()
            except Exception as e:
                err = str(e)
                if "401" in err or "unauthorized" in err.lower() or "invalid_api_key" in err.lower():
                    hint = "❌ API Key ไม่ถูกต้อง — ตรวจสอบแล้วลองใหม่"
                elif "429" in err or "rate" in err.lower():
                    hint = "⏳ Rate limit — รอสักครู่แล้วลองใหม่"
                elif "quota" in err.lower() or "billing" in err.lower():
                    hint = "💳 Quota หมด — ตรวจสอบ billing ใน dashboard"
                elif "timeout" in err.lower():
                    hint = "⏱ Timeout — เครือข่ายช้า ลองใหม่"
                else:
                    hint = "🔌 เชื่อมต่อไม่ได้ — ตรวจสอบ internet และ API key"
                st.markdown(
                    f'<div class="err-box"><strong>{hint}</strong><br>'
                    f'<span style="font-size:.73rem;opacity:.7;">{err[:300]}</span></div>',
                    unsafe_allow_html=True,
                )

# ---------------------------------------------------------------
# SHARED UI
# ---------------------------------------------------------------
def render_header():
    render_ai_settings_sidebar()
    if st.session_state.logged_in:
        badge = '<span style="background:rgba(0,184,148,.15);border:1px solid rgba(0,184,148,.4);color:#00b894;font-size:.65rem;font-weight:700;padding:3px 8px;border-radius:8px;">Settrade Live</span>'
    else:
        badge = '<span style="background:rgba(253,203,110,.1);border:1px solid rgba(253,203,110,.4);color:#fdcb6e;font-size:.65rem;font-weight:700;padding:3px 8px;border-radius:8px;">ยังไม่ได้ Login</span>'
    st.markdown(
        '<div class="app-hdr"><h1>Stock Scanner Pro</h1>'
        '<div class="sub"><span class="ldot"></span>Real-time · 15+ Indicators · 3 ตลาด &nbsp;' + badge + '</div></div>',
        unsafe_allow_html=True
    )

def render_params():
    with st.expander("⚙️ ตั้งค่า Indicators & Filter", expanded=False):
        # ── Preset buttons ──────────────────────────────────────
        st.markdown(
            '<div style="font-size:.72rem;font-weight:700;color:var(--txt3);text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:8px;">Preset สำหรับหุ้นไทย SET</div>',
            unsafe_allow_html=True
        )
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            if st.button("🔥 Swing Trade\n(2–10 วัน)", use_container_width=True, key="preset_swing"):
                for k,v in [("p_sma_s",10),("p_sma_m",25),("p_sma_l",75),
                             ("p_rsi_ob",68),("p_rsi_os",35),("p_min_score",55),("p_min_rr",1.2),("p_min_adx",15)]:
                    st.session_state[k] = v
                st.rerun()
        with pc2:
            if st.button("📈 Trend Follow\n(สัปดาห์–เดือน)", use_container_width=True, key="preset_trend"):
                for k,v in [("p_sma_s",20),("p_sma_m",50),("p_sma_l",150),
                             ("p_rsi_ob",70),("p_rsi_os",40),("p_min_score",60),("p_min_rr",1.5),("p_min_adx",22)]:
                    st.session_state[k] = v
                st.rerun()
        with pc3:
            if st.button("💎 Value+Tech\n(เน้นคุณภาพ)", use_container_width=True, key="preset_value"):
                for k,v in [("p_sma_s",25),("p_sma_m",75),("p_sma_l",200),
                             ("p_rsi_ob",65),("p_rsi_os",38),("p_min_score",62),("p_min_rr",1.8),("p_min_adx",20)]:
                    st.session_state[k] = v
                st.rerun()

        st.markdown("---")
        st.markdown(
            '<div class="info-box" style="font-size:.75rem;">'
            '<strong>💡 คำแนะนำ SET:</strong> '
            'SMA 10/25/75 เหมาะกับหุ้นไทยมากกว่า 20/50/200 · '
            'RSI Oversold ที่ 35 จับ bounce ได้ก่อน · '
            'ADX &gt; 15 เริ่มมี trend · '
            'ลด min_score → เห็นหุ้นมากขึ้น แต่ noise มากด้วย'
            '</div>',
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Moving Averages**")
            st.slider("SMA สั้น (วัน)", 5, 30, DEF["sma_s"], key="p_sma_s",
                      help="10 วัน = momentum สั้น / swing")
            st.slider("SMA กลาง (วัน)", 15, 75, DEF["sma_m"], key="p_sma_m",
                      help="25 วัน = แนวโน้ม mid-term")
            st.slider("SMA ยาว (วัน)", 50, 250, DEF["sma_l"], key="p_sma_l",
                      help="75 วัน = trend ระยะกลาง (200 ยาวเกินสำหรับ SET)")
            st.markdown("**RSI**")
            st.slider("RSI Period", 7, 21, DEF["rsi_p"], key="p_rsi_p")
            st.slider("RSI Overbought", 60, 82, DEF["rsi_ob"], key="p_rsi_ob",
                      help="SET มักหมุนก่อนถึง 70 → แนะนำ 65–68")
            st.slider("RSI Oversold", 20, 45, DEF["rsi_os"], key="p_rsi_os",
                      help="35 จับ bounce ได้ก่อน 30")
            st.markdown("**MACD**")
            st.slider("MACD Fast", 8, 20, DEF["macd_f"], key="p_macd_f")
            st.slider("MACD Slow", 20, 40, DEF["macd_s"], key="p_macd_s")
            st.slider("MACD Signal", 5, 15, DEF["macd_sg"], key="p_macd_sg")
        with c2:
            st.markdown("**Bollinger Bands & Stoch**")
            st.slider("BB Period", 10, 30, DEF["bb_p"], key="p_bb_p")
            st.slider("BB Std Dev", 1, 3, DEF["bb_k"], key="p_bb_k")
            st.slider("Stoch %K", 5, 21, DEF["stoch_k"], key="p_stoch_k")
            st.slider("Stoch %D", 2, 7, DEF["stoch_d"], key="p_stoch_d")
            st.markdown("**Other Indicators**")
            st.slider("ATR Period", 7, 21, DEF["atr_p"], key="p_atr_p")
            st.slider("CCI Period", 10, 30, DEF["cci_p"], key="p_cci_p")
            st.slider("Williams %R", 7, 21, DEF["wr_p"], key="p_wr_p")
            st.slider("MFI Period", 7, 21, DEF["mfi_p"], key="p_mfi_p")
            st.slider("ADX Period", 7, 21, DEF["adx_p"], key="p_adx_p")

        st.markdown("**ตัวกรองผลลัพธ์**")
        c3, c4, c5 = st.columns(3)
        with c3:
            st.slider("คะแนนขั้นต่ำ", 0, 100, DEF["min_score"], key="p_min_score",
                      help="55 = เห็นมาก, 65 = เข้มงวด")
        with c4:
            st.slider("R/R ขั้นต่ำ", 0.5, 5.0, float(DEF["min_rr"]), step=0.1, key="p_min_rr",
                      help="1.2 เหมาะ SET / 1.5+ เข้มงวด")
        with c5:
            st.slider("ADX ขั้นต่ำ", 0, 40, DEF["min_adx"], key="p_min_adx",
                      help="15 = early trend / 25 = strong trend")

def render_deep(sym, mkt_key, I, S, info, yf_info=None):
    p = get_params()
    mkt = MARKETS.get(mkt_key, {"flag":"?","name":"Custom","currency":"","tag":"tus"})
    cur = mkt["currency"]
    tag = mkt["tag"]
    pr  = I["price"]
    sc  = S["sc"]

    # pre-compute all display strings (no conditionals inside f-strings)
    price_color  = "#00b894" if I["chg"] >= 0 else "#d63031"
    chg_sign     = "+" if I["chg"] >= 0 else ""
    chg5_sign    = "+" if I["chg_5d"] >= 0 else ""
    chg20_sign   = "+" if I["chg_20d"] >= 0 else ""
    pr_str       = cur + "{:,.2f}".format(pr)
    chg_str      = chg_sign + "{:.2f}%".format(I["chg"])
    chg5_str     = chg5_sign + "{:.1f}%".format(I["chg_5d"])
    chg20_str    = chg20_sign + "{:.1f}%".format(I["chg_20d"])
    sc_color     = "#00b894" if sc >= 65 else "#fdcb6e" if sc >= 45 else "#d63031"
    score_cls    = "sh" if sc >= 65 else "sm" if sc >= 45 else "sl"
    chip_cls     = "chip-" + S["cls"]
    chg_cls      = "cup" if I["chg"] >= 0 else "cdn"
    src_lbl      = {"settrade":"Settrade Live","yfinance":"Yahoo Finance","mock":"Mock Data"}.get(info.get("source","mock"),"")
    name_str     = dict(mkt.get("stocks",[])).get(sym, sym)
    rr_str       = "1:" + "{:.2f}".format(S["rr"])
    entry_str    = cur + "{:,.2f}".format(S["entry"])
    sl_str       = cur + "{:,.2f}".format(S["sl"])
    t1_str       = cur + "{:,.2f}".format(S["t1"])
    t2_str       = cur + "{:,.2f}".format(S["t2"])
    t2_pct       = round((S["t2"]/pr-1)*100, 1) if pr > 0 else 0
    open_str     = cur + "{:,.2f}".format(I["open"])
    high_str     = cur + "{:,.2f}".format(I["high_d"])
    low_str      = cur + "{:,.2f}".format(I["low_d"])
    volr_str     = "{:.1f}x".format(I["vol_r"])
    volr_cls     = "t1" if I["vol_r"] > 1.5 else ""
    r2_str       = cur + "{:,.2f}".format(I["r2"])
    r1_str       = cur + "{:,.2f}".format(I["r1"])
    pv_str       = cur + "{:,.2f}".format(I["pivot"])
    s1_str       = cur + "{:,.2f}".format(I["s1"])
    s2_str       = cur + "{:,.2f}".format(I["s2"])
    ic_conv_str  = cur + "{:,.2f}".format(I["ichi_conv"])
    ic_base_str  = cur + "{:,.2f}".format(I["ichi_base"])
    ic_sa_str    = cur + "{:,.2f}".format(I["ichi_sa"])
    ic_sb_str    = cur + "{:,.2f}".format(I["ichi_sb"])
    wl_str       = cur + "{:,.2f}".format(I["52wl"])
    wh_str       = cur + "{:,.2f}".format(I["52wh"])
    sma_s_str    = cur + "{:,.1f}".format(I["sma_s"])
    sma_m_str    = cur + "{:,.1f}".format(I["sma_m"])
    sma_l_str    = cur + "{:,.1f}".format(I["sma_l"])
    vwap_str     = cur + "{:,.2f}".format(I["vwap"])
    atr_str      = cur + "{:,.2f}".format(I["atr"])
    ts_now       = datetime.now().strftime("%H:%M:%S")
    rr_advice    = ("R/R ดีมาก" if S["rr"] >= 2 else "R/R พอได้" if S["rr"] >= 1.5 else "R/R ต่ำ ระวัง")
    rr_color     = "#00b894" if S["rr"] >= 2 else "#fdcb6e" if S["rr"] >= 1.5 else "#d63031"
    ichi_b       = pr > I["ichi_sa"] and pr > I["ichi_sb"]
    ichi_s       = pr < I["ichi_sa"] and pr < I["ichi_sb"]
    ichi_txt     = "เหนือ Cloud Bullish" if ichi_b else ("ใต้ Cloud Bearish" if ichi_s else "ใน Cloud Neutral")
    ichi_color   = "#00b894" if ichi_b else "#d63031" if ichi_s else "#fdcb6e"
    pct_52       = min(100, max(0, (pr-I["52wl"])/(I["52wh"]-I["52wl"]+1e-9)*100))
    pct_52_str   = "{:.0f}%".format(pct_52)
    pct_52_w     = "{:.1f}%".format(pct_52)

    # Header
    st.markdown(
        '<div class="da-hdr">'
        '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">'
        '<div><span class="da-sym">' + sym + '</span>'
        '<span class="da-tag ' + tag + '">' + mkt["flag"] + ' ' + mkt_key + '</span>'
        '<div style="font-size:.72rem;color:#8892b0;margin-top:4px;">' + name_str + '</div></div>'
        '<div class="sring ' + score_cls + '" style="width:54px;height:54px;font-size:1.05rem;">' + str(sc) + '</div>'
        '</div>'
        '<div style="margin-top:14px;display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:8px;">'
        '<div><div class="da-price" style="color:' + price_color + '">' + pr_str + '</div>'
        '<span class="sc-chg ' + chg_cls + '">' + chg_str + ' วันนี้</span>'
        ' <span style="color:#8892b0;font-size:.7rem;">' + chg5_str + ' 5วัน ' + chg20_str + ' 20วัน</span></div>'
        '<div style="text-align:right;">'
        '<span class="chip ' + chip_cls + '">' + S["rec"] + '</span>'
        '<div style="font-size:.7rem;color:#8892b0;margin-top:5px;">R/R <span style="color:#6c63ff;font-weight:700;">' + rr_str + '</span></div>'
        '</div></div>'
        '<div style="margin-top:10px;font-size:.68rem;color:#636e72;">' + src_lbl + ' · ' + ts_now + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # OHLCV
    st.markdown(
        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:12px;">'
        '<div class="tgt"><div class="tl">เปิด</div><div class="tv" style="color:#e2e8f0;">' + open_str + '</div></div>'
        '<div class="tgt"><div class="tl">สูงสุด</div><div class="tv t1">' + high_str + '</div></div>'
        '<div class="tgt"><div class="tl">ต่ำสุด</div><div class="tv ts">' + low_str + '</div></div>'
        '<div class="tgt"><div class="tl">Volume</div><div class="tv ' + volr_cls + '">' + volr_str + '</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    tab_tech, tab_target, tab_sig, tab_fund, tab_ai = st.tabs(["Technical","เป้าหมาย","สัญญาณ","พื้นฐาน","🤖 AI วิเคราะห์"])

    with tab_tech:
        def ib(lbl, val, is_b, is_s):
            cls2 = "bull" if is_b else "bear" if is_s else "neut"
            arrow = "Bullish" if is_b else "Bearish" if is_s else "Neutral"
            return ('<div class="ibox"><div class="ilabel">' + lbl + '</div>'
                    '<div class="ival ' + cls2 + '">' + str(val) + '</div>'
                    '<div class="ist ' + cls2 + '">' + arrow + '</div></div>')

        ma_b = pr > I["sma_s"] > I["sma_m"]
        ma_s = pr < I["sma_s"] < I["sma_m"]
        rows = [
            ib("RSI", "{:.1f}".format(I["rsi"]), I["rsi"]<p["rsi_os"], I["rsi"]>p["rsi_ob"]),
            ib("MACD Hist", "{:.4f}".format(I["macd_h"]), I["macd"]>I["macd_sig"], I["macd"]<I["macd_sig"]),
            ib("SMA Trend", "Up" if ma_b else "Down" if ma_s else "Flat", ma_b, ma_s),
            ib("SMA" + str(p["sma_l"]), sma_l_str, pr > I["sma_l"], pr < I["sma_l"]),
            ib("BB %B", "{:.2f}".format(I["bbp"]), I["bbp"]<0.2, I["bbp"]>0.8),
            ib("BB Width", "{:.1f}%".format(I["bb_width"]), False, False),
            ib("Stoch %K", "{:.1f}".format(I["sk"]), I["sk"]<20 and I["sk"]>I["sd"], I["sk"]>80 and I["sk"]<I["sd"]),
            ib("CCI", "{:.1f}".format(I["cci"]), I["cci"]<-100, I["cci"]>100),
            ib("Williams %R", "{:.1f}".format(I["wr"]), I["wr"]<-80, I["wr"]>-20),
            ib("MFI", "{:.1f}".format(I["mfi"]), I["mfi"]<20, I["mfi"]>80),
            ib("ADX", "{:.1f}".format(I["adx"]), I["adx"]>25 and I["dip"]>I["dim"], I["adx"]>25 and I["dim"]>I["dip"]),
            ib("OBV", "Up" if I["obv_up"] else "Down", I["obv_up"], not I["obv_up"]),
            ib("VWAP", vwap_str, pr > I["vwap"], pr < I["vwap"]),
            ib("Ichimoku", ichi_txt, ichi_b, ichi_s),
            ib("Vol Ratio", volr_str, I["vol_r"]>1.5, I["vol_r"]<0.5),
            ib("ATR", atr_str, False, False),
        ]
        st.markdown('<div class="ind-grid">' + "".join(rows) + '</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-title">Pivot Points</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="pvt-row">'
            '<div class="pvt"><div class="pvtl">R2</div><div class="pvtv" style="color:#ff7675;">' + r2_str + '</div></div>'
            '<div class="pvt"><div class="pvtl">R1</div><div class="pvtv" style="color:#fab1a0;">' + r1_str + '</div></div>'
            '<div class="pvt"><div class="pvtl">PIVOT</div><div class="pvtv" style="color:#74b9ff;">' + pv_str + '</div></div>'
            '<div class="pvt"><div class="pvtl">S1</div><div class="pvtv" style="color:#55efc4;">' + s1_str + '</div></div>'
            '<div class="pvt"><div class="pvtl">S2</div><div class="pvtv" style="color:#00cec9;">' + s2_str + '</div></div>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="sec-title">Ichimoku</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;">'
            '<div class="tgt"><div class="tl">Tenkan</div><div class="tv te">' + ic_conv_str + '</div></div>'
            '<div class="tgt"><div class="tl">Kijun</div><div class="tv" style="color:#fab1a0;">' + ic_base_str + '</div></div>'
            '<div class="tgt"><div class="tl">Span A</div><div class="tv t1">' + ic_sa_str + '</div></div>'
            '<div class="tgt"><div class="tl">Span B</div><div class="tv ts">' + ic_sb_str + '</div></div>'
            '</div>'
            '<div style="background:' + ichi_color + '18;border:1px solid ' + ichi_color + '50;border-radius:10px;padding:10px;text-align:center;font-size:.82rem;color:' + ichi_color + ';font-weight:700;">'
            + ichi_txt + '</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="sec-title">52-Week Range</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="background:#1a1a2e;border-radius:10px;padding:12px;">'
            '<div style="display:flex;justify-content:space-between;font-size:.7rem;color:#8892b0;margin-bottom:6px;">'
            '<span>Low: ' + wl_str + '</span>'
            '<span style="color:#e2e8f0;font-weight:600;">' + pct_52_str + ' จากต่ำสุด</span>'
            '<span>High: ' + wh_str + '</span></div>'
            '<div style="background:#2a2a4a;border-radius:4px;height:8px;position:relative;">'
            '<div style="position:absolute;left:0;top:0;height:8px;width:' + pct_52_w + ';background:linear-gradient(90deg,#6c63ff,#00b894);border-radius:4px;"></div>'
            '</div></div>',
            unsafe_allow_html=True
        )

    with tab_target:
        st.markdown(
            '<div style="background:rgba(108,99,255,.08);border:1px solid rgba(108,99,255,.25);border-radius:14px;padding:16px;margin-bottom:14px;text-align:center;">'
            '<div style="font-size:.72rem;color:#8892b0;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">คะแนนรวม</div>'
            '<div style="font-size:2.5rem;font-weight:700;color:' + sc_color + ';font-family:IBM Plex Mono,monospace;">' + str(sc) + '<span style="font-size:1rem;color:#636e72;">/100</span></div>'
            '<div style="margin-top:8px;"><span class="chip ' + chip_cls + '" style="font-size:.85rem;padding:6px 16px;">' + S["rec"] + '</span></div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="sec-title">ราคาเป้าหมาย</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="trow" style="grid-template-columns:1fr 1fr;gap:10px;">'
            '<div class="tgt" style="padding:14px;"><div class="tl">จุดซื้อ</div><div class="tv te" style="font-size:1.1rem;margin-top:6px;">' + entry_str + '</div><div style="font-size:.65rem;color:#8892b0;margin-top:4px;">-1.5%</div></div>'
            '<div class="tgt" style="padding:14px;"><div class="tl">Stop Loss</div><div class="tv ts" style="font-size:1.1rem;margin-top:6px;">' + sl_str + '</div><div style="font-size:.65rem;color:#8892b0;margin-top:4px;">-' + "{:.1f}%".format(S["dn"]) + ' ATRx1.5</div></div>'
            '<div class="tgt" style="padding:14px;"><div class="tl">เป้า 1</div><div class="tv t1" style="font-size:1.1rem;margin-top:6px;">' + t1_str + '</div><div style="font-size:.65rem;color:#8892b0;margin-top:4px;">+' + "{:.1f}%".format(S["up"]) + ' ATRx2</div></div>'
            '<div class="tgt" style="padding:14px;"><div class="tl">เป้า 2</div><div class="tv t2" style="font-size:1.1rem;margin-top:6px;">' + t2_str + '</div><div style="font-size:.65rem;color:#8892b0;margin-top:4px;">+' + "{:.1f}%".format(t2_pct) + ' ATRx3.5</div></div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="background:rgba(108,99,255,.08);border:1px solid rgba(108,99,255,.3);border-radius:12px;padding:14px;margin-top:12px;text-align:center;">'
            '<div style="font-size:.72rem;color:#8892b0;text-transform:uppercase;letter-spacing:1px;">Risk / Reward</div>'
            '<div style="font-size:2rem;font-weight:700;color:' + rr_color + ';font-family:IBM Plex Mono,monospace;margin:6px 0;">' + rr_str + '</div>'
            '<div style="font-size:.78rem;color:#8892b0;">+' + "{:.1f}%".format(S["up"]) + ' vs -' + "{:.1f}%".format(S["dn"]) + '%</div>'
            '<div style="font-size:.7rem;color:' + rr_color + ';margin-top:6px;">' + rr_advice + '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="sec-title">ระยะห่างจากค่าเฉลี่ย</div>', unsafe_allow_html=True)
        for sma_v, sma_str, lbl in [(I["sma_s"], sma_s_str, "SMA"+str(p["sma_s"])),
                                     (I["sma_m"], sma_m_str, "SMA"+str(p["sma_m"])),
                                     (I["sma_l"], sma_l_str, "SMA"+str(p["sma_l"]))]:
            dist = (pr/sma_v-1)*100 if sma_v else 0
            bar_w = min(abs(dist)*3, 100)
            bar_c = "#00b894" if dist >= 0 else "#d63031"
            dist_sign = "+" if dist >= 0 else ""
            dist_str2 = dist_sign + "{:.1f}%".format(dist)
            bar_ml = "margin-left:auto;" if dist < 0 else ""
            st.markdown(
                '<div style="background:#1a1a2e;border-radius:10px;padding:10px 12px;margin-bottom:6px;">'
                '<div style="display:flex;justify-content:space-between;font-size:.78rem;margin-bottom:5px;">'
                '<span style="color:#8892b0;">' + lbl + '</span>'
                '<span style="color:' + bar_c + ';font-weight:700;font-family:IBM Plex Mono,monospace;">' + dist_str2 + '</span></div>'
                '<div style="background:#2a2a4a;border-radius:4px;height:4px;">'
                '<div style="height:4px;width:' + "{:.0f}%".format(bar_w) + ';background:' + bar_c + ';border-radius:4px;' + bar_ml + '"></div>'
                '</div></div>',
                unsafe_allow_html=True
            )

    with tab_sig:
        buy_n = len(S["bs"]); sell_n = len(S["ss"]); neut_n = len(S["ns"])
        st.markdown(
            '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px;">'
            '<div style="background:rgba(0,184,148,.1);border:1px solid rgba(0,184,148,.25);border-radius:10px;padding:10px;text-align:center;">'
            '<div style="font-size:1.4rem;font-weight:700;color:#00b894;">' + str(buy_n) + '</div>'
            '<div style="font-size:.68rem;color:#8892b0;">ซื้อ</div></div>'
            '<div style="background:rgba(99,110,114,.1);border:1px solid rgba(99,110,114,.25);border-radius:10px;padding:10px;text-align:center;">'
            '<div style="font-size:1.4rem;font-weight:700;color:#636e72;">' + str(neut_n) + '</div>'
            '<div style="font-size:.68rem;color:#8892b0;">กลาง</div></div>'
            '<div style="background:rgba(214,48,49,.1);border:1px solid rgba(214,48,49,.25);border-radius:10px;padding:10px;text-align:center;">'
            '<div style="font-size:1.4rem;font-weight:700;color:#d63031;">' + str(sell_n) + '</div>'
            '<div style="font-size:.68rem;color:#8892b0;">ขาย</div></div>'
            '</div>',
            unsafe_allow_html=True
        )
        if S["bs"]:
            st.markdown('<div class="sec-title">สัญญาณซื้อ</div>', unsafe_allow_html=True)
            for sig in S["bs"]:
                st.markdown('<div class="sig-item sig-buy">' + sig + '</div>', unsafe_allow_html=True)
        if S["ss"]:
            st.markdown('<div class="sec-title">สัญญาณขาย</div>', unsafe_allow_html=True)
            for sig in S["ss"]:
                st.markdown('<div class="sig-item sig-sell">' + sig + '</div>', unsafe_allow_html=True)
        if S["ns"]:
            st.markdown('<div class="sec-title">ข้อมูลกลาง</div>', unsafe_allow_html=True)
            for sig in S["ns"]:
                st.markdown('<div class="sig-item sig-neut">' + sig + '</div>', unsafe_allow_html=True)

    with tab_fund:
        if yf_info and isinstance(yf_info, dict) and yf_info.get("regularMarketPrice"):
            yi = yf_info
            def _fmtv(key, mult=1, fmt="{:.2f}", fallback="N/A"):
                v = yi.get(key)
                if v is None: return fallback
                try: return fmt.format(float(v)*mult)
                except Exception: return fallback
            mc_r = yi.get("marketCap")
            mc_str = "{:,}".format(int(mc_r)) if mc_r else "N/A"
            biz = str(yi.get("longBusinessSummary","N/A"))[:300]
            rows2 = [
                ("P/E (TTM)", _fmtv("trailingPE"), "ราคาต่อกำไร"),
                ("Forward P/E", _fmtv("forwardPE"), "P/E คาดการณ์"),
                ("P/B", _fmtv("priceToBook"), "ราคาต่อมูลค่าบัญชี"),
                ("ROE", _fmtv("returnOnEquity", 100, "{:.1f}%"), "ผลตอบแทนผู้ถือหุ้น"),
                ("EPS (TTM)", _fmtv("trailingEps"), "กำไรต่อหุ้น"),
                ("Div Yield", _fmtv("dividendYield", 100, "{:.2f}%"), "อัตราปันผล"),
                ("Market Cap", mc_str, "มูลค่าตลาด"),
                ("Beta", _fmtv("beta"), "ความผันผวน"),
                ("Rev Growth", _fmtv("revenueGrowth", 100, "{:.1f}%"), "การเติบโตรายได้"),
                ("Margin", _fmtv("profitMargins", 100, "{:.1f}%"), "อัตรากำไร"),
                ("D/E", _fmtv("debtToEquity"), "หนี้สินต่อทุน"),
                ("Current Ratio", _fmtv("currentRatio"), "สภาพคล่อง"),
            ]
            html = '<div class="fund-grid">'
            for lbl, val, desc in rows2:
                html += ('<div class="fbox"><div class="flabel">' + lbl + '</div>'
                         '<div class="fval">' + val + '</div>'
                         '<div class="fdesc">' + desc + '</div></div>')
            html += '</div>'
            html += ('<div style="background:#1a1a2e;border-radius:10px;padding:12px;font-size:.78rem;color:#8892b0;line-height:1.7;">'
                     '<span style="color:#e2e8f0;font-weight:600;">Business: </span>' + biz + '...</div>')
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("ข้อมูลพื้นฐานใช้ได้กับหุ้น US/CN ผ่าน yfinance\nติดตั้ง: pip install yfinance")

    with tab_ai:
        company_name = dict(mkt.get("stocks",[])).get(sym, sym)
        render_ai_tab(sym, company_name, mkt_key, I, S)

# ---------------------------------------------------------------
# VIEWS
# ---------------------------------------------------------------
def view_login():
    render_header()
    ta_ok  = "OK" if TA_OK  else "ยังไม่ติดตั้ง"
    st_ok  = "OK" if ST_OK  else "ยังไม่ติดตั้ง"
    yf_ok  = "OK" if YF_OK  else "ยังไม่ติดตั้ง"
    lib_warn = "" if ST_OK and TA_OK else "pip install settrade-v2 pandas_ta yfinance"
    st.markdown(
        '<div style="background:#12122a;border:1px solid #2a2a4a;border-radius:12px;padding:12px 16px;margin-bottom:14px;">'
        '<div style="font-size:.72rem;color:#8892b0;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">สถานะ Library</div>'
        '<div style="font-size:.82rem;">'
        'settrade-v2: <strong style="color:#e2e8f0;">' + st_ok + '</strong> &nbsp;|&nbsp; '
        'pandas_ta: <strong style="color:#e2e8f0;">' + ta_ok + '</strong> &nbsp;|&nbsp; '
        'yfinance: <strong style="color:#e2e8f0;">' + yf_ok + '</strong>'
        '</div>'
        + ('<div style="margin-top:8px;font-size:.75rem;color:#fdcb6e;">ติดตั้ง: ' + lib_warn + '</div>' if lib_warn else '')
        + '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="login-card">'
        '<h2>เชื่อมต่อ Settrade API</h2>'
        '<div class="login-sub">'
        'กรอก credential จาก <strong style="color:#6c63ff;">developer.settrade.com</strong><br>'
        'สำหรับ SANDBOX ใช้ค่าด้านล่างได้เลย (ข้อมูล demo ไม่ใช่ real-time)'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="info-box">'
        '<strong>📋 วิธีรับ Credential จริง</strong><br>'
        '1. เข้า developer.settrade.com แล้ว Register<br>'
        '2. สร้าง Application รับ APP_ID และ APP_SECRET<br>'
        '3. APP_CODE และ BROKER_ID ดูจากหน้า Application<br>'
        '<span style="color:#fdcb6e;">⚠ SANDBOX ใช้ข้อมูล demo เท่านั้น ไม่ใช่ราคาจริง</span>'
        '</div>',
        unsafe_allow_html=True
    )
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("🧪 ใช้ค่า SANDBOX (ทดสอบ)", use_container_width=True):
            st.session_state.prefill_id     = "MPRZz1Hymo6nR50A"
            st.session_state.prefill_secret = "Te/3LKXBb+IM20T/ygcFAMWXjIgkadJ+o1cDstkjRDQ="
            st.session_state.prefill_code   = "SANDBOX"
            st.session_state.prefill_broker = "SANDBOX"
            st.rerun()
    with col_sb2:
        if st.button("🗑 ล้างค่า", use_container_width=True):
            st.session_state.prefill_id     = ""
            st.session_state.prefill_secret = ""
            st.session_state.prefill_code   = ""
            st.session_state.prefill_broker = ""
            st.rerun()
    with st.form("login_form"):
        app_id     = st.text_input("APP_ID", value=st.session_state.prefill_id, placeholder="เช่น MPRZz1Hymo6nR50A")
        app_secret = st.text_input("APP_SECRET", value=st.session_state.prefill_secret, type="password", placeholder="App Secret จาก Settrade Developer")
        app_code   = st.text_input("APP_CODE", value=st.session_state.prefill_code, placeholder="เช่น SANDBOX หรือ code ของคุณ")
        broker_id  = st.text_input("BROKER_ID", value=st.session_state.prefill_broker, placeholder="เช่น SANDBOX หรือรหัสโบรกเกอร์")
        show_debug = st.checkbox("แสดง debug log", value=False)
        submitted  = st.form_submit_button("🔌 เชื่อมต่อ Settrade", use_container_width=True)
    if submitted:
        if not ST_OK:
            st.markdown('<div class="err-box">settrade_v2 ไม่ได้ติดตั้ง: pip install settrade-v2</div>', unsafe_allow_html=True)
        elif not app_id.strip() or not app_secret.strip():
            st.markdown('<div class="err-box">กรุณากรอก APP_ID และ APP_SECRET</div>', unsafe_allow_html=True)
        else:
            with st.spinner("กำลังเชื่อมต่อ Settrade..."):
                err_detail = ""
                try:
                    if show_debug:
                        st.info("Debug: กำลัง connect ด้วย app_id=" + app_id.strip()[:8] + "... app_code=" + app_code.strip() + " broker=" + broker_id.strip())
                    # settrade-v2 รองรับทั้ง parameter เก่าและใหม่
                    # ลอง is_auto_queue=True ก่อน (version ใหม่ >= 1.x)
                    try:
                        inv = Investor(
                            app_id=app_id.strip(),
                            app_secret=app_secret.strip(),
                            app_code=app_code.strip(),
                            broker_id=broker_id.strip(),
                            is_auto_queue=False,
                        )
                    except TypeError:
                        # version เก่าไม่มี is_auto_queue
                        inv = Investor(
                            app_id=app_id.strip(),
                            app_secret=app_secret.strip(),
                            app_code=app_code.strip(),
                            broker_id=broker_id.strip(),
                        )

                    mkt_api = inv.MarketData()

                    # settrade-v2 เปลี่ยนชื่อ method ระหว่าง version:
                    # v0.x → RealtimeData()
                    # v1.x+ → ไม่มี RealtimeData แล้ว ใช้ MarketData แทนทุกอย่าง
                    rt_api = None
                    for _rt_method in ["RealtimeData", "Streaming", "realtime"]:
                        if hasattr(inv, _rt_method):
                            try:
                                rt_api = getattr(inv, _rt_method)()
                            except Exception:
                                pass
                            break
                    # ถ้าไม่มี RealtimeData เลย ให้ใช้ MarketData แทน (v1.x)
                    if rt_api is None:
                        rt_api = mkt_api
                        if show_debug:
                            st.info("Debug: ไม่พบ RealtimeData → ใช้ MarketData แทน (settrade-v2 v1.x+)")

                    # ทดสอบ connection ด้วย candlestick ของ PTT
                    try:
                        test = mkt_api.get_candlestick("PTT", interval="1d", limit=5)
                        connected = test is not None and len(test) > 0
                        if show_debug:
                            st.info("Debug: candlestick test = " + str(test)[:200])
                    except Exception as test_err:
                        err_detail = " (candlestick test: " + str(test_err) + ")"
                        if show_debug:
                            st.warning("Debug candlestick error: " + str(test_err))
                        # ถ้า test ล้มเหลวแต่ connect ได้ให้ยังถือว่า connected
                        connected = True

                    if connected:
                        st.session_state.logged_in    = True
                        st.session_state.market_api   = mkt_api
                        st.session_state.realtime_api = rt_api
                        st.session_state.view = "scan"
                        st.rerun()
                    else:
                        raise ValueError("API ตอบสนองแต่ไม่มีข้อมูล (ลอง SANDBOX credentials)")

                except Exception as e:
                    full_err = str(e) + err_detail
                    st.markdown(
                        '<div class="err-box">'
                        '<strong>เชื่อมต่อไม่สำเร็จ</strong><br>'
                        + full_err +
                        '<br><br>'
                        '<span style="color:#fdcb6e;font-size:.78rem;">'
                        '💡 ตรวจสอบ: APP_ID / APP_SECRET ถูกต้องไหม? '
                        'BROKER_ID ตรงกับ account ไหม? '
                        'หรือลอง SANDBOX สำหรับทดสอบ'
                        '</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("ข้าม / Mock Data", use_container_width=True):
            st.session_state.view = "scan"; st.rerun()
    with c2:
        if st.button("ข้าม / Yahoo Finance", use_container_width=True):
            st.session_state.view = "scan"; st.rerun()

def view_scan():
    render_header()
    render_params()
    p = get_params()
    col_n1, col_n2 = st.columns([3, 1])
    with col_n2:
        if st.button("วิเคราะห์หุ้น", use_container_width=True):
            st.session_state.view = "manual"; st.rerun()
    st.markdown('<div class="sec-title">1 เลือกตลาดหุ้น</div>', unsafe_allow_html=True)
    mkt_cols = st.columns(3)
    mkt_labels = {"SET":"TH SET\nSET50/100/mai", "US":"US Tech\nNASDAQ/NYSE", "CN":"CN Tech\nNYSE ADR"}
    for i, mkt_key in enumerate(["SET","US","CN"]):
        with mkt_cols[i]:
            is_sel = st.session_state.market == mkt_key
            if st.button(mkt_labels[mkt_key], key="mkt_"+mkt_key, use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                st.session_state.market = mkt_key; st.rerun()
    mkt_key = st.session_state.market
    if not mkt_key:
        st.markdown('<div style="text-align:center;padding:32px;color:#636e72;">เลือกตลาดก่อน</div>', unsafe_allow_html=True)
        return
    mkt = MARKETS[mkt_key]; cur = mkt["currency"]; n = len(mkt["stocks"])
    use_live = st.session_state.logged_in and mkt_key == "SET"
    src_lbl = "Settrade Live" if use_live else ("Yahoo Finance" if YF_OK else "Mock")
    st.markdown(
        '<div style="background:#12122a;border:1px solid rgba(108,99,255,.3);border-radius:10px;padding:10px 14px;margin:8px 0 14px;display:flex;justify-content:space-between;align-items:center;">'
        '<span style="color:#e2e8f0;font-size:.85rem;"><strong>' + mkt["name"] + '</strong> · ' + str(n) + ' หุ้น · ' + cur + '</span>'
        '<span style="font-size:.68rem;color:#8892b0;">' + src_lbl + '</span></div>',
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        filt_sig = st.multiselect("สัญญาณ", ["🟢 ซื้อ","🟡 เฝ้าระวัง","⚪ ถือ","🔴 ขาย"],
            default=["🟢 ซื้อ","🟡 เฝ้าระวัง"], key="filt_sig", label_visibility="collapsed", placeholder="เลือกสัญญาณ")
    with c2:
        sort_by = st.selectbox("เรียง", ["Score","RSI","Change","ADX"], key="sort_by", label_visibility="collapsed")
    st.markdown('<div class="sec-title">2 สแกน</div>', unsafe_allow_html=True)
    if st.button("สแกน " + mkt["flag"] + " " + mkt_key + " (" + str(n) + " หุ้น)", use_container_width=True):
        results = []; prog = st.progress(0); stxt = st.empty()
        for i, (sym, name) in enumerate(mkt["stocks"]):
            stxt.markdown('<div style="text-align:center;font-size:.75rem;color:#8892b0;">สแกน ' + sym + ' (' + str(i+1) + '/' + str(n) + ')</div>', unsafe_allow_html=True)
            try:
                df, info = get_data(sym, mkt_key)
                I = compute_indicators(df, p); S = score_stock(I, p)
                results.append(dict(Symbol=sym, Name=name, Market=mkt_key,
                    Price=round(I["price"],2), Change=round(I["chg"],2),
                    RSI=round(I["rsi"],1), ADX=round(I["adx"],1),
                    BB=round(I["bbp"],2), VR=round(I["vol_r"],2),
                    Score=S["sc"], Signal=S["rec"], SigCls=S["cls"],
                    Entry=S["entry"], T1=S["t1"], T2=S["t2"], SL=S["sl"], RR=S["rr"],
                    _I=I, _S=S, _info=info))
            except Exception:
                pass
            prog.progress((i+1)/n)
        prog.empty(); stxt.empty()
        st.session_state.scan_results[mkt_key] = pd.DataFrame(results)
    df_res = st.session_state.scan_results.get(mkt_key)
    if df_res is None or len(df_res) == 0:
        return
    sigs = filt_sig or ["🟢 ซื้อ","🟡 เฝ้าระวัง","⚪ ถือ","🔴 ขาย"]
    df_f = df_res[(df_res["Score"] >= p["min_score"]) & (df_res["RR"] >= p["min_rr"]) & (df_res["Signal"].isin(sigs))].copy()
    sort_map = {"Score":"Score","RSI":"RSI","Change":"Change","ADX":"ADX"}
    df_f = df_f.sort_values(sort_map.get(sort_by,"Score"), ascending=False)
    buy_n = len(df_res[df_res["SigCls"]=="buy"]); sell_n = len(df_res[df_res["SigCls"]=="sell"])
    watch_n = len(df_res[df_res["SigCls"]=="watch"]); avg_sc = df_res["Score"].mean()
    st.markdown(
        '<div class="upd-bar">'
        '<span>พบ <strong style="color:#e2e8f0;">' + str(len(df_f)) + '</strong> / ' + str(len(df_res)) + ' หุ้น</span>'
        '<span>Buy:' + str(buy_n) + ' Watch:' + str(watch_n) + ' Sell:' + str(sell_n) + ' avg ' + "{:.0f}pt".format(avg_sc) + '</span>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="sec-title">3 ผลการสแกน</div>', unsafe_allow_html=True)
    if len(df_f) == 0:
        st.info("ไม่มีหุ้นผ่านเงื่อนไข ลองปรับ Parameters")
        return
    for _, row in df_f.iterrows():
        chg_cls  = "cup" if row["Change"] >= 0 else "cdn"
        chip_cls = "chip-" + row["SigCls"]
        scls     = "sh" if row["Score"]>=65 else "sm" if row["Score"]>=45 else "sl"
        chg_sym  = "+" if row["Change"] >= 0 else ""
        rsi_c    = "bull" if row["RSI"]<p["rsi_os"] else "bear" if row["RSI"]>p["rsi_ob"] else ""
        bb_c     = "bull" if row["BB"]<0.2 else "bear" if row["BB"]>0.8 else ""
        vr_c     = "bull" if row["VR"]>1.5 else ""
        price_s  = cur + "{:,.2f}".format(row["Price"])
        entry_s  = cur + "{:,.2f}".format(row["Entry"])
        t1_s     = cur + "{:,.2f}".format(row["T1"])
        t2_s     = cur + "{:,.2f}".format(row["T2"])
        sl_s     = cur + "{:,.2f}".format(row["SL"])
        chg_s    = chg_sym + "{:.2f}%".format(row["Change"])
        rr_s     = "1:" + "{:.2f}".format(row["RR"])
        score_s  = str(int(row["Score"]))
        st.markdown(
            '<div class="stock-card ' + row["SigCls"] + '">'
            '<div class="sc-top">'
            '<div><div class="sc-sym">' + row["Symbol"] + '</div><div class="sc-name">' + row["Name"] + '</div></div>'
            '<div><div class="sc-price">' + price_s + '</div><div class="sc-chg ' + chg_cls + '">' + chg_s + '</div></div>'
            '</div>'
            '<div class="sc-bars">'
            '<div class="sbi"><div class="sbl">RSI</div><div class="sbv ' + rsi_c + '">' + "{:.0f}".format(row["RSI"]) + '</div></div>'
            '<div class="sbi"><div class="sbl">ADX</div><div class="sbv">' + "{:.0f}".format(row["ADX"]) + '</div></div>'
            '<div class="sbi"><div class="sbl">BB%</div><div class="sbv ' + bb_c + '">' + "{:.2f}".format(row["BB"]) + '</div></div>'
            '<div class="sbi"><div class="sbl">Vol</div><div class="sbv ' + vr_c + '">' + "{:.1f}x".format(row["VR"]) + '</div></div>'
            '</div>'
            '<div class="trow">'
            '<div class="tgt"><div class="tl">ซื้อ</div><div class="tv te">' + entry_s + '</div></div>'
            '<div class="tgt"><div class="tl">เป้า 1</div><div class="tv t1">' + t1_s + '</div></div>'
            '<div class="tgt"><div class="tl">เป้า 2</div><div class="tv t2">' + t2_s + '</div></div>'
            '<div class="tgt"><div class="tl">SL</div><div class="tv ts">' + sl_s + '</div></div>'
            '</div>'
            '<div class="sc-bot">'
            '<div><span class="chip ' + chip_cls + '">' + row["Signal"] + '</span>'
            ' <span style="font-size:.7rem;color:#8892b0;">R/R <span style="color:#6c63ff;font-weight:700;">' + rr_s + '</span></span></div>'
            '<div class="sring ' + scls + '">' + score_s + '</div>'
            '</div></div>',
            unsafe_allow_html=True
        )
        if st.button("วิเคราะห์ " + row["Symbol"] + " เจาะลึก", key="da_"+row["Symbol"]+"_"+mkt_key, use_container_width=True):
            st.session_state.detail_sym = row["Symbol"]
            st.session_state.detail_mkt = mkt_key
            st.session_state.view = "detail"
            st.rerun()

def view_manual():
    render_header()
    if st.button("กลับหน้าสแกน"):
        st.session_state.view = "scan"; st.rerun()
    st.markdown('<div class="sec-title">วิเคราะห์หุ้นรายตัว</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">พิมพ์ชื่อย่อหุ้น (Ticker) แล้วเลือกตลาด<br>TH: ADVANC, KBANK, PTT | US: AAPL, NVDA | CN: BABA, NIO</div>', unsafe_allow_html=True)
    with st.form("manual_form"):
        sym_input = st.text_input("ชื่อหุ้น (Ticker)", placeholder="เช่น ADVANC, AAPL, BABA", max_chars=10)
        mkt_sel   = st.selectbox("ตลาด", ["SET - ไทย","US - สหรัฐ","CN - จีน"])
        submitted = st.form_submit_button("วิเคราะห์เจาะลึก", use_container_width=True)
    if submitted and sym_input.strip():
        sym = sym_input.strip().upper()
        mkt_map = {"SET - ไทย":"SET","US - สหรัฐ":"US","CN - จีน":"CN"}
        mkt_key = mkt_map[mkt_sel]
        p = get_params()
        with st.spinner("กำลังดึงข้อมูล " + sym + "..."):
            try:
                df, info = get_data(sym, mkt_key)
                I = compute_indicators(df, p); S = score_stock(I, p)
                yf_inf = info.get("yf") if info.get("source") == "yfinance" else None
                render_params()
                render_deep(sym, mkt_key, I, S, info, yf_info=yf_inf)
            except Exception as e:
                st.markdown('<div class="err-box">ดึงข้อมูลไม่ได้: ' + str(e) + '</div>', unsafe_allow_html=True)
    else:
        render_params()

def view_detail():
    render_header()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("กลับรายการหุ้น", use_container_width=True):
            st.session_state.view = "scan"; st.rerun()
    with c2:
        if st.button("วิเคราะห์หุ้นอื่น", use_container_width=True):
            st.session_state.view = "manual"; st.rerun()
    sym = st.session_state.detail_sym; mkt_key = st.session_state.detail_mkt
    p = get_params()
    cached = st.session_state.scan_results.get(mkt_key)
    if cached is not None and sym in cached["Symbol"].values:
        row = cached[cached["Symbol"]==sym].iloc[0]
        I = row["_I"]; S = row["_S"]; info = row.get("_info", {"source":"mock"})
        yf_inf = None
        if YF_OK and mkt_key != "SET":
            try:
                _, yf_inf = fetch_yfinance(sym)
            except Exception:
                pass
    else:
        with st.spinner("กำลังดึงข้อมูล " + sym + "..."):
            df, info = get_data(sym, mkt_key)
            I = compute_indicators(df, p); S = score_stock(I, p)
            yf_inf = info.get("yf")
    render_params()
    render_deep(sym, mkt_key, I, S, info, yf_info=yf_inf)

# ---------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------
view = st.session_state.view
if view == "login":
    view_login()
elif view == "scan":
    view_scan()
elif view == "manual":
    view_manual()
elif view == "detail":
    view_detail()

st.markdown(
    '<div style="text-align:center;padding:20px 0 10px;color:#2a2a4a;font-size:.68rem;line-height:1.8;">'
    'ใช้เพื่อการศึกษาเท่านั้น · ไม่ใช่คำแนะนำการลงทุน'
    '</div>',
    unsafe_allow_html=True
)
