# TWIN API - Complete Postman & cURL Testing Guide

## 📦 Postman Collection

Import `TWIN_API.postman_collection.json` into Postman to get all pre-configured requests.

### How to Import:
1. Open Postman
2. Click **Import** button (top left)
3. Select `TWIN_API.postman_collection.json`
4. Collection appears in your sidebar

### Environment Variable:
- `base_url` = `http://localhost:5000` (change for production)

---

## 🔍 Fuzzy Matching Tests

### Test 1: Exact Match
**cURL:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "apple in 4 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"input": "apple in 4 days"}' | ConvertTo-Json -Depth 10
```

**Expected:** `"stock": "AAPL"` with forecast

---

### Test 2: Typo - "aple" (88.9% match)
**cURL:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "aple in 4 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"input": "aple in 4 days"}' | ConvertTo-Json -Depth 10
```

**Expected:** Still matches `"stock": "AAPL"` ✅

---

### Test 3: Typo - "microsft" (94.1% match)
**cURL:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "microsft in 3 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"input": "microsft in 3 days"}' | ConvertTo-Json -Depth 10
```

**Expected:** Matches `"stock": "MSFT"` ✅

---

### Test 4: Abbreviated - "tsl" (75% match)
**cURL:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "tsl in 5 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"input": "tsl in 5 days"}' | ConvertTo-Json -Depth 10
```

**Expected:** Matches `"stock": "TSLA"` ✅

---

### Test 5: Multi-word Company - "jp morgan"
**cURL:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "jp morgan in 5 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"input": "jp morgan in 5 days"}' | ConvertTo-Json -Depth 10
```

**Expected:** Matches `"stock": "JPM"` ✅

---

### Test 6: Partial Word - "coke"
**cURL:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "coke in 3 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"input": "coke in 3 days"}' | ConvertTo-Json -Depth 10
```

**Expected:** Should suggest Coca-Cola or close matches

---

### Test 7: Invalid Input - Always Get 3 Suggestions
**cURL:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "blahblah in 2 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"input": "blahblah in 2 days"}' | ConvertTo-Json -Depth 10
```

**Expected:** 
```json
{
  "error": "Could not detect a valid ticker/company from input.",
  "suggestions": [
    {"symbol": "BALL", "name": "Ball", "echo": "BALL in 2 days"},
    {"symbol": "AA", "name": "Alcoa", "echo": "AA in 2 days"},
    {"symbol": "ECL", "name": "Ecolab", "echo": "ECL in 2 days"}
  ]
}
```
**Status:** 400 (but includes suggestions - never empty) ✅

---

### Test 8: Explicit Ticker - "$TSLA"
**cURL:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "$TSLA in 5 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"input": "$TSLA in 5 days"}' | ConvertTo-Json -Depth 10
```

**Expected:** Exact match `"stock": "TSLA"` ✅

---

## 🧪 TWIN+ Diagnostics Tests

### Test 9: Tesla Full Diagnostics
**cURL:**
```bash
curl -X POST http://localhost:5000/predict_plus \
  -H "Content-Type: application/json" \
  -d '{"input": "tesla in 10 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict_plus" -Method Post -ContentType "application/json" -Body '{"input": "tesla in 10 days"}' | ConvertTo-Json -Depth 10
```

**Expected:**
```json
{
  "stock": "TSLA",
  "mode": "twin_plus",
  "diagnostics": {
    "momentum_12m": 0.2599,
    "dma50_slope": 0.0,
    "dma200_slope": 0.0,
    "donchian50_breakout": false,
    "ann_vol_forecast": 0.4638,
    "position_size": 0.43
  },
  "decision": "Trend filters not aligned — reduce risk...",
  "summary": [...]
}
```

---

### Test 10: Apple Diagnostics
**cURL:**
```bash
curl -X POST http://localhost:5000/predict_plus \
  -H "Content-Type: application/json" \
  -d '{"input": "apple in 5 days"}'
```

---

## 🎯 TWIN* Ensemble Tests

### Test 11: Microsoft Ensemble Forecast
**cURL:**
```bash
curl -X POST http://localhost:5000/predict_star \
  -H "Content-Type: application/json" \
  -d '{"input": "microsoft in 7 days"}'
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict_star" -Method Post -ContentType "application/json" -Body '{"input": "microsoft in 7 days"}' | ConvertTo-Json -Depth 10
```

**Expected:**
```json
{
  "stock": "MSFT",
  "duration": "7 days",
  "lastClose": 485.50,
  "result": 494.50,
  "method": "ensemble_v1",
  "mode": "twin_star"
}
```

---

### Test 12: Amazon Long-term Ensemble
**cURL:**
```bash
curl -X POST http://localhost:5000/predict_star \
  -H "Content-Type: application/json" \
  -d '{"input": "amazon in 14 days"}'
```

---

## 📊 Historical Data Tests

### Test 13: Get AAPL 90-Day History
**cURL:**
```bash
curl "http://localhost:5000/history?ticker=AAPL&days=90"
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/history?ticker=AAPL&days=90"
```

**Expected:**
```json
{
  "ticker": "AAPL",
  "closes": [245.67, 247.23, 248.91, ...]
}
```

---

### Test 14: Get TSLA 180-Day History
**cURL:**
```bash
curl "http://localhost:5000/history?ticker=TSLA&days=180"
```

---

## 🔬 Backtest Tests

### Test 15: Backtest AAPL with EMA Drift
**cURL:**
```bash
curl "http://localhost:5000/backtest?ticker=AAPL&k=3&method=ema_drift"
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/backtest?ticker=AAPL&k=3&method=ema_drift"
```

**Expected:**
```json
{
  "ticker": "AAPL",
  "k": 3,
  "method": "ema_drift",
  "mae": 7.88
}
```

---

### Test 16: Backtest MSFT with Linear Trend
**cURL:**
```bash
curl "http://localhost:5000/backtest?ticker=MSFT&k=5&method=linear_trend"
```

---

## ✅ Health Check

**cURL:**
```bash
curl http://localhost:5000/health
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health"
```

**Expected:**
```json
{
  "ok": true,
  "time": "2025-11-27T03:13:13.442321"
}
```

---

## 🔄 Time Variations to Test

Try these different time formats:

```bash
# Tomorrow
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"input": "apple tomorrow"}'

# Next week
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"input": "microsoft next week"}'

# Multiple days
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"input": "tesla in 7 days"}'

# Month
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"input": "nvidia in 1 month"}'
```

---

## 🎨 Pretty Print JSON (cURL)

Add `| jq` for formatted output (requires jq installed):

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "apple in 4 days"}' | jq
```

Or use Python:
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "apple in 4 days"}' | python -m json.tool
```

---

## 📝 Test Checklist

- [ ] Health check returns OK
- [ ] Exact company names work (apple, microsoft, tesla)
- [ ] Typos are corrected (aple → AAPL, microsft → MSFT)
- [ ] Abbreviated names work (tsl → TSLA)
- [ ] Multi-word companies work (jp morgan → JPM)
- [ ] Explicit tickers work ($AAPL, $TSLA)
- [ ] Invalid input returns 3 suggestions
- [ ] TWIN+ diagnostics include momentum, volatility, position size
- [ ] TWIN* ensemble returns blended forecast
- [ ] Historical data returns price arrays
- [ ] Backtests return MAE metrics
- [ ] All responses are JSON formatted
- [ ] Response times < 5 seconds

---

## 🚀 Quick Test Script (Bash)

```bash
#!/bin/bash
BASE_URL="http://localhost:5000"

echo "Testing TWIN Fuzzy Matching API..."

# Test 1: Health
echo -e "\n1. Health Check"
curl -s $BASE_URL/health | python -m json.tool

# Test 2: Exact match
echo -e "\n2. Exact Match - Apple"
curl -s -X POST $BASE_URL/predict -H "Content-Type: application/json" -d '{"input": "apple in 4 days"}' | python -m json.tool

# Test 3: Typo
echo -e "\n3. Typo Test - aple"
curl -s -X POST $BASE_URL/predict -H "Content-Type: application/json" -d '{"input": "aple in 4 days"}' | python -m json.tool

# Test 4: Suggestions
echo -e "\n4. Invalid Input - Get Suggestions"
curl -s -X POST $BASE_URL/predict -H "Content-Type: application/json" -d '{"input": "blahblah in 2 days"}' | python -m json.tool

echo -e "\n✅ Tests complete!"
```

---

## 📈 Expected Performance

| Test Type | Expected Response Time | Status Code |
|-----------|----------------------|-------------|
| Health Check | < 50ms | 200 |
| Fuzzy Match (hit) | < 3s | 200 |
| Fuzzy Match (suggestions) | < 1s | 400 |
| TWIN+ Diagnostics | < 5s | 200 |
| TWIN* Ensemble | < 8s | 200 |
| Historical Data | < 2s | 200 |
| Backtest | < 10s | 200 |
