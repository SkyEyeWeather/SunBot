"""
Weather API handler module
"""

#=================================
#   LIBRARIES USED BY THIS MODULE
#=================================

import json
import logging
import os
import requests


#=================================
#       MODULE'S FUNCTIONS
#=================================

def __perform_request(request : str) -> dict:
    """Perform the request contained in the string specified as argument, and return
    the result provided by the weather API. This is a private function.
    ## Parameters:
    * `request`: request to send to the weather API, as a string
    ## Return value :
    Dictionnary containing API response for the specified request. This dictionnary
    can be empty if an error occured when querying the API"""
    logging.info("Sending request %s to the weather API", request)
    response = requests.get(request)
    #If an error occured when querying weather API :
    if response.status_code != 200:
        logging.error("An error occured when querying weather API. Error code: %d", response.status_code)
        return {}
    #Return received response in JSON format, as a dictionnary:
    json_response = response.json()
    logging.info("Response received: %s", json_response)
    return json_response


def ask_current_weather(location_name : str) -> dict:
    """Perform a request to the weather API to get the current weather conditions 
    for the specified location.
    ## Parameters:
    * `locationName`: name of the location for which we want to know current weather
    conditions
    ## Return value:
    JSON response to the request, as a dictionnary"""
    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_name}/today?unitGroup=metric&include=current&key={os.environ['idVisualCrossing']}&contentType=json&lang=id"
    logging.info("Performing a current weather request for %s", location_name)
    return __perform_request(request)["currentConditions"]


def ask_daily_weather(location_name : str) -> dict:
    """Perform a request to the weather API to get the daily weather for the
    specified location passed in argument
    ## Parameter:
    * `locationName` : name of the location for which we want to know the daily weather
    ## Return value:
    JSON response to the request, as a dictionnary"""
    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_name}/today?unitGroup=metric&include=days&key={os.environ['idVisualCrossing']}&contentType=json&lang=id"
    logging.info("Retrieving the daily weather for the location %s", location_name)
    return __perform_request(request)


def ask_daily_rain(location_name : str) -> dict :
    """Perform a request to the weather API to retrieve hourly rainfall data
    for the current day for the location whose name was specified in argument.
    ## Parameters:
    * `locationName`: name of the locality whose we want to get data about rain conditions for the current day
    ## Return value:
    JSON request response from the weather API, as a dictionnary"""
    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_name}/today?unitGroup=metric&elements=datetime%2CdatetimeEpoch%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Csnow%2Csource&include=hours%2Cdays&key={os.environ['idVisualCrossing']}&contentType=json&lang=fr"
    logging.info("Performing a daily rainfall request for %s", location_name)
    return __perform_request(request)
