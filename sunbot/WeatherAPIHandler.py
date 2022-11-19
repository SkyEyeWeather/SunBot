
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
    """Perform request contained in string specified in argument and return the
    result provides by the weather API. This is a private function.
    ## Parameter :
    * request [in]: request to send to the weather API, as a string

    ## Return value :
    Dictionnary that contains API response to the specified request. This dictionnary
    can be empty if an error occured when querying the API"""

    logging.info(f"Sending request {request} to the weather API")
    response = requests.get(request)
    #If an error occured when querying weather API :
    if response.status_code != 200:
        logging.error(f"An error occured when querying weather API. Code error: {response.status_code}")
        return {}
    #Return received response in JSON format, in a dictionnary:
    responseJson = response.json()
    logging.info(f"Response received: {responseJson}")
    return responseJson


def currentWeatherRequest(locationName : str) -> dict:
    """Perform a request to the weather API to get current weather for specified location
    ## Parameter:
    * locationName [in]: name of the location whose we want know current weather

    ## Return:
    JSON response to the request, as a dictionnary"""

    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locationName}/today?unitGroup=metric&include=current&key={os.environ['idVisualCrossing']}&contentType=json&lang=id"
    logging.info(f"Performing a current weather request for {locationName}")
    return _performRequest(request)["currentConditions"]


def dailyWeatherRequest(locationName : str) -> dict:
    """Perform a request to the weather API to get daily weather for specified
    location in argument
    ## Parameter:
    * locationName [in]: name of the location which we want know the weather for current day

    # Return value:
    JSON response to the request, as a dictionnary"""

    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locationName}/today?unitGroup=metric&include=days&key={os.environ['idVisualCrossing']}&contentType=json&lang=id"
    logging.info(f"Performing a daily weather request for {locationName}")
    return _performRequest(request)


def dailyRainRequest(locationName : str) -> dict :
    """Perform a request to weather API to retrieve data about hourly rain for
    current day for the locality whose name is specified into argument.
    # Parameter :
    * locationName [in]: name of the locality whose wants get data about rain conditions in the current day

    #Return value:
    Request response from the weather API, in a dictionnary (JSON format)"""

    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locationName}/today?unitGroup=metric&elements=datetime%2CdatetimeEpoch%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Csnow%2Csource&include=hours%2Cdays&key={os.environ['idVisualCrossing']}&contentType=json&lang=fr"
    logging.info(f"Performing a daily rain request for {locationName}")
    return _performRequest(request)