# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortWelcomeViewComponent.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.FortWelcomeViewMeta import FortWelcomeViewMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.events import OpenLinkEvent
from gui.shared.fortifications.settings import CLIENT_FORT_STATE, FORT_RESTRICTION
from helpers import i18n
from debug_utils import LOG_DEBUG, LOG_ERROR

class FortWelcomeViewComponent(FortWelcomeViewMeta, FortViewHelper, AppRef):

    def __init__(self):
        super(FortWelcomeViewComponent, self).__init__()

    def onNavigate(self, code):
        LOG_DEBUG('navigate: %s' % code)
        g_eventBus.handleEvent(OpenLinkEvent(code))

    def onClientStateChanged(self, state):
        if not self.isDisposed():
            self.__updateData()

    def onClanMembersListChanged(self):
        if not self.isDisposed():
            self.__updateData()

    def _populate(self):
        super(FortWelcomeViewComponent, self)._populate()
        self.startFortListening()
        self.__updateData()
        clanSearch = self.__makeHyperLink('clanSearch', FORTIFICATIONS.FORTWELCOMEVIEW_CLANSEARCH)
        clanCreate = self.__makeHyperLink('clanCreate', FORTIFICATIONS.FORTWELCOMEVIEW_CLANCREATE)
        detail = self.__makeHyperLink('fortDescription', FORTIFICATIONS.FORTWELCOMEVIEW_HYPERLINK_MORE)
        self.as_setHyperLinksS(clanSearch, clanCreate, detail)

    def __makeHyperLink(self, linkType, textId):
        text = i18n.makeString(textId)
        attrs = {'linkType': linkType,
         'text': text}
        linkHtml = makeHtmlString('html_templates:lobby/fortifications', 'link', attrs)
        return linkHtml

    def _dispose(self):
        self.stopFortListening()
        super(FortWelcomeViewComponent, self)._dispose()

    def _getCustomData(self):
        return {'isOnClan': g_clanCache.isInClan,
         'canRoleCreateFortRest': self.fortCtrl.getPermissions().canCreate(),
         'canCreateFortLim': self.fortCtrl.getLimits().isCreationValid()[0]}

    def __updateData(self):
        data = self.getData()
        self.as_setCommonDataS(data)
        self.__updateViewState(data)

    def onViewReady(self):
        g_eventBus.handleEvent(events.FortEvent(events.FortEvent.VIEW_LOADED), scope=EVENT_BUS_SCOPE.FORT)

    def __updateViewState(self, data):
        state = self.fortState
        if state.getStateID() == CLIENT_FORT_STATE.NO_CLAN:
            self.as_setRequirementTextS(self.__getNoClanText())
        elif self.fortCtrl.getPermissions().canCreate():
            result, reason = self.fortCtrl.getLimits().isCreationValid()
            if not result:
                if reason == FORT_RESTRICTION.CREATION_MIN_COUNT:
                    self.as_setWarningTextS(*self.__getNotEnoughMembersText(data))
                else:
                    LOG_ERROR('Text is not found by reason', reason)
        else:
            self.as_setRequirementTextS(self.__getClanMemberWelcomeText(data))

    def __getNoClanText(self):
        return self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTWELCOMEVIEW_REQUIREMENTCLAN))

    def __getNotEnoughMembersText(self, data):
        minClanSize = data.get('minClanSize', 0)
        text = self.app.utilsManager.textManager.getText(TextType.ALERT_TEXT, i18n.makeString(FORTIFICATIONS.FORTWELCOMEVIEW_WARNING, minClanSize=minClanSize))
        header = i18n.makeString(TOOLTIPS.FORTIFICATION_WELCOME_CANTCREATEFORT_HEADER)
        body = i18n.makeString(TOOLTIPS.FORTIFICATION_WELCOME_CANTCREATEFORT_BODY, minClanSize=minClanSize)
        return (text, header, body)

    def __getClanMemberWelcomeText(self, data):
        textOne = ((TextType.STANDARD_TEXT, i18n.makeString(FORTIFICATIONS.FORTWELCOMEVIEW_REQUIREMENTCOMMANDER)), (TextType.NEUTRAL_TEXT, data.get('clanCommanderName', '')))
        return self.app.utilsManager.textManager.concatStyles(textOne)
