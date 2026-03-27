import os
import sys

# Make sure Python can see project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
from parsers.csvparser import parse_csv
def testparse_returns_list():
    records=parse_csv('sample_csvs/Acct_Statement_XXXXXXXX2864_22112025.csv')
    # assert type(records)==list
    assert isinstance(records,list)
    assert len(records)>0
    row=records[0]
    assert 'date' in row
    assert 'amount' in row
    assert 'description' in row
    assert 'ref_number' in row
    assert 'balance' in row
    assert isinstance(row['balance'],float)
    assert isinstance(row['amount'],float)
    assert isinstance(row['description'],str)


