#=====================================
#	Modules utilisés par la classe
#=====================================
import requests
from MetaSingleton import MetaSingleton

#==============================
#	Déclaration de la classe
#===============================

class VisualCrossingHandler(metaclass = MetaSingleton) :
	"""Classe singleton permettant de centraliser et de gérer les requêtes vers l'API
	de Visual Crossing ainsi que les réponses obtenues"""
	
	request = ""

	def performRequestTest(cls, request) -> dict :
		"""Perform request contains in request attribute"""
		reponse = requests.get(request)
		if reponse.status_code != 200 :
			print("performRequest : Une erreur (code {}) est survenue lors de l'exécution de la requête {}".format(reponse.status_code, request))
			return {}
		print(reponse.json())
		return reponse.json()
		
		