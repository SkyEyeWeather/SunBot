#Importation des différents modules
import os
import discord
import requests
import json
import os
import time
from pickle import Pickler, Unpickler
import numpy as np
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, CheckFailure, check

from WebServer import keep_alive
from SunBotHelpCommand import SunBotHelpCommand
import BotUser
import Meteo
import random



PATH_SAVE_USER_REP = "./Data/Save/Users/"


#====================================
#          Décorateurs
#====================================


def betaFunction(function):
    async def fonctionModifie(*args, **opt):
        if args[0].author.id != 691614947280551936:
            await args[0].channel.send(
                "J'aimerais pouvoir t'aider, mais mon créateur (ce ravagé) me l'a interdit car cette fonctionnalité est actuellement en travaux !"
            )
        else:
            await function(*args, **opt)

    return fonctionModifie


def adminFunction(function):
  async def fonctionModifie(*args, **kwargs):
    if args[0].author.id != 691614947280551936 and args[0].author.id != 690593377250443374:
      await args[0].channel.send(
            "Il faut être ravagé ou complètement chèvre pour utiliser cette commande !")
    else:
        await function(*args, **kwargs)

  return fonctionModifie


#=======================================
#     Fonctions associées au bot
#=======================================

#Déclaration du robot:
sunBot = commands.Bot(command_prefix='+',
                      intents=discord.Intents.all(),
                      help_command=SunBotHelpCommand())
dictUsersBot = {}
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
messageTeteDePomme = 0  #Nombre de messages "tête de pomme" consécutifs (on suppose que l'invocation n'est faite que sur un erveur à la fois)

#==================================
#     Evénements liés au bot
#==================================


@sunBot.event
async def on_ready():
    #Création du dictionnaire des membres (à voir plus tard pour diff serveur) :
    print("Initialisation du bot...")
    print("Chargement des données des utilisateurs...")
    for member in sunBot.get_all_members():
      with open("{}/{}.txt".format(PATH_SAVE_USER_REP, member.id), 'rb') as userFile :
        print("Chargement des données de l'utilisateur n°{}".format(member.id))
        userUnpickler = Unpickler(userFile)
        dictUsersBot[member.id] = userUnpickler.load()
    print("Chargement des données utilisateur : OK")
    #Création du thread écoutant les alertes météos:
    webhookServeurTest1 = discord.Webhook.from_url(
        'https://discord.com/api/webhooks/923863299270013018/6jfjT1QtrZ8UCXM1aEUhUD7z5G5Or9S3loFvlQs34Age8hX7VPfrD4UUQvGXCzmDN0Oo',
        adapter=discord.RequestsWebhookAdapter())
    #webhookServeurTest2 = discord.Webhook.from_url('https://discord.com/api/webhooks/927208384946638898/zRq8mLQT2aEV4GqufzrEYOFAdOdaTVxNypOuXDc4mgpnZCBNaQXpZbl1zqmwXS8pp4hC', adapter=discord.RequestsWebhookAdapter())
    webhookServeurCUPGE = discord.Webhook.from_url(
        'https://discord.com/api/webhooks/921547043196002324/NJohjH9dduqidXHvV4Ei9V4KuIUvOiAPnbMEVPf_x06CUStZou0TlTapQi3B1i_zuLfp',
        adapter=discord.RequestsWebhookAdapter())
    alerteMeteo = Meteo.AlerteMeteo()
    alerteMeteo.addWebhook(webhookServeurTest1)
    alerteMeteo.start()
    print("Webhook alerte météo prêt")
    #Création du thread écoutant les informations météo quotidiennes :
    dailyMeteo = Meteo.DailyMeteo()
    dailyMeteo.addWebhook(webhookServeurCUPGE)
    dailyMeteo.addWebhook(webhookServeurTest1)
    #dailyMeteo.addWebhook(webhookServeurTest2)
    dailyMeteo.start()
    print("Webhook daily météo prêt")
    print("SunBot est chaud patate!")


@sunBot.event
async def on_member_join(member):
    print("{} a rejoint le serveur {} !".format(member.name,
                                                member.guild.name))
    userBot = BotUser.BotUser(member)
    dictUsersBot[member.id] = userBot
    if member.guild.id == 816226592556580865:
        channel = sunBot.get_channel(816226592556580868)
        await channel.send(
            "Bienvenue sur le serveur {}! Je suis SunBot, bot spécialiste de la météo (ou pas)! Tu peux utiliser +help dans le channel des bots pour en savoir plus sur moi!"
            .format(member.mention))


@sunBot.event
async def on_message(message):

    global messageTeteDePomme

    await sunBot.process_commands(message)
    if not message.author.bot:
        await dictUsersBot[message.author.id].addReaction(message)
    messageMin = message.content.lower()
    #Si le message correspond à l'invocation tête de pomme
    if messageMin in ["tête de pomme", "tete de pomme", "#tetedepomme"]:
        messageTeteDePomme += 1
        #Si le message a été répété 3 fois de suite, on invoque le gif :
        if messageTeteDePomme == 3:
            messageTeteDePomme = 0
            print("Invocation tête de pomme !")
            embedToSend = discord.Embed(
                title="Et tu savais qu'à Jean Jaurès...", color=0xff0000)
            gifTeteDePomme = discord.File("./Data/TeteDePomme.gif",
                                          "TeteDePomme.gif")
            embedToSend.set_image(url="attachment://TeteDePomme.gif")
            await message.channel.send(embed=embedToSend, file=gifTeteDePomme)
    #Autres type de message :
    else:
        messageTeteDePomme = 0
        if "me foutre au sol" in messageMin and np.random.uniform() > 0.5:
            await message.reply(
                "Tu sais, il y a des gens qui disaient ça avant toi et qui ont fini ingénieurs aéronautique chez Boeing ! Donc ne te décourage pas \U0001f31e !"
            )
        if messageMin == "sinus":
            await message.channel.send("Tangente")
        if messageMin in ["patrick", "patou", "patoche", "pata", "patrikou"
                          ] and np.random.uniform() > 0.25:
            indiceGifToSend = int(np.random.uniform(0, len(listeGifMignons)))
            await message.reply(listeGifMignons[indiceGifToSend])
            await message.channel.send("Mignon !!")
        if "kernel is dead" in messageMin:
          indiceGifToSend = int(np.random.uniform(0, len(listeGifKernelDead)))
          await message.reply(listeGifKernelDead[indiceGifToSend])


@sunBot.event
async def on_disconnect():
  print("Déconnexion du bot...")
  #Si le répertoire de sauvegarde des données utilisateurs n'existe pas, le créer:
  if not os.path.exists(PATH_SAVE_USER_REP):
    print("on_disconnect : Répertoire de sauvegarde des utilisateurs inexistant.")
    os.makedirs(PATH_SAVE_USER_REP, exist_ok=True)
  #Enregistrement des données des utilisateurs (un fichier par utilisateur) :
  for userId in dictUsersBot.keys():
    print("Sauvegarde des données de l'utilisateur n°{}".format(userId))
    with open("{}/{}.txt".format(PATH_SAVE_USER_REP, userId), 'wb') as userFile:
      userPickler = Pickler(userFile)
      userPickler.dump(dictUsersBot[userId])
  print("Déconnexion terminée")


async def deleteCommand(ctx : discord.ext.commands.Context):
  await ctx.message.delete()

  
#=====================
# COMMANDES DE SUN BOT
#=====================

@adminFunction
async def adminSetEmoji(ctx, userId :int, emoji : str, freq : float):
  try :
    dictUsersBot[userId].setEmoji(emoji, freq)
  except KeyError:
    await ctx.channel.send("L'ID ne correspond à aucun utilisateur de mes services...\U0001f622")
  except ValueError:
    await ctx.channel.send("La fréquence doit être dans l'intervalle [0, 1] \U0001f620")
  else:
    await ctx.channel.send("L'emoji a bien été mis à jour \U0001f642")


@sunBot.command(
    name="ping",
    brief="Si je suis réveillé, je réponds pong ! Sinon c'est que je dors...")
async def ping(ctx):
  await ctx.channel.send("pong !")
  await deleteCommand(ctx)
  


@sunBot.command(name="meteo",
                brief="Pour obtenir la météo actuelle d'une localité")
async def meteo(*args, nomLocalite=""):
  print(len(args))
  ctx = args[0]
  #Si une localité est spécificiée dans la commande :
  if len(args) > 1:
    nomLocalite = args[1]
    for s in args[2:]:
      nomLocalite += " " + s
  #Sinon utilisé la localité favorite de l'utilisateur appelant:
  else:
    print("ok")
    nomLocalite = dictUsersBot[ctx.author.id].favMeteo
  print("Recherche de la météo pour la localité {} par {}".format(nomLocalite, ctx.author.name))
  url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&lang=fr&units=metric".format(nomLocalite, os.environ['idOpenWeather'])
  reponse = requests.get(url)
  if reponse.status_code != 200:
      print("Echec de lors de la récupération de l'API. Code erreur : {}".format(reponse.status_code))
      await ctx.channel.send("Désolé, une erreur est survenue lors de l'exécution de la commande \U0001f972")
  else:
      (embed, image) = Meteo.jsonToMeteoCourante(reponse.json())
      await ctx.channel.send(embed=embed, file=image)


@sunBot.command(
    name="pluie",
    brief=
    "Répond à la question existentielle : va t-il pleuvoir dans l'heure ? [en construction]"
)
async def pluie(ctx):
    print("Demande pluie dans l'heure demandé par {}".format(ctx.author.name))


@sunBot.command(name="favMeteo", brief="Envie de connaître la météo d'une localité sans te casser la tête ? Cette commande est pour toi !")
async def favMeteo(ctx, nomLocalte):
  await dictUsersBot[ctx.author.id].setFavMeteo(ctx, nomLocalte)

@sunBot.command(name="vocalConnect", brief="Vous m'avez appelez ? Je vous réponds (vraiment) ! [admin]")
@adminFunction
async def vocalConnect(ctx):
  channel = ctx.author.voice.channel
  await channel.connect()
  time.sleep(1)
  ctx.voice_client.play(discord.FFmpegPCMAudio("./Data/Source/alpha.mp3"))
  await deleteCommand(ctx)

@sunBot.command(name="vocalDisconnect", brief="Deconnexion serveur vocal [admin]")
@adminFunction
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
@adminFunction
async def disconnect(ctx):
  await sunBot.logout()



#ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES - ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES

keep_alive()
sunBot.run(os.environ["token"])