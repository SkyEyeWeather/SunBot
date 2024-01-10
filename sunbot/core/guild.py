"""Sunbot guild module"""

import json
import logging
from pathlib import Path

from sunbot.core.user import SunUser


class SunGuild:
    """This class defines a discord guild where the bot is present. A
    discord guild is a set of sun users (discord users) and has webhooks that
    allow the bot to send message without a context. It is identified by an ID
    that corresponds to its ID on Discord.
    """

    backup_dir = None

    def __init__(self, guild_id: int) -> None:
        """Constructor of this class
        ## Parameter :
        * `id`: discord ID for the guild to create. This ID is unique on Discord
        """
        self.__id = guild_id
        self.__guild_members = {}
        self.__guild_webhooks = {}

        # if backup directory for guilds does not already exist, create it:
        if not SunGuild.backup_dir:
            logging.warning(
                "guild backup directory path was not set. Use a default repository."
            )
            SunGuild.backup_dir = Path("./save/srv/")

        self.__backup_file = SunGuild.backup_dir / Path(f"{self.id}.json")
        # if backup guild file does not yet exist, create it:
        if not self.__backup_file.exists():
            logging.info("Backup file for guild %d doesn't exist. Creating it", self.id)
            self.__backup_file.parent.mkdir(parents=True, exist_ok=True)
            self.save_srv_data()
        else:
            with open(self.__backup_file, "r", encoding="UTF-8") as backup_file:
                try:
                    guild_data = json.load(backup_file)
                    self.__guild_webhooks = guild_data["guild_webhooks"]
                except json.decoder.JSONDecodeError:
                    logging.error(
                        "An error occured when retrieving data for guild n°%d",
                        self.id,
                    )

    @property
    def id(self) -> int:
        """Return discord guild ID"""
        return self.__id

    @id.setter
    def id(self, _value: int) -> None:
        raise AttributeError("Guild ID cannot be modified")

    def __eq__(self, __o: object) -> bool:
        """Test if the specified object `__o` is equal to this instance
        ## Parameter:
        * `__o`: object to compare to this instance
        ## Return value:
        `True` if the specified object to this instance, `False` otherwise
        """
        if not isinstance(__o, SunGuild):
            return False
        # Two guilds are equal if they have the same ID:
        return self.id == __o.id

    def __hash__(self) -> int:
        return self.id

    def add_member(self, member: SunUser) -> bool:
        """Adds an user to this guild.
        ## Parameter:
        * `member`: user to add to this guild
        ## Return value:
        returns `True` if the user was added to the guild, otherwise `False`. Falling to add
        an user can be explain by the fact that user was already added in this guild
        """
        # if user was already added into this guild, do nothing:
        if member.id in self.__guild_members:
            logging.error(
                "User n°%d was already added to the guild %d. Nothing to do.",
                member.id,
                self.id,
            )
            return False
        # add the user to the guild  member  dictionnary:
        self.__guild_members[member.id] = member
        logging.info("User n°%d has been added to the guild %d", member.id, self.id)
        return True

    def remove_member(self, member_id: int) -> bool:
        """Removes an user from this guild, if the user exists in this guild.
        ## Parameter:
        * `member_id`: identifiant of the user to be removed from this guild
        ## Return value:
        Return `True` if the corresponding user was successfully removed from this
        guild, otherwise `False`
        """
        # if ID specified in arguments does not correspond to any guild's user :
        if member_id not in self.__guild_members:
            logging.error(
                "Member n°%d does not belong to the guild %d", member_id, self.id
            )
            return False
        self.__guild_members.pop(member_id)
        logging.info(
            "Member %d has been removed from the guild %d",
            member_id,
            self.id,
        )
        return True

    def add_webhook(self, webhook_link: str, enabled: bool = True) -> bool:
        """Adds a webhook to this guild. If webhook was already added, do nothing.
        ## Parameters:
        * `webhookLink`: link corresponding to the webhook to add
        * `enabled`:boolean that indicates whether specified webhook is enabled
        ## Return value:
        Return `True` if the webhook was successfully added to this guild,
        otherwise `False`
        """
        if webhook_link in self.__guild_webhooks:
            logging.error(
                "Webhook pointed by %s was already added to the guild %d. Abort"
            )
            return False
        self.__guild_webhooks[webhook_link] = enabled
        logging.info(
            "Webhook %s was successfully added to the guild n°%d",
            webhook_link,
            self.id,
        )
        return True

    def remove_webhook(self, webhook_link: str) -> bool:
        """Removes a webhoook from this guild. If webhook does not exist,
        do nothing.
        ## Parameter:
        * `webhookLink`: link corresponding to the webhook to remove
        ## Return value:
        Return True if webhook was removed successfully, otherwise False
        """
        if webhook_link not in self.__guild_webhooks.keys():
            logging.error(
                "Webhook pointed by %s doesn't exist in the guild %d.Do nothing.",
                webhook_link,
                self.id,
            )
            return False
        self.__guild_webhooks.pop(webhook_link)
        logging.info(
            "Webhook %s was successfully removed from the guild %d",
            webhook_link,
            self.id,
        )
        return True

    def update_webhook(self, webhook_link: str, enabled: bool) -> bool:
        """Enables or disables webhook specified in arguments, if it exists in
        this guild.
        ## Parameters:
        * `webhooklink`: link corresponding to the webhook to update the status
        * `enabled`: flag that indicates the new state for specified webhook. `True`
        to enable, `False` to disable
        ## Return value:
        Return `True` if operation was a success, otherwise `False`
        """
        if webhook_link not in self.__guild_webhooks.keys():
            logging.error(
                "Webhook %s does not exist in the guild %d. Do nothing",
                webhook_link,
                self.id,
            )
            return False
        self.__guild_webhooks[webhook_link] = enabled
        logging.info("Webhook %s is now enabled in the guild %d", webhook_link, self.id)
        return True

    def save_srv_data(self):
        """Private method used to save guild's data into corresponding backup file"""
        with open(self.__backup_file, "w", encoding="UTF-8") as guild_file:
            backup_dict = {
                "guild_id": self.id,
                "guild_members": list(self.__guild_members.keys()),
                "guild_webhooks": self.__guild_webhooks,
            }

            json_data = json.dumps(backup_dict, ensure_ascii=False, indent=2)
            guild_file.write(json_data)
