# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReferralReferralsIntroWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ReferralReferralsIntroWindowMeta(DAAPIModule):

    def onClickApplyBtn(self):
        self._printOverrideError('onClickApplyBtn')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
