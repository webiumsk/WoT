# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortFixedPlayersWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortFixedPlayersWindowMeta(DAAPIModule):

    def assignToBuilding(self):
        self._printOverrideError('assignToBuilding')

    def as_setWindowTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowTitle(value)

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
