
#=================================
#   LIBRARIES USED BY THIS CLASS
#=================================

import json
import logging
import os
from click import command
import requests
import discord
from discord.ext import commands

import sunbot.sunbot as sunbot
from sunbot.SunServer import SunServer
from sunbot.SunUser import SunUser


#=================================
#       CLASS DECLARATION
#=================================

class SunController :
    """This class is the core class of the SunBot. This is the class that makes
    the link between server that contains users, the discord API, the bot weather part
    and the weather API"""

    def __init__(self, discordBot : commands.Bot) -> None:
        """Constructor of this class. Link the specified bot to this controller.
        
        ## Parameter :
        * discordBot [in]: bot to link to the new controller 
        
        ## Return value :
        Not applicable"""

        self.bot = discordBot
        self.usersDict = {}
        self.serversDict = {}


    def on_ready(self) -> None:
        """This method specified actions to perform when launching the bot"""
        print("Starting bot initialisation...")
        print("Charging users' data")
        #For all servers where the bot is:
        for server in self.bot.guilds:
            self.serversDict[server.id] = SunServer(server.id)
            #For all members in the current server (bot users):
            for user in server.members:
                currentUser = SunUser(user.id)
                #else create a new user :
                self.usersDict[user.id] = currentUser
                self.serversDict[server.id].addUser(currentUser)
        print("Bot is ready !")
        
        #Creation of webhooks used by the bot:

