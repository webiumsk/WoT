# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrbSendInvitesWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PrbSendInvitesWindowMeta(DAAPIModule):

    def showError(self, value):
        self._printOverrideError('showError')

    def setOnlineFlag(self, value):
        self._printOverrideError('setOnlineFlag')

    def sendInvites(self, accountsToInvite, comment):
        self._printOverrideError('sendInvites')

    def getAllAvailableContacts(self):
        self._printOverrideError('getAllAvailableContacts')

    def as_onReceiveSendInvitesCooldownS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_onReceiveSendInvitesCooldown(value)

    def as_setDefaultOnlineFlagS(self, onlineFlag):
        if self._isDAAPIInited():
            return self.flashObject.as_setDefaultOnlineFlag(onlineFlag)

    def as_showClanOnlyS(self, showClanOnly):
        if self._isDAAPIInited():
            return self.flashObject.as_showClanOnly(showClanOnly)

    def as_setWindowTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowTitle(value)

    def as_onContactUpdatedS(self, contact):
        if self._isDAAPIInited():
            return self.flashObject.as_onContactUpdated(contact)

    def as_onListStateChangedS(self, isEmpty):
        if self._isDAAPIInited():
            return self.flashObject.as_onListStateChanged(isEmpty)
