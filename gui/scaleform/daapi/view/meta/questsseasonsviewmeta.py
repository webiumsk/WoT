# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsSeasonsViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsSeasonsViewMeta(DAAPIModule):

    def onShowAwardsClick(self, seasonID):
        self._printOverrideError('onShowAwardsClick')

    def onTileClick(self, tileID):
        self._printOverrideError('onTileClick')

    def onSlotClick(self, slotID):
        self._printOverrideError('onSlotClick')

    def as_setSeasonsDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setSeasonsData(data)

    def as_setSlotsDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setSlotsData(data)
