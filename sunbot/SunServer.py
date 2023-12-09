
#=================================
#   LIBRARIES USED BY THIS CLASS
#=================================

import json
import logging
import os

from sunbot.SunUser import SunUser

#================================
#        CLASS DEFINITION
#================================

class SunServer:
    """This class defines a discord server (guild) where the bot is present. A 
    discord server is a set of sun users (discord users) and has webhooks that
    allow the bot to send message without a context. It is identified by an ID 
    that corresponds to its ID on Discord.
    """
    srv_backup_path = ""

    def __init__(self, id : int) -> None:
        """Constructor of this class
        ## Parameter :
        * `id`: discord ID for the server to create. This ID is unique on Discord"""
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "usersDict", {})       #In this dict users' ID are the keys and users the values
        object.__setattr__(self, "webhooksDict", {})    #In this dict links to the webhook are the keys and state of this webhooks the values

        #If backup directory for servers does not already exist, create it:
        if SunServer.srv_backup_path == "":
            logging.warning("Server backup directory path was not set. Use a default repository.")
            SunServer.srv_backup_path = "./save/srv/"
        if not os.path.exists(f"{SunServer.srv_backup_path}"):
            logging.info("Repertory %s doesn't exist. Creating it", SunServer.srv_backup_path)
            os.makedirs(SunServer.srv_backup_path)

        #if server was already created in the past, load data from corresponding file:
        if os.path.isfile(f"{SunServer.srv_backup_path}{id}.json"):
            with open(f"{SunServer.srv_backup_path}{id}.json", "r", encoding="UTF-8") as serverFile:
                try:
                    serverData = json.load(serverFile)
                    object.__setattr__(self, "webhooksDict", serverData["webhooksDict"])
                except json.decoder.JSONDecodeError:
                    logging.error(f"An error occured when retrieving data for server n°{id}")
        #Else, create a new server with a new corresponding backup file:
        else:
            logging.info(f"Creating server n°{id}")
            self.save_srv_data()


    def __setattr__(self, __name: str, __value) -> None:
        """Special method used to update object fields. Here, redefinition
        prohibites all modifications.
        ## Parameters:
        * `__name`: name of the field to update
        * `__value`: new value for the field to update"""
        logging.error("Server attributes cannot be directly modified")


    def __eq__(self, __o: object) -> bool:
        """Test if the specified object `__o` is equal to this instance
        ## Parameter:
        * `__o`: object to compare to this instance
        ## Return value:
        `True` if the specified object to this instance, `False` otherwise"""

        if type(__o) != SunServer:
            return False
        #Two servers are equal if they have the same ID:
        return self.id == __o.id


    def addUser(self, user : SunUser) -> bool:
        """Adds an user to this server.
        ## Parameter:
        * `user`: user to add to this server
        ## Return value:
        returns `True` if the user was added to the server, otherwise `False`. Falling to add
        an user can be explain by the fact that user was already added in this server"""
        #If user was already added into this server, do nothing:
        if user.id in self.usersDict.keys():
            logging.error(f"User n°{user.id} was already added to the server {self.id}. Do nothing.")
            return False
        #Add the user to the server users dictionnary:
        self.usersDict[user.id] = user
        logging.info(f"User n°{user.id} sucessfully added to the server {self.id}")
        return True


    def removeUser(self, userID : int) -> bool:
        """Removes an user from this server, if the user exists in this server.
        ## Parameter:
        * `userID`: identifiant of the user to be removed from this server
        ## Return value:
        Return `True` if the corresponding user was successfully removed from this 
        server, otherwise `False`"""
        #If ID specified in arguments does not correspond to any server's user :
        if userID not in self.usersDict.keys():
            logging.error(f"User n°{userID} not in the server {self.id}")
            return False
        self.usersDict.pop(userID)
        logging.info(f"User {userID} removed from the server {self.id} with success")
        return True


    def addWebhook(self, webhookLink : str, enabled : bool = True) -> bool:
        """Adds a webhook to this server. If webhook was already added, do nothing.
        ## Parameters:
        * `webhookLink`: link corresponding to the webhook to add
        * `enabled`:boolean that indicates whether specified webhook is enabled
        ## Return value:
        Return `True` if the webhook was successfully added to this server, 
        otherwise `False`"""
        if webhookLink in self.webhooksDict.keys():
            logging.error(f"Webhook pointed by {webhookLink} was already added to the server {self.id}. Abort")
            return False
        self.webhooksDict[webhookLink] = enabled
        logging.info(f"Webhook {webhookLink} was successfully added to the server {self.id}")
        return True


    def removeWebhook(self, webhookLink : str) -> bool:
        """Removes a webhoook from this server. If webhook does not exist,
        do nothing.
        ## Parameter:
        * `webhookLink`: link corresponding to the webhook to remove
        ## Return value:
        Return True if webhook was removed successfully, otherwise False"""
        if webhookLink not in self.webhooksDict.keys():
            logging.error(f"Webhook pointed by {webhookLink} doesn't exist in the server {self.id}. Do nothing")
            return False
        self.webhooksDict.pop(webhookLink)
        logging.info(f"Webhook {webhookLink} was successfully removed from the server {self.id}")
        return True


    def udpateWebhookState(self, webhookLink : str, enabled : bool) -> bool:
        """Enables or disables webhook specified in arguments, if it exists in 
        this server.
        ## Parameters:
        * `webhooklink`: link corresponding to the webhook to update the status
        * `enabled`: flag that indicates the new state for specified webhook. `True`
        to enable, `False` to disable
        ## Return value:
        Return `True` if operation was a success, otherwise `False`"""
        if webhookLink not in self.webhooksDict.keys():
            logging.error(f"Webhook {webhookLink} does not exist in the server {self.id}. Do nothing")
            return False
        self.webhooksDict[webhookLink] = True
        logging.info(f"Webhook {webhookLink} is now enabled in the server {self.id}")
        return True



    def save_srv_data(self):
        """Private method used to save server's data into corresponding backup 
        file"""
        with open(f"{SunServer.srv_backup_path}{self.id}.json", "w", encoding="UTF-8") as serverFile:
            #To make current object transient, clear temporally dictionnary of users:
            tmpUsersDict = self.usersDict
            object.__setattr__(self, "usersDict", None)
            #Save server data into the backup file:
            jsonData = json.dumps(self.__dict__, ensure_ascii=False, indent=2)
            serverFile.write(jsonData)
            object.__setattr__(self, "usersDict", tmpUsersDict)
        os.chmod(f"{SunServer.srv_backup_path}{self.id}.json", mode=0o777)
