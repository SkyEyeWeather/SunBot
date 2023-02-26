from abc import ABC, abstractmethod
from copy import deepcopy
import asyncio
import logging

from discord import Interaction
from sunbot.SunUser import SunUser
from sunbot.SunServer import SunServer


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
        dict_to_return = deepcopy(self.__users_location_dict)
        self.__mutex_users_dict.release()
        return dict_to_return
    

    async def get_server_location_dict(self) -> dict:
        """"""
        await self.__mutex_servers_dict.acquire()
        dict_to_return = deepcopy(self.__servers_location_dict)
        self.__mutex_servers_dict.release()
        return dict_to_return


    async def is_usr_sub2location(self, user : SunUser, location_name : str) -> bool:
        """"""
        await self.__mutex_users_dict.acquire()
        location_users_list = self.__users_location_dict.get(location_name, [])
        user_in_list = (user in location_users_list)
        self.__mutex_users_dict.release()
        return user_in_list


    async def add_usr2location(self, user : SunUser, location_name : str) -> bool:
        """"""
        if not await self.is_usr_sub2location(user, location_name):
            await self.__mutex_users_dict.acquire()
            if not location_name in self.__users_location_dict:
                self.__users_location_dict[location_name] = []
            self.__users_location_dict[location_name].append(user)
            self.__mutex_users_dict.release()
            logging.info(f"User n°{user.id} was successfully added to the list for the location {location_name}")
            return True
        logging.warning(f"User n°{user.id} is already listening for the location {location_name}. Do nothing")
        return False


    async def del_usr_from_location(self, user : SunUser, location_name : str) -> bool:
        """"""
        if not await self.is_usr_sub2location(user, location_name):
            logging.warning(f"User n°{user.id} has no subscribed to the location {location_name}")
            return False
        await self.__mutex_users_dict.acquire()
        self.__users_location_dict[location_name].remove(user)
        self.__mutex_users_dict.release()
        logging.info(f"User n°{user.id} was successfully removed from the list for the location {location_name}")
        return True


    async def is_srv_sub2location(self, server : SunServer, location_name : str) -> bool:
        """"""
        await self.__mutex_servers_dict.acquire()
        location_srv_dict = self.__servers_location_dict.get(location_name, {})
        srv_in_dict = (server.id in location_srv_dict)
        self.__mutex_servers_dict.release()
        return srv_in_dict


    async def add_srv2location(self, server : SunServer, interaction : Interaction, location_name : str) -> bool:
        """"""
        if not await self.is_srv_sub2location(server, location_name):
            await self.__mutex_servers_dict.acquire()
            if not location_name in self.__servers_location_dict:
                self.__servers_location_dict[location_name] = {}
            self.__servers_location_dict[location_name][server.id] = interaction
            self.__mutex_servers_dict.release()
            logging.info(f"Server n°{server.id} was successfully added to the list for the location {location_name}")
            return True
        logging.warning(f"User n°{server.id} is already listening for the location {location_name}. Do nothing")
        return False


    async def del_srv_from_location(self, server : SunServer, location_name : str) -> bool:
        """"""
        if not await self.is_srv_sub2location(server, location_name):
            logging.warning(f"User n°{server.id} has no subscribed to the location {location_name}")
            return False
        await self.__mutex_servers_dict.acquire()
        self.__servers_location_dict[location_name].pop(server)
        self.__mutex_servers_dict.release()
        logging.info(f"User n°{server.id} was successfully removed from the list for the location {location_name}")
        return True


    @abstractmethod
    def run_event_task(self):
        pass


class DailyWeatherEvent(WeatherEvent):
    """"""

    def __init__(self) -> None:
        super().__init__()
    

    def run_event_task(self):
        """"""
        pass


class WeatherAlertEvent(WeatherEvent):
    """"""

    def __init__(self) -> None:
        super().__init__()


    def run_event_task(self):
        """"""
        pass 