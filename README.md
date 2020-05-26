# Streaming-Finance-Data-with-AWS-Lambda
   
This project is aiming to provision a few Lambda functions to generate near real time finance data records for downstream   processing and interactive querying. 

The data is collected from Yahoo finance with *yfinance* package and loaded into AWS S3 bucket. AWS Glue and AWS Athena are leveraged to perform interactive querying.  

## Data Collecting  

Collect one full day’s worth of stock HIGH and LOW prices for ten company listed below on Thursday, May 14th 2020, at an one minute interval.  

*Facebook (FB), Shopify (SHOP), Beyond Meat (BYND), Netflix (NFLX), Pinterest (PINS)*  
*Square (SQ), The Trade Desk (TTD), Okta (OKTA), Snap (SNAP), Datadog (DDOG)*

* query.sql
```Python
import boto3
import os
import subprocess
import sys
import json

subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/tmp", 'yfinance'])
sys.path.append('/tmp')
import yfinance as yf

def lambda_handler(event, context):
    companies = ["FB", "SHOP", "BYND", "NFLX", "PINS", "SQ", "TTD", "OKTA", "SNAP", "DDOG"]
    for company in companies:
        company_ticker = yf.Ticker(company)
        hist = company_ticker.history(start="2020-05-14", end="2020-05-15", interval = "1m")
        for index, row in hist.iterrows():
            dic = {"high":row["High"], "low":row["Low"], "ts":index.strftime('%Y-%m-%d %X'), "name":company}
            as_jsonstr = json.dumps(dic)
            # initialize boto3 client
            fh = boto3.client("firehose", "us-east-1")
            
            # this actually pushed to our firehose datastream
            # we must "encode" in order to convert it into the
            # bytes datatype as all of AWS libs operate over
            # bytes not strings
            fh.put_record(
                DeliveryStreamName="finance-data-stream", 
                Record={"Data": as_jsonstr.encode('utf-8')})
    return {
    'statusCode': 200,
    'body': json.dumps('Done!')
    }
```
Data is shown in folder *finance_data*


## Lambda Function URL
This is the API endpoint (Only for demonstration purpose):  

https://m59bh6cym5.execute-api.us-east-1.amazonaws.com/default/data_collector_p3

## AWS Configuration

1) Lambda Function for Data Collector Configuration 

![AppendixA_Lambda_Collector_Config](https://github.com/Youran-Zhu/Streaming-Finance-Data-with-AWS-Lambda/blob/master/AppendixA_Lambda_Collector_Config.png)

2) Kinesis Data Firehose Delivery Stream Monitoring

![AppendixB_Kinesis_Monitor](https://github.com/Youran-Zhu/Streaming-Finance-Data-with-AWS-Lambda/blob/master/AppendixB_Kinesis_Monitor.png)

## Data Analysis


Query the highest hourly stock “high” per company from the list above using AWS Glue & AWS Athena.

* query.sql
```SQL
WITH T1 AS 
    (SELECT name,
         high,
         ts,
         SUBSTRING(ts,
         12,
         2) AS hour_of_day
    FROM finance_data_p3), T2 AS 
    (SELECT T1.name AS company_name,
         MAX(T1.high) AS high_price_hour,
         T1.hour_of_day AS hour_of_day
    FROM T1
    GROUP BY  T1.name, T1.hour_of_day)
SELECT T2.company_name,
         T2.high_price_hour,
         T2.hour_of_day,
         T1.ts
FROM T1, T2
WHERE T1.name = T2.company_name
        AND T1.high = T2.high_price_hour
        AND T1.hour_of_day = T2.hour_of_day
ORDER BY  T2.company_name, T2.hour_of_day 
```
Result is shown in file:
* results.csv



