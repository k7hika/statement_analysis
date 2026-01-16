from parsers.csvparser import parse_csv
# from parsers.pdf_parser import parse_pdf
data=parse_csv('sample_csvs/Acct_Statement_XXXXXXXX2864_22112025.csv')
# datapdf=parse_pdf('sample_pdfs/Account_stmt_XX4936_12122025.pdf')
print(data[0])
# print(datapdf[0])
