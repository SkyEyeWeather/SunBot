#==================================
#   MODULES USED IN THIS FILE
#==================================

import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import logging
import os
import time

from sunbot.apiHandler.VisualCrossingHandler import VisualCrossingHandler
from sunbot.apiHandler.discordHandler import DiscordHandler
import sunbot.sunbot as sunbot
from sunbot.SunBotHelpCommand import SunBotHelpCommand
from sunbot.SunController import SunController


#=======================
#    GLOBAL VARIABLES
#=======================

PATH_SAVE_USER_REP = "./Data/Save/Users/"

listeGifMignons = [
    "https://i.pinimg.com/originals/2a/65/72/2a6572296e58045b3f89c73e06e4916f.gif",
    "https://pa1.narvii.com/6935/ed72ab48336b42b9fdfaa9f245637841cb2208ber1-504-282_hq.gif",
    "https://acegif.com/wp-content/gifs/cute-bunny-gif-51.gif",
    "https://i.pinimg.com/originals/de/b9/49/deb949a2ea8afe6f7f0358137aac721b.gif",
    "https://img.filmsactu.net/datas/seriestv/t/h/the-mandalorian/n/the-mandalorian-gif-5fad8376c586e.gif",
    "https://2.bp.blogspot.com/-bKltZSToaSk/WpfSKtfVdZI/AAAAAAAADmY/mYeUGkpOdf8HoEq0c7N9Z5ixU5OuFn9FACLcBGAs/s1600/hamtaro.gif",
    "https://64.media.tumblr.com/a1f42c7b213265bde529ca41bd6c7e63/tumblr_nh5g2v3KlU1u465olo1_400.gifv",
    "https://c.tenor.com/rWDSYK2dWoMAAAAM/red-panda.gif",
    "https://tel.img.pmdstatic.net/fit/http.3A.2F.2Fprd2-bone-image.2Es3-website-eu-west-1.2Eamazonaws.2Ecom.2FTEL.2Enews.2F2018.2F01.2F11.2F7b751402-2a98-47d6-a69f-0e3d733181ed.2Egif/495x277/quality/80/thumbnail.gif",
    "https://phoneky.co.uk/thumbs/screensavers/down/cartoon-anime/sweetcat_jo9eelal.gif",
    "https://thumbs.gfycat.com/UnacceptableLittleCapybara-size_restricted.gif"
]

listeGifKernelDead = [
    "https://c.tenor.com/Ojww2DB8_x0AAAAd/dead-teletubbies.gif",
    "https://c.tenor.com/CXZRwTD_4BsAAAAM/im-dead-lol.gif",
    "https://c.tenor.com/LPYL83NEVcAAAAAM/dead-dog.gif",
    "https://c.tenor.com/X13wwMFZN2YAAAAM/dies-cat.gif"
]

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
  """ Commande permettant de mettre à jour l'emoji ajouté aux messages postés par l'utilisateur dont l'ID est
  passé en paramètre.
  Paramètres :  - ctx : contexte d'appel de la compile
                - userId : Identifiant de l'utisateur dont on souhaite modifier l'emoji
                - freq : fréquende d'apparition de l'émoji sur les messages envoyés par l'utilisateur
  Ne retourne rien
  """
  await adminSetEmoji(ctx, userId, emoji, freq)


@sunBot.command(name="disconnect", brief="Vous voulez vraiment me tuer ?!! [Admin]")
@sunbot.adminFunction
async def disconnect(unused_ctx):
  print("Déconnexion du bot...")
  #Enregistrement des données des utilisateurs (un fichier par utilisateur) :
  for userId in dictUsersBot :
    dictUsersBot[userId].saveUser(PATH_SAVE_USER_REP)
  print("Déconnexion terminée")
  await sunBot.logout()


async def main():
    await sunBot.add_cog(SunController(sunBot))
    await sunBot.start(os.environ['token'])
#####################################################################################################
#ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES - ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES
#####################################################################################################
asyncio.run(main())
