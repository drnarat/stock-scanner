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
    import yfinance as y极f
    YF_OK = True
except ImportError:
    YF_OK = False

# ... (โค้ด CSS และส่วนอื่นๆ เหมือนเดิม)

# ---------------------------------------------------------------
# ฟังก์ชันทดสอบการเชื่อมต่อ (แก้ไขใหม่)
# ---------------------------------------------------------------
def test_settrade_connection(app_id, app_secret, app_code, broker_id):
    """ทดสอบการเชื่อมต่อกับ Settrade API"""
    try:
        inv = Investor(
            app_id=app_id,
            app_secret=app_secret,
            app极_code=app_code if app_code else None,
            broker_id=broker_id if broker_id else None
        )
        
        # ทดสอบการเชื่อมต่อด้วยการดึงข้อมูลหุ้นตัวอย่าง
        market_api = inv.market
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
        '<极div style="font-size:.82rem;">'
        'settrade-v2: <strong style="color:#e2e8f0;">' + st_ok + '</strong> &nbsp;|&nbsp; '
        'pandas_ta: <strong style="color:#e2e8f0;">' + ta_ok + '</strong> &nbsp;|&nbsp; '
        'yfinance: <strong style="color:#e2e8f0;">' + yf_ok + '</strong>'
        '</div>'
        + ('<div style="margin-top:8px;font-size:.75rem;color:#fdcb6e;">ติดตั้ง: ' + lib_warn + '</div>' if lib_warn else '')
        + '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="login-card"><h极2>เชื่อมต่อ Settrade API</h2><div class="login-sub">กรอก credential จาก developer.settrade.com</div></div>', unsafe_allow_html=True)
    
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
            st.markdown('<div class="err-box">settrade_v2 ไม่ได้ติดตั้ง: pip install settrade极-v2</div>', unsafe_allow_html=True)
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
                    st.session_state.market_api = inv.market  # ใช้ inv.market แทน
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

# ---------------------------------------------------------------
# DATA FETCH (แก้ไขฟังก์ชัน get_data)
# ---------------------------------------------------------------
def get_data(symbol, mkt_key):
    info = {}
    use_live = st.session_state.logged_in and mkt_key == "SET"
    
    if use_live and st.session_state.market_api:
        try:
            df = fetch_settrade(symbol)
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
# SESSION STATE (ลบ realtime_api)
# ---------------------------------------------------------------
for k, v in [
    ("logged_in", False), 
    ("investor", None),
    ("market_api", None), 
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
