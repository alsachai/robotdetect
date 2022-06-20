import tkinter as tk
import tkinter.font
from logzero import logger
import logzero
from PIL import Image, ImageTk
import threading
import numpy as np
import cv2
from robot_control import RobotController
import time
import json
from utils import send_requests, coordinate_fix, search_contain_box, \
    base64_encode, replay_coordinate_fix

log_format = '%(color)s[%(levelname)1.1s %(module)s:%(lineno)d]%(end_color)s %(message)s'
formatter = logzero.LogFormatter(fmt=log_format)
logzero.setup_default_logger(formatter=formatter)

timer = None
step_path = "../arm_steps/keep-3/"

class Step(object):
    def __init__(self, action, x, y, x_fix, y_fix, screenshot_name):
        self.action = action
        self.x = x
        self.y = y
        self.x_fix = x_fix
        self.y_fix = y_fix
        self.screenshot_name = screenshot_name

    def json_output(self):
        output = {
            "action": self.action,
            "x": self.x,
            "y": self.y,
            "x_fix": self.x_fix,
            "y_fix": self.y_fix,
            "screenshot_name": self.screenshot_name
        }
        return output

class Controller(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.minsize(580, 662)
        self.root.title('Controller')
        self.steps = list()
        self.replay_steps = None
        self.reload_config()
        self.robot = RobotController()
        self.robot.reset()
        self.my_font = tkinter.font.Font(family='微软雅黑', size=10)
        self.log_font = tkinter.font.Font(family='微软雅黑', size=10)

        # init camera
        logger.debug("Loading Camera Drivers...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2340)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        logger.debug("Camera Ready")

        self.record_flag = False
        self.log = tk.StringVar()
        self.log.set('')
        self.canvas = tk.Canvas(self.root, width=348, height=618)
        self.canvas.place(x=0, y=50)
        self.canvas.bind("<Button-1>", self.handleButtonPress)
        self.canvas.bind('<ButtonRelease-1>', self.handleButtonRelease)
        thread1 = CreateThreading(1, "Thread-1", 1, self.update)
        thread1.start()

    def get_one_picture(self):
        _, image = self.cap.read()
        cv2.imwrite("1.jpg", image)
        # transpose逆时针旋转
        image = cv2.transpose(image)
        cv2.imwrite("2.jpg", image)
        # flip 1:水平翻转
        image = cv2.flip(image, 1)
        return image

    def reload_config(self):
        content = json.loads(open("config.json").read())
        logger.debug("Load config successfully!")
        self.record_config, self.replay_config = content['record_config'], content['record_config']

    def on_closing(self):
        self.root.destroy()
        self.robot.close_connect()
        logger.debug("Robot Disconnected")

    def change_record_status(self):
        if self.record_flag == False:
            self.record_flag = True
            self.steps = list()
            self.log.set("Start Recording")
        else:
            self.record_flag = False
            if len(self.steps) > 0:
                output_str = {
                    "steps": list()
                }
                for step in self.steps:
                    output_str['steps'].append(step.json_output())
                output_str_json = json.dumps(output_str, indent=4).encode('utf-8').decode('utf-8')
                with open('steps.json', 'w') as f:
                    print(output_str_json, file = f)
            self.log.set("End Recording")
        logger.debug(self.record_flag)

    def replay(self):
        self.record_flag = False
        steps = json.loads(open("steps.json").read())
        # steps = json.loads(open(step_path + "output.json").read())
        if len(steps) == 0:
            logger.debug("Empty Steps")
            return
        self.replay_steps = steps
        logger.debug("Start Replay")
        thread1 = CreateThreading(2, "Thread-2", 2, self.__replay)
        thread1.start()

    # caculate the relative coordinate on the screen
    def rel_cor(self, bounds, config):
        #emulator attributes
        emu_width = 1080
        emu_length = 2340
        rel_x = int((bounds[1][0] + bounds[0][0])/2)
        rel_y = int((bounds[1][1] + bounds[0][1])/2)
        # x_ratio = rel_x/emu_width
        # y_ratio = rel_y/emu_length
        # screen_left_top = config['screen_left_top']
        # screen_right_bottom = config['screen_right_bottom']
        # screen_length = screen_right_bottom[1] - screen_left_top[1]
        # screen_width = screen_right_bottom[0] - screen_left_top[0]
        # x = screen_left_top[0] + screen_width * x_ratio
        # y = screen_left_top[1] + screen_length * y_ratio
        return rel_x, rel_y

    def __replay(self):
        crop_size = (1080, 2340)
        for step in self.replay_steps:
            print(step)
            logger.debug(f"REPLAY Action: {step['tag']} {step['event_type']} {step['bounds']}")
            screenshot_name = step_path + step['tag']+".jpg"
            record_figure_base64 = base64_encode(screenshot_name)
            # record_figure_base64 = cv2.resize(record_figure_base64, crop_size, interpolation = cv2.INTER_CUBIC)
            realtime_image = self.get_one_picture()
            realtime_image = cv2.resize(realtime_image, crop_size, interpolation = cv2.INTER_CUBIC)
            cv2.imwrite("tmp.jpg", realtime_image)
            replay_figure_base64 = base64_encode("tmp.jpg")
            logger.debug("sending matching request")
            pair_result = send_requests(record_figure_base64, replay_figure_base64)
            logger.debug("matching request received")
            x, y = self.rel_cor(step['bounds'], self.replay_config)
            logger.debug(f"x:{x}, y:{y}")
            pair_x, pair_y = search_contain_box(x, y, pair_result, screenshot_name)
            pair_x_2, pair_y_2 = replay_coordinate_fix(pair_x, pair_y)
            pair_x_2, pair_y_2 = coordinate_fix(pair_x_2, pair_y_2, self.replay_config)
            logger.debug(f"{pair_x} {pair_y} {pair_x_2} {pair_y_2}")
            if step['event_type'] == "touch":
                self.robot.click([pair_x_2, pair_y_2, self.replay_config['height']])
            elif step['action'] == "long_touch":
                self.robot.longPress([pair_x_2, pair_y_2, self.replay_config['height']])
            time.sleep(10)
        logger.debug("Replay Completed")

    def thread_robot_play(self, action, x, y, z):
        if action == "Click":
            self.robot.click([x, y, z])
        elif action == "LongPress":
            self.robot.longPress([x, y, z])

    def clean_steps(self):
        self.steps = []
        self.log.set('')
        logger.debug("Steps Reset")

    def handleButtonPress(self, event):
        global timer
        timer = time.time()

    def handleButtonRelease(self, event):
        global timer
        if (round(time.time() - timer)) > 0.5:
            self.longpress_callback(event)
        else:
            self.click_callback(event)

    def click_callback(self, event):
        x, y = event.x, event.y
        old_str = self.log.get()
        strs = f"Action: Click  X: {x}  Y: {y}"
        self.log.set(old_str + '\n' + strs)
        x_fix, y_fix = coordinate_fix(x, y, self.record_config)
        frame = self.get_one_picture()
        save_name = f"step-{time.strftime('%m%d%H%M%S',time.localtime(time.time()))}.jpg"
        if self.record_flag:
            step = Step("Click", int(x*(1080/348)), int(y*(2340/618)), x_fix, y_fix, save_name)
            self.steps.append(step)
            cv2.imwrite(save_name, frame)
            logger.debug("Click Image Saved")
        thread3 = threading.Thread(name = "Thread-3", target = self.thread_robot_play, args = ("Click", x_fix, y_fix, self.record_config['height']))
        thread3.start()

    def doubleclick_callback(self, event):
        pass

    def longpress_callback(self, event):
        x, y = event.x, event.y
        old_str = self.log.get()
        strs = f"Action: LongPress  X: {x}  Y: {y}"
        self.log.set(old_str + '\n' + strs)
        self.log.set(old_str + '\n' + strs)
        x_fix, y_fix = coordinate_fix(x, y, self.record_config)
        frame = self.get_one_picture()
        save_name = f"step-{time.strftime('%m%d%H%M%S',time.localtime(time.time()))}.jpg"
        if self.record_flag:
            step = Step("LongPress", int(x*(1080/348)), int(y*(2340/618)), x_fix, y_fix, save_name)
            self.steps.append(step)
            cv2.imwrite(save_name, frame)
            logger.debug("LongPress Image Saved")
        thread4 = threading.Thread(name="Thread-4", target=self.thread_robot_play, args=("LongPress", x_fix, y_fix, self.record_config['height']))
        thread4.start()

    def update(self):
        frame = self.get_one_picture()
        frame = cv2.resize(frame, (348, 618), interpolation=cv2.INTER_CUBIC)
        frame = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.real_time_image = frame
        self.canvas.create_image(0, 0, anchor="nw", image=self.real_time_image)
        self.root.after(100, self.update)

    def main(self):
        btn_fg = "#909194"
        btn_bg = "#22222C"
        input_bg = "#393943"
        num_fg = "#DCDCDC"
        btn_w = 173
        btn_h = 25

        btn_re = tk.Button(self.root, text='Record', font=self.my_font, bg=btn_bg, fg=btn_fg, bd=0,
                           command=lambda: self.change_record_status())
        btn_re.place(x=btn_w * 0, y=0, width=btn_w, height=btn_h)
        btn_pl = tk.Button(self.root, text="Replay", font=self.my_font, bg=btn_bg, fg=btn_fg, bd=0,
                           command=lambda: self.replay())
        btn_pl.place(x=btn_w * 1, y=0, width=btn_w, height=btn_h)
        btn_cr = tk.Button(self.root, text="Reset Record Steps", font=self.my_font, bg=btn_bg, fg=btn_fg, bd=0,
                           command=lambda: self.clean_steps())
        btn_cr.place(x=0, y=btn_h * 1, width=btn_w, height=btn_h)
        btn_cr = tk.Button(self.root, text="Reload Config", font=self.my_font, bg=btn_bg, fg=btn_fg, bd=0,
                           command=lambda: self.reload_config())
        btn_cr.place(x=btn_w * 1, y=btn_h * 1, width=btn_w, height=btn_h)

        label = tk.Label(self.root, font=self.log_font, bg=input_bg, bd='9', fg=num_fg, anchor='nw',
                         textvariable=self.log)
        label.place(x=345, y=0, width=300, height=662)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

# 多线程
class CreateThreading(threading.Thread):
    def __init__(self, thread_id, name, counter, call_back):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.call_back = call_back

    def run(self):
        self.call_back()


if __name__ == "__main__":
    ctl = Controller()
    ctl.main()
    ctl.root.mainloop()
