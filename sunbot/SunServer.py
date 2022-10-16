
#=================================
#   LIBRARIES USED BY THIS CLASS
#=================================

import json
import logging
import os
import sunbot.sunbot as sunbot
from sunbot.SunUser import SunUser

#================================
#        CLASS DEFINITION
#================================

class SunServer:
    """This class defines a discord server where the bot is present. A discord server
    is a set of sun users (discord users) and have webhooks that allow the bot to send
    message without a context. It identify by an ID that corresponds to its ID on Discord.
    There are two sorts of server : normal and 'fun' server."""

    def __init__(self, id : int, fun : bool = False) -> None:
        """Constructor of this class
        ## Parameters :
        * id [in] : discord ID for the server to create. This ID is unique"""

        object.__setattr__(self, "id", id)
        object.__setattr__(self, "fun", fun)
        object.__setattr__(self, "usersDict", {})       #In this dict users' ID are the keys and users the values
        object.__setattr__(self, "webhooksDict", {})    #In this dict links to the webhook are the keys and state of this webhooks the values
        object.__setattr__(self, "appleHead", 0)

        #If backup directory doesn't exist, create it:
        if not os.path.exists(f"{sunbot.SERVER_BACKUP_REPERTORY_PATH}"):
            logging.info(f"Repertory {sunbot.SERVER_BACKUP_REPERTORY_PATH} doesn't exist. Creating it")
            os.makedirs(sunbot.SERVER_BACKUP_REPERTORY_PATH)

        #if server was already created in the past, load data from corresponding file:
        if os.path.isfile(f"{sunbot.SERVER_BACKUP_REPERTORY_PATH}{id}.json"):
            with open(f"{sunbot.SERVER_BACKUP_REPERTORY_PATH}{id}.json", "r") as serverFile:
                try:
                    serverData = json.load(serverFile)
                    object.__setattr__(self, "webhooksDict", serverData["webhooksDict"])
                    object.__setattr__(self, "fun", serverData["fun"])
                except json.decoder.JSONDecodeError:
                    logging.error(f"An error occured when retrieving data for server n°{id}")
        #Else, create a new server with a new corresponding backup file:
        else:
            logging.info(f"Creating server n°{id}")
            self._saveServer()


    def __setattr__(self, __name: str, __value) -> None:
        """Special method used to update object attributes. Here, redefinition
        prohibite all modifications excepted fun status and appleHead
        ## Parameters:
        * __name [in] : name of the attribute to update
        * __value [in] : new value for the attribute to update"""

        if __name == "fun" :
            object.__setattr__(self, __name, __value)
            self._saveServer()
            logging.info(f"Fun status for server {self.id} was updated. New value : {self.fun}")
        if __name == "appleHead":
            object.__setattr__(self, __name, __value)
        else:
            logging.error("Server attributes cannot directly modified")


    def addUser(self, user : SunUser) -> bool:
        """Add an user to this server.
        ## Parameter:
        * user [in] : user to add to the server
        ##Return:
        return True if the user was added to the server, otherwise False. Falling to add
        an user can be explain by the fact that user was already added in this server"""

        #If user was already added in this server, do nothing:
        if user.id in self.usersDict.keys():
            logging.error(f"User n°{user.id} was already added to the server {self.id}. Do nothing.")
            return False
        #Add user to the server users dictionnary:
        self.usersDict[user.id] = user
        logging.info(f"User n°{user.id} sucessfully added to the server {self.id}")
        return True


    def removeUser(self, userID : int) -> bool:
        """Remove an user from this server, if the user exists in this server.
        ##Parameters:
        * userID [in] : identifiant of the user to be removed from this server
        ##Return:
        Return True if the corresponding user was successfully removed from the server, otherwise False"""

        #If ID specified in argument doesn't correspond to any server's user :
        if userID not in self.usersDict.keys():
            logging.error(f"User n°{userID} not in the server {self.id}")
            return False
        self.usersDict.pop(userID)
        logging.info(f"User {userID} removed from the server {self.id} with success")
        return True


    def addWebhook(self, webhookLink : str, enabled : bool = True) -> bool:
        """Add a webhook for this server. If webhook was already added, do nothing.
        ## Parameters:
        * webhookLink [in] : link corresponding to the webhook to add
        * enabled [in] : boolean that indicates whether specified webhook is enabled.
        ## Return :
        Return true if the webhook was successfully added to this server, otherwise False"""

        if webhookLink in self.webhooksDict.keys():
            logging.error(f"Webhook pointed by {webhookLink} was already added to the server {self.id}. Abort")
            return False
        self.webhooksDict[webhookLink] = enabled
        logging.info(f"Webhook {webhookLink} was successfully added to the server {self.id}")
        return True


    def removeWebhook(self, webhookLink : str) -> bool:
        """Remove a webhoook from this server. If webhook doesn't exist, do nothing.
        ## Parameter:
        * webhookLink [in] : link corresponding to the webhook to remove
        ## Return:
        Return True if webhook was removed successfully, otherwise False"""

        if webhookLink not in self.webhooksDict.keys():
            logging.error(f"Webhook pointed by {webhookLink} doesn't exist in the server {self.id}. Do nothing")
            return False
        self.webhooksDict.pop(webhookLink)
        logging.info(f"Webhook {webhookLink} was successfully removed from the server {self.id}")
        return True


    def udpateWebhookState(self, webhookLink : str, enabled : bool) -> bool:
        """Enable or disabled webhook specified in argument, if it exists in this server.
        ## Parameter:
        * webhooklink [in] : link corresponding to the webhook to update state
        * enabled [in] : flag that indicates the new state for specified webhook. True to enable,
        False to disable
        ## Return:
        Return True if operation was a success, otherwise False"""

        if webhookLink not in self.webhooksDict.keys():
            logging.error(f"Webhook {webhookLink} doesn't exist in the server {self.id}. Do nothing")
            return False
        self.webhooksDict[webhookLink] = True
        logging.info(f"Webhook {webhookLink} is now enabled in the server {self.id}")
        return True



    def _saveServer(self):
        """Private method used to save server's data into corresponding backup file"""

        with open(f"{sunbot.SERVER_BACKUP_REPERTORY_PATH}{self.id}.json", "w") as serverFile:
            #To make current object transient, clear temporally dictionnary of users:
            tmpUsersDict = self.usersDict
            object.__setattr__(self, "usersDict", None)
            #Save server data in the backup file:
            jsonData = json.dumps(self.__dict__, ensure_ascii=False, indent=2)
            serverFile.write(jsonData)
            object.__setattr__(self, "usersDict", tmpUsersDict)