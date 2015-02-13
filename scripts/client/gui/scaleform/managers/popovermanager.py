# Embedded file name: scripts/client/gui/Scaleform/managers/PopoverManager.py
from gui.Scaleform.framework import ViewTypes, g_entitiesFactories, AppRef
from gui.Scaleform.framework.entities.abstract.PopoverManagerMeta import PopoverManagerMeta
from gui.shared.events import HidePopoverEvent

class PopoverManager(PopoverManagerMeta, AppRef):

    def __init__(self):
        super(PopoverManager, self).__init__()
        self.addListener(HidePopoverEvent.POPOVER_DESTROYED, self.__handlerDestroyPopover)

    def requestShowPopover(self, alias, data):
        self.fireEvent(g_entitiesFactories.makeShowPopoverEvent(alias, {'data': data}))

    def requestHidePopover(self):
        self.fireEvent(HidePopoverEvent(HidePopoverEvent.HIDE_POPOVER))

    def destroy(self):
        self.removeListener(HidePopoverEvent.POPOVER_DESTROYED, self.__handlerDestroyPopover)
        super(PopoverManager, self).destroy()

    def __handlerDestroyPopover(self, event):
        self.as_onPopoverDestroyS()
