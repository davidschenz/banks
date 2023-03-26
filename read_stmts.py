import os
import json
from datetime import datetime as dt
import csv
import random
"""
Nothing found for CIK 0001569650
Nothing found for CIK 0001943802
Nothing found for CIK 0001492165
Nothing found for CIK 0001913971
Nothing found for CIK 0001288784
Nothing found for CIK 0001299939
Nothing found for CIK 0001132979
Nothing found for CIK 0001103838
Nothing found for CIK 0001103838
"""

item_counts = {}

finstmt_pull = {}
finstmt_pull['afs_unrealized_loss'] = ['AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedLossBeforeTax','AvailableForSaleSecuritiesAccumulatedGrossUnrealizedLossBeforeTax','AvailableForSaleDebtSecuritiesGrossUnrealizedLoss','AvailableForSaleSecuritiesGrossUnrealizedLoss','AvailableForSaleSecuritiesGrossUnrealizedLosses1','AvailableForSaleSecuritiesGrossUnrealizedLosses','DebtSecuritiesAvailableForSaleUnrealizedLossPosition']
finstmt_pull['afs_unrealized_gain'] = ['AvailableForSaleDebtSecuritiesAccumulatedGrossUnrealizedGainBeforeTax','AvailableForSaleSecuritiesAccumulatedGrossUnrealizedGainBeforeTax','AvailableForSaleDebtSecuritiesGrossUnrealizedGain','AvailableforsaleSecuritiesGrossUnrealizedGain','AvailableForSaleSecuritiesGrossUnrealizedGains','DebtSecuritiesAvailableForSaleUnrealizedGainPosition']
finstmt_pull['afs_unrealized_net'] = ['AvailableForSaleSecuritiesAccumulatedGrossUnrealizedGainLossBeforeTax','AvailableForSaleSecuritiesGrossUnrealizedGainLoss','AvailableforsaleSecuritiesGrossUnrealizedGainLoss1']
finstmt_pull['afs_fair_value'] = ['AvailableForSaleSecuritiesDebtSecurities','AvailableForSaleSecurities',]
finstmt_pull['afs_historical_value'] = ['AvailableForSaleDebtSecuritiesAmortizedCostBasis','AvailableForSaleSecuritiesAmortizedCost']
finstmt_pull['deposits'] = ['Deposits','DepositsSavingsDeposits','DepositsFairValueDisclosure']
finstmt_pull['htm_fair_value'] = ['HeldToMaturitySecuritiesDebtMaturitiesFairValue','HeldToMaturitySecuritiesFairValue','HeldToMaturitySecuritiesFairValueDisclosure']
finstmt_pull['htm_unrealized_gain'] = ['HeldToMaturitySecuritiesAccumulatedUnrecognizedHoldingGain','HeldtomaturitySecuritiesUnrecognizedHoldingGain','HeldToMaturitySecuritiesUnrecognizedHoldingGains']
finstmt_pull['htm_unrealized_loss'] = ['HeldToMaturitySecuritiesAccumulatedUnrecognizedHoldingLoss','HeldToMaturitySecuritiesUnrecognizedHoldingLoss','HeldToMaturitySecuritiesUnrecognizedHoldingLosses']
finstmt_pull['htm_historical_value'] = ['HeldToMaturitySecuritiesDebtMaturitiesNetCarryingAmount','HeldToMaturitySecurities','HeldToMaturitySecuritiesDebtMaturitiesNetCarryingAmount']
finstmt_pull['htm_fair_value']= ['HeldToMaturitySecuritiesDebtMaturitiesFairValue','HeldToMaturitySecuritiesCurrent','HeldToMaturitySecuritiesFairValue']
finstmt_pull['notes_historical_value'] = ['NotesReceivableGross','LoansAndLeasesReceivableGrossCarryingAmount','LoansAndLeasesReceivableNetReportedAmount']
finstmt_pull['total_assets'] = ['Assets']
finstmt_pull['total_liabilities'] = ['Liabilities']
finstmt_pull['net_income']= ['NetIncomeLoss','ProfitLoss']
finstmt_pull['oci'] = ['ComprehensiveIncomeNetOfTax']



def count_items(finstmt: dict):
    """
    Update global item counts of each finstmt item
    """
    keys = finstmt['facts']['us-gaap'].keys()
    for key in keys:
        if key not in item_counts.keys():
            item_counts[key] = 1
        else:
            item_counts[key] += 1


def map_fact(finstmt_tfm: dict, item_list: list, item_name:str) -> dict:
    """
    Map facts from numerous statement names to the higher level grouping
    """
    stmt_item = ""
    cy_present = False;
    py_present = False;
    for item in item_list:
        if item in finstmt_tfm['cy'].keys():
            finstmt_tfm['cy_stmt'][item_name] = finstmt_tfm['cy'][item]
            finstmt_tfm['cy_stmt_item_name'][item_name] = item            
            break
    for item in item_list:
        if item in finstmt_tfm['py'].keys():
            finstmt_tfm['py_stmt'][item_name] = finstmt_tfm['py'][item]
            finstmt_tfm['py_stmt_item_name'][item_name] = item
            break
    return finstmt_tfm

    if output == {}:
        print("Blank return for {} - {}".format(finstmt['cik'], item_list))
        return {}

def guess_currency(finstmt: dict) -> str:
    """
    Return currency code after sampling a few items
    """
    stmt = finstmt['facts']['us-gaap']
    keys = stmt.keys()
    currencies = {}
    for key in random.sample(list(keys), 25):
        currency = list(stmt[key]['units'].keys())[0]
        if currency not in currencies.keys():
            currencies[currency] = 1
        else:
            currencies[currency] += 1
    max_value = max(currencies, key=currencies.get)
    return max_value
    
def guess_dates(finstmt:dict, form: str, currency: str) -> dt | dt:
    last_date = ""
    second_last_date = ""
    for row in finstmt['facts']['us-gaap']["Assets"]["units"][currency]:
        if row['form'] == form:
            new_dt = dt.strptime(row['end'], "%Y-%m-%d")
            if last_date == "":
                last_date = new_dt
            elif new_dt > last_date:
                second_last_date = last_date
                last_date = new_dt
    return last_date, second_last_date

def transform_stmt(finstmt: dict,form: str, currency: str, last_date: dt, second_last_date: dt):
    output = {
        'last_date': last_date, 
        'second_last_date': second_last_date,
        'form': form,
        'currency': currency,
        'cy': {},
        'py': {},
        'cy_stmt': {},
        'py_stmt': {},
        'cy_stmt_item_name': {},
        'py_stmt_item_name': {}
    }
    for key, value in finstmt['facts']['us-gaap'].items():
        if currency in value['units']:
            for row in value['units'][currency]:
                new_dt = dt.strptime(row['end'], "%Y-%m-%d")
                if new_dt == last_date:
                    output['cy'][key] = row['val']
                elif new_dt == second_last_date:
                    output['py'][key] = row['val']
    return output


def read_fin_stmt(cik: str, input_directory:str):
    """
    Read all of the financial statement items
    """
    input_file_name = os.path.join(input_directory,"{}.json".format(cik))
    try:
        with open(input_file_name,'r') as input_file:
            finstmt = json.loads(input_file.read())
            assert 'us-gaap' in finstmt['facts'].keys()
            assert len(finstmt['facts']['us-gaap'].keys()) > 25
            #print(finstmt['cik'])
            #print(finstmt['facts']['us-gaap']['Deposits'])
            currency = guess_currency(finstmt)
            last_date, second_last_date = guess_dates(finstmt,'10-K',currency)
            assert last_date!=""
            assert second_last_date!=""
            #count_items(finstmt)
            stmt_tsfm = transform_stmt(finstmt, '10-K', currency, last_date, second_last_date)
            for key, value in finstmt_pull.items():
                stmt_tsfm = map_fact(stmt_tsfm, value, key)
        return stmt_tsfm, currency
    except (json.JSONDecodeError, FileNotFoundError, AssertionError):
        print("Error opening file")
        return {}, ""

def format_stmt_item(finstmt_tfm: dict):
    """
    Takes an financial statement input and writes output row
    """
    #Get last two dates of 10k
    output = {}
    #Verify we have current data
    if finstmt_tfm['last_date'].year < 2022:
        print("Statements old for bank in {}".format(finstmt_tfm['last_date'].year))
        return {}
    for year in ['cy','py']:
        for key,value in finstmt_tfm[year+'_stmt'].items():
            output[year.upper() +"_"+key] = value
    for year in ['cy','py']:
        for key,value in finstmt_tfm[year+'_stmt_item_name'].items():
            output[year.upper() +"_"+key+'_stmt_item_name'] = value

    output['CY'] = finstmt_tfm['last_date'].strftime("%Y-%m-%d")
    output['PY'] = finstmt_tfm['second_last_date'].strftime("%Y-%m-%d")
    return output


def run():
    with open("./tickers.csv",'r') as input_file_handle, open('./finresults.csv','w') as output_file_handle:
        ticker_csv = csv.DictReader(input_file_handle)
        output_csv = csv.DictWriter(output_file_handle,[ 'cik', 'ticker', 'name', 'country', 'currency','CY','PY','CY_afs_unrealized_loss', 'CY_afs_unrealized_gain', 'CY_afs_fair_value', 'CY_afs_historical_value', 'CY_deposits', 'CY_htm_fair_value', 'CY_htm_unrealized_gain', 'CY_htm_unrealized_loss', 'CY_htm_historical_value', 'CY_notes_historical_value', 'CY_total_assets', 'CY_total_liabilities', 'CY_net_income', 'CY_oci', 'PY_afs_unrealized_loss', 'PY_afs_unrealized_gain', 'PY_afs_fair_value', 'PY_afs_historical_value', 'PY_deposits', 'PY_htm_fair_value', 'PY_htm_unrealized_gain', 'PY_htm_unrealized_loss', 'PY_htm_historical_value', 'PY_notes_historical_value', 'PY_total_assets', 'PY_total_liabilities', 'PY_net_income', 'PY_oci', 'CY_afs_unrealized_loss_stmt_item_name', 'CY_afs_unrealized_gain_stmt_item_name', 'CY_afs_fair_value_stmt_item_name', 'CY_afs_historical_value_stmt_item_name', 'CY_deposits_stmt_item_name', 'CY_htm_fair_value_stmt_item_name', 'CY_htm_unrealized_gain_stmt_item_name', 'CY_htm_unrealized_loss_stmt_item_name', 'CY_htm_historical_value_stmt_item_name', 'CY_notes_historical_value_stmt_item_name', 'CY_total_assets_stmt_item_name', 'CY_total_liabilities_stmt_item_name', 'CY_net_income_stmt_item_name', 'CY_oci_stmt_item_name', 'PY_afs_unrealized_loss_stmt_item_name', 'PY_afs_unrealized_gain_stmt_item_name', 'PY_afs_fair_value_stmt_item_name', 'PY_afs_historical_value_stmt_item_name', 'PY_deposits_stmt_item_name', 'PY_htm_fair_value_stmt_item_name', 'PY_htm_unrealized_gain_stmt_item_name', 'PY_htm_unrealized_loss_stmt_item_name', 'PY_htm_historical_value_stmt_item_name', 'PY_notes_historical_value_stmt_item_name', 'PY_total_assets_stmt_item_name', 'PY_total_liabilities_stmt_item_name', 'PY_net_income_stmt_item_name', 'PY_oci_stmt_item_name'])
        output_csv.writeheader()
        for row in ticker_csv:
            print("Reading {ticker} with CIK {cik}", row)
            stmt_result, currency = read_fin_stmt(row['cik'],'./finstmts')
            if stmt_result != {}:
                stmt_output = format_stmt_item(stmt_result)
                if stmt_output != {}:
                    stmt_output['cik'] = row['cik']
                    stmt_output['ticker'] = row['ticker']
                    stmt_output['name'] = row['name']
                    stmt_output['country'] = row['country']
                    stmt_output['currency'] = currency
                    #print(stmt_output.keys())
                    print(stmt_output)
                    output_csv.writerow(stmt_output)
    with open('finstmt_item_count.txt','w') as output_file:
        for key, value in item_counts.items():
            output_file.write("{},{}\n".format(key, value))

def run_one():
    CIK = '0001810546'
    with open('./finresults.csv','w') as output_file_handle:
        stmt_result, curency = read_fin_stmt(CIK,'./finstmts')
        stmt_output = format_stmt_item(stmt_result)
        stmt_output['cik'] = CIK
        stmt_output['ticker'] = 'NONE'
        stmt_output['name'] = 'NONE'
        stmt_output['country'] = 'NONE'
        stmt_output['currency'] = "USD"
        output_csv = csv.DictWriter(output_file_handle,[ 'cik', 'ticker', 'name', 'country', 'currency','CY','PY','CY_afs_unrealized_loss', 'CY_afs_unrealized_gain', 'CY_afs_fair_value', 'CY_afs_historical_value', 'CY_deposits', 'CY_htm_fair_value', 'CY_htm_unrealized_gain', 'CY_htm_unrealized_loss', 'CY_htm_historical_value', 'CY_notes_historical_value', 'CY_total_assets', 'CY_total_liabilities', 'CY_net_income', 'CY_oci', 'PY_afs_unrealized_loss', 'PY_afs_unrealized_gain', 'PY_afs_fair_value', 'PY_afs_historical_value', 'PY_deposits', 'PY_htm_fair_value', 'PY_htm_unrealized_gain', 'PY_htm_unrealized_loss', 'PY_htm_historical_value', 'PY_notes_historical_value', 'PY_total_assets', 'PY_total_liabilities', 'PY_net_income', 'PY_oci', 'CY_afs_unrealized_loss_stmt_item_name', 'CY_afs_unrealized_gain_stmt_item_name', 'CY_afs_fair_value_stmt_item_name', 'CY_afs_historical_value_stmt_item_name', 'CY_deposits_stmt_item_name', 'CY_htm_fair_value_stmt_item_name', 'CY_htm_unrealized_gain_stmt_item_name', 'CY_htm_unrealized_loss_stmt_item_name', 'CY_htm_historical_value_stmt_item_name', 'CY_notes_historical_value_stmt_item_name', 'CY_total_assets_stmt_item_name', 'CY_total_liabilities_stmt_item_name', 'CY_net_income_stmt_item_name', 'CY_oci_stmt_item_name', 'PY_afs_unrealized_loss_stmt_item_name', 'PY_afs_unrealized_gain_stmt_item_name', 'PY_afs_fair_value_stmt_item_name', 'PY_afs_historical_value_stmt_item_name', 'PY_deposits_stmt_item_name', 'PY_htm_fair_value_stmt_item_name', 'PY_htm_unrealized_gain_stmt_item_name', 'PY_htm_unrealized_loss_stmt_item_name', 'PY_htm_historical_value_stmt_item_name', 'PY_notes_historical_value_stmt_item_name', 'PY_total_assets_stmt_item_name', 'PY_total_liabilities_stmt_item_name', 'PY_net_income_stmt_item_name', 'PY_oci_stmt_item_name'])
        output_csv.writeheader()
        output_csv.writerow(stmt_output)

run()