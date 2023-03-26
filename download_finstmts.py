import requests
from ratelimit import limits, sleep_and_retry
from datetime import timedelta
import csv
import os

@sleep_and_retry
@limits(calls=1, period=timedelta(seconds=1).total_seconds())
def download_file(cik: str, output_directory: str):
    """
    Download the file from Edgar's API in beta
    """
    url = "https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json".format(cik)
    headers = {
        'User-Agent': 'Your User Agent',
        'From': 'Your Email Address'
    }
    #print(url)
    response = requests.get(url, headers=headers)
    if response.text.find("<Error><Code>NoSuchKey</Code><Message>")>-1:
        print("Nothing found for CIK {}".format(cik))
    else:
        file_name = os.path.join(output_directory,"{}.json".format(cik))
        with open(file_name,'w') as output_file:
            output_file.write(response.text)


with open('tickers.csv','r') as input_file:
    input_csv = csv.DictReader(input_file)
    for row in input_csv:
        download_file(row["cik"],"./finstmts")