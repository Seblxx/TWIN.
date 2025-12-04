"""Test the reverted fuzzy matching implementation"""
from companies import COMPANY_TICKER_MAP
from rapidfuzz import fuzz, process

def test_fuzzy_matching():
    """Test fuzzy matching with various inputs"""
    
    test_cases = [
        ("apple", "AAPL"),
        ("aple", "AAPL"),  # typo
        ("microsft", "MSFT"),  # typo
        ("microsoft", "MSFT"),
        ("google", "GOOGL"),
        ("alphabet", "GOOGL"),
        ("tesla", "TSLA"),
        ("coca cola", "KO"),
        ("jpmorgan", "JPM"),
        ("disney", "DIS"),
    ]
    
    print("Testing fuzzy matching:")
    print("-" * 70)
    
    for query, expected_ticker in test_cases:
        best_match = process.extractOne(
            query,
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=70
        )
        
        if best_match:
            company_name, score, _ = best_match
            ticker = COMPANY_TICKER_MAP[company_name]
            status = "✓" if ticker == expected_ticker else "✗"
            print(f"{status} '{query}' -> {ticker} ({score:.1f}% confidence, matched: {company_name})")
        else:
            print(f"✗ '{query}' -> No match found (expected {expected_ticker})")
    
    print("-" * 70)

def test_suggestions():
    """Test suggestion candidates"""
    from rapidfuzz import process
    
    test_queries = ["aple", "microsft", "tsl", "random text", "coke"]
    
    print("\nTesting suggestions:")
    print("-" * 70)
    
    for query in test_queries:
        matches = process.extract(
            query,
            COMPANY_TICKER_MAP.keys(),
            scorer=fuzz.token_sort_ratio,
            limit=3
        )
        
        print(f"Query: '{query}'")
        for company_name, score, _ in matches:
            ticker = COMPANY_TICKER_MAP[company_name]
            print(f"  - {ticker} ({company_name.title()}) - {score:.1f}%")
        print()

if __name__ == "__main__":
    print(f"Loaded {len(COMPANY_TICKER_MAP)} companies\n")
    test_fuzzy_matching()
    test_suggestions()
