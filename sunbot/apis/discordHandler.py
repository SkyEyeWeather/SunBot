"""discord handler module"""

# =================================
# 	Modules used byt the class
# =================================

import time

import discord

from sunbot.MetaSingleton import MetaSingleton


class DiscordHandler(metaclass=MetaSingleton):
    """Singleton class that allows to centralize and handle request to discord API"""

    @staticmethod
    def sendWebhookMessage(
        webhook: discord.Webhook, msg: str = "", embedMsg: discord.Embed = None
    ) -> bool:
        """@brief : This function allow to send a message to the channel pointed by webhook specified in argument. If string message is empty, a embed message must be specified.
        ## Param :
        * webhook : webhook used to publish a message in to pointed channel on discord
        * msg [opt] : string message to send
        * embedMsg [opt] : embed to send, must be specified if string is not
        """
        numAttempt = 1
        sendSucessfully = False
        while not sendSucessfully and numAttempt <= 5:
            try:
                webhook.send(content=msg, embed=embedMsg)
                sendSucessfully = True
            # if there is and HTTP exception in sending webhook message :
            except discord.errors.HTTPException as e:
                numAttempt += 1
                with open("./error.txt", "w") as file:
                    file.write(e.text)
                time.sleep(300)
