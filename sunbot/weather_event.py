from abc import ABC, abstractmethod
import asyncio
import logging
import time

import discord
from matplotlib import interactive
from sunbot.weather.Meteo import create_daily_weather_img
import sunbot.sunbot as sunbot
import sunbot.WeatherAPIHandler as weather_api_handler


#One class for all locations in order so do not have too many tasks running in the same time
class WeatherEvent(ABC):
    """"""

    def __init__(self) -> None:
        """"""

        #Public fields:
        self.__users_location_dict = {}
        self.__servers_location_dict = {}
        #private fields:
        self.__mutex_users_dict = asyncio.Lock()
        self.__mutex_servers_dict = asyncio.Lock()


    async def get_users_location_dict(self) -> dict:
        """"""
        await self.__mutex_users_dict.acquire()
        dict_to_return = self.__users_location_dict.copy() #/!\ shallow copy
        self.__mutex_users_dict.release()
        return dict_to_return


    async def get_server_location_dict(self) -> dict:
        """"""
        dict_to_return = {}
        await self.__mutex_servers_dict.acquire()
        dict_to_return = self.__servers_location_dict.copy() #/!\ shallow copy
        self.__mutex_servers_dict.release()
        return dict_to_return
    

    async def get_interaction(self, server_id : int, location_name : str) -> discord.Interaction:
        """"""
        await self.__mutex_servers_dict.acquire()
        try:
            interaction = self.__servers_location_dict[location_name][server_id]
        except KeyError as e:
            logging.error(e.__cause__)
            return None
        finally:
            self.__mutex_servers_dict.release()
        return interaction
        

    async def is_usr_sub2location(self, user_id : int, location_name : str) -> bool:
        """"""
        await self.__mutex_users_dict.acquire()
        location_users_list = self.__users_location_dict.get(location_name, [])
        user_in_list = (user_id in location_users_list)
        self.__mutex_users_dict.release()
        return user_in_list


    async def add_usr2location(self, user_id : int, location_name : str) -> bool:
        """"""
        if not await self.is_usr_sub2location(user_id, location_name):
            await self.__mutex_users_dict.acquire()
            if not location_name in self.__users_location_dict:
                self.__users_location_dict[location_name] = []
            self.__users_location_dict[location_name].append(user_id)
            self.__mutex_users_dict.release()
            logging.info(f"User n°{user_id} was successfully added to the list for the location {location_name}")
            return True
        logging.warning(f"User n°{user_id} is already listening for the location {location_name}. Do nothing")
        return False


    async def del_usr_from_location(self, user_id : int, location_name : str) -> bool:
        """"""
        if not await self.is_usr_sub2location(user_id, location_name):
            logging.warning(f"User n°{user_id} has no subscribed to the location {location_name}")
            return False
        await self.__mutex_users_dict.acquire()
        self.__users_location_dict[location_name].remove(user_id)
        self.__mutex_users_dict.release()
        logging.info(f"User n°{user_id} was successfully removed from the list for the location {location_name}")
        return True


    async def is_srv_sub2location(self, server_id : int, location_name : str) -> bool:
        """"""
        await self.__mutex_servers_dict.acquire()
        location_srv_dict = self.__servers_location_dict.get(location_name, {})
        srv_in_dict = (server_id in location_srv_dict)
        self.__mutex_servers_dict.release()
        return srv_in_dict


    async def add_srv2location(self, server_id : int, interaction : discord.Interaction, location_name : str) -> bool:
        """"""
        if not await self.is_srv_sub2location(server_id, location_name):
            await self.__mutex_servers_dict.acquire()
            if not location_name in self.__servers_location_dict:
                self.__servers_location_dict[location_name] = {}
            self.__servers_location_dict[location_name][server_id] = interaction
            self.__mutex_servers_dict.release()
            logging.info(f"Server n°{server_id} was successfully added to the list for the location {location_name}")
            return True
        logging.warning(f"User n°{server_id} is already listening for the location {location_name}. Do nothing")
        return False


    async def del_srv_from_location(self, server_id : int, location_name : str) -> bool:
        """"""
        if not await self.is_srv_sub2location(server_id, location_name):
            logging.warning(f"User n°{server_id} has no subscribed to the location {location_name}")
            return False
        await self.__mutex_servers_dict.acquire()
        self.__servers_location_dict[location_name].pop(server_id)
        self.__mutex_servers_dict.release()
        logging.info(f"User n°{server_id} was successfully removed from the list for the location {location_name}")
        return True


    @abstractmethod
    async def run_event_task(self):
        pass


class DailyWeatherEvent(WeatherEvent):
    """"""

    def __init__(self) -> None:
        super().__init__()
        self.weather_sent = False


    async def run_event_task(self):
        """"""

        logging.info("Starting daily weather task")
        #Run forever:
        while True:
            await asyncio.sleep(60)
            #Get current UTC hour:
            utc_hour = time.gmtime(time.time())
            current_hour = utc_hour[3]
            current_minute = utc_hour[4]
            #If it is the time to reset:
            if (current_hour == sunbot.DAILY_WEATHER_RESET_UTC_HOUR) and (current_minute in [0, 1]):
                self.weather_sent = False
            #Else, if it is the time to send daily weather:
            elif (current_hour == 20) and (current_minute in[56, 57]) and not self.weather_sent:
            #elif (current_hour == sunbot.DAILY_WEATHER_SEND_UTC_HOUR) and (current_minute in[0, 1])and not self.weather_sent:
                self.weather_sent = True
                #Send daily weather on all registered servers, for all location:
                await self.__send_daily_weather2srv()
                #Send daily weather to all the users registered for all location:
                await self.__send_daily_weather2usr()
    

    async def __send_daily_weather2srv(self) -> None:
        """"""
        for location_name, server_dict in (await self.get_server_location_dict()).items():
            #Get daily weather response from the API for current location:
            request_response = weather_api_handler.dailyWeatherRequest(location_name)
            if request_response != {}:
                create_daily_weather_img(request_response, "./Data/Images")
            #Send data for current location on each registered server
            for server in server_dict:
                #Get interaction for current server, which contain a channel
                #where send daily weather:
                interaction : discord.Interaction = server_dict[server]
                #Send daily weather:
                await interaction.channel.send(content=f"Voici la météo prévue pour aujourd'hui à {location_name}\n", file=discord.File(f"{sunbot.DAILY_IMAGE_PATH}{sunbot.DAILY_IMAGE_NAME}"))
                await asyncio.sleep(0.1)


    async def __send_daily_weather2usr(self) -> None:
        """"""
        pass #TODO : Send daily weather to all registered users, in PM


class WeatherAlertEvent(WeatherEvent):
    """"""

    def __init__(self) -> None:
        super().__init__()


    async def run_event_task(self):
        """"""
        pass