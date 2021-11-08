import tkinter as tk
import tkinter.font
from logzero import logger
from PIL import Image, ImageTk
from camera_config import setup_camera
import mvsdk
import threading
import numpy as np
import cv2
from robot_control import RobotController

## X: [150, 350] Y: [0,80]


class Controller(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.minsize(640, 740)
        self.root.title('Controller')
        self.robot = RobotController()
        self.robot.reset()
        self.my_font = tkinter.font.Font(family='微软雅黑', size=15)
        self.log_font = tkinter.font.Font(family='微软雅黑', size=10)
        self.hCamera, self.pFrameBuffer = setup_camera()
        self.record_flag = False
        self.log = tk.StringVar()
        self.log.set('')
        # self.real_time_image = self.get_one_picture()
        self.canvas = tk.Canvas(self.root, width=360, height=640)
        self.canvas.place(x=0, y=100)
        self.canvas.bind("<Button-1>", self.click_callback)
        self.im = self.get_one_picture()

        self.image_open = Image.open("2.png")
        self.image = ImageTk.PhotoImage(self.image_open)
        thread1 = CreateThreading(1, "Thread-1", 1, self.update)
        thread1.start()


    def get_one_picture(self):
        # get one frame from camera
        pRawData, FrameHead = mvsdk.CameraGetImageBuffer(self.hCamera, 200)
        mvsdk.CameraImageProcess(self.hCamera, pRawData, self.pFrameBuffer, FrameHead)
        mvsdk.CameraReleaseImageBuffer(self.hCamera, pRawData)

        frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(self.pFrameBuffer)
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = frame.reshape(
            (FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3))

        frame = cv2.resize(frame, (480, 640), interpolation=cv2.INTER_LINEAR)
        frame = frame[::, 100:460]
        frame = cv2.flip(frame, 1, dst=None)
        frame = ImageTk.PhotoImage(Image.fromarray(frame))
        return frame

    def on_closing(self):
        mvsdk.CameraUnInit(self.hCamera)
        mvsdk.CameraAlignFree(self.pFrameBuffer)
        self.root.destroy()
        self.robot.close_connect()
        logger.debug("Robot Disconnected")

    def change_record_status(self):
        if self.record_flag == False:
            self.record_flag = True
            self.log.set("Start Recording")
        else:
            self.record_flag = False
            self.log.set("End Recording")
        logger.debug(self.record_flag)

    def click_callback(self, event):
        x, y = event.x, event.y
        old_str = self.log.get()
        strs = f"Action: Click\tX: {x}\tY: {y}"
        self.log.set(old_str + '\n' + strs)
        x_coor = int((x / 480) * 350) + 150
        y_coor = int((y / 640) * 80)
        self.robot.click([x_coor, y_coor, 60])

    def doubleclick_callback(self, event):
        pass

    def longpress_callback(self, event):
        pass

    def update(self):
        self.real_time_image = self.get_one_picture()
        im = self.real_time_image
        self.canvas.create_image(0, 0, anchor="nw", image=im)
        self.root.after(100, self.update)

    def main(self):
        btn_fg = "#909194"
        btn_bg = "#22222C"
        input_bg = "#393943"
        num_fg = "#DCDCDC"
        btn_w = 185
        btn_h = 100

        btn_re = tk.Button(self.root, text='Record', font=self.my_font, bg=btn_bg, fg=btn_fg, bd=0,
                           command=lambda: self.change_record_status())
        btn_re.place(x=btn_w * 0, y=0, width=btn_w, height=btn_h)
        btn_pl = tk.Button(self.root, text="Replay", font=self.my_font, bg=btn_bg, fg=btn_fg, bd=0)
        btn_pl.place(x=btn_w * 1, y=0, width=btn_w, height=btn_h)

        label = tk.Label(self.root, font=self.log_font, bg=input_bg, bd='9', fg=num_fg, anchor='nw',
                         textvariable=self.log)
        label.place(x=365, y=0, width=300, height=740)

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
