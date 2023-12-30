import discord
from discord.ext import commands


class SunBotHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        messageToSend = discord.Embed(
            title="Voici la liste de mes commandes :", color=0x77B5FE
        )
        for commande in mapping[None]:
            if commande.name == "help":
                messageToSend.add_field(
                    name="help",
                    value="Affiche ce message si utilisée sans paramètre, ou bien la doc de la commande dont le nom est passée en argument",
                    inline=False,
                )
            else:
                messageToSend.add_field(
                    name=commande.name, value=commande.brief, inline=False
                )
        await self.get_destination().send(embed=messageToSend)

    async def send_cog_help(self, cog):
        return await super().send_cog_help(cog)

    async def send_group_help(self, group):
        return await super().send_group_help(group)

    async def send_command_help(self, command):
        return await super().send_command_help(command)
