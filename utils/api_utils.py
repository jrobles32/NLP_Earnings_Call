"""
Contains functions that help organize api data and create requests
"""
import logging

from utils.ratelimit_utils import RateLimit, sleep_and_retry


@sleep_and_retry
@RateLimit(calls=2, interval=10)
def api_request(session, url, **kwargs):
    """
    Sends a request using a session to the desired API and converts the available data to json
    format.

    Parameters
    ----------
    session: object
        A initialized request session.
    url: str
        The url link of the API.
    **kwargs: dic
        Additional key-value pairs to add to GET request. Helps improve request query and API
        recognition.
        The keyword arguments are passed to initialized request session, 'session.get()'.

    Return
    ------
    dict
        The available data in the API request.
    """
    # creating the get request based on api url and throwing an error if invalid query
    api_request = session.get(url, **kwargs)
    logging.info(f'Request made: {api_request.url}, Status code:{api_request.status_code}')
    api_request.raise_for_status()

    # converting the data to json format and returning it
    json_data = api_request.json()['data']
    return json_data


def years_dict(content:dict):
    """
    Groups based on year keys found dictionary. Creating a list of quarters each representing
    published earnings transcripts. Helps reduce the total number of dictionaries created. 

    Parameters
    ----------
    content: dict
        A dictionary that must contain the date information for available earning call transcripts.

    Return
    ------
    list
        A list of dictionaries, each containing an individual year with the available quarters for 
        that year.
    """
    # stores the restructured dictionary
    condensed_dic = {}

    # looping over each of the transcipts found to find date content
    for transcript in content:

        # removing the date key
        transcript.pop('date')

        # determing if a year is already a key in the dictionary
        if transcript['year'] in condensed_dic:

            # determining if value of quarter key is a list
            if isinstance(condensed_dic[transcript['year']]['quarter'], list):

                # appending quarter values to existing list in key of dictionary
                condensed_dic[transcript['year']]['quarter'].append(transcript['quarter'])

            else:

                # establishing the values for quarter key as lists and adding the second value
                condensed_dic[transcript['year']]['quarter'] = [
                    condensed_dic[transcript['year']]['quarter'], transcript['quarter']
                    ]

        else:
            # setting a not included year as a key, and its value being the content of first occurrence
            condensed_dic[transcript['year']] = transcript
    
    # selecting only the values from the dictionary and storing each dictionary result in a list
    return list(condensed_dic.values())


def merge_list_dict(list_dicts):
    """
    Combines a list of dictionaries into a single dictionary. If dictionary does not have a key,
    None is added as its value.

    Parameter
    ---------
    list_dicts: list
        A list containing the desired dictionaries to combine.

    Return
    ------
    dict
        A dictionary containing all the keys available from each dictionary in input. The value being
        a list of the shared values for key.
    """
    # initializing set object to keep only unique keys and unpacking all the keys in list of dicts
    keys = set().union(*list_dicts)
    
    # dict to store the values of list of dicts
    final_dict = {}

    # looping over the unique keys
    for key in keys:

        # looping over each dictionary in input list
        for dict in list_dicts:

            # checking to see if key is already in final dict 
            if key not in final_dict:

                # initializing key value to an empty list
                final_dict[key] = []

            # getting the value from dict in list and adding it to key in final
            final_dict[key].append(dict.get(key))

    return final_dict