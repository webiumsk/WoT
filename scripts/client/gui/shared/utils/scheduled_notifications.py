# Embedded file name: scripts/client/gui/shared/utils/scheduled_notifications.py
import operator
import BigWorld
from helpers import time_utils
from gui.shared.utils import findFirst, forEach

class Notifiable(object):

    def __init__(self, *args, **kwargs):
        super(Notifiable, self).__init__()
        self.__notificators = []

    def addNotificator(self, notificator):
        self.__notificators.append(notificator)

    def addNotificators(self, *notificators):
        self.__notificators.extend(notificators)

    def startNotification(self):
        forEach(operator.methodcaller('startNotification'), self.__notificators)

    def stopNotification(self):
        forEach(operator.methodcaller('stopNotification'), self.__notificators)

    def clearNotification(self):
        self.stopNotification()
        forEach(operator.methodcaller('clear'), self.__notificators)
        self.__notificators = []


class _Notifier(object):

    def __init__(self, deltaFunc, updateFunc):
        self.__deltaFunc = deltaFunc
        self.__updateFunc = updateFunc
        self.__notificationCallbackID = None
        return

    def clear(self):
        self.__deltaFunc = None
        self.__updateFunc = None
        return

    def startNotification(self):
        self.__cancelNotification()
        self.__processNotification()

    def stopNotification(self):
        self.__cancelNotification()

    def _getNextNotificationDelta(self, delta):
        raise NotImplementedError

    def __processNotification(self):
        delta = self.__deltaFunc()
        if not delta:
            return
        nextNotification = self._getNextNotificationDelta(delta)
        if not nextNotification:
            return
        self.__notificationCallbackID = BigWorld.callback(nextNotification, self.__onNotification)

    def __cancelNotification(self):
        if self.__notificationCallbackID is not None:
            BigWorld.cancelCallback(self.__notificationCallbackID)
            self.__notificationCallbackID = None
        return

    def __onNotification(self):
        self.__notificationCallbackID = None
        self.__updateFunc()
        self.__processNotification()
        return


class PeriodicNotifier(_Notifier):

    def __init__(self, deltaFunc, updateFunc, periods = None):
        super(PeriodicNotifier, self).__init__(deltaFunc, updateFunc)
        self.__periods = periods or (time_utils.ONE_DAY, time_utils.ONE_HOUR, time_utils.ONE_MINUTE)

    def _getNextNotificationDelta(self, delta):
        period = findFirst(lambda p: delta >= p, self.__periods, delta)
        return delta % period or period


class DeltaNotifier(_Notifier):

    def __init__(self, deltaFunc, updateFunc, delta):
        super(DeltaNotifier, self).__init__(deltaFunc, updateFunc)
        self.__delta = delta

    def _getNextNotificationDelta(self, delta):
        if delta >= self.__delta:
            return delta - self.__delta
        return 0
