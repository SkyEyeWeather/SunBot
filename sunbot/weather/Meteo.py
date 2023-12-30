import os
import time
from datetime import datetime

import discord
import requests
from PIL import ImageFont

from sunbot import sunbot
from sunbot.SunImager import SunImage

# ===========================================================#
#           CONSTANTES VARIABLES DECLARATIONS               #
# ===========================================================#

# CONSTANTES FOR WIND DIRECTION :
VENT_NORD = "\u2B07"
VENT_NORD_EST = "\u2199"
VENT_EST = "\u2B05"
VENT_SUD_EST = "\u2196"
VENT_SUD = "\u2B06"
VENT_SUD_OUEST = "\u2197"
VENT_OUEST = "\u27A1"
VENT_NORD_OUEST = "\u2198"


# ===================================================#
#           GLOBAL VARIABLES DECLARATIONS           #
# ===================================================#

# Global variables for weather image generation :
bigFont = ImageFont.truetype(sunbot.FONT_PATH, sunbot.BIG_FONT_SIZE)
mediumFont = ImageFont.truetype(sunbot.FONT_PATH, sunbot.MEDIUM_FONT_SIZE)
smallFont = ImageFont.truetype(sunbot.FONT_PATH, sunbot.SMALL_FONT_SIZE)


dictWeatherType = {
    "type_1": (
        "Poudrerie",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/snowFlackIcon.png",
    ),
    "type_2": (
        "bruine",
        "./Data/Images/Backgrounds/drizzle.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/mediuùDrizzleIcon.png",
    ),
    "type_3": (
        "bruine lourde",
        "./Data/Images/Backgrounds/drizzle.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/mediumDrizzleIcon.png",
    ),
    "type_4": (
        "bruine légère",
        "./Data/Images/Backgrounds/drizzle.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/lightDrizzleIcon.png",
    ),
    "type_5": (
        "forte bruine",
        "./Data/Images/Backgrounds/drizzle.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/heavyDrizzleIcon.png",
    ),
    "type_6": (
        "légère bruine",
        "./Data/Images/Backgrounds/drizzle.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/lightDrizzleIcon.png",
    ),
    "type_7": (
        "tempête de poussière",
        "./Data/Images/Backgrounds/dustStorm.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/hurrycaneIcon.png",
    ),
    "type_8": (
        "Brouillard",
        "./Data/Images/Backgrounds/fog.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/fogIcon.png",
    ),
    "type_9": (
        "Bruine verglaçante",
        "./Data/Images/Backgrounds/blackIce.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/fogIcon.png",
    ),
    "type_10": (
        "Forte bruine verglaçante",
        "./Data/Images/Backgrounds/blackIce.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/snowFlackIcon.png",
    ),
    "type_11": (
        "Légère bruine verglaçante",
        "./Data/Images/Backgrounds/blackIce.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/snowFlackIcon.png",
    ),
    "type_12": (
        "Brouillard verglaçant",
        "./Data/Images/Backgrounds/fog.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/fogIcon.png",
    ),
    "type_13": (
        "Forte pluie verglaçante",
        "./Data/Images/Backgrounds/blackIce.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/heavyRainIcon.png",
    ),
    "type_14": (
        "Légère pluie verglaçante",
        "./Data/Images/Backgrounds/blackIce.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/lightRainIcon.png",
    ),
    "type_15": (
        "Tornade",
        "./Data/Images/Backgrounds/tornado.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/hurrycaneIcon.png",
    ),
    "type_16": (
        "Chute de grêle",
        "./Data/Images/Backgrounds/storm.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/stormIcon.png",
    ),
    "type_17": (
        "Grezzil",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/stormIcon.png",
    ),
    "type_18": (
        "foudre sans tonnerre",
        "./Data/Images/Backgrounds/storm.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/stormIcon.png",
    ),
    "type_19": (
        "Brume",
        "./Data/Images/Backgrounds/fog.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/fogIcon.png",
    ),
    "type_20": (
        "Précipations à proximité",
        "./Data/Images/Backgrounds/rain.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/mediumRainIcon.png",
    ),
    "type_21": (
        "Pluie",
        "./Data/Images/Backgrounds/rain.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/mediumRainIcon.png",
    ),
    "type_22": (
        "Forte pluie et neige",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/heavyRainIcon.png",
    ),
    "type_23": (
        "Légère pluie et neige",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/lightRainIcon.png",
    ),
    "type_24": (
        "Averse",
        "./Data/Images/Backgrounds/rain.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/heavyRainIcon.png",
    ),
    "type_25": (
        "Forte pluie",
        "./Data/Images/Backgrounds/rain.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/heavyRainIcon.png",
    ),
    "type_26": (
        "Légère pluie",
        "./Data/Images/Backgrounds/rain.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/lightRainIcon.png",
    ),
    "type_27": (
        "Eclaircissement",
        "./Data/Images/Backgrounds/thinning.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/sunAndCloudIcon.png",
    ),
    "type_28": (
        "Assombrissement",
        "./Data/Images/Backgrounds/cloudy.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/cloudyIcon.png",
    ),
    "type_29": (
        "Ciel inchangé",
        "./Data/Images/Backgrounds/thinning.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/sunAndCloudIcon.png",
    ),
    "type_30": (
        "Fumée",
        "./Data/Images/Backgrounds/smoke.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/fogIcon.png",
    ),
    "type_31": (
        "Neige",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/mediumSnowFallIcon.png",
    ),
    "type_32": (
        "Pluie et neige mêlée",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/mediumSnowFallIcon.png",
    ),
    "type_33": (
        "Chutes de neige",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/heavySnowFallIcon.png",
    ),
    "type_34": (
        "Averses de neige",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/heavySnowFallIcon.png",
    ),
    "type_35": (
        "Quelques flocons",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/lightSnowFallIcon.png",
    ),
    "type_36": (
        "Grains",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/lightSnowFallIcon.png",
    ),
    "type_37": (
        "Orage",
        "./Data/Images/Backgrounds/storm.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/stormIcon.png",
    ),
    "type_38": (
        "Orage sans précipitation",
        "./Data/Images/Backgrounds/storm.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/stormIcon.png",
    ),
    "type_39": (
        "Voilé",
        "./Data/Images/Backgrounds/cloudyHaze.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/hazeIcon.png",
    ),
    "type_40": (
        "Blizzard",
        "./Data/Images/Backgrounds/snow.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/hurrycaneIcon.png",
    ),
    "type_41": (
        "Couvert",
        "./Data/Images/Backgrounds/cloudy.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/cloudyIcon.png",
    ),
    "type_42": (
        "Partiellement nuageux",
        "./Data/Images/Backgrounds/thinning.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/sunAndCloudIcon.png",
    ),
    "type_43": (
        "Ensoleillé",
        "./Data/Images/Backgrounds/sun.png",
        f"{sunbot.ICON_DIR_PATH}WeatherIcons/sunIcon.png",
    ),
}


def getPathImageWeatherType(weatherCondition: str) -> str:
    """Returns the path to the image corresponding to the weather conditions type
    specified in arguments
    ## Parameter:
    * `weatherCondition`: weather condition type, as a string
    ## Return value:
    The path to the image, as a string"""
    firstType = weatherCondition.split(",")[0]
    return dictWeatherType.get(
        firstType,
        (
            "Ciel inchangé",
            "./Data/Images/Backgrounds/thinning.png",
            f"{sunbot.ICON_DIR_PATH}WeatherIcons/sunAndCloudIcon.png",
        ),
    )[1]


def getDescriptionWeatherType(weatherCondition: str) -> str:
    """Returns the weather description for the weather condition type specified
    in arguments
    ## Parameter:
    * `weatherCondition`: weather condition type, as a string
    ## Return value:
    The weather description, as a string"""
    firstType = weatherCondition.split(",")[0]
    return dictWeatherType.get(
        firstType,
        (
            "Ciel inchangé",
            "./Data/Images/Backgrounds/thinning.png",
            f"{sunbot.ICON_DIR_PATH}WeatherIcons/sunAndCloud.png",
        ),
    )[0]


def getIconPathWeatherType(weatherCondition: str) -> str:
    """Returns the weather icon path corresponding to the weather condition type
    specified in arguments
    ## Parameter:
    * `weatherCondition`: weather condition type, as a string
    ## Return value:
    The weather icon path, as a string"""
    firstType = weatherCondition.split(",")[0]
    return dictWeatherType.get(
        firstType,
        (
            "Ciel inchangé",
            "./Data/Images/Backgrounds/thinning.png",
            f"{sunbot.ICON_DIR_PATH}WeatherIcons/sunAndCloud.png",
        ),
    )[2]


def degToStrDirectVent(directionVent: int) -> tuple:
    """Convertie l'angle passé en paramètre en direction cardinal afin de rendre l'affichage
    de cette information plus conviviale
    Paramètre : - directionVent : direction du vent (en degré) à convertir
    Retour: un tuple contenant un émoji flèche donnant la direction du vent, puis une chaîne donnant
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


def generateWeatherImage(weatherConditionCode: str) -> SunImage:
    """Generates a basic image with adapted background and weather icon according
    to the specified weather condition type
    ## Parameter:
    * `weatherConditionCode` : weather conditon type, as a string
    ## Return value:
    Returns basic image with adapted background. This image can be used to add
    elements on top of it"""
    # Create background image according to the current weather conditions:
    weatherImage = SunImage(getPathImageWeatherType(weatherConditionCode))
    # Add mask to the image:
    weatherImage.add_mask(
        "BLACK", 180, (weatherImage.width // 2 + 40, weatherImage.height), (0, 0)
    )
    # Add the weather icon according to the current weather conditions:
    weatherImage.add_icon(
        getIconPathWeatherType(weatherConditionCode),
        sunbot.MAIN_ICON_SIZE,
        (350, sunbot.UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}logoVC.jpeg",
        sunbot.ICON_SIZE,
        (5, weatherImage.height - 45),
    )
    weatherImage.draw_txt(
        "Données de l'API VisualCrossing", smallFont, (60, weatherImage.height - 40)
    )
    return weatherImage


def addPrecipData(request_response: dict, weather_image: SunImage) -> SunImage:
    """Adds precipitation data contained in JSON request response to the
    specified `weather_image`
    ## Parameters:
    * `request_response`: JSON response to the request, as a dict
    * `weather_image`: image where to add precipitations data
    ## Return value:
    Weather image with added precipitations data, for chained calls"""
    # If excepted precipitation type is rain, freezing or ice:
    if request_response["preciptype"] in ["rain", "freezing", "ice"]:
        weather_image.add_icon(
            f"{sunbot.ICON_DIR_PATH}water-drop.png",
            sunbot.ICON_SIZE,
            (sunbot.LEFT_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
        )
        weather_image.draw_txt(
            f"{request_response['precipprob']}%",
            mediumFont,
            (sunbot.TXT_VERTICAL_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
        )
        weather_image.add_icon(
            f"{sunbot.ICON_DIR_PATH}pluviometer.png",
            sunbot.ICON_SIZE,
            (sunbot.CENTRE_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
        )
        precip = request_response["precip"]
        if precip > 0.0:
            weather_image.draw_txt(
                f"{precip}mm",
                mediumFont,
                (sunbot.TXT_CENTRAL_VERTICAL_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
            )
    # If excepted precipitation type is snow:
    elif request_response["preciptype"] == "snow":
        weather_image.add_icon(
            f"{sunbot.ICON_DIR_PATH}snowflake.png",
            sunbot.ICON_SIZE,
            (sunbot.LEFT_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
        )
        weather_image.draw_txt(
            f"{request_response['precipprob']}%",
            mediumFont,
            (sunbot.TXT_VERTICAL_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
        )
        weather_image.add_icon(
            f"{sunbot.ICON_DIR_PATH}snow-depth.png",
            sunbot.ICON_SIZE,
            (sunbot.CENTRE_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
        )
        weather_image.draw_txt(
            f"{request_response['snowdepth']}+{request_response['snow']}",
            mediumFont,
            (sunbot.TXT_CENTRAL_VERTICAL_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
        )
    return weather_image


def addWindData(request_response: dict, weather_image: SunImage) -> SunImage:
    """Add wind information (speed, gust and direction) contained in JSON `request_response`
    to the specified `weather_image`
    ## Parameters:
    * `request_response`: JSON response to the weather request, as a dict
    * `weather_image`: image where to add wind data
    ## Return value;
    Weather image with wind data added, for chained calls"""
    # if wind speed data is specified:
    if request_response["windspeed"] is not None:
        weather_image.add_icon(
            f"{sunbot.ICON_DIR_PATH}wind.png",
            sunbot.ICON_SIZE,
            (sunbot.LEFT_ALIGNMENT, sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
        )
        weather_image.draw_txt(
            f"{request_response['windspeed']}km/h",
            mediumFont,
            (
                sunbot.TXT_VERTICAL_ALIGNMENT,
                sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
            ),
        )
        weather_image.add_icon(
            f"{sunbot.ICON_DIR_PATH}windDirection.png",
            sunbot.ICON_SIZE,
            (sunbot.LEFT_ALIGNMENT, 2 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
            360 - request_response["winddir"],
        )
        weather_image.draw_txt(
            f"{degToStrDirectVent(request_response['winddir'])[1]}",
            mediumFont,
            (
                sunbot.TXT_VERTICAL_ALIGNMENT,
                2 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
            ),
        )
    # If a wind gust data is specified:
    if request_response["windgust"] is not None:
        weather_image.add_icon(
            f"{sunbot.ICON_DIR_PATH}wind.png",
            sunbot.ICON_SIZE,
            (sunbot.CENTRE_ALIGNMENT, sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
        )
        weather_image.draw_txt(
            f"{request_response['windgust']}",
            mediumFont,
            (
                sunbot.TXT_CENTRAL_VERTICAL_ALIGNMENT,
                sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
            ),
        )
    return weather_image


def addHumidityData(request_response: dict, weather_image: SunImage) -> None:
    """Adds humidity data retrieved from `request_response` to the specified weather
    image
    ## Parameter:
    * `request_response`: JSON response from the weather API, as a dict
    * `weather_image`: image where add humidity data
    ## Return value:
    Weather image with humidity data added, for chained calls"""
    weather_image.add_icon(
        f"{sunbot.ICON_DIR_PATH}humidity.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, 5 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    weather_image.draw_txt(
        f"{request_response['humidity']}%",
        mediumFont,
        (
            sunbot.TXT_VERTICAL_ALIGNMENT,
            5 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
        ),
    )


def createCurrentWeatherImage(currentWeather: dict, path: str) -> None:
    """Creates an image for the API response specified in arguments
    ## Parameters :
    * `currentWeather` : response returned by the weather API, as a dictionnary
    ## Return value :
    An image that represents response from weather API"""
    # Create a basic image according to the current weather conditions:
    currentWeatherImage = generateWeatherImage(currentWeather["conditions"])
    # Add temperature data to the image:
    currentWeatherImage.draw_txt(
        f"{round(currentWeather['temp'], 1)}°C",
        bigFont,
        (sunbot.LEFT_ALIGNMENT, sunbot.UP_ALIGNMENT),
    )
    currentWeatherImage.draw_txt(
        f"ressenti {round(currentWeather['feelslike'], 1)}°C",
        mediumFont,
        (sunbot.LEFT_ALIGNMENT, sunbot.MIN_MAX_TEMP_ALIGNMENT),
    )
    # Add precipitation data to the image :
    addPrecipData(currentWeather, currentWeatherImage)
    # Add wind data to the image:
    addWindData(currentWeather, currentWeatherImage)
    # Add atmospheric data to the image:
    currentWeatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}pressure.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, 3 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    currentWeatherImage.draw_txt(
        f"{currentWeather['pressure']}hPa",
        mediumFont,
        (
            sunbot.TXT_VERTICAL_ALIGNMENT,
            3 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
        ),
    )
    currentWeatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}visibility.png",
        sunbot.ICON_SIZE,
        (sunbot.CENTRE_ALIGNMENT, 3 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    currentWeatherImage.draw_txt(
        f"{int(currentWeather['visibility'] * 1000)}m",
        mediumFont,
        (
            sunbot.TXT_CENTRAL_VERTICAL_ALIGNMENT,
            3 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
        ),
    )
    currentWeatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}rays.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, 4 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    currentWeatherImage.draw_txt(
        f"{currentWeather['uvindex']}",
        mediumFont,
        (
            sunbot.TXT_VERTICAL_ALIGNMENT,
            4 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
        ),
    )
    currentWeatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}cloudcover.png",
        sunbot.ICON_SIZE,
        (sunbot.CENTRE_ALIGNMENT, 4 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    currentWeatherImage.draw_txt(
        f"{currentWeather['cloudcover']}%",
        mediumFont,
        (
            sunbot.TXT_CENTRAL_VERTICAL_ALIGNMENT,
            4 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
        ),
    )
    # Add humidity data to the image:
    addHumidityData(currentWeather, currentWeatherImage)

    currentWeatherImage.save_img(
        f"{sunbot.CURRENT_WEATHER_IMAGE_PATH}{sunbot.CURRENT_WEATHER_IMAGE_NAME}"
    )


def create_rain_embed(data: dict, period: str = "aujourd'hui"):
    """create embed to send to discord from received data"""
    en2fr_dict = {
        "rain": "averse",
        "snow": "neige",
        "freezing rain ": "pluie verglaçante",
        "ice": "grêle",
    }
    embed2send = discord.Embed(
        title=f"Pluie prévue {period}",
        description=f"Voici la pluie prévue {period} sur {data['address']}",
        color=0x77B5FE,
    )
    sunny_day = True
    for i in range(24):
        hour = data[f"days/0/hours/{i}/datetime"]
        preciptype = data[f"days/0/hours/{i}/preciptype"]
        precipprob = data[f"days/0/hours/{i}/precipprob"]
        preciplvl = data[f"days/0/hours/{i}/precip"]
        # If rain is forecast for the current hour, add it to the embed message:
        if precipprob > 0.0 and preciptype is not None:
            sunny_day = False
            preciptype = en2fr_dict[preciptype[0]]
            embed2send.add_field(
                name=f"Pluie prévue à {hour} : ",
                value=f"Probabilité de {preciptype[0]} à {precipprob} %, attendu {preciplvl} mm",
                inline=False,
            )
    # If no rain is forecast for the day :
    if sunny_day:
        embed2send.add_field(
            name=f"Pas de pluie prévue {period} !", value="\u2600\uFE0F", inline=False
        )
    embed2send.set_footer(text="Données de l'API Visual Crossing")
    return embed2send


def create_daily_weather_img(day_info: dict, path: str) -> None:
    """Creates an image for the daily weather, according to the specified `requestResponse`
    passed in arguments.
    ## Parameters:
        * `request_response` : response to the request for daily weather returned by Visual
        Crossing handler
        * `path`            : string that contains path where save generated image"""
    # Create background image according to the weather condition for the day:
    weatherImage = SunImage(getPathImageWeatherType(day_info["conditions"]))
    # Add mask to the image:
    weatherImage.add_mask(
        "BLACK", 180, (weatherImage.width // 2 + 40, weatherImage.height), (0, 0)
    )
    # Add weather icon according to the forecast daily weather :
    weatherImage.add_icon(
        getIconPathWeatherType(day_info["conditions"]),
        sunbot.MAIN_ICON_SIZE,
        (350, sunbot.UP_ALIGNMENT),
    )
    # Add icons to the daily weather image:
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}water-drops.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}pluviometer.png",
        sunbot.ICON_SIZE,
        (sunbot.CENTRE_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}wind.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}windDirection.png",
        sunbot.ICON_SIZE,
        (sunbot.CENTRE_ALIGNMENT, sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
        360 - day_info["winddir"],
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}pressure.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, 2 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}humidity.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, 3 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}rays.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, 4 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}sunrise.png",
        sunbot.ICON_SIZE,
        (sunbot.LEFT_ALIGNMENT, 5 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}sunset.png",
        sunbot.ICON_SIZE,
        (sunbot.CENTRE_ALIGNMENT, 5 * sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.add_icon(
        f"{sunbot.ICON_DIR_PATH}logoVC.jpeg",
        sunbot.ICON_SIZE,
        (5, weatherImage.height - 45),
    )
    # Write text on the image:
    weatherImage.draw_txt(
        f"{round(day_info['temp'], 1)}°C",
        bigFont,
        (sunbot.LEFT_ALIGNMENT, sunbot.UP_ALIGNMENT),
    )
    weatherImage.draw_txt(
        f"{round(day_info['tempmin'], 1)}°C",
        mediumFont,
        (sunbot.LEFT_ALIGNMENT, sunbot.MIN_MAX_TEMP_ALIGNMENT),
        (0, 63, 255),
    )
    weatherImage.draw_txt(
        f"{round(day_info['tempmax'], 1)}°C",
        mediumFont,
        (200, sunbot.MIN_MAX_TEMP_ALIGNMENT),
        "ORANGE",
    )
    weatherImage.draw_txt(
        f"{day_info['precipprob']}%",
        mediumFont,
        (sunbot.TXT_VERTICAL_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
    )
    precip = day_info["precip"]
    if precip > 0:
        weatherImage.draw_txt(
            f"{precip}mm",
            mediumFont,
            (sunbot.TXT_CENTRAL_VERTICAL_ALIGNMENT, sunbot.ITEMS_UP_ALIGNMENT),
        )
    weatherImage.draw_txt(
        f"{round(day_info['windspeed'], 2)}km/h",
        mediumFont,
        (sunbot.TXT_VERTICAL_ALIGNMENT, sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT),
    )
    weatherImage.draw_txt(
        f"{degToStrDirectVent(day_info['winddir'])[1]}",
        mediumFont,
        (
            sunbot.TXT_CENTRAL_VERTICAL_ALIGNMENT,
            sunbot.ITEM_HEIGHT + sunbot.ITEMS_UP_ALIGNMENT,
        ),
    )
    weatherImage.draw_txt(
        f"{day_info['pressure']}hPa",
        mediumFont,
        (
            sunbot.TXT_VERTICAL_ALIGNMENT,
            2 * sunbot.ITEM_HEIGHT
            + sunbot.ITEMS_UP_ALIGNMENT
            + sunbot.TXT_HORIZONTAL_ALIGNMENT,
        ),
    )
    weatherImage.draw_txt(
        f"{day_info['humidity']}%",
        mediumFont,
        (
            sunbot.TXT_VERTICAL_ALIGNMENT,
            3 * sunbot.ITEM_HEIGHT
            + sunbot.ITEMS_UP_ALIGNMENT
            + sunbot.TXT_HORIZONTAL_ALIGNMENT,
        ),
    )
    weatherImage.draw_txt(
        f"{day_info['uvindex']}",
        mediumFont,
        (
            sunbot.TXT_VERTICAL_ALIGNMENT,
            4 * sunbot.ITEM_HEIGHT
            + sunbot.ITEMS_UP_ALIGNMENT
            + sunbot.TXT_HORIZONTAL_ALIGNMENT,
        ),
    )
    weatherImage.draw_txt(
        f"{day_info['sunrise'][0 : 5]}",
        mediumFont,
        (
            sunbot.TXT_VERTICAL_ALIGNMENT,
            5 * sunbot.ITEM_HEIGHT
            + sunbot.ITEMS_UP_ALIGNMENT
            + sunbot.TXT_HORIZONTAL_ALIGNMENT,
        ),
    )
    weatherImage.draw_txt(
        f"{day_info['sunset'][0 : 5]}",
        mediumFont,
        (
            sunbot.TXT_CENTRAL_VERTICAL_ALIGNMENT,
            5 * sunbot.ITEM_HEIGHT
            + sunbot.ITEMS_UP_ALIGNMENT
            + sunbot.TXT_HORIZONTAL_ALIGNMENT,
        ),
    )
    weatherImage.draw_txt(
        "Données de l'API VisualCrossing", smallFont, (60, weatherImage.height - 40)
    )
    # Save the image:
    weatherImage.save_img()(f"{path}/{sunbot.DAILY_IMAGE_NAME}")
