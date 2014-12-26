# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Crew.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.CrewMeta import CrewMeta
from gui import SystemMessages
from gui.shared.utils.functions import getViewName
from items.tankmen import getSkillsConfig, compareMastery, ACTIVE_SKILLS
from helpers.i18n import convert
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import events, g_itemsCache
from gui.shared.events import LoadViewEvent
from gui.Scaleform.Waiting import Waiting
from gui.shared.utils import decorators
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman
from gui.shared.gui_items.processors.tankman import TankmanUnload, TankmanEquip

class Crew(CrewMeta):

    def __init__(self):
        super(Crew, self).__init__()

    def _populate(self):
        super(Crew, self)._populate()
        g_clientUpdateManager.addCallbacks({'inventory': self.onInventoryUpdate})

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(Crew, self)._dispose()

    def onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            self.updateTankmen()

    def updateTankmen(self):
        Waiting.show('updateTankmen')
        if g_currentVehicle.isPresent():
            tankmen = g_itemsCache.items.getTankmen()
            vehicle = g_currentVehicle.item
            commander_bonus = vehicle.bonuses['commander']
            roles = []
            lessMastered = 0
            tankmenDescrs = dict(vehicle.crew)
            for slotIdx, tman in vehicle.crew:
                if slotIdx > 0 and tman is not None and (tankmenDescrs[lessMastered] is None or compareMastery(tankmenDescrs[lessMastered].descriptor, tman.descriptor) > 0):
                    lessMastered = slotIdx
                role = vehicle.descriptor.type.crewRoles[slotIdx][0]
                roles.append({'tankmanID': tman.invID if tman is not None else None,
                 'roleType': role,
                 'role': convert(getSkillsConfig()[role]['userString']),
                 'roleIcon': Tankman.getRoleBigIconPath(role),
                 'nationID': vehicle.nationID,
                 'typeID': vehicle.innationID,
                 'slot': slotIdx,
                 'vehicleType': vehicle.shortUserName,
                 'tankType': vehicle.type,
                 'vehicleElite': vehicle.isPremium,
                 'roles': list(vehicle.descriptor.type.crewRoles[slotIdx])})

            tankmenData = []
            for tankman in tankmen.itervalues():
                if tankman.isInTank and tankman.vehicleInvID != vehicle.invID:
                    continue
                tankmanVehicle = g_itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
                bonus_role_level = commander_bonus if tankman.descriptor.role != 'commander' else 0.0
                skills_count = len(list(ACTIVE_SKILLS))
                skillsList = []
                for skill in tankman.skills:
                    skillsList.append({'tankmanID': tankman.invID,
                     'id': str(tankman.skills.index(skill)),
                     'name': skill.userName,
                     'desc': skill.description,
                     'icon': skill.icon,
                     'level': skill.level,
                     'active': skill.isEnable and skill.isActive})

                newSkillsCount, lastNewSkillLvl = tankman.newSkillCount
                if newSkillsCount > 0:
                    skillsList.append({'buy': True,
                     'tankmanID': tankman.invID,
                     'level': lastNewSkillLvl})
                tankmanData = {'firstname': tankman.firstUserName,
                 'lastname': tankman.lastUserName,
                 'rank': tankman.rankUserName,
                 'specializationLevel': tankman.realRoleLevel[0],
                 'role': tankman.roleUserName,
                 'vehicleType': tankmanVehicle.shortUserName,
                 'iconFile': tankman.icon,
                 'rankIconFile': tankman.iconRank,
                 'roleIconFile': Tankman.getRoleBigIconPath(tankman.descriptor.role),
                 'contourIconFile': tankmanVehicle.iconContour,
                 'tankmanID': tankman.invID,
                 'nationID': tankman.nationID,
                 'typeID': tankmanVehicle.innationID,
                 'inTank': tankman.isInTank,
                 'roleType': tankman.descriptor.role,
                 'tankType': tankmanVehicle.type,
                 'efficiencyLevel': tankman.efficiencyRoleLevel,
                 'bonus': bonus_role_level,
                 'lastSkillLevel': tankman.descriptor.lastSkillLevel,
                 'isLessMastered': vehicle.crewIndices.get(tankman.invID) == lessMastered and vehicle.isXPToTman,
                 'compact': tankman.strCD,
                 'availableSkillsCount': skills_count,
                 'skills': skillsList}
                tankmenData.append(tankmanData)

            self.as_tankmenResponseS(roles, tankmenData)
        Waiting.hide('updateTankmen')
        return

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.RECRUIT_WINDOW, ctx={'data': rendererData,
         'menuEnabled': menuEnabled,
         'currentVehicleId': g_currentVehicle.invID}))

    @decorators.process('equipping')
    def equipTankman(self, tmanInvID, slot):
        tankman = g_itemsCache.items.getTankman(int(tmanInvID))
        result = yield TankmanEquip(tankman, g_currentVehicle.item, int(slot)).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def unloadAllTankman(self):
        self.unloadCrew()

    @staticmethod
    @decorators.process('unloading')
    def unloadCrew():
        result = yield TankmanUnload(g_currentVehicle.item).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def openPersonalCase(self, value, tabNumber):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.PERSONAL_CASE, getViewName(VIEW_ALIAS.PERSONAL_CASE, value), {'tankmanID': int(value),
         'page': int(tabNumber)}))
