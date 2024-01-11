"""Weather API handler class definition"""

from sunbot.core import APIHandler


class WeatherAPIHandler(APIHandler):
    """Common methods for weather API handler"""

    def get_rain_data(self, location_name: str, period: str = "aujourd'hui") -> dict:
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
        raise NotImplementedError

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
        raise NotImplementedError

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
        raise NotImplementedError
