import csv
import re
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)
def parse_record(record):
    # remove_keys = ['debit','credit']
    # rename_keys={'Date':'date','Narration':'description','Amount':'amount','Chq/Ref_Number': 'ref_number',
    #              'Closing_Balance':'balance'}
    for idx,r in enumerate(record,start=1):
        try:
            r['date'] = datetime.strptime(r['date'], "%d/%m/%y").date()
            r['date'] = r['date'].isoformat()
        except (ValueError,TypeError,KeyError):
            logger.error(f"row {idx} has no date column in csv file")
            r['date'] = None

        # r['Date']=datetime.strptime(r['Date'] ,'%d/%m/%y')
        # r['Value_Dat']=datetime.strptime(r['Value_Dat'] ,'%d/%m/%y')

        for field in ['debit','credit','balance']:
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
                if field == "balance":
                    r[field]=None
                else:
                    r[field] = 0.0
        if r['credit']==0 and r['debit']==0:
            logger.error(f"row {idx} has no credit and  debit row={r}")
            raise ValueError("invalid credit or debit are zero in csv file")

        r['amount']= r['credit']-r['debit']
        r.pop('debit',None)
        r.pop('credit',None)
    # for m in record:
    #     new_r = {rename_keys.get(k,k): v for k, v in m.items() if k not in remove_keys}
    #     final_record.append(new_r)
    return record
def parse_csv(path):
    sample_headers = {"date": ["date", "txn_date", "transaction_date"],
                      "debit": ["debit", "debit_amount", "withdrawal", "dr"],
                      "credit": ["credit", "credit_amount", "deposit", "cr"],
                      "balance": ["balance", "closing_balance", "available_balance"],
                      "description": ["narration", "description", "remarks", "particulars"],
                      "ref_number": ["ref_no", "reference", "chq_no", "cheque_no",'chq/ref_number']}
    with open(path,mode='r') as csvfile:
        normalised_header = []
        normalised_index=[]
        # csvreader=csv.DictReader(csvfile)
        while True:
            line=csvfile.readline()
            if not line :
                logger.info("reached end of file for searching header")
                break
            if not line.strip():
                continue
            header = line.split(',')
            # cleaned_header = [col.strip().replace(' ',"_") for col in header]
            cleaned_header=[re.sub(r'\s+','_',col.strip()).lower() for col in header]
            break
        logger.info(f"cleaned header: {cleaned_header}")
        for id,n in enumerate(cleaned_header):
            for k,alter in sample_headers.items():
                if n in alter:
                    normalised_header.append(k)
                    normalised_index.append(id)
                    break
        logger.info(f"normalised header: {normalised_header}")
        if 'date' not in normalised_header:
            logger.error("No date column in csv file")
            raise ValueError("No date column in csv file")
        if 'description' not in normalised_header:
            logger.error("No description column in csv file")
            raise ValueError("No narration column in csv file")
        if 'credit' not in normalised_header and 'debit' not in normalised_header:
            logger.error("No credit and  debit column in csv file")
            raise ValueError("No transaction value  column in csv file")
        if 'balance' not in normalised_header:
            logger.error("No balance column in csv file")
            raise ValueError("No balance column in csv file")
        cleaned_row=[]
        for line in csv.reader(csvfile):
            cleaned_line = [line[i].strip() for i in normalised_index]
            cleaned_row.append(cleaned_line)
        # for line in csv.reader(csvfile):
        #     cleaned_line= [r.strip() for r in line]
        #     # cleaned_row.append(cleaned_line[0])
        #     cleaned_row.append(cleaned_line)
        cleaned_record=[dict(zip(normalised_header,r)) for r in cleaned_row]
        # cleaned_record = [dict(zip(updated, r)) for r in cleaned_row]
        return parse_record(cleaned_record)