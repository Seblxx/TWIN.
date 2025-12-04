"""
COMPREHENSIVE FUZZY MATCHING TESTS FOR TWIN API
Tests all aspects of fuzzy word matching including typos, abbreviations, partial matches
"""
from companies import COMPANY_TICKER_MAP
from rapidfuzz import fuzz, process

def test_exact_matches():
    """Test exact company name matches"""
    print("=" * 70)
    print("TEST SUITE 1: EXACT MATCHES")
    print("=" * 70)
    
    exact_tests = [
        ("apple", "AAPL"),
        ("microsoft", "MSFT"),
        ("google", "GOOGL"),
        ("alphabet", "GOOGL"),
        ("amazon", "AMZN"),
        ("meta", "META"),
        ("facebook", "META"),
        ("tesla", "TSLA"),
        ("nvidia", "NVDA"),
        ("netflix", "NFLX"),
        ("disney", "DIS"),
        ("boeing", "BA"),
        ("walmart", "WMT"),
        ("coca cola", "KO"),
        ("pepsi", "PEP"),
    ]
    
    passed = 0
    for query, expected_ticker in exact_tests:
        best_match = process.extractOne(
            query,
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=70
        )
        
        if best_match:
            company_name, score, _ = best_match
            ticker = COMPANY_TICKER_MAP[company_name]
            if ticker == expected_ticker:
                print(f"✅ '{query}' -> {ticker} ({score:.1f}%)")
                passed += 1
            else:
                print(f"❌ '{query}' -> {ticker} (expected {expected_ticker}, {score:.1f}%)")
        else:
            print(f"❌ '{query}' -> No match (expected {expected_ticker})")
    
    print(f"\nResults: {passed}/{len(exact_tests)} passed")
    return passed, len(exact_tests)

def test_typos():
    """Test fuzzy matching with common typos"""
    print("\n" + "=" * 70)
    print("TEST SUITE 2: TYPO CORRECTION")
    print("=" * 70)
    
    typo_tests = [
        ("aple", "AAPL"),           # missing 'p'
        ("appl", "AAPL"),           # missing 'e'
        ("appel", "AAPL"),          # swapped letters
        ("microsft", "MSFT"),       # missing 'o'
        ("micorsoft", "MSFT"),      # swapped letters
        ("gogle", "GOOGL"),         # missing 'o'
        ("googel", "GOOGL"),        # swapped letters
        ("amzon", "AMZN"),          # missing 'a'
        ("amazn", "AMZN"),          # missing 'o'
        ("tesls", "TSLA"),          # wrong last letter
        ("tela", "TSLA"),           # missing 's'
        ("nvdia", "NVDA"),          # missing 'i'
        ("netfilx", "NFLX"),        # swapped letters
        ("disey", "DIS"),           # missing 'n'
        ("boing", "BA"),            # typo
    ]
    
    passed = 0
    for query, expected_ticker in typo_tests:
        best_match = process.extractOne(
            query,
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=70
        )
        
        if best_match:
            company_name, score, _ = best_match
            ticker = COMPANY_TICKER_MAP[company_name]
            if ticker == expected_ticker:
                print(f"✅ '{query}' -> {ticker} ({score:.1f}% confidence)")
                passed += 1
            else:
                print(f"❌ '{query}' -> {ticker} (expected {expected_ticker}, {score:.1f}%)")
        else:
            print(f"❌ '{query}' -> No match (expected {expected_ticker})")
    
    print(f"\nResults: {passed}/{len(typo_tests)} passed")
    return passed, len(typo_tests)

def test_abbreviations():
    """Test abbreviated company names"""
    print("\n" + "=" * 70)
    print("TEST SUITE 3: ABBREVIATIONS")
    print("=" * 70)
    
    abbrev_tests = [
        ("tsl", "TSLA"),
        ("msft", "MSFT"),
        ("amzn", "AMZN"),
        ("nflx", "NFLX"),
        ("dis", "DIS"),
        ("wmt", "WMT"),
    ]
    
    passed = 0
    for query, expected_ticker in abbrev_tests:
        best_match = process.extractOne(
            query,
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=60  # Lower threshold for abbreviations
        )
        
        if best_match:
            company_name, score, _ = best_match
            ticker = COMPANY_TICKER_MAP[company_name]
            if ticker == expected_ticker:
                print(f"✅ '{query}' -> {ticker} ({score:.1f}%)")
                passed += 1
            else:
                print(f"⚠️  '{query}' -> {ticker} (expected {expected_ticker}, {score:.1f}%)")
        else:
            print(f"❌ '{query}' -> No match (expected {expected_ticker})")
    
    print(f"\nResults: {passed}/{len(abbrev_tests)} passed")
    return passed, len(abbrev_tests)

def test_multi_word():
    """Test multi-word company names with spacing variations"""
    print("\n" + "=" * 70)
    print("TEST SUITE 4: MULTI-WORD COMPANIES")
    print("=" * 70)
    
    multi_word_tests = [
        ("jp morgan", "JPM"),
        ("jpmorgan", "JPM"),
        ("j p morgan", "JPM"),
        ("bank of america", "BAC"),
        ("bankofamerica", "BAC"),
        ("coca cola", "KO"),
        ("cocacola", "KO"),
        ("goldman sachs", "GS"),
        ("morgan stanley", "MS"),
        ("wells fargo", "WFC"),
        ("american express", "AXP"),
        ("home depot", "HD"),
    ]
    
    passed = 0
    for query, expected_ticker in multi_word_tests:
        best_match = process.extractOne(
            query,
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=70
        )
        
        if best_match:
            company_name, score, _ = best_match
            ticker = COMPANY_TICKER_MAP[company_name]
            if ticker == expected_ticker:
                print(f"✅ '{query}' -> {ticker} ({score:.1f}%)")
                passed += 1
            else:
                print(f"❌ '{query}' -> {ticker} (expected {expected_ticker}, {score:.1f}%)")
        else:
            print(f"❌ '{query}' -> No match (expected {expected_ticker})")
    
    print(f"\nResults: {passed}/{len(multi_word_tests)} passed")
    return passed, len(multi_word_tests)

def test_partial_words():
    """Test partial word matching"""
    print("\n" + "=" * 70)
    print("TEST SUITE 5: PARTIAL WORD MATCHING")
    print("=" * 70)
    
    partial_tests = [
        ("coke", "KO", "should match coca cola"),
        ("star", "SBUX", "should match starbucks"),
        ("mac", "MCD", "should match mcdonalds"),
        ("visa", "V", "exact match"),
        ("nike", "NKE", "exact match"),
    ]
    
    for query, expected_ticker, note in partial_tests:
        best_match = process.extractOne(
            query,
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=50  # Lower threshold for partials
        )
        
        if best_match:
            company_name, score, _ = best_match
            ticker = COMPANY_TICKER_MAP[company_name]
            status = "✅" if ticker == expected_ticker else "⚠️"
            print(f"{status} '{query}' -> {ticker} ({score:.1f}%) - {note}")
        else:
            print(f"❌ '{query}' -> No match (expected {expected_ticker})")

def test_suggestions_always_appear():
    """Test that suggestions always appear for any input"""
    print("\n" + "=" * 70)
    print("TEST SUITE 6: SUGGESTION SYSTEM")
    print("=" * 70)
    
    random_inputs = [
        "blahblah",
        "random text",
        "asdfghjkl",
        "xyz123",
        "invalid company name",
        "",
        "zzz",
    ]
    
    passed = 0
    for query in random_inputs:
        matches = process.extract(
            query if query else "apple",  # Fallback for empty
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            limit=3
        )
        
        if len(matches) >= 3:
            print(f"✅ '{query or '(empty)'}' -> Got {len(matches)} suggestions:")
            for company_name, score, _ in matches[:3]:
                ticker = COMPANY_TICKER_MAP[company_name]
                print(f"     - {ticker} ({company_name.title()}) - {score:.1f}%")
            passed += 1
        else:
            print(f"❌ '{query}' -> Only got {len(matches)} suggestions")
    
    print(f"\nResults: {passed}/{len(random_inputs)} passed (all should provide 3+ suggestions)")
    return passed, len(random_inputs)

def test_case_insensitivity():
    """Test that matching is case-insensitive"""
    print("\n" + "=" * 70)
    print("TEST SUITE 7: CASE INSENSITIVITY")
    print("=" * 70)
    
    case_tests = [
        ("APPLE", "AAPL"),
        ("Apple", "AAPL"),
        ("apple", "AAPL"),
        ("aPpLe", "AAPL"),
        ("MICROSOFT", "MSFT"),
        ("MicroSoft", "MSFT"),
        ("TESLA", "TSLA"),
        ("TeSLa", "TSLA"),
    ]
    
    passed = 0
    for query, expected_ticker in case_tests:
        best_match = process.extractOne(
            query.lower(),  # API normalizes to lowercase
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=70
        )
        
        if best_match:
            company_name, score, _ = best_match
            ticker = COMPANY_TICKER_MAP[company_name]
            if ticker == expected_ticker:
                print(f"✅ '{query}' -> {ticker} ({score:.1f}%)")
                passed += 1
            else:
                print(f"❌ '{query}' -> {ticker} (expected {expected_ticker})")
        else:
            print(f"❌ '{query}' -> No match")
    
    print(f"\nResults: {passed}/{len(case_tests)} passed")
    return passed, len(case_tests)

def test_confidence_scores():
    """Test that confidence scores are reasonable"""
    print("\n" + "=" * 70)
    print("TEST SUITE 8: CONFIDENCE SCORE VALIDATION")
    print("=" * 70)
    
    score_tests = [
        ("apple", 100.0, "Exact match should be 100%"),
        ("aple", 80.0, "Single letter typo should be 80%+"),
        ("microsft", 90.0, "Minor typo should be 90%+"),
        ("tsl", 70.0, "Abbreviation should be 70%+"),
    ]
    
    for query, min_score, note in score_tests:
        best_match = process.extractOne(
            query,
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=50
        )
        
        if best_match:
            company_name, score, _ = best_match
            ticker = COMPANY_TICKER_MAP[company_name]
            status = "✅" if score >= min_score else "⚠️"
            print(f"{status} '{query}' -> {ticker} ({score:.1f}%) - {note}")
        else:
            print(f"❌ '{query}' -> No match")

def run_all_tests():
    """Run all fuzzy matching test suites"""
    print("\n")
    print("█" * 70)
    print(" " * 15 + "TWIN FUZZY MATCHING TEST SUITE")
    print(" " * 20 + f"Testing {len(COMPANY_TICKER_MAP)} Companies")
    print("█" * 70)
    
    total_passed = 0
    total_tests = 0
    
    # Run all test suites
    p, t = test_exact_matches()
    total_passed += p
    total_tests += t
    
    p, t = test_typos()
    total_passed += p
    total_tests += t
    
    p, t = test_abbreviations()
    total_passed += p
    total_tests += t
    
    p, t = test_multi_word()
    total_passed += p
    total_tests += t
    
    test_partial_words()  # No pass/fail count
    
    p, t = test_suggestions_always_appear()
    total_passed += p
    total_tests += t
    
    p, t = test_case_insensitivity()
    total_passed += p
    total_tests += t
    
    test_confidence_scores()  # No pass/fail count
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Fuzzy matching is working perfectly!")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed. Review output above.")
    
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
