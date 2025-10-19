# app.py
from __future__ import annotations
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import re
import requests
import yfinance as yf
import pandas as pd
import numpy as np

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
    No hard-coded aliases. Prioritizes EQUITY on US exchanges whose name overlaps the query tokens.
    Avoids single-letter fallbacks unless explicitly typed by the user.
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
    """Honor explicit uppercase tickers first; else resolve via Yahoo name search."""
    if not user_text:
        return None
    # 1) explicit ticker typed by the user (e.g., "AAPL", "$MSFT")
    for m in SYMBOL_RE.finditer(user_text):
        raw = m.group(0)
        sym = raw[1:] if raw.startswith("$") else raw
        # only accept explicit tokens that are 2-5 chars OR exactly what user typed (incl. 1-char)
        if sym.isupper() and validate_ticker(sym) and (2 <= len(sym) <= 5 or raw == sym or raw == f"${sym}"):
            return sym
        

    # 2) fallback: name search (with duration stripped)
    sym = yahoo_search_company_to_symbol(user_text)
    if sym and validate_ticker(sym):
        return sym
    return None

# ------- suggestions for "did you mean?" -------------------------------------
def suggestion_candidates(user_text: str, limit: int = 3):
    """
    Return up to `limit` suggestions as (symbol, display_name).
    """
    q_raw = strip_duration_phrases(user_text or "").strip()
    q = (extract_company_query(q_raw) or q_raw).strip()
    quotes = _yahoo_search(q)
    if not quotes:
        return []

    out = []
    for it in quotes:
        sym = (it.get("symbol") or "").upper()
        name = it.get("shortname") or it.get("longname") or sym
        qtype = it.get("quoteType")
        region = it.get("region")
        exch = it.get("exchange")
        if not sym or len(sym) > 5:   # equity-like symbols
            continue
        if qtype not in (None, "EQUITY", "ETF", "INDEX", "MUTUALFUND"):
            continue
        # prefer US listings
        score = 0
        if region == "US" or exch in {"NMS","NYQ","ASE","NMS2"}:
            score -= 1
        out.append((score, sym, name))
    out.sort(key=lambda t: (t[0], len(t[2])))
    uniq, seen = [], set()
    for _, sym, name in out:
        if sym in seen:
            continue
        uniq.append((sym, name))
        seen.add(sym)
        if len(uniq) >= limit:
            break
    return uniq

def echo_with_duration(name_or_symbol: str, original: str) -> str:
    """Build echo like 'Apple in 2 days' reusing the user's duration."""
    n, unit = parse_period(original)
    if n is None or unit is None:
        return name_or_symbol
    return f"{name_or_symbol} in {n} {unit}"

def _suggest_payload(user_input: str):
    cands = suggestion_candidates(user_input, limit=3)
    if not cands:
        return None
    suggestions = []
    for sym, name in cands:
        display = (name or sym).split(" (")[0]
        suggestions.append({
            "symbol": sym,
            "name": display,
            "echo": echo_with_duration(display.split(",")[0], user_input)
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

def forecast_with_method(series: pd.Series, horizon_days: int, method: str = "ema_drift"):
    last_close = float(series.iloc[-1])
    if method == "ema_drift":
        drift = ema_drift(series, span=6)
    elif method == "linear_trend":
        drift = linear_trend_drift(series, window=20)
    elif method == "baseline_drift":
        drift = baseline_drift(series)
    else:
        drift = ema_drift(series, span=6); method = "ema_drift"
    forecast = last_close + drift * max(horizon_days, 0)
    return last_close, forecast, method, drift

def backtest_mae(series: pd.Series, k_days: int, method: str = "ema_drift", lookback: int = 120) -> float | None:
    s = series.tail(lookback + 30)
    if len(s) < k_days + 10:
        return None
    preds, actuals = [], []
    for i in range(10, len(s) - k_days):
        hist = s.iloc[:i]
        if method == "ema_drift":
            d = ema_drift(hist, span=6)
        elif method == "linear_trend":
            d = linear_trend_drift(hist, window=min(20, len(hist)))
        else:
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
    hi = series.rolling(n).max(); lo = series.rolling(n).min()
    return float(series.iloc[-1] >= hi.iloc[-1]), float(hi.iloc[-1]), float(lo.iloc[-1])

def dma_slope(series, n):
    m = sma(series, n).dropna()
    if len(m) < 5: return 0.0
    return float(m.tail(5).diff().mean())

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

# --------------------------------- routes ------------------------------------
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

# helper for debugging name->ticker
@app.get("/lookup")
def lookup():
    q = request.args.get("query","")
    sym = yahoo_search_company_to_symbol(q)
    valid = validate_ticker(sym) if sym else False
    return jsonify({"query": q, "symbol": sym, "valid": bool(valid)})

@app.post("/predict")
def predict():
    try:
        body = request.get_json(force=True) or {}
        user_input = body.get("input","")
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
            return jsonify({
                "stock": ticker,
                "lastClose": round(last_close,2),
                "mode": "price_only",
                "message": "No duration detected. Add a timeframe (e.g., 'in 3 days') to get a forecast."
            })

        horizon_days = horizon_to_trading_days(n, unit)
        last_close, forecast, method_used, drift = forecast_with_method(closes, horizon_days, method)
        mae = backtest_mae(closes, k_days=horizon_days, method=method_used, lookback=120)

        return jsonify({
            "stock": ticker,
            "duration": f"{n} {unit}",
            "lastClose": round(last_close,2),
            "result": round(forecast,2),
            "method": method_used,
            "drift_per_day": round(drift,4),
            "backtest": None if mae is None else {"mae": round(mae,2), "window_days": 120},
            "mode": "forecast"
        })
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
        mom_12m = float((closes.iloc[-1] / closes.iloc[-look] - 1.0)) if look > 0 else 0.0
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

        return jsonify({
            "stock": ticker,
            "mode": "twin_plus",
            "duration": f"{n} {unit}" if (n and unit) else None,
            "diagnostics": {
                "momentum_12m": round(mom_12m,4),
                "dma50_slope": round(slope_50,6),
                "dma200_slope": round(slope_200,6),
                "donchian50_breakout": bool(breakout),
                "donchian50_hi": round(dc_hi,2),
                "donchian50_lo": round(dc_lo,2),
                "ann_vol_forecast": None if ann_vol is None else round(ann_vol,4),
                "target_vol": 0.20,
                "position_size": None if position is None else round(position,2),
            },
            "decision": decision,
            "summary": summary,
            "method": "twin_plus_v1"
        })
    except Exception as e:
        return jsonify({"error": f"server_error: {type(e).__name__}: {e}"}), 500

if __name__ == "__main__":
    print("TWIN/TWIN+ server active")
    app.run(debug=True, port=5000)
