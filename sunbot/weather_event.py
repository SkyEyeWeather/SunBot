from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import logging
from typing import Dict

import discord
from sunbot.location import Location
from sunbot.weather.Meteo import create_daily_weather_img
import sunbot.sunbot as sunbot
import sunbot.WeatherAPIHandler as weather_api_handler


# One class for all locations in order to not have too many tasks running in the same time
class WeatherEvent(ABC):
    """Abstract class that represent a general weather event. Because this class
    is abstract, it cannot be directly instantiate
    """

    def __init__(self) -> None:
        """Constructor for this class, which can only be called by inheriting classes"""

        # private attributes:
        self.__users_location_dict : dict[Location, list[int]] = {}                         # Dict containing user that subscribed to each location
        self.__servers_location_dict : dict[Location, dict[int, discord.Interaction]] = {}  # Dict containing server that subscribed to each location
        self.__mutex_users_dict = asyncio.Lock()    # Mutex to handle access to user dict
        self.__mutex_servers_dict = asyncio.Lock()  # Mutex to handle access to server dict

    async def get_users_location_dict(self) -> dict[Location, list[int]] :
        """ Return dictionary containing ID of all users that subscribed to
        each location. Thus, in the returned dict, location names are the keys
        and list of ID the values
        """
        await self.__mutex_users_dict.acquire()
        dict_to_return = self.__users_location_dict.copy() # /!\ shallow copy
        self.__mutex_users_dict.release()
        return dict_to_return

    async def get_server_location_dict(self) -> dict[Location, dict[int, discord.Interaction]]:
        """Return dictionnary containing ID of all servers that subsribed to each
        location. Thus, in the returned dict, location names are the keys and list
        of ID the values
        """
        dict_to_return = {}
        await self.__mutex_servers_dict.acquire()
        dict_to_return = self.__servers_location_dict.copy() # /!\ shallow copy
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

    async def add_usr2location(self, user_id : int, location_name : str, location_tz="") -> bool:
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
            if current_location not in self.__users_location_dict:
                self.__users_location_dict[current_location] = []
            self.__users_location_dict[current_location].append(user_id)
            self.__mutex_users_dict.release()
            logging.info("User n°%d was successfully added to the list for the location %s", user_id, location_name)
            return True
        logging.warning("User n°%d is already listening for the location %s. Do nothing", user_id, location_name)
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
            logging.warning("User n°{user_id} has no subscribed to the location {location_name}")
            return False
        await self.__mutex_users_dict.acquire()
        self.__users_location_dict[Location(location_name, "")].remove(user_id)
        self.__mutex_users_dict.release()
        logging.info("User n°%d was successfully removed from the list for the location", user_id)
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
            logging.info("Server n°%d was successfully added to the list for the location %s", server_id, location_name)
            return True
        logging.warning("User n°%d is already listening for the location %s. Do nothing", server_id, location_name)
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
            logging.warning("Server n°%d has no subscribed to the location %s", server_id, location_name)
            return False
        await self.__mutex_servers_dict.acquire()
        self.__servers_location_dict[Location(location_name, "")].pop(server_id)
        self.__mutex_servers_dict.release()
        logging.info("Server n°%d was successfully removed from the list for the location %s", server_id, location_name)
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
        # Flag that indicates if daily weather was sent or not for each location:
        self.__dict_weather_sent_flag : Dict[Location, bool] = {}
        self.__mutex_dict_flag = asyncio.Lock()

    async def get_location_flag(self, location : Location) -> bool:
        """Return the flag for the specified location. The value of the flag is
        `True` if the daily weather was already sent for the location, `False`
        otherwise
        ## Parameters:
        * `location`: location for which flag has to be retrieved
        ## Return value:
        A boolean representing the flag
        """
        flag = False
        await self.__mutex_dict_flag.acquire()
        try:
            flag = self.__dict_weather_sent_flag[location]
        except KeyError:
            logging.error("Specified location (%s) is not in daily weather flag", location.name)
        finally:
            self.__mutex_dict_flag.release()
        return flag

    async def set_location_flag(self, location : Location, value : bool) -> None:
        """Set the flag for the specified location to the `value` value.
        ## Parameters:
        * `location` : location for which flag has to be set
        * `value`: `True` or `False`
        ## Return value:
        Not applicable
        """
        await self.__mutex_dict_flag.acquire()
        self.__dict_weather_sent_flag[location] = value
        self.__mutex_dict_flag.release()

    async def add_srv2location(self, interaction : discord.Interaction, location_name : str, location_tz : str = "") -> bool:
        """
        """
        # Only add specified location if there is not already known by the task:
        current_location = Location(location_name, location_tz)
        if current_location not in self.__dict_weather_sent_flag:
            # Add current location to the task:
            await self.set_location_flag(current_location, False)
        return (await super().add_srv2location(interaction, location_name, location_tz))

    async def run_event_task(self):
        logging.info("Starting daily weather task")
        # Run forever:
        while True:
            await asyncio.sleep(60)
            # Check for each known location if it is the time to send the daily
            # weather or reset flag:
            for location, server_dict in (await self.get_server_location_dict()).items():
                loc_cur_h = int(datetime.now(location.tz).strftime("%H"))
                loc_cur_min = int(datetime.now(location.tz).strftime("%M"))
                # Check if it is the time to reset flag. This flag is reset between 0h00 and 0h01:
                if(loc_cur_h == sunbot.DAILY_WEATHER_RESET_HOUR) and (loc_cur_min in [0, 1]):
                    await self.set_location_flag(location, False)
                elif(loc_cur_h == sunbot.DAILY_WEATHER_SEND_HOUR) and (loc_cur_min in [0, 1]) and not await self.get_location_flag(location):
                    await self.set_location_flag(location, True)
                    await self.__send_daily_weather2srv(location, server_dict)

    @staticmethod
    async def __send_daily_weather2srv(location : Location, server_dict : Dict[int, discord.Interaction]) -> None:
        """Private method that send daily weather for all location on all
        subscribing servers.
        ## Parameters:
        * `location`: location for which the weather is sent to all subscribing servers
        * `server_dict`: dict of subscribing servers
        ## Return value:
        Not applicable
        """
        # Get daily weather response from the API for current location:
        request_response = weather_api_handler.dailyWeatherRequest(location.name)
        # If a response was sent by the weather API:
        if request_response != {}:
            create_daily_weather_img(request_response, "./Data/Images")
            # Send data for current location on each registered server:
            for server in server_dict:
                # Get interaction for current server, which contains a channel
                # where send daily weather:
                interaction = server_dict[server]
                # Send daily weather:
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