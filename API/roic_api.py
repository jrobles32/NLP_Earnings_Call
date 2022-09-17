"""
Class used to collect data from 'roic.ai'
"""
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from utils.api_utils import years_dict, api_request, merge_list_dict

import json
import logging
import requests


class Roic_API:
    """Creates a request session that collects earnings call transcipts from 'roic.ai' API.

    Parameters
    ----------
    ticker: str or list of str
        Desired company ticker or list of company tickers to be used for data collection.
    year: int, optional
        The year of a desired earnings call. Needs to be used along with quarter. 
    quarter: int, optional
        The quarter of a desired earnings call. Needs to be used along with year. 

    Attributes
    ----------
    api_url: str
        URL being used to make API requests.
    ticker: str or list of str
        Company ticker(s) used in data collection.
    quarter: int
        Desired quarter of single transcript
    session: session object
        Created request session to maintain persistent parameters across API request. Acessing it 
        can be useful to update headers, cookies, etc.
    web_url: str
        URL being used to collect available trancripts using playwright
    year: int
        Desired year of single transcript.
 
    Methods
    -------
    get()
        Creates a single API request based on ticker, year, and quarter passed when class
        was initialized. Collects earnings call data based on those parameters.
    get_all()
        Creates multiple API request to collect all the earnings call transcripts for a ticker
        or list of tickers. Tickers need to be passed when intialized.
    _available_transcripts(ticker)
        Collects the dates of all the available transcripts on the 'roic.ai' website. Not intended
        to be used outside of class, but can helpful to view all available dates.
    """
    def __init__(self, ticker, year:int=None, quarter:int=None):
        self.session = requests.Session()
        self.session.headers.update({
            "authority": "roic.ai",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": "^\^Chromium^^;v=^\^104^^, ^\^",
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "if-none-match": "W/^\^d2e9-yBgQT8spgq6KBk/ZS9/fM3sHHvA^^",
        })
        self.payload = ''
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        self.api_url = "https://roic.ai/api/transcript/"
        self.web_url = 'https://roic.ai/transcripts/'


    def get(self):
        """
        Uses the initialized request session along with desired ticker, year, and quarter to extract a single 
        earning call transcript from the roic API.

        Returns
        ------
        dict
            A dictionary containing the JSON data of a single API request. Includes ticker, transcript, and 
            published data information.
        """
        # Ensuring ticker is capitalized and passing year and quarter of desired earnings transcript
        upper_ticker = str.upper(self.ticker)
        querystring = {"y":f"{self.year}","q":f"{self.quarter}"}

        # creating the reference url for header and the base api url
        referer_header = {"referer": f"https://roic.ai/transcripts/{upper_ticker}?y={self.year}&q={self.quarter}"}
        url_comp = self.api_url + upper_ticker

        # creating the api request and extracting a single transcript in json format
        json_data = api_request(self.session, url_comp, params=querystring, headers=referer_header, data=self.payload)

        return json_data


    def get_all(self):
        """
        Uses initialized request session along with playwright to collect all the available earnings call transcripts
        for a ticker or list of tickers.

        Returns
        ------
        dict
            A dictionary containing the JSON data of all the API requests succesfully made. Includes ticker, transcript, 
            and published data information.
        """
        # collecting all the available earnings calls for a ticker or list of tickers
        self.ticker_years = self._available_transcripts(self.ticker)

        # initializing empty list to store the dictionary of each API request
        transcripts = []

        # looping over all the available tickers
        for key in self.ticker_years.keys():

            # looping over the total number of years available for each ticker
            for year in range(len(self.ticker_years[key])):
                
                # extracting the quarter and year values from dictionary
                pos_quarters = self.ticker_years[key][year]['quarter']
                year = self.ticker_years[key][year]['year']

                # determining if quarters is a single value, if true converting it to list
                if isinstance(pos_quarters, int):
                    pos_quarters = [pos_quarters]

                # looping over the available quarters for a year
                for quarter in range(len(pos_quarters)):

                    # defining parameters to pass to request based on ticker, year, and quarter
                    querystring = {"y":f"{year}","q":f"{pos_quarters[quarter]}"}
                    referer_header = {"referer": f"https://roic.ai/transcripts/{key}?y={year}&q={pos_quarters[quarter]}"}
                    url_comp = self.api_url + key

                    # attempting to make API request, exiting loop if httperror occurs inorder to collect extracted data 
                    try:
                        json_data = api_request(self.session, url_comp, params=querystring, headers=referer_header, data=self.payload)
                    except requests.HTTPError:
                        break
                    
                    # adding the collected API data to initialized list
                    transcripts.append(json_data)
        
        # combining the dictionaries in list into a single dictionary
        return merge_list_dict(transcripts)


    def _available_transcripts(self, ticker):
        """
        Uses playwright and bs4 to parse the HTML content for the dates of earning call transcripts
        available of a company. It creates a dictionary to store the information.

        Parameter
        ----------
        tickers: str or list of str
            The stock ticker of desired companies.

        Returns
        -------
        dict
            A dictionary with the company ticker being the key and values being a list of dictionaries.
            Each containing a year with a list of quarters available for said year.  
        """
        # standardizing the tickers and creating a dictonary for comp_earnings attribute
        if isinstance(ticker, str):
            ticker = [ticker]

        cap_tickers = [str.upper(ticker) for ticker in ticker]
        dict_years = dict.fromkeys(cap_tickers)

        # creating a context manager for playwright
        with sync_playwright() as p:

            # initializing the chrome browser
            browser = p.chromium.launch()
            page = browser.new_page()

            for ticker in cap_tickers:
                # creating the desired url and going to it
                earnings_url = self.web_url + ticker
                page.goto(earnings_url)

                # waiting until dates are present in the webpage and extracting the HTML
                page.is_visible('//*[@id="__next"]/div/main/div[3]/div/div[1]/div[2]/div[1]')
                hmtl = page.content()

                # creating a bs4 object to find the script containing the dates
                soup = BeautifulSoup(hmtl, features='lxml')
                dates_data = soup.find('script', id='__NEXT_DATA__')

                # constructing the content found in json format and extracting earnings call data
                json_data = json.loads(dates_data.text)
                quarters_available = json_data["props"]['pageProps']['data']['data']['earningscalls']
                logging.info(f'Available Earnings Call for {ticker}: {len(quarters_available)} quarters.')

                # extracting only the dates and updating the values of ticker_quarters keys
                available = years_dict(content=quarters_available)
                dict_years.update({ticker:available})

            browser.close()
        return dict_years