# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ContextMenuManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ContextMenuManagerMeta(DAAPIModule):

    def requestOptions(self, itemId, type, ctx):
        self._printOverrideError('requestOptions')

    def onOptionSelect(self, optionId):
        self._printOverrideError('onOptionSelect')

    def onHide(self):
        self._printOverrideError('onHide')

    def _getUserInfo(self, uid, userName):
        self._printOverrideError('_getUserInfo')

    def _getDenunciations(self):
        self._printOverrideError('_getDenunciations')

    def _isMoneyTransfer(self):
        self._printOverrideError('_isMoneyTransfer')

    def showUserInfo(self, uid, userName):
        self._printOverrideError('showUserInfo')

    def showMoneyTransfer(self, uid, userName):
        self._printOverrideError('showMoneyTransfer')

    def createPrivateChannel(self, uid, userName):
        self._printOverrideError('createPrivateChannel')

    def addFriend(self, uid, userName):
        self._printOverrideError('addFriend')

    def removeFriend(self, uid):
        self._printOverrideError('removeFriend')

    def setMuted(self, uid, userName):
        self._printOverrideError('setMuted')

    def unsetMuted(self, uid):
        self._printOverrideError('unsetMuted')

    def setIgnored(self, uid, userName):
        self._printOverrideError('setIgnored')

    def unsetIgnored(self, uid):
        self._printOverrideError('unsetIgnored')

    def appeal(self, uid, userName, topic):
        self._printOverrideError('appeal')

    def copyToClipboard(self, name):
        self._printOverrideError('copyToClipboard')

    def kickPlayerFromPrebattle(self, accountID):
        self._printOverrideError('kickPlayerFromPrebattle')

    def kickPlayerFromUnit(self, databaseID):
        self._printOverrideError('kickPlayerFromUnit')

    def giveLeadership(self, databaseID):
        self._printOverrideError('giveLeadership')

    def canGiveLeadership(self, databaseID):
        self._printOverrideError('canGiveLeadership')

    def createSquad(self, databaseID):
        self._printOverrideError('createSquad')

    def invite(self, databaseID, data):
        self._printOverrideError('invite')

    def canInvite(self, databaseID):
        self._printOverrideError('canInvite')

    def fortDirection(self):
        self._printOverrideError('fortDirection')

    def fortAssignPlayers(self, uid):
        self._printOverrideError('fortAssignPlayers')

    def fortModernization(self, uid):
        self._printOverrideError('fortModernization')

    def fortDestroy(self, uid):
        self._printOverrideError('fortDestroy')

    def fortPrepareOrder(self, uid):
        self._printOverrideError('fortPrepareOrder')

    def as_setOptionsS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setOptions(data)
