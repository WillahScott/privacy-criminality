
## XML table to CSV
 
# Goal: Download the following table: [Insider SEC Filings](http://www.secform4.com/sec-filings.htm?printable=true) 
# For this we will read the source and parse the HTML table to download into a pandas dataframe and write a .csv with the info.

import pandas as pd


# Table URL and column names
url = "http://www.secform4.com/sec-filings.htm?printable=true"
heads = ["Transaction Date","Reported Date","Company","Symbol","Insider Relationship","Shares Traded","Average Price","Total Amount","SharesOwned","Filing"]

# Get the second table in the url
SECfilings = pd.read_html(url)[1]

# Add column names
SECfilings.columns = heads

# Save csv
SECfilings.to_csv("SEC_filings.csv")

