import discord
import os
import requests
from numpy.random import uniform


class BotUser:
	"""Classe représentant un utilisateur du SunBot. Est considéré comme utilisateur du bot tout membre étant présent sur un des serveurs sur lequel se trouve SunBot. La classe reprend les fonctionnalités de la classe discord.Member au travers de l'attribut discordMember qui sert de référence vers une instance de cette classe. Cette classe permet l'ajout de fonctionnalités spécifique à chaque utilisateur du bot, tel que l'ajout d'emojis sur certains messages de l'utilisateur représenté par une instance de cette classe ou encore l'ajout de favoris"""

	#Variables de classe:
	COMMON_MESSAGE = 0  #Message commun


	#Constructeur de la classe
	def __init__(self, emojis=None, favMeteo="Toulouse") -> None:
	    """Constructeur de la classe BotUser. Permet de générer un nouvel utilisateur du SunBot.
	    Paramètres :  - discordMember : référence vers l'instance de la classe discord.Member représentant l'utilisateur du bot à créer
	                  - emoji : [Optionnel] reaction par défaut que le bot va ajouter aux messages envoyés par l'utilisateur"""
	    if emojis is None:
	        emojis = {}
	    self.emojis = emojis
	    self.favMeteo = favMeteo
	
	def __str__(self):
		return " emoji = {}, favori météo = {}".format(self.emojis,
													   self.favMeteo)

	def setEmoji(self, emoji: str, freq: float, typeMessage: int = 0) -> None:
		"""Modifie l'emoji spécifié pour le type de message passé en paramètre de la méthode.
	Paramètres :  - emoji : chaine de caractère représentant l'unicode de l'emoji
				  - freq : probabilité qu'une réaction correspondant à l'émoji soit ajouté au message du type typeMessage. Nombre compris entre 0 et 1.
				  - typeMessage : type de messages auquel l'emoji devra être ajouté"""
		if freq < 0 or freq > 1:
			raise ValueError(
				"BotUser.setEmoji :  Freq must be between 0 and 1 !")
		self.emojis[typeMessage] = (emoji, freq)

	async def setFavMeteo(self, ctx, nomLocalite) -> None:
		print("Test favori : recherche de la météo pour la localité {} par {}".
			  format(nomLocalite, ctx.author.name))
		url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&lang=fr&units=metric".format(
			nomLocalite, os.environ['idOpenWeather'])
		reponse = requests.get(url)
		#Si la localité n'existe pas dans l'API d'OpenWeather
		if reponse.status_code != 200:
			print(
				"Echec de lors de la récupération de l'API. Code erreur : {}".
				format(reponse.status_code))
			await ctx.channel.send(
				"Désolé, je ne reconnais par la localité...\U0001f972")
		else:
			await ctx.channel.send("Favori modifié avec succès !")
			self.favMeteo = nomLocalite

	async def addReaction(self,
						  msg: discord.Message,
						  typeMessage=0) -> None:
		"""Ajoute une réaction au message msg envoyé par l'utilisateur.
	Paramètres: - msg: message envoyé par l'utilisateur
				- typeMessage: type du message envoyé"""
		emoji, prob = self.emojis.get(typeMessage, ("", 0))
		if emoji != "" and uniform() <= prob:
			try:
				await msg.add_reaction(emoji)
			except discord.errors.NotFound:
				print("Le message a disparu !")
