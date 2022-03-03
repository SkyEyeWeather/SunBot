#Module used in this module
import discord
import os
import time
import requests
from discord.ext import commands

from sunBotModule.SunBotHelpCommand import SunBotHelpCommand
import Meteo



#============================
#    GLOBAL VARIABELS
#============================

sunBot = commands.Bot(command_prefix='+', intents=discord.Intents.all(), help_command=SunBotHelpCommand())
dictUsersBot = {}


#============================
#        DECORATORS
#============================

def betaFunction(function):
  """Decorator used to indicate that a function can only be call by robot's maintainers"""
  async def fonctionModifie(*args, **opt):
      if args[0].author.id != 691614947280551936:
          await args[0].channel.send(
              "J'aimerais pouvoir t'aider, mais mon créateur (ce ravagé) me l'a interdit car cette fonctionnalité est actuellement en travaux !"
          )
      else:
          await function(*args, **opt)
  return fonctionModifie


def adminFunction(function):
  """Decorator used to indicate that function can only be call by an adminstrator of 
  the bot. Other users will receive an error message."""
  async def fonctionModifie(*args, **kwargs):
    if args[0].author.id != 691614947280551936 and args[0].author.id != 690593377250443374:
      await args[0].channel.send(
            "Il faut être ravagé ou complètement chèvre pour utiliser cette commande !")
    else:
        await function(*args, **kwargs)
  return fonctionModifie


#====================
#    FUNCTIONS
#====================
  
async def deleteCommand(ctx : discord.ext.commands.Context):
  await ctx.message.delete()


  
#====================
#    BOT'S COMMANDS 
#====================

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


@sunBot.command(name="ping", brief="Si je suis réveillé, je réponds pong ! Sinon c'est que je dors...")
async def ping(ctx):
  await ctx.channel.send("pong !")
  await deleteCommand(ctx)



@sunBot.command(name="meteo",
                brief="Pour obtenir la météo actuelle d'une localité")
async def meteo(ctx : discord.ext.commands.Context, *args):
  nomLocalite = " ".join(args)
  #Si une localité n'est pas spécificiée dans la commande :
  if nomLocalite == " " or nomLocalite == "":
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