# 📈 Stock Data Pipeline

[![Tests](https://github.com/jonjonfung/stock-data-pipeline/actions/workflows/test.yml/badge.svg)](https://github.com/jonjonfung/stock-data-pipeline/actions/workflows/test.yml)

A fully automated serverless data pipeline that fetches daily stock prices from the 
Alpha Vantage API and stores them in AWS S3 for analysis with Athena. The pipeline 
runs automatically every day at 9am Sydney time via EventBridge, building a growing  
historical dataset over time.

## 🏗️ Architecture

![Image](https://github.com/user-attachments/assets/00b25a99-c36d-4d72-a1d1-fc4db997a683)
```
EventBridge (daily trigger 9am Sydney)
  → AWS Step Functions (orchestration)
    → Lambda 1 — fetch (calls Alpha Vantage API)
      → S3 raw/YYYY-MM-DD/ (stores raw JSON)
        → Lambda 2 — transform (cleans JSON → Parquet)
          → S3 processed/ (stores clean Parquet)
            → Athena (query growing dataset)
```

## 🛠️ Tech Stack

| Service | Purpose |
|---|---|
| **AWS EventBridge** | Daily schedule trigger |
| **AWS Step Functions** | Pipeline orchestration + error handling |
| **AWS Lambda** | Serverless compute for fetch + transform |
| **Alpha Vantage API** | Real time stock market data |
| **AWS S3** | Raw JSON and processed Parquet storage |
| **AWS Athena** | Serverless SQL queries on growing dataset |
| **GitHub Actions** | Automated testing on every push |

## 📊 Stocks Tracked

| Symbol | Company |
|---|---|
| AAPL | Apple |
| GOOGL | Google |
| MSFT | Microsoft |
| AMZN | Amazon |
| META | Meta |

## 🔄 How the Pipeline Works

### Step 1 — EventBridge triggers daily
Every day at 9am Sydney time EventBridge automatically triggers the Step Functions 
state machine — no manual intervention needed.

### Step 2 — Step Functions orchestrates
Step Functions manages the flow between Lambda 1 and Lambda 2. If either function 
fails it automatically retries up to 3 times with exponential backoff before 
marking the execution as failed.

### Step 3 — Lambda 1 fetches data
Lambda 1 calls the Alpha Vantage API for each stock symbol and saves the raw JSON 
response to S3 partitioned by date:
```
s3://stock-pipeline-john/raw/2026-03-16/AAPL.json
s3://stock-pipeline-john/raw/2026-03-16/GOOGL.json
...
```

### Step 4 — Lambda 2 transforms data
Lambda 2 reads the raw JSON files, cleans and transforms them into a structured 
DataFrame using Pandas, and saves the result as a Snappy compressed Parquet file:
```
s3://stock-pipeline-john/processed/2026-03-16/stocks.parquet
```

### Step 5 — Athena queries growing dataset
Athena points at the entire processed/ folder — so as new Parquet files are added 
daily the dataset automatically grows and all historical data is queryable.

## 🪣 S3 Structure
```
stock-pipeline-john/
  ├── raw/
  │   ├── 2026-03-16/
  │   │   ├── AAPL.json
  │   │   ├── GOOGL.json
  │   │   ├── MSFT.json
  │   │   ├── AMZN.json
  │   │   └── META.json
  │   └── 2026-03-17/
  │       └── ...
  ├── processed/
  │   ├── 2026-03-16/
  │   │   └── stocks.parquet
  │   └── 2026-03-17/
  │       └── stocks.parquet
  └── output/
      └── (Athena query results)
```

## 📁 Project Structure
```
├── .github/
│   └── workflows/
│       └── test.yml           # Automated tests on every push
├── lambda/
│   ├── fetch_data.py          # Lambda 1 — calls Alpha Vantage API
│   └── transform_data.py      # Lambda 2 — cleans and transforms data
├── step_functions/
│   └── state_machine.json     # Step Functions state machine definition
├── requirements.txt
└── README.md
```

## 🚀 How to Deploy

### Prerequisites
- AWS account with Lambda, S3, Step Functions and Athena access
- Alpha Vantage free API key from alphavantage.co

### Step 1 — Create S3 bucket
```bash
aws s3 mb s3://stock-pipeline-john --region ap-southeast-2
```

### Step 2 — Deploy Lambda functions
1. Create `stock-fetch-data` Lambda with Python 3.12
2. Add environment variables:
   - `ALPHA_VANTAGE_API_KEY` — your API key
   - `S3_BUCKET` — your bucket name
3. Attach `AWSSDKPandas-Python312` layer
4. Create `stock-transform-data` Lambda with Python 3.12
5. Attach `AWSSDKPandas-Python312` layer

### Step 3 — Create Step Functions state machine
Use the definition in `step_functions/state_machine.json`

### Step 4 — Create EventBridge rule
Schedule: `cron(0 23 * * ? *)` → triggers daily at 9am Sydney time

### Step 5 — Create Athena table
```sql
CREATE EXTERNAL TABLE IF NOT EXISTS stock_db.daily_stocks (
  symbol string,
  date string,
  open double,
  high double,
  low double,
  price double,
  volume bigint,
  previous_close double,
  change double,
  change_percent double,
  ingested_at string
)
STORED AS PARQUET
LOCATION 's3://stock-pipeline-john/processed/';
```

## 📊 Sample Queries
```sql
-- Latest stock prices
SELECT symbol, price, change_percent
FROM stock_db.daily_stocks
ORDER BY price DESC;

-- Biggest daily movers
SELECT symbol, change, change_percent
FROM stock_db.daily_stocks
ORDER BY change ASC;

-- Daily summary
SELECT 
    date,
    COUNT(symbol) as stocks_tracked,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(SUM(volume), 0) as total_volume
FROM stock_db.daily_stocks
GROUP BY date
ORDER BY date DESC;
```

## 🔮 Future Improvements
- Add more stock symbols
- Store data in Redshift for faster analytical queries
- Build Streamlit dashboard showing price trends over time
- Add SNS email alerts when stocks move more than 5% in a day
- Add data quality checks using AWS Glue Data Quality
- Expand to intraday data for more granular analysis

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `ALPHA_VANTAGE_API_KEY` | Free API key from alphavantage.co |
| `S3_BUCKET` | S3 bucket name for raw and processed data |
