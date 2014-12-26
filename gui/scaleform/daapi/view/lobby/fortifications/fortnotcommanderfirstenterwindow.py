# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortNotCommanderFirstEnterWindow.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.FortNotCommanderFirstEnterWindowMeta import FortNotCommanderFirstEnterWindowMeta
from gui.Scaleform.framework import AppRef
from helpers import i18n
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS

class FortNotCommanderFirstEnterWindow(AbstractWindowView, View, FortNotCommanderFirstEnterWindowMeta, AppRef):

    def __init__(self, ctx = None):
        super(FortNotCommanderFirstEnterWindow, self).__init__()

    def _populate(self):
        super(FortNotCommanderFirstEnterWindow, self)._populate()
        self.__makeData()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        super(FortNotCommanderFirstEnterWindow, self)._dispose()

    def __makeData(self):
        ms = i18n.makeString
        self.as_setWindowTitleS(ms(FORTIFICATIONS.FORTNOTCOMMANDERFIRSTENTERWINDOW_WINDOWTITLE))
        self.as_setTitleS(ms(FORTIFICATIONS.FORTNOTCOMMANDERFIRSTENTERWINDOW_TEXTTITLE))
        self.as_setTextS(ms(FORTIFICATIONS.FORTNOTCOMMANDERFIRSTENTERWINDOW_TEXTDESCRIPTION))
        self.as_setButtonLblS(ms(FORTIFICATIONS.FORTNOTCOMMANDERFIRSTENTERWINDOW_APPLYBTNLABEL))
