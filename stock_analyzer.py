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
# CSS (ใช้โค้ด CSS เดิม)
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
.info-box{background:rgba(108,99,255,.08);border:1px solid rgba(108,99,255,.25);border-radius:10px;padding:12px;margin-bottom:16px;font-size:.78rem;color:#a8b2d8;line-height:1.7}
.warn-box{background:rgba(253,203,110,.08);border:1px solid rgba(253,203,110,.3);border-radius:10px;padding:10px 12px;margin-bottom:14px;font-size:.75rem;color:#fdcb6e;line-height:1.6}
.err-box{background:rgba(214,48,49,.1);border:1px solid rgba(214,48,49,.4);border-radius:10px;padding:12px;font-size:.82rem;color:#ff7675;line-height:1.6}
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
    ("logged_in", False), 
    ("investor", None),
    ("market_api", None), 
    ("realtime_api", None),
    ("market", None), 
    ("scan_results", {}), 
    ("view", "login"),
    ("detail_sym", None), 
    ("detail_mkt", None),
    ("prefill_id", ""), 
    ("prefill_secret", ""),
    ("prefill_code", "SANDBOX"), 
    ("prefill_broker", "SANDBOX"),
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
            I["adx"] = _safe(adx_df[ac[0]]); I["dip"] = _safe(adxdf[ac[1]]); I["dim"] = _safe(adx_df[ac[2]])
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
    try:
        if st.session_state.market_api:
            raw = st.session_state.market_api.get_candlestick(
                symbol, 
                interval="1d", 
                limit=limit
            )
            
            if isinstance(raw, dict) and 'data' in raw:
                df = pd.DataFrame(raw['data'])
            else:
                df = pd.DataFrame(raw)
                
            rename = {
                "last":"close","c":"close","o":"open","h":"high",
                "l":"low","v":"volume","vol":"volume","close":"close"
            }
            df.rename(columns={col: rename.get(col, col) for col in df.columns}, inplace=True)
            
            required_cols = ["open", "high", "low", "close", "volume"]
            for col in required_cols:
                if col not in df.columns:
                    for alt in [col.upper(), col.capitalize()]:
                        if alt in df.columns:
                            df[col] = df[alt]
                            break
                    if col not in df.columns:
                        if col == "close" and "last" in df.columns:
                            df["close"] = df["last"]
                        elif col == "volume":
                            df["volume"] = 1000000
                        else:
                            df[col] = df["close"] if "close" in df.columns else 100
            
            df = df[["open","high","low","close","volume"]].apply(
                pd.to_numeric, errors="coerce"
            ).dropna()
            
            if len(df) < 30:
                raise ValueError("ข้อมูลน้อยเกิน去")
                
            return df
            
    except Exception as e:
        print(f"Error fetching from settrade: {e}")
        raise

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
    
    if use_live and st.session_state.market_api:
        try:
            df = fetch_settrade(symbol)
            
            try:
                if st.session_state.realtime_api:
                    q = st.session_state.realtime_api.get_quote(symbol)
                    if q and 'last' in q:
                        df.iloc[-1, df.columns.get_loc("close")] = float(q["last"])
            except Exception:
                pass
                
            info["source"] = "settrade"
            return df, info
            
        except Exception as e:
            info["err"] = str(e)
            # Fallback to yfinance or mock
            st.warning(f"ไม่สามารถดึงข้อมูลจาก Settrade: {e} กำลังใช้ Yahoo Finance แทน")
    
    # ใช้ yfinance เป็น fallback
    yf_sym = symbol + ".BK" if mkt_key == "SET" else symbol
    if YF_OK:
        try:
            df, yf_info = fetch_yfinance(yf_sym)
            info["source"] = "yfinance"
            info["yf"] = yf_info
            return df, info
        except Exception as e:
            info["err"] = str(e)
            st.warning(f"ไม่สามารถดึงข้อมูลจาก Yahoo Finance: {e} กำลังใช้ Mock Data แทน")
    
    # Fallback to mock data
    df = fetch_mock(symbol)
    info["source"] = "mock"
    return df, info

# ---------------------------------------------------------------
# DEFAULT PARAMS
# ---------------------------------------------------------------
DEF = dict(
    sma_s=20, sma_m=50, sma_l=200, ema_f=12, ema_s=26,
    rsi_p=14, rsi_ob=70, rsi_os=30,
    macd_f=12, macd_s=26, macd_sg=9,
    bb_p=20, bb_k=2, stoch_k=14, stoch_d=3,
    atr_p=14, cci_p=20, wr_p=14, mfi_p=14, adx_p=14,
    min_score=60, min_rr=1.5, min_adx=18,
)

def get_params():
    return {k: st.session_state.get("p_"+k, v) for k, v in DEF.items()}

# ---------------------------------------------------------------
# SHARED UI
# ---------------------------------------------------------------
def render_header():
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
    with st.expander("ตั้งค่า Parameters", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.slider("SMA สั้น", 5, 50, DEF["sma_s"], key="p_sma_s")
            st.slider("SMA กลาง", 20, 100, DEF["sma_m"], key="p_sma_m")
            st.slider("SMA ยาว", 100, 300, DEF["sma_l"], key="p_sma_l")
            st.slider("RSI Period", 7, 21, DEF["rsi_p"], key="p_rsi_p")
            st.slider("RSI Overbought", 60, 85, DEF["rsi_ob"], key="p_rsi_ob")
            st.slider("RSI Oversold", 15, 40, DEF["rsi_os"], key="p_rsi_os")
            st.slider("MACD Fast", 8, 20, DEF["macd_f"], key="p_macd_f")
            st.slider("MACD Slow", 20, 40, DEF["macd_s"], key="p_macd_s")
            st.slider("MACD Signal", 5, 15, DEF["macd_sg"], key="p_macd_sg")
        with c2:
            st.slider("BB Period", 10, 30, DEF["bb_p"], key="p_bb_p")
            st.slider("BB Std Dev", 1, 3, DEF["bb_k"], key="p_bb_k")
            st.slider("Stoch %K", 5, 21, DEF["stoch_k"], key="p_stoch_k")
            st.slider("Stoch %D", 2, 7, DEF["stoch_d"], key="p_stoch_d")
            st.slider("ATR Period", 7, 21, DEF["atr_p"], key="p_atr_p")
            st.slider("CCI Period", 10, 30, DEF["cci_p"], key="p_cci_p")
            st.slider("Williams %R", 7, 21, DEF["wr_p"], key="p_wr_p")
            st.slider("MFI Period", 7, 21, DEF["mfi_p"], key="p_mfi_p")
            st.slider("ADX Period", 7, 21, DEF["adx_p"], key="p_adx_p")
        c3, c4 = st.columns(2)
        with c3:
            st.slider("คะแนนขั้นต่ำ", 0, 100, DEF["min_score"], key="p_min_score")
        with c4:
            st.slider("R/R ขั้นต่ำ", 0.5, 5.0, float(DEF["min_rr"]), step=0.5, key="p_min_rr")

def render_deep(sym, mkt_key, I, S, info, yf_info=None):
    # ... (โค้ดเดิมของ render_deep)
    pass

# ---------------------------------------------------------------
# ฟังก์ชันทดสอบการเชื่อมต่อ (แก้ไขใหม่)
# ---------------------------------------------------------------
def test_settrade_connection(app_id, app_secret, app_code, broker_id):
    """ทดสอบการเชื่อมต่อกับ Settrade API"""
    try:
        inv = Investor(
            app_id=app_id,
            app_secret=app_secret,
            app_code=app_code if app_code else None,
            broker_id=broker_id if broker_id else None
        )
        
        # ทดสอบการเชื่อมต่อด้วยการดึงข้อมูลหุ้นตัวอย่าง
        market_api = inv.MarketData()
        test_data = market_api.get_candlestick("PTT", interval="1d", limit=5)
        
        if test_data:
            return True, "เชื่อมต่อสำเร็จ", inv
        else:
            return False, "ไม่สามารถดึงข้อมูลจาก API ได้", None
            
    except Exception as e:
        return False, f"ข้อผิดพลาด: {str(e)}", None

# ---------------------------------------------------------------
# VIEWS (แก้ไข view_login)
# ---------------------------------------------------------------
def view_login():
    render_header()
    ta_ok  = "OK" if TA_OK  else "ยังไม่ติดตั้ง"
    st_ok  = "OK" if ST_OK  else "ยังไม่ติดตั้ง"
    yf_ok  = "OK" if YF_OK  else "ยัง不ติดตั้ง"
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
    
    st.markdown('<div class="login-card"><h2>เชื่อมต่อ Settrade API</h2><div class="login-sub">กรอก credential จาก developer.settrade.com</div></div>', unsafe_allow_html=True)
    
    # แสดงคำแนะนำการกรอกข้อมูล
    st.markdown("""
    <div class="info-box">
    <strong>คำแนะนำการกรอก:</strong><br>
    • APP_ID และ APP_SECRET: มาจาก developer.settrade.com<br>
    • APP_CODE: ป้อน "SANDBOX" สำหรับบัญชีทดสอบ<br>
    • BROKER_ID: ป้อน "SANDBOX" สำหรับบัญชีทดสอบ
    </div>
    """, unsafe_allow_html=True)
    
    # ปุ่มล้างค่าที่กรอก
    if st.button("ล้างค่าที่กรอก", use_container_width=False):
        st.session_state.prefill_id = ""
        st.session_state.prefill_secret = ""
        st.session_state.prefill_code = "SANDBOX"
        st.session_state.prefill_broker = "SANDBOX"
        st.rerun()
    
    with st.form("login_form"):
        app_id = st.text_input("APP_ID", value=st.session_state.prefill_id, placeholder="เช่น MPRZz1Hymo6nR50A")
        app_secret = st.text_input("APP_SECRET", value=st.session_state.prefill_secret, type="password", placeholder="เช่น Te/3LKXBb+IM20T/ygcFAMWXjIgkadJ+o1cDstkjRDQ=")
        app_code = st.text_input("APP_CODE", value=st.session_state.prefill_code, placeholder="ป้อน SANDBOX สำหรับทดสอบ")
        broker_id = st.text_input("BROKER_ID", value=st.session_state.prefill_broker, placeholder="ป้อน SANDBOX สำหรับทดสอบ")
        submitted = st.form_submit_button("เชื่อมต่อ Settrade", use_container_width=True)
    
    if submitted:
        if not ST_OK:
            st.markdown('<div class="err-box">settrade_v2 ไม่ได้ติดตั้ง: pip install settrade-v2</div>', unsafe_allow_html=True)
        elif not app_id.strip() or not app_secret.strip():
            st.markdown('<div class="err-box">กรุณากรอก APP_ID และ APP_SECRET</div>', unsafe_allow_html=True)
        else:
            with st.spinner("กำลังเชื่อมต่อ..."):
                success, message, inv = test_settrade_connection(
                    app_id.strip(), 
                    app_secret.strip(),
                    app_code.strip(),
                    broker_id.strip()
                )
                
                if success:
                    st.session_state.logged_in = True
                    st.session_state.investor = inv
                    st.session_state.market_api = inv.MarketData()
                    st.session_state.realtime_api = inv.RealtimeData()
                    st.session_state.view = "scan"
                    st.rerun()
                else:
                    st.markdown(f'<div class="err-box">{message}</div>', unsafe_allow_html=True)
                    st.info("คุณยังสามารถใช้ Yahoo Finance หรือ Mock Data ได้โดยกดปุ่มด้านล่าง")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("ใช้ Mock Data", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.view = "scan"
            st.rerun()
    with c2:
        if st.button("ใช้ Yahoo Finance", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.view = "scan"
            st.rerun()

def view_scan():
    render_header()
    render_params()
    p = get_params()
    col_n1, col_n2 = st.columns([3, 1])
    with col_n2:
        if st.button("วิเคราะห์หุ้น", use_container_width=True):
            st.session_state.view = "manual"
            st.rerun()
    
    st.markdown('<div class="sec-title">1 เลือกตลาดหุ้น</div>', unsafe_allow_html=True)
    mkt_cols = st.columns(3)
    mkt_labels = {"SET":"TH SET\nSET50/100/mai", "US":"US Tech\nNASDAQ/NYSE", "CN":"CN Tech\nNYSE ADR"}
    for i, mkt_key in enumerate(["SET","US","CN"]):
        with mkt_cols[i]:
            is_sel = st.session_state.market == mkt_key
            if st.button(mkt_labels[mkt_key], key="mkt_"+mkt_key, use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                st.session_state.market = mkt_key
                st.rerun()
    
    mkt_key = st.session_state.market
    if not mkt_key:
        st.markdown('<div style="text-align:center;padding:32px;color:#636e72;">เลือกตลาดก่อน</div>', unsafe_allow_html=True)
        return
    
    mkt = MARKETS[mkt_key]
    cur = mkt["currency"]
    n = len(mkt["stocks"])
    
    # กำหนดแหล่งข้อมูล
    if st.session_state.logged_in and mkt_key == "SET":
        src_lbl = "Settrade Live"
    elif YF_OK:
        src_lbl = "Yahoo Finance"
    else:
        src_lbl = "Mock Data"
    
    st.markdown(
        f'<div style="background:#12122a;border:1px solid rgba(108,99,255,.3);border-radius:10px;padding:10px 14px;margin:8px 0 14px;display:flex;justify-content:space-between;align-items:center;">'
        f'<span style="color:#e2e8f0;font-size:.85rem;"><strong>{mkt["name"]}</strong> · {n} หุ้น · {cur}</span>'
        f'<span style="font-size:.68rem;color:#8892b0;">{src_lbl}</span></div>',
        unsafe_allow_html=True
    )
    
    c1, c2 = st.columns(2)
    with c1:
        filt_sig = st.multiselect("สัญญาณ", ["🟢 ซื้อ","🟡 เฝ้าระวัง","⚪ ถือ","🔴 ขาย"],
            default=["🟢 ซื้อ","🟡 เฝ้าระวัง"], key="filt_sig", label_visibility="collapsed", placeholder="เลือกสัญญาณ")
    with c2:
        sort_by = st.selectbox("เรียง", ["Score","RSI","Change","ADX"], key="sort_by", label_visibility="collapsed")
    
    st.markdown('<div class="sec-title">2 สแกน</div>', unsafe_allow_html=True)
    
    if st.button(f"สแกน {mkt['flag']} {mkt_key} ({n} หุ้น)", use_container_width=True):
        results = []
        prog = st.progress(0)
        stxt = st.empty()
        
        for i, (sym, name) in enumerate(mkt["stocks"]):
            stxt.markdown(f'<div style="text-align:center;font-size:.75rem;color:#8892b0;">สแกน {sym} ({i+1}/{n})</div>', unsafe_allow_html=True)
            try:
                df, info = get_data(sym, mkt_key)
                I = compute_indicators(df, p)
                S = score_stock(I, p)
                results.append(dict(Symbol=sym, Name=name, Market=mkt_key,
                    Price=round(I["price"],2), Change=round(I["chg"],2),
                    RSI=round(I["rsi"],1), ADX=round(I["adx"],1),
                    BB=round(I["bbp"],2), VR=round(I["vol_r"],2),
                    Score=S["sc"], Signal=S["rec"], SigCls=S["cls"],
                    Entry=S["entry"], T1=S["t1"], T2=S["t2"], SL=S["sl"], RR=S["rr"],
                    _I=I, _S=S, _info=info))
            except Exception as e:
                st.warning(f"ไม่สามารถวิเคราะห์ {sym}: {e}")
            
            prog.progress((i+1)/n)
        
        prog.empty()
        stxt.empty()
        st.session_state.scan_results[mkt_key] = pd.DataFrame(results)
    
    df_res = st.session_state.scan_results.get(mkt_key)
    if df_res is None or len(df_res) == 0:
        st.info("กดปุ่ม 'สแกน' เพื่อเริ่มการวิเคราะห์หุ้น")
        return
    
    # ... (โค้ดส่วนแสดงผลต่อไป)

# ... (โค้ด view_manual, view_detail และส่วนอื่นๆ ตามเดิม)

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
