import os
from uarm.wrapper import SwiftAPI
from logzero import logger
import time

class RobotController(object):
    def __init__(self):
        self.swift = SwiftAPI()
        self.move_speed = 80
        self.press_distance = 10 # 按压力度

    def reset(self):
        logger.debug("Robot Reset")
        self.swift.set_position(x=150, y=0, z=100, speed=self.move_speed, wait=False, timeout=10, cmd='G0')
        self.swift.flush_cmd()
        # time.sleep(wait_time)

    def __click_before(self, point):
        self.swift.set_position(x=point[0], y=point[1], z=point[2], speed=self.move_speed, wait=False, timeout=10, cmd='G0')
        self.swift.flush_cmd()
        self.swift.set_position(z=point[2] - 2, speed=self.move_speed, wait=False, timeout=10, cmd='G1')
        self.swift.flush_cmd()

    def click(self, coor):
        self.__click_before(coor)
        self.swift.set_position(x=coor[0], y=coor[1], z=coor[2] + 10, speed=self.move_speed, wait=False, timeout=10, cmd='G0')
        self.swift.flush_cmd()
        logger.debug(f"Robot Click X: {coor[0]}, Y: {coor[1]}")
        self.reset()

    def doubleclick(self, coor):
        self.__click_before(coor)
        self.swift.set_position(x=coor[0], y=coor[1], z=coor[2], speed=self.move_speed, wait=False, timeout=10,
                                cmd='G0')
        self.swift.flush_cmd()
        self.__click_before(coor)
        self.swift.set_position(x=coor[0], y=coor[1], z=coor[2], speed=self.move_speed, wait=False, timeout=10,
                                cmd='G0')
        self.swift.flush_cmd()
        self.reset()

    def longPress(self, coor):
        x = coor[0]
        y = coor[1]
        z = coor[2]
        self.swift.set_position(x=x, y=y, z=z - 5, speed=self.move_speed, wait=False, timeout=10, cmd='G0')
        self.swift.flush_cmd()
        time.sleep(1)
        self.swift.set_position(z=z + self.press_distance, speed=100, wait=False, timeout=10, cmd='G1')
        self.swift.flush_cmd()
        self.reset()

    def close_connect(self):
        self.swift.disconnect()

    def reconnect(self):
        self.swift.connect()