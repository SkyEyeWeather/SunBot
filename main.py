#Importation des différents modules
import logging
import os
import discord
from discord.ext import commands
from discord import app_commands
import threading
import json
import requests
import numpy as np
import time
from PIL import Image

import sunbot.sunbot as sunbot
from sunbot.apiHandler.VisualCrossingHandler import VisualCrossingHandler
from sunbot.apiHandler.discordHandler import DiscordHandler

import sunbot.BotUser as BotUser
import sunbot.weather.Meteo as Meteo

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
sunController = SunController(sunBot)
sunController.on_ready()
vcRequestHandler = VisualCrossingHandler()
discordAPI_handler = DiscordHandler()
dictUsersBot = {}
dailyMeteo = Meteo.DailyMeteo(vcRequestHandler, dictUsersBot)



#==================================
#     Evénements liés au bot
#==================================

@sunBot.event
async def on_ready(): 
  await sunController.on_ready()

  """
  #Création du thread écoutant les alertes météos:
  print("Génération des webhooks...")
  webhookServeurTest1 = discord.Webhook.from_url(
    'https://discord.com/api/webhooks/923863299270013018/6jfjT1QtrZ8UCXM1aEUhUD7z5G5Or9S3loFvlQs34Age8hX7VPfrD4UUQvGXCzmDN0Oo', adapter=discord.RequestsWebhookAdapter())
  webhookServeurCUPGE = discord.Webhook.from_url(
    'https://discord.com/api/webhooks/921547043196002324/NJohjH9dduqidXHvV4Ei9V4KuIUvOiAPnbMEVPf_x06CUStZou0TlTapQi3B1i_zuLfp', adapter=discord.RequestsWebhookAdapter())
  webhookServeurPrive = discord.Webhook.from_url(
    'https://discord.com/api/webhooks/965521867026866196/M_nmSDjgplk8a6DAbzAD8qZVEMBoVvR1FF9Mcts_-NQRg3Qc5lvXmFSSgUJxgDcAOQb5', adapter=discord.RequestsWebhookAdapter())
  webhookServeurTest2 = discord.Webhook.from_url(
    'https://discord.com/api/webhooks/990651246643929158/S75JOEUf-_clJXMhp22x2QCmgJd-W40U7FTGUtIvODWZteKqrBkKo2MnRAJ2hOojSMSx', adapter=discord.RequestsWebhookAdapter())
  alerteMeteo = Meteo.AlerteMeteo(vcRequestHandler)
  #alerteMeteo.addWebhook(webhookServeurTest1)
  #alerteMeteo.addWebhook(webhookServeurPrive)
  alerteMeteo.start()
  print("Webhook alerte météo prêt")
  #Création du thread écoutant les informations météo quotidiennes :
  dailyMeteo.addWebhook(webhookServeurCUPGE)
  #dailyMeteo.addWebhook(webhookServeurTest1)
  dailyMeteo.addWebhook(webhookServeurPrive)
  dailyMeteo.addWebhook(webhookServeurTest2)
  dailyMeteo.start()
"""


@sunBot.event
async def on_member_join(member):
  await sunController.on_member_join(member)


@sunBot.event
async def on_message(message):
  await sunController.on_message(message)
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

@sunBot.command(name="setMP", brief="Autorise / Interdit les MP du bot (dailyMeteo...)")
async def mp(ctx):
  """Enable / Disable private message for the user that call this command"""
  dictUsersBot[ctx.author.id].mp = not dictUsersBot[ctx.author.id].mp
  if dictUsersBot[ctx.author.id].mp:
    dailyMeteo.addUserToList(ctx.author.id)
    await ctx.channel.send("Je vous enverrai maintenant les bulletins météo par message privé \U0001f973 !")
  else:
    if not dailyMeteo.delUserFromList(ctx.author.id):
      print(f"MP : L'identifiant {ctx.author.id} n'est pas dans la liste des ID")
    await ctx.channel.send("Je ne vous enverrai plus de message privé !")


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


@sunBot.tree.command(name="ping", description="Si je suis réveillé, je réponds pong! Sinon... et bien c'est que je dors 😴", guild=discord.Object(id=1029313313827471413))
async def ping(interaction : discord.Interaction):
  await sunController.ping(interaction)


@sunbot.betaFunction
@sunBot.command(name="meteo", brief="Pour obtenir la météo actuelle d'une localité")
async def meteo(ctx : discord.ext.commands.Context, *args):
  nomLocalite = " ".join(args)
  #Si une localité n'est pas spécificiée dans la commande :
  if nomLocalite in (" ", ""):
    nomLocalite = dictUsersBot[ctx.author.id].favMeteo
  print("Recherche de la météo pour la localité {} par {}".format(nomLocalite, ctx.author.name))
  url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&lang=fr&units=metric".format(nomLocalite, os.environ["idOpenWeather"])
  reponse = requests.get(url)
  if reponse.status_code != 200:
      print("Echec de lors de la récupération de l'API. Code erreur : {}".format(reponse.status_code))
      await ctx.channel.send("Désolé, une erreur est survenue lors de l'exécution de la commande \U0001f972")
  else:
      embed = Meteo.jsonToMeteoCourante(reponse.json())
      await ctx.channel.send(embed=embed)


@sunBot.tree.command(name="pluie", description="Quand va-t-il pleuvoir aujourd'hui? ☔",  guild=discord.Object(id=1029313313827471413))
@app_commands.describe(place_name="Nom de la localité")
async def pluie(interaction : discord.Interaction, place_name : str) -> None:
  await sunController.pluie(interaction, place_name)


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

@sunBot.command(name="test", brief="Commande de test [Admin]")
async def test(ctx : commands.Context) -> None:
  """"""
  Meteo.DailyMeteo.createDailyWeatherImage("")

@sunBot.command(name="disconnect", brief="Vous voulez vraiment me tuer ?!! [Admin]")
@sunbot.adminFunction
async def disconnect(unused_ctx):
  print("Déconnexion du bot...")
  #Enregistrement des données des utilisateurs (un fichier par utilisateur) :
  for userId in dictUsersBot :
    dictUsersBot[userId].saveUser(PATH_SAVE_USER_REP)
  print("Déconnexion terminée")
  await sunBot.logout()


#####################################################################################################
#ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES - ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES
#####################################################################################################

sunBot.run("ODk2MTMwNzY5MTE2ODg5MDg4.YWCo0A.D85z93cfwKwfcHSkeGdPW7PJpJo")
