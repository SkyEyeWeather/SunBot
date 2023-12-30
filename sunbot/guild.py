""" Sunbot guild module"""

import json
import logging
import os
from pathlib import Path

from sunbot.SunUser import SunUser


class SunGuild:
    """This class defines a discord guild where the bot is present. A
    discord guild is a set of sun users (discord users) and has webhooks that
    allow the bot to send message without a context. It is identified by an ID
    that corresponds to its ID on Discord.
    """

    srv_backup_path = None

    def __init__(self, guild_id: int) -> None:
        """Constructor of this class
        ## Parameter :
        * `id`: discord ID for the server to create. This ID is unique on Discord"""
        self.guild_id = guild_id
        self.__guild_members = {}
        self.__guild_webhooks = {}

        # if backup directory for servers does not already exist, create it:
        if not SunGuild.srv_backup_path:
            logging.warning(
                "Server backup directory path was not set. Use a default repository."
            )
            SunGuild.srv_backup_path = Path("./save/srv/")

        self.backup = SunGuild.srv_backup_path / Path(f"{self.guild_id}.json")
        # if backup guild file does not yet exist, create it:
        if not self.backup.exists():
            logging.info(
                "Backup file for guild %d doesn't exist. Creating it", self.guild_id
            )
            SunGuild.srv_backup_path.mkdir(parents=True, exist_ok=True, mode=777)
            self.save_srv_data()
        else:
            with open(self.backup, "r", encoding="UTF-8") as backup_file:
                try:
                    guild_data = json.load(backup_file)
                    self.__guild_webhooks = guild_data["webhooks_dict"]
                except json.decoder.JSONDecodeError:
                    logging.error(
                        "An error occured when retrieving data for guild n°%d",
                        self.guild_id,
                    )

    @property
    def id(self) -> int:
        """Return discord guild ID"""
        return self.id

    @id.setter
    def id(self, _value: int) -> None:
        raise AttributeError("Guild ID cannot be modified")

    def __eq__(self, __o: object) -> bool:
        """Test if the specified object `__o` is equal to this instance
        ## Parameter:
        * `__o`: object to compare to this instance
        ## Return value:
        `True` if the specified object to this instance, `False` otherwise"""

        if not isinstance(__o, SunGuild):
            return False
        # Two servers are equal if they have the same ID:
        return self.id == __o.id

    def add_member(self, member: SunUser) -> bool:
        """Adds an user to this server.
        ## Parameter:
        * `member`: user to add to this server
        ## Return value:
        returns `True` if the user was added to the server, otherwise `False`. Falling to add
        an user can be explain by the fact that user was already added in this server"""
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
        logging.info(
            "User n°%d has been sucessfully added to the server %d", member.id, self.id
        )
        return True

    def remove_member(self, member_id: int) -> bool:
        """Removes an user from this server, if the user exists in this server.
        ## Parameter:
        * `member_id`: identifiant of the user to be removed from this server
        ## Return value:
        Return `True` if the corresponding user was successfully removed from this
        server, otherwise `False`"""
        # if ID specified in arguments does not correspond to any server's user :
        if member_id not in self.__guild_members:
            logging.error(
                "Member n°%d does not belong to the guild %d", member_id, self.id
            )
            return False
        self.__guild_members.pop(member_id)
        logging.info(
            "Member %d has been removed from the guild %d with success",
            member_id,
            self.id,
        )
        return True

    def add_webhook(self, webhook_link: str, enabled: bool = True) -> bool:
        """Adds a webhook to this server. If webhook was already added, do nothing.
        ## Parameters:
        * `webhookLink`: link corresponding to the webhook to add
        * `enabled`:boolean that indicates whether specified webhook is enabled
        ## Return value:
        Return `True` if the webhook was successfully added to this server,
        otherwise `False`"""
        if webhook_link in self.__guild_webhooks:
            logging.error(
                "Webhook pointed by %s was already added to the guild %d. Abort"
            )
            return False
        self.__guild_webhooks[webhook_link] = enabled
        logging.info(
            "Webhook %s was successfully added to the server n°%d",
            webhook_link,
            self.id,
        )
        return True

    def remove_webhook(self, webhook_link: str) -> bool:
        """Removes a webhoook from this server. If webhook does not exist,
        do nothing.
        ## Parameter:
        * `webhookLink`: link corresponding to the webhook to remove
        ## Return value:
        Return True if webhook was removed successfully, otherwise False"""
        if webhook_link not in self.__guild_webhooks.keys():
            logging.error(
                "Webhook pointed by %s doesn't exist in the server %d.Do nothing.",
                webhook_link,
                self.id,
            )
            return False
        self.__guild_webhooks.pop(webhook_link)
        logging.info(
            "Webhook %s was successfully removed from the server %d",
            webhook_link,
            self.id,
        )
        return True

    def update_webhook(self, webhook_link: str, enabled: bool) -> bool:
        """Enables or disables webhook specified in arguments, if it exists in
        this server.
        ## Parameters:
        * `webhooklink`: link corresponding to the webhook to update the status
        * `enabled`: flag that indicates the new state for specified webhook. `True`
        to enable, `False` to disable
        ## Return value:
        Return `True` if operation was a success, otherwise `False`"""
        if webhook_link not in self.__guild_webhooks.keys():
            logging.error(
                "Webhook %s does not exist in the server %d. Do nothing",
                webhook_link,
                self.id,
            )
            return False
        self.__guild_webhooks[webhook_link] = enabled
        logging.info(
            "Webhook %s is now enabled in the server %d", webhook_link, self.id
        )
        return True

    def save_srv_data(self):
        """Private method used to save server's data into corresponding backup
        file"""
        with open(
            f"{SunGuild.srv_backup_path}{self.id}.json", "w", encoding="UTF-8"
        ) as guild_file:
            # To make current object transient, clear temporally dictionnary of users:
            tmp_members_dict = self.__guild_members
            object.__setattr__(self, "usr_dir", None)
            # Save server data into the backup file:
            json_data = json.dumps(self.__dict__, ensure_ascii=False, indent=2)
            guild_file.write(json_data)
            object.__setattr__(self, "usr_dir", tmp_members_dict)
        os.chmod(f"{SunGuild.srv_backup_path}{self.id}.json", mode=0o777)
