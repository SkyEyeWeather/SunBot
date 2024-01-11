import os

from sunbot import sunbot
from sunbot.apis.weather import WeatherAPIHandler


class VisualCrossingHandler(WeatherAPIHandler):
    """Visual Crossing API Handler"""

    def __init__(self) -> None:
        self.domain_name = "weather.visualcrossing.com"
        super().__init__(
            domain_name=self.domain_name,
            auth_mode="token",
            accepted_formats=None,
        )
        self.token_key = os.environ["idVisualCrossing"]

    def get_rain_data(self, location_name: str, period: str = "aujoud'hui") -> dict:
        """Get rain data for specified location and period

        Parameters
        ----------
        location_name : str
            name of the location for which to retrieve rain data
        period : str, optional
            period of the location for which to retrieve rain data. For now two periods are
            supported: `aujourd'hui` (today) and `demain` (tommorrow). Default to `aujourd'hui`

        Returns
        -------
        dict
            rain data for specified location and period

        Raises
        ------
        NotImplementedError
            This method must be redefined by inheriting weather API handler
        """
        response = self.request(
            resource_path=f"VisualCrossingWebServices/rest/services/timeline/{location_name}/{sunbot.PERIODS[period]}",
            request_args={
                "unitGroup": "metric",
                "elements": "datetime%2CdatetimeEpoch%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Csnow%2Csource",
                "include": "hours%2Cdays",
                "key": os.environ["idVisualCrossing"],
                "contentType": "json",
                "lang": "fr",
            },
        )

        if not response.ok:
            return {}
        data = self.get_data(
            response=response,
            targets=(
                [f"days/0/hours/{i}/datetime" for i in range(24)]
                + [f"days/0/hours/{i}/preciptype" for i in range(24)]
                + [f"days/0/hours/{i}/precipprob" for i in range(24)]
                + [f"days/0/hours/{i}/precip" for i in range(24)]
                + ["address"]
            ),
        )
        return data

    def get_current_weather_data(self, location_name: str) -> dict:
        """Get current weather data for specified location

        Parameters
        ----------
        location_name : str
            name of the location for which to retrive current weather data

        Returns
        -------
        dict
            current weather data for specified location

        Raises
        ------
        NotImplementedError
            This method must be redefined by inheriting weather API handler
        """
        response = self.request(
            resource_path=f"VisualCrossingWebServices/rest/services/timeline/{location_name}/today",
            request_args={
                "unitGroup": "metric",
                "include": "current",
                "key": os.environ["idVisualCrossing"],
                "contentType": "json",
                "lang": "id",
            },
        )

        if not response.ok:
            return {}
        data = self.get_data(
            response=response,
            targets={
                "currentConditions/conditions": "conditions",
                "currentConditions/temp": "temp",
                "currentConditions/feelslike": "feelslike",
                "currentConditions/preciptype": "preciptype",
                "currentConditions/precipprob": "preciprob",
                "currentConditions/precip": "precip",
                "currentConditions/snowdepth": "snowdepth",
                "currentConditions/snow": "snow",
                "currentConditions/windspeed": "windspeed",
                "currentConditions/winddir": "winddir",
                "currentConditions/windgust": "windgust",
                "currentConditions/humidity": "humidity",
                "currentConditions/pressure": "pressure",
                "currentConditions/visibility": "visibility",
                "currentConditions/uvindex": "uvindex",
                "currentConditions/cloudcover": "cloudcover",
            },
            verbose=True,
        )
        return data

    def get_daily_weather_data(self, location_name: str) -> dict:
        """Get daily weather data for specified location

        Parameters
        ----------
        location_name : str
            name of the location for which to retrieve daily weather data

        Returns
        -------
        dict
            daily weather data for specified location

        Raises
        ------
        NotImplementedError
            This method must be redefined by inheriting weather API handler
        """
        response = self.request(
            resource_path=f"VisualCrossingWebServices/rest/services/timeline/{location_name}/today",
            request_args={
                "unitGroup": "metric",
                "include": "days",
                "key": os.environ["idVisualCrossing"],
                "contentType": "json",
                "lang": "id",
            },
        )

        if not response.ok:
            return {}
        data = self.get_data(
            response=response,
            targets=[
                "timezone",
                "conditions",
                "temp",
                "tempmin",
                "tempmax",
                "preciptype",
                "precipprob",
                "precip",
                "snowdepth",
                "snow",
                "windspeed",
                "winddir",
                "windgust",
                "humidity",
                "pressure",
                "uvindex",
                "sunrise",
                "sunset",
            ],
        )
        return data
