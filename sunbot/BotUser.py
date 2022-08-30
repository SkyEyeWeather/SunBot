
#=================================
# Modules utilisés par la classe
#=================================

import discord
import os
import json
from numpy.random import uniform


#=================================
#	Déclaration de la classe
#==================================

class BotUser:
    """Classe représentant un utilisateur du SunBot. Est considéré comme utilisateur du bot tout membre étant présent sur un des serveurs sur lequel se trouve SunBot. Cette classe permet ainsi de gérer les différents paramètres utilisateurs (émoji, favoris ...) et la sauvegarde de ceux-ci."""

    #Variables de classe:
    COMMON_MESSAGE = 0  #Message commun


    #Constructeur de la classe
    def __init__(self, userDiscord : discord.Member, emojis=None, favMeteo="Toulouse", offSet : int = 2,  mp=False) -> None:
        """Constructeur de la classe BotUser. Permet de générer un nouvel utilisateur du SunBot.
        Paramètres :
                        - userDiscord : Référence vers l'utilisateur Discord
                        - emoji : [Optionnel] reaction par défaut que le bot va ajouter aux messages envoyés par l'utilisateur
        - favMeteo : localisation favorite de l'utilisateur pour la météo courante
        - offSetFav : décalage horaire de la localisation favorite par rapport à UTC
        - mp : autorise le bot à envoyer des mp à l'utilisateur"""
        self.userDiscord = userDiscord
        if emojis is None:
            emojis = {}
        self.emojis = emojis
        self.favMeteo = favMeteo
        self.offSetFav = offSet
        self.mp = mp


    def __str__(self):
        return f"emoji = {self.emojis}, favori météo = {self.favMeteo}, mp = {self.mp}"


    def saveUser(self, pathSaveRep : str) -> None :
        """Sauvegarde les paramètres de l'utilisateur dans un fichier dont le nom
        correspond à l'identifiant de l'utilisateur dans le répertoire de sauvegarde
        dont le chemin est passé en paramètre. Si ce dernier n'existe pas, le
        répertoire est créé.
        Paramètre :	- pathSaveRep : répertoire de sauvegarde où stocker le fichier
                        contenant les paramètres de l'utilisateur"""
        #Si le répertoire de sauvegarde n'existe pas, le créer :
        if not os.path.exists(pathSaveRep):
            print("Création du répertoire : {}".format(pathSaveRep))
            os.makedirs(pathSaveRep, exist_ok=True)
        print(f"Sauvegarde des données de l'utilisateur n°{self.userDiscord.id}")
        #Sauvegarde des données de l'utilisateur dans le fichier :
        with open(f"{pathSaveRep}/{self.userDiscord.id}.txt", 'w') as saveFile:
            #Création variable temporaire pour rendre l'attribut userDiscord transcient :
            tempUser = self.userDiscord
            self.userDiscord = None
            dataJson = json.dumps(self.__dict__, ensure_ascii=False, indent = 2)
            self.userDiscord = tempUser
            saveFile.write(dataJson)


    def setEmoji(self, emoji: str, freq: float, typeMessage: int = COMMON_MESSAGE) -> None:
        """Modifie l'emoji spécifié pour le type de message passé en paramètre de la méthode.
    Paramètres :  - emoji : chaine de caractère représentant l'unicode de l'emoji
                  - freq : probabilité qu'une réaction correspondant à l'émoji soit ajouté au message du type typeMessage. Nombre compris entre 0 et 1.
                  - typeMessage : type de messages auquel l'emoji devra être ajouté"""
        if freq < 0 or freq > 1:
            raise ValueError("BotUser.setEmoji :  Freq must be between 0 and 1 !")
        self.emojis[str(typeMessage)] = (emoji, freq)


    async def addReaction(self, msg: discord.Message, typeMessage=0) -> None:
        """Ajoute une réaction au message msg envoyé par l'utilisateur.
    Paramètres: - msg: message envoyé par l'utilisateur
                - typeMessage: type du message envoyé"""
        emoji, prob = self.emojis.get(str(typeMessage), ("", 0))
        if emoji != "" and uniform() <= prob:
            try:
                await msg.add_reaction(emoji)
            except discord.errors.NotFound:
                print("Le message a disparu !")
