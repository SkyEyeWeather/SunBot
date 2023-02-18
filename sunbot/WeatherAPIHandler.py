
#=================================
#   LIBRARIES USED BY THIS MODULE
#=================================

import logging
import os
import requests


#=================================
#       MODULE'S FUNCTIONS
#=================================

def _performRequest(request : str) -> dict:
    """Performs the request contained in the string specified as argument and returns 
    the result provided by the weather API. This is a private function.
    ## Parameter :
    * `request`: request to send to the weather API, as a string
    ## Return value :
    Dictionnary that contains API response for the specified request. This dictionnary
    can be empty if an error occured when querying the API"""

    logging.info(f"Sending request {request} to the weather API")
    response = requests.get(request)
    #If an error occured when querying weather API :
    if response.status_code != 200:
        logging.error(f"An error occured when querying weather API. Error code: {response.status_code}")
        return {}
    #Return received response in JSON format, as a dictionnary:
    responseJson = response.json()
    logging.info(f"Response received: {responseJson}")
    return responseJson


def currentWeatherRequest(locationName : str) -> dict:
    """Performs a request to the weather API to get the current weather conditions 
    for the specified location.
    ## Parameter:
    * `locationName`: name of the location for which we want to know the current weather
    ## Return value:
    JSON response to the request, as a dictionnary"""

    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locationName}/today?unitGroup=metric&include=current&key={os.environ['idVisualCrossing']}&contentType=json&lang=id"
    logging.info(f"Performing a current weather request for {locationName}")
    return _performRequest(request)["currentConditions"]


def dailyWeatherRequest(locationName : str) -> dict:
    """Performs a request to the weather API to get the daily weather for the
    specified location passed in argument
    ## Parameter:
    * `locationName` : name of the location for which we want to know the daily weather
    ## Return value:
    JSON response to the request, as a dictionnary"""

    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locationName}/today?unitGroup=metric&include=days&key={os.environ['idVisualCrossing']}&contentType=json&lang=id"
    logging.info(f"Retrieving the daily weather for the location {locationName}")
    return _performRequest(request)


def dailyRainRequest(locationName : str) -> dict :
    """Performs a request to the weather API to retrieve hourly rainfall data
    for the current day for the location whose name was specified in argument.
    ## Parameter :
    * `locationName`: name of the locality whose we want to get data about rain conditions for the current day
    ## Return value:
    JSON request response from the weather API, as a dictionnary"""

    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locationName}/today?unitGroup=metric&elements=datetime%2CdatetimeEpoch%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Csnow%2Csource&include=hours%2Cdays&key={os.environ['idVisualCrossing']}&contentType=json&lang=fr"
    logging.info(f"Performing a daily rainfall request for {locationName}")
    return _performRequest(request)