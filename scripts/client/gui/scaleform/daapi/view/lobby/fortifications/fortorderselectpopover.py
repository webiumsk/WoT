# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortOrderSelectPopover.py
import constants
from adisp import process
from helpers.i18n import makeString as _ms
from debug_utils import LOG_DEBUG
from gui.prb_control import getBattleID
from gui.prb_control.prb_helpers import UnitListener
from gui.shared.fortifications.context import ActivateConsumableCtx, ReturnConsumableCtx
from gui.Scaleform.daapi.view.meta.FortOrderSelectPopoverMeta import FortOrderSelectPopoverMeta
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework import AppRef
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper

class FortOrderSelectPopover(FortOrderSelectPopoverMeta, SmartPopOverView, View, FortViewHelper, AppRef, UnitListener):

    def __init__(self, ctx = None):
        super(FortOrderSelectPopover, self).__init__()
        self.__slotIdx = ctx.get('data')

    def onWindowClose(self):
        self.destroy()

    @process
    def addOrder(self, consumableOrderTypeID):
        yield self.fortProvider.sendRequest(ActivateConsumableCtx(consumableOrderTypeID, self.__slotIdx, waitingID='fort/activateConsumable'))

    @process
    def removeOrder(self, consumableOrderTypeID):
        yield self.fortProvider.sendRequest(ReturnConsumableCtx(consumableOrderTypeID, waitingID='fort/returnConsumable'))

    def onConsumablesChanged(self, battleID, consumableOrderTypeID):
        self.destroy()

    def _populate(self):
        super(FortOrderSelectPopover, self)._populate()
        self.startFortListening()
        self.__updateData()

    def _dispose(self):
        self.stopFortListening()
        super(FortOrderSelectPopover, self)._dispose()

    def __updateData(self):
        fort = self.fortCtrl.getFort()
        battle = fort.getBattle(getBattleID())
        _getText = self.app.utilsManager.textManager.getText
        result = []
        if battle is not None:
            activeConsumes = dict(((otID, slotIdx) for slotIdx, (otID, level) in battle.getActiveConsumables().iteritems()))
            for orderTypeID in constants.FORT_ORDER_TYPE.CONSUMABLES:
                orderItem = fort.getOrder(orderTypeID)
                building = fort.getBuilding(orderItem.buildingID)
                isBuildingReady = building is not None
                isSelected = orderTypeID in activeConsumes
                isSelectedInThisSlot = isSelected and activeConsumes[orderTypeID] == self.__slotIdx
                isConsumableEnabled = isSelectedInThisSlot or not isSelected and orderItem.count > 0
                showArsenalIcon = isBuildingReady and not isSelected
                if isSelectedInThisSlot:
                    returnBtnLabel = FORTIFICATIONS.ORDERSELECTPOPOVER_RETURNBTNLABEL
                else:
                    returnBtnLabel = ''
                orderLevelLabel = _getText(TextType.MAIN_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_ORDERLEVEL, orderLevel=orderItem.level))
                if not isBuildingReady:
                    icon = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_REDNOTAVAILABLE, 16, 16, -2, 0))
                    description = '%s %s' % (icon, _getText(TextType.ERROR_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_NOTAVAILABLE)))
                    orderCountText = ''
                elif not isSelected:
                    description = orderLevelLabel
                    if orderItem.count:
                        orderCountText = _getText(TextType.STANDARD_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_ORDERCOUNT, orderNumber=_getText(TextType.STATS_TEXT, str(orderItem.count))))
                    else:
                        orderCountText = _getText(TextType.STANDARD_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_ORDERCOUNT, orderNumber=orderItem.count))
                else:
                    if isSelectedInThisSlot:
                        description = ''
                    else:
                        description = orderLevelLabel
                    icon = self.app.utilsManager.textManager.getIcon(TextIcons.CHECKMARK_ICON)
                    orderCountText = icon + _getText(TextType.SUCCESS_TEXT, _ms(FORTIFICATIONS.ORDERSELECTPOPOVER_SELECTED))
                result.append({'orderID': orderTypeID,
                 'orderIconSrc': orderItem.icon,
                 'headerText': _getText(TextType.MIDDLE_TITLE, _ms(orderItem.userName)),
                 'descriptionText': description,
                 'orderCountText': orderCountText,
                 'isEnabled': isConsumableEnabled,
                 'isSelected': isSelectedInThisSlot,
                 'showArsenalIcon': showArsenalIcon,
                 'returnBtnLabel': returnBtnLabel})

        self.as_setDataS({'orders': result})
        return
