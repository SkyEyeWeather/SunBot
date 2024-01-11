"""SunController.py"""
# =================================
#   LIBRARIES USED BY THIS CLASS
# =================================

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

import discord
from discord import app_commands
from discord.ext import commands

import sunbot.weather.Meteo as weather
from sunbot import sunbot, weather_event
from sunbot.core.guild import SunGuild
from sunbot.core.user import SunUser
from sunbot.weather_event import DailyWeatherEvent
from sunbot.apis.weather import VisualCrossingHandler


async def _get_period_autocompletion(
    _interaction: discord.Interaction, current: str
) -> List[app_commands.Choice[str]]:
    """Return period time for autocompletion"""
    choice_list = []
    for period in sunbot.PERIODS:
        if current.lower() in period.lower():
            choice_list.append(app_commands.Choice(name=period, value=period))
    return choice_list


# =================================
#       CLASS DECLARATION
# =================================


class SunController(commands.Cog):
    """This class is the core class of the SunBot. This is the class that makes
    the link between guild that contains users, the discord API, the bot weather part
    and the weather API handler
    """

    def __init__(self, bot: commands.Bot, test_mode: bool = False) -> None:
        """Constructor of this class. Bind the specified bot to this controller.
        ## Parameter :
        * `discordBot`: bot to bind to the new controller
        * `test_mode`: mount point for bot persistent data storage
        ## Return value :
        Not applicable
        """
        # Reference to the discord client for the bot
        self.bot: commands.Bot = bot
        # Define whether the bot is running in test mode or not:
        self.test_mode = test_mode
        # Mount point toward bot data:
        if test_mode:
            self.data_mount_pt = "./data/"
        else:
            self.data_mount_pt = "/data/"
        SunUser.backup_dir = Path(self.data_mount_pt + "save/usr/")
        SunGuild.backup_dir = Path(self.data_mount_pt + "save/srv/")
        # Dict containing all Discord users who can use the bot:
        self.usr_dict: Dict[int, SunUser] = {}
        # Dict containing all the guilds to which the bot belongs
        self.srv_dict: Dict[int, SunGuild] = {}
        # apu handlers
        self.vc_handler = VisualCrossingHandler()
        # Handler for daily weather events
        self.daily_weather_handler = DailyWeatherEvent(
            f"{self.data_mount_pt}save/daily_weather_sub.json", self.vc_handler
        )

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """This method specifies actions to be performed when the bot is
        launched
        """
        logging.info("Starting bot initialization...")
        logging.info("Synchronize bot commands tree to discord")
        await self.bot.tree.sync()
        logging.info("Loading user data")
        # For all guilds known by the bot:
        for guild in self.bot.guilds:
            self.srv_dict[guild.id] = SunGuild(guild.id)
            # For all members in the current guild (bot users):
            for user in guild.members:
                current_usr = SunUser(user.id)
                # If the current user was not already added to the known users dict:
                if user.id not in self.usr_dict:
                    self.usr_dict[user.id] = current_usr
                self.srv_dict[guild.id].add_member(current_usr)
        # load daily weather data
        await self.daily_weather_handler.load_locations_subscribers(
            self.bot.get_user,
            self.bot.get_channel,
        )
        loop = asyncio.get_running_loop()
        # Create and launch tasks:
        logging.info("Launching weather tasks...")
        loop.create_task(self.daily_weather_handler.run_event_task())
        logging.info("Bot is ready !")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """This method is called when a new member joins a guild where the bot
        belongs
        ## Parameter:
        * `member` : reference to the new member that has joined a guild known
        by the bot
        ## Return value:
        not applicable
        """
        logging.info("%s joins the guild %s", member.name, member.guild.name)
        # Create a new user:
        new_usr = SunUser(member.id)
        # If user is already known by the bot, for example because he / she is present
        # on another guild where the bot is, do not add him to the list of bot users:
        if member.id not in self.usr_dict:
            self.usr_dict[member.id] = new_usr
        # Add new user to the corresponding guild:
        self.srv_dict[member.guild.id].addUser(new_usr)
        # Send a welcome message to the new user on system channel of the guild:
        system_channel = member.guild.system_channel
        # If no system channel was set on the guild, try to find another channel:
        if system_channel is None:
            logging.warning(
                "No system channel was found for the guild %s. Trying to send on another channel",
                member.guild.name,
            )
            system_channel = member.guild.channels[0]
        system_channel.send(
            f"Bienvenue sur le serveur {member.mention}!"
            " Je suis SunBot, bot spécialiste de la météo (ou pas)!"
            " Tu peux utiliser +help dans le channel des bots pour en savoir plus sur moi!"
        )
        new_usr.save_usr_data()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """This method is called when a message is published on one of the guild the bot belongs
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
        logging.info("A message was received on guild n°%d", msg_srv.id)
        # Commands must be processed first
        await self.bot.process_commands(message)

    @commands.Cog().listener()
    async def on_shut_down(self, signame: str):
        """This method is called when the SIGINT signal is trigerred"""
        logging.info("%s signal received", signame)
        await self.__save_data()
        logging.info("Data was saved on %s", self.data_mount_pt)
        # stop running tasks:
        logging.info("Stopping running tasks...")
        current_task = asyncio.current_task()
        tasks = asyncio.all_tasks()
        tasks.remove(current_task)
        # cancel all the tasks except current and main tasks:
        for task in tasks:
            # Task-1 is for main task (launched with asyncio.run())
            if task.get_name() != "Task-1":
                task.cancel()
        await self.bot.close()

    # ====================================================================================
    #                                   COMMANDS PART
    # ====================================================================================

    @app_commands.command(
        name="disconnect", description="[admin] Deconnecte le bot de discord"
    )
    @app_commands.describe(debug="1=mode debug on, 0=mode debut off")
    @app_commands.guilds(discord.Object(id=726063782606143618))
    async def disconnect(
        self, interaction: discord.Interaction, debug: Optional[int] = 1
    ) -> None:
        """Mainteners' command used to disconnect the bot from discord, mainly for
        debug purposes.
        ## Parameters:
        - `interaction`: discord interaction which contains context data
        - `debug`: if set to `1`, only disconnect a local debug run of the bot.
        If set to `0` the remote bot will be disonnected from discord. Default
        to `1`.
        ## Return value:
        not applicable
        """
        if debug not in [0, 1]:
            logging.warning("User has used an unknown value for debug argument")
            await interaction.response.send_message(
                "Je ne reconnais pas la valeur utilisée pour `debug`"
            )
            return

        logging.info("Bot is disconnecting...")
        await self.__save_data()
        await interaction.response.send_message(
            "La sauvegarde des données est terminée, je me déconnecte. Bonne nuit!"
        )
        # To avoid to accidently disconnect remote bot durint a debug session:
        if not self.test_mode and debug:
            logging.warning("The disconnection signal was ignored")
            return
        logging.info("Bot was disconnected")
        await self.bot.close()

    @app_commands.command(
        name="ping",
        description="Si je suis réveillé, je réponds pong! Sinon...et bien c'est que je dors 😴",
    )
    async def ping(self, interaction: discord.Interaction) -> None:
        """Send a string to indicate that the bot is alive
        ## Parameters:
        * `interaction`: discord interaction which contains context data for
        current command call
        ## Return value:
        not applicable
        """
        await interaction.response.send_message("Pong !")

    @app_commands.command(name="meteo", description="Donne la météo courante")
    @app_commands.describe(location_name="Nom de la localité")
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
        logging.info(
            "User n°%d called the command `meteo` for the location %s",
            interaction.user.id,
            location_name,
        )

        data = self.vc_handler.get_current_weather_data(location_name)
        # Create current weather image:
        weather.createCurrentWeatherImage(data, sunbot.CURRENT_WEATHER_IMAGE_PATH)
        await interaction.response.send_message(
            f"Voici la météo actuelle sur {location_name}:",
            file=discord.File(
                f"{sunbot.CURRENT_WEATHER_IMAGE_PATH}{sunbot.CURRENT_WEATHER_IMAGE_NAME}"
            ),
        )

    @app_commands.command(
        name="pluie", description="Quand va-t-il pleuvoir aujourd'hui? ☔"
    )
    @app_commands.describe(location_name="Nom de la localité")
    @app_commands.describe(period="Période (aujourd'hui / demain)")
    @app_commands.autocomplete(period=_get_period_autocompletion)
    async def pluie(
        self,
        interaction: discord.Interaction,
        location_name: str,
        period: str = "aujourd'hui",
    ) -> None:
        """Handle a call to the `pluie` slash command by requesting rain information
        for the specified location name and returning acquired data to discord.
        ## Parameters:
        * `interaction`: discord interaction which contains context dara for
        current command call
        * `location_name`: name of the location for which the user wants to retrieve
        rain data
        * `period`: period to be considered
        ## Return value:
        not applicable
        """
        # If no location was provided by the user, use its favorite one:
        if location_name == "":
            location_name = self.usr_dict[interaction.user.id].favLocation
        logging.info(
            "%d called the command 'pluie' for the location %s and period %s",
            interaction.user.id,
            location_name,
            sunbot.PERIODS[period],
        )
        data = self.vc_handler.get_rain_data(location_name, period)
        if not data:
            logging.error(
                "An error occured when trying to get daily rain informations for the place %s",
                location_name,
            )
            await interaction.response.send_message(
                "Humm, quelque chose s'est mal passé en essayant de récupérer"
                f" les informations de pluie pour {location_name} 😢"
            )
            return
        # Build the embed message to send in response to the command call:
        embed2send = weather.create_rain_embed(data, period=period)
        await interaction.response.send_message(embed=embed2send)

    @app_commands.command(
        name="daily_weather",
        description="Active ou désactive l'envoi quotidien de la météo du jour pour la localisation indiquée",
    )
    @app_commands.describe(location_name="Nom de la localité")
    async def set_daily_weather_channel(
        self, interaction: discord.Interaction, location_name: str
    ) -> None:
        """Handle the call to the `daily_weather` slash command by adding or
        removing a guild to / from the list of subscribing guilds. This command
        can only be used by an user that have admin permissions on the guild where
        the command was called.
        ## Parameters:
        * `interaction`: discord interaction which contains context data
        * `location_name`: location to which the guild have to be add / remove
        ## Return value:
        not applicable
        """
        guild_id = interaction.guild_id
        # command can only be used by an admin of the guild that called it
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "Seul les administrateurs du serveur sont autorisés à utiliser cette commande!"
            )
        # If daily weather for specified location and guild was already set:
        if await self.daily_weather_handler.is_sub2location(
            weather_event.SERVER_SUB_TYPE, guild_id, location_name
        ):
            # If specified interaction is the same as the current registered interaction
            # for current guild and location name:
            registered_entity = await self.daily_weather_handler.get_sub_entity(
                weather_event.SERVER_SUB_TYPE, guild_id, location_name
            )
            # If the bot already sends daily weather on current channel, disable the sending
            if interaction.channel_id == registered_entity.id:
                await self.daily_weather_handler.del_sub_from_location(
                    weather_event.SERVER_SUB_TYPE, guild_id, location_name
                )
                await interaction.response.send_message(
                    f"Bien compris, je n'enverrai plus la météo quotidienne pour {location_name} 😀"
                )
                logging.info(
                    "Daily weather was disabled for the location %s on the guild n°%d",
                    location_name,
                    guild_id,
                )
            # Else replace registered interaction with the new one:
            else:
                await self.daily_weather_handler.add_sub2location(
                    interaction.channel, location_name
                )
                await interaction.response.send_message(
                    f"Ok, j'enverrai désormais la météo quotidienne pour {location_name} ici à la place du channel précédent!"
                )
                logging.info(
                    "Daily weather for location %s on the server n°%d was updated with a new channel",
                    location_name,
                    guild_id,
                )
        # If daily weather for specified location and server is not set:
        else:
            # Check if location is known by the API:
            data = self.vc_handler.get_daily_weather_data(location_name)
            if not data:
                logging.error("Unknown location:  %s", location_name)
                await interaction.response.send_message(
                    f"Je n'ai pas {location_name} dans mes données, vérifies le nom !"
                )
                return
            location_tz: str = data["timezone"]
            await self.daily_weather_handler.add_sub2location(
                interaction.channel, location_name, location_tz
            )
            await interaction.response.send_message(
                f"C'est compris, j'enverrai désormais quotidiennement la météo du jour pour {location_name} ici 😉"
            )
        await self.daily_weather_handler.save_locations_subscribers()

    @app_commands.command(
        name="mp_daily_weather",
        description="Active ou désactive l'envoi quotidien de la météo du jour pour la localisation indiquée",
    )
    @app_commands.describe(location_name="Nom de la localité")
    async def set_daily_weather_pm(
        self, interaction: discord.Interaction, location_name: str
    ) -> None:
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
        if await self.daily_weather_handler.is_sub2location(
            weather_event.USER_SUB_TYPE, user_id, location_name
        ):
            # User has already used the command for the indicated location, so
            # disable the sending for this location and user
            await self.daily_weather_handler.del_sub_from_location(
                weather_event.USER_SUB_TYPE, user_id, location_name
            )
            await interaction.response.send_message(
                content=f"C'est entendu, je ne vous enverrai plus la météo quotidienne pour {location_name}"
            )
            logging.info(
                "User n°%d has disabled daily weather pm for %s", user_id, location_name
            )
            await self.daily_weather_handler.save_locations_subscribers()
            return
        # User has not enable the pm for the specified location, so first check
        # that this city is known by the API to avoid future errors
        data = self.vc_handler.get_daily_weather_data(location_name)
        if not data:
            logging.error("Location %s is unknown by the API", location_name)
            await interaction.response.send_message(
                content=f"Je ne connais pas {location_name}, désolé ! Vérifiez l'orthographe de la localisation et reéessayez!"
            )
            return
        # Add the user to the location subscribers list:
        location_tz = data["timezone"]
        await self.daily_weather_handler.add_sub2location(
            interaction.user, location_name, location_tz
        )
        logging.info(
            "User n°%d has subscribed to receive daily weather for the location %s",
            user_id,
            location_name,
        )
        await interaction.response.send_message(
            content=f"Super ! Je vous enverrez désormais la météo pour {location_name} chaque jour en message privé! (à 7h00 heure locale de la localisation)"
        )
        await self.daily_weather_handler.save_locations_subscribers()

    @app_commands.command(
        name="global_info",
        description="Envoi un message sur tous les channels système connus par le bot",
    )
    @app_commands.describe(msg="message à envoyer")
    @app_commands.guilds(discord.Object(id=726063782606143618))
    async def global_info(self, interaction: discord.Interaction, msg: str) -> None:
        """Send a message to all the guilds to which the bot belongs
        ## Parameters:
        * `interaction`: discord interaction which contains context data
        ## Return value:
        None
        """
        embed2send = discord.Embed(
            title="Informations concernant la SunRisVersion (V2)", description=msg
        )
        for guild in self.bot.guilds:
            guild_syst_channel = guild.system_channel
            # check the existence of a system channel for the current guild:
            if guild_syst_channel is None:
                await guild.channels[0].send(embed=embed2send)
            # if no system channel was set, send to the first channel available
            else:
                await guild_syst_channel.send(embed=embed2send)
        await interaction.response.send_message("Message envoyé !")

    # ====================================================================================
    #                                   PRIVATE METHODS PART
    # ====================================================================================

    async def __save_data(self):
        """Save bot data on the disk"""
        for usr in self.usr_dict.values():
            logging.info("Saving data for user n°%d", usr.id)
            usr.save_usr_data()
        for srv in self.srv_dict.values():
            logging.info("Saving data for guild n°%d", srv.id)
            srv.save_srv_data()
        await self.daily_weather_handler.save_locations_subscribers()
