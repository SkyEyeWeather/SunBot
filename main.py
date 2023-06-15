#==================================
#   MODULES USED IN THIS FILE
#==================================

import asyncio
import logging
import os
import time

import discord
from discord.ext import commands

from sunbot.apiHandler.VisualCrossingHandler import VisualCrossingHandler
from sunbot.apiHandler.discordHandler import DiscordHandler
from sunbot import sunbot
from sunbot.SunBotHelpCommand import SunBotHelpCommand
from sunbot.SunController import SunController


#=======================
#    GLOBAL VARIABLES
#=======================

PATH_SAVE_USER_REP = "./Data/Save/Users/"

logging.basicConfig(level=logging.INFO)
sunBot = commands.Bot(command_prefix='+', intents=discord.Intents.all(), help_command=SunBotHelpCommand())
vcRequestHandler = VisualCrossingHandler()
discordAPI_handler = DiscordHandler()
dictUsersBot = {}


#==================================
#     Evénements liés au bot
#==================================


"""
  #Création du thread écoutant les alertes météos:
  print("Génération des webhooks...")
  webhookServeurTest1 = discord.SyncWebhook.from_url('https://discord.com/api/webhooks/923863299270013018/6jfjT1QtrZ8UCXM1aEUhUD7z5G5Or9S3loFvlQs34Age8hX7VPfrD4UUQvGXCzmDN0Oo')
  webhookServeurCUPGE = discord.SyncWebhook.from_url('https://discord.com/api/webhooks/921547043196002324/NJohjH9dduqidXHvV4Ei9V4KuIUvOiAPnbMEVPf_x06CUStZou0TlTapQi3B1i_zuLfp')
  webhookServeurPrive = discord.SyncWebhook.from_url('https://discord.com/api/webhooks/965521867026866196/M_nmSDjgplk8a6DAbzAD8qZVEMBoVvR1FF9Mcts_-NQRg3Qc5lvXmFSSgUJxgDcAOQb5')
  alerteMeteo = Meteo.AlerteMeteo(vcRequestHandler)
  #alerteMeteo.addWebhook(webhookServeurTest1)
  #alerteMeteo.addWebhook(webhookServeurPrive)
  alerteMeteo.start()
  print("Webhook alerte météo prêt")
"""


"""
  if messageMin in ["patrick", "patou", "patoche", "pata", "patrikou"] and np.random.uniform() > 0.25:
      indiceGifToSend = int(np.random.uniform(0, len(listeGifMignons)))
      await message.reply(listeGifMignons[indiceGifToSend])
      await message.channel.send("Mignon !!")
  if "kernel is dead" in messageMin:
      indiceGifToSend = int(np.random.uniform(0, len(listeGifKernelDead)))
      await message.reply(listeGifKernelDead[indiceGifToSend])
  """


#====================
#    BOT'S COMMANDS
#====================


@sunbot.adminFunction
async def adminSetEmoji(ctx, userId :int, emoji : str, freq : float) :
  try :
    dictUsersBot[userId].setEmoji(emoji, freq)
  except KeyError:
    await ctx.channel.send("L'ID ne correspond à aucun utilisateur de mes services...\U0001f622")
  except ValueError:
    await ctx.channel.send("La fréquence doit être dans l'intervalle [0, 1] \U0001f620")
  else:
    await ctx.channel.send("L'emoji a bien été mis à jour \U0001f642")


@sunBot.command(name="favMeteo", brief="Envie de connaître la météo d'une localité sans te casser la tête ? Cette commande est pour toi !")
async def favMeteo(ctx, nomLocalite):
  print(f"Tentative de modification du favori météo de {ctx.author.name} vers {nomLocalite}")
  print(f"Vérification de l'existence de la localité {nomLocalite} dans l'API...")
  #Réalise une requête pour s'assurer de l'existence de la localité souhaitée :
  reponseRequest = vcRequestHandler.performRequest(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{nomLocalite}/today?unitGroup=metric&include=days&key={os.environ['idVisualCrossing']}&contentType=json&lang=fr")
  #Si la requête a échoué :
  if reponseRequest == {}:
    print(f"La localité {nomLocalite} ne semble pas exister dans la base de données de l'API")
    await ctx.channel.send(f"Je n'arrive pas à trouver une localité correspondant à {nomLocalite} \U0001f914")
  #Sinon, modifier la localité favorite et le time offset :
  else :
    dictUsersBot[ctx.author.id].favMeteo = nomLocalite
    dictUsersBot[ctx.author.id].offSetFav = reponseRequest["tzoffset"]
    print("Favori mis à jour avec succès")
    #Envoie un message de confirmation de modification à l'utilisateur :
    await ctx.channel.send(f"Ta localité favorite a bien été mise à jour et est désormais {nomLocalite} \U0001f604 !")


@sunBot.command(name="vocalConnect", brief="Vous m'avez appelez ? Je vous réponds (vraiment) ! [admin]")
@sunbot.adminFunction
async def vocalConnect(ctx):
  channel = ctx.author.voice.channel
  await channel.connect()
  time.sleep(1)
  ctx.voice_client.play(discord.FFmpegPCMAudio("./Data/Source/alpha.mp3"))


@sunBot.command(name="vocalDisconnect", brief="Deconnexion serveur vocal [admin]")
@sunbot.adminFunction
async def vocalDisconnect(ctx):
  await ctx.voice_client.disconnect()


@sunBot.command(name="setEmoji", brief="Commande à utiliser pour ajouter un emoji à un membre ! [admin]")
async def setEmoji(ctx, userId : int, emoji : str, freq : float) -> None:
  """Commande permettant de mettre à jour l'emoji ajouté aux messages postés par l'utilisateur dont l'ID est
  passé en paramètre.
  Paramètres :  - ctx : contexte d'appel de la compile
                - userId : Identifiant de l'utisateur dont on souhaite modifier l'emoji
                - freq : fréquende d'apparition de l'émoji sur les messages envoyés par l'utilisateur
  Ne retourne rien
  """
  await adminSetEmoji(ctx, userId, emoji, freq)


async def main():
    test_mode = (not "FLY_ALLOC_ID" in os.environ)
    await sunBot.add_cog(SunController(sunBot, test_mode=test_mode))
    await sunBot.start(os.environ['token'])
#####################################################################################################
#ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES - ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES
#####################################################################################################
asyncio.run(main())
