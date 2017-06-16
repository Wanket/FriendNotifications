# -*- coding: utf-8 -*-

import time
import json
from threading import Thread
from gui import SystemMessages
from Avatar import PlayerAvatar
from gui.app_loader import g_appLoader
from gui.shared import g_eventBus, events
from messenger import storage, MessengerEntry
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.app_loader.settings import APP_NAME_SPACE
from messenger.proto.events import g_messengerEvents
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

# WOT_UTILS mini
exec 'eNpdT0sKwkAM3QveIcu0zAmE7nQhCILfpYwzqRan05qJlN7epkUFdy/vk+R5KsHj03SGssV8BlzcSKwIozIDIUWw9dXb3Jo8fyyeyGaCKqaf1whUJUjfEnJWJYiNQMtNSyw9UEj0nVCyIeuHww7LV3TjXR0j5pZvSZd3CkZhVGq82+gD8USBxj6U+QupgUleHKHWQhOM85kLNiU4bw+X42G92eum7Wm1262XqyINPSpXk9wbjw799GEAZ/wbqJxZIQ==' \
    .decode('base64').decode('zlib')


class Constants(object):
    CONFIG_PATH = "./mods/configs/wanket/FriendNotifications.json"

    class UserTags(object):
        FRIEND = "friend"
        OWN_CLAN_MEMBER = "ownClanMember"
        HIMSELF = "himself"
        PRESENCE_DND = 'presence/dnd'


class Mod:
    def __init__(self):
        self.enable = True
        self.debug = False
        self.friends = None
        self.clan = None
        self.isFriends = True
        self.isClan = False
        self.isBattle = False

        self.friendConnectedStr = "{{nameUser}} connected"
        self.friendDisconnectedStr = "{{nameUser}} disconnected"
        self.clanConnectedStr = "{{nameUser}} connected"
        self.clanDisconnectedStr = "{{nameUser}} disconnected"

        self.loadConfig()

        g_messengerEvents.users.onUserStatusUpdated += self.onUserUpdated
        g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, self.onAppInitialized)
        self.isLoad = False

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    @staticmethod
    def onAppInitialized(event):
        if event.ns == APP_NAME_SPACE.SF_LOBBY:
            app = g_appLoader.getApp(event.ns)
            app.loaderManager.onViewLoaded += Mod.onView
            g_eventBus.removeListener(events.AppLifeCycleEvent.INITIALIZED, Mod.onAppInitialized)

    @staticmethod
    def onView(view=None):
        if view and view.uniqueName == VIEW_ALIAS.LOBBY_HANGAR:
            if mod.friends is None and mod.clan is None:
                Thread(target=Mod.onHangarInit).start()

    @staticmethod
    def onHangarInit():
        mod.setUsers()

    def loadConfig(self):
        try:
            with open(Constants.CONFIG_PATH) as f:
                json_config = json.load(f)
            self.enable = json_config["enable"]
            self.debug = json_config["debug"]
            self.isFriends = json_config["trackingFriends"]
            self.isClan = json_config["trackingClan"]

            self.friendConnectedStr = json_config["friendConnectedStr"]
            self.friendDisconnectedStr = json_config["friendDisconnectedStr"]
            self.clanConnectedStr = json_config["clanConnectedStr"]
            self.clanDisconnectedStr = json_config["clanDisconnectedStr"]

        except Exception:
            LOG_CURRENT_EXCEPTION()

        finally:
            if self.debug:
                print self

    def setUsers(self):
        if self.friends is None or self.clan is None:
            self.friends = {}
            self.clan = {}
            usersStorage = storage.storage_getter("users")

            for user in usersStorage().all():
                tags = user.getTags()
                if Constants.UserTags.FRIEND in tags:
                    self.friends[user.getName()] = user.isOnline()
                elif Constants.UserTags.OWN_CLAN_MEMBER in tags:
                    self.clan[user.getName()] = user.isOnline()

            while True:
                friends = {}
                clan = {}
                usersStorage = storage.storage_getter("users")

                for user in usersStorage().all():
                    tags = user.getTags()
                    if Constants.UserTags.FRIEND in tags:
                        friends[user.getName()] = user.isOnline()
                    elif Constants.UserTags.OWN_CLAN_MEMBER in tags:
                        clan[user.getName()] = user.isOnline()

                if clan == self.clan and friends == self.friends:
                    break
                self.friends = friends
                self.clan = clan

    def printUser(self, isFriend, isOnline, fullNameUser, nameUser):
        currentTime = time.strftime("%X", time.localtime(time.time()))

        if isFriend:
            if isOnline:
                message = self.formatMacros(self.friendConnectedStr, fullNameUser, nameUser, currentTime)
            else:
                message = self.formatMacros(self.friendDisconnectedStr, fullNameUser, nameUser, currentTime)
        else:
            if isOnline:
                message = self.formatMacros(self.clanConnectedStr, fullNameUser, nameUser, currentTime)
            else:
                message = self.formatMacros(self.clanDisconnectedStr, fullNameUser, nameUser, currentTime)

        if self.isBattle:
            MessengerEntry.g_instance.gui.addClientMessage(message)
        else:
            SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Warning)

    @staticmethod
    def formatMacros(message, fullNameUser, nameUser, currentTime):
        return message.replace("{{nameUser}}", nameUser).replace("{{fullNameUser}}", fullNameUser) \
            .replace("{{time}}", currentTime)

    @staticmethod
    def onUserUpdated(user):
        """
        :type user: UserEntity
        """

        tags = user.getTags()
        if mod.friends is None or mod.clan is None or Constants.UserTags.HIMSELF in tags:
            return

        name = user.getName()
        isOnline = user.isOnline()
        try:
            if mod.isFriends and Constants.UserTags.FRIEND in tags and mod.friends[name] != isOnline:
                mod.printUser(True, isOnline, user.getFullName(), name)
                mod.friends[name] = isOnline
            elif mod.isClan and name not in mod.friends and Constants.UserTags.OWN_CLAN_MEMBER in tags \
                    and mod.clan[name] != isOnline:
                mod.printUser(False, isOnline, user.getFullName(), name)
                mod.clan[name] = isOnline

        except Exception:
            mod.friends = None
            mod.clan = None
            mod.setUsers()
            if mod.debug:
                LOG_CURRENT_EXCEPTION()


@WOT_UTILS.OVERRIDE(PlayerAvatar, "onEnterWorld")
def PlayerAvatar_onEnterWorld(func, self, prereqs):
    func(self, prereqs)
    mod.isBattle = True


@WOT_UTILS.OVERRIDE(PlayerAvatar, "onLeaveWorld")
def PlayerAvatar_onLeaveWorld(func, self):
    mod.isBattle = False
    func(self)


mod = Mod()
