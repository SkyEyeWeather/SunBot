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

    @staticmethod
    def performRequest(request) -> dict :
        """Perform request contains in request attribute"""
        reponse = requests.get(request)
        if reponse.status_code != 200 :
            print(f"performRequest : Une erreur (code {reponse.status_code}) est survenue lors de l'exécution de la requête {request}")
            return {}
        print(reponse.json())
        return reponse.json()

    @staticmethod
    def dailyMeteoRequest(nomLieu) -> dict :
        """Réalise une requ$ete auprès de l'API Visual Crossing pour récupérer
        la météo du jour pour la localité dont le nom est passé en paramètre
        # Paramètre :
        * nomLieu : nom de la localité dont on souhaite obtenir la météo du jour
        # Retourne :
        Le dictionnaire représentant la réponse de l'API à la requête sous formde de
        dictionnaire"""

        request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{nomLieu}/today?unitGroup=metric&include=days&key={os.environ['idVisualCrossing']}&contentType=json&lang=fr"
        return VisualCrossingHandler.performRequest(request)

    @staticmethod
    def dailyRainRequest(localityName):
        """Perform a request to Visual Crossing API to retrieve data about hourly rain in the
        current day for the locality whose name is passed into argument.
        # Parameter :
        * locality name : name of the locality whose wants get data about rain conditions in the current day
        #Return :
        Request response from the Visual Crossing API, in a dictionnary (JSON format)"""

        request = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{localityName}/today?unitGroup=metric&elements=datetime%2CdatetimeEpoch%2Cprecip%2Cprecipprob%2Cprecipcover%2Cpreciptype%2Csnow%2Csource&include=hours%2Cdays&key=97BCTBN3FWN3U36QZKRG8J4A4&contentType=json&lang=fr"
        return VisualCrossingHandler.performRequest(request)

