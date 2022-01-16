import discord
import threading


class WebhookEvent(threading.Thread):
  """Classe mère permettant d'envoyer des webhooks sur les serveurs à l'écoute à l'occurrence d'événements"""
  def __init__(self, url):
    threading.Thread.__init__(self) 

    self.webhooksList = []    #Liste des webhooks à l'écoute d'un événement
    self.url = url            #Url contenant la requête à envoyer à l'API
  
  def addWebhook(self, webhook : discord.Webhook):
    """Ajout un listener à la liste des webhooks à l'écoute d'un événement"""
    self.webhooksList.append(webhook)