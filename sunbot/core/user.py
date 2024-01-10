"""Sunbot users module"""

import json
import logging
from pathlib import Path

# ================================
#        CLASS DEFINITION
# ================================


class SunUser:
    """This class represents a SunBot user. Each user has an ID that allows to
    identify it in discord API. This can be used to send it a message for example.
    """

    backup_dir = None

    def __init__(
        self, usr_id: int, fav_location: str = "Toulouse", mp: bool = False
    ) -> None:
        """Constructor for this class. A SunBot user is defined by its Discord ID.
        Other informations can be provided in arguments, such as if the user authorize private
        message from the bot, or a specific favorite location for weather notifications.
        Each instance of this class is associated to a backup file. The link
        between the user and its backup file is done thanks to the user ID
        (so ID is defined as a constant and cannot be modified).
        ## Parameters:
        * `user_id`: discord identifiant of the SunBot user to create
        * `fav_location`: optional, string indicating the favourite location name
        for user to create. Default to Toulouse
        * `mp`: optional, boolean indicating if the user allows private messages
        from the SunBot. Default value is `False`
        """
        self.__id = usr_id
        self.fav_location = fav_location
        self.mp = mp

        # Create a backup repository, if it was not already created:
        if not SunUser.backup_dir:
            logging.warning(
                "Users backup directory was not set. Use a default repository."
            )
            SunUser.backup_dir = Path("./save/usr/")

        self.__backup_file = SunUser.backup_dir / Path(f"{self.id}.json")
        if not self.__backup_file.exists():
            logging.info("Backup file for user %d doesn't exist. Creating it.", self.id)
            self.__backup_file.parent.mkdir(parents=True, exist_ok=True)
            self.save_usr_data()
        else:
            # If this user was already created by the past, load its data from the corresponding
            # file instead of values passed in arguments of the constructor:
            logging.info(
                "User n°%d already exists. Loading data from existing file.", self.id
            )
            with open(self.__backup_file, "r", encoding="UTF-8") as usr_file:
                try:
                    usr_data = json.load(usr_file)
                    self.fav_location = usr_data["fav_location"]
                    self.mp = usr_data["mp"]
                except json.decoder.JSONDecodeError:
                    logging.error(
                        "An error occured when retrieving data for user %d. File may be corrupted",
                        self.id,
                    )

    @property
    def id(self) -> int:
        """Return discord user ID"""
        return self.__id

    @id.setter
    def id(self, value: int) -> None:
        raise AttributeError("User ID cannot be modified")

    def __eq__(self, __o: object) -> bool:
        """Test if the specified object `o` is equal to this instance
        ## Parameter:
        * `__o`: object to compare to this instance
        ## Return value:
        `True` if the specified object and this user are equal, `False` otherwise
        """
        # If specified object is not a sunbot user, return false:
        if not isinstance(__o, SunUser):
            return False
        # Two users are equal if and only if they have the same ID:
        return self.id == __o.id

    def __hash__(self) -> int:
        return self.id

    def save_usr_data(self) -> None:
        """Method used to save user's data into corresponding backup file."""
        with open(self.__backup_file, "w", encoding="UTF-8") as usr_file:
            backup_dict = {
                "user_id": self.id,
                "fav_location": self.fav_location,
                "mp": self.mp,
            }

            json_data = json.dumps(backup_dict, ensure_ascii=False, indent=2)
            usr_file.write(json_data)
