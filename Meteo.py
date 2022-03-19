import discord
from WebhookEvent import WebhookEvent
import time
import os
from datetime import datetime
import requests

#Constantes direction vent :
VENT_NORD = "\u2B07"
VENT_NORD_EST = "\u2199"
VENT_EST = "\u2B05"
VENT_SUD_EST = "\u2196"
VENT_SUD = "\u2B06"
VENT_SUD_OUEST = "\u2197"
VENT_OUEST = "\u27A1"
VENT_NORD_OUEST = "\u2198"

dictWeatherCode = {
    200: "200.jpg",
    201: "200.jpg",
    202: "200.jpg",
    210: "200.jpg",
    211: "200.jpg",
    212: "200.jpg",
    221: "200.jpg",
    230: "200.jpg",
    231: "200.jpg",
    232: "200.jpg",
    300: "300.jpg",
    301: "300.jpg",
    302: "300.jpg",
    310: "300.jpg",
    311: "300.jpg",
    312: "300.jpg",
    313: "300.jpg",
    314: "300.jpg",
    321: "300.jpg",
    500: "500.jpg",
    501: "500.jpg",
    502: "500.jpg",
    503: "500.jpg",
    504: "500.jpg",
    511: "500.jpg",
    520: "500.jpg",
    521: "500.jpg",
    522: "500.jpg",
    531: "500.jpg",
    600: "600.jpg",
    601: "600.jpg",
    602: "600.jpg",
    611: "600.jpg",
    612: "600.jpg",
    613: "600.jpg",
    615: "600.jpg",
    616: "600.jpg",
    620: "600.jpg",
    621: "600.jpg",
    622: "600.jpg",
    701: "701.jpg",
    711: "701.jpg",
    721: "721.jpg",
    731: "701.jpg",
    741: "721.jpg",
    751: "701.jpg",
    761: "701.jpg",
    762: "701.jpg",
    771: "701.jpg",
    781: "781.jpg",
    800: "800d.jpg",
    #8002  : "800n.jpg",
    801: "801d.jpg",
    #8012  : "801n.jpg",
    802: "802d.jpg",
    #8022  : "802n.jpg",
    803: "803d.jpg",
    #8032  : "803n.jpg",
    804: "804.jpg"
}


def degToStrDirectVent(directionVent: int) -> tuple:
    """Convertie l'angle passé en paramètre en direction cardinal afin de rendre l'affichage
  de cette information plus conviviale
  Paramètre : - directionVent : direction du vent (en degré) à convertir
  Retour : un tuple contenant un émoji flèche donnant la direction du vent, puis une chaîne donnant
  la direction carnidale en suivant la norme."""
    if directionVent < 157:
        if directionVent < 67:
            if directionVent < 22:
                return (VENT_NORD, "N")
            return (VENT_NORD_EST, "NE")
        elif directionVent < 112:
            return (VENT_EST, "E")
        else:
            return (VENT_SUD_EST, "SE")
    else:
        if directionVent < 257:
            if directionVent < 212:
                return (VENT_SUD, "S")
            return (VENT_SUD_OUEST, "SW")
        else:
            if directionVent < 292:
                return (VENT_OUEST, "W")
            return (VENT_NORD_OUEST, "NW")


def jsonToMeteoCourante(messageJson: dict) -> tuple:
    """Fonction qui converti un message au format JSON issu d'un appel à l'API d'OpenWeather en 
  message affichable sur Discord pour la météo courante."""
    print(messageJson)
    #Création de l'embed :
    messageToSend = discord.Embed(
        title="Météo actuelle sur {} [{}]".format(
            messageJson["name"], messageJson["sys"]["country"]),
        description=messageJson["weather"][0]["description"],
        color=0x77b5fe)
    thumbnail = discord.File(
        "./Data/Images/{}".format(dictWeatherCode[int(
            messageJson["weather"][0]["id"])]), "thumbnail.jpg")
    messageToSend.set_thumbnail(url="attachment://thumbnail.jpg")

    #Ajout des différents domaines :
    messageToSend.add_field(name="Température :",
                            value=str(round(messageJson["main"]["temp"], 1)) +
                            "°C",
                            inline=True)
    messageToSend.add_field(
        name="Température ressentie :",
        value=str(round(messageJson["main"]["feels_like"], 1)) + "°C",
        inline=True)
    messageToSend.add_field(name="Pression au niveau de la mer :", value=str(messageJson["main"]["pressure"]) + "hPa", inline=False)
    messageToSend.add_field(name="Humidité :", value=str(messageJson["main"]["humidity"]) + "%", inline=False)
    directionVent = degToStrDirectVent(messageJson["wind"]["deg"])
    messageToSend.add_field(name="Direction vent :", value=directionVent[0] + "  [**" + directionVent[1] + "**]", inline=True)
    messageToSend.add_field(name="Vitesse vent :", value=str(round(messageJson["wind"]["speed"] * 3.6, 2)) + "km/h", inline=True)
    vitesseRafale = messageJson["wind"].get("gust", -1.)
    if vitesseRafale >= 0.:
        messageToSend.add_field(name="Rafale :", value=str(round(vitesseRafale * 3.6, 2)) + "km/h", inline=True)
    messageToSend.add_field(name="Visibilité", value=str(messageJson["visibility"]) + "m", inline=False)
    #Pied de l'embed
    messageToSend.set_footer(text="Data from OpenWeather ({})".format(messageJson["base"]), icon_url="https://openweathermap.org/themes/openweathermap/assets/img/logo_white_cropped.png")
    return (messageToSend, thumbnail)


class AlerteMeteo(WebhookEvent):
    """Classe permettant de récupérer les alertes météo générées par l'API et de les transmettre sous forme
  de Webhook aux serveurs Discord reliés"""
    def __init__(self):
        WebhookEvent.__init__(
            self,
            "https://api.openweathermap.org/data/2.5/onecall?lat=43.604259&lon=1.44367&exclude=current,minutely,hourly,daily&appid={}&lang=fr"
            .format(os.environ['idOpenWeather']))

        #Attributs de la classe
        self.decompteurStopAlerte = 0  #Nombre de requêtes consécutives ne renvoyant pas d'alerte en cours avant de considérer la levée de l'alerte.

    def run(self):
        while True:
            time.sleep(300)
            reponse = requests.get(self.url)
            if reponse.status_code != 200:
                print("AlerteMeteo : Une erreur est survenue lors du traitement de la requête de récupération d'alerte météo. code erreur = {}".format(reponse.status_code))
            else:
                reponseJson = reponse.json()
                #S'il n'y a aucune alerte en cours sur Toulouse :
                if reponseJson.get("alerts", None) is None:
                    print("AlerteMeteo : Aucune alerte en cours sur Toulouse")
                    self.decompteurStopAlerte -= 1  #Décompte de 1 pour indiquer qu'aucune alerte n'a été renvoyée pour la requête en cours
                else:
                    #Si l'alerte vient de débuter on envoie un webHook :
                    if self.decompteurStopAlerte <= 0:
                        self.decompteurStopAlerte = 2
                        #Création de l'embed à envoyer
                        alerteToSend = discord.Embed(title="Alerte météo", description=reponseJson["alerts"][0]["event"],
                            color=0x77b5fe)

                        alerteToSend.add_field(
                            name="Début du phénomène :",
                            value=datetime.fromtimestamp(
                                reponseJson["alerts"][0]["start"]),
                            inline=False)
                        alerteToSend.add_field(
                            name="Fin du phénomène :",
                            value=datetime.fromtimestamp(
                                reponseJson["alerts"][0]["end"]),
                            inline=False)
                        alerteToSend.add_field(
                            name="Description :",
                            value=reponseJson["alerts"][0]["description"],
                            inline=False)
                        #Envoie de l'embed sur les différents serveurs reliés au bot:
                        for webhook in self.webhooksList:
                            time.sleep(1)
                            logoMeteoFrance = discord.File(
                                "./Data/Images/logoMeteoFrance.png",
                                "logoMeteoFrance.png")
                            alerteToSend.set_thumbnail(
                                url="attachment://logoMeteoFrance.png")
                            alerteToSend.set_footer(
                                text="Source : Météo France via OpenWeather")
                            webhook.send(file=logoMeteoFrance,
                                         embed=alerteToSend)
                    #Si l'alerte a déjà été signalée :
                    else:
                        self.decompteurStopAlerte = 2
                        print("AlerteMeteo : Alerte en cours déjà signalée")


class DailyMeteo(WebhookEvent):
    """Classe permettant de générer un thread ayant pour objectif de récupérer la météo du jour via l'API de openweather
  et de d'envoyer un webHook sur les serveurs connectés"""
    def __init__(self):
        WebhookEvent.__init__(
            self,
            "https://api.openweathermap.org/data/2.5/onecall?lat=43.604259&lon=1.44367&exclude=current,minutely,hourly,alerts&appid={}&lang=fr&units=metric"
            .format(os.environ['idOpenWeather']))

        #Attributs de la classe
        self.alreadySend = False  #Booleen to indicate if daily message has already been sent

    def run(self):
        while True:
            time.sleep(60)
            currentTime = time.localtime()
            hour = currentTime[3] + 1
            minute = currentTime[4]
            #Si l'heure de reset quotidienne a été atteinte, mettre à jour le drapeau
            if (hour == 1) and (minute >= 0 and minute <= 1):
                self.alreadySend = False
            #Si l'heure d'envoyer le weebhook a été atteinte et que le webhook n'a pas déjà été envoyé:
            if (hour == 7) and (minute >= 0
                                and minute <= 1) and not self.alreadySend:
                reponse = requests.get(self.url)
                if reponse.status_code != 200:
                    print(
                        "DailyMeteo : Une erreur est survenue lors de la récupération des informations de l'API"
                    )
                else:
                    self.alreadySend = True
                    reponseJson = reponse.json()
                    #Création de l'embed à envoyer
                    dailyMeteoToSend = discord.Embed(
                        title="Météo du jour sur Toulouse",
                        description=
                        "\u26A0\uFE0F Changement d'API à venir \u26A0\uFE0F",
                        color=0x77b5fe)

                    #Domaines de l'Embed
                    dailyMeteoToSend.add_field(
                        name="Temps :",
                        value="{}".format(reponseJson["daily"][0]["weather"][0]
                                          ["description"]),
                        inline=False)
                    dailyMeteoToSend.add_field(
                        name="Température max :",
                        value="{}°C".format(
                            round(reponseJson["daily"][0]["temp"]["max"], 1)))
                    dailyMeteoToSend.add_field(
                        name="Température min :",
                        value="{}°C".format(
                            round(reponseJson["daily"][0]["temp"]["min"], 1)))
                    dailyMeteoToSend.add_field(
                        name="Température moyenne :",
                        value="{}°C".format(
                            round(reponseJson["daily"][0]["temp"]["day"], 1)))
                    dailyMeteoToSend.add_field(
                        name="Température ressentie :",
                        value="{}°C".format(
                            round(reponseJson["daily"][0]["feels_like"]["day"],
                                  1)))
                    dailyMeteoToSend.add_field(
                        name="Pression au niveau de la mer :",
                        value="{}hPa".format(
                            reponseJson["daily"][0]["pressure"]),
                        inline=False)
                    dailyMeteoToSend.add_field(
                        name="Humidité :",
                        value="{}%".format(
                            reponseJson["daily"][0]["humidity"]),
                        inline=False)
                    directionVent = degToStrDirectVent(
                        reponseJson["daily"][0]["wind_deg"])
                    dailyMeteoToSend.add_field(name="Direction vent :",
                                               value="{} **{}**".format(
                                                   directionVent[0],
                                                   directionVent[1]))
                    dailyMeteoToSend.add_field(
                        name="Vitesse vent :",
                        value="{}km/h".format(
                            round(reponseJson["daily"][0]["wind_speed"] * 3.6,
                                  2)))

                    vitesseRafale = reponseJson["daily"][0].get("gust", -1.)
                    if vitesseRafale >= 0.:
                        dailyMeteoToSend.add_field(name="Rafale :",
                                                   value="{}km/h".format(
                                                       round(
                                                           vitesseRafale * 3.6,
                                                           2)),
                                                   inline=True)
                    dailyMeteoToSend.add_field(
                        name="Risque de précipitation :",
                        value="{}%".format(reponseJson["daily"][0]["pop"] *
                                           100),
                        inline=False)
                    dailyMeteoToSend.add_field(
                        name="Indice UV :",
                        value="{}".format(reponseJson["daily"][0]["uvi"],
                                          inline=False),
                        inline=False)
                    dailyMeteoToSend.add_field(
                        name="Levé du soleil:",
                        value="{}:{}".format(
                            int(
                                datetime.fromtimestamp(
                                    reponseJson["daily"][0]
                                    ["sunrise"]).strftime("%H")) + 1,
                            datetime.fromtimestamp(
                                reponseJson["daily"][0]["sunrise"]).strftime(
                                    "%M")))
                    dailyMeteoToSend.add_field(
                        name="Couché du soleil:",
                        value="{}:{}".format(
                            int(
                                datetime.fromtimestamp(
                                    reponseJson["daily"][0]
                                    ["sunset"]).strftime("%H")) + 1,
                            datetime.fromtimestamp(reponseJson["daily"][0]
                                                   ["sunset"]).strftime("%M"))
                    )  #Envoie l'embed sur les différents serveurs reliés au bot :
                    for webhook in self.webhooksList:
                        time.sleep(1)
                        dailyMeteoLogo = discord.File(
                            "./Data/Images/{}".format(dictWeatherCode[
                                reponseJson["daily"][0]["weather"][0]["id"]]),
                            "dailyMeteoLogo.jpg")
                        dailyMeteoToSend.set_thumbnail(
                            url="attachment://dailyMeteoLogo.jpg")
                        dailyMeteoToSend.set_footer(
                            text="Données de l'API d'OpenWeather",
                            icon_url=
                            "https://openweathermap.org/themes/openweathermap/assets/img/logo_white_cropped.png"
                        )
                        webhook.send(embed=dailyMeteoToSend,
                                     file=dailyMeteoLogo)
