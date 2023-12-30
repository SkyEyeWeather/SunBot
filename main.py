"""main.py"""

import asyncio
import logging
import os

import discord
from discord.ext import commands

from sunbot.SunController import SunController


async def main():
    """Entry point of the program"""
    logging.basicConfig(level=logging.INFO)

    bot = commands.Bot(command_prefix="+", intents=discord.Intents.all())
    test_mode = "FLY_ALLOC_ID" not in os.environ

    await bot.add_cog(SunController(bot=bot, test_mode=test_mode))
    # run the bot until shut down
    await bot.start(os.environ["token"])

    logging.info("bot was disconnected")


###########################################################################
# ALWAYS RUN PART - DO NOT PUT ANY CODE UNDER THESE LINES - ALWAYS RUN PART
###########################################################################

asyncio.run(main())
