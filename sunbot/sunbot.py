# ==================================
#       CONSTANTS DECLARATION
# ==================================

# Path constants:
ICON_DIR_PATH = "./Data/Images/Icons/"
DAILY_IMAGE_PATH = "./Data/Images/"
CURRENT_WEATHER_IMAGE_PATH = "./Data/Images/"
FONT_PATH = "./Data/Font/Ubuntu-R.ttf"


# File name constants:
DAILY_IMAGE_NAME = "dailyImage.png"
CURRENT_WEATHER_IMAGE_NAME = "currentWeather.png"


# Constants for image generation:
BIG_FONT_SIZE = 80
MEDIUM_FONT_SIZE = 40
SMALL_FONT_SIZE = 20
ICON_SIZE = (50, 50)

LEFT_ALIGNMENT = 20
CENTRE_ALIGNMENT = 320
UP_ALIGNMENT = 10
INTER_ALIGNMENT = 30
MIN_MAX_TEMP_ALIGNMENT = UP_ALIGNMENT + BIG_FONT_SIZE + 10
ITEMS_UP_ALIGNMENT = MIN_MAX_TEMP_ALIGNMENT + MEDIUM_FONT_SIZE + INTER_ALIGNMENT
TXT_VERTICAL_ALIGNMENT = LEFT_ALIGNMENT + ICON_SIZE[0] + INTER_ALIGNMENT
TXT_CENTRAL_VERTICAL_ALIGNMENT = CENTRE_ALIGNMENT + ICON_SIZE[0] + INTER_ALIGNMENT
TXT_HORIZONTAL_ALIGNMENT = 10

MAIN_ICON_SIZE = (
    MIN_MAX_TEMP_ALIGNMENT + MEDIUM_FONT_SIZE,
    MIN_MAX_TEMP_ALIGNMENT + MEDIUM_FONT_SIZE,
)
ITEM_HEIGHT = ICON_SIZE[1] + INTER_ALIGNMENT


DAILY_WEATHER_RESET_HOUR = 0
DAILY_WEATHER_SEND_HOUR = 7

PERIODS = {"aujourd'hui": "today", "demain": "tomorrow"}

# ===================================
#       DECORATORS DECLARATION
# ===================================


def betaFunction(function):
    """Decorator used to indicate that a function can only be call by bot's maintainers"""

    async def fonctionModifie(*args, **opt):
        if args[0].author.id != 691614947280551936:
            await args[0].channel.send(
                "J'aimerais pouvoir t'aider, mais mon créateur (ce ravagé) me l'a interdit car cette fonctionnalité est actuellement en travaux !"
            )
        else:
            await function(*args, **opt)

    return fonctionModifie


def adminFunction(function):
    """Decorator used to indicate that a function can only be call by an
    adminstrator of the bot. Other users will receive an error message."""

    async def fonctionModifie(*args, **kwargs):
        if args[0].author.id not in (691614947280551936, 690593377250443374):
            await args[0].channel.send(
                "Il faut être ravagé pour utiliser cette commande !"
            )
        else:
            await function(*args, **kwargs)

    return fonctionModifie
