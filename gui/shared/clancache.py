# Embedded file name: scripts/client/gui/shared/ClanCache.py
import BigWorld
from Event import Event
from account_helpers import getPlayerDatabaseID
from adisp import async, process
from constants import CLAN_MEMBER_FLAGS
from debug_utils import LOG_ERROR
from gui.shared.utils.functions import getClanRoleString
from gui.shared.fortifications.fort_provider import ClientFortProvider
from gui.shared.utils import code2str
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
CLAN_MEMBERS = {CLAN_MEMBER_FLAGS.LEADER: 'leader',
 CLAN_MEMBER_FLAGS.VICE_LEADER: 'vice_leader',
 CLAN_MEMBER_FLAGS.RECRUITER: 'recruiter',
 CLAN_MEMBER_FLAGS.TREASURER: 'treasurer',
 CLAN_MEMBER_FLAGS.DIPLOMAT: 'diplomat',
 CLAN_MEMBER_FLAGS.COMMANDER: 'commander',
 CLAN_MEMBER_FLAGS.PRIVATE: 'private',
 CLAN_MEMBER_FLAGS.RECRUIT: 'recruit',
 CLAN_MEMBER_FLAGS.STAFF: 'staff',
 CLAN_MEMBER_FLAGS.JUNIOR: 'junior',
 CLAN_MEMBER_FLAGS.RESERVIST: 'reservist'}

class _ClanCache(object):

    def __init__(self):
        self.__waitForSync = False
        self.__fortProvider = ClientFortProvider()
        self.__clanMembersLen = None
        self.onSyncStarted = Event()
        self.onSyncCompleted = Event()
        return

    def init(self):
        pass

    def fini(self):
        self.onSyncStarted.clear()
        self.onSyncCompleted.clear()

    def onAccountShowGUI(self):
        self.__startFortProvider()

    def onAvatarBecomePlayer(self):
        self.__stopFortProvider()

    def onDisconnected(self):
        self.__stopFortProvider()

    @property
    def waitForSync(self):
        return self.__waitForSync

    @async
    def update(self, diff = None, callback = None):
        self.__invalidateData(diff, callback)

    def clear(self):
        pass

    @storage_getter('users')
    def usersStorage(self):
        return None

    @property
    def fortProvider(self):
        return self.__fortProvider

    @property
    def clanDBID(self):
        from gui.shared import g_itemsCache
        return g_itemsCache.items.stats.clanDBID

    @property
    def isInClan(self):
        """
        @return: is current player in clan
        """
        return self.clanDBID is not None and self.clanDBID != 0

    @property
    def clanMembers(self):
        members = set()
        if self.isInClan:
            members = set(self.usersStorage.getClanMembersIterator(False))
        return members

    @property
    def clanInfo(self):
        from gui.shared import g_itemsCache
        info = g_itemsCache.items.stats.clanInfo
        if info and len(info) > 1:
            return info
        else:
            return (None, None, -1, 0, 0)

    @property
    def clanName(self):
        return self.clanInfo[0]

    @property
    def clanAbbrev(self):
        return self.clanInfo[1]

    @property
    def clanTag(self):
        result = self.clanAbbrev
        if result:
            return '[%s]' % result
        return result

    @property
    def clanCommanderName(self):
        for member in self.clanMembers:
            if member.getClanRole() == CLAN_MEMBER_FLAGS.LEADER:
                return member.getName()

        return None

    @property
    def clanRole(self):
        user = self.usersStorage.getUser(getPlayerDatabaseID())
        if user:
            role = user.getClanRole()
        else:
            role = 0
        return role

    @property
    def isClanLeader(self):
        return self.clanRole == CLAN_MEMBER_FLAGS.LEADER

    @async
    @process
    def getClanEmblemID(self, callback):
        clanEmblem = None
        if self.isInClan:
            tID = 'clanInfo' + BigWorld.player().name
            clanEmblem = yield self.getClanEmblemTextureID(self.clanDBID, False, tID)
        callback(clanEmblem)
        return

    @async
    def getFileFromServer(self, clanId, fileType, callback):
        if not BigWorld.player().serverSettings['file_server'].has_key(fileType):
            LOG_ERROR("Invalid server's file type: %s" % fileType)
            self._valueResponse(0, (None, None), callback)
            return None
        else:
            clan_emblems = BigWorld.player().serverSettings['file_server'][fileType]
            BigWorld.player().customFilesCache.get(clan_emblems['url_template'] % clanId, lambda url, file: self._valueResponse(0, (url, file), callback), True)
            return None

    @async
    @process
    def getClanEmblemTextureID(self, clanDBID, isBig, textureID, callback):
        import imghdr
        if clanDBID is not None and clanDBID != 0:
            _, clanEmblemFile = yield self.getFileFromServer(clanDBID, 'clan_emblems_small' if not isBig else 'clan_emblems_big')
            if clanEmblemFile and imghdr.what(None, clanEmblemFile) is not None:
                BigWorld.wg_addTempScaleformTexture(textureID, clanEmblemFile)
                callback(textureID)
                return
        callback(None)
        return

    def getClanRoleUserString(self):
        position = self.clanInfo[3]
        return getClanRoleString(position)

    def _valueResponse(self, resID, value, callback):
        if resID < 0:
            LOG_ERROR('[class %s] There is error while getting data from cache: %s[%d]' % (self.__class__.__name__, code2str(resID), resID))
            return callback(value)
        callback(value)

    def _onResync(self):
        if not self.__waitForSync:
            self.__invalidateData()

    def __invalidateData(self, diff = None, callback = lambda *args: None):
        if diff is not None:
            if 'stats' in diff and 'clanInfo' in diff['stats']:
                self.__fortProvider.resetState()
        callback(True)
        return

    def __startFortProvider(self):
        self.__clanMembersLen = len(self.clanMembers)
        g_messengerEvents.users.onClanMembersListChanged += self.__me_onClanMembersListChanged
        self.__fortProvider.start(self)

    def __stopFortProvider(self):
        self.__clanMembersLen = None
        g_messengerEvents.users.onClanMembersListChanged -= self.__me_onClanMembersListChanged
        self.__fortProvider.stop()
        return

    def __me_onClanMembersListChanged(self):
        clanMembersLen = len(self.clanMembers)
        if self.__clanMembersLen is not None and clanMembersLen != self.__clanMembersLen:
            self.__clanMembersLen = clanMembersLen
            self.__fortProvider.resetState()
        self.__fortProvider.notify('onClanMembersListChanged')
        return


g_clanCache = _ClanCache()
