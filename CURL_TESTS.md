# TWIN API - CURL Test Commands

## Health Check
```bash
curl http://localhost:5000/health
```

## Basic Predictions (TWIN-)

### Exact Match
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"apple in 4 days\"}"
```

### Fuzzy Match - Typo "aple"
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"aple in 4 days\"}"
```

### Fuzzy Match - Typo "microsft"
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"microsft in 3 days\"}"
```

### Unclear Input - Should Get Suggestions
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"blahblah in 2 days\"}"
```

### Explicit Ticker
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"\$TSLA in 5 days\"}"
```

## TWIN+ Diagnostics

### Tesla with Diagnostics
```bash
curl -X POST http://localhost:5000/predict_plus \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"tesla in 10 days\"}"
```

### Apple with Diagnostics
```bash
curl -X POST http://localhost:5000/predict_plus \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"apple in 5 days\"}"
```

## TWIN* Ensemble

### Microsoft Ensemble Forecast
```bash
curl -X POST http://localhost:5000/predict_star \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"microsoft in 7 days\"}"
```

### Amazon Ensemble Forecast
```bash
curl -X POST http://localhost:5000/predict_star \
  -H "Content-Type: application/json" \
  -d "{\"input\": \"amazon in 14 days\"}"
```

## Other Endpoints

### Get Historical Data
```bash
curl "http://localhost:5000/history?ticker=AAPL&days=90"
```

### Backtest a Method
```bash
curl "http://localhost:5000/backtest?ticker=AAPL&k=3&method=ema_drift"
```

## PowerShell Equivalents

If using PowerShell instead of curl:

### Basic Prediction
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"input": "apple in 4 days"}'
```

### Fuzzy Match
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"input": "aple in 4 days"}'
```

### TWIN+ Diagnostics
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict_plus" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"input": "tesla in 10 days"}'
```

## Expected Behaviors

✅ **Fuzzy Matching Works**: Typos like "aple", "microsft", "tsl" match correctly
✅ **Always Get Suggestions**: Invalid input returns 3 company suggestions
✅ **No "Could not detect" Errors**: System always provides either prediction or suggestions
✅ **Fast Response**: No slow Yahoo Finance API calls
✅ **276 Companies**: Large hardcoded list covers major stocks

## Test Results Summary

All 8 tests passed:
1. ✅ Health check
2. ✅ Exact match (apple → AAPL)
3. ✅ Fuzzy match typo (aple → AAPL)
4. ✅ Another fuzzy typo (microsft → MSFT)
5. ✅ Suggestions for unclear input (always 3 suggestions)
6. ✅ Explicit ticker ($TSLA → TSLA)
7. ✅ TWIN+ diagnostics
8. ✅ TWIN* ensemble
