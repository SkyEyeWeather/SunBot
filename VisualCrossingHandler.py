#=====================================
#	Modules utilisés par la classe
#=====================================
import requests
import os
from MetaSingleton import MetaSingleton

#==============================
#	Déclaration de la classe
#===============================

class VisualCrossingHandler(metaclass = MetaSingleton) :
	"""Classe singleton permettant de centraliser et de gérer les requêtes vers l'API
	de Visual Crossing ainsi que les réponses obtenues"""
	

	def performRequest(cls, request) -> dict :
		"""Perform request contains in request attribute"""
		reponse = requests.get(request)
		if reponse.status_code != 200 :
			print(f"performRequest : Une erreur (code {reponse.status_code}) est survenue lors de l'exécution de la requête {request}")
			return {}
		print(reponse.json())
		return reponse.json()
		
	def dailyMeteoRequest(cls, nomLieu) -> dict :
		"""Réalise une requ$ete auprès de l'API Visual Crossing pour récupérer
		la météo du jour pour la localité dont le nom est passé en paramètre
		# Paramètre :
		* nomLieu : nom de la localité dont on souhaite obtenir la météo du jour
		# Retourne :
		Le dictionnaire représentant la réponse de l'API à la requête sous formde de
		dictionnaire"""

		request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{nomLieu}/today?unitGroup=metric&include=days&key={os.environ['idVisualCrossing']}&contentType=json&lang=fr"
		return cls.performRequest(request)


