# 🎯 TWIN Fuzzy Matching - Quick Reference

## 📍 Test File Locations

### Fuzzy Matching Tests
1. **`test_fuzzy_comprehensive.py`** ⭐ **MAIN FUZZY TEST FILE**
   - 8 test suites covering all fuzzy matching scenarios
   - 63 total tests (98.4% pass rate)
   - Run: `python test_fuzzy_comprehensive.py`

2. **`test_revert.py`**
   - Basic fuzzy matching tests
   - 10 unit tests for core functionality
   - Run: `python test_revert.py`

### API Integration Tests
3. **`test_api_curl.py`**
   - Full API endpoint testing
   - 8 comprehensive integration tests
   - Run: `python test_api_curl.py` (requires server running)

### Manual Testing Resources
4. **`POSTMAN_CURL_GUIDE.md`** ⭐ **COMPLETE CURL/POSTMAN GUIDE**
   - 16+ curl examples
   - PowerShell equivalents
   - Expected responses
   - Quick test scripts

5. **`TWIN_API.postman_collection.json`**
   - Import into Postman
   - Pre-configured requests
   - Organized by feature

6. **`CURL_TESTS.md`**
   - Quick curl commands
   - Basic test examples

---

## 🚀 Quick Start Testing

### 1. Run Fuzzy Matching Tests (No Server Needed)
```bash
python test_fuzzy_comprehensive.py
```

**Tests:**
- ✅ Exact matches (apple → AAPL)
- ✅ Typos (aple → AAPL, microsft → MSFT)
- ✅ Abbreviations (tsl → TSLA)
- ✅ Multi-word (jp morgan → JPM)
- ✅ Case insensitivity
- ✅ Suggestions always appear
- ✅ Confidence scores

---

### 2. Run API Tests (Requires Server)
```bash
# Terminal 1: Start server
python app.py

# Terminal 2: Run tests
python test_api_curl.py
```

---

### 3. Manual curl Testing
```bash
# Test typo correction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "aple in 4 days"}'

# Test suggestions
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "blahblah in 2 days"}'
```

---

## 📊 Test Coverage

### Fuzzy Matching (test_fuzzy_comprehensive.py)
| Test Suite | Tests | Pass Rate | What It Tests |
|------------|-------|-----------|---------------|
| Exact Matches | 15 | 100% | Perfect company name matches |
| Typo Correction | 15 | 100% | Missing/swapped letters |
| Abbreviations | 6 | 100% | Short forms (tsl → TSLA) |
| Multi-Word | 12 | 92% | Companies with spaces |
| Suggestions | 7 | 100% | Always return 3 suggestions |
| Case Insensitivity | 8 | 100% | APPLE = apple = Apple |
| **TOTAL** | **63** | **98.4%** | **Comprehensive fuzzy matching** |

### API Integration (test_api_curl.py)
| Test | Endpoint | Status |
|------|----------|--------|
| Health Check | GET /health | ✅ |
| Exact Match | POST /predict | ✅ |
| Typo Match | POST /predict | ✅ |
| Another Typo | POST /predict | ✅ |
| Suggestions | POST /predict | ✅ |
| Explicit Ticker | POST /predict | ✅ |
| TWIN+ Diagnostics | POST /predict_plus | ✅ |
| TWIN* Ensemble | POST /predict_star | ✅ |

---

## 🔍 Fuzzy Matching Examples

### Exact Matches (100% confidence)
```
"apple" → AAPL
"microsoft" → MSFT
"google" → GOOGL
"tesla" → TSLA
```

### Typos (80-95% confidence)
```
"aple" → AAPL (88.9%)
"microsft" → MSFT (94.1%)
"gogle" → GOOGL (90.9%)
"tesls" → TSLA (80.0%)
```

### Abbreviations (70-80% confidence)
```
"tsl" → TSLA (75.0%)
"amzn" → AMZN (80.0%)
"nflx" → NFLX (72.7%)
```

### Multi-Word (77-100% confidence)
```
"jp morgan" → JPM (94.1%)
"coca cola" → KO (100.0%)
"bank of america" → BAC (100.0%)
"goldman sachs" → GS (100.0%)
```

---

## 📝 PowerShell Quick Tests

### Test Exact Match
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"input": "apple in 4 days"}' | ConvertTo-Json -Depth 10
```

### Test Typo Correction
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"input": "aple in 4 days"}' | ConvertTo-Json -Depth 10
```

### Test Suggestions
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"input": "blahblah in 2 days"}' | ConvertTo-Json -Depth 10
```

---

## 🎨 Expected Behavior

### ✅ Successful Match (Status 200)
```json
{
  "stock": "AAPL",
  "duration": "4 days",
  "lastClose": 277.55,
  "result": 282.88,
  "method": "ema_drift",
  "mode": "forecast"
}
```

### ⚠️ No Match - Get Suggestions (Status 400)
```json
{
  "error": "Could not detect a valid ticker/company from input.",
  "suggestions": [
    {"symbol": "AAPL", "name": "Apple", "echo": "AAPL in 2 days"},
    {"symbol": "MSFT", "name": "Microsoft", "echo": "MSFT in 2 days"},
    {"symbol": "GOOGL", "name": "Alphabet", "echo": "GOOGL in 2 days"}
  ]
}
```

---

## 🏆 Test Results Summary

**All Tests: 71 total**
- Fuzzy Matching: 63 tests (98.4% pass)
- API Integration: 8 tests (100% pass)

**Key Features Verified:**
- ✅ 276 companies supported
- ✅ Typo correction (88-94% accuracy)
- ✅ Always provides 3 suggestions
- ✅ No "Could not detect" errors without suggestions
- ✅ Fast response times (< 3 seconds)
- ✅ Works offline (no API dependencies)

---

## 📚 Documentation Files

1. **POSTMAN_CURL_GUIDE.md** - Complete curl/Postman guide with 16+ examples
2. **CURL_TESTS.md** - Quick curl command reference
3. **TEST_RESULTS.md** - Full test results documentation
4. **REVERT_CHANGES.md** - What changed from Yahoo Finance to fuzzy matching
5. **TWIN_API.postman_collection.json** - Postman collection for import

---

## 🔧 Troubleshooting

### Server Not Running
```bash
# Start server
python app.py

# Check if running
curl http://localhost:5000/health
```

### Import Errors
```bash
# Install dependencies
pip install -r requirements.txt

# Verify companies.py exists
python -c "from companies import COMPANY_TICKER_MAP; print(len(COMPANY_TICKER_MAP))"
```

### Test Failures
```bash
# Run verbose tests
python test_fuzzy_comprehensive.py

# Check specific API endpoint
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"input": "apple in 4 days"}' | python -m json.tool
```

---

## ✨ Best Practices

1. **Run fuzzy tests first** (no server needed)
2. **Then run API tests** (requires server)
3. **Use Postman** for manual exploratory testing
4. **Use curl** for quick command-line verification
5. **Check TEST_RESULTS.md** for expected behaviors
