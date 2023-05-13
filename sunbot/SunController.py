"""SunController.py"""
# =================================
#   LIBRARIES USED BY THIS CLASS
# =================================

import asyncio
import logging
from http.client import HTTPException
import numpy as np
import discord
from discord.ext import commands

import sunbot.sunbot as sunbot
from sunbot.SunServer import SunServer
from sunbot.SunUser import SunUser
import sunbot.weather_api_handler as weather_api_handler
import sunbot.weather.Meteo as weather
import sunbot.weather_event as weather_event
from sunbot.weather_event import DailyWeatherEvent


# =================================
#       CLASS DECLARATION
# =================================

class SunController:
    """This class is the core class of the SunBot. This is the class that makes
    the link between server that contains users, the discord API, the bot weather part
    and the weather API handler
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Constructor of this class. Bind the specified bot to this controller.
        ## Parameter :
        * `discordBot`: bot to bind to the new controller
        ## Return value :
        Not applicable"""
        self.bot: commands.Bot = bot  # Reference to the discord client for the bot
        self.usr_dict: dict = {}      # Dict containing all Discord users who can use the bot
        # Dict containing all the servers to which the bot belongs
        self.srv_dict: dict = {}
        # Handler for daily weather events
        self.daily_weather_handler = DailyWeatherEvent("./Data/Save/save.json")

    async def on_ready(self) -> None:
        """This method specifies actions to be performed when the bot is
        launched"""
        logging.info("Starting bot initialization...")
        logging.info("Synchronize bot commands tree to discord")
        await self.bot.tree.sync(guild=discord.Object(id=726063782606143618))
        logging.info("Loading user data")
        # For all servers known by the bot:
        for server in self.bot.guilds:
            self.srv_dict[server.id] = SunServer(server.id)
            # For all members in the current server (bot users):
            for user in server.members:
                current_usr = SunUser(user.id)
                # If the current user was not already added to the known users dict:
                if user.id not in self.usr_dict:
                    self.usr_dict[user.id] = current_usr
                self.srv_dict[server.id].addUser(current_usr)
        # Create and launch tasks:
        logging.info("Launching weather tasks...")
        loop = asyncio.get_event_loop()
        loop.create_task(self.daily_weather_handler.run_event_task())
        logging.info("Bot is ready !")

    async def on_member_join(self, member: discord.Member) -> None:
        """This method is called when a new member joins a server where the bot
        belongs
        ## Parameter:
        * `member` : reference to the new member that has joined a server known
        by the bot
        ## Return value:
        not applicable
        """
        logging.info("%s joins the server %s", member.name, member.guild.name)
        # Create a new user:
        new_usr = SunUser(member.id)
        # If user is already known by the bot, for example because he / she is present
        # on another server where the bot is, do not add him to the list of bot users:
        if member.id not in self.usr_dict:
            self.usr_dict[member.id] = new_usr
        # Add new user to the corresponding server:
        self.srv_dict[member.guild.id].addUser(new_usr)
        # Send a welcome message to the new user on system channel of the server:
        system_channel = member.guild.system_channel
        # If no system channel was set on the server, try to find another channel:
        if system_channel is None:
            logging.warning("No system channel was found for the server %s. Trying to send on another channel",
                            member.guild.name)
            system_channel = member.guild.channels[0]
        system_channel.send(
            f"Bienvenue sur le serveur {member.metion}! Je suis SunBot, bot spécialiste de la météo (ou pas)! Tu peux utiliser +help dans le channel des bots pour en savoir plus sur moi!")

    async def on_message(self, message: discord.Message) -> None:
        """This method is called when a message is published on one of the server the bot belongs
        or in PM
        ## Parameters:
        * `message` : discord message sent
        ## Return value:
        not applicable
        """
        # In the case where specified message is a PM, there is no guild attached
        # to it, so it is needed to check the channel type where message was sent
        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            logging.info("A private message was received")
            return  # Nothing to do
        msg_srv = self.srv_dict[message.guild.id]
        logging.info("A message was received on server n°%d", msg_srv.id)
        # Commands must be processed first
        await self.bot.process_commands(message)
        # Enable eastereggs only on "fun" servers:
        if msg_srv.fun:
            # Randomly add a reaction to the message:
            await self.__add_reaction(message)
            lowered_msg = message.content.lower()
            if lowered_msg in ["tête de pomme", "tete de pomme", "#tetedepomme"]:
                msg_srv.appleHead += 1
                # If the message was repeted three consecutive times, send the gif:
                if msg_srv.appleHead == 3:
                    msg_srv.appleHead = 0
                    logging.info(
                        "Invocation of apple head on server %s!", message.guild.name)
                    embed2send = discord.Embed(title="Et tu savais qu'à Jean Jaurès",
                                               color=0xff0000)
                    apple_head_gif = discord.File(
                        f"{sunbot.GIF_REPERTORY_PATH}{sunbot.APPLE_HEAD_GIF_NAME}")
                    embed2send.set_image(
                        url=f"attachment://{sunbot.APPLE_HEAD_GIF_NAME}")
                    await message.channel.send(embed=embed2send, file=apple_head_gif)
            # Other types of messages:
            else:
                msg_srv.appleHead = 0
                # Easter eggs:
                if "me foutre au sol" in lowered_msg and np.random.uniform() > 0.5:
                    await message.reply("Tu sais, il y a des gens qui disaient ça \
                                        et qui ont fini ingénieurs chez Boeing. \
                                        Donc tu as du potentiel \U0001f31e !")
                elif lowered_msg == "sinus":
                    await message.channel.send("Tangente")
                elif lowered_msg in ["patrick", "patou", "patoche", "pata", "patrikou"] and np.random.uniform() > 0.25:
                    pass  # TODO add the list of gifs
                elif "kernel is dead" in lowered_msg:
                    pass    # TODO add corresponding list of gifs

    # ====================================================================================
    #                                   COMMANDS PART
    # ====================================================================================

    # TODO Replace this classic command by it slash counterpart:
    @np.deprecate_with_doc
    async def set_emoji(self, ctx: commands.Context, usr_id: int, emoji: str, emoji_freq: float):
        """Set an emoji for specified user that the bot will used to randomly
        react to a message from this user
        ## Parameters:
        - `ctx`: command call context
        - `usr_id`: id of the user for which the emoji will be set
        - `emoji`: emoji to set
        - `emoji_freq`: probability that the bot reacts to an user message using
        specified emoji
        ## Return value:
        not applicable
        """
        try:
            self.usr_dict[usr_id].emoji = emoji
        except KeyError:
            pass

    @staticmethod
    async def ping(interaction: discord.Interaction) -> None:
        """Send a string to indicate that the bot is alive
        ## Parameters:
        * `interaction`: discord interaction which contains context data for
        current command call
        ## Return value:
        not applicable
        """
        await interaction.response.send_message("Pong !")

    async def meteo(self, interaction: discord.Interaction, location_name: str) -> None:
        """Handle a call to the `meteo` slash command by querying current weather
        condition for the indicated `location_name` and sending the generated
        weather image to discord in response to the command
        ## Parameters:
        * `interaction`: discord interaction which contains context data for
        current command call
        ## Return value:
        not applicable
        """
        if location_name == "":
            location_name = self.usr_dict[interaction.user.id].favLocation
        logging.info("User n°%d called the command `meteo` for the location %s",
                     interaction.user.id, location_name)
        json_current_weather = weather_api_handler.ask_current_weather(
            location_name)
        # Create current weather image:
        weather.createCurrentWeatherImage(
            json_current_weather, sunbot.CURRENT_WEATHER_IMAGE_PATH)
        await interaction.response.send_message(f"Voici la météo actuelle sur {location_name}:",
                                                file=discord.File(f"{sunbot.CURRENT_WEATHER_IMAGE_PATH}{sunbot.CURRENT_WEATHER_IMAGE_NAME}"))

    async def pluie(self, interaction: discord.Interaction, location_name: str) -> None:
        """Handle a call to the `pluie` slash command by requesting rain information
        for the specified location name and returning acquired data to discord.
        ## Parameters:
        * `interaction`: discord interaction which contains context dara for
        current command call
        * `location_name`: name of the location for which the user wants to retrieve
        rain data
        ## Return value:
        not applicable
        """
        # If no location was provided by the user, use its favorite one:
        if location_name == "":
            location_name = self.usr_dict[interaction.user.id].favLocation
        logging.info("%d called the command 'pluie' for the location %s",
                     interaction.user.id, location_name)
        request_response = weather_api_handler.ask_daily_rain(location_name)
        if request_response == {}:
            logging.error("An error occured when trying to get daily rain informations for the place %s",
                          location_name)
            await interaction.response.send_message(f"Humm, quelque chose s'est mal passé en essayant de récupérer les informations de pluie pour {location_name} 😢")
            return
        # Build the embed message to send in response to the command call:
        embed2send = weather.createEmbedRainEmbed(request_response)
        await interaction.response.send_message(embed=embed2send)

    async def set_daily_weather_channel(self, interaction: discord.Interaction, location_name: str) -> None:
        """Handle the call to the `daily_weather` slash command by adding or
        removing a server to / from the list of subscribing servers
        ## Parameters:
        * `interaction`: discord interaction which contains context data
        * `location_name`: location to which the server have to be add / remove
        ## Return value:
        not applicable
        """
        server_id = interaction.guild_id
        # If daily weather for specified location and server was already set:
        if await self.daily_weather_handler.is_sub2location(weather_event.SERVER_SUB_TYPE, server_id, location_name):
            # If specified interaction is the same as the current registered interaction
            # for current server and location name:
            registered_entity = await self.daily_weather_handler.get_sub_entity(weather_event.SERVER_SUB_TYPE, server_id, location_name)
            # If the bot already sends daily weather on current channel, disable the sending
            if interaction.channel_id == registered_entity.id:
                await self.daily_weather_handler.del_sub_from_location(weather_event.SERVER_SUB_TYPE, server_id, location_name)
                await interaction.response.send_message(f"Bien compris, je n'enverrai plus la météo quotidienne pour {location_name} 😀")
                logging.info(
                    "Daily weather was disabled for the location %s on the server n°%d", location_name, server_id)
            # Else replace registered interaction with the new one:
            else:
                await self.daily_weather_handler.add_sub2location(weather_event.SERVER_SUB_TYPE, interaction, location_name)
                await interaction.response.send_message(f"Ok, j'enverrai désormais la météo quotidienne pour {location_name} ici à la place du channel précédent!")
                logging.info(
                    "Daily weather for location %s on the server n°%d was updated with a new channel", location_name, server_id)
        # If daily weather for specified location and server is not set:
        else:
            # Check if location is known by the API:
            daily_weather_test = weather_api_handler.ask_daily_weather(
                location_name)
            if daily_weather_test == {}:
                logging.error("Unknown location:  %s", location_name)
                await interaction.response.send_message(f"Je n'ai pas {location_name} dans mes données, vérifies le nom !")
            else:
                location_tz: str = daily_weather_test['timezone']
                await self.daily_weather_handler.add_sub2location(weather_event.SERVER_SUB_TYPE, interaction, location_name, location_tz)
                await interaction.response.send_message(f"C'est compris, j'enverrai désormais quotidiennement la météo du jour pour {location_name} ici 😉")

    async def set_daily_weather_pm(self, interaction: discord.Interaction, location_name: str) -> None:
        """Handle a call to the `mp_daily_weather` slash command by adding or
        removing user that invoked it to/from the list of user subscribing
        to the specified location.
        ## Parameters:
        * `interaction`: command context
        * `location_name`: location name for which the user want to enable or
        disable the sending of daily weather in private message
        ## Return value:
        not applicable
        """
        user_id = interaction.user.id
        # Two cases depending on whether user has already used this command or not
        # for the specified location
        if await self.daily_weather_handler.is_sub2location(weather_event.USER_SUB_TYPE, user_id, location_name):
            # User has already used the command for the indicated location, so
            # disable the sending for this location and user
            await self.daily_weather_handler.del_sub_from_location(weather_event.USER_SUB_TYPE, user_id, location_name)
            await interaction.response.send_message(content=f"C'est entendu, je ne vous enverrai plus la météo quotidienne pour {location_name}")
            logging.info(
                "User n°%d has disabled daily weather pm for %s", user_id, location_name)
            return
        # User has not enable the pm for the specified location, so first check
        # that this city is known by the API to avoid future errors
        daily_weather_test = weather_api_handler.ask_daily_weather(
            location_name)
        if daily_weather_test == {}:
            logging.error("Location %s is unknown by the API", location_name)
            interaction.response.send_message(
                content="Je ne connais pas %s, désolé ! Vérifiez l'orthographe de la localisation et reéessayez!")
            return
        # Add the user to the location subscribers list:
        location_tz: str = daily_weather_test["timezone"]
        await self.daily_weather_handler.add_sub2location(weather_event.USER_SUB_TYPE, interaction, location_name, location_tz)
        logging.info(
            "User n°%d has subscribed to receive daily weather for the location %s", user_id, location_name)
        await interaction.response.send_message(content=f"Super ! Je vous enverrez désormais la météo pour {location_name} chaque jour en message privé! (à 7h00 heure locale de la localisation)")

    # ====================================================================================
    #                                   PRIVATE METHODS PART
    # ====================================================================================

    async def __add_reaction(self, msg: discord.Message) -> None:
        """Private method to add a reaction to the specified message published
        by an user, according to the user probability for this action
        ## Parameters:
        * `msg` : discord message that triggered this method
        ## Return value:
        not applicable
        """
        # Add a reaction only if the user is not a bot:
        if not msg.author.bot:
            # Get the user that sent the message:
            user: SunUser = self.usr_dict[msg.author.id]
            # If an emoji is define for this user and probability is under freqEmoji proba:
            if user.emoji != "" and np.random.uniform() <= user.freqEmoji:
                try:
                    await msg.add_reaction(user.emoji)
                except discord.errors.NotFound:
                    logging.error(
                        "Reaction cannot be added because the message was deleted or the emoji %s does not exist", user.emoji)
                except TypeError:
                    logging.error(
                        "Emoji %s, set for the user n°%dis not in a valid emoji format", user.emoji, user.id)

    # TODO Remove this unused private method:
    @np.deprecate_with_doc
    async def __delete_command_msg(self, ctx: commands.Context) -> None:
        """Private method to delete the message written by an user to invoke a bot command
        ## Parameters:
        * `ctx` : discord context in which the command has been invoked
        ## Return value:
        not applicable
        """
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            logging.error(
                "The bot doesn't have the permissions to delete a message on the server %s", ctx.guild.name)
        except (discord.NotFound, HTTPException):
            logging.error(
                "The message to be deleted was not found on the server %s", ctx.guild.name)
