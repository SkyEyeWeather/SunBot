
#=================================
#   LIBRARIES USED BY THIS CLASS
#=================================

import json
import logging
import os

from sunbot import sunbot


#================================
#        CLASS DEFINITION
#================================

class SunUser:
    """This class represents a SunBot user. Each user has an ID that allows to 
    identify it in discord API. This can be used to send it a message for example. 
    In this class, an user is also defined by its name."""


    def __init__(self, id : int, emoji : str = "", freqEmoji : float = 0.5, favLocation : str = "Toulouse", mp : bool = False) -> None:
        """Constructor for this class. A SunBot user is defined by its Discord ID. 
        Other informations can be provided in arguments, such as an emoji that is 
        used to react to a message sent by this user, if the user authorize private 
        message from the bot, or a specific favorite location for weather notifications. 
        Each instance of this class is associated to a backup file. The link 
        between the user and its backup file is done thanks to the user ID 
        (so ID is defined as a constant and cannot be modified).
        ## Parameters:
        * `id`: discord identifiant of the SunBot user to create
        * `emoji`: optional, string code corresponding to the emoji that will be 
        used to react to messages sent by the user
        * `freqEmoji`: optional, float corresponding to frequency at which an emoji 
        is added to a message from the user
        * `favLocation`: optional, string indicating the favourite location name 
        for user to create. Default to Toulouse
        * `mp`: optional, boolean indicating if the user allows private messages 
        from the SunBot. Default value is `False`"""
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "emoji", emoji)
        object.__setattr__(self, "freqEmoji", freqEmoji)
        object.__setattr__(self, "favLocation", favLocation)
        object.__setattr__(self, "mp", mp)

        #Creation of a file corresponding to the user, for data saving purposes:
        #if backup repertory does not exist, create it:
        if not os.path.exists(sunbot.USER_BACKUP_REPERTORY_PATH):
            os.makedirs(sunbot.USER_BACKUP_REPERTORY_PATH)
            logging.info(f"Repertory {sunbot.USER_BACKUP_REPERTORY_PATH} doesn't exist. Creating it.")

        #If this user was already created in the past, use data from corresponding 
        #file instead of values passed in arguments of the constructor:
        if os.path.isfile(f"{sunbot.USER_BACKUP_REPERTORY_PATH}{id}.json"):
            logging.info(f"User n°{id} already exists. Loading data from existing file.")
            with open(f"{sunbot.USER_BACKUP_REPERTORY_PATH}{id}.json", "r") as userFile:
                try:
                    userData = json.load(userFile)
                    object.__setattr__(self, "emoji", userData["emoji"])
                    object.__setattr__(self, "freqEmoji", userData["freqEmoji"])
                    object.__setattr__(self, "favLocation", userData["favLocation"])
                    object.__setattr__(self, "mp", userData["mp"])
                except json.decoder.JSONDecodeError:
                    logging.error(f"An error occured when retrieving data for user n°{id}. File may be corrupted")
        #Else, create a new user with a new corresponding backup file:
        else:
            logging.info(f"Creating user n°{id}")
            self.save_usr_data()


    def __setattr__(self, __name: str, __value) -> None:
        """Special method used to update object attributes
        ## Parameters:
        * `__name`: name of the attribute to update
        * `__value`: new value for the attribute to update"""
        #if attribute exists:
        if __name in self.__dict__:
            #User id cannot be modified:
            if __name == "id":
                logging.error("User identifiant cannot be modified. Abort")
                return
            #Value for emoji frequency must be in [0, 1] interval:
            if __name == "freqEmoji":
                if __value < 0 or __value > 1:
                    raise ValueError
                object.__setattr__(self, __name, __value)
            else:
                object.__setattr__(self, __name, __value)
            self.save_usr_data()
        else:
            logging.error(f"Class {__class__.__name__} haven't got a attribute named {__name}")


    def __eq__(self, __o: object) -> bool:
        """Test if the specified object `o` is equal to this instance
        ## Parameter: 
        * `__o`: object to compare to this instance
        ## Return value:
        `True` if the specified object and this user are equal, `False` otherwise"""

        #If specified object is not a sunbot user, return false:
        if type(__o) != SunUser:
            return False
        #Two users are equal if and only if they have the same ID:
        return self.id == __o.id


    def save_usr_data(self) -> None:
        """Method used to save user's data into corresponding backup file."""
        with open(f"{sunbot.USER_BACKUP_REPERTORY_PATH}{self.id}.json", "w") as userFile:
            jsonData = json.dumps(self.__dict__, ensure_ascii=False, indent=2)
            userFile.write(jsonData)
