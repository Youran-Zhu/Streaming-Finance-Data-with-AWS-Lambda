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