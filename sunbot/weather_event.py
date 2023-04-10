"""
Weather Event module
"""

from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import logging
from typing import Dict, Literal

import discord
from sunbot.location import Location
from sunbot.weather.Meteo import create_daily_weather_img
import sunbot.sunbot as sunbot
import sunbot.WeatherAPIHandler as weather_api_handler


USER_SUB_TYPE = 'u'
SERVER_SUB_TYPE = 's'
SUB_TYPE_LIST = [USER_SUB_TYPE, SERVER_SUB_TYPE]
SubType = Literal['u', 's']


# One class for all locations in order to not have too many tasks running in the same time
class WeatherEvent(ABC):
    """Abstract class representing a general weather event. Because this class
    is abstract, it cannot be directly instantiate
    """

    def __init__(self) -> None:
        """Constructor for this class, which can only be called by inheriting classes"""

        # private attributes:
        self.__sub_locations_dict : dict[str, dict[Location, dict[int, discord.Interaction]]] = \
            {SERVER_SUB_TYPE : {}, USER_SUB_TYPE : {}}
        self.__mutex_access_dict = asyncio.Lock()    # Mutex to handle access to user dict

    async def get_subscribers_list(self, sub_type : SubType) -> dict[Location, dict[int, discord.Interaction]]:
        """ Return a dictionnary containing entities that subscribed to each
        location. Possible value for `sub_type` is `SERVER_SUB_TYPE` for servers
        and `USER_SUB_TYPE` for users. Returned dictionnary is a shallow copy of
        the original one, so directly modifying it can be dangerous.
        ## Parameters:
        * `sub_type`: type of subscribers to retrieve, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        ## Return value:
        A dictionnary that contains subscribers (server or user) for each registered
        location
        ## Exceptions:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Argument checking:
        self.check_sub_type(sub_type)
        await self.__mutex_access_dict.acquire()
        #Get dictionnary corresponding to sub_type value
        sub_type_dict = self.__sub_locations_dict[sub_type]
        dict_to_return = sub_type_dict.copy()  # /!\ shallow copy
        self.__mutex_access_dict.release()
        return dict_to_return

    async def get_interaction(self, sub_type : SubType, sub_id : int, location_name : str) -> discord.Interaction:
        """Return discord interaction linked to the specified `entity_id` and
        `location_name`. Possible value for `sub_type` is `SERVER_SUB_TYPE` for
        servers and `USER_SUB_TYPE` for users
        ## Parameters:
        * `sub_type`: type of subscribers, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `sub_id`: subscriber ID
        * `location_name`: name of the location
        ## Return value:
        Discord interaction corresponding to the specified `entity_id` and
        `location name`
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Argument checking:
        self.check_sub_type(sub_type)
        await self.__mutex_access_dict.acquire()
        sub_type_dict = self.__sub_locations_dict[sub_type]
        try:
            for location in sub_type_dict:
                if location.name == location_name:
                    interaction = sub_type_dict[Location(location_name, "")][sub_id]
        except KeyError as err:
            logging.error(err.__cause__)
            return None
        finally:
            self.__mutex_access_dict.release()
        return interaction

    async def is_sub2location(self, sub_type : SubType, sub_id : int, location_name : str) -> bool:
        """Return whether the entity corresponding to the specified `entity_id`
        subscribed to the indicated `location_name` or not. Possible value for
        `sub_type` is `SERVER_SUB_TYPE` for servers and `USER_SUB_TYPE` for users
        ## Parameters:
        * `sub_type`: type of subscribers to retrieve, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `sub_id`: subscriber ID
        * `location_name`: name of the location
        ## Return value:
        `True` if the subscriber listen to the specified location, `False`
        otherwise
        ##Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Argument checking:
        self.check_sub_type(sub_type)
        await self.__mutex_access_dict.acquire()
        sub_type_dict = self.__sub_locations_dict[sub_type]
        location_sub_dict = sub_type_dict.get(Location(location_name, ""), {})
        sub_in_dict = sub_id in location_sub_dict
        self.__mutex_access_dict.release()
        return sub_in_dict

    async def add_sub2location(self, sub_type : SubType, interaction : discord.Interaction, location_name : str, location_tz="") -> None:
        """Add an entity contained in the specified `interaction `to the `location_name`
        dict of subscribers.Possible value for `sub_type` is `SERVER_SUB_TYPE`
        for servers and `USER_SUB_TYPE` for users. If the entity was already added
        to the location, the corresponding interaction is updated.
        ## Parameters:
        * `sub_type`: type of subscribers to retrieve, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `interaction`: Discord interaction, use to retrieve context data
        * `location_name`: name of the location to which specified user whish
        to subscribe
        * `location_tz`: time zone of the location, optional
        ## Return value:
        Not applicable
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Argument checking:
        self.check_sub_type(sub_type)
        #Retrieve entity ID:
        if sub_type == USER_SUB_TYPE:
            sub_id = interaction.user.id
        else:
            sub_id = interaction.guild.id
        # It is not needed to check if entity was already added, the corresponding
        # discord interaction will just be updated
        await self.__mutex_access_dict.acquire()
        current_location = Location(location_name, location_tz)
        # If location is not yet known by the bot:
        if current_location not in self.__sub_locations_dict[sub_type]:
            self.__sub_locations_dict[sub_type][current_location] = {}
        self.__sub_locations_dict[sub_type][current_location][sub_id] = interaction
        self.__mutex_access_dict.release()
        logging.info("Subscriber n°%d was successfully added to the list for the location %s", sub_id, location_name)

    async def del_sub_from_location(self, sub_type : SubType, sub_id : int, location_name : str) -> bool:
        """Delete subscriber whose ID is specified in argument from the list
        of subscribers for the indicated `location_name`. Possible value for
        `sub_type` is `SERVER_SUB_TYPE` for servers and `USER_SUB_TYPE` for users.
        ## Parameters:
        * `sub_type`: type of subscribers to retrieve, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `sub_id`: sub ID to delete from the list of subscribers
        * `location_name`: name of the location from which the subsriber will be
        deleted
        ## Return value:
        `True` if the sub ID was successfully deleted from the list of
        subscribers for the specified location, `False` otherwise
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Argument checking:
        self.check_sub_type(sub_type)
        # If specified subscriber was not added to the indicated location, do
        # nothing:
        if not await self.is_sub2location(sub_type, sub_id, location_name):
            logging.warning("Subscriber n°%d has no subscribed to the location %s", sub_id, location_name)
            return False
        location = Location(location_name, "")
        await self.__mutex_access_dict.acquire()
        self.__sub_locations_dict[sub_type][location].pop(sub_id)
        # If there is no subscriber remaning for the location, delete it for memory saving
        if self.__sub_locations_dict[sub_type][location] == {}:
            self.__sub_locations_dict[sub_type].pop(location)
        self.__mutex_access_dict.release()
        logging.info("Subscriber n°%d was successfully removed from the list for the location %s", sub_id, location_name)
        return True

    @staticmethod
    def check_sub_type(sub_type : SubType):
        """
        """
        if sub_type not in SUB_TYPE_LIST:
            logging.error("Unknown subscriber type %s", sub_type)
            raise ValueError("Unknown subscriber type")

    @abstractmethod
    async def run_event_task(self):
        """Abstract method that listen for an event and handle it when it is
        triggered. Must be implemented by inheriting classes
        """


class DailyWeatherEvent(WeatherEvent):
    """Class that handle daily weather event and send it to subscriber
    """

    def __init__(self) -> None:
        super().__init__()
        # Flag that indicates if daily weather was sent or not for each location:
        self.__dict_weather_sent_flag : Dict[str, Dict[Location, bool]] = \
            {SERVER_SUB_TYPE : {}, USER_SUB_TYPE : {}}
        self.__mutex_dict_flag = asyncio.Lock()

    async def get_location_flag(self, sub_type : SubType, location : Location) -> bool:
        """Return the flag for the specified location and subscriber type. The
        value of the flag is `True` if the daily weather was already sent for the
        location and subscriber type, `False` otherwise. Possible value for
        `sub_type` is `SERVER_SUB_TYPE` for servers and `USER_SUB_TYPE` for users.
        ## Parameters:
        * `sub_type`: type of subscribers to retrieve, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `location`: location for which flag has to be retrieved
        ## Return value:
        A boolean representing the flag value
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Argument checking:
        self.check_sub_type(sub_type)
        flag = False
        await self.__mutex_dict_flag.acquire()
        try:
            flag = self.__dict_weather_sent_flag[sub_type][location]
        except KeyError:
            logging.error("Specified location (%s) is not in daily weather flag", location.name)
        finally:
            self.__mutex_dict_flag.release()
        return flag

    async def set_location_flag(self, sub_type : SubType, location : Location, value : bool) -> None:
        """Set the flag for the specified subscriber type and location to the
        indicated value. Possible value for `sub_type` is `SERVER_SUB_TYPE` for
        servers and `USER_SUB_TYPE` for users.
        ## Parameters:
        * `sub_type`: type of subscribers to retrieve, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `location` : location for which flag has to be set
        * `value`: `True` or `False`
        ## Return value:
        Not applicable
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Argument checking:
        self.check_sub_type(sub_type)
        await self.__mutex_dict_flag.acquire()
        self.__dict_weather_sent_flag[sub_type][location] = value
        self.__mutex_dict_flag.release()

    async def add_sub2location(self, sub_type : SubType, interaction : discord.Interaction, location_name : str, location_tz : str = "") -> bool:
        """Add an entity contained in the specified `interaction `to the `location_name`
        dict of subscribers.Possible value for `sub_type` is `SERVER_SUB_TYPE`
        for servers and `USER_SUB_TYPE` for users. If the entity was already added
        to the location, the corresponding interaction is updated.
        ## Parameters:
        * `sub_type`: type of subscribers to retrieve, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `interaction`: Discord interaction, use to retrieve context data
        * `location_name`: name of the location to which specified user whish
        to subscribe
        * `location_tz`: time zone of the location, optional
        ## Return value:
        `True` if the subscriber was successfully added, `False` otherwise
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Only add specified location if there is not already known by the task:
        location = Location(location_name, location_tz)
        if location not in self.__dict_weather_sent_flag[sub_type]:
            # Add current location to the task:
            await self.set_location_flag(sub_type, location, False)
        return (await super().add_sub2location(sub_type, interaction, location_name, location_tz))

    async def run_event_task(self):
        logging.info("Starting daily weather task")
        # Run forever:
        while True:
            await asyncio.sleep(60)
            # Check for each known location if it is the time to send the daily
            # weather or reset flag:
            for sub_type in SUB_TYPE_LIST:
                for location, sub_dict in (await self.get_subscribers_list(sub_type)).items():
                    loc_cur_h = int(datetime.now(location.tz).strftime("%H"))
                    loc_cur_min = int(datetime.now(location.tz).strftime("%M"))
                    # Check if it is the time to reset flag. It is reset between 0h00 and 0h01:
                    if(loc_cur_h == sunbot.DAILY_WEATHER_RESET_HOUR) and (loc_cur_min in [0, 1]):
                        await self.set_location_flag(sub_type, location, False)
                    elif(loc_cur_h == sunbot.DAILY_WEATHER_SEND_HOUR) and (loc_cur_min in [0, 1]) and not await self.get_location_flag(sub_type, location):
                        await self.set_location_flag(sub_type, location, True)
                        await self.__send_daily_weather2sub(location, sub_type, sub_dict)

    async def __send_daily_weather2sub(self, location : Location, sub_type : SubType, sub_dict : Dict[int, discord.Interaction]) -> None:
        """Private method that sends daily weather for the specified location to
        all subscribers. Possible value for `sub_type` is `SERVER_SUB_TYPE` for
        servers and `USER_SUB_TYPE` for users.
        ## Parameters:
        * `location`: location for which the weather is sent to all subscribing servers
        * `sub_type`: type of subscribers to retrieve, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `sub_dict`: dict of subscribers
        ## Return value:
        None
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        self.check_sub_type(sub_type)
        # Get daily weather response from the API for current location:
        request_response = weather_api_handler.dailyWeatherRequest(location.name)
        # If a response was sent by the weather API:
        if request_response != {}:
            create_daily_weather_img(request_response, "./Data/Images")
            # Send data for current location on each registered server:
            for sub_id in sub_dict:
                # Get interaction for current server, which contains a channel
                # where send daily weather:
                interaction = sub_dict[sub_id]
                # Send daily weather:
                logging.info("Sending daily weather for %s to subscriber n°%d", location.name, sub_id)
                if sub_type == SERVER_SUB_TYPE:
                    await interaction.channel.send(content=f"Voici la météo prévue pour aujourd'hui à {location.name}\n", file=discord.File(f"{sunbot.DAILY_IMAGE_PATH}{sunbot.DAILY_IMAGE_NAME}"))
                else:
                    await interaction.user.send(content=f"Voici la météo prévue pour aujourd'hui à {location.name}\n", file=discord.File(f"{sunbot.DAILY_IMAGE_PATH}{sunbot.DAILY_IMAGE_NAME}"))
                await asyncio.sleep(0.1)


#TODO implement weather alert event handling
class WeatherAlertEvent(WeatherEvent):
    """"""

    def __init__(self) -> None:
        super().__init__()

    async def run_event_task(self):
        """"""
        pass