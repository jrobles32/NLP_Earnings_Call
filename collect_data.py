import logging
from API.roic_api import Roic_API
import pandas as pd

# setting the standard logging format
LOGGER_FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]', level=logging.INFO)

# creating a list containing a list of tickers to collect data in batches
tickers = [
    ['xom', 'cvx', 'cop', 'eog', 'pxd'], 
    ['duk', 'wmb', 'aee', 'eix', 'oxy'], 
    ['d', 'dte', 'aep', 'ed', 'exc'], 
    ['kmi', 'xel', 'so', 'oke', 'nee'], 
    ['sre', 'fe', 'ppl', 'peg', 'wec'], 
    ['es', 'etr', 'psx', 'mpc', 'vlo']
]

# creating empty dataframe to store data
data = pd.DataFrame()

# passing list of tickers to collect data for from the api
for ticker in tickers:

    # initializing class with desired tickers and collecting them
    api_data = Roic_API(tickers)
    available_data = api_data.get_all()

    # appending extracted data to main dataframe
    data = pd.concat([data, available_data], ignore_index=True)

# extracting the collected data as a csv
filename = 'energy_transcripts.csv'
data.to_csv(filename, index=False)