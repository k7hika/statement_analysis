import pdfplumber
import re
import logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)
from pdfplumber.table import TableSettings
checks=re.compile(r'^(0[1-9]|[1,2][0-9]|[3][01])[\/\-.](0[1-9]|1[0-2])[\/\-.](\d{4})')
def parse_value(final_record):
    for idx,reco in enumerate(final_record,start=1):
        for field in ['ref_number','description']:
            if not reco[field].strip():
                reco[field]=None
        for field in ['debit','credit','balance']:
            negat=False
            try:
                reco[field]=str(reco[field])
                if reco[field].startswith('(') and reco[field].endswith(')'):
                    negat=True
                reco[field]=float(re.sub(r'[^0-9-+.]','',reco[field]))
                if negat:
                    reco[field]=-1*reco[field]
            except (KeyError,ValueError,TypeError):
                if field =='balance':
                    reco[field]=None
                else:
                    reco[field]=0.00
        if reco['debit']==0 and reco['credit']==0:
            logger.info(f"No credit and  debit entry in row number {idx}  and row is {reco}")
            raise ValueError("invalid credit or debit are zero in csv file ")
        reco['amount']=reco['credit']-reco['debit']
        reco.pop('debit',None)
        reco.pop('credit',None)
    return final_record
# checks=re.compile(r'^(0[1-9]|[12][0-9]|3[01])[\/\-.](0[1-9]|1[0-2])[\/\-.](\d{4})')
def parse_pdf(path):
    sample_headers = {"date": ["date", "txn_date", "transaction_date","tran_date"],
                      "debit": ["debit", "debit_amount", "withdrawal", "dr"],
                      "credit": ["credit", "credit_amount", "deposit", "cr"],
                      "balance": ["balance", "closing_balance", "available_balance"],
                      "description": ["narration", "description", "remarks", "particulars"],
                      "ref_number": ["ref_no", "reference", "chq_no", "cheque_no", 'chq/ref_number']}
    with pdfplumber.open(path) as pdf_file:
    # with pdfplumber.open('../sample_pdfs/Account_stmt_XX4936_12122025.pdf') as pdf_file:
    # with pdfplumber.open('../sample_pdfs/Acct_Statement_XX2864_07122025.pdf') as pdf_file:
        normalised_header = []
        normalised_index = []
        first_page=pdf_file.pages[0]
        # second_page=pdf_file.pages[1]
        records=[]
        tabl=first_page.extract_table()
        header=tabl[0]
        y=[]
        cleaned_header=[re.sub(r'\s+','_',h.strip().lower()) for h in header]
        logger.info(f"cleaned header: {cleaned_header}")
        for id,col in enumerate(cleaned_header):
            for k,v in sample_headers.items():
                if col in v:
                    normalised_header.append(k)
                    normalised_index.append(id)
                    print(id)
                    break
        logger.info(f"normalised header: {normalised_header}")
        if 'date' not in normalised_header:
            logger.info("No date column in csv file")
            raise ValueError('No date column in csv file')
        if 'description' not in normalised_header:
            logger.info("No description column in csv file")
            raise ValueError('No description column in csv file')
        if 'balance' not in normalised_header:
            logger.info("No balance column in csv file")
            raise ValueError('No balance column in csv file')
        if 'debit' not in normalised_header:
            logger.info("No debit column in csv file")
            raise ValueError("No debit column in csv file")
        if 'credit' not in normalised_header:
            logger.info("No credit column in csv file")
            raise ValueError("No credit column in csv file")
        for page_num,page in enumerate(pdf_file.pages[0:3],start=1):
            tabl=page.extract_table()
            if tabl:
                for ro,line in enumerate(tabl[1:],start=1):
                    if checks.match(line[0]):
                        # cleanedline = [l.strip() if l.strip() else '' for l in line]
                        # records.append(cleanedline)
                        cleanedline = [line[i].strip() if line[i].strip() else '' for i in normalised_index]
                        records.append(cleanedline)
                    else:
                        logger.info(f"particular{line} in page number{page_num} with entry number {ro} has no date")
                        continue
            else:
                logger.info(f'Page {page_num} has no table')
                continue
        final_record=[dict(zip(normalised_header,reco)) for reco in records]
    # return parse_value(final_record)
    return parse_value(final_record)
pdf_data=parse_pdf('../sample_pdfs/Account_stmt_XX4936_12122025.pdf')
print(pdf_data)
