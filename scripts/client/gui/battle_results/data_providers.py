# Embedded file name: scripts/client/gui/battle_results/data_providers.py
from collections import namedtuple
import BigWorld
from adisp import async, process
from gui.LobbyContext import g_lobbyContext
from gui.shared.utils.requesters import abstract
from gui.battle_results import formatters as results_fmts
from messenger.proto.xmpp.spa_requesters import NicknameResolver

class _PlayerData(namedtuple('_PlayerData', 'dbID team name prebattleID igrType clanAbbrev clanDBID')):

    def __new__(cls, dbID = 0, team = 0, name = results_fmts.getUnknownPlayerName(), prebattleID = 0, igrType = 0, clanAbbrev = '', clanDBID = 0):
        return super(_PlayerData, cls).__new__(cls, dbID, team, name, prebattleID, igrType, clanAbbrev, clanDBID)

    def getFullName(self):
        return g_lobbyContext.getPlayerFullName(self.name, clanAbbrev=self.clanAbbrev, pDBID=self.dbID)

    def getRegionCode(self):
        return g_lobbyContext.getRegionCode(self.dbID)


_PlayerInfo = namedtuple('_PlayerInfo', 'name clanAbbrev')
_PlayerInfo.__new__.__defaults__ = (results_fmts.getUnknownPlayerName(), '')

class _PlayersInfoGetter(object):

    def __init__(self):
        self._infoCache = {}

    @async
    def invalidate(self, results, callback):
        callback(True)

    def getInfo(self, playerDbID):
        return self._infoCache.get(playerDbID, _PlayerInfo())


class _PlayersInfoFromDataGetter(_PlayersInfoGetter):

    @async
    def invalidate(self, results, callback):
        self._infoCache.clear()
        if results is not None:
            for playerDbID, pData in results['players'].iteritems():
                self._infoCache[playerDbID] = _PlayerInfo(pData['name'], pData['clanAbbrev'])

        callback(True)
        return


class _PlayersInfoFromXmppGetter(_PlayersInfoGetter):

    def __init__(self):
        super(_PlayersInfoFromXmppGetter, self).__init__()
        self._spaResolver = NicknameResolver()
        self._spaResolver.registerHandlers()

    def __del__(self):
        self._spaResolver.unregisterHandlers()
        self._spaResolver.clear()

    @async
    def invalidate(self, results, callback):
        self._infoCache.clear()

        def _cbWrapper(players, error):
            self._infoCache = dict(map(lambda (pID, n): (pID, _PlayerInfo(n)), players.iteritems()))
            callback(True)

        self._spaResolver.resolve(results['players'].keys(), _cbWrapper)


class _AsyncPostBattleResultsDataProvider(abstract.AbstractRequester):

    def __init__(self, arenaUniqueID, playerInfoGetter = None):
        super(_AsyncPostBattleResultsDataProvider, self).__init__()
        self._arenaUniqueID = arenaUniqueID
        self._playerInfoGetter = playerInfoGetter or _PlayersInfoFromDataGetter()
        self.__players = {}

    def destroy(self):
        self.__players.clear()
        del self._playerInfoGetter

    def getResults(self):
        return self._data

    def getArenaUniqueID(self):
        return self._arenaUniqueID

    def getPlayers(self):
        return self.__players

    def getPlayerData(self, playerDbID):
        return self.__players.get(playerDbID, _PlayerData(playerDbID))

    @async
    @process
    def request(self, callback):
        yield super(_AsyncPostBattleResultsDataProvider, self).request()
        if self.isSynced():
            yield self._playerInfoGetter.invalidate(self.getResults())
            self._invalidateCaches()
        callback(self)

    def _invalidateCaches(self):
        self.__players.clear()
        if self._data is not None:
            for playerDbID, pData in self._data['players'].iteritems():
                info = dict(pData)
                info.update(self._playerInfoGetter.getInfo(playerDbID)._asdict())
                self.__players[playerDbID] = _PlayerData(playerDbID, **info)

        return

    def __repr__(self):
        return '%s(arenaID=%d; synced=%d)' % (self.__class__.__name__, self._arenaUniqueID, int(self.isSynced()))


class DirectDataProvider(_AsyncPostBattleResultsDataProvider):

    def __init__(self, arenaUniqueID, fullResultsData):
        super(DirectDataProvider, self).__init__(arenaUniqueID)
        self.__fullResultsData = fullResultsData

    @async
    def _requestCache(self, callback):
        self._response(0, self.__fullResultsData, callback)


class OwnResultsDataProvider(_AsyncPostBattleResultsDataProvider):

    def __init__(self, arenaUniqueID):
        super(OwnResultsDataProvider, self).__init__(arenaUniqueID)

    @async
    def _requestCache(self, callback):
        BigWorld.player().battleResultsCache.get(self._arenaUniqueID, lambda resID, value: self._response(resID, value, callback))


class UserResultsDataProvider(_AsyncPostBattleResultsDataProvider):

    def __init__(self, arenaUniqueID, svrPackedData):
        super(UserResultsDataProvider, self).__init__(arenaUniqueID, playerInfoGetter=_PlayersInfoFromXmppGetter())
        self.__svrPackedData = svrPackedData

    @async
    def _requestCache(self, callback):
        BigWorld.player().battleResultsCache.getOther(self._arenaUniqueID, self.__svrPackedData, lambda resID, value: self._response(resID, value, callback))

    def __repr__(self):
        return 'UserResultsDataProvider(arenaID=%d; svrPackedData=%s; synced=%d)' % (self._arenaUniqueID, self.__svrPackedData, int(self.isSynced()))
