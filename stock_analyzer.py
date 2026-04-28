# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import time
import requests
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
# CSS (คงเดิมไว้ทั้งหมดตามต้นฉบับ)
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
.chip-buy{background:rgba(0,184,148,.15);color:#00b894;border:1px solid rgba(0,184,
