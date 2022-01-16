import discord
from numpy.random import uniform

class BotUser:
  """Classe représentant un utilisateur du bot MétéoDevin. Est considéré comme utilisateur du bot tout membre étant présent sur un des serveurs sur lequel se trouve MétéoDevin. La classe reprend les fonctionnalités de la classe discord.Member au travers de l'attribut discordMember qui sert de référence vers une instance de cette classe. Cette classe permet l'ajout de fonctionnalités spécifique à chaque utilisateur du bot, tel que l'ajout d'emojis sur certains messages de l'utilisateur représenté par une instance de cette classe"""

  #Variables de classe:
  COMMON_MESSAGE = 0        #Message commun

  #Constructeur de la classe
  def __init__(self, discordMember : discord.Member) -> None:
    """Constructeur de la classe BotUser. Permet de générer un nouvel utilisateur du bot MétéoDevin.
    Paramètres :  - discordMember : référence vers l'instance de la classe discord.Member représentant l'utilisateur du bot à créer
                  - emoji : [Optionnel] reaction par défaut que le bot va ajouter aux messages envoyés par l'utilisateur"""
    self.discordMember = discordMember
    self.emojis = {}
  

  def setEmoji(self, emoji : str, freq : float, typeMessage : int = COMMON_MESSAGE) -> None:
    """Modifie l'emoji spécifié pour le type de message passé en paramètre de la méthode.
    Paramètres :  - emoji : chaine de caractère représentant l'unicode de l'emoji
                  - freq : probabilité qu'une réaction correspondant à l'émoji soit ajouté au message du type typeMessage. Nombre compris entre 0 et 1.
                  - typeMessage : type de messages auquel l'emoji devra être ajouté"""
    if freq < 0 or freq > 1:
      raise ValueError("BotUser.setEmoji :  Freq must be between 0 and 1 !")
    self.emojis[typeMessage] = (emoji, freq)



  async def addReaction(self, msg : discord.Message, typeMessage = COMMON_MESSAGE)-> None:
    """Ajoute une réaction au message msg envoyé par l'utilisateur.
    Paramètres: - msg: message envoyé par l'utilisateur
                - typeMessage: type du message envoyé"""
    emoji, prob = self.emojis.get(typeMessage, ("", 0))
    if emoji != "" and uniform() <= prob:
      await msg.add_reaction(emoji)
