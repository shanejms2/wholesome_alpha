import pandas as pd
import alpha as az

symbol = ['SRET']
end_date = pd.to_datetime('today').normalize()
start_date = end_date - pd.DateOffset(months=2)

providers = {'yahoo', 'eodhistoricaldata_yahoo', 'eodhistoricaldata',
             'alphavantage_yahoo', 'alphavantage', 'marketstack'
            }

for provider in providers:
    mktl = az.MkTreader()
