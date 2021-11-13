from robot_control import RobotController
import time

robot = RobotController()
robot.reset()

robot.click([295,34,60])
robot.click([206,57,60])
# robot.click([255,58,60])
time.sleep(2)
robot.click([284,42,60])
time.sleep(0.5)
robot.click([178,12,60])
time.sleep(0.5)
robot.click([240,32,60])
time.sleep(0.5)
robot.click([240,46,60])

robot.close_connect()