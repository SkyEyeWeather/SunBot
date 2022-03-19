#Importation des différents modules
import os
import discord
import json
import numpy as np

from WebServer import keep_alive

import BotUser
import Meteo
import sunBotModule.commands as sbm

#=======================
#    GLOBAL VARIABLES
#=======================

PATH_SAVE_USER_REP = "./Data/Save/Users/"

listeGifMignons = [
    "https://i.pinimg.com/originals/2a/65/72/2a6572296e58045b3f89c73e06e4916f.gif",
    "https://pa1.narvii.com/6935/ed72ab48336b42b9fdfaa9f245637841cb2208ber1-504-282_hq.gif",
    "https://acegif.com/wp-content/gifs/cute-bunny-gif-51.gif",
    "https://i.pinimg.com/originals/de/b9/49/deb949a2ea8afe6f7f0358137aac721b.gif",
    "https://img.filmsactu.net/datas/seriestv/t/h/the-mandalorian/n/the-mandalorian-gif-5fad8376c586e.gif",
    "https://2.bp.blogspot.com/-bKltZSToaSk/WpfSKtfVdZI/AAAAAAAADmY/mYeUGkpOdf8HoEq0c7N9Z5ixU5OuFn9FACLcBGAs/s1600/hamtaro.gif",
    "https://64.media.tumblr.com/a1f42c7b213265bde529ca41bd6c7e63/tumblr_nh5g2v3KlU1u465olo1_400.gifv",
    "https://c.tenor.com/rWDSYK2dWoMAAAAM/red-panda.gif",
    "https://tel.img.pmdstatic.net/fit/http.3A.2F.2Fprd2-bone-image.2Es3-website-eu-west-1.2Eamazonaws.2Ecom.2FTEL.2Enews.2F2018.2F01.2F11.2F7b751402-2a98-47d6-a69f-0e3d733181ed.2Egif/495x277/quality/80/thumbnail.gif",
    "https://phoneky.co.uk/thumbs/screensavers/down/cartoon-anime/sweetcat_jo9eelal.gif",
    "https://thumbs.gfycat.com/UnacceptableLittleCapybara-size_restricted.gif"
]

listeGifKernelDead = [
    "https://c.tenor.com/Ojww2DB8_x0AAAAd/dead-teletubbies.gif",
    "https://c.tenor.com/CXZRwTD_4BsAAAAM/im-dead-lol.gif",
    "https://c.tenor.com/LPYL83NEVcAAAAAM/dead-dog.gif",
    "https://c.tenor.com/X13wwMFZN2YAAAAM/dies-cat.gif"
]

messageTeteDePomme = 0  #Nombre de messages "tête de pomme" consécutifs (on suppose que l'invocation n'est faite que sur un erveur à la fois)

#==================================
#     Evénements liés au bot
#==================================


@sbm.sunBot.event
async def on_ready():
    #Création du dictionnaire des membres :
    print("Initialisation du bot...")
    print("Chargement des données des utilisateurs...")
    userLoadIsOK = True
    #Pour chaque utilisateur présent sur un des serveurs du bot :
    for member in sbm.sunBot.get_all_members():
        userFilePath = "{}/{}.txt".format(PATH_SAVE_USER_REP, member.id)
        #Teste si l'utilisateur est dans la base de données du bot:
        if os.path.isfile(userFilePath):
            #Si l'utilisateur existe, chargement de ses données à partir du fichier correspondant:
            with open("{}/{}.txt".format(PATH_SAVE_USER_REP, member.id),'r') as userFile:
                print("Chargement des données de l'utilisateur n°{}".format(member.id))
                try:
                    dataUser = json.load(userFile)
                    sbm.dictUsersBot[member.id] = BotUser.BotUser( dataUser["emojis"], dataUser["favMeteo"])
                    print(sbm.dictUsersBot[member.id])
                except json.decoder.JSONDecodeError:
                    print("Une erreur est survenue lors du chargement de l'utilisateur n°{} : le fichier est soit vide soit corrompu. Suppression du fichier".format(member.id))
                    os.system("rm {}{}.txt".format(PATH_SAVE_USER_REP,member.id))
                    userLoadIsOK = False
        #Sinon création d'un nouvel utilisateur :
        else:
            print("Création de l'utilisateur n°{}".format(member.id))
            sbm.dictUsersBot[member.id] = BotUser.BotUser()
    print("Chargement des données utilisateur : {}".format(userLoadIsOK))

    #Création du thread écoutant les alertes météos:
    print("Génération des webhooks...")
    webhookServeurTest1 = discord.Webhook.from_url(
        'https://discord.com/api/webhooks/923863299270013018/6jfjT1QtrZ8UCXM1aEUhUD7z5G5Or9S3loFvlQs34Age8hX7VPfrD4UUQvGXCzmDN0Oo',
        adapter=discord.RequestsWebhookAdapter())
    #webhookServeurTest2 = discord.Webhook.from_url('https://discord.com/api/webhooks/927208384946638898/zRq8mLQT2aEV4GqufzrEYOFAdOdaTVxNypOuXDc4mgpnZCBNaQXpZbl1zqmwXS8pp4hC', adapter=discord.RequestsWebhookAdapter())
    webhookServeurCUPGE = discord.Webhook.from_url(
        'https://discord.com/api/webhooks/921547043196002324/NJohjH9dduqidXHvV4Ei9V4KuIUvOiAPnbMEVPf_x06CUStZou0TlTapQi3B1i_zuLfp',
        adapter=discord.RequestsWebhookAdapter())
    alerteMeteo = Meteo.AlerteMeteo()
    alerteMeteo.addWebhook(webhookServeurTest1)
    alerteMeteo.start()
    print("Webhook alerte météo prêt")
    #Création du thread écoutant les informations météo quotidiennes :
    dailyMeteo = Meteo.DailyMeteo()
    dailyMeteo.addWebhook(webhookServeurCUPGE)
    dailyMeteo.addWebhook(webhookServeurTest1)
    #dailyMeteo.addWebhook(webhookServeurTest2)
    dailyMeteo.start()
    print("Webhook daily météo prêt")
    print("SunBot est chaud patate!")


@sbm.sunBot.event
async def on_member_join(member):
    print("{} a rejoint le serveur {} !".format(member.name, member.guild.name))
    userBot = BotUser.BotUser(member)
    sbm.dictUsersBot[member.id] = userBot
    if member.guild.id == 816226592556580865:
        channel = sbm.sunBot.get_channel(816226592556580868)
        await channel.send("Bienvenue sur le serveur {}! Je suis SunBot, bot spécialiste de la météo (ou pas)! Tu peux utiliser +help dans le channel des bots pour en savoir plus sur moi!".format(member.mention))


@sbm.sunBot.event
async def on_message(message):

    global messageTeteDePomme

    await sbm.sunBot.process_commands(message)
    if not message.author.bot:
        await sbm.dictUsersBot[message.author.id].addReaction(message)
    messageMin = message.content.lower()
    #Si le message correspond à l'invocation tête de pomme
    if messageMin in ["tête de pomme", "tete de pomme", "#tetedepomme"]:
        messageTeteDePomme += 1
        #Si le message a été répété 3 fois de suite, on invoque le gif :
        if messageTeteDePomme == 3:
            """
            messageTeteDePomme = 0
            print("Invocation tête de pomme !")
            embedToSend = discord.Embed(
                title="Et tu savais qu'à Jean Jaurès...", color=0xff0000)
            gifTeteDePomme = discord.File("./Data/TeteDePomme.gif",
                                          "TeteDePomme.gif")
            embedToSend.set_image(url="attachment://TeteDePomme.gif")
            await message.channel.send(embed=embedToSend, file=gifTeteDePomme)"""
            await message.channel.send("Fonctionnalité suspendue")
    #Autres type de message :
    else:
        messageTeteDePomme = 0
        if "me foutre au sol" in messageMin and np.random.uniform() > 0.5:
            await message.reply("Tu sais, il y a des gens qui disaient ça avant toi et qui ont fini ingénieurs aéronautique chez Boeing ! Donc ne te décourage pas \U0001f31e !"
            )
        if messageMin == "sinus":
            await message.channel.send("Tangente")
        if messageMin in ["patrick", "patou", "patoche", "pata", "patrikou"] and np.random.uniform() > 0.25:
            indiceGifToSend = int(np.random.uniform(0, len(listeGifMignons)))
            await message.reply(listeGifMignons[indiceGifToSend])
            await message.channel.send("Mignon !!")
        if "kernel is dead" in messageMin:
            indiceGifToSend = int(np.random.uniform(0, len(listeGifKernelDead)))
            await message.reply(listeGifKernelDead[indiceGifToSend])


@sbm.sunBot.event
async def on_disconnect():
    print("Déconnexion du bot...")
    #Si le répertoire de sauvegarde des données utilisateurs n'existe pas, le créer:
    if not os.path.exists(PATH_SAVE_USER_REP):
        print("on_disconnect : Répertoire de sauvegarde des utilisateurs inexistant.")
        os.makedirs(PATH_SAVE_USER_REP, exist_ok=True)
    #Enregistrement des données des utilisateurs (un fichier par utilisateur) :
    for userId in sbm.dictUsersBot.keys():
        print("Sauvegarde des données de l'utilisateur n°{}".format(userId))
        with open("{}/{}.txt".format(PATH_SAVE_USER_REP, userId), 'w') as userFile:
            dataJson = json.dumps(sbm.dictUsersBot[userId].__dict__)
            userFile.write(dataJson)
    print("Déconnexion terminée")


#####################################################################################################
#ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES - ALWAYS RUN PART - NE RIEN METTRE SOUS CES LIGNES
#####################################################################################################

keep_alive()
sbm.sunBot.run(os.environ["token"])
