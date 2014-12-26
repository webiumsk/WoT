# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortBattleRoomWindow.py
import BigWorld
from UnitBase import UNIT_BROWSER_ERROR
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui import DialogsInterface, SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.dialogs.rally_dialog_meta import UnitConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.rally import NavigationStack
from gui.Scaleform.framework import AppRef
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.managers.windows_stored_data import stored_window, DATA_TYPE, TARGET_ID
from gui.Scaleform.daapi.view.meta.FortBattleRoomWindowMeta import FortBattleRoomWindowMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control import settings
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.context import unit_ctx
from gui.prb_control.context.unit_ctx import JoinUnitCtx, LeaveUnitCtx
from gui.prb_control.formatters import messages
from gui.prb_control.prb_helpers import prbPeripheriesHandlerProperty
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES, UNIT_MODE_FLAGS, FUNCTIONAL_EXIT
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent
from gui.shared import events
from gui.shared.fortifications.context import CreateSortieCtx, CreateOrJoinFortBattleCtx
from gui.shared.fortifications.fort_helpers import fortProviderProperty, FortListener

@stored_window(DATA_TYPE.UNIQUE_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class FortBattleRoomWindow(FortBattleRoomWindowMeta, AppRef, FortListener):

    def __init__(self, ctx = None):
        self.__isMinimize = False
        super(FortBattleRoomWindow, self).__init__()
        self.__modeFlags = ctx.get('modeFlags', UNIT_MODE_FLAGS.UNDEFINED)

    @fortProviderProperty
    def fortProvider(self):
        return None

    @prbPeripheriesHandlerProperty
    def prbPeripheriesHandler(self):
        return None

    def onWindowClose(self):
        self.__clearCache()
        self.prbDispatcher.doLeaveAction(LeaveUnitCtx(waitingID='prebattle/leave', funcExit=FUNCTIONAL_EXIT.NO_FUNC))

    def onWindowMinimize(self):
        self.__isMinimize = True
        g_eventDispatcher.showUnitProgressInCarousel(PREBATTLE_TYPE.SORTIE)
        self.destroy()

    def getIntroViewAlias(self):
        return FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_INTRO_VIEW_UI

    def getFlashAliases(self):
        return FORTIFICATION_ALIASES.FLASH_ALIASES

    def getPythonAliases(self):
        return FORTIFICATION_ALIASES.PYTHON_ALIASES

    def getNavigationKey(self):
        return 'FortBattleRoomWindow'

    def getPrbType(self):
        return PREBATTLE_TYPE.SORTIE

    def onBrowseRallies(self):
        self._requestViewLoad(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_LIST_VIEW_UI, None)
        return

    def onBrowseClanBattles(self):
        self._requestViewLoad(FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_LIST_VIEW_UI, None)
        return

    def onJoinClanBattle(self, battleID, slotIndex, peripheryID):
        self.__handleCreateOrJoinFortBattle(peripheryID, battleID, slotIndex)

    def onCreatedBattleRoom(self, battleID, peripheryID):
        self.__handleCreateOrJoinFortBattle(peripheryID, battleID)

    def onCreateRally(self):
        if not BigWorld.player().isLongDisconnectedFromCenter:
            self.__clearCache()
            self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            SystemMessages.pushI18nMessage('#system_messages:fortification/errors/CENTER_NOT_AVAILABLE', type=SystemMessages.SM_TYPE.Error)

    def onJoinRally(self, rallyId, slotIndex, peripheryID):
        self.__clearCache()
        ctx = JoinUnitCtx(rallyId, PREBATTLE_TYPE.SORTIE, slotIndex, waitingID='prebattle/join')
        if g_lobbyContext.isAnotherPeriphery(peripheryID):
            if g_lobbyContext.isPeripheryAvailable(peripheryID):
                self.__requestToReloginAndJoinSortie(peripheryID, ctx)
            else:
                SystemMessages.pushI18nMessage('#system_messages:periphery/errors/isNotAvailable', type=SystemMessages.SM_TYPE.Error)
        else:
            self.__requestToJoinSortie(ctx)

    def autoSearchCancel(self, value):
        self.currentState = value
        if value == CYBER_SPORT_ALIASES.AUTO_SEARCH_COMMANDS_STATE or value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE or value == CYBER_SPORT_ALIASES.AUTO_SEARCH_WAITING_PLAYERS_STATE:
            self.unitFunctional.request(unit_ctx.AutoSearchUnitCtx(action=0))
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_CONFIRMATION_STATE:
            self.unitFunctional.request(unit_ctx.DeclineSearchUnitCtx())
        elif value == CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE:
            self.unitFunctional.request(unit_ctx.BattleQueueUnitCtx(action=0))

    def onUnitFunctionalInited(self):
        self.__loadRoomView()

    def onUnitFunctionalFinished(self):
        if self.unitFunctional.getExit() == settings.FUNCTIONAL_EXIT.INTRO_UNIT:
            if self.unitFunctional.isKicked():
                self._goToNextView(closeForced=True)
        else:
            NavigationStack.clear(self.getNavigationKey())

    def onUnitPlayerAdded(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_ADDED, pInfo)

    def onUnitPlayerRemoved(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_REMOVED, pInfo)

    def __addPlayerNotification(self, key, pInfo):
        chat = self.chat
        if chat and not pInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getUnitPlayerNotification(key, pInfo))

    def onUnitStateChanged(self, state, timeLeft):
        if self.unitFunctional.hasLockedState():
            if state.isInQueue():
                self.as_enableWndCloseBtnS(False)
                self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE
            else:
                LOG_ERROR('View for modal state is not resolved', state)
            self.__initState(timeLeft=timeLeft)
        else:
            self.__clearState()

    def onUnitErrorReceived(self, errorCode):
        self.as_autoSearchEnableBtnS(True)

    def onUnitAutoSearchFinished(self):
        self.__clearState()

    def onUnitBrowserErrorReceived(self, errorCode):
        if errorCode == UNIT_BROWSER_ERROR.ACCEPT_TIMEOUT:
            self.currentState = CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE
            self.__initState()
        else:
            self.as_autoSearchEnableBtnS(True)

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        if pInfo.isCurrentPlayer():
            self.as_changeAutoSearchBtnsStateS(pPermissions.canInvokeAutoSearch(), pPermissions.canStopBattleQueue())

    def loadListView(self):
        self._requestViewLoad(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_LIST_VIEW_UI, None)
        return

    def onUnitRejoin(self):
        super(FortBattleRoomWindow, self).onUnitRejoin()
        self.__clearState()

    def onIntroUnitFunctionalFinished(self):
        if self.unitFunctional.getExit() != settings.FUNCTIONAL_EXIT.UNIT:
            NavigationStack.clear(self.getNavigationKey())

    def _populate(self):
        super(FortBattleRoomWindow, self)._populate()
        from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.SORTIE)
        self.addListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleUnitWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(FortEvent.CHOICE_DIVISION, self.__onLoadStart, scope=EVENT_BUS_SCOPE.LOBBY)
        unitMgrID = self.unitFunctional.getID()
        if unitMgrID > 0:
            self.__loadRoomView()
        else:
            self.__initIntroView()
        self.unitFunctional.initEvents(self)
        g_eventDispatcher.hideUnitProgressInCarousel(PREBATTLE_TYPE.SORTIE)

    def _dispose(self):
        self.removeListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleUnitWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(FortEvent.CHOICE_DIVISION, self.__onLoadStart, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__clearCache()
        super(FortBattleRoomWindow, self)._dispose()

    def __clearCache(self):
        if not self.__isMinimize and self.fortCtrl is not None:
            self.fortCtrl.removeSortiesCache()
            self.fortCtrl.removeFortBattlesCache()
        return

    def __initIntroView(self):
        isListShow = self.__modeFlags & UNIT_MODE_FLAGS.SHOW_LIST > 0
        navKey = self.getNavigationKey()
        if isListShow:
            NavigationStack.clear(navKey)
            self._requestViewLoad(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_LIST_VIEW_UI, None)
        else:
            NavigationStack.exclude(navKey, FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_UI)
            NavigationStack.exclude(navKey, FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_ROOM_VIEW_UI)
            if NavigationStack.hasHistory(navKey):
                flashAlias, _, itemID = NavigationStack.current(navKey)
                self._requestViewLoad(flashAlias, itemID)
            else:
                self._requestViewLoad(self.getIntroViewAlias(), None)
        return

    @process
    def __requestToCreateSortie(self, value):
        yield self.fortProvider.sendRequest(CreateSortieCtx(value, 'fort/sortie/create'))

    @process
    def __requestToReloginAndJoinSortie(self, peripheryID, ctx):
        result = yield DialogsInterface.showDialog(UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'changePeriphery', messageCtx={'host': g_lobbyContext.getPeripheryName(peripheryID)}))
        if result:
            self.prbPeripheriesHandler.join(peripheryID, ctx)

    @process
    def __requestToJoinSortie(self, ctx):
        yield self.prbDispatcher.join(ctx)

    def __handleCreateOrJoinFortBattle(self, peripheryID, battleID, slotIndex = -1):
        self.__clearCache()
        if g_lobbyContext.isAnotherPeriphery(peripheryID):
            if g_lobbyContext.isPeripheryAvailable(peripheryID):
                self.__requestToReloginAndCreateOrJoinFortBattle(peripheryID, battleID, slotIndex)
            else:
                SystemMessages.pushI18nMessage('#system_messages:periphery/errors/isNotAvailable', type=SystemMessages.SM_TYPE.Error)
        else:
            self.__requestToCreateOrJoinFortBattle(battleID, slotIndex)

    @process
    def __requestToCreateOrJoinFortBattle(self, battleID, slotIndex = -1):
        yield self.prbDispatcher.join(CreateOrJoinFortBattleCtx(battleID, slotIndex, 'fort/fortBattle/createOrJoin'))

    @process
    def __requestToReloginAndCreateOrJoinFortBattle(self, peripheryID, battleID, slotIndex = -1):
        result = yield DialogsInterface.showDialog(UnitConfirmDialogMeta(PREBATTLE_TYPE.FORT_BATTLE, 'changePeriphery', messageCtx={'host': g_lobbyContext.getPeripheryName(peripheryID)}))
        if result:
            self.prbPeripheriesHandler.join(peripheryID, CreateOrJoinFortBattleCtx(battleID, slotIndex, 'fort/fortBattle/createOrJoin'))

    def __onLoadStart(self, event):
        divisionLevel = event.ctx.get('data', None)
        if divisionLevel:
            self.__requestToCreateSortie(divisionLevel)
        return

    def __handleUnitWindowHide(self, _):
        self.destroy()

    def __initState(self, timeLeft = 0, acceptDelta = 0):
        model = None
        if self.isPlayerInSlot():
            if self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_ENEMY_STATE:
                model = self.__createAutoUpdateModel(self.currentState, timeLeft, '', [])
            elif self.currentState == CYBER_SPORT_ALIASES.AUTO_SEARCH_ERROR_STATE:
                model = self.__createAutoUpdateModel(self.currentState, 0, '', [])
        if model is not None:
            self.as_changeAutoSearchStateS(model)
        return

    def __clearState(self):
        self.currentState = ''
        self.as_enableWndCloseBtnS(True)
        self.as_hideAutoSearchS()

    def __createAutoUpdateModel(self, state, countDownSeconds, ctxMessage, playersReadiness):
        permissions = self.unitFunctional.getPermissions(unitIdx=self.unitFunctional.getUnitIdx())
        model = {'state': state,
         'countDownSeconds': countDownSeconds,
         'contextMessage': ctxMessage,
         'playersReadiness': playersReadiness,
         'canInvokeAutoSearch': permissions.canInvokeAutoSearch(),
         'canInvokeBattleQueue': permissions.canStopBattleQueue()}
        return model

    def __loadRoomView(self):
        unit = self.unitFunctional
        state = unit.getState()
        if state.isFortBattle():
            self._requestViewLoad(FORTIFICATION_ALIASES.FORT_CLAN_BATTLE_ROOM_VIEW_UI, self.unitFunctional.getID())
        elif state.isSortie():
            self._requestViewLoad(FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_VIEW_UI, self.unitFunctional.getID())
