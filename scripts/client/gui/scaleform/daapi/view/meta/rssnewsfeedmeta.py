# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RssNewsFeedMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class RssNewsFeedMeta(DAAPIModule):

    def openBrowser(self, linkToOpen):
        self._printOverrideError('openBrowser')

    def as_updateFeedS(self, feed):
        if self._isDAAPIInited():
            return self.flashObject.as_updateFeed(feed)
