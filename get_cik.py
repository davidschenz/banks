from pathlib import Path
import sys
import csv
import requests



def get_cik_mapping():
    """
    Download the CIK mapping from the SEC
    Adapted from https://github.com/sec-edgar/sec-edgar/blob/master/secedgar/cik_lookup.py
    """
    
    response = requests.get("https://www.sec.gov/files/company_tickers.json")
    json_response = response.json()
    return {key: {v[key].upper(): str(v["cik_str"]) for v in json_response.values()
                  if v[key] is not None}
            for key in ("ticker", "title")}


cik_mapping = get_cik_mapping()
print(cik_mapping["ticker"])
source_dir = Path('./listings/')
files = source_dir.iterdir()
with open("./tickers.csv",'w') as out_file:
    out_csv = csv.DictWriter(out_file,['ticker','cik','name','country'])
    out_csv.writeheader()
    for file in files:
        with file.open('r') as file_handle:
            input_csv = csv.DictReader(file_handle)
            for row in input_csv:
                ticker = row['Ticker']
                try:
                    cik = "{:0>10}".format(cik_mapping['ticker'][ticker])
                    print(cik)
                except KeyError:
                    print("Missing CIK for ticker {}".format(ticker))
                out_row = {
                    "name": row["Name"].strip(),
                    "ticker": ticker,
                    "country": row["Country"],
                    "cik": cik
                }
                out_csv.writerow(out_row)


