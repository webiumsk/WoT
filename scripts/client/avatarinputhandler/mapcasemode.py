# Embedded file name: scripts/client/AvatarInputHandler/MapCaseMode.py
import functools
from ArtilleryEquipment import ArtilleryEquipment
from AvatarInputHandler.ArtyHitMarker import ArtyHitMarker
from AvatarInputHandler.CallbackDelayer import CallbackDelayer
from AvatarInputHandler.DynamicCameras import StrategicCamera
import BattleReplay
import BigWorld
import CommandMapping
import GUI
import Keys
import Math
from Math import Matrix, Vector2, Vector3
import weakref
from AvatarInputHandler.control_modes import IControlMode, dumpStateEmpty, _createGunMarker, _SuperGunMarker
from ProjectileMover import getCollidableEntities
import SoundGroups
from constants import SERVER_TICK_LENGTH
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from post_processing import g_postProcessing
from items import vehicles, artefacts
import Flock
from constants import AIMING_MODE
import BattleReplay

class _DefaultStrikeSelector(object):
    marker = None

    def __init__(self, position, equipment):
        self.equipment = equipment

    def destroy(self):
        pass

    def processSelection(self, position, reset = False):
        return False

    def processHover(self, position, force = False):
        pass

    def processReplayHover(self):
        pass


class _ArtilleryStrikeSelector(_DefaultStrikeSelector):
    maker = property(lambda self: self.__marker)

    def __init__(self, position, equipment):
        _DefaultStrikeSelector.__init__(self, position, equipment)
        self.hitPosition = position
        myTeam = BigWorld.player().team
        udos = BigWorld.userDataObjects.values()
        myArtyEquipment = [ x for x in udos if isinstance(x, ArtilleryEquipment) and x.team == myTeam ]
        if len(myArtyEquipment) > 1:
            LOG_ERROR('This map has multiple (%d) UDO of ArtilleryEquipment for team %d' % (len(myArtyEquipment), myTeam))
        myArtyEquipment = myArtyEquipment[0]
        self.__artyEquipmentUDO = myArtyEquipment
        self.__marker = ArtyHitMarker(self.__getArtyShotInfo, self.__updateMarkerComponent, self.__getDesiredBombardmentState)
        self.__marker.create()
        self.__marker.enable(None)
        self.__marker.setReloading(0, isReloading=False)
        self.__marker.setupShotParams({'maxDistance': 1000.0,
         'gravity': self.__artyEquipmentUDO.gravity})
        self.__marker.setGUIVisible(True)
        self.processHover(position)
        self.writeStateToReplay()
        return

    def destroy(self):
        self.__marker.destroy()
        self.__marker = None
        return

    def __updateMarkerComponent(self, component):
        component.setupFlatRadialDispersion(self.equipment.areaRadius)

    def __getDesiredBombardmentState(self):
        startPos = self.hitPosition + self.__artyEquipmentUDO.position
        endPos = self.hitPosition
        return (endPos, startPos, self.__artyEquipmentUDO.launchVelocity)

    def __getArtyShotInfo(self):
        launchPosition = self.hitPosition + self.__artyEquipmentUDO.position
        launchVelocity = self.__artyEquipmentUDO.launchVelocity
        gravity = Vector3(0, -self.__artyEquipmentUDO.gravity, 0)
        return (launchPosition, launchVelocity, gravity)

    def processSelection(self, position, reset = False):
        self.hitPosition = position
        if reset:
            return False
        BigWorld.player().setEquipmentApplicationPoint(self.equipment.id[1], self.hitPosition, Vector2(0, 1))
        return True

    def __markerForceUpdate(self):
        self.__marker.update(self.hitPosition, Vector3(0, 0, 1), 10, 1000, None)
        return

    def processHover(self, position, force = False):
        if force:
            self.__marker.setPosition(position)
            BigWorld.callback(SERVER_TICK_LENGTH, self.__markerForceUpdate)
        else:
            self.__marker.update(position, Vector3(0, 0, 1), 10, SERVER_TICK_LENGTH, None)
        self.hitPosition = position
        self.writeStateToReplay()
        return

    def processReplayHover(self):
        replayCtrl = BattleReplay.g_replayCtrl
        _, self.hitPosition, direction = replayCtrl.getGunMarkerParams(self.hitPosition, Math.Vector3(0.0, 0.0, 0.0))
        self.__marker.update(self.hitPosition, Vector3(0, 0, 1), 10, SERVER_TICK_LENGTH, None)
        return

    def writeStateToReplay(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            if self.hitPosition is not None:
                replayCtrl.setConsumablesPosition(self.hitPosition)
        return


class _AreaStrikeSelector(_DefaultStrikeSelector):

    def __init__(self, position, equipment, direction = Vector3(0, 0, 1)):
        _DefaultStrikeSelector.__init__(self, position, equipment)
        self.area = BigWorld.player().createEquipmentSelectedArea(position, Vector3(0, 0, 1), equipment)
        self.direction = direction
        self.__sightUpdateActivity = None
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            self.__sightUpdateActivity = BigWorld.callback(0.0, self.__areaUpdate)
            self.__lastUpdateTime = BigWorld.time()
        self.writeStateToReplay()
        return

    def destroy(self):
        if self.area is not None:
            self.area.destroy()
            self.area = None
        if self.__sightUpdateActivity is not None:
            BigWorld.cancelCallback(self.__sightUpdateActivity)
            self.__sightUpdateActivity = None
        return

    def processSelection(self, position, reset = False):
        direction = Vector2(self.direction.x, self.direction.z)
        direction.normalise()
        BigWorld.player().setEquipmentApplicationPoint(self.equipment.id[1], self.area.position, direction)
        self.writeStateToReplay()
        return True

    def processHover(self, position, force = False):
        self.area.relocate(position, self.direction)
        self.writeStateToReplay()

    def processReplayHover(self):
        replayCtrl = BattleReplay.g_replayCtrl
        _, hitPosition, direction = replayCtrl.getGunMarkerParams(self.area.position, self.direction)
        self.area.setNextPosition(hitPosition, direction)

    def __areaUpdate(self):
        currentTime = BigWorld.time()
        deltaTime = BigWorld.time() - self.__lastUpdateTime
        self.__lastUpdateTime = currentTime
        self.area.update(deltaTime)
        self.__sightUpdateActivity = BigWorld.callback(0.0, self.__areaUpdate)

    def writeStateToReplay(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setConsumablesPosition(self.area.position, self.direction)


class _BomberStrikeSelector(_AreaStrikeSelector):

    def __init__(self, position, equipment):
        _AreaStrikeSelector.__init__(self, position, equipment)
        self.selectingPosition = True

    def processSelection(self, position, reset = False):
        if reset:
            self.selectingPosition = True
            self.direction = Vector3(0, 0, 1)
            _AreaStrikeSelector.processHover(self, position)
            return False
        else:
            if self.selectingPosition:
                self.area.relocate(position, self.direction)
            else:
                return _AreaStrikeSelector.processSelection(self, position)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                if position is not None:
                    replayCtrl.setConsumablesPosition(self.area.position, self.direction)
            self.selectingPosition = False
            return False

    def processHover(self, position, force = False):
        if self.selectingPosition:
            _AreaStrikeSelector.processHover(self, position)
        else:
            self.direction = position - self.area.position
            if self.direction.lengthSquared <= 0.001:
                self.direction = Vector3(0, 0, 1)
            _AreaStrikeSelector.processHover(self, self.area.position)


_STRIKE_SELECTORS = {artefacts.Artillery: _ArtilleryStrikeSelector,
 artefacts.Bomber: _BomberStrikeSelector}

class MapCaseControlMode(IControlMode, CallbackDelayer):
    camera = property(lambda self: self.__cam)
    aimingMode = property(lambda self: self.__aimingMode)
    equipmentID = property(lambda self: self.__equipmentID)
    prevCtlMode = None
    deactivateCallback = None
    __PREFERED_POSITION = 0
    __MODE_NAME = 1
    __AIM_MODE = 2

    def __init__(self, dataSection, avatarInputHandler):
        CallbackDelayer.__init__(self)
        self.__preferredPos = Vector3(0, 0, 0)
        self.__aih = weakref.proxy(avatarInputHandler)
        self.__cam = StrategicCamera.StrategicCamera(dataSection['camera'], None)
        self.__isEnabled = False
        self.__updateInterval = 0.1
        self.__activeSelector = _DefaultStrikeSelector(Vector3(0, 0, 0), None)
        self.__equipmentID = None
        self.__aimingMode = 0
        MapCaseControlMode.prevCtlMode = [Vector3(0, 0, 0), '', 0]
        return

    def create(self):
        self.__cam.create(None)
        self.__cam.setMaxDist()
        self.disable()
        return

    def destroy(self):
        CallbackDelayer.destroy(self)
        self.disable()
        self.__activeSelector = None
        self.__cam.destroy()
        self.__aih = None
        return

    def dumpState(self):
        return dumpStateEmpty()

    def enable(self, **args):
        SoundGroups.g_instance.changePlayMode(2)
        targetPos = args.get('preferredPos', Vector3(0, 0, 0))
        self.__cam.enable(targetPos, args.get('saveDist', True))
        self.__aimingMode = args.get('aimingMode', self.__aimingMode)
        self.setGUIVisible(BigWorld.player().isGuiVisible)
        self.__isEnabled = True
        g_postProcessing.enable('strategic')
        BigWorld.setFloraEnabled(False)
        equipmentID = args.get('equipmentID', None)
        if equipmentID is None:
            self.__activeSelector = _DefaultStrikeSelector(Vector3(0, 0, 0), None)
        else:
            self.activateEquipment(equipmentID)
        return

    def disable(self):
        self.__isEnabled = False
        self.__cam.disable()
        self.__activeSelector.destroy()
        self.__activeSelector = _DefaultStrikeSelector(Vector3(0, 0, 0), None)
        self.setGUIVisible(False)
        g_postProcessing.disable()
        BigWorld.setFloraEnabled(True)
        return

    def handleKeyEvent(self, isDown, key, mods, event = None):
        if not self.__isEnabled:
            raise AssertionError
            cmdMap = CommandMapping.g_instance
            if key == Keys.KEY_LEFTMOUSE and isDown:
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying:
                    return True
                shouldClose = self.__activeSelector.processSelection(self.__getDesiredShotPoint())
                if shouldClose:
                    self.turnOff()
                return True
            if key == Keys.KEY_RIGHTMOUSE and isDown:
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying:
                    return True
                self.__activeSelector.processSelection(self.__getDesiredShotPoint(), True)
                return True
            if cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying:
                    return True
                self.turnOff()
                return True
            if cmdMap.isFiredList((CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT,
             CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT,
             CommandMapping.CMD_CM_CAMERA_ROTATE_UP,
             CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN,
             CommandMapping.CMD_CM_INCREASE_ZOOM,
             CommandMapping.CMD_CM_DECREASE_ZOOM), key):
                dx = dy = dz = 0.0
                if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT):
                    dx = -1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT):
                    dx = 1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_UP):
                    dy = -1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN):
                    dy = 1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_INCREASE_ZOOM):
                    dz = 1.0
                if cmdMap.isActive(CommandMapping.CMD_CM_DECREASE_ZOOM):
                    dz = -1.0
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
                    return True
                self.__cam.update(dx, dy, dz, False if dx == dy == dz == 0.0 else True)
                if dx == dy == dz == 0.0:
                    self.stopCallback(self.__tick)
                else:
                    self.delayCallback(0.0, self.__tick)
                return True
            if cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA, key):
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying:
                    return True
                isDown or MapCaseControlMode.prevCtlMode[MapCaseControlMode.__AIM_MODE] &= -1 - AIMING_MODE.USER_DISABLED
            else:
                MapCaseControlMode.prevCtlMode[MapCaseControlMode.__AIM_MODE] |= AIMING_MODE.USER_DISABLED
        return False

    def handleMouseEvent(self, dx, dy, dz):
        if not self.__isEnabled:
            raise AssertionError
            GUI.mcursor().position = Math.Vector2(0, 0)
            self.__cam.update(dx, dy, dz)
            replayCtrl = BattleReplay.g_replayCtrl
            replayCtrl.isRecording and self.__activeSelector.processHover(self.__getDesiredShotPoint())
        return True

    def onMinimapClicked(self, worldPos):
        self.__cam.teleport(worldPos)
        self.__activeSelector.processHover(worldPos, True)

    def setAimingMode(self, enable, mode):
        if mode == AIMING_MODE.USER_DISABLED:
            return
        if mode == AIMING_MODE.TARGET_LOCK and not enable:
            MapCaseControlMode.prevCtlMode[MapCaseControlMode.__AIM_MODE] &= -1 - mode
        if enable:
            self.__aimingMode |= mode
        else:
            self.__aimingMode &= -1 - mode

    def getAimingMode(self, mode):
        return self.__aimingMode & mode == mode

    def getDesiredShotPoint(self):
        if not self.__isEnabled:
            raise AssertionError
            return self.__aimingMode == 0 and self.__getDesiredShotPoint()
        else:
            return None

    def __getDesiredShotPoint(self):
        defaultPoint = self.__cam.aimingSystem.getDesiredShotPoint(True)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            _, hitPosition, _ = replayCtrl.getGunMarkerParams(defaultPoint, Math.Vector3(0.0, 0.0, 1.0))
            return hitPosition
        return defaultPoint

    def setReloading(self, duration, startTime):
        pass

    def setReloadingInPercent(self, percent):
        pass

    def onRecreateDevice(self):
        marker = self.__activeSelector.marker
        if marker is not None:
            marker.onRecreateDevice()
        return

    def getAim(self):
        return None

    def setGUIVisible(self, isVisible):
        marker = self.__activeSelector.marker
        if marker is not None:
            marker.setGUIVisible(isVisible)
        return

    def isManualBind(self):
        return True

    def updateGunMarker(self, pos, dir, size, relaxTime, collData):
        replayCtrl = BattleReplay.g_replayCtrl
        if not (replayCtrl.isPlaying and self.__isEnabled):
            raise AssertionError
            self.__activeSelector.processReplayHover()

    def turnOff(self, sendStopEquipment = True):
        if sendStopEquipment and MapCaseControlMode.deactivateCallback is not None:
            MapCaseControlMode.deactivateCallback()
            MapCaseControlMode.deactivateCallback = None
        prevMode = MapCaseControlMode.prevCtlMode
        self.__aih.onControlModeChanged(prevMode[MapCaseControlMode.__MODE_NAME], preferredPos=prevMode[MapCaseControlMode.__PREFERED_POSITION], aimingMode=prevMode[MapCaseControlMode.__AIM_MODE], saveDist=True, saveZoom=True)
        self.stopCallback(self.__tick)
        self.__cam.update(0.0, 0.0, 0.0, False)
        return

    def activateEquipment(self, equipmentID):
        equipment = vehicles.g_cache.equipments()[equipmentID]
        strikeSelectorConstructor = _STRIKE_SELECTORS.get(type(equipment))
        if strikeSelectorConstructor is None:
            LOG_ERROR('Cannot use equipment with id', equipmentID)
            return
        else:
            self.__activeSelector.destroy()
            self.__activeSelector = strikeSelectorConstructor(self.__getDesiredShotPoint(), equipment)
            self.__equipmentID = equipmentID
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.setEquipmentID(equipmentID)
            return

    def __tick(self):
        self.__activeSelector.processHover(self.__getDesiredShotPoint())
        return 0.0


def activateMapCase(equipmentID, deactivateCallback):
    inputHandler = BigWorld.player().inputHandler
    if isinstance(inputHandler.ctrl, MapCaseControlMode):
        if MapCaseControlMode.deactivateCallback is not None:
            MapCaseControlMode.deactivateCallback()
        MapCaseControlMode.deactivateCallback = deactivateCallback
        inputHandler.ctrl.activateEquipment(equipmentID)
    else:
        MapCaseControlMode.deactivateCallback = deactivateCallback
        pos = inputHandler.getDesiredShotPoint()
        if pos is None:
            pos = inputHandler.ctrl.camera.aimingSystem.getDesiredShotPoint()
            if pos is None:
                pos = Vector3(0.0, 0.0, 0.0)
        MapCaseControlMode.prevCtlMode = [pos, inputHandler.ctrlModeName, inputHandler.ctrl.aimingMode]
        MapCaseControlMode.setReloading = inputHandler.ctrl.setReloading
        MapCaseControlMode.setReloadingInPercent = inputHandler.ctrl.setReloadingInPercent
        MapCaseControlMode.getAim = inputHandler.ctrl.getAim
        inputHandler.onControlModeChanged('mapcase', preferredPos=pos, aimingMode=AIMING_MODE.USER_DISABLED, equipmentID=equipmentID)
    return


def turnOffMapCase(equipmentID):
    inputHandler = BigWorld.player().inputHandler
    if isinstance(inputHandler.ctrl, MapCaseControlMode):
        if inputHandler.ctrl.equipmentID == equipmentID:
            MapCaseControlMode.deactivateCallback = None
            inputHandler.ctrl.turnOff(False)
    return
