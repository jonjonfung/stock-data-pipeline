import json
import boto3
import urllib.request
import os
from datetime import datetime

def lambda_handler(event, context):
    
    # Config
    api_key = os.environ['ALPHA_VANTAGE_API_KEY']
    bucket = os.environ['S3_BUCKET']
    
    # Stocks to track
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
    
    results = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for symbol in symbols:
        try:
            # Call Alpha Vantage API
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
            
            # Save raw JSON to S3
            s3 = boto3.client('s3')
            key = f'raw/{today}/{symbol}.json'
            
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            
            print(f"✅ Saved {symbol} to s3://{bucket}/{key}")
            results.append({'symbol': symbol, 'status': 'success'})
            
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {str(e)}")
            results.append({'symbol': symbol, 'status': 'error', 'error': str(e)})
    
    return {
        'statusCode': 200,
        'date': today,
        'results': results
    }
