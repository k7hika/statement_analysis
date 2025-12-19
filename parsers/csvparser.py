#### ###############cleaning using pandas#################################
# import pandas as pd
# import datetime as dt
# df=pd.read_csv("sample_csvs/Acct_Statement_XXXXXXXX2864_22112025.csv")
# df.columns=df.columns.str.strip()
# df.rename(columns={'Debit Amount':'Debit','Credit Amount':'Credit','Chq/Ref Number':'Ref_number','Value Dat':'value_date'}, inplace=True)
# df['Date']=pd.to_datetime(df['Date'],dayfirst=True,errors='coerce')
# df['value_date']=pd.to_datetime(df['value_date'],dayfirst=True,errors='coerce')
# df['Narration']=(
#     df['Narration']
#     .astype(str)
#     .str.strip()
#     .str.lower()
#     .str.replace(r'\s+',' ',regex=True)
# )
# df['Debit']=df['Debit'].fillna(0)
# df['Credit']=df['Credit'].fillna(0)
# print(df['Narration'].head())
# print(df['Date'].head())
# print(df['value_date'].head())
# print(df.info())
import csv
import re
from datetime import datetime

def parse_record(record):
    final_record = []
    remove_keys = ['Value_Dat', 'Debit_Amount', 'Credit_Amount']
    rename_keys={'Date':'date','Narration':'description','Amount':'amount','Chq/Ref_Number': 'ref_number',
                 'Closing_Balance':'balance'}
    for r in record:
        for field in ['Date','Value_Dat']:

            try:
                r[field] = datetime.strptime(r[field], "%d/%m/%y").date()
                r[field] = r[field].isoformat()
                # r[field] = str(r[field])
            except (ValueError,TypeError,KeyError):
                r[field] = None

        # r['Date']=datetime.strptime(r['Date'] ,'%d/%m/%y')
        # r['Value_Dat']=datetime.strptime(r['Value_Dat'] ,'%d/%m/%y')

        for field in ['Debit_Amount','Credit_Amount','Closing_Balance']:
            negat = False
            try:
                r[field] =str(r[field])
                # r[field] = float(re.sub(r'[",)(]','',r[field]))
                if r[field].startswith("(") and r[field].endswith(")"):
                    negat=True
                    # r[field]=(float(r[field]))*-1
                r[field] = float(re.sub(r'[^0-9.-]','',r[field]))
                if negat:
                    r[field]=-1*r[field]
            except (ValueError,TypeError,KeyError) :
                if field == "Closing_Balance":
                    r[field]=None
                else:
                    r[field] = 0.0
        r['Amount']= r['Credit_Amount']-r['Debit_Amount']
    for m in record:
        new_r = {rename_keys.get(k,k): v for k, v in m.items() if k not in remove_keys}
        final_record.append(new_r)
    return final_record
def parse_csv(path):
    sample_headers = {"date": ["date", "txn_date", "transaction_date"],
                      "debit": ["debit", "debit_amount", "withdrawal", "dr"],
                      "credit": ["credit", "credit_amount", "deposit", "cr"],
                      "balance": ["balance", "closing_balance", "available_balance"],
                      "description": ["narration", "description", "remarks", "particulars"],
                      "ref_number": ["ref_no", "reference", "chq_no", "cheque_no"]}
    with open(path,mode='r') as csvfile:
        # csvreader=csv.DictReader(csvfile)
        while True:
            line=csvfile.readline()
            if not line :
                break
            if not line.strip():
                continue
            header = line.split(',')
            # cleaned_header = [col.strip().replace(' ',"_") for col in header]
            cleaned_header=[re.sub(r'\s+','_',col.strip()) for col in header]
            # print(cleaned_header)
            break
        cleaned_row=[]
        for line in csv.reader(csvfile):
            cleaned_line= [r.strip() for r in line]
            # print(cleaned_line)
            # cleaned_row.append(cleaned_line[0])
            cleaned_row.append(cleaned_line)
        # print(cleaned_row[0])
        # cleaned_record=[dict(zip(cleaned_header,r)) for r in cleaned_row]
        cleaned_record = [dict(zip(cleaned_header,r)) for r in cleaned_row]
        return parse_record(cleaned_record)