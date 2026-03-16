import json
import boto3
import pandas as pd
import io
from datetime import datetime

def lambda_handler(event, context):
    
    # Config
    bucket = event['bucket']
    date = event['date']
    
    s3 = boto3.client('s3')
    
    # List all JSON files for today
    prefix = f'raw/{date}/'
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    
    if 'Contents' not in response:
        return {
            'statusCode': 404,
            'message': f'No raw data found for {date}'
        }
    
    records = []
    
    for obj in response['Contents']:
        # Read each JSON file
        file = s3.get_object(Bucket=bucket, Key=obj['Key'])
        data = json.loads(file['Body'].read().decode())
        
        quote = data.get('Global Quote', {})
        
        if quote:
            records.append({
                'symbol': quote.get('01. symbol'),
                'date': quote.get('07. latest trading day'),
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('04. high', 0)),
                'low': float(quote.get('03. low', 0)),
                'price': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'previous_close': float(quote.get('08. previous close', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0%').replace('%', '')
            })
    
    if not records:
        return {
            'statusCode': 404,
            'message': 'No valid records found'
        }
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    df['ingested_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df['change_percent'] = pd.to_numeric(df['change_percent'], errors='coerce')
    
    print(f"✅ Transformed {len(df)} records")
    print(df)
    
    # Save as Parquet to processed/
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)
    
    key = f'processed/{date}/stocks.parquet'
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=parquet_buffer.getvalue(),
        ContentType='application/octet-stream'
    )
    
    print(f"✅ Saved Parquet to s3://{bucket}/{key}")
    
    return {
        'statusCode': 200,
        'date': date,
        'records_processed': len(df),
        'output_key': key
    }
