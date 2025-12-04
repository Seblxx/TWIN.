"""
TWIN - Comprehensive Test Suite
Runs all tests for the TWIN Stock Assistant application
"""

import sys
import traceback
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_test(name, passed, details=""):
    status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if passed else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
    print(f"{status} | {name}")
    if details:
        print(f"       {details}")

def print_section(text):
    print(f"\n{Colors.OKCYAN}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{'-'*70}{Colors.ENDC}")

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

print_header("🧪 TWIN - Comprehensive Test Suite")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# TEST 1: Import and Dependency Checks
# ============================================================================
print_section("1. Checking Dependencies and Imports")

dependencies = [
    ('flask', 'Flask'),
    ('flask_cors', 'Flask-CORS'),
    ('yfinance', 'yfinance'),
    ('pandas', 'pandas'),
    ('numpy', 'numpy'),
    ('rapidfuzz', 'rapidfuzz'),
    ('requests', 'requests'),
    ('sklearn', 'scikit-learn'),
]

for module_name, display_name in dependencies:
    total_tests += 1
    try:
        __import__(module_name)
        print_test(f"Import {display_name}", True)
        passed_tests += 1
    except ImportError as e:
        print_test(f"Import {display_name}", False, str(e))
        failed_tests += 1

# ============================================================================
# TEST 2: App Module Import and Configuration
# ============================================================================
print_section("2. Testing App Module")

total_tests += 1
try:
    import app
    print_test("Import app.py", True)
    passed_tests += 1
except Exception as e:
    print_test("Import app.py", False, str(e))
    failed_tests += 1

total_tests += 1
try:
    from app import detect_ticker, parse_period, fetch_closes
    print_test("Import core functions", True)
    passed_tests += 1
except Exception as e:
    print_test("Import core functions", False, str(e))
    failed_tests += 1

# ============================================================================
# TEST 3: Fuzzy Matching Tests
# ============================================================================
print_section("3. Testing Fuzzy Matching (rapidfuzz)")

from rapidfuzz import fuzz

fuzzy_tests = [
    ('MICROSFT', 'MSFT', 'symbol', 60),
    ('MICROSFT', 'MICROSOFT CORPORATION', 'name', 80),
    ('TESLLA', 'TSLA', 'symbol', 60),
    ('TESLLA', 'TESLA, INC.', 'name', 60),
    ('GOGLE', 'GOOGL', 'symbol', 60),
    ('APPL', 'AAPL', 'symbol', 60),
]

for query, target, match_type, min_score in fuzzy_tests:
    total_tests += 1
    ratio_score = fuzz.ratio(query, target)
    token_score = fuzz.token_set_ratio(query, target)
    best_score = max(ratio_score, token_score)
    passed = best_score >= min_score
    
    print_test(
        f"Fuzzy match: '{query}' → '{target}' ({match_type})",
        passed,
        f"Score: {best_score:.1f}% (min: {min_score}%)"
    )
    
    if passed:
        passed_tests += 1
    else:
        failed_tests += 1

# ============================================================================
# TEST 4: Duration Parsing Tests
# ============================================================================
print_section("4. Testing Duration Parsing")

from app import parse_period

duration_tests = [
    ('Apple in 3 days', (3, 'days')),
    ('Tesla in 2 weeks', (2, 'weeks')),
    ('MSFT next month', (1, 'months')),
    ('GOOGL next week', (1, 'weeks')),
    ('NVDA tomorrow', (1, 'days')),
    ('AMD today', (0, 'days')),
    ('Apple', (None, None)),
]

for text, expected in duration_tests:
    total_tests += 1
    result = parse_period(text)
    passed = result == expected
    
    print_test(
        f"Parse: '{text}'",
        passed,
        f"Expected: {expected}, Got: {result}"
    )
    
    if passed:
        passed_tests += 1
    else:
        failed_tests += 1

# ============================================================================
# TEST 5: Ticker Detection Tests (if possible without API calls)
# ============================================================================
print_section("5. Testing Ticker Detection")

from app import SYMBOL_RE

symbol_tests = [
    ('AAPL', True, 'AAPL'),
    ('Buy TSLA stock', True, 'TSLA'),
    ('Check $MSFT', True, 'MSFT'),
    ('GOOGL in 3 days', True, 'GOOGL'),
    ('apple', False, None),  # lowercase, won't match explicit regex
]

for text, should_match, expected_symbol in symbol_tests:
    total_tests += 1
    matches = SYMBOL_RE.finditer(text)
    found_symbols = [m.group(0).lstrip('$') for m in matches if m.group(0).isupper()]
    
    if should_match:
        passed = len(found_symbols) > 0 and (expected_symbol is None or expected_symbol in found_symbols)
        result = found_symbols[0] if found_symbols else "None"
    else:
        passed = len(found_symbols) == 0
        result = "None"
    
    print_test(
        f"Symbol detection: '{text}'",
        passed,
        f"Expected: {expected_symbol}, Got: {result}"
    )
    
    if passed:
        passed_tests += 1
    else:
        failed_tests += 1

# ============================================================================
# TEST 6: Flask App Configuration Tests
# ============================================================================
print_section("6. Testing Flask App Configuration")

total_tests += 1
try:
    from app import app as flask_app
    has_cors = 'cors' in dir(flask_app)
    print_test("Flask app has CORS enabled", has_cors)
    if has_cors:
        passed_tests += 1
    else:
        failed_tests += 1
except Exception as e:
    print_test("Flask app CORS check", False, str(e))
    failed_tests += 1

# ============================================================================
# TEST 7: Yahoo Finance API Tests (Light)
# ============================================================================
print_section("7. Testing Yahoo Finance API (Sample)")

yahoo_test_queries = ['apple', 'microsoft', 'tesla']

for query in yahoo_test_queries[:2]:  # Test only 2 to avoid rate limits
    total_tests += 1
    try:
        import requests
        r = requests.get(
            'https://query2.finance.yahoo.com/v1/finance/search',
            params={'q': query, 'quotesCount': 3},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=5
        )
        quotes = r.json().get('quotes', [])
        passed = len(quotes) > 0
        
        if passed:
            top_result = f"{quotes[0].get('symbol')} - {quotes[0].get('shortname', 'N/A')[:30]}"
            print_test(f"Yahoo API search: '{query}'", True, f"Found: {top_result}")
            passed_tests += 1
        else:
            print_test(f"Yahoo API search: '{query}'", False, "No results")
            failed_tests += 1
    except Exception as e:
        print_test(f"Yahoo API search: '{query}'", False, str(e))
        failed_tests += 1

# ============================================================================
# TEST 8: File Structure Tests
# ============================================================================
print_section("8. Testing File Structure")

import os

required_files = [
    'app.py',
    'index.html',
    'intro.html',
    'script.js',
    'theme-toggle.js',
    'requirements.txt',
    'Procfile',
    'render.yaml',
    'royal.css',
    'dark.css',
    'light.css',
    'monochrome.css',
    'liquidglass.css',
]

for filename in required_files:
    total_tests += 1
    exists = os.path.exists(filename)
    print_test(f"File exists: {filename}", exists)
    
    if exists:
        passed_tests += 1
    else:
        failed_tests += 1

# ============================================================================
# TEST 9: Combined Scoring Algorithm Test
# ============================================================================
print_section("9. Testing Combined Scoring Algorithm")

combined_tests = [
    ("MICROSFT", "MSFT", "MICROSOFT CORPORATION", 70),  # Should score high
    ("TESLLA", "TSLA", "TESLA, INC.", 70),  # Should score high
    ("GOGLE", "GOOGL", "ALPHABET INC.", 60),  # Should score decent
]

for query, symbol, name, min_combined_score in combined_tests:
    total_tests += 1
    
    symbol_score = fuzz.ratio(query, symbol)
    name_score = fuzz.token_set_ratio(query, name)
    
    # Use the same weighting logic as in app.py
    if len(query) <= 4:
        combined = 0.80 * symbol_score + 0.20 * name_score
    else:
        combined = 0.30 * symbol_score + 0.70 * name_score
    
    passed = combined >= min_combined_score
    
    print_test(
        f"Combined scoring: '{query}' → {symbol}",
        passed,
        f"Score: {combined:.1f}% (Symbol: {symbol_score:.1f}%, Name: {name_score:.1f}%)"
    )
    
    if passed:
        passed_tests += 1
    else:
        failed_tests += 1

# ============================================================================
# FINAL RESULTS
# ============================================================================
print_header("📊 Test Results Summary")

pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests:  {total_tests}")
print(f"{Colors.OKGREEN}Passed:       {passed_tests}{Colors.ENDC}")
print(f"{Colors.FAIL}Failed:       {failed_tests}{Colors.ENDC}")
print(f"\nPass Rate:    {pass_rate:.1f}%")

if failed_tests == 0:
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed! Your app is ready!{Colors.ENDC}")
    sys.exit(0)
elif pass_rate >= 80:
    print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  Most tests passed, but some issues need attention.{Colors.ENDC}")
    sys.exit(1)
else:
    print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Several tests failed. Please review the issues above.{Colors.ENDC}")
    sys.exit(1)
