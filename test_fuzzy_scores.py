from rapidfuzz import fuzz, process
from companies import COMPANY_TICKER_MAP

test_inputs = [
    "apple",
    "appel", 
    "applelflk",
    "apppple",
    "micrsf",
    "microsoft",
    "teslaaa",
    "googl",
    "amzon"
]

print("=== Fuzzy Match Score Analysis ===\n")
for query in test_inputs:
    matches = process.extract(
        query,
        COMPANY_TICKER_MAP.keys(),
        scorer=fuzz.token_sort_ratio,
        limit=5
    )
    print(f"Input: '{query}'")
    for company, score, _ in matches:
        ticker = COMPANY_TICKER_MAP[company]
        print(f"  {score:>3}% - {company} ({ticker})")
    print()
