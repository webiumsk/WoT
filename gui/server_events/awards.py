# Embedded file name: scripts/client/gui/server_events/awards.py
from helpers import i18n
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardAbstract
from gui.Scaleform.framework.managers.TextManager import TextType

class AchievementsAward(AwardAbstract):

    def __init__(self, achieves):
        raise hasattr(achieves, '__iter__') or AssertionError
        self.__achieves = achieves

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWMEDALS)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS_GLOW

    def getHeader(self):
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_QUESTS_MEDALS_HEADER))

    def getDescription(self):
        descr = []
        for achieve in self.__achieves:
            noteInfo = achieve.getNotificationInfo()
            if len(noteInfo):
                descr.append(noteInfo)

        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, '\n\n'.join(descr))

    def getBottomText(self):
        return i18n.makeString(MENU.AWARDWINDOW_OKBUTTON)

    def getExtraFields(self):
        result = []
        for a in self.__achieves:
            result.append({'type': a.getRecordName()[1],
             'block': a.getBlock(),
             'icon': {'big': a.getBigIcon(),
                      'small': a.getSmallIcon()}})

        return {'achievements': result}


class TokensAward(AwardAbstract):

    def __init__(self, tokens):
        raise hasattr(tokens, '__iter__') or AssertionError
        self.__tokens = tokens

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_TOKENS)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_QUESTS_TOKEN256

    def getHeader(self):
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TOKENS_HEADER, count=self.__getTotalTokensCount()))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TOKENS_DESCRIPTION))

    def getBottomText(self):
        return i18n.makeString(MENU.AWARDWINDOW_OKBUTTON)

    def __getTotalTokensCount(self):
        return sum(self.__tokens.values())


class VehicleAward(AwardAbstract):

    def __init__(self, vehicle):
        self.__vehicle = vehicle

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWVEHICLE)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return self.__vehicle.iconUniqueLight

    def getHeader(self):
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_QUESTS_VEHICLE_HEADER, vehicleName=self.__vehicle.userName))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.AWARDWINDOW_QUESTS_VEHICLE_DESCRIPTION))

    def getBottomText(self):
        return i18n.makeString(MENU.AWARDWINDOW_OKBUTTON)


class TankwomanAward(AwardAbstract):

    def __init__(self, questID, tankmanData):
        self.__questID = questID
        self.__tankmanData = tankmanData

    def getWindowTitle(self):
        return i18n.makeString(MENU.AWARDWINDOW_TITLE_NEWTANKMAN)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEORANGE

    def getHeader(self):
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TANKMANFEMALE_HEADER))

    def getDescription(self):
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(MENU.AWARDWINDOW_QUESTS_TANKMANFEMALE_DESCRIPTION))

    def getBottomText(self):
        return i18n.makeString(MENU.AWARDWINDOW_RECRUITBUTTON)

    def handleOkButton(self):
        from gui.server_events import events_dispatcher as quests_events
        quests_events.showTankwomanRecruitWindow(self.__questID, self.__tankmanData.isPremium, self.__tankmanData.fnGroupID, self.__tankmanData.lnGroupID, self.__tankmanData.iGroupID)
