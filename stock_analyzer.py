# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import platform
import urllib.request
import urllib.parse
import json
import ssl
import re

# --- ปรับแต่งการนำเข้า Library ---
try: import pandas_ta as ta; TA_OK = True
except: TA_OK = False
try: from settrade_v2 import Investor; from settrade_v2.errors import SettradeError; ST_OK = True
except: ST_OK = False
try: import yfinance as yf; YF_OK = True
except: YF_OK = False
try: import plotly.graph_objects as go; from plotly.subplots import make_subplots; PLOTLY_OK = True
except: PLOTLY_OK = False

# ==========================================
# 2. ตั้งค่าหน้าเว็บและ CSS (เหมือนเดิม)
# ==========================================
st.set_page_config(page_title="Stock Scanner Pro AI", layout="centered")

# ==========================================
# 8. ระบบค้นหาข่าวย้อนหลัง 1 เดือน (New Update! 🚀)
# ==========================================
def _http_get(url):
    real_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    req = urllib.request.Request(url, headers={"User-Agent": real_ua})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

def search_stock_news_one_month(symbol, company_name, market="SET"):
    results = []
    # ใช้ "when:1m" เพื่อดึงข่าวย้อนหลัง 1 เดือนจาก Google News
    if market == "SET":
        query = f"หุ้น {symbol} {company_name} when:1m"
    else:
        query = f"{symbol} stock news when:1m"

    try:
        rss_url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(query) + "&hl=th&gl=TH&ceid=TH:th"
        raw = _http_get(rss_url)
        items = re.findall(r'<item>(.*?)</item>', raw, re.DOTALL)
        
        for item in items[:10]: # เอา 10 ข่าวเด่น
            title_m = re.search(r'<title>(.*?)</title>', item)
            src_m = re.search(r'<source[^>]*>(.*?)</source>', item)
            if title_m:
                results.append({
                    "title": title_m.group(1).replace("<![CDATA[", "").replace("]]>", ""),
                    "source": src_m.group(1) if src_m else "News"
                })
    except: pass
    return results

# ==========================================
# 9. ฟังก์ชันเรียก AI วิเคราะห์ (Fix Session State Bug)
# ==========================================
def call_gemini_api(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        data = json.loads(r.read().decode())
    return data["candidates"][0]["content"]["parts"][0]["text"]

# --- แก้ไขส่วนหน้าจอ AI Tab เพื่อป้องกัน Error ---
def render_ai_tab(sym, company_name, mkt_key, I, S):
    st.markdown("### 🤖 AI Insight (วิเคราะห์ข่าว + เทคนิค)")
    
    # ดึงค่า Key จาก session_state หลัก
    api_key = st.text_input("ใส่ Gemini API Key", type="password", value=st.session_state.get("aikey_gemini", ""))

    if st.button(f"🚀 เริ่มวิเคราะห์หุ้น {sym} ย้อนหลัง 1 เดือน"):
        if not api_key:
            st.error("กรุณาใส่ API Key ก่อนครับ")
        else:
            st.session_state["aikey_gemini"] = api_key # บันทึกไว้ใช้ครั้งหน้า
            
            with st.spinner("🌐 กำลังรวบรวมข่าวย้อนหลัง 1 เดือน..."):
                news = search_stock_news_one_month(sym, company_name, mkt_key)
                news_text = "\n".join([f"- {n['title']} (ที่มา: {n['source']})" for n in news])
                
            with st.spinner("🧠 AI กำลังประมวลผลข้อมูล..."):
                prompt = f"""วิเคราะห์หุ้น {sym} ({company_name})
                ข้อมูลราคา: {I['price']} RSI: {I['rsi']:.1f} สัญญาณ: {S['rec']}
                
                ข่าวเด่นในรอบ 1 เดือนที่ผ่านมา:
                {news_text if news else "ไม่พบข่าวเด่น"}
                
                ช่วยสรุปว่า:
                1. ข่าวในรอบเดือนส่งผลบวกหรือลบ?
                2. กราฟเทคนิคตอนนี้ได้เปรียบไหม?
                3. คำแนะนำจุดเข้าและจุดขายที่เหมาะสม
                (ตอบเป็นภาษาไทยแบบมืออาชีพ)"""
                
                try:
                    result = call_gemini_api(prompt, api_key)
                    st.success("วิเคราะห์เสร็จสิ้น!")
                    st.markdown(result)
                    if news:
                        with st.expander("ดูรายการข่าวที่ AI นำมาวิเคราะห์"):
                            for n in news: st.write(f"📰 {n['title']}")
                except Exception as e:
                    st.error(f"AI Error: {e}")

# (หมายเหตุ: ส่วนอื่นๆ ของโค้ดเช่น การดึงข้อมูลเทรด หรือหน้า Login ให้คงไว้ตามเดิมครับ)
