from abc import ABC, abstractmethod
import asyncio
import logging
import time

import discord
from sunbot.location import Location
from sunbot.weather.Meteo import create_daily_weather_img
import sunbot.sunbot as sunbot
import sunbot.WeatherAPIHandler as weather_api_handler


#One class for all locations in order to not have too many tasks running in the same time
class WeatherEvent(ABC):
    """Abstract class that represent a general weather event. Because this class
    is abstract, it cannot be directly instantiate
    """

    def __init__(self) -> None:
        """Constructor for this class, which can only be called by inheriting classes"""

        #private attributes:
        self.__users_location_dict : dict[Location, list[int]] = {}                         #Dict containing user that subscribed to each location
        self.__servers_location_dict : dict[Location, dict[int, discord.Interaction]] = {}  #Dict containing server that subscribed to each location
        self.__mutex_users_dict = asyncio.Lock()    #Mutex to handle access to user dict
        self.__mutex_servers_dict = asyncio.Lock()  #Mutex to handle access to server dict


    async def get_users_location_dict(self) -> dict[Location, list[int]] :
        """ Return dictionary containing ID of all users that subscribed to
        each location. Thus, in the returned dict, location names are the keys
        and list of ID the values
        """
        await self.__mutex_users_dict.acquire()
        dict_to_return = self.__users_location_dict.copy() #/!\ shallow copy
        self.__mutex_users_dict.release()
        return dict_to_return


    async def get_server_location_dict(self) -> dict[Location, dict[int, discord.Interaction]]:
        """Return dictionnary containing ID of all servers that subsribed to each
        location. Thus, in the returned dict, location names are the keys and list
        of ID the values
        """
        dict_to_return = {}
        await self.__mutex_servers_dict.acquire()
        dict_to_return = self.__servers_location_dict.copy() #/!\ shallow copy
        self.__mutex_servers_dict.release()
        return dict_to_return
    

    async def get_interaction(self, server_id : int, location_name : str) -> discord.Interaction:
        """Return discord interaction linked to the specified `server_id` and
        `location_name`

        ## Parameters:
        * `server_id`: server ID 
        * `location_name`: name of the location
        ## Return value:
        Discord interaction corresponding to the specified `server_id` and
        `location name`
        """
        await self.__mutex_servers_dict.acquire()
        try:
            for location in self.__servers_location_dict:
                if location.name == location_name:
                    interaction = self.__servers_location_dict[Location(location_name, "")][server_id]
        except KeyError as e:
            logging.error(e.__cause__)
            return None
        finally:
            self.__mutex_servers_dict.release()
        return interaction
        

    async def is_usr_sub2location(self, user_id : int, location_name : str) -> bool:
        """Return wether the user corresponding to specified `user_id` subscribed

        to the indicated `location_name` or not.
        ## Parameters:
        * `user_id`: user ID
        * `location_name`: name of the location
        ## Return value:
        `True` if the user subrscribed to specified location, `False` otherwise
        """
        await self.__mutex_users_dict.acquire()
        location_users_list = self.__users_location_dict.get(Location(location_name, ""), [])
        user_in_list = (user_id in location_users_list)
        self.__mutex_users_dict.release()
        return user_in_list


    async def add_usr2location(self, user_id : int, location_name : str, location_tz = "") -> bool:
        """Add user whose Discord ID is specified to the `location_name` list
        of subscribers

        ## Parameters:
        * `user_id`: user ID to add to the list of subscriber
        * `location_name`: name of the location to which specified user whish
        to subscribe
        * `location_tz`: time zone of the location, optional
        ## Return value:
        `True` if the user was successfully added, `False` otherwise
        """
        if not await self.is_usr_sub2location(user_id, location_name):
            await self.__mutex_users_dict.acquire()
            current_location = Location(location_name, location_tz)
            if not current_location in self.__users_location_dict:
                self.__users_location_dict[current_location] = []
            self.__users_location_dict[location_name].append(user_id)
            self.__mutex_users_dict.release()
            logging.info(f"User n°{user_id} was successfully added to the list for the location {location_name}")
            return True
        logging.warning(f"User n°{user_id} is already listening for the location {location_name}. Do nothing")
        return False


    async def del_usr_from_location(self, user_id : int, location_name : str) -> bool:
        """Delete specified `user_id` from the list of subscribers for the
        indicated `location_name`

        ## Parameters:
        * `user_id`: user ID to delete from the list of subscribers
        * `location_name`: name of the location from which the user will be 
        deleted
        ## Return value:
        `True` if the user ID was successfully deleted from the list of 
        subscribers for the specified location, `False` otherwise
        """
        if not await self.is_usr_sub2location(user_id, location_name):
            logging.warning(f"User n°{user_id} has no subscribed to the location {location_name}")
            return False
        await self.__mutex_users_dict.acquire()
        self.__users_location_dict[Location(location_name, "")].remove(user_id)
        self.__mutex_users_dict.release()
        logging.info(f"User n°{user_id} was successfully removed from the list for the location {location_name}")
        return True


    async def is_srv_sub2location(self, server_id : int, location_name : str) -> bool:
        """Return wether the server corresponding to specified `server_id` 
        subscribed to the indicated `location_name` or not.

        ## Parameters:
        * `server_id`: user ID
        * `location_name`: name of the location
        ## Return value:
        `True` if the server subrscribed to specified location, `False` otherwise
        """
        await self.__mutex_servers_dict.acquire()
        location_srv_dict = self.__servers_location_dict.get(Location(location_name, ""), {})
        srv_in_dict = (server_id in location_srv_dict)
        self.__mutex_servers_dict.release()
        return srv_in_dict


    async def add_srv2location(self, interaction : discord.Interaction, location_name : str, location_tz : str = "") -> bool:
        """Add server whose Discord ID is specified to the `location_name` list
        of subscribing servers, with indicated discord `interaction`

        ## Parameters:
        * `interaction` : Discord interaction, used to retrieve context data
        * `location_name`: name of the location to which specified user whish
        to subscribe
        * `location_tz` : time zone of the location, optional
        ## Return value:
        `True` if the server was successfully added, `False` otherwise
        """
        server_id = interaction.guild_id
        if not await self.is_srv_sub2location(server_id, location_name):
            await self.__mutex_servers_dict.acquire()
            current_location = Location(location_name, location_tz)
            if not location_name in self.__servers_location_dict:
                self.__servers_location_dict[current_location] = {}
            self.__servers_location_dict[current_location][server_id] = interaction
            self.__mutex_servers_dict.release()
            logging.info(f"Server n°{server_id} was successfully added to the list for the location {location_name}")
            return True
        logging.warning(f"User n°{server_id} is already listening for the location {location_name}. Do nothing")
        return False


    async def del_srv_from_location(self, server_id : int, location_name : str) -> bool:
        """Delete specified `server_id` from the list of subscribing servers for the
        indicated `location_name`

        ## Parameters:
        * `user_id`: user ID to delete from the list of subscribers
        * `location_name`: name of the location from which the server will be 
        deleted
        ## Return value:
        `True` if the server ID was successfully deleted from the list of 
        subscribing servers for the specified location, `False` otherwise
        """
        if not await self.is_srv_sub2location(server_id, location_name):
            logging.warning(f"User n°{server_id} has no subscribed to the location {location_name}")
            return False
        await self.__mutex_servers_dict.acquire()
        self.__servers_location_dict[Location(location_name, "")].pop(server_id)
        self.__mutex_servers_dict.release()
        logging.info(f"User n°{server_id} was successfully removed from the list for the location {location_name}")
        return True


    @abstractmethod
    async def run_event_task(self):
        """Abstract method that listen for an event and handle it when it is
        triggered. Must be implemented by inheriting classes
        """
        pass


class DailyWeatherEvent(WeatherEvent):
    """Class that handle daily weather event"""

    def __init__(self) -> None:
        super().__init__()
        self.weather_sent = False   #Flag that indicates if daily weather was sent or not


    async def run_event_task(self):
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
            elif (current_hour == sunbot.DAILY_WEATHER_SEND_UTC_HOUR) and (current_minute in[0, 1]) and not self.weather_sent:
            #elif (current_hour == sunbot.DAILY_WEATHER_SEND_UTC_HOUR) and (current_minute in[0, 1])and not self.weather_sent:
                self.weather_sent = True
                #Send daily weather on all registered servers, for all location:
                await self.__send_daily_weather2srv()
                #Send daily weather to all the users registered for all location:
                await self.__send_daily_weather2usr()
    

    async def __send_daily_weather2srv(self) -> None:
        """Private method that send daily weather for all location on all
        subscribing servers
        """
        for location, server_dict in (await self.get_server_location_dict()).items():
            #Get daily weather response from the API for current location:
            request_response = weather_api_handler.dailyWeatherRequest(location.name)
            if request_response != {}:
                create_daily_weather_img(request_response, "./Data/Images")
            #Send data for current location on each registered server
            for server in server_dict:
                #Get interaction for current server, which contain a channel
                #where send daily weather:
                interaction : discord.Interaction = server_dict[server]
                #Send daily weather:
                await interaction.channel.send(content=f"Voici la météo prévue pour aujourd'hui à {location.name}\n", file=discord.File(f"{sunbot.DAILY_IMAGE_PATH}{sunbot.DAILY_IMAGE_NAME}"))
                await asyncio.sleep(0.1)


    async def __send_daily_weather2usr(self) -> None:
        """"""
        pass #TODO : Send daily weather to all registered users, in PM


#TODO implement weather alert event handling
class WeatherAlertEvent(WeatherEvent):
    """"""

    def __init__(self) -> None:
        super().__init__()


    async def run_event_task(self):
        """"""
        pass