import discord
import threading
from VisualCrossingHandler import VisualCrossingHandler
from discordHandler import DiscordHandler


class WebhookEvent(threading.Thread):
    """Classe mère permettant d'envoyer des webhooks sur les serveurs à l'écoute à l'occurrence d'événements"""
    def __init__(self, url, apiHandler : VisualCrossingHandler):
        #Initialisation du thread :
        threading.Thread.__init__(self)
        self.daemon = True
      
        self.webhooksList = []    		#Liste des webhooks à l'écoute d'un événement
        self.url = url            		#Url contenant la requête à envoyer à l'API
        self.apiHandler = apiHandler	#Référence vers le gestionnaire de l'API Visual Crossing
      

    def addWebhook(self, webhook : discord.Webhook):
        """Ajout un listener à la liste des webhooks à l'écoute d'un événement"""
        self.webhooksList.append(webhook)
        
