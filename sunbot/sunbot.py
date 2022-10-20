
#==================================
#       CONSTANTS DECLARATION
#==================================

USER_BACKUP_REPERTORY_PATH = "./Data/Save/Users/"
SERVER_BACKUP_REPERTORY_PATH = "./Data/Save/Servers/"

GIF_REPERTORY_PATH = "./Data/Images/Gifs/"
APPLE_HEAD_GIF_NAME = "appleHead.gif"


#===================================
#       DECORATORS DECLARATION
#===================================

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
    if args[0].author.id not in (691614947280551936, 690593377250443374):
      await args[0].channel.send(
            "Il faut être ravagé pour utiliser cette commande !")
    else:
        await function(*args, **kwargs)
  return fonctionModifie