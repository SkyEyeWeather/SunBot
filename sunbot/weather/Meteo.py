import discord
from numpy import deprecate
from sunbot.WebhookEvent import WebhookEvent
import time
import os
from datetime import datetime
import requests
from PIL import Image, ImageFont, ImageDraw

from sunbot.apiHandler.VisualCrossingHandler import VisualCrossingHandler
from sunbot.apiHandler.discordHandler import DiscordHandler
from sunbot.SunImager import SunImage

#===========================================================#
#           CONSTANTES VARIABLES DECLARATIONS               #
#===========================================================#

#CONSTANTES FOR IMAGE GENERATION:

FONT_PATH = "./Data/Font/Ubuntu-R.ttf"
ICON_DIR_PATH = "./Data/Images/Icons/"

DAILY_IMAGE_PATH = "./Data/Images"
DAILY_IMAGE_NAME = "dailyImage.png"

BIG_FONT_SIZE =     80
MEDIUM_FONT_SIZE =  40
SMALL_FONT_SIZE =   20
ICON_SIZE =         (50, 50)

LEFT_ALIGNMENT = 20
CENTRE_ALIGNMENT = 320
UP_ALIGNMENT = 10
INTER_ALIGNMENT = 30
MIN_MAX_TEMP_ALIGNMENT = UP_ALIGNMENT + BIG_FONT_SIZE + 10
ITEMS_UP_ALIGNMENT = MIN_MAX_TEMP_ALIGNMENT + MEDIUM_FONT_SIZE + INTER_ALIGNMENT
TXT_VERTICAL_ALIGNMENT = LEFT_ALIGNMENT + ICON_SIZE[0] + INTER_ALIGNMENT
TXT_CENTRAL_VERTICAL_ALIGNMENT = CENTRE_ALIGNMENT + ICON_SIZE[0] + INTER_ALIGNMENT
TXT_HORIZONTAL_ALIGNMENT = 10

MAIN_ICON_SIZE = (MIN_MAX_TEMP_ALIGNMENT + MEDIUM_FONT_SIZE, MIN_MAX_TEMP_ALIGNMENT + MEDIUM_FONT_SIZE)
ITEM_HEIGHT = 50 + INTER_ALIGNMENT


#CONSTANTES FOR WIND DIRECTION :
VENT_NORD = "\u2B07"
VENT_NORD_EST = "\u2199"
VENT_EST = "\u2B05"
VENT_SUD_EST = "\u2196"
VENT_SUD = "\u2B06"
VENT_SUD_OUEST = "\u2197"
VENT_OUEST = "\u27A1"
VENT_NORD_OUEST = "\u2198"


#===================================================#
#           GLOBAL VARIABLES DECLARATIONS           #
#===================================================#

#Global variables for weather image generation :
bigFont = ImageFont.truetype(FONT_PATH, BIG_FONT_SIZE)
mediumFont = ImageFont.truetype(FONT_PATH, MEDIUM_FONT_SIZE)
smallFont = ImageFont.truetype(FONT_PATH, SMALL_FONT_SIZE)


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

dictWeatherType = {
    "type_1" : ("Poudrerie",                    "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/snowFlackIcon.png"),
    "type_2" : ("bruine",                       "./Data/Images/Backgrounds/drizzle.png",    f"{ICON_DIR_PATH}WeatherIcons/mediuùDrizzleIcon.png"),
    "type_3" : ("bruine lourde",                "./Data/Images/Backgrounds/drizzle.png",    f"{ICON_DIR_PATH}WeatherIcons/mediumDrizzleIcon.png"),
    "type_4" : ("bruine légère",                "./Data/Images/Backgrounds/drizzle.png",    f"{ICON_DIR_PATH}WeatherIcons/lightDrizzleIcon.png"),
    "type_5" : ("forte bruine",                 "./Data/Images/Backgrounds/drizzle.png",    f"{ICON_DIR_PATH}WeatherIcons/heavyDrizzleIcon.png"),
    "type_6" : ("légère bruine",                "./Data/Images/Backgrounds/drizzle.png",    f"{ICON_DIR_PATH}WeatherIcons/lightDrizzleIcon.png"),
    "type_7" : ("tempête de poussière",         "./Data/Images/Backgrounds/dustStorm.png",  f"{ICON_DIR_PATH}WeatherIcons/hurrycaneIcon.png"),
    "type_8" : ("Brouillard",                   "./Data/Images/Backgrounds/fog.png",        f"{ICON_DIR_PATH}WeatherIcons/fogIcon.png"),
    "type_9" : ("Bruine verglaçante",           "./Data/Images/Backgrounds/blackIce.png",   f"{ICON_DIR_PATH}WeatherIcons/fogIcon.png"),
    "type_10" : ("Forte bruine verglaçante",    "./Data/Images/Backgrounds/blackIce.png",   f"{ICON_DIR_PATH}WeatherIcons/snowFlackIcon.png"),
    "type_11" : ("Légère bruine verglaçante",   "./Data/Images/Backgrounds/blackIce.png",   f"{ICON_DIR_PATH}WeatherIcons/snowFlackIcon.png"),
    "type_12" : ("Brouillard verglaçant",       "./Data/Images/Backgrounds/fog.png",        f"{ICON_DIR_PATH}WeatherIcons/fogIcon.png"),
    "type_13" : ("Forte pluie verglaçante",     "./Data/Images/Backgrounds/blackIce.png",   f"{ICON_DIR_PATH}WeatherIcons/heavyRainIcon.png"),
    "type_14" : ("Légère pluie verglaçante",    "./Data/Images/Backgrounds/blackIce.png",   f"{ICON_DIR_PATH}WeatherIcons/lightRainIcon.png"),
    "type_15" : ("Tornade",                     "./Data/Images/Backgrounds/tornado.png",    f"{ICON_DIR_PATH}WeatherIcons/hurrycaneIcon.png"),
    "type_16" : ("Chute de grêle",              "./Data/Images/Backgrounds/storm.png",      f"{ICON_DIR_PATH}WeatherIcons/stormIcon.png"),
    "type_17" : ("Grezzil",                     "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/stormIcon.png"),
    "type_18" : ("foudre sans tonnerre",        "./Data/Images/Backgrounds/storm.png",      f"{ICON_DIR_PATH}WeatherIcons/stormIcon.png"),
    "type_19" : ("Brume",                       "./Data/Images/Backgrounds/fog.png",        f"{ICON_DIR_PATH}WeatherIcons/fogIcon.png"),
    "type_20" : ("Précipations à proximité",    "./Data/Images/Backgrounds/rain.png",       f"{ICON_DIR_PATH}WeatherIcons/mediumRainIcon.png"),
    "type_21" : ("Pluie",                       "./Data/Images/Backgrounds/rain.png",       f"{ICON_DIR_PATH}WeatherIcons/mediumRainIcon.png"),
    "type_22" : ("Forte pluie et neige",        "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/heavyRainIcon.png"),
    "type_23" : ("Légère pluie et neige",       "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/lightRainIcon.png"),
    "type_24" : ("Averse",                      "./Data/Images/Backgrounds/rain.png",       f"{ICON_DIR_PATH}WeatherIcons/heavyRainIcon.png"),
    "type_25" : ("Forte pluie",                 "./Data/Images/Backgrounds/rain.png",       f"{ICON_DIR_PATH}WeatherIcons/heavyRainIcon.png"),
    "type_26" : ("Légère pluie",                "./Data/Images/Backgrounds/rain.png",       f"{ICON_DIR_PATH}WeatherIcons/lightRainIcon.png"),
    "type_27" : ("Eclaircissement",             "./Data/Images/Backgrounds/thinning.png",   f"{ICON_DIR_PATH}WeatherIcons/sunAndCloudIcon.png"),
    "type_28" : ("Assombrissement",             "./Data/Images/Backgrounds/cloudy.png",     f"{ICON_DIR_PATH}WeatherIcons/cloudyIcon.png"),
    "type_29" : ("Ciel inchangé",               "./Data/Images/Backgrounds/thinning.png",   f"{ICON_DIR_PATH}WeatherIcons/sunAndCloudIcon.png"),
    "type_30" : ("Fumée",                       "./Data/Images/Backgrounds/smoke.png",      f"{ICON_DIR_PATH}WeatherIcons/fogIcon.png"),
    "type_31" : ("Neige",                       "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/mediumSnowFallIcon.png"),
    "type_32" : ("Pluie et neige mêlée",        "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/mediumSnowFallIcon.png"),
    "type_33" : ("Chutes de neige",             "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/heavySnowFallIcon.png"),
    "type_34" : ("Averses de neige",            "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/heavySnowFallIcon.png"),
    "type_35" : ("Quelques flocons",            "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/lightSnowFallIcon.png"),
    "type_36" : ("Grains",                      "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/lightSnowFallIcon.png"),
    "type_37" : ("Orage",                       "./Data/Images/Backgrounds/storm.png",      f"{ICON_DIR_PATH}WeatherIcons/stormIcon.png"),
    "type_38" : ("Orage sans précipitation",    "./Data/Images/Backgrounds/storm.png",      f"{ICON_DIR_PATH}WeatherIcons/stormIcon.png"),
    "type_39" : ("Voilé",                       "./Data/Images/Backgrounds/cloudyHaze.png", f"{ICON_DIR_PATH}WeatherIcons/hazeIcon.png"),
    "type_40" : ("Blizzard",                    "./Data/Images/Backgrounds/snow.png",       f"{ICON_DIR_PATH}WeatherIcons/hurrycaneIcon.png"),
    "type_41" : ("Couvert",                     "./Data/Images/Backgrounds/cloudy.png",     f"{ICON_DIR_PATH}WeatherIcons/cloudyIcon.png"),
    "type_42" : ("Partiellement nuageux",       "./Data/Images/Backgrounds/thinning.png",   f"{ICON_DIR_PATH}WeatherIcons/sunAndCloudIcon.png"),
    "type_43" : ("Ensoleillé",                  "./Data/Images/Backgrounds/sun.png",        f"{ICON_DIR_PATH}WeatherIcons/sunIcon.png"),
}

def getPathImageWeatherType(weatherCondition : str) -> str :
    """Get path to the image corresponding to weather conditions type specified in argument

    ### Return :
    path to the image as a string"""

    firstType = weatherCondition.split(",")[0]
    return dictWeatherType.get(firstType, ("Ciel inchangé", "./Data/Images/Backgrounds/thinning.png", f"{ICON_DIR_PATH}WeatherIcons/sunAndCloud.png"))[1]


def getDescriptionWeatherType(weatherCondition : str) -> str :
    """Get weather description of the weather condition type specified in argument
    ### Return :
    weather description as string
    """

    firstType = weatherCondition.split(",")[0]
    return dictWeatherType.get(firstType, ("Ciel inchangé", "./Data/Images/Backgrounds/thinning.png", f"{ICON_DIR_PATH}WeatherIcons/sunAndCloud.png"))[0]


def getIconPathWeatherType(weatherCondition : str) -> str :
    """Get weather icon path corresponding to weather condition type specified in argument
    ### Return :
    weather icon path as string"""

    firstType = weatherCondition.split(",")[0]
    return dictWeatherType.get(firstType, ("Ciel inchangé", "./Data/Images/Backgrounds/thinning.png", f"{ICON_DIR_PATH}WeatherIcons/sunAndCloud.png"))[2]


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
        if directionVent < 112:
            return (VENT_EST, "E")
        return (VENT_SUD_EST, "SE")
    if directionVent < 257:
        if directionVent < 212:
            return (VENT_SUD, "S")
        return (VENT_SUD_OUEST, "SW")
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


def createEmbedRainEmbed(requestResponse : dict):
    """"""
    dictRainType = {"rain" : "averse", "snow" : "neige", "freezing rain " : "pluie verglaçante", "ice" : "grêle"}
    embedToSend = discord.Embed(title="Pluie prévue aujourd'hui", description="Voici la pluie prévue aujourd'hui sur {}".format(requestResponse["address"]), color=0x77b5fe)
    fieldAdded = False
    for hour in requestResponse["days"][0]["hours"]:
        preciptype = hour["preciptype"]
        #If there is rain announced for the current hour, add it to the embed :
        if hour["precipprob"] > 0. and preciptype is not None:
            fieldAdded = True
            embedToSend.add_field(name="Pluie prévue à {} : ".format(hour["datetime"]), value="Probabilité de {} à {} %, attendu {} mm".format(dictRainType.get(preciptype[0], "pluie"), hour["precipprob"], hour["precip"]), inline=False)
    #If there is not rain announced for the day :
    if not fieldAdded:
        embedToSend.add_field(name="Pas de pluie prévue aujourd'hui !", value="\u2600\uFE0F", inline=False)
    embedToSend.set_footer(text="Données de l'API Visual Crossing")
    return embedToSend


class AlerteMeteo(WebhookEvent):
    """Classe permettant de récupérer les alertes météo générées par l'API et de les transmettre sous forme
  de Webhook aux serveurs Discord reliés"""
    def __init__(self, apiHandler : VisualCrossingHandler):
        WebhookEvent.__init__(
            self,
            "https://api.openweathermap.org/data/2.5/onecall?lat=43.604259&lon=1.44367&exclude=current,minutely,hourly,daily&appid={}&lang=fr"
            .format(os.environ['idOpenWeather']), apiHandler)

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
    """Classe permettant de générer un thread ayant pour objectif de récupérer la météo du jour via l'API de 	openweather et de d'envoyer un webHook sur les serveurs connectés"""
    def __init__(self, apiHandler : VisualCrossingHandler, dictUsersBot : dict):
        WebhookEvent.__init__(self, "", apiHandler)
        #Fields of the class :
        self.dictUsersBot = dictUsersBot
        self.alreadySend = False	#Booleen to indicate if daily message has already been sent
        self.listUserToSend = []	#Liste contenant les identifiants des utilisateurs à qui envoyer le bulletin quotidien

    def addUserToList(self, idUser : int) -> None :
        """Add the user whose id is specified to the list to receive daily weather newsletter
        #Parameter :
        * idUser : user's id"""
        self.listUserToSend.append(idUser)

    def delUserFromList(self, idUser : int) -> bool :
        """Remove the user whose id is passed as a parameter from the list to receive daily weather newsletter
        #Parameter :
        *idUser : id of the user
        #Return :
        return True if user successfully deleted from the list, False if id passed doesn't exist in the list"""
        try:
            self.listUserToSend.remove(idUser)
            return True
        except ValueError:
            return False

    @staticmethod
    def createDailyWeatherImage(requestResponse : str, path : str) -> None :
        """Create image for daily weather according to specified requestResponse passed into argument
        ## Param :
         * requestResponse : response to the request for daily weather return by Visual Crossing handler
         * path            : string that contains path where store generated image """

        dayInfo = requestResponse["days"][0]

        #Create background image according to weather condition for the day :
        weatherImage = SunImage(getPathImageWeatherType(dayInfo['conditions']))
        #Add mask to the image :
        weatherImage.addMask("BLACK", 180, (weatherImage.width // 2 + 40, weatherImage.height), (0, 0))
        #Add weather icon according announced daily weather :
        weatherImage.addIcon(getIconPathWeatherType(dayInfo['conditions']), MAIN_ICON_SIZE, (350, UP_ALIGNMENT))
        #Add icons to the daily weather image :
        weatherImage.addIcon(f"{ICON_DIR_PATH}water-drops.png", ICON_SIZE, (LEFT_ALIGNMENT, ITEMS_UP_ALIGNMENT))
        weatherImage.addIcon(f"{ICON_DIR_PATH}pluviometer.png", ICON_SIZE, (CENTRE_ALIGNMENT, ITEMS_UP_ALIGNMENT))
        weatherImage.addIcon(f"{ICON_DIR_PATH}wind.png", ICON_SIZE, (LEFT_ALIGNMENT, ITEM_HEIGHT + ITEMS_UP_ALIGNMENT))
        weatherImage.addIcon(f"{ICON_DIR_PATH}windDirection.png", ICON_SIZE, (CENTRE_ALIGNMENT, ITEM_HEIGHT + ITEMS_UP_ALIGNMENT), 360 - dayInfo['winddir'])
        weatherImage.addIcon(f"{ICON_DIR_PATH}pressure.png", ICON_SIZE, (LEFT_ALIGNMENT, 2 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT))
        weatherImage.addIcon(f"{ICON_DIR_PATH}humidity.png", ICON_SIZE, (LEFT_ALIGNMENT, 3 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT))
        weatherImage.addIcon(f"{ICON_DIR_PATH}rays.png", ICON_SIZE, (LEFT_ALIGNMENT, 4 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT))
        weatherImage.addIcon(f"{ICON_DIR_PATH}sunrise.png", ICON_SIZE, (LEFT_ALIGNMENT,  5 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT))
        weatherImage.addIcon(f"{ICON_DIR_PATH}sunset.png", ICON_SIZE, (CENTRE_ALIGNMENT, 5 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT))
        weatherImage.addIcon(f"{ICON_DIR_PATH}logoVC.jpeg", ICON_SIZE, (5, weatherImage.height - 45))
        #Write text on the image :
        weatherImage.drawText(f"{round(dayInfo['temp'], 1)}°C", bigFont, (LEFT_ALIGNMENT, UP_ALIGNMENT))
        weatherImage.drawText(f"{round(dayInfo['tempmin'], 1)}°C", mediumFont, (LEFT_ALIGNMENT, MIN_MAX_TEMP_ALIGNMENT), (0, 63, 255))
        weatherImage.drawText(f"{round(dayInfo['tempmax'], 1)}°C", mediumFont, (200, MIN_MAX_TEMP_ALIGNMENT), "ORANGE")
        weatherImage.drawText(f"{dayInfo['precipprob']}%", mediumFont, (TXT_VERTICAL_ALIGNMENT, ITEMS_UP_ALIGNMENT))
        precip = dayInfo["precip"]
        if precip > 0 :
            weatherImage.drawText(f"{precip}mm", mediumFont, (TXT_CENTRAL_VERTICAL_ALIGNMENT, ITEMS_UP_ALIGNMENT))
        weatherImage.drawText(f"{round(dayInfo['windspeed'], 2)}km/h", mediumFont, (TXT_VERTICAL_ALIGNMENT, ITEM_HEIGHT + ITEMS_UP_ALIGNMENT))
        weatherImage.drawText(f"{degToStrDirectVent(dayInfo['winddir'])[1]}", mediumFont, (TXT_CENTRAL_VERTICAL_ALIGNMENT, ITEM_HEIGHT + ITEMS_UP_ALIGNMENT))
        weatherImage.drawText(f"{dayInfo['pressure']}hPa", mediumFont, (TXT_VERTICAL_ALIGNMENT, 2 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT + TXT_HORIZONTAL_ALIGNMENT))
        weatherImage.drawText(f"{dayInfo['humidity']}%", mediumFont, (TXT_VERTICAL_ALIGNMENT, 3 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT + TXT_HORIZONTAL_ALIGNMENT))
        weatherImage.drawText(f"{dayInfo['uvindex']}", mediumFont, (TXT_VERTICAL_ALIGNMENT, 4 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT + TXT_HORIZONTAL_ALIGNMENT))
        weatherImage.drawText(f"{dayInfo['sunrise'][0 : 5]}", mediumFont, (TXT_VERTICAL_ALIGNMENT, 5 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT + TXT_HORIZONTAL_ALIGNMENT))
        weatherImage.drawText(f"{dayInfo['sunset'][0 : 5]}", mediumFont, (TXT_CENTRAL_VERTICAL_ALIGNMENT, 5 * ITEM_HEIGHT + ITEMS_UP_ALIGNMENT + TXT_HORIZONTAL_ALIGNMENT))
        weatherImage.drawText("Données de l'API VisualCrossing", smallFont, (60, weatherImage.height - 40))
        #Save the image:
        weatherImage.saveImage(f"{path}/{DAILY_IMAGE_NAME}")

    @staticmethod
    def createEmbedMessage(requestResponse : str) -> discord.Embed:
        """Creates an embed message from the requestResponse of API passed in parameter.
        # Parameter :
        * requestResponse : string corresponding to the response of the request to API
        # Return :
        Discord embed of the request response"""

        #Creation of the embed
        dailyMeteoToSend = discord.Embed(title="Météo du jour", description= "Voici la météo prévue aujourd'hui à {}".format(requestResponse["address"]), color=0x77b5fe)

        #Domaines de l'Embed
        dayInfo = requestResponse["days"][0]
        dailyMeteoToSend.add_field(name="Temps :", value="{}".format(dayInfo["description"]), inline=False)
        dailyMeteoToSend.add_field(name="Température max :", value="{}°C".format(round(dayInfo["tempmax"], 1)))
        dailyMeteoToSend.add_field(name="Température min :", value="{}°C".format(round(dayInfo["tempmin"], 1)))
        dailyMeteoToSend.add_field(name="Température moyenne :", value="{}°C".format(round(dayInfo["temp"], 1)))
        dailyMeteoToSend.add_field(name="Température ressentie :", value="{}°C".format(round(dayInfo["feelslike"], 1)))
        dailyMeteoToSend.add_field(name="Pression au niveau de la mer :", value="{}hPa".format(dayInfo["pressure"]), inline=False)
        dailyMeteoToSend.add_field(name="Humidité :", value="{}%".format(dayInfo["humidity"]), inline=False)
        directionVent = degToStrDirectVent(dayInfo["winddir"])
        dailyMeteoToSend.add_field(name="Direction vent :", value="{} **{}**".format(directionVent[0], directionVent[1]))
        dailyMeteoToSend.add_field(name="Vitesse vent :", value="{}km/h".format(round(dayInfo["windspeed"], 2)))
        vitesseRafale = dayInfo["windgust"]
        if vitesseRafale > 0.:
            dailyMeteoToSend.add_field(name="Rafale :", value="{}km/h".format(round(vitesseRafale, 2)), inline=True)
        dailyMeteoToSend.add_field(name="Risque de précipitation :", value="{}%".format(dayInfo["precipprob"]), inline=False)
        dailyMeteoToSend.add_field(name="Indice UV :", value="{}".format(dayInfo["uvindex"]), inline=False)
        dailyMeteoToSend.add_field(name="Levé du soleil:", value="{}:{}".format(int(datetime.fromtimestamp(dayInfo["sunriseEpoch"]).strftime("%H")) + requestResponse["tzoffset"], datetime.fromtimestamp(dayInfo["sunriseEpoch"]).strftime("%M")))
        dailyMeteoToSend.add_field(name="Couché du soleil:", value="{}:{}".format(int(datetime.fromtimestamp(dayInfo["sunsetEpoch"]).strftime("%H")) + requestResponse["tzoffset"], datetime.fromtimestamp(dayInfo["sunsetEpoch"]).strftime("%M")))
        dailyMeteoToSend.set_footer(text="Données de l'API VisualCrossing", icon_url="https://www.visualcrossing.com/images/vclogo.svg")
        return dailyMeteoToSend


    def run(self):
        #Création d'un dictionnaire dont les clés sont les ID des utilisateurs et les valeurs des drapeaux
        #indiquant si la météo du jour a déjà été envoyée à l'utilisateur correspondant :
        dictAlreadySendFlag = {}
        for userId in self.dictUsersBot :
            dictAlreadySendFlag[userId] = False
            #If user allowing mp, add him to list to send daily weather newsletter :
            if self.dictUsersBot[userId].mp :
                self.listUserToSend.append(userId)
        #Main loop of the thread :
        while True:
            time.sleep(60)
            #Getting of UTC time :
            currentTime = time.localtime()
            hour = currentTime[3]
            minute = currentTime[4]
            #If time of reset reached, update flags :
            if (hour == 0) and (minute >= 0 and minute <= 1):
                self.alreadySend = False
                for userId in dictAlreadySendFlag :
                    dictAlreadySendFlag[userId] = False
            else :
                #For each user in list of user to send daily weather newsletter :
                for userId in self.listUserToSend:
                    #Check if it is time to send newsletter (at 7:00 am local):
                    userOffSetFav = self.dictUsersBot[userId].offSetFav
                    if (hour + userOffSetFav == 16) and (minute >= 4 and minute <= 5) and not dictAlreadySendFlag[userId]:
                        jsonResponse = self.apiHandler.dailyMeteoRequest(self.dictUsersBot[userId].favMeteo)
                        #If request received a response from API:
                        if jsonResponse != {}:
                            dictAlreadySendFlag[userId] = True
                            #Creation of the embed message :
                            embedMessage = self.createEmbedMessage(jsonResponse)
                        else:
                            self.dictUsersBot[userId].userDiscord.send("Aïe, il y a eu un problème avec la requête à l'API \U0001f625")

                if (hour == 5) and (minute >= 0 and minute <= 1) and not self.alreadySend:
                    jsonResponse = self.apiHandler.dailyMeteoRequest("Toulouse")
                    #Si la requête n'a pas échoué :
                    if jsonResponse != {}:
                        self.alreadySend = True
                        #dailyMeteoToSend = self.createEmbedMessage(jsonResponse)
                        self.createDailyWeatherImage(jsonResponse, "./Data/Images")
                        #Envoie l'embed sur les différents serveurs reliés au bot :
                        for webhook in self.webhooksList:
                            time.sleep(1)
                            webhook.send("*Voici la météo prévue aujourd'hui à Toulouse*\n", file = discord.File(f"{DAILY_IMAGE_PATH}/{DAILY_IMAGE_NAME}"))


