from sunbot.core import APIHandler

class WeatherAPIHandler(APIHandler):
    """"""

    def get_rain_data(self, location_name: str, period: str = "aujourd'hui") -> dict:
        """"""
        raise NotImplementedError

    def get_current_weather_data(self, location_name:str) -> dict:
        """"""
        raise NotImplementedError

    def get_daily_weather_data(self, location_name:str) -> dict:
        """"""
        raise NotImplementedError
