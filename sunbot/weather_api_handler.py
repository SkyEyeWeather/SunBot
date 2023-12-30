"""
Weather API handler module
"""

# =================================
#   LIBRARIES USED BY THIS MODULE
# =================================

import logging
import os

import requests

REQUEST_TIME_OUT = 10  # Timeout for a GET action, in seconds

# =================================
#       MODULE'S FUNCTIONS
# =================================


def __perform_request(request: str) -> dict:
    """Perform the request contained in the string specified as argument, and return
    the result provided by the weather API. This is a private function.
    ## Parameters:
    * `request`: request to send to the weather API, as a string
    ## Return value :
    Dictionnary containing API response for the specified request. This dictionnary
    can be empty if an error occured when querying the API
    """
    logging.info("Sending a request to the weather API...")
    response = requests.get(request, timeout=REQUEST_TIME_OUT)
    # If an error occured when querying weather API :
    if response.status_code != 200:
        logging.error(
            "An error occured when querying weather API. Error code: %d",
            response.status_code,
        )
        return {}
    # Return received response in JSON format, as a dictionnary:
    json_response = response.json()
    logging.info("Response received: %s", json_response)
    return json_response


def ask_current_weather(location_name: str) -> dict:
    """Perform a request to the weather API to get the current weather conditions
    for the specified location.
    ## Parameters:
    * `location_name`: name of the location for which we want to know current
    weather
    conditions
    ## Return value:
    JSON response to the request, as a dictionnary
    """
    keys_list = [
        "preciptype",
        "precipprob",
        "precip",
        "windspeed",
        "winddir",
        "windgust",
        "humidity",
        "conditions",
        "temp",
        "feelslike",
        "pressure",
        "visibility",
        "uvindex",
        "cloudcover",
    ]
    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_name}/today?unitGroup=metric&include=current&key={os.environ['idVisualCrossing']}&contentType=json&lang=id"
    logging.info("Retrieving current weather conditions for %s", location_name)
    request_response = __perform_request(request)
    if request_response == {}:
        logging.error("Dict is empty!")
        # Continue to execute function to have empty key
    dict2return = {}
    for key in keys_list:
        try:
            dict2return[key] = request_response["currentConditions"][key]
        except KeyError:
            logging.error(
                "Key %s is not in the request response. Set to the default value", key
            )
            dict2return[key] = ""
    return dict2return


def ask_daily_weather(location_name: str) -> dict:
    """Perform a request to the weather API to get the daily weather for the
    specified location passed in argument
    ## Parameter:
    * `location_name` : name of the location for which we want to know the daily
    weather
    ## Return value:
    JSON response to the request, as a dictionnary
    """
    keys_list = [
        "temp",
        "tempmin",
        "tempmax",
        "precip",
        "preciptype",
        "precipprob",
        "windspeed",
        "winddir",
        "pressure",
        "humidity",
        "uvindex",
        "sunrise",
        "sunset",
        "conditions",
    ]
    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_name}/today?unitGroup=metric&include=days&key={os.environ['idVisualCrossing']}&contentType=json&lang=id"
    logging.info("Retrieving the daily weather for the location %s", location_name)
    request_response = __perform_request(request)
    if request_response == {}:
        logging.error("Dict is empty!")
    dict2return = {}
    for key in keys_list:
        try:
            dict2return[key] = request_response["days"][0][key]
        except KeyError:
            logging.error(
                "Key %s is not in the request response. Set to the default value", key
            )
            dict2return[key] = ""
    dict2return["timezone"] = request_response["timezone"]
    return dict2return


def ask_daily_rain(location_name: str, period: str = "today") -> dict:
    """Perform a request to the weather API to retrieve hourly rainfall data
    for the current day for the location whose name was specified in argument.
    ## Parameters:
    * `location_name`: name of the locality whose we want to get data about rainfalls
       for the current day
    * `period`: period to be considered
    ## Return value:
    JSON request response from the weather API, as a dictionnary
    """
    request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location_name}/{period}?unitGroup=metric&elements=datetime%2CdatetimeEpoch%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Csnow%2Csource&include=hours%2Cdays&key={os.environ['idVisualCrossing']}&contentType=json&lang=fr"
    dict2return = {"address": "", "rainfall_data": {}}
    logging.info("Performing a daily rainfall request for %s", location_name)
    request_response = __perform_request(request)
    if request_response == {}:
        logging.error("Dict is empty")
        return dict2return
    dict2return["address"] = request_response["address"]
    for hour_data in request_response["days"][0]["hours"]:
        hour_dict = {
            "preciptype": hour_data["preciptype"],
            "precipprob": hour_data["precipprob"],
            "precip": hour_data["precip"],
        }
        dict2return["rainfall_data"][hour_data["datetime"]] = hour_dict
    return dict2return
