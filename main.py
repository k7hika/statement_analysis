from parsers.csvparser import parse_csv
data=parse_csv('sample_csvs/Acct_Statement_XXXXXXXX2864_22112025.csv')
print(data[0])
