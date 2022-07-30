import requests
import webbrowser
import bs4
import re


def google_href(company:str)->list:
    """
    The first page hyperlinks of a google search focused on finding the earnings call of a company.

    Parameters
    ----------
    company: str
        The name of a company that one wants to find the earning call for.

    Returns
    -------
    list
        Hyperlinks of the first page of the google search.
    """
    # setting up the base url and desired search
    base_url = 'https://www.google.com/search?q='
    search = f'{company} earnings call'.replace(' ', '+')

    # extracting the html content and setting it up for parsing
    search_url = requests.get(base_url + search).text
    soup = bs4.BeautifulSoup(search_url, 'lxml')

    # extracting tag and class containing desired links
    desired_div = soup.find_all('div', class_="egMi0 kCrYT")
    earnings_links = [tag.a.get('href') for tag in desired_div]

    # cleaning the links: removing everything before http and selecting everything before &
    p = re.compile(r'http[^&]*')
    clean_links = [p.search(link).group() for link in earnings_links]
    print(clean_links)

google_href('tesla')


