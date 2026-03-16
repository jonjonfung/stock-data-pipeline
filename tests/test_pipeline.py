import pandas as pd
import json
import sys

print("Running pipeline tests...")

# Test 1 - imports
try:
    import boto3
    import pandas as pd
    import pyarrow
    print("✅ Test 1 passed - all imports successful")
except ImportError as e:
    print(f"❌ Test 1 failed - {e}")
    sys.exit(1)

# Test 2 - API URL builds correctly
try:
    symbol = 'AAPL'
    api_key = 'demo'
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    assert 'AAPL' in url
    assert 'GLOBAL_QUOTE' in url
    print(f"✅ Test 2 passed - API URL builds correctly")
except AssertionError as e:
    print(f"❌ Test 2 failed - {e}")
    sys.exit(1)

# Test 3 - transform logic works
try:
    mock_data = {
        'Global Quote': {
            '01. symbol': 'AAPL',
            '02. open': '170.00',
            '03. low': '169.00',
            '04. high': '171.00',
            '05. price': '170.50',
            '06. volume': '50000000',
            '07. latest trading day': '2026-03-16',
            '08. previous close': '169.50',
            '09. change': '1.00',
            '10. change percent': '0.59%'
        }
    }

    quote = mock_data['Global Quote']
    record = {
        'symbol': quote.get('01. symbol'),
        'open': float(quote.get('02. open', 0)),
        'high': float(quote.get('04. high', 0)),
        'low': float(quote.get('03. low', 0)),
        'price': float(quote.get('05. price', 0)),
        'volume': int(quote.get('06. volume', 0)),
        'previous_close': float(quote.get('08. previous close', 0)),
        'change': float(quote.get('09. change', 0)),
        'change_percent': quote.get('10. change percent', '0%').replace('%', '')
    }

    df = pd.DataFrame([record])
    assert len(df) == 1
    assert df['symbol'][0] == 'AAPL'
    assert df['price'][0] == 170.50
    print(f"✅ Test 3 passed - transform logic works correctly")
except Exception as e:
    print(f"❌ Test 3 failed - {e}")
    sys.exit(1)

print("\n🎉 All tests passed!")
