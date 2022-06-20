import os
import DobotDllType as dType
from logzero import logger
import time


class RobotController(object):
    def __init__(self):
        self.robot = dType.load()
        self.CON_STR = {
        dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}
        state = dType.ConnectDobot(self.robot, "10.6.1.6", 115200)[0]
        logger.debug(f"Connect status:{self.CON_STR[state]} ")
        dType.SetHOMEParams(self.robot, 190, 0, -30, 0)
        dType.SetPTPCommonParams(self.robot, 100, 100)
        dType.SetPTPCoordinateParams(self.robot, 80, 80, 80, 80)
        dType.SetPTPCommonParams(self.robot, 100, 100)
        dType.SetHOMECmd(self.robot, temp = 0)
        # self.swift.set_position(z=60, speed=100, wait=False, timeout=10, cmd='G1')

    def reset(self):
        logger.debug("Resetting the Robot...")
        # dType.SetQueuedCmdStopExec(self.robot)
        dType.SetPTPCmd(self.robot, dType.PTPMode.PTPMOVLXYZMode, 168, 0, -10, 0)
        # dType.SetQueuedCmdClear(self.robot)

    def __click_before(self, coor):
        logger.debug(f"Robot is going to click...")
        dType.SetPTPCmd(self.robot, dType.PTPMode.PTPMOVLXYZMode, coor[0], coor[1], coor[2], 0)
        dType.SetPTPCmd(self.robot, dType.PTPMode.PTPMOVLXYZMode, coor[0], coor[1], coor[2]-5, 0)

    def click(self, coor):
        self.__click_before(coor)
        dType.SetPTPCmd(self.robot, dType.PTPMode.PTPMOVLXYZMode, coor[0], coor[1], coor[2]+20, 0)
        logger.debug(f"Robot Click X: {coor[0]}, Y: {coor[1]}")
        self.reset()

    def doubleclick(self, coor):
        self.__click_before(coor)
        dType.SetPTPCmd(self.robot, dType.PTPMode.PTPMOVLXYZMode, coor[0], coor[1], coor[2], 0)
        self.__click_before(coor)
        dType.SetPTPCmd(self.robot, dType.PTPMode.PTPMOVLXYZMode, coor[0], coor[1], coor[2], 0)
        self.reset()

    def longPress(self, coor):
        dType.SetPTPCmd(self.robot, dType.PTPMode.PTPMOVLXYZMode, coor[0], coor[1], coor[2], 0)
        time.sleep(1)
        dType.SetPTPCmd(self.robot, dType.PTPMode.PTPMOVLXYZMode, coor[0], coor[1], coor[2]+10, 0)
        self.reset()

    def connect(self):
        state = dType.ConnectDobot(self.robot, "10.6.1.6", 115200)[0]
        logger.debug("Connect status:",self.CON_STR[state])
        dType.SetPTPCoordinateParams(self.robot, 80, 80, 80, 80)
        dType.SetPTPCommonParams(self.robot, 100, 100)

    def close_connect(self):
        dType.DisconnectDobot(self.robot)

    def reconnect(self):
        state = dType.ConnectDobot(self.robot, "10.6.1.6", 115200)[0]
        logger.debug("Reconnect status:",self.CON_STR[state])