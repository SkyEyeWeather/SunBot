#==================================
#   MODULES USED IN THIS FILE
#==================================

import asyncio
import logging
import os

import discord
from discord.ext import commands

from sunbot.SunBotHelpCommand import SunBotHelpCommand
from sunbot.SunController import SunController


logging.basicConfig(level=logging.INFO)
sunBot = commands.Bot(command_prefix='+', intents=discord.Intents.all(), help_command=SunBotHelpCommand())

async def main():
    test_mode = ("FLY_ALLOC_ID" not in os.environ)
    await sunBot.add_cog(SunController(sunBot, test_mode=test_mode))
    await sunBot.start(os.environ['token'])


#####################################################################################################
#ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES - ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES
#####################################################################################################

asyncio.run(main())
