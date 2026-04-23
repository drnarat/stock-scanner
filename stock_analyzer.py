import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta

# ============================================================
# หมายเหตุ: ในการใช้งานจริง ให้ uncomment ส่วนนี้
# from settrade_v2 import Investor
# ============================================================

# ============================================================
# 1. CONFIGURATION
# ============================================================
APP_ID = "MPRZz1Hymo6nR50A"
APP_SECRET = "Te/3LKXBb+IM20T/ygcFAMWXjIgkadJ+o1cDstkjRDQ="
APP_CODE = "SANDBOX"
BROKER_ID = "SANDBOX"

st.set_page_config(
    page_title="🚀 AI Stock Scanner Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. CUSTOM CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    padding: 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(48, 43, 99, 0.4);
}

.main-header h1 {
    color: #fff;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: -0.5px;
}

.main-header p {
    color: #a8b2d8;
    margin: 0.5rem 0 0 0;
    font-size: 0.95rem;
}

.signal-buy {
    background: linear-gradient(135deg, #0f9b58, #00b894);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.8rem;
    display: inline-block;
}

.signal-sell {
    background: linear-gradient(135deg, #d63031, #e17055);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.8rem;
    display: inline-block;
}

.signal-neutral {
    background: linear-gradient(135deg, #636e72, #b2bec3);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.8rem;
    display: inline-block;
}

.signal-watch {
    background: linear-gradient(135deg, #e17055, #fdcb6e);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.8rem;
    display: inline-block;
}

.metric-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    color: white;
}

.metric-card .value {
    font-size: 1.6rem;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
}

.metric-card .label {
    font-size: 0.8rem;
    color: #a8b2d8;
    margin-top: 4px;
}

.score-badge {
    display: inline-block;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    line-height: 50px;
    text-align: center;
    font-weight: 700;
    font-size: 1rem;
    font-family: 'Space Grotesk', sans-serif;
}

.score-high { background: #00b894; color: white; }
.score-med  { background: #fdcb6e; color: #2d3436; }
.score-low  { background: #d63031; color: white; }

.indicator-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

.status-dot-green { color: #00b894; }
.status-dot-red   { color: #d63031; }
.status-dot-yellow{ color: #fdcb6e; }

.stDataFrame table {
    font-size: 0.85rem;
}

div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
}

div[data-testid="stSidebar"] label,
div[data-testid="stSidebar"] .stSelectbox label,
div[data-testid="stSidebar"] h1,
div[data-testid="stSidebar"] h2,
div[data-testid="stSidebar"] h3,
div[data-testid="stSidebar"] p,
div[data-testid="stSidebar"] span {
    color: #e2e8f0 !important;
}

.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #a8b2d8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1rem 0 0.5rem 0;
    padding-bottom: 0.3rem;
    border-bottom: 2px solid rgba(168, 178, 216, 0.2);
}

.analysis-box {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-left: 4px solid #6c63ff;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    color: #e2e8f0;
    font-size: 0.9rem;
    line-height: 1.7;
}

.buy-reason { border-left-color: #00b894; }
.sell-reason { border-left-color: #d63031; }
.neutral-reason { border-left-color: #636e72; }

.target-box {
    background: rgba(108, 99, 255, 0.1);
    border: 1px solid rgba(108, 99, 255, 0.3);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    text-align: center;
    color: #e2e8f0;
}

.target-box .target-label {
    font-size: 0.75rem;
    color: #a8b2d8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.target-box .target-value {
    font-size: 1.2rem;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    color: #6c63ff;
    margin-top: 4px;
}

.stButton > button {
    background: linear-gradient(135deg, #6c63ff, #302b63);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: 0.5px;
    transition: all 0.2s;
    box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #7d75ff, #4a3f99);
    box-shadow: 0 6px 20px rgba(108, 99, 255, 0.5);
    transform: translateY(-1px);
}

.update-time {
    font-size: 0.75rem;
    color: #636e72;
    text-align: right;
    margin-top: 0.5rem;
}

.thailand-flag { font-size: 1.2rem; }
.usa-flag { font-size: 1.2rem; }
.china-flag { font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. SETTRADE API CONNECTION (MOCK MODE สำหรับ demo)
# ============================================================
USE_MOCK = True  # เปลี่ยนเป็น False เมื่อต้องการใช้ Settrade จริง

@st.cache_resource
def init_settrade():
    if USE_MOCK:
        return None, None
    investor = Investor(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        app_code=APP_CODE,
        broker_id=BROKER_ID
    )
    return investor.Market(), investor.Realtime()

# ============================================================
# 4. THAI STOCK UNIVERSE (ตลาดหลักทรัพย์ไทยทั้งหมด - ตัวอย่าง SET100)
# ============================================================
THAI_STOCKS = [
    # ธนาคาร
    ("KBANK", "กสิกรไทย"), ("BBL", "กรุงเทพ"), ("SCB", "ไทยพาณิชย์"),
    ("KTB", "กรุงไทย"), ("TMB", "ทหารไทย"), ("BAY", "กรุงศรี"),
    ("TISCO", "ทิสโก้"), ("KKP", "เกียรตินาคินภัทร"),
    # พลังงาน
    ("PTT", "ปตท."), ("PTTEP", "ปตท.สผ."), ("GULF", "กัลฟ์"), 
    ("GPSC", "โกลบอลเพาเวอร์"), ("RATCH", "ราช กรุ๊ป"), ("BGRIM", "บี.กริม"),
    ("EGCO", "เอ็กโก"), ("CKP", "ซีเค เพาเวอร์"),
    # สื่อสาร / เทคโนโลยี
    ("ADVANC", "แอดวานซ์"), ("TRUE", "ทรู"), ("DTAC", "ดีแทค"), ("INSET", "อินเซ็ท"),
    ("BE8", "บี8"), ("MFEC", "MFEC"), ("INET", "อินเทอร์เน็ต"),
    # ค้าปลีก / อุปโภคบริโภค
    ("CPALL", "ซีพีออลล์"), ("CRC", "เซ็นทรัล รีเทล"), ("HMPRO", "โฮมโปร"),
    ("MAKRO", "แม็คโคร"), ("BJC", "บีเจซี"), ("DOHOME", "โดโฮม"),
    # อาหาร / เกษตร
    ("CPF", "ซีพีเอฟ"), ("TU", "ไทยยูเนี่ยน"), ("GFPT", "จีเอฟพีที"),
    ("NRF", "NRF"), ("BTG", "บีทาเก้น"),
    # อสังหาริมทรัพย์
    ("LH", "แลนด์แอนด์เฮาส์"), ("AP", "เอพี"), ("SIRI", "แสนสิริ"),
    ("QH", "ควอลิตี้เฮ้าส์"), ("SC", "เอสซี แอสเสท"),
    # การบิน / การท่องเที่ยว
    ("AOT", "ท่าอากาศยาน"), ("AAV", "เอเชีย เอวิเอชั่น"), ("CENTEL", "เซ็นทารา"),
    ("MINT", "ไมเนอร์"), ("ERW", "อีอาร์ดับบิ้ว"),
    # สุขภาพ
    ("BDMS", "กรุงเทพดุสิต"), ("BGH", "กรุงเทพ"), ("BCH", "บางกอก"),
    ("BH", "กรุงเทพ เชน"), ("VIBHA", "วิภาวดี"),
    # วัสดุก่อสร้าง / อุตสาหกรรม
    ("SCC", "ปูนซิเมนต์ไทย"), ("SCCC", "ปูนซีเมนต์นครหลวง"),
    ("TPIPP", "ทีพีไอ"), ("IRPC", "IRPC"), ("PTTGC", "พีทีที โกลบอล"),
    # การเงิน
    ("MTC", "เมืองไทย แคปปิตอล"), ("TIDLOR", "ไทยเดินทาง"),
    ("SAWAD", "ศาวะดี"), ("AEONTS", "อิออน"), ("ASK", "เอเซียร์"),
]

INTL_TECH_STOCKS = [
    # สหรัฐอเมริกา
    ("AAPL", "Apple Inc.", "US"),
    ("MSFT", "Microsoft Corp.", "US"),
    ("NVDA", "NVIDIA Corp.", "US"),
    ("GOOGL", "Alphabet Inc.", "US"),
    ("META", "Meta Platforms", "US"),
    ("AMZN", "Amazon.com", "US"),
    ("TSLA", "Tesla Inc.", "US"),
    ("AMD", "Advanced Micro Devices", "US"),
    ("INTC", "Intel Corp.", "US"),
    ("AVGO", "Broadcom Inc.", "US"),
    ("QCOM", "Qualcomm", "US"),
    ("MU", "Micron Technology", "US"),
    ("AMAT", "Applied Materials", "US"),
    ("LRCX", "Lam Research", "US"),
    ("SNPS", "Synopsys", "US"),
    # จีน
    ("BABA", "Alibaba Group", "CN"),
    ("JD", "JD.com", "CN"),
    ("BIDU", "Baidu Inc.", "CN"),
    ("NTES", "NetEase", "CN"),
    ("PDD", "Pinduoduo", "CN"),
    ("TCOM", "Trip.com", "CN"),
    ("NIO", "NIO Inc.", "CN"),
    ("XPEV", "XPeng Inc.", "CN"),
    ("LI", "Li Auto", "CN"),
    ("BILI", "Bilibili", "CN"),
    ("IQ", "iQIYI", "CN"),
    ("WB", "Weibo Corp.", "CN"),
    ("FUTU", "Futu Holdings", "CN"),
    ("TIGR", "UP Fintech", "CN"),
    ("CAMT", "Camtek", "CN"),
]

# ============================================================
# 5. MOCK DATA GENERATOR (เลียนแบบ Settrade API)
# ============================================================
def generate_mock_candles(symbol, n=100):
    """สร้างข้อมูล OHLCV จำลอง"""
    np.random.seed(hash(symbol) % 10000)
    base = random.uniform(10, 500)
    prices = [base]
    for _ in range(n - 1):
        change = np.random.normal(0, 0.015)
        prices.append(max(prices[-1] * (1 + change), 1))
    
    dates = [(datetime.now() - timedelta(days=n - i)).strftime("%Y-%m-%d") for i in range(n)]
    volumes = [int(np.random.uniform(500000, 5000000)) for _ in range(n)]
    opens = [p * np.random.uniform(0.995, 1.005) for p in prices]
    highs = [max(o, p) * np.random.uniform(1.001, 1.02) for o, p in zip(opens, prices)]
    lows = [min(o, p) * np.random.uniform(0.98, 0.999) for o, p in zip(opens, prices)]
    
    df = pd.DataFrame({
        "date": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "last": prices,
        "volume": volumes
    })
    return df

def get_mock_quote(symbol):
    """สร้าง quote จำลอง"""
    np.random.seed(hash(symbol + str(datetime.now().hour)) % 10000)
    base = random.uniform(10, 500)
    change = np.random.normal(0, 1.5)
    return {
        "symbol": symbol,
        "last": round(base, 2),
        "change": round(change, 2),
        "changePercent": round(change / base * 100, 2),
        "volume": int(np.random.uniform(500000, 8000000)),
        "bid": round(base * 0.999, 2),
        "ask": round(base * 1.001, 2),
        "high": round(base * 1.02, 2),
        "low": round(base * 0.98, 2),
    }

# ============================================================
# 6. TECHNICAL INDICATORS
# ============================================================
def calc_sma(series, period):
    return series.rolling(window=period).mean()

def calc_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def calc_macd(series, fast=12, slow=26, signal=9):
    ema_fast = calc_ema(series, fast)
    ema_slow = calc_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calc_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calc_bbands(series, period=20, std_dev=2):
    mid = calc_sma(series, period)
    std = series.rolling(window=period).std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    pct_b = (series - lower) / (upper - lower + 1e-10)
    return upper, mid, lower, pct_b

def calc_stochastic(high, low, close, k_period=14, d_period=3):
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    d = k.rolling(window=d_period).mean()
    return k, d

def calc_atr(high, low, close, period=14):
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def calc_obv(close, volume):
    direction = np.sign(close.diff())
    direction.iloc[0] = 0
    return (volume * direction).cumsum()

def calc_cci(high, low, close, period=20):
    typical = (high + low + close) / 3
    sma = typical.rolling(window=period).mean()
    mad = typical.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    return (typical - sma) / (0.015 * mad + 1e-10)

def calc_williams_r(high, low, close, period=14):
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    return -100 * (highest_high - close) / (highest_high - lowest_low + 1e-10)

def calc_mfi(high, low, close, volume, period=14):
    typical = (high + low + close) / 3
    money_flow = typical * volume
    positive = money_flow.where(typical > typical.shift(), 0).rolling(period).sum()
    negative = money_flow.where(typical < typical.shift(), 0).rolling(period).sum()
    mfi = 100 - (100 / (1 + positive / (negative + 1e-10)))
    return mfi

def calc_adx(high, low, close, period=14):
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    dm_plus = (high - high.shift()).clip(lower=0)
    dm_minus = (low.shift() - low).clip(lower=0)
    dm_plus = dm_plus.where(dm_plus > dm_minus, 0)
    dm_minus = dm_minus.where(dm_minus > dm_plus, 0)
    atr14 = tr.rolling(period).mean()
    di_plus = 100 * dm_plus.rolling(period).mean() / (atr14 + 1e-10)
    di_minus = 100 * dm_minus.rolling(period).mean() / (atr14 + 1e-10)
    dx = 100 * (di_plus - di_minus).abs() / (di_plus + di_minus + 1e-10)
    adx = dx.rolling(period).mean()
    return adx, di_plus, di_minus

def calc_vwap(high, low, close, volume):
    typical = (high + low + close) / 3
    cumvol = volume.cumsum()
    cumtp = (typical * volume).cumsum()
    return cumtp / (cumvol + 1e-10)

def calc_pivot(high, low, close):
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    return pivot, r1, r2, s1, s2

def compute_all_indicators(df, params):
    """คำนวณ indicator ทุกตัว"""
    close = df["last"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]
    
    ind = {}
    # Trend
    ind["sma20"]  = calc_sma(close, params["sma_short"]).iloc[-1]
    ind["sma50"]  = calc_sma(close, params["sma_mid"]).iloc[-1]
    ind["sma200"] = calc_sma(close, params["sma_long"]).iloc[-1]
    ind["ema12"]  = calc_ema(close, params["ema_fast"]).iloc[-1]
    ind["ema26"]  = calc_ema(close, params["ema_slow"]).iloc[-1]
    
    # Momentum
    ind["rsi"]    = calc_rsi(close, params["rsi_period"]).iloc[-1]
    macd_l, macd_s, macd_h = calc_macd(close, params["macd_fast"], params["macd_slow"], params["macd_signal"])
    ind["macd"]   = macd_l.iloc[-1]
    ind["macd_signal"] = macd_s.iloc[-1]
    ind["macd_hist"]   = macd_h.iloc[-1]
    
    # Volatility
    bbu, bbm, bbl, bbp = calc_bbands(close, params["bb_period"], params["bb_std"])
    ind["bb_upper"] = bbu.iloc[-1]
    ind["bb_mid"]   = bbm.iloc[-1]
    ind["bb_lower"] = bbl.iloc[-1]
    ind["bb_pct"]   = bbp.iloc[-1]
    ind["atr"]      = calc_atr(high, low, close, params["atr_period"]).iloc[-1]
    
    # Stochastic
    stoch_k, stoch_d = calc_stochastic(high, low, close, params["stoch_k"], params["stoch_d"])
    ind["stoch_k"] = stoch_k.iloc[-1]
    ind["stoch_d"] = stoch_d.iloc[-1]
    
    # Volume
    ind["obv"]     = calc_obv(close, volume).iloc[-1]
    ind["mfi"]     = calc_mfi(high, low, close, volume, params["mfi_period"]).iloc[-1]
    ind["vol_avg"] = volume.rolling(20).mean().iloc[-1]
    ind["vol_ratio"] = volume.iloc[-1] / (ind["vol_avg"] + 1)
    
    # Other Oscillators
    ind["cci"]     = calc_cci(high, low, close, params["cci_period"]).iloc[-1]
    ind["williams_r"] = calc_williams_r(high, low, close, params["williams_period"]).iloc[-1]
    
    # Trend Strength
    adx_val, di_plus, di_minus = calc_adx(high, low, close, params["adx_period"])
    ind["adx"]     = adx_val.iloc[-1]
    ind["di_plus"] = di_plus.iloc[-1]
    ind["di_minus"]= di_minus.iloc[-1]
    
    # VWAP
    ind["vwap"]    = calc_vwap(high, low, close, volume).iloc[-1]
    
    # Pivot
    pivot, r1, r2, s1, s2 = calc_pivot(high.iloc[-1], low.iloc[-1], close.iloc[-1])
    ind["pivot"] = pivot
    ind["r1"] = r1
    ind["r2"] = r2
    ind["s1"] = s1
    ind["s2"] = s2
    
    # Price
    ind["price"]    = close.iloc[-1]
    ind["price_prev"] = close.iloc[-2]
    ind["change_pct"] = (close.iloc[-1] / close.iloc[-2] - 1) * 100
    ind["price_52wh"] = high.rolling(252).max().iloc[-1]
    ind["price_52wl"] = low.rolling(252).min().iloc[-1]
    
    return ind

# ============================================================
# 7. SCORING ENGINE
# ============================================================
def score_stock(ind, params):
    """คะแนน 0-100 + สัญญาณ + เหตุผล"""
    buy_signals = []
    sell_signals = []
    neutral_signals = []
    score = 50  # เริ่มต้นกลาง

    price = ind["price"]
    rsi = ind["rsi"]
    ob = params["rsi_overbought"]
    os = params["rsi_oversold"]

    # --- RSI ---
    if rsi < os:
        score += 8; buy_signals.append(f"RSI = {rsi:.1f} (Oversold < {os}) → โซนซื้อ")
    elif rsi > ob:
        score -= 8; sell_signals.append(f"RSI = {rsi:.1f} (Overbought > {ob}) → โซนขาย")
    else:
        neutral_signals.append(f"RSI = {rsi:.1f} (ปกติ)")

    # --- MACD ---
    if ind["macd"] > ind["macd_signal"] and ind["macd_hist"] > 0:
        score += 7; buy_signals.append("MACD ตัดขึ้น Signal Line → โมเมนตัมขาขึ้น")
    elif ind["macd"] < ind["macd_signal"] and ind["macd_hist"] < 0:
        score -= 7; sell_signals.append("MACD ตัดลง Signal Line → โมเมนตัมขาลง")

    # --- MA Trend ---
    if price > ind["sma20"] > ind["sma50"]:
        score += 6; buy_signals.append(f"ราคา > SMA20 > SMA50 → uptrend ชัดเจน")
    elif price < ind["sma20"] < ind["sma50"]:
        score -= 6; sell_signals.append(f"ราคา < SMA20 < SMA50 → downtrend ชัดเจน")

    if price > ind["sma200"]:
        score += 4; buy_signals.append(f"ราคา > SMA200 → เหนือค่าเฉลี่ยระยะยาว")
    else:
        score -= 4; sell_signals.append(f"ราคา < SMA200 → ต่ำกว่าค่าเฉลี่ยระยะยาว")

    # --- Bollinger Bands ---
    bb_pct = ind["bb_pct"]
    if bb_pct < 0.2:
        score += 6; buy_signals.append(f"ราคาใกล้ BB Lower → โซน oversold ของ BB")
    elif bb_pct > 0.8:
        score -= 5; sell_signals.append(f"ราคาใกล้ BB Upper → โซน overbought ของ BB")
    if price > ind["bb_upper"]:
        score += 3; buy_signals.append("Breakout เหนือ BB Upper → สัญญาณ breakout")

    # --- Stochastic ---
    sk, sd = ind["stoch_k"], ind["stoch_d"]
    if sk < 20 and sd < 20 and sk > sd:
        score += 5; buy_signals.append(f"Stochastic %K={sk:.1f} ตัดขึ้น %D={sd:.1f} ในโซน oversold")
    elif sk > 80 and sd > 80 and sk < sd:
        score -= 5; sell_signals.append(f"Stochastic %K={sk:.1f} ตัดลง %D={sd:.1f} ในโซน overbought")

    # --- CCI ---
    cci = ind["cci"]
    if cci < -100:
        score += 4; buy_signals.append(f"CCI = {cci:.1f} < -100 → oversold")
    elif cci > 100:
        score -= 4; sell_signals.append(f"CCI = {cci:.1f} > 100 → overbought")

    # --- Williams %R ---
    wr = ind["williams_r"]
    if wr < -80:
        score += 4; buy_signals.append(f"Williams %R = {wr:.1f} < -80 → oversold")
    elif wr > -20:
        score -= 4; sell_signals.append(f"Williams %R = {wr:.1f} > -20 → overbought")

    # --- ADX / Trend Strength ---
    adx = ind["adx"]
    if adx > 25:
        if ind["di_plus"] > ind["di_minus"]:
            score += 5; buy_signals.append(f"ADX = {adx:.1f} > 25 & +DI > -DI → uptrend แข็งแกร่ง")
        else:
            score -= 5; sell_signals.append(f"ADX = {adx:.1f} > 25 & -DI > +DI → downtrend แข็งแกร่ง")
    else:
        neutral_signals.append(f"ADX = {adx:.1f} < 25 → ไม่มีแนวโน้มชัดเจน (sideways)")

    # --- MFI (Money Flow Index) ---
    mfi = ind["mfi"]
    if mfi < 20:
        score += 4; buy_signals.append(f"MFI = {mfi:.1f} < 20 → เงินไหลออกมาก (โอกาสดีดกลับ)")
    elif mfi > 80:
        score -= 4; sell_signals.append(f"MFI = {mfi:.1f} > 80 → เงินไหลเข้ามากเกิน (ระวังแรงขาย)")

    # --- Volume ---
    vol_ratio = ind["vol_ratio"]
    if vol_ratio > 1.5:
        score += 3; buy_signals.append(f"Volume สูงกว่าค่าเฉลี่ย {vol_ratio:.1f}x → มีนัยสำคัญ")
    elif vol_ratio < 0.5:
        neutral_signals.append(f"Volume ต่ำผิดปกติ ({vol_ratio:.1f}x) → ระวังสัญญาณหลอก")

    # --- VWAP ---
    if price > ind["vwap"]:
        score += 3; buy_signals.append(f"ราคา > VWAP → นักลงทุนสถาบันยังซื้ออยู่")
    else:
        score -= 3; sell_signals.append(f"ราคา < VWAP → แรงขายจากสถาบัน")

    # --- 52-week ---
    pct_52wh = (price / ind["price_52wh"] - 1) * 100
    pct_52wl = (price / ind["price_52wl"] - 1) * 100
    if pct_52wh > -5:
        score += 3; buy_signals.append(f"ราคาใกล้ 52W High → momentum สูง")
    if pct_52wl < 20:
        buy_signals.append(f"ราคาห่างจาก 52W Low {pct_52wl:.1f}% → โซนต่ำ")

    # Clamp
    score = max(0, min(100, score))

    if score >= 65:
        recommendation = "🟢 ซื้อ"
        rec_class = "buy"
    elif score <= 35:
        recommendation = "🔴 ขาย"
        rec_class = "sell"
    elif 55 <= score < 65:
        recommendation = "🟡 เฝ้าระวัง"
        rec_class = "watch"
    else:
        recommendation = "⚪ ถือ"
        rec_class = "neutral"

    # Price targets
    atr = ind["atr"]
    buy_entry   = round(price * 0.985, 2)
    target1     = round(price + atr * 2, 2)
    target2     = round(price + atr * 3.5, 2)
    stop_loss   = round(price - atr * 1.5, 2)
    
    upside = round((target1 / price - 1) * 100, 1)
    downside = round((price / stop_loss - 1) * 100, 1)
    risk_reward = round(upside / downside, 2) if downside > 0 else 0

    return {
        "score": score,
        "recommendation": recommendation,
        "rec_class": rec_class,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "neutral_signals": neutral_signals,
        "buy_entry": buy_entry,
        "target1": target1,
        "target2": target2,
        "stop_loss": stop_loss,
        "upside": upside,
        "downside": downside,
        "risk_reward": risk_reward,
    }

# ============================================================
# 8. SCAN ENGINE
# ============================================================
def scan_stocks(stock_list, params, progress_bar=None, status_text=None):
    results = []
    total = len(stock_list)
    for i, item in enumerate(stock_list):
        if len(item) == 2:
            symbol, name = item
            country = "TH"
        else:
            symbol, name, country = item

        try:
            if USE_MOCK:
                df = generate_mock_candles(symbol)
                quote = get_mock_quote(symbol)
            else:
                market_api, realtime_api = init_settrade()
                raw = market_api.get_candlestick(symbol, interval="1d", limit=100)
                df = pd.DataFrame(raw)
                quote = realtime_api.get_quote_symbol(symbol)

            ind = compute_all_indicators(df, params)
            scored = score_stock(ind, params)

            results.append({
                "Symbol": symbol,
                "Name": name,
                "Country": country,
                "Price": round(ind["price"], 2),
                "Change%": round(ind["change_pct"], 2),
                "RSI": round(ind["rsi"], 1),
                "MACD_Hist": round(ind["macd_hist"], 4),
                "ADX": round(ind["adx"], 1),
                "BB%": round(ind["bb_pct"], 3),
                "Volume_Ratio": round(ind["vol_ratio"], 2),
                "Score": scored["score"],
                "Signal": scored["recommendation"],
                "Signal_Class": scored["rec_class"],
                "BuyEntry": scored["buy_entry"],
                "Target1": scored["target1"],
                "Target2": scored["target2"],
                "StopLoss": scored["stop_loss"],
                "RiskReward": scored["risk_reward"],
                "_ind": ind,
                "_scored": scored,
            })
        except Exception as e:
            pass

        if progress_bar:
            progress_bar.progress((i + 1) / total)
        if status_text:
            status_text.text(f"กำลังสแกน... {symbol} ({i+1}/{total})")

    return pd.DataFrame(results)

# ============================================================
# 9. SIDEBAR PARAMETERS
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ ตั้งค่าพารามิเตอร์")

    st.markdown('<div class="section-header">📊 Trend</div>', unsafe_allow_html=True)
    sma_short = st.slider("SMA Short (วัน)", 5, 50, 20)
    sma_mid   = st.slider("SMA Mid (วัน)", 30, 100, 50)
    sma_long  = st.slider("SMA Long (วัน)", 100, 300, 200)
    ema_fast  = st.slider("EMA Fast (วัน)", 5, 20, 12)
    ema_slow  = st.slider("EMA Slow (วัน)", 15, 50, 26)

    st.markdown('<div class="section-header">🔄 Momentum</div>', unsafe_allow_html=True)
    rsi_period     = st.slider("RSI Period", 7, 21, 14)
    rsi_overbought = st.slider("RSI Overbought", 60, 85, 70)
    rsi_oversold   = st.slider("RSI Oversold", 15, 40, 30)
    macd_fast   = st.slider("MACD Fast", 8, 20, 12)
    macd_slow   = st.slider("MACD Slow", 20, 40, 26)
    macd_signal_p = st.slider("MACD Signal", 5, 15, 9)
    stoch_k = st.slider("Stochastic %K", 5, 21, 14)
    stoch_d = st.slider("Stochastic %D", 2, 7, 3)
    cci_period = st.slider("CCI Period", 10, 30, 20)
    williams_period = st.slider("Williams %R Period", 7, 21, 14)
    mfi_period = st.slider("MFI Period", 7, 21, 14)

    st.markdown('<div class="section-header">📏 Volatility</div>', unsafe_allow_html=True)
    bb_period = st.slider("Bollinger Period", 10, 30, 20)
    bb_std    = st.slider("Bollinger Std Dev", 1.0, 3.0, 2.0, step=0.5)
    atr_period = st.slider("ATR Period", 7, 21, 14)
    adx_period = st.slider("ADX Period", 7, 21, 14)

    st.markdown('<div class="section-header">🎯 ฟิลเตอร์ผลลัพธ์</div>', unsafe_allow_html=True)
    min_score   = st.slider("คะแนนขั้นต่ำ", 0, 100, 60)
    min_rr      = st.slider("Risk/Reward ขั้นต่ำ", 0.5, 5.0, 1.5, step=0.5)
    min_adx     = st.slider("ADX ขั้นต่ำ (ความแรงแนวโน้ม)", 0, 50, 20)
    show_signal = st.multiselect(
        "แสดงสัญญาณ",
        ["🟢 ซื้อ", "🟡 เฝ้าระวัง", "⚪ ถือ", "🔴 ขาย"],
        default=["🟢 ซื้อ", "🟡 เฝ้าระวัง"]
    )

params = {
    "sma_short": sma_short, "sma_mid": sma_mid, "sma_long": sma_long,
    "ema_fast": ema_fast, "ema_slow": ema_slow,
    "rsi_period": rsi_period, "rsi_overbought": rsi_overbought, "rsi_oversold": rsi_oversold,
    "macd_fast": macd_fast, "macd_slow": macd_slow, "macd_signal": macd_signal_p,
    "stoch_k": stoch_k, "stoch_d": stoch_d,
    "cci_period": cci_period, "williams_period": williams_period, "mfi_period": mfi_period,
    "bb_period": bb_period, "bb_std": bb_std, "atr_period": atr_period, "adx_period": adx_period,
}

# ============================================================
# 10. MAIN UI
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🚀 AI Stock Scanner Pro</h1>
    <p>สแกนหาหุ้นไทย + เทคโนโลยีโลก ด้วย 15+ Technical Indicators</p>
    <p style="font-size:0.8rem; color:#636e72;">⚡ Powered by Settrade API | RSI · MACD · BB · Stochastic · ADX · CCI · Williams %R · MFI · OBV · VWAP · ATR · Pivot</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🇹🇭 หุ้นไทย (SET)", "🌏 หุ้นต่างประเทศ", "🔍 วิเคราะห์เจาะลึก"])

# ============================================================
# TAB 1: THAI STOCKS
# ============================================================
with tab1:
    st.markdown("### 🇹🇭 สแกนหุ้นไทย — ตลาดหลักทรัพย์ (SET)")
    
    col_a, col_b, col_c = st.columns([2,2,1])
    with col_a:
        st.info(f"📋 มีหุ้นในฐานข้อมูล {len(THAI_STOCKS)} ตัว (SET50, SET100, mai)")
    with col_c:
        scan_thai = st.button("🔍 เริ่มสแกน", key="scan_thai", use_container_width=True)

    if scan_thai or "thai_results" in st.session_state:
        if scan_thai:
            with st.spinner(""):
                pb = st.progress(0)
                st_txt = st.empty()
                df_thai = scan_stocks(THAI_STOCKS, params, pb, st_txt)
                pb.empty()
                st_txt.empty()
                st.session_state["thai_results"] = df_thai
        
        df_thai = st.session_state["thai_results"]
        
        # Filter
        df_filtered = df_thai[
            (df_thai["Score"] >= min_score) &
            (df_thai["RiskReward"] >= min_rr) &
            (df_thai["ADX"] >= min_adx) &
            (df_thai["Signal"].isin(show_signal))
        ].sort_values("Score", ascending=False)

        # Summary metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            buy_count = len(df_thai[df_thai["Signal_Class"] == "buy"])
            st.metric("🟢 สัญญาณซื้อ", f"{buy_count} หุ้น")
        with c2:
            sell_count = len(df_thai[df_thai["Signal_Class"] == "sell"])
            st.metric("🔴 สัญญาณขาย", f"{sell_count} หุ้น")
        with c3:
            avg_score = df_thai["Score"].mean()
            st.metric("📊 คะแนนเฉลี่ย", f"{avg_score:.1f}/100")
        with c4:
            st.metric("🎯 ผ่านฟิลเตอร์", f"{len(df_filtered)} หุ้น")

        st.markdown(f"### 📋 ผลการสแกน — พบ **{len(df_filtered)}** หุ้นที่น่าสนใจ")
        
        if len(df_filtered) > 0:
            display_cols = ["Symbol", "Name", "Price", "Change%", "RSI", "ADX", "Score", "Signal", "BuyEntry", "Target1", "Target2", "StopLoss", "RiskReward"]
            
            def color_signal(val):
                colors = {"🟢 ซื้อ": "#00b894", "🔴 ขาย": "#d63031", "🟡 เฝ้าระวัง": "#e17055", "⚪ ถือ": "#636e72"}
                return f"color: {colors.get(val, '#fff')}; font-weight: bold"

            def color_change(val):
                return "color: #00b894" if val >= 0 else "color: #d63031"

            def color_score(val):
                if val >= 65: return "background-color: rgba(0,184,148,0.2); color: #00b894; font-weight:bold"
                elif val <= 35: return "background-color: rgba(214,48,49,0.2); color: #d63031; font-weight:bold"
                else: return "color: #fdcb6e"

            styled_df = df_filtered[display_cols].style \
                .applymap(color_signal, subset=["Signal"]) \
                .applymap(color_change, subset=["Change%"]) \
                .applymap(color_score, subset=["Score"]) \
                .format({
                    "Price": "฿{:.2f}", "Change%": "{:+.2f}%",
                    "RSI": "{:.1f}", "ADX": "{:.1f}", "Score": "{:.0f}",
                    "BuyEntry": "฿{:.2f}", "Target1": "฿{:.2f}", "Target2": "฿{:.2f}",
                    "StopLoss": "฿{:.2f}", "RiskReward": "{:.2f}x"
                })
            
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # Click to analyze
            st.markdown("---")
            selected_thai = st.selectbox(
                "🔍 เลือกหุ้นเพื่อวิเคราะห์เจาะลึก →",
                ["-- เลือกหุ้น --"] + df_filtered["Symbol"].tolist(),
                key="sel_thai"
            )
            if selected_thai != "-- เลือกหุ้น --":
                st.session_state["analyze_symbol"] = selected_thai
                st.session_state["analyze_df"] = df_thai

        else:
            st.warning("ไม่พบหุ้นที่ผ่านเงื่อนไขฟิลเตอร์ ลองปรับพารามิเตอร์ในแถบซ้ายมือ")

        st.markdown(f'<div class="update-time">🕐 อัปเดตล่าสุด: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)

# ============================================================
# TAB 2: INTERNATIONAL STOCKS
# ============================================================
with tab2:
    st.markdown("### 🌏 สแกนหุ้นเทคโนโลยี — สหรัฐ 🇺🇸 & จีน 🇨🇳")
    
    col_x, col_y = st.columns([1,1])
    with col_x:
        country_filter = st.multiselect("เลือกประเทศ", ["US", "CN"], default=["US", "CN"])
    
    intl_filtered_list = [(s, n, c) for s, n, c in INTL_TECH_STOCKS if c in country_filter]
    st.info(f"📋 มีหุ้น Tech {len(intl_filtered_list)} ตัว | 🇺🇸 US: {sum(1 for _,_,c in intl_filtered_list if c=='US')} | 🇨🇳 CN: {sum(1 for _,_,c in intl_filtered_list if c=='CN')}")

    scan_intl = st.button("🔍 เริ่มสแกน", key="scan_intl", use_container_width=False)

    if scan_intl or "intl_results" in st.session_state:
        if scan_intl:
            with st.spinner(""):
                pb2 = st.progress(0)
                st2 = st.empty()
                df_intl = scan_stocks(intl_filtered_list, params, pb2, st2)
                pb2.empty(); st2.empty()
                st.session_state["intl_results"] = df_intl
        
        df_intl = st.session_state["intl_results"]
        
        df_intl_f = df_intl[
            (df_intl["Score"] >= min_score) &
            (df_intl["RiskReward"] >= min_rr) &
            (df_intl["Signal"].isin(show_signal))
        ].sort_values("Score", ascending=False)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("🟢 ซื้อ", f"{len(df_intl[df_intl['Signal_Class']=='buy'])} หุ้น")
        with c2: st.metric("🔴 ขาย", f"{len(df_intl[df_intl['Signal_Class']=='sell'])} หุ้น")
        with c3: st.metric("📊 คะแนนเฉลี่ย", f"{df_intl['Score'].mean():.1f}/100")
        with c4: st.metric("🎯 ผ่านฟิลเตอร์", f"{len(df_intl_f)} หุ้น")

        # US vs CN breakdown
        if len(df_intl_f) > 0:
            col_us, col_cn = st.columns(2)
            for flag, ctry, col in [("🇺🇸", "US", col_us), ("🇨🇳", "CN", col_cn)]:
                sub = df_intl_f[df_intl_f["Country"] == ctry]
                with col:
                    st.markdown(f"#### {flag} หุ้น {ctry} ({len(sub)} ตัว)")
                    if len(sub) > 0:
                        for _, row in sub.iterrows():
                            score_cls = "score-high" if row["Score"] >= 65 else "score-med" if row["Score"] >= 45 else "score-low"
                            chg_color = "#00b894" if row["Change%"] >= 0 else "#d63031"
                            st.markdown(f"""
                            <div style="background:#1a1a2e; border-radius:10px; padding:10px; margin:5px 0; display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <strong style="color:#e2e8f0; font-size:1rem;">{row['Symbol']}</strong>
                                    <span style="color:#a8b2d8; font-size:0.8rem; margin-left:8px;">{row['Name']}</span><br>
                                    <span style="color:#e2e8f0;">$ {row['Price']:.2f}</span>
                                    <span style="color:{chg_color}; margin-left:8px;">{row['Change%']:+.2f}%</span>
                                </div>
                                <div style="text-align:right;">
                                    <span class="score-badge {score_cls}">{row['Score']:.0f}</span><br>
                                    <small style="color:#a8b2d8;">{row['Signal']}</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("ไม่มีหุ้นผ่านฟิลเตอร์")

            st.markdown("---")
            selected_intl = st.selectbox(
                "🔍 เลือกหุ้นเพื่อวิเคราะห์เจาะลึก →",
                ["-- เลือกหุ้น --"] + df_intl_f["Symbol"].tolist(),
                key="sel_intl"
            )
            if selected_intl != "-- เลือกหุ้น --":
                st.session_state["analyze_symbol"] = selected_intl
                st.session_state["analyze_df"] = df_intl

# ============================================================
# TAB 3: DEEP ANALYSIS
# ============================================================
with tab3:
    st.markdown("### 🔍 วิเคราะห์หุ้นเจาะลึก")

    analyze_symbol = st.session_state.get("analyze_symbol", None)
    analyze_df_src = st.session_state.get("analyze_df", None)

    # Manual entry
    manual_sym = st.text_input("หรือพิมพ์ชื่อหุ้นที่ต้องการวิเคราะห์:", placeholder="เช่น ADVANC, NVDA, BABA")
    if manual_sym:
        analyze_symbol = manual_sym.strip().upper()
        analyze_df_src = None

    if analyze_symbol:
        st.markdown(f"#### 📌 กำลังวิเคราะห์: **{analyze_symbol}**")

        # ดึงข้อมูล
        if analyze_df_src is not None and analyze_symbol in analyze_df_src["Symbol"].values:
            row = analyze_df_src[analyze_df_src["Symbol"] == analyze_symbol].iloc[0]
            ind = row["_ind"]
            scored = row["_scored"]
        else:
            with st.spinner(f"กำลังดึงข้อมูล {analyze_symbol}..."):
                df_raw = generate_mock_candles(analyze_symbol)
                ind = compute_all_indicators(df_raw, params)
                scored = score_stock(ind, params)

        price = ind["price"]
        currency = "฿" if len(analyze_symbol) >= 3 and analyze_symbol.isalpha() and not any(c.isdigit() for c in analyze_symbol) else "$"

        # Score display
        score = scored["score"]
        score_color = "#00b894" if score >= 65 else "#fdcb6e" if score >= 45 else "#d63031"
        
        col_score, col_rec, col_rr = st.columns([1,2,2])
        with col_score:
            st.markdown(f"""
            <div style="text-align:center; padding:20px;">
                <div style="font-size:3rem; font-weight:700; color:{score_color}; font-family:'Space Grotesk',sans-serif;">
                    {score}
                </div>
                <div style="color:#a8b2d8; font-size:0.85rem;">คะแนนรวม (0-100)</div>
                <div style="font-size:1.2rem; margin-top:8px;">{scored['recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_rec:
            chg_color = "#00b894" if ind["change_pct"] >= 0 else "#d63031"
            st.markdown(f"""
            <div style="background:#1a1a2e; border-radius:12px; padding:16px; height:100%;">
                <div style="font-size:1.8rem; font-weight:700; color:#e2e8f0; font-family:'Space Grotesk',sans-serif;">
                    {currency}{price:.2f}
                </div>
                <div style="color:{chg_color}; font-size:1rem;">{ind['change_pct']:+.2f}% วันนี้</div>
                <div style="color:#a8b2d8; font-size:0.8rem; margin-top:8px;">
                    52W สูง: {currency}{ind['price_52wh']:.2f} | ต่ำ: {currency}{ind['price_52wl']:.2f}
                </div>
                <div style="color:#a8b2d8; font-size:0.8rem;">
                    Volume Ratio: {ind['vol_ratio']:.2f}x
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_rr:
            st.markdown(f"""
            <div style="background:#1a1a2e; border-radius:12px; padding:16px; height:100%;">
                <div style="color:#a8b2d8; font-size:0.8rem; text-transform:uppercase;">Risk/Reward Ratio</div>
                <div style="font-size:1.8rem; font-weight:700; color:#6c63ff; font-family:'Space Grotesk',sans-serif;">
                    1 : {scored['risk_reward']:.2f}
                </div>
                <div style="color:#00b894; font-size:0.85rem;">📈 Upside: +{scored['upside']}%</div>
                <div style="color:#d63031; font-size:0.85rem;">📉 Downside: -{scored['downside']}%</div>
            </div>
            """, unsafe_allow_html=True)

        # Price targets
        st.markdown("#### 🎯 เป้าหมายราคา")
        t1, t2, t3, t4 = st.columns(4)
        targets = [
            ("จุดซื้อ", scored["buy_entry"], "#6c63ff"),
            ("เป้าหมาย 1", scored["target1"], "#00b894"),
            ("เป้าหมาย 2", scored["target2"], "#00b894"),
            ("Stop Loss", scored["stop_loss"], "#d63031"),
        ]
        for col, (label, val, color) in zip([t1, t2, t3, t4], targets):
            with col:
                st.markdown(f"""
                <div class="target-box" style="border-color: {color}40; background: {color}10;">
                    <div class="target-label">{label}</div>
                    <div class="target-value" style="color:{color};">{currency}{val:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Indicator summary table
        col_ind1, col_ind2 = st.columns(2)
        
        with col_ind1:
            st.markdown("#### 📊 สรุป Indicators")
            
            def ind_status(condition_buy, condition_sell, val_str):
                if condition_buy: return f"🟢 {val_str}"
                elif condition_sell: return f"🔴 {val_str}"
                else: return f"🟡 {val_str}"

            indicators_display = [
                ("RSI", ind_status(ind["rsi"] < params["rsi_oversold"], ind["rsi"] > params["rsi_overbought"], f"{ind['rsi']:.1f}")),
                ("MACD", ind_status(ind["macd"] > ind["macd_signal"], ind["macd"] < ind["macd_signal"], f"{ind['macd']:.4f}")),
                ("Stochastic %K", ind_status(ind["stoch_k"] < 20, ind["stoch_k"] > 80, f"{ind['stoch_k']:.1f}")),
                ("Bollinger %B", ind_status(ind["bb_pct"] < 0.2, ind["bb_pct"] > 0.8, f"{ind['bb_pct']:.2f}")),
                ("CCI", ind_status(ind["cci"] < -100, ind["cci"] > 100, f"{ind['cci']:.1f}")),
                ("Williams %R", ind_status(ind["williams_r"] < -80, ind["williams_r"] > -20, f"{ind['williams_r']:.1f}")),
                ("MFI", ind_status(ind["mfi"] < 20, ind["mfi"] > 80, f"{ind['mfi']:.1f}")),
                ("ADX", ind_status(ind["adx"] > 25 and ind["di_plus"] > ind["di_minus"], ind["adx"] > 25 and ind["di_minus"] > ind["di_plus"], f"{ind['adx']:.1f}")),
                ("VWAP", ind_status(price > ind["vwap"], price < ind["vwap"], f"{currency}{ind['vwap']:.2f}")),
                ("Volume", ind_status(ind["vol_ratio"] > 1.5, ind["vol_ratio"] < 0.5, f"{ind['vol_ratio']:.2f}x")),
                ("vs SMA20", ind_status(price > ind["sma20"], price < ind["sma20"], f"{currency}{ind['sma20']:.2f}")),
                ("vs SMA50", ind_status(price > ind["sma50"], price < ind["sma50"], f"{currency}{ind['sma50']:.2f}")),
                ("vs SMA200", ind_status(price > ind["sma200"], price < ind["sma200"], f"{currency}{ind['sma200']:.2f}")),
                ("ATR", ("🟡" + f" {currency}{ind['atr']:.2f}")),
                ("Pivot", f"🟡 {currency}{ind['pivot']:.2f}"),
            ]
            
            for name, status in indicators_display:
                st.markdown(f"""
                <div class="indicator-row" style="padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between;">
                    <span style="color:#a8b2d8; font-size:0.85rem;">{name}</span>
                    <span style="font-size:0.85rem; color:#e2e8f0;">{status}</span>
                </div>
                """, unsafe_allow_html=True)

        with col_ind2:
            st.markdown("#### 🧠 เหตุผลการวิเคราะห์")
            
            if scored["buy_signals"]:
                st.markdown("**🟢 สัญญาณซื้อ**")
                for sig in scored["buy_signals"]:
                    st.markdown(f'<div class="analysis-box buy-reason">✅ {sig}</div>', unsafe_allow_html=True)
            
            if scored["sell_signals"]:
                st.markdown("**🔴 สัญญาณขาย**")
                for sig in scored["sell_signals"]:
                    st.markdown(f'<div class="analysis-box sell-reason">❌ {sig}</div>', unsafe_allow_html=True)
            
            if scored["neutral_signals"]:
                st.markdown("**⚪ ข้อมูลกลาง**")
                for sig in scored["neutral_signals"]:
                    st.markdown(f'<div class="analysis-box neutral-reason">ℹ️ {sig}</div>', unsafe_allow_html=True)

        # Pivot Levels
        st.markdown("#### 📐 Pivot Points & Support/Resistance")
        pc1, pc2, pc3, pc4, pc5 = st.columns(5)
        pvt_data = [
            ("R2 (แรงต้าน 2)", ind["r2"], "#ff7675"),
            ("R1 (แรงต้าน 1)", ind["r1"], "#fab1a0"),
            ("PIVOT", ind["pivot"], "#74b9ff"),
            ("S1 (แนวรับ 1)", ind["s1"], "#55efc4"),
            ("S2 (แนวรับ 2)", ind["s2"], "#00cec9"),
        ]
        for col, (label, val, color) in zip([pc1,pc2,pc3,pc4,pc5], pvt_data):
            with col:
                st.markdown(f"""
                <div style="text-align:center; background:#1a1a2e; border-radius:8px; padding:10px;">
                    <div style="font-size:0.7rem; color:#a8b2d8;">{label}</div>
                    <div style="font-size:1rem; font-weight:700; color:{color}; font-family:'Space Grotesk',sans-serif;">{currency}{val:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.info("👆 สแกนหุ้นในแท็บ 'หุ้นไทย' หรือ 'หุ้นต่างประเทศ' ก่อน แล้วคลิกเลือกหุ้นเพื่อวิเคราะห์เจาะลึก\nหรือพิมพ์ชื่อหุ้นด้านบนโดยตรง")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#636e72; font-size:0.8rem; padding:10px;">
    ⚠️ <strong>คำเตือน:</strong> โปรแกรมนี้ใช้เพื่อการศึกษาและวิเคราะห์เท่านั้น ไม่ใช่คำแนะนำการลงทุน<br>
    การลงทุนมีความเสี่ยง ผู้ลงทุนควรศึกษาข้อมูลก่อนตัดสินใจ<br>
    🚀 <strong>AI Stock Scanner Pro</strong> | Powered by Settrade API + Technical Analysis Engine
</div>
""", unsafe_allow_html=True)
