"""Weather Event module"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Literal, Union

import discord

from sunbot.location import Location
from sunbot.weather.Meteo import create_daily_weather_img
from sunbot import sunbot
from sunbot.apis.weather import WeatherAPIHandler

USER_SUB_TYPE = "u"
SERVER_SUB_TYPE = "s"
SUB_TYPE_LIST = [USER_SUB_TYPE, SERVER_SUB_TYPE]
SubType = Literal["u", "s"]


# One class for all locations in order to not have too many tasks running in the same time
class WeatherEvent(ABC):
    """Abstract class representing a general weather event. Because this class
    is abstract, it cannot be directly instantiate
    """

    def __init__(self, save_path : str, api_handler: WeatherAPIHandler) -> None:
        """Constructor for this class, which can only be called by inheriting classes
        ## Parameters:
        * `save_path`: path to the file where saving locations' subscribers data
        * `api_handler`: API handler
        """
        # private attributes:
        self.save_file_path = save_path
        self.api_handler = api_handler
        self.__sub_locations_dict : dict[str, dict[Location, dict[int, Union[discord.TextChannel, discord.User]]]] = \
            {SERVER_SUB_TYPE : {}, USER_SUB_TYPE : {}}
        self.__mutex_access_dict = asyncio.Lock()    # Mutex to handle access to user dict

    async def get_subscribers_list(
        self, sub_type: SubType
    ) -> dict[Location, dict[int, discord.Interaction]]:
        """Return a dictionnary containing entities that subscribed to each
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
        # Get dictionnary corresponding to sub_type value
        sub_type_dict = self.__sub_locations_dict[sub_type]
        dict_to_return = sub_type_dict.copy()  # /!\ shallow copy
        self.__mutex_access_dict.release()
        return dict_to_return

    async def get_sub_entity(
        self, sub_type: SubType, sub_id: int, location_name: str
    ) -> Union[discord.TextChannel, discord.User]:
        """Return discord object linked to the specified `entity_id` and
        `location_name`. Possible value for `sub_type` is `SERVER_SUB_TYPE` for
        servers and `USER_SUB_TYPE` for users
        ## Parameters:
        * `sub_type`: type of subscribers, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        * `sub_id`: subscriber ID
        * `location_name`: name of the location
        ## Return value:
        Discord object corresponding to the specified `entity_id` and
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
                    sub_entity = sub_type_dict[Location(location_name, "")][sub_id]
        except KeyError as err:
            logging.error(err.__cause__)
            return None
        finally:
            self.__mutex_access_dict.release()
        return sub_entity

    async def is_sub2location(
        self, sub_type: SubType, sub_id: int, location_name: str
    ) -> bool:
        """Return whether the entity corresponding to the specified `entity_id`
        subscribed to the indicated `location_name` or not. Possible value for
        `sub_type` is `SERVER_SUB_TYPE` for servers and `USER_SUB_TYPE` for users
        ## Parameters:
        * `sub_type`: type of subscribers to check, `SERVER_SUB_TYPE` for server,
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

    async def add_sub2location(
        self,
        subscriber: Union[discord.TextChannel, discord.User],
        location_name: str,
        location_tz="",
    ) -> None:
        """Add an entity contained in the specified `interaction `to the `location_name`
        dict of subscribers.Possible value for `sub_type` is `SERVER_SUB_TYPE`
        for servers and `USER_SUB_TYPE` for users. If the entity was already added
        to the location, the corresponding interaction is updated.
        ## Parameters:
        * `subscriber`: discord subscriber entity, must be a `TextChannel` or an
        `User`.
        * `location_name`: name of the location to which specified user whish
        to subscribe
        * `location_tz`: time zone of the location, optional
        ## Return value:
        Not applicable
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # Check subscriber type:
        if isinstance(subscriber, (discord.User, discord.Member)):
            sub_id = subscriber.id
            sub_type = USER_SUB_TYPE
        elif isinstance(subscriber, discord.TextChannel):
            sub_id = subscriber.guild.id
            sub_type = SERVER_SUB_TYPE
        else:
            raise ValueError(f"Unknown subscriber type {type(subscriber)}")
        # It is not needed to check if entity was already added, the corresponding
        # discord interaction will just be updated
        await self.__mutex_access_dict.acquire()
        current_location = Location(location_name, location_tz)
        # If location is not yet known by the bot:
        if current_location not in self.__sub_locations_dict[sub_type]:
            self.__sub_locations_dict[sub_type][current_location] = {}
        self.__sub_locations_dict[sub_type][current_location][sub_id] = subscriber
        self.__mutex_access_dict.release()
        logging.info(
            "Subscriber n°%d was successfully added to the list for the location %s",
            sub_id,
            location_name,
        )

    async def del_sub_from_location(
        self, sub_type: SubType, sub_id: int, location_name: str
    ) -> bool:
        """Delete subscriber whose ID is specified in argument from the list
        of subscribers for the indicated `location_name`. Possible value for
        `sub_type` is `SERVER_SUB_TYPE` for servers and `USER_SUB_TYPE` for users.
        ## Parameters:
        * `sub_type`: type of subscribers to remove, `SERVER_SUB_TYPE` for server,
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
            logging.warning(
                "Subscriber n°%d has no subscribed to the location %s",
                sub_id,
                location_name,
            )
            return False
        location = Location(location_name, "")
        await self.__mutex_access_dict.acquire()
        self.__sub_locations_dict[sub_type][location].pop(sub_id)
        # If there is no subscriber remaning for the location, delete it for memory saving
        if self.__sub_locations_dict[sub_type][location] == {}:
            self.__sub_locations_dict[sub_type].pop(location)
        self.__mutex_access_dict.release()
        logging.info(
            "Subscriber n°%d was successfully removed from the list for the location %s",
            sub_id,
            location_name,
        )
        return True

    @staticmethod
    def check_sub_type(sub_type: SubType) -> None:
        """Check whether sub type correspond to a known type of subscriber.
        ## Parameters:
        * `sub_type`: type of subscribers, `SERVER_SUB_TYPE` for server,
        `USER_SUB_TYPE` for user
        ## Return value:
        None
        ## Exception:
         * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        if sub_type not in SUB_TYPE_LIST:
            logging.error("Unknown subscriber type %s", sub_type)
            raise ValueError("Unknown subscriber type")

    async def save_locations_subscribers(self) -> None:
        """Save all locations' subscribers into a file at JSON format"""
        logging.info("Saving locations' subscribers data...")
        await self.__mutex_access_dict.acquire()
        copy_dict = {}
        for sub_type, sub_dict in self.__sub_locations_dict.items():
            copy_dict[sub_type] = []
            for location, location_subs_dict in sub_dict.items():
                # Replace location by their name and tz to allow serialization:
                location_dict = {
                    "name": location.name,
                    "tz": str(location.tz),
                    "subscribers": [],
                }
                # Only subsribers' id need to be saved:
                for sub_id, entity in location_subs_dict.items():
                    subscriber_dict = {"sub_id": sub_id, "entity_id": entity.id}
                    location_dict["subscribers"].append(subscriber_dict)
                copy_dict[sub_type].append(location_dict)
        self.__mutex_access_dict.release()
        with open(self.save_file_path, "w", encoding="UTF-8") as json_file:
            json.dump(copy_dict, json_file, ensure_ascii=False, indent=2)
        os.chmod(self.save_file_path, mode=0o777)
        logging.info("Location's subscribers data saved into %s", self.save_file_path)

    async def load_locations_subscribers(self, usr_loader, channel_loader) -> None:
        """Load data from a JSON save file into the structure that contains
        entities that subscribe to each location
        ## Parameters:
        * `usr_loader`: function or method used to load a discor user
        * `srv_loader`: function or method used to load a discord server
        ## Return value:
        None
        ## Exceptions:
        * `FileNotFoundError` in the case where save file is not found
        """
        logging.info("Loading subscriber data for each location...")
        loaded_dict = {}
        try:
            with open(self.save_file_path, "r", encoding="UTF-8") as json_file:
                loaded_dict = json.load(json_file)
        except FileNotFoundError:
            logging.error(
                "Unable to load data from the JSON file at %s : file not found",
                self.save_file_path,
            )
        # Copy loaded dict into subscribers structure:
        for sub_type, locations_dict_list in loaded_dict.items():
            for location_dict in locations_dict_list:
                location = Location(location_dict["name"], location_dict["tz"])
                for sub_dict in location_dict["subscribers"]:
                    if sub_type == USER_SUB_TYPE:
                        subscriber = usr_loader(sub_dict["sub_id"])
                    else:
                        subscriber = channel_loader(sub_dict["entity_id"])
                    # subscriber is None if current subscriber is not linked to an
                    # existent discord entity:
                    if subscriber is None:
                        logging.error(
                            "Subscriber %d does not correspond to any discord entity",
                            sub_dict["sub_id"],
                        )
                        continue  # Do not add a None subscriber, as it can broke the bot
                    await self.add_sub2location(
                        subscriber, location.name, str(location.tz)
                    )
        logging.info("Subscribers data was successfully loaded")

    @abstractmethod
    async def run_event_task(self):
        """Abstract method that listen for an event and handle it when it is
        triggered. Must be implemented by inheriting classes
        """


class DailyWeatherEvent(WeatherEvent):
    """Class that handle daily weather event and send it to subscriber"""

    def __init__(self, save_path: str, api_handler: WeatherAPIHandler) -> None:
        super().__init__(save_path, api_handler)
        # Flag that indicates if daily weather was sent or not for each location:
        self.__dict_weather_sent_flag: Dict[str, Dict[Location, bool]] = {
            SERVER_SUB_TYPE: {},
            USER_SUB_TYPE: {},
        }
        self.__mutex_dict_flag = asyncio.Lock()

    async def get_location_flag(self, sub_type: SubType, location: Location) -> bool:
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
            logging.error(
                "Specified location (%s) is not in daily weather flag", location.name
            )
        finally:
            self.__mutex_dict_flag.release()
        return flag

    async def set_location_flag(
        self, sub_type: SubType, location: Location, value: bool
    ) -> None:
        """Set the flag for the specified subscriber type and location to the
        indicated value. Possible value for `sub_type` is `SERVER_SUB_TYPE` for
        servers and `USER_SUB_TYPE` for users.
        ## Parameters:
        * `sub_type`: type of subscribers, `SERVER_SUB_TYPE` for server,
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

    async def add_sub2location(
        self,
        subscriber: Union[discord.TextChannel, discord.User],
        location_name: str,
        location_tz: str = "",
    ) -> bool:
        """Add an entity contained in the specified `interaction `to the `location_name`
        dict of subscribers.Possible value for `sub_type` is `SERVER_SUB_TYPE`
        for servers and `USER_SUB_TYPE` for users. If the entity was already added
        to the location, the corresponding interaction is updated.
        ## Parameters:
        * `subscriber`: discord subscriber entity, must be a `TextChannel` or an
        `User`.
        * `location_name`: name of the location to which specified user whish
        to subscribe
        * `location_tz`: time zone of the location, optional
        ## Return value:
        Not applicable
        ## Exception:
        * `ValueError` if `sub_type` value is neither `SERVER_SUB_TYPE` nor
        `USER_SUB_TYPE`
        """
        # TODO : Unneeded double check here
        if isinstance(subscriber, (discord.User, discord.Member)):
            sub_type = USER_SUB_TYPE
        elif isinstance(subscriber, discord.TextChannel):
            sub_type = SERVER_SUB_TYPE
        else:
            raise ValueError(f"Unknown subscriber type: {type(subscriber)}")
        # Only add specified location if there is not already known by the task:
        location = Location(location_name, location_tz)
        if location not in self.__dict_weather_sent_flag[sub_type]:
            # Add current location to the task:
            await self.set_location_flag(sub_type, location, False)
        return await super().add_sub2location(subscriber, location_name, location_tz)

    async def run_event_task(self):
        try:
            logging.info("Starting daily weather task")
            # Run forever:
            while True:
                await asyncio.sleep(60)
                # Check for each known location if it is the time to send the daily
                # weather or reset flag:
                for sub_type in SUB_TYPE_LIST:
                    for location, sub_dict in (
                        await self.get_subscribers_list(sub_type)
                    ).items():
                        loc_cur_h = int(datetime.now(location.tz).strftime("%H"))
                        loc_cur_min = int(datetime.now(location.tz).strftime("%M"))
                        # Check if it is the time to reset flag. It is reset between 0h00 and 0h01:
                        if loc_cur_h == sunbot.DAILY_WEATHER_RESET_HOUR and (
                            loc_cur_min in [0, 1]
                        ):
                            await self.set_location_flag(sub_type, location, False)
                        elif (
                            loc_cur_h == sunbot.DAILY_WEATHER_SEND_HOUR
                            and (loc_cur_min in [0, 1])
                            and not await self.get_location_flag(sub_type, location)
                        ):
                            await self.set_location_flag(sub_type, location, True)
                            await self.__send_daily_weather2sub(location, sub_dict)
        except asyncio.CancelledError:
            logging.info("Stopping the daily weather task")

    async def __send_daily_weather2sub(
        self, location: Location, sub_dict: Dict[int, discord.Interaction]
    ) -> None:
        """Private method that sends daily weather for the specified location to
        all subscribers. Possible value for `sub_type` is `SERVER_SUB_TYPE` for
        servers and `USER_SUB_TYPE` for users.
        ## Parameters:
        * `location`: location for which the weather is sent to all subscribing servers
        * `sub_dict`: dict of subscribers
        ## Return value:
        None
        """
        # Get daily weather response from the API for current location:
        data = self.api_handler.get_daily_weather_data(location.name)
        # If a response was sent by the weather API:
        if data:
            create_daily_weather_img(data, "./Data/Images")
            # Send data for current location on each registered server:
            for sub_id in sub_dict:
                # Get interaction for current server, which contains a channel
                # where send daily weather:
                subscriber = sub_dict[sub_id]
                # Send daily weather to current subscriber:
                logging.info(
                    "Sending daily weather for %s to subscriber n°%d",
                    location.name,
                    sub_id,
                )
                await subscriber.send(
                    content=f"Voici la météo prévue pour aujourd'hui à {location.name}\n",
                    file=discord.File(
                        f"{sunbot.DAILY_IMAGE_PATH}{sunbot.DAILY_IMAGE_NAME}"
                    ),
                )
                await asyncio.sleep(0.1)


class WeatherAlertEvent(WeatherEvent):
    """"""

    def __init__(self, save_path, api_handler) -> None:
        super().__init__(save_path, api_handler)
        raise NotImplementedError

    async def run_event_task(self):
        """"""
        raise NotImplementedError
