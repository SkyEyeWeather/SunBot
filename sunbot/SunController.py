
#=================================
#   LIBRARIES USED BY THIS CLASS
#=================================

import discord
from discord import app_commands
from discord.ext import commands
from http.client import HTTPException
import logging
import numpy as np

import sunbot.sunbot as sunbot
from sunbot.SunServer import SunServer
from sunbot.SunUser import SunUser
import sunbot.WeatherAPIHandler as weatherAPIHandler
import sunbot.weather.Meteo as weather


#=================================
#       CLASS DECLARATION
#=================================

class SunController :
    """This class is the core class of the SunBot. This is the class that makes
    the link between server that contains users, the discord API, the bot weather part
    and the weather API handler"""

    def __init__(self, discordBot : commands.Bot) -> None:
        """Constructor of this class. Bind the specified bot to this controller.
        ## Parameter :
        * `discordBot`: bot to bind to the new controller 
        ## Return value :
        Not applicable"""
        self.bot : commands.Bot = discordBot       #reference to the discord client for the bot
        self.usersDict : dict = {}                 #Dict that contains all Discord users who can use the bot
        self.serversDict : dict = {}               #Dict that contains all the servers to which the bot belongs


    async def on_ready(self) -> None:
        """This method specifies the actions to be performed when the bot is 
        launched"""
        logging.info("Starting bot initialization...")
        logging.info("Synchronize bot commands tree to discord")
        await self.bot.tree.sync(guild=discord.Object(id=1029313313827471413))
        logging.info("Loading user data")
        #For all servers known by the bot:
        for server in self.bot.guilds:
            self.serversDict[server.id] = SunServer(server.id)
            #For all members in the current server (bot users):
            for user in server.members:
                currentUser = SunUser(user.id)
                #If the current user was not already added to the known users dict:
                if user.id not in self.usersDict :
                    self.usersDict[user.id] = currentUser
                self.serversDict[server.id].addUser(currentUser)
        logging.info("Bot is ready !")


    async def on_member_join(self, member : discord.Member) -> None:
        """This method is called when a new member joins a server where the bot belongs
        ## Parameter:
        * `member` : reference to the new member that joined a server known by the bot
        ## Return value:
        not applicable"""
        logging.info(f"{member.name} joins the server {member.guild.name}")
        #Create a new user:
        newUser = SunUser(member.id)
        #If user is already known by the bot, for example because he / she is present
        #on another server where the bot is, do not add him to the list of bot users:
        if member.id not in self.usersDict:
            self.usersDict[member.id] = newUser
        #Add new user to the corresponding server:
        self.serversDict[member.guild.id].addUser(newUser)
        #Send a welcome message to the new user on system channel of the server:
        systemChannel = member.guild.system_channel
        #If no system channel was set on the server, try to find another channel:
        if systemChannel is None:
            logging.warning(f"No system channel was found for the server {member.guild.name}. Trying to send on another channel")
            systemChannel = member.guild.channels[0]
        systemChannel.send(f"Bienvenue sur le serveur {member.metion}! Je suis SunBot, bot spécialiste de la météo (ou pas)! Tu peux utiliser +help dans le channel des bots pour en savoir plus sur moi!")


    async def on_message(self, message : discord.Message) -> None:
        """This method is called when a message is published on one of the server the bot belongs
        ## Parameters:
        * `message` : discord message sent
        ## Return value:
        not applicable"""
        logging.info("A message was received")
        msgServer = self.serversDict[message.guild.id]
        #Firstly process the command (if message is a command):
        await self.bot.process_commands(message)

        #If the server where the message was sent is a "fun" server:
        if msgServer.fun:
            #Randomly add a reaction to the message:
            await self._addReaction(message)
            lowerMsg = message.content.lower()
            #if the message corresponds to the "apple head" invocation and the server is a funny server:
            if lowerMsg in ["tête de pomme", "tete de pomme", "#tetedepomme"]:
                msgServer.appleHead += 1
                #If the message was repeted three consecutive times, send the gif:
                if msgServer.appleHead == 3:
                    msgServer.appleHead = 0
                    logging.info(f"Invocation of apple head on server {message.guild.name}!")
                    embedToSend = discord.Embed(title="Et tu savais qu'à Jean Jaurès", color=0xff0000)
                    appleHeadGif = discord.File(f"{sunbot.GIF_REPERTORY_PATH}{sunbot.APPLE_HEAD_GIF_NAME}")
                    embedToSend.set_image(url=f"attachment://{sunbot.APPLE_HEAD_GIF_NAME}")
                    await message.channel.send(embed=embedToSend, file=appleHeadGif)
            #Other types of messages:
            else:
                msgServer.appleHead = 0
                #Easter egg:
                if "me foutre au sol" in lowerMsg and np.random.uniform() > 0.5:
                    await message.reply("Tu sais, il y a des gens qui disaient ça et qui ont fini ingénieurs chez Boeing. Donc tu as du potentiel \U0001f31e !")
                elif lowerMsg == "sinus":
                    await message.channel.send("Tangente")
                elif lowerMsg in ["patrick", "patou", "patoche", "pata", "patrikou"] and np.random.uniform() > 0.25:
                    pass #TODO add the list of gifs
                elif "kernel is dead" in lowerMsg:
                    pass    #TODO add corresponding list of gifs


    #====================================================================================
    #                                   COMMANDS PART
    #====================================================================================
    async def setEmoji(self, ctx : commands.Context, userId : int, emoji : str, emojiFreq : float):
        """"""
        try:
            self.usersDict[userId].emoji = emoji
        except KeyError:
            pass


    @staticmethod
    async def ping(interaction : discord.Interaction)->None:
        """"""

        await interaction.response.send_message("Pong !")


    async def meteo(self, interaction : discord.Interaction, place_name : str) -> None:
        """"""

        if place_name == "":
            place_name = self.usersDict[interaction.user.id].favLocation
        logging.info(f"{interaction.user.id} called the command `meteo` for the location {place_name}")
        json_current_weather = weatherAPIHandler.currentWeatherRequest(place_name)
        #Create current weather image:
        weather.createCurrentWeatherImage(json_current_weather, sunbot.CURRENT_WEATHER_IMAGE_PATH)
        await interaction.response.send_message(f"Voici la météo actuelle sur {place_name}:", file=discord.File(f"{sunbot.CURRENT_WEATHER_IMAGE_PATH}{sunbot.CURRENT_WEATHER_IMAGE_NAME}"))


    @app_commands.command()
    async def pluie(self, interaction : discord.Interaction, place_name : str) -> None:
        """"""

        #if no location was provided by the user, use its favorite one:
        if place_name == "":
            place_name = self.usersDict[interaction.user.id].favLocation
        logging.info(f"{interaction.user.id} called the command 'pluie' for the location {place_name}")
        requestResponse = weatherAPIHandler.dailyRainRequest(place_name)
        if requestResponse == {}:
            logging.error(f"An error occured when trying to get daily rain informations for the place {place_name}")
            await interaction.response.send_message(f"Humm, quelque chose s'est mal passé en essayant de récupérer les informations de pluie pour {place_name} 😢")
            return
        #Build the embed message to send in response to the call of the command:
        embedToSend = weather.createEmbedRainEmbed(requestResponse)
        await interaction.response.send_message(embed=embedToSend)

    #====================================================================================
    #                                   PRIVATE METHODS PART
    #====================================================================================

    async def _addReaction(self, msg : discord.Message) -> None:
        """Private method to add a reaction to the specified message published 
        by an user, according to the user probability for this action
        ## Parameters:
        * `msg` : discord message that triggered this method
        ## Return value:
        not applicable"""
        #Add a reaction only if the user is not a bot:
        if not msg.author.bot:
            #Get the user that sent the message:
            user : SunUser = self.usersDict[msg.author.id]
            #If an emoji is define for this user and probability is under freqEmoji proba:
            if user.emoji != "" and np.random.uniform() <= user.freqEmoji:
                try:
                    await msg.add_reaction(user.emoji)
                except discord.errors.NotFound:
                    logging.error(f"Reaction cannot be added because the message was deleted or the emoji {user.emoji} doesn't exist")
                except TypeError:
                    logging.error(f"Emoji {user.emoji}, set for the user n°{user.id} is not in a valid emoji format")


    async def _deleteMsgCommand(ctx : commands.Context) -> None:
        """Private method to delete the message written by an user to invoke a bot command
        ## Parameters:
        * `ctx` : discord context in which the command has been invoked
        ## Return value:
        not applicable"""
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            logging.error(f"The bot doesn't have the permissions to delete a message on the server {ctx.guild.name}")
        except (discord.NotFound, HTTPException):
            logging.error(f"The message to be deleted was not found on the server {ctx.guild.name}")
