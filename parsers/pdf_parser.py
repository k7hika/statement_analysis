import pdfplumber
import re
import logging
import pandas as pd
logging.basicConfig(level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)
# date_check=re.compile(r'^(0[1-9]|[1,2][0-9]|[3][01])[\/\-.](0[1-9]|1[0-2])[\/\-.](\d{4})')
date_check=re.compile(r'^(0[1-9]|[1,2][0-9]|[3][01])[\/\-.\" "](0[1-9]|1[0-2]|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)[\/\-.\" "](\d{4})',
                      re.IGNORECASE)
# file_path='../sample_pdfs/544516929-ICICI-BANK-STATEMENT.pdf'
file_path='../sample_pdfs/686976004-PUNJAB-NATIONAL-BANK-STATEMENT.pdf'
# file_path='../sample_pdfs/axisbank.pdf'
# file_path='../sample_pdfs/sample_multiline.pdf'
# file_path='../sample_pdfs/sbibank.pdf'
# file_path='../sample_pdfs/hdfcbank.pdf'
# file_path='../sample_pdfs/686976004-PUNJAB-NATIONAL-BANK-STATEMENT.pdf'
# file_path='../sample_pdfs/544516929-ICICI-BANK-STATEMENT.pdf'
sample_headers = {"date": ["date", "txn_date", "transaction_date","tran_date"],
                      "debit": ["debit", "debit_amount", "withdrawal", "dr"],
                      "credit": ["credit", "credit_amount", "deposit", "cr"],
                      "balance": ["balance", "closing_balance", "available_balance"],
                      "description": ["narration", "description", "remarks", "particulars","details"],
                      "ref_number": ["ref_no", "reference", "chq_no", "cheque_no", 'chq/ref_number','Ref No./Cheque','chq._no.']}
def header_detection(pdf_file,sample_headers):
    """
    detect table headers
    """
    # with pdfplumber.open('../sample_pdfs/Account_stmt_XX4936_12122025.pdf') as pdf_file:
    # with pdfplumber.open('../sample_pdfs/Acct_Statement_XX2864_07122025.pdf') as pdf_file:
    cleaned_header=[]
    cleaned_index=[]
    narration_index = None
    for pagnum,page in enumerate(pdf_file.pages,start=1):
        tabl = page.extract_table()
        if not tabl:
            continue
        if tabl:
            for line in tabl:
                temp_header = []
                temp_header_index = []
                check_header = [re.sub(r'\s+', '_', (h or '').strip().lower()) for h in line]
                for inde, da in enumerate(check_header):
                    for k, v in sample_headers.items():
                        if da in v:
                            temp_header.append(da)
                            temp_header_index.append(inde)
                            if k == 'description':
                                narration_index = inde
                if len(temp_header)>3:
                    cleaned_header=temp_header
                    cleaned_index=temp_header_index
                    if narration_index is not None:
                        narration_index=cleaned_index.index(narration_index)
                    logger.info(f"header found in {cleaned_header}")
                    break
        if cleaned_header:
            break
    return cleaned_header,cleaned_index,narration_index
def extract_row(pdf_file,cleaned_index,checks,narrat_index):
    """
    extract table rows with date column,

    """
    last_record = None
    records=[]
    for page_num,page in enumerate(pdf_file.pages,start=1):
        tabl=page.extract_table()
        if not tabl:
            logger.info(f'Page {page_num} has no table')
            continue
        for ro,line in enumerate(tabl):
            if not line:
                continue
            line=[cell if isinstance(cell,str) else '' for cell in line ]
            if any(isinstance(cell,str) and checks.match(cell.strip()) for cell in line):
                cleanedline = [line[i].strip() if line[i].strip() else '' for i in cleaned_index]
                records.append(cleanedline)
                last_record=records[-1]
            elif(narrat_index is not None
                    and last_record is not None
                    and narrat_index<len(line)
                    and isinstance(line[narrat_index],str)
                    and all(not(line[i].strip()) for i in range(len(line)) if i != narrat_index)
                    and line[narrat_index].strip()
            ):
                last_record[narrat_index]+=" "+line[narrat_index].strip()
            else:
                logger.info(f"specific {line} in page number{page_num} with entry number {ro} has no date")
                continue
    # for page_num,page in enumerate(pdf_file.pages,start=1):
    #     tabl=page.extract_table()
    #     if not tabl:
    #         logger.info(f'Page {page_num} has no table')
    #         continue
    #     for ro,line in enumerate(tabl,start=1):
    #         if not line:
    #             continue
    #         if any(isinstance(cell,str) and checks.match(cell.strip()) for cell in line):
    #                 cleanedline = [line[i].strip() if line[i].strip() else '' for i in cleaned_index]
    #                 records.append(cleanedline)
    #         else:
    #             logger.info(f"specific {line} in page number{page_num} with entry number {ro} has no date")
    #             continue
    return records
def normalised_records(extracted_row,headers,sample_headers):
    """
    Normalize headers,numeric values (debit, credit, balance),
    handle negatives, compute transaction amount,
    """
    normalised_header=[]
    for id, col in enumerate(headers):
        for k, v in sample_headers.items():
            if col in v:
                normalised_header.append(k)
                # normalised_index.append(id)
                break
    logger.info(f"normalised header: {normalised_header}")
    if 'date' not in normalised_header:
        logger.info("No date column in pdf file")
        raise ValueError('No date column in pdf file')
    if 'description' not in normalised_header:
        logger.info("No description column in pdf file")
        raise ValueError('No description column in pdf file')
    if 'balance' not in normalised_header:
        logger.info("No balance column in pdf file")
        # raise ValueError('No balance column in pdf file')
    if 'debit' not in normalised_header:
        logger.info("No debit column in pdf file")
        raise ValueError("No debit column in pdf file")
    if 'credit' not in normalised_header:
        logger.info("No credit column in pdf file")
        raise ValueError("No credit column in pdf file")

    final_record = [dict(zip(normalised_header, reco)) for reco in extracted_row]
    for idx,reco in enumerate(final_record,start=1):
        for field in ['ref_number','description']:
            if field in reco:
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
        reco['amount']=reco['credit']-reco['debit']
        reco.pop('debit',None)
        reco.pop('credit',None)
    return final_record
def csv_conversion(final_parsedata): #csv conversion
    """
    convert to csv
    """
    df=pd.DataFrame(final_parsedata)
    df.to_csv("pdf_data.csv",index=False)
def parse_pdf(file_path):
    """
    parse pdf file
    """
    with pdfplumber.open(file_path) as pdf_file:
        headers,indexes,narrat_index=header_detection(pdf_file,sample_headers)
        extracted_rows=extract_row(pdf_file,indexes,date_check,narrat_index)
        normalised_data=normalised_records(extracted_rows,headers,sample_headers)
    return normalised_data
def main():
    final_parsedata=parse_pdf(file_path)
    print(final_parsedata)
    csv_conversion(final_parsedata)
if __name__ == '__main__':
    main()
