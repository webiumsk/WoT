# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationStaffViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class StaticFormationStaffViewMeta(DAAPIModule):

    def showRecriutmentWindow(self):
        self._printOverrideError('showRecriutmentWindow')

    def showInviteWindow(self):
        self._printOverrideError('showInviteWindow')

    def setRecruitmentOpened(self, opened):
        self._printOverrideError('setRecruitmentOpened')

    def removeMember(self, id, userName):
        self._printOverrideError('removeMember')

    def promoteMember(self, id, userName):
        self._printOverrideError('promoteMember')

    def demoteMember(self, id, userName):
        self._printOverrideError('demoteMember')

    def as_setStaticHeaderDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setStaticHeaderData(data)

    def as_updateHeaderDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateHeaderData(data)

    def as_updateStaffDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateStaffData(data)

    def as_setRecruitmentAvailabilityS(self, available):
        if self._isDAAPIInited():
            return self.flashObject.as_setRecruitmentAvailability(available)
