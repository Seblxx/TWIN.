# app.py
from __future__ import annotations
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import re
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import os
import json
from companies import COMPANY_TICKER_MAP

# Supabase Configuration
SUPABASE_URL = 'https://tocuqnqdewhqhbhkbplm.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3VxbnFkZXdocWhiaGticGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDE2MzgsImV4cCI6MjA3OTU3NzYzOH0.vWfItFkQpHA7Is-KX4eQalI-wxUAJcejPAvy7NDQHvc'

# Initialize Supabase client
try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Supabase connected successfully!")
except ImportError:
    supabase = None
    print("[WARNING] Supabase not installed. Run: pip install supabase")

app = Flask(__name__)
CORS(app)  # allow local frontends

# ---------------------------- period parsing ---------------------------------
DUR_RE_SIMPLE = re.compile(r"(\d+)?\s*(day|days|week|weeks|month|months|year|years)", re.I)

# permissive duration phrases we want to strip from name search
DUR_RE_NUMBERED = re.compile(
    r"\b(?:in\s+)?(?:about|around|approx(?:imate(?:ly)?)?|~)?\s*(\d+)\s*"
    r"(day|days|week|weeks|month|months|year|years)\b",
    re.I,
)
DUR_RE_AFORM = re.compile(
    r"\b(?:in\s+)?(?:about|around|approximately|~)?\s*(?:a|an|one)\s*"
    r"(day|week|month|year)s?\b",
    re.I,
)
DUR_RE_KEYWORDS = re.compile(
    r"\b(?:in\s+)?(?:the\s+)?(?:next|upcoming|coming|this)\s*"
    r"(day|week|month|year)s?\b", re.I
)
# common misspellings of "tomorrow"
TOMORROW_RE = re.compile(r"\bto+m+o*r*o*w+\b", re.I)  # tomorrow, tommorrow, tomorow, etc.

def parse_period(text: str) -> tuple[int | None, str | None]:
    """Return (n, unit) when a duration exists; else (None, None)."""
    t = (text or "").lower().strip()
    if not t:
        return None, None

    if TOMORROW_RE.search(t):
        return 1, "days"
    if "today" in t:
        return 0, "days"
    if re.search(r"\bnext\s+week\b", t):
        return 1, "weeks"
    if re.search(r"\bnext\s+month\b", t):
        return 1, "months"
    if re.search(r"\bnext\s+year\b", t):
        return 1, "years"

    m = DUR_RE_NUMBERED.search(t) or DUR_RE_AFORM.search(t) or DUR_RE_KEYWORDS.search(t) or DUR_RE_SIMPLE.search(t)
    if not m:
        return None, None

    # normalize to plural unit
    if len(m.groups()) >= 2 and m.group(1) and m.group(2):
        n = int(m.group(1))
        unit = m.group(2).lower()
    else:
        # a/an/one + unit || keyword paths
        n = 1
        unit = (m.group(1) or m.group(2)).lower()

    if "day" in unit: unit = "days"
    elif "week" in unit: unit = "weeks"
    elif "month" in unit: unit = "months"
    elif "year" in unit: unit = "years"
    return n, unit

def horizon_to_trading_days(n: int, unit: str) -> int:
    return {"days": n, "weeks": n*5, "months": n*21, "years": n*252}.get(unit, n)

# -------------------------- duration stripping for name search ---------------
def strip_duration_phrases(text: str) -> str:
    """Remove timeframe words so they don't contaminate company search."""
    s = text or ""
    s = TOMORROW_RE.sub(" ", s)
    s = re.sub(r"\btoday\b", " ", s, flags=re.I)
    s = DUR_RE_NUMBERED.sub(" ", s)
    s = DUR_RE_AFORM.sub(" ", s)
    s = DUR_RE_KEYWORDS.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# -------------------------- name -> ticker search (robust) -------------------
STOPWORDS = {
    "in","for","over","the","next","this","coming","upcoming","today","tomorrow",
    "week","weeks","day","days","month","months","year","years","about","around",
    "approximately","approx","~", "a", "an"  # drop articles so "apple a" can't happen
}
CLEAN_RE = re.compile(r"[^a-zA-Z\s]")
NUM_RE   = re.compile(r"\b\d+\b")
SYMBOL_RE = re.compile(r"\b\$?[A-Z]{1,5}\b")

def extract_company_query(text: str) -> str | None:
    """Remove numbers/punct/stopwords to keep only a clean company name."""
    t = strip_duration_phrases((text or "")).lower().replace("’","'")
    t = NUM_RE.sub(" ", t)
    t = CLEAN_RE.sub(" ", t)
    words = [w for w in t.split() if w and w not in STOPWORDS]
    q = " ".join(words).strip()
    return q or None

def _yahoo_search(query: str) -> list[dict]:
    """Call Yahoo Search (query2, then query1) with headers. Return quotes list or []."""
    if not query:
        return []
    params = {"q": query, "quotesCount": 20, "newsCount": 0, "listsCount": 0}
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
    }
    urls = [
        "https://query2.finance.yahoo.com/v1/finance/search",
        "https://query1.finance.yahoo.com/v1/finance/search",
    ]
    for url in urls:
        try:
            r = requests.get(url, params=params, headers=headers, timeout=5)
            r.raise_for_status()
            quotes = (r.json() or {}).get("quotes") or []
            if quotes:
                return quotes
        except Exception:
            continue
    return []

def yahoo_search_company_to_symbol(text: str) -> str | None:
    """
    Resolve a free-text company name to a ticker using Yahoo Search.
    Prioritizes EQUITY on US exchanges whose name overlaps the query tokens.
    """
    q_raw = strip_duration_phrases(text or "").strip()
    q = (extract_company_query(q_raw) or q_raw).strip()
    if not q:
        return None

    tokens = [t for t in re.split(r"\s+", q.lower()) if t]
    token_set = set(tokens)

    def rank(item: dict) -> tuple:
        name = (item.get("shortname") or item.get("longname") or "").lower()
        sym  = (item.get("symbol") or "")
        quote_type = item.get("quoteType")
        exch = item.get("exchange")
        region = item.get("region")

        # token overlap (prefer more shared words)
        name_tokens = set(re.findall(r"[a-z]+", name))
        overlap = len(token_set & name_tokens)

        contains_all = 0 if all(t in name for t in token_set) else 1
        contains_any = 0 if any(t in name for t in token_set) else 1
        eq = 0 if quote_type == "EQUITY" else 1
        us = 0 if (exch in {"NMS","NYQ","ASE","NMS2"} or region == "US") else 1
        sym_len_penalty = 0 if 2 <= len(sym) <= 5 else (2 if len(sym) == 1 else 1)  # penalize 1-letter symbols

        # shorter names with same overlap get a tiny boost
        return (-overlap, contains_all, contains_any, eq, us, sym_len_penalty, len(name) if name else 999)

    quotes = _yahoo_search(q)
    if not quotes:
        # try stripping common corporate suffixes
        q2 = re.sub(r"\b(inc|incorporated|corp|corporation|co|company|ltd|limited|plc|nv|sa|ag)\b\.?", "", q, flags=re.I)
        q2 = re.sub(r"\s+", " ", q2).strip()
        if q2:
            quotes = _yahoo_search(q2)

    if not quotes:
        return None

    # sort by our rank and drop obvious non-stocks
    quotes = [it for it in quotes if (it.get("quoteType") in {"EQUITY","ETF","MUTUALFUND","INDEX"} or it.get("quoteType") is None)]
    quotes.sort(key=rank)
    # prefer non-single-letter symbols; keep a second pass if needed
    for it in quotes:
        sym = it.get("symbol") or ""
        if 2 <= len(sym) <= 5:
            return sym

    # last resort: single-letter only if user explicitly typed it
    explicit_syms = set([m.group(0).lstrip("$") for m in SYMBOL_RE.finditer(text or "") if m.group(0).isupper() ])
    for it in quotes:
        sym = it.get("symbol") or ""
        if len(sym) == 1 and sym in explicit_syms:
            return sym
    return None

def validate_ticker(ticker: str) -> bool:
    """Use yfinance to make sure the symbol returns data."""
    try:
        end = datetime.utcnow(); start = end - timedelta(days=14)
        df = yf.download(ticker, start=start.strftime("%Y-%m-%d"),
                         end=end.strftime("%Y-%m-%d"), progress=False)
        return (df is not None) and (not df.empty) and ("Close" in df.columns)
    except Exception:
        return False

def detect_ticker(user_text: str) -> str | None:
    """Detect ticker using explicit symbols or fuzzy matching against hardcoded list."""
    if not user_text:
        return None
    
    # 1) explicit ticker typed by the user (e.g., "AAPL", "$MSFT")
    for m in SYMBOL_RE.finditer(user_text):
        raw = m.group(0)
        sym = raw[1:] if raw.startswith("$") else raw
        if sym.isupper() and validate_ticker(sym) and (2 <= len(sym) <= 5 or raw == sym or raw == f"${sym}"):
            return sym
    
    # 2) fuzzy match against company names
    query = extract_company_query(user_text)
    if not query:
        return None
    
    best_match = process.extractOne(
        query,
        COMPANY_TICKER_MAP.keys(),
        scorer=fuzz.token_sort_ratio,
        score_cutoff=82  # Balanced: catches reasonable typos, rejects garbled input
    )
    
    if best_match:
        company_name = best_match[0]
        ticker = COMPANY_TICKER_MAP[company_name]
        if validate_ticker(ticker):
            return ticker
    
    return None

# ------- suggestions for "did you mean?" -------------------------------------
def suggestion_candidates(user_text: str, limit: int = 3):
    """
    Return up to `limit` suggestions as (symbol, display_name).
    Uses fuzzy matching against hardcoded company list.
    """
    query = extract_company_query(user_text) or user_text.lower().strip()
    
    if not query:
        return [
            ("AAPL", "Apple"),
            ("MSFT", "Microsoft"),
            ("GOOGL", "Alphabet")
        ]
    
    matches = process.extract(
        query,
        COMPANY_TICKER_MAP.keys(),
        scorer=fuzz.token_sort_ratio,
        limit=limit * 2
    )
    
    suggestions = []
    for company_name, score, _ in matches:
        if len(suggestions) >= limit:
            break
        ticker = COMPANY_TICKER_MAP[company_name]
        display_name = company_name.title()
        suggestions.append((ticker, display_name))
    
    if not suggestions:
        suggestions = [
            ("AAPL", "Apple"),
            ("MSFT", "Microsoft"),
            ("GOOGL", "Alphabet")
        ]
    
    return suggestions[:limit]

def echo_with_duration(name_or_symbol: str, original: str) -> str:
    """Build echo like 'Apple in 2 days' reusing the user's duration."""
    n, unit = parse_period(original)
    if n is None or unit is None:
        return name_or_symbol
    return f"{name_or_symbol} in {n} {unit}"

def _suggest_payload(user_input: str):
    cands = suggestion_candidates(user_input, limit=3)
    # Always return suggestions (never None)
    suggestions = []
    for sym, name in cands:
        display = (name or sym).split(" (")[0]
        suggestions.append({
            "symbol": sym,
            "name": display,
            "echo": echo_with_duration(display, user_input)  # Use company name for "Did you mean?"
        })
    return {"suggestions": suggestions}

# ------------------------- prices + forecasting ------------------------------
def fetch_closes(ticker: str, days_back: int = 365) -> pd.Series | None:
    end = datetime.utcnow(); start = end - timedelta(days=days_back)
    df = yf.download(ticker, start=start.strftime("%Y-%m-%d"),
                     end=end.strftime("%Y-%m-%d"), progress=False)
    if df is None or df.empty or "Close" not in df:
        return None
    return df["Close"].dropna()

def baseline_drift(series: pd.Series) -> float:
    return float(series.tail(6).diff().mean()) if len(series) >= 6 else 0.0

def ema_drift(series: pd.Series, span: int = 6) -> float:
    changes = series.diff().dropna()
    if changes.empty:
        return 0.0
    return float(changes.ewm(span=span, adjust=False).mean().iloc[-1])

def linear_trend_drift(series: pd.Series, window: int = 20) -> float:
    y = series.tail(window).astype(float).to_numpy()
    if len(y) < 2:
        return 0.0
    x = np.arange(len(y), dtype=float)
    slope = float(np.polyfit(x, y, 1)[0])
    return slope

# ----------------------- light ML style forecast ---------------------------
def light_ml_forecast(series: pd.Series, horizon_days: int) -> tuple[float,float,str,float]:
    """
    Enhanced ML forecast using scikit-learn with ensemble methods.
    Features:
      - 20-day momentum (pct change vs 20 days ago)
      - 50-DMA slope (avg diff of last 5 points of SMA50)
      - 200-DMA slope (avg diff of last 5 points of SMA200)
      - Annualized volatility (sqrt(252 * mean of squared daily returns last 22 days))
      - 5-day momentum (shorter term trend)
      - 10-day momentum (medium term trend)
    Target: next-day return.
    Uses Ridge regression (L2 regularization) to reduce overfitting.
    Returns: (last_close, forecast_price, method_name, drift_per_day_price)
    """
    closes = series.dropna().astype(float)
    if len(closes) < 250:  # need enough history for 200-DMA related features
        last_close = float(closes.iloc[-1])
        drift = ema_drift(closes, span=6)
        forecast = last_close + drift * max(horizon_days,0)
        return last_close, forecast, "ema_drift", drift

    sma50 = closes.rolling(50).mean()
    sma200 = closes.rolling(200).mean()
    returns = closes.pct_change().dropna()

    rows = []
    targets = []
    start = 200
    for t in range(start, len(closes)-1):
        if t < 22 or t < 20:
            continue
        try:
            # Enhanced features with multiple momentum timeframes
            mom5 = float((closes.iloc[t] / closes.iloc[t-5]) - 1.0) if t >= 5 else 0.0
            mom10 = float((closes.iloc[t] / closes.iloc[t-10]) - 1.0) if t >= 10 else 0.0
            mom20 = float((closes.iloc[t] / closes.iloc[t-20]) - 1.0)
            
            dma50_seg = sma50.iloc[t-5:t]
            dma200_seg = sma200.iloc[t-5:t]
            if len(dma50_seg) < 5 or len(dma200_seg) < 5:
                continue
            slope50 = float(dma50_seg.diff().mean())
            slope200 = float(dma200_seg.diff().mean())
            
            vol_seg = returns.iloc[t-22:t]
            if len(vol_seg) < 22:
                continue
            vol22 = float(np.sqrt(252 * (vol_seg**2).mean()))
            
            ret_next = float((closes.iloc[t+1] / closes.iloc[t]) - 1.0)
            
            # Skip if any feature is NaN
            if any(np.isnan(x) for x in [mom5, mom10, mom20, slope50, slope200, vol22, ret_next]):
                continue
                
            rows.append([mom5, mom10, mom20, slope50, slope200, vol22])
            targets.append(ret_next)
        except Exception:
            continue

    X = np.array(rows, dtype=float)
    y = np.array(targets, dtype=float)
    
    if X.shape[0] < 50:
        last_close = float(closes.iloc[-1])
        drift = ema_drift(closes, span=6)
        forecast = last_close + drift * max(horizon_days,0)
        return last_close, forecast, "ema_drift", drift

    # Scale features for better model performance
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Use Ridge regression with cross-validation to find best alpha
    # Higher alpha = more regularization = more conservative predictions
    try:
        # Try different alpha values and pick the best
        best_score = -np.inf
        best_model = None
        
        for alpha in [0.1, 1.0, 10.0, 50.0]:
            model = Ridge(alpha=alpha)
            # Use last 60 samples for validation to avoid look-ahead bias
            if len(X_scaled) > 60:
                scores = cross_val_score(model, X_scaled[-60:], y[-60:], cv=3, scoring='neg_mean_absolute_error')
                score = scores.mean()
                if score > best_score:
                    best_score = score
                    best_model = Ridge(alpha=alpha)
        
        if best_model is None:
            best_model = Ridge(alpha=10.0)  # default conservative
            
        # Train on all data
        best_model.fit(X_scaled, y)
        
    except Exception:
        last_close = float(closes.iloc[-1])
        drift = ema_drift(closes, span=6)
        forecast = last_close + drift * max(horizon_days,0)
        return last_close, forecast, "ema_drift", drift

    # Make prediction for current state
    t = len(closes)-1
    mom5 = float((closes.iloc[t] / closes.iloc[t-5]) - 1.0) if t >= 5 else 0.0
    mom10 = float((closes.iloc[t] / closes.iloc[t-10]) - 1.0) if t >= 10 else 0.0
    mom20 = float((closes.iloc[t] / closes.iloc[t-20]) - 1.0)
    
    dma50_seg = sma50.iloc[t-5:t].dropna()
    dma200_seg = sma200.iloc[t-5:t].dropna()
    slope50 = float(dma50_seg.diff().mean()) if len(dma50_seg) == 5 else 0.0
    slope200 = float(dma200_seg.diff().mean()) if len(dma200_seg) == 5 else 0.0
    vol22 = float(np.sqrt(252 * (returns.iloc[t-22:t]**2).mean()))
    
    x_cur = np.array([[mom5, mom10, mom20, slope50, slope200, vol22]], dtype=float)
    x_cur_scaled = scaler.transform(x_cur)
    pred_ret_next = float(best_model.predict(x_cur_scaled)[0])
    
    # Conservative damping: reduce prediction magnitude for multi-day horizons
    # The further out, the more we regress toward zero return
    damping_factor = 1.0 / (1.0 + 0.1 * max(horizon_days - 1, 0))
    pred_ret_next *= damping_factor

    last_close = float(closes.iloc[-1])
    daily_price_drift = pred_ret_next * last_close
    forecast = last_close + daily_price_drift * max(horizon_days,0)
    return last_close, float(forecast), "ridge_ml_v2", float(daily_price_drift)

# ----------------------- new simple forecast variants -----------------------
def forecast_linear_trend(series: pd.Series, horizon_days: int, window: int = 60):
    """Linear trend forecast: fit slope to last `window` closes and extrapolate."""
    window = min(window, len(series))
    if window < 2:
        # fallback to ema drift path
        last_close = float(series.iloc[-1])
        drift = ema_drift(series, span=6)
        return last_close, last_close + drift * horizon_days, "ema_drift", drift
    seg = series.tail(window).astype(float).to_numpy()
    x = np.arange(len(seg), dtype=float)
    slope, intercept = np.polyfit(x, seg, 1)
    last_close = float(seg[-1])
    # extrapolate horizon days beyond last index
    forecast_idx = len(seg) - 1 + max(horizon_days, 0)
    forecast = float(intercept + slope * forecast_idx)
    return last_close, forecast, "linear_trend", float(slope)

def forecast_mean_reversion(series: pd.Series, horizon_days: int, ma_window: int = 20):
    """Mean reversion toward a moving average.
    Moves a fraction of the gap (scaled by horizon/ma_window, capped at 1).
    """
    if len(series) < 5:
        last_close = float(series.iloc[-1])
        drift = ema_drift(series, span=6)
        return last_close, last_close + drift * horizon_days, "ema_drift", drift
    last_close = float(series.iloc[-1])
    ma = float(series.tail(ma_window).mean())
    gap = ma - last_close
    strength = min(1.0, max(horizon_days, 0) / float(ma_window))
    forecast = last_close + gap * strength
    drift = (forecast - last_close) / max(horizon_days, 1)
    return last_close, forecast, "mean_reversion", drift

def forecast_with_method(series: pd.Series, horizon_days: int, method: str = "ema_drift"):
    """Dispatch to appropriate forecasting logic and return tuple.
    Returns (last_close, forecast, method_used, drift_per_day).
    """
    m = (method or "ema_drift").lower()
    if m == "ema_drift":
        last_close = float(series.iloc[-1])
        drift = ema_drift(series, span=6)
        forecast = last_close + drift * max(horizon_days, 0)
        return last_close, forecast, "ema_drift", drift
    if m == "linear_trend":
        return forecast_linear_trend(series, horizon_days, window=60)
    if m == "mean_reversion":
        return forecast_mean_reversion(series, horizon_days, ma_window=20)
    if m == "trend_blend":  # placeholder: reuse linear_trend; future: blend multiple signals
        return forecast_linear_trend(series, horizon_days, window=60)
    if m == "baseline_drift":
        last_close = float(series.iloc[-1])
        drift = baseline_drift(series)
        forecast = last_close + drift * max(horizon_days, 0)
        return last_close, forecast, "baseline_drift", drift
    # fallback
    last_close = float(series.iloc[-1])
    drift = ema_drift(series, span=6)
    forecast = last_close + drift * max(horizon_days, 0)
    return last_close, forecast, "ema_drift", drift

def backtest_mae(series: pd.Series, k_days: int, method: str = "ema_drift", lookback: int = 120) -> float | None:
    s = series.tail(lookback + 30)
    if len(s) < k_days + 10:
        return None
    preds, actuals = [], []
    for i in range(10, len(s) - k_days):
        hist = s.iloc[:i]
        m = (method or "ema_drift").lower()
        if m == "ema_drift":
            d = ema_drift(hist, span=6)
            pred = float(hist.iloc[-1]) + d * k_days
        elif m == "linear_trend" or m == "trend_blend":
            d = linear_trend_drift(hist, window=min(20, len(hist)))
            pred = float(hist.iloc[-1]) + d * k_days
        elif m == "mean_reversion":
            last_close_bt = float(hist.iloc[-1])
            ma = float(hist.tail(20).mean()) if len(hist) >= 5 else last_close_bt
            gap = ma - last_close_bt
            strength = min(1.0, k_days / 20.0)
            pred = last_close_bt + gap * strength
        else:  # baseline_drift or unknown
            d = baseline_drift(hist)
            pred = float(hist.iloc[-1]) + d * k_days
        act  = float(s.iloc[i + k_days - 1])
        preds.append(pred); actuals.append(act)
    if not preds:
        return None
    err = np.abs(np.array(preds) - np.array(actuals))
    return float(err.mean())

# ----------------------------- diagnostics (TWIN+) ----------------------------
def pct_change(series):  return series.pct_change().dropna()
def sma(series, n):      return series.rolling(n).mean()

def donchian_breakout(series, n=50):
    hi = series.rolling(n).max()
    lo = series.rolling(n).min()
    
    # Convert to scalars using .values[-1] to avoid Series ambiguity
    current_price = series.values[-1]
    hi_val = hi.values[-1] if not pd.isna(hi.values[-1]) else current_price
    lo_val = lo.values[-1] if not pd.isna(lo.values[-1]) else current_price
    
    # Compare scalars - this will be a Python bool, then convert to float
    breakout = 1.0 if current_price >= hi_val else 0.0
    return breakout, float(hi_val), float(lo_val)

def dma_slope(series, n):
    m = sma(series, n).dropna()
    if len(m) < 5: return 0.0
    # Get the last 5 values, compute diff, and get mean as a scalar
    tail_vals = m.tail(5).values  # Convert to numpy array
    diffs = np.diff(tail_vals)  # Compute differences
    if len(diffs) == 0:
        return 0.0
    mean_val = np.mean(diffs)
    # Handle NaN case
    if np.isnan(mean_val):
        return 0.0
    return float(mean_val)  # Return mean as float

def rv_daily(series):    return (pct_change(series)**2)

def har_rv_forecast(series):
    """
    HAR-RV style one-step forecast using daily/weekly/monthly RV.
    Returns annualized volatility as a fraction (e.g., 0.22 = 22%).
    """
    rv = rv_daily(series).dropna()
    if len(rv) < 22: return None
    RV_d = float(rv.iloc[-1])
    RV_w = float(rv.tail(5).mean())
    RV_m = float(rv.tail(22).mean())
    c, bd, bw, bm = 0.0, 0.3, 0.3, 0.4
    rv_next = c + bd*RV_d + bw*RV_w + bm*RV_m
    return float(np.sqrt(252 * rv_next))
def ensemble_forecast(series: pd.Series, horizon_days: int):
    """
    TWIN* Ensemble: Blend multiple forecasting methods with weighted averaging.
    Combines:
    - Light ML (OLS regression on engineered features)
    - Linear trend (extrapolation)
    - Mean reversion (moving average pull)
    - EMA drift (exponential smoothing)
    
    Returns: (last_close, forecast, method_name, drift_per_day)
    """
    if len(series) < 60:
        # Fallback to light ML if insufficient data
        return light_ml_forecast(series, horizon_days)
    
    forecasts = []
    weights = []
    
    # Method 1: Light ML (40% weight - most sophisticated)
    try:
        _, f1, _, _ = light_ml_forecast(series, horizon_days)
        forecasts.append(f1)
        weights.append(0.40)
    except:
        pass
    
    # Method 2: Linear Trend (25% weight)
    try:
        _, f2, _, _ = forecast_linear_trend(series, horizon_days, window=60)
        forecasts.append(f2)
        weights.append(0.25)
    except:
        pass
    
    # Method 3: Mean Reversion (20% weight)
    try:
        _, f3, _, _ = forecast_mean_reversion(series, horizon_days, ma_window=20)
        forecasts.append(f3)
        weights.append(0.20)
    except:
        pass
    
    # Method 4: EMA Drift (15% weight - baseline)
    try:
        last_close = float(series.iloc[-1])
        drift = ema_drift(series, span=6)
        f4 = last_close + drift * horizon_days
        forecasts.append(f4)
        weights.append(0.15)
    except:
        pass
    
    if not forecasts:
        # Ultimate fallback
        last_close = float(series.iloc[-1])
        drift = ema_drift(series, span=6)
        return last_close, last_close + drift * horizon_days, "ema_drift_fallback", drift
    
    # Normalize weights (in case some methods failed)
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]
    
    # Weighted average
    ensemble_forecast_value = sum(f * w for f, w in zip(forecasts, weights))
    last_close = float(series.iloc[-1])
    drift = (ensemble_forecast_value - last_close) / max(horizon_days, 1)
    
    return last_close, float(ensemble_forecast_value), "ensemble_v1", float(drift)

# --------------------------------- routes ------------------------------------
@app.get("/")
def index():
    """Serve the intro page as default"""
    response = send_from_directory('.', 'intro.html')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.get("/api/config")
def get_config():
    """Return Supabase configuration for frontend"""
    return jsonify({
        "supabaseUrl": SUPABASE_URL,
        "supabaseKey": SUPABASE_KEY
    })

@app.get("/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}

@app.get("/history")
def history():
    ticker = request.args.get("ticker","").strip().upper()
    days   = int(request.args.get("days","90"))
    if not ticker or not validate_ticker(ticker):
        return jsonify({"error":"Invalid or missing ticker."}), 400
    s = fetch_closes(ticker, days_back=max(days+30, 120))
    if s is None or s.empty:
        return jsonify({"error": f"No price data for {ticker}."}), 400
    s = s.tail(days)
    return jsonify({"ticker": ticker, "closes": [float(x) for x in s.values]})

@app.get("/backtest")
def backtest():
    ticker = request.args.get("ticker","").strip().upper()
    k      = int(request.args.get("k","3"))
    method = request.args.get("method","ema_drift")
    if not ticker or not validate_ticker(ticker):
        return jsonify({"error":"Invalid or missing ticker."}), 400
    s = fetch_closes(ticker, days_back=365)
    if s is None or s.empty:
        return jsonify({"error": f"No price data for {ticker}."}), 400
    mae = backtest_mae(s, k_days=k, method=method, lookback=120)
    return jsonify({"ticker": ticker, "k": k, "method": method, "mae": None if mae is None else round(mae, 2)})

@app.post("/predict")
def predict():
    try:
        body = request.get_json(force=True) or {}
        user_input = body.get("input","")
        # Allow method override (non-ML simple variants)
        method = (body.get("method") or "ema_drift").strip()

        ticker = detect_ticker(user_input)
        if not ticker:
            payload = {"error":"Could not detect a valid ticker/company from input."}
            sug = _suggest_payload(user_input)
            if sug: payload.update(sug)
            return jsonify(payload), 400

        closes = fetch_closes(ticker)
        if closes is None or closes.empty:
            return jsonify({"error": f"No price data for {ticker}."}), 400

        n, unit = parse_period(user_input)
        if n is None or unit is None:
            last_close = float(closes.iloc[-1])
            
            # Add suggestions even for price-only mode
            sug = _suggest_payload(user_input)
            response_payload = {
                "stock": ticker,
                "lastClose": round(last_close,2),
                "mode": "price_only",
                "message": "No duration detected. Add a timeframe (e.g., 'in 3 days') to get a forecast."
            }
            if sug:
                response_payload.update(sug)
            
            return jsonify(response_payload)

        horizon_days = horizon_to_trading_days(n, unit)
        last_close, forecast, method_used, drift = forecast_with_method(closes, horizon_days, method)
        mae = backtest_mae(closes, k_days=horizon_days, method=method_used, lookback=120)

        # Add suggestions for alternative companies
        sug = _suggest_payload(user_input)
        
        response_payload = {
            "stock": ticker,
            "duration": f"{n} {unit}",
            "lastClose": round(last_close,2),
            "result": round(forecast,2),
            "method": method_used,
            "drift_per_day": round(drift,4),
            "backtest": None if mae is None else {"mae": round(mae,2), "window_days": 120},
            "mode": "forecast"
        }
        
        # Add suggestions to show "Did you mean?" alternatives
        if sug:
            response_payload.update(sug)
        
        return jsonify(response_payload)
    except Exception as e:
        return jsonify({"error": f"server_error: {type(e).__name__}: {e}"}), 500

@app.post("/predict_plus")
def predict_plus():
    """
    TWIN+ deep diagnostics:
    - 12m momentum, 50/200-DMA slope, Donchian-50 breakout
    - HAR-RV annualized vol + position size for 20% vol target
    """
    try:
        body = request.get_json(force=True) or {}
        user_input = body.get("input","")

        ticker = detect_ticker(user_input)
        if not ticker:
            payload = {"error":"Could not detect a valid ticker/company from input."}
            sug = _suggest_payload(user_input)
            if sug: payload.update(sug)
            return jsonify(payload), 400

        closes = fetch_closes(ticker, days_back=400)
        if closes is None or closes.empty:
            return jsonify({"error": f"No price data for {ticker}."}), 400

        n, unit = parse_period(user_input)

        look = min(252, len(closes)-1) if len(closes) > 1 else 1
        # Ensure we get scalar values from Series operations using .values
        current_close = closes.values[-1]
        past_close = closes.values[-look]
        mom_12m = float((current_close / past_close - 1.0)) if look > 0 else 0.0
        slope_50  = dma_slope(closes, 50)
        slope_200 = dma_slope(closes, 200)
        breakout, dc_hi, dc_lo = donchian_breakout(closes, 50)
        allow_long = (mom_12m > 0) and (slope_50 > 0) and (slope_200 >= 0)

        ann_vol = har_rv_forecast(closes)  # 0.22 => 22%
        target_vol = 0.20
        position = float(min(1.0, target_vol / ann_vol)) if (ann_vol and ann_vol > 0) else None

        summary = [
            f"12-month momentum: {mom_12m:+.2%}",
            f"Slope of 50-DMA: {slope_50:+.4f} | 200-DMA: {slope_200:+.4f}",
            f"Donchian-50 breakout: {'YES' if breakout else 'no'} (range {dc_lo:.2f} – {dc_hi:.2f})"
        ]
        if ann_vol:
            summary.append(f"Forecast annualized vol (HAR-RV): {ann_vol:.1%}")
            if position is not None:
                summary.append(f"Position size for 20% vol target: {position:.0%}")
        else:
            summary.append("Not enough data to estimate volatility reliably.")

        decision = ("Uptrend intact — longs allowed." if allow_long
                    else "Trend filters not aligned — reduce risk / avoid new longs.")

        # Light ML forecast if duration present
        forecast_payload = {}
        if n is not None and unit is not None:
            horizon_days = horizon_to_trading_days(n, unit)
            last_close_ml, forecast_ml, ml_method, ml_drift = light_ml_forecast(closes, horizon_days)
            forecast_payload = {
                "lastClose": round(last_close_ml,2),
                "result": round(forecast_ml,2),
                "method": ml_method,
                "drift_per_day": round(ml_drift,4),
            }
        return jsonify({
            "stock": ticker,
            "mode": "twin_plus",
            "duration": f"{n} {unit}" if (n and unit) else None,
            **forecast_payload,
            "diagnostics": {
                "momentum_12m": round(mom_12m,4) if not np.isnan(mom_12m) else 0.0,
                "dma50_slope": round(slope_50,6) if not np.isnan(slope_50) else 0.0,
                "dma200_slope": round(slope_200,6) if not np.isnan(slope_200) else 0.0,
                "donchian50_breakout": bool(breakout),
                "donchian50_hi": round(dc_hi,2) if not np.isnan(dc_hi) else 0.0,
                "donchian50_lo": round(dc_lo,2) if not np.isnan(dc_lo) else 0.0,
                "ann_vol_forecast": None if ann_vol is None else round(ann_vol,4),
                "target_vol": 0.20,
                "position_size": None if position is None else round(position,2),
            },
            "decision": decision,
            "summary": summary,
            "method": forecast_payload.get("method", "twin_plus_v1")
        })
    except Exception as e:
        return jsonify({"error": f"server_error: {type(e).__name__}: {e}"}), 500

@app.post("/predict_star")
def predict_star():
    """
    TWIN* heavy ensemble ML forecast:
    - Blends light ML, linear trend, mean reversion, and EMA drift
    - Weighted averaging for robust predictions
    """
    try:
        body = request.get_json(force=True) or {}
        user_input = body.get("input","")

        ticker = detect_ticker(user_input)
        if not ticker:
            payload = {"error":"Could not detect a valid ticker/company from input."}
            sug = _suggest_payload(user_input)
            if sug: payload.update(sug)
            return jsonify(payload), 400

        closes = fetch_closes(ticker, days_back=400)
        if closes is None or closes.empty:
            return jsonify({"error": f"No price data for {ticker}."}), 400

        n, unit = parse_period(user_input)
        if n is None or unit is None:
            return jsonify({"error": "Please specify a timeframe (e.g., 'in 5 days')"}), 400

        horizon_days = horizon_to_trading_days(n, unit)
        last_close, forecast, method, drift = ensemble_forecast(closes, horizon_days)

        return jsonify({
            "stock": ticker,
            "duration": f"{n} {unit}",
            "lastClose": round(last_close,2),
            "result": round(forecast,2),
            "method": method,
            "drift_per_day": round(drift,4),
            "mode": "twin_star"
        })
    except Exception as e:
        return jsonify({"error": f"server_error: {type(e).__name__}: {e}"}), 500

@app.post("/api/predictions/save")
def save_prediction():
    """
    Save a prediction to the database for the authenticated user.
    Requires Authorization header with Supabase token.
    """
    try:
        if not supabase:
            return jsonify({"error": "Database not available"}), 503
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        user_id = user_response.user.id
        
        data = request.get_json()
        
        # Use the user's token to set auth context for the request
        # Create a new client with auth header
        from supabase import create_client, Client
        user_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Set the auth token for this request
        user_supabase.postgrest.auth(token)
        
        # Prepare prediction data using proper user_id from auth
        prediction_data = {
            'user_id': user_id,
            'stock': data.get('stock'),
            'duration': data.get('duration'),
            'last_close': float(data.get('lastClose', 0)),
            'predicted_price': float(data.get('predictedPrice', 0)),
            'method': data.get('method'),
            'delta': float(data.get('delta', 0)),
            'pct': float(data.get('pct', 0)),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'feedback': None
        }
        
        # Insert into Supabase with authenticated client
        result = user_supabase.table('predictions').insert(prediction_data).execute()
        
        return jsonify({
            "success": True,
            "message": "Prediction saved successfully",
            "data": result.data
        })
    
    except Exception as e:
        print(f"Error saving prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to save prediction: {str(e)}"}), 500

@app.get("/api/predictions/user")
def get_user_predictions():
    """
    Retrieve all predictions for the authenticated user.
    Requires Authorization header with Supabase token.
    """
    try:
        if not supabase:
            return jsonify({"error": "Database not available"}), 503
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        user_id = user_response.user.id
        
        # Use the user's token to set auth context
        from supabase import create_client, Client
        user_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        user_supabase.postgrest.auth(token)
        
        # Fetch predictions from Supabase using authenticated client
        result = user_supabase.table('predictions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .execute()
        
        return jsonify({
            "success": True,
            "predictions": result.data
        })
    
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch predictions: {str(e)}"}), 500

@app.post("/save_feedback")
def save_feedback():
    """
    Save user feedback (yes/no) for prediction accuracy.
    Updates the feedback field in predictions table.
    Also stores in predictions_feedback.json for backwards compatibility.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['predictionId', 'feedback', 'stock']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        
        # Update in Supabase if authenticated
        if supabase and token:
            try:
                user_response = supabase.auth.get_user(token)
                user_id = user_response.user.id
                
                # Use the user's token to set auth context
                from supabase import create_client, Client
                user_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
                user_supabase.postgrest.auth(token)
                
                user_supabase.table('predictions')\
                    .update({'feedback': data['feedback']})\
                    .eq('id', data['predictionId'])\
                    .eq('user_id', user_id)\
                    .execute()
            except Exception as db_error:
                print(f"Database update error: {db_error}")
        
        # Also save to JSON file for backwards compatibility
        feedback_file = 'predictions_feedback.json'
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                feedback_data = json.load(f)
        else:
            feedback_data = []
        
        # Add new feedback entry
        feedback_entry = {
            'predictionId': data['predictionId'],
            'feedback': data['feedback'],
            'stock': data['stock'],
            'duration': data.get('duration', ''),
            'predictedPrice': data.get('predictedPrice', 0),
            'lastClose': data.get('lastClose', 0),
            'method': data.get('method', ''),
            'timestamp': data.get('timestamp', ''),
            'feedbackTimestamp': data.get('feedbackTimestamp', datetime.now().isoformat()),
            'userEmail': data['userEmail']
        }
        
        # Add inaccuracy data if provided (for "no" feedback)
        inaccuracy_data = data.get('inaccuracyData')
        if inaccuracy_data:
            feedback_entry['inaccuracyType'] = inaccuracy_data.get('type', 'percentage')
            feedback_entry['inaccuracyValue'] = inaccuracy_data.get('value', 0)
            feedback_entry['inaccuracyNotes'] = inaccuracy_data.get('notes', '')
        
        feedback_data.append(feedback_entry)
        
        # Save updated feedback data
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": "Feedback saved successfully"
        })
    
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return jsonify({"error": f"Failed to save feedback: {str(e)}"}), 500

@app.delete("/api/predictions/delete/<int:prediction_id>")
def delete_prediction(prediction_id):
    """
    Delete a prediction by ID.
    Requires Authorization header with Supabase token.
    Only allows deleting user's own predictions.
    """
    try:
        if not supabase:
            return jsonify({"error": "Database not available"}), 503
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        user_id = user_response.user.id
        print(f"DELETE request: user_id={user_id}, prediction_id={prediction_id}")
        
        # First, verify the prediction belongs to this user
        check_result = supabase.table('predictions')\
            .select('user_id')\
            .eq('id', prediction_id)\
            .execute()
        
        print(f"Check result: {check_result.data}")
        
        if not check_result.data or len(check_result.data) == 0:
            print(f"Prediction not found")
            return jsonify({"error": "Prediction not found"}), 404
        
        pred_owner = check_result.data[0]['user_id']
        print(f"Prediction owner: {pred_owner}, Requesting user: {user_id}")
        
        if pred_owner != user_id:
            print(f"Unauthorized delete attempt!")
            return jsonify({"error": "Unauthorized to delete this prediction"}), 403
        
        # Use the user's token to set auth context
        from supabase import create_client, Client
        user_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        user_supabase.postgrest.auth(token)
        
        # Delete prediction (verified ownership above)
        result = user_supabase.table('predictions')\
            .delete()\
            .eq('id', prediction_id)\
            .execute()
        
        return jsonify({
            "success": True,
            "message": "Prediction deleted successfully"
        })
    
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.delete("/api/predictions/clear")
def clear_all_predictions():
    """Clear all predictions for the authenticated user"""
    try:
        if not supabase:
            return jsonify({"error": "Database not available"}), 503
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else None
        
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        user_id = user_response.user.id
        print(f"Clearing all predictions for user: {user_id}")
        
        # Use the user's token to set auth context
        from supabase import create_client, Client
        user_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        user_supabase.postgrest.auth(token)
        
        # First get all prediction IDs for this user
        fetch_result = user_supabase.table('predictions')\
            .select('id')\
            .eq('user_id', user_id)\
            .execute()
        
        if not fetch_result.data or len(fetch_result.data) == 0:
            # No predictions to delete
            return jsonify({
                "success": True,
                "message": "No predictions to clear"
            })
        
        # Delete all predictions using a single delete with user_id filter
        # Note: Supabase requires neq('*', '*') to delete multiple rows
        delete_result = user_supabase.table('predictions')\
            .delete()\
            .eq('user_id', user_id)\
            .neq('id', 0)\
            .execute()
        
        print(f"Deleted {len(fetch_result.data)} predictions")
        
        return jsonify({
            "success": True,
            "message": f"Cleared {len(fetch_result.data)} predictions successfully"
        })
    
    except Exception as e:
        print(f"Error clearing predictions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to clear predictions: {str(e)}"}), 500

# Catch-all route for static files - MUST be last so API routes aren't intercepted
@app.get("/<path:filename>")
def static_files(filename):
    """Serve static files (HTML, CSS, JS)"""
    response = send_from_directory('.', filename)
    # Add no-cache headers for HTML, CSS, and JS files during development
    if filename.endswith('.html') or filename.endswith(('.css', '.js')):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

if __name__ == "__main__":
    print("TWIN/TWIN+/TWIN* server active")
    
    # Debug: Print all registered routes
    print("\\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint:30} {rule.rule}")
    print()
    
    # Use environment variables for production
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") != "production"
    
    # Disable reloader to avoid import issues
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)




