import tkinter as tk
import tkinter.font
from logzero import logger
from PIL import Image, ImageTk

class Controller(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.minsize(780, 740)
        self.root.title('Controller')
        self.my_font = tkinter.font.Font(family='微软雅黑', size=15)
        self.log_font = tkinter.font.Font(family='微软雅黑', size=10)
        self.record_flag = False
        self.log = tk.StringVar()
        self.log.set('')
        self.image_open = Image.open("2.png")
        self.image = ImageTk.PhotoImage(self.image_open)

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

    def doubleclick_callback(self, event):
        pass

    def longpress_callback(self, event):
        pass

    def main(self):
        btn_fg = "#909194"
        btn_bg = "#22222C"
        input_bg = "#393943"
        num_fg = "#DCDCDC"
        btn_w = 240
        btn_h = 100

        label = tk.Label(self.root, font=self.log_font, bg=input_bg, bd='9', fg=num_fg, anchor='nw',
                              textvariable=self.log)
        label.place(x=480, y = 0, width = 300, height=740)
        pic = tk.Label(self.root, image = self.image)
        pic.bind("<Button-1>", self.click_callback)
        pic.place(x = 0, y = 400)

        btn_re = tk.Button(self.root, text = 'Record', font=self.my_font, bg=btn_bg, fg=btn_fg, bd=0,
                           command = lambda:self.change_record_status())
        btn_re.place(x=btn_w * 0, y=0, width=btn_w, height=btn_h)
        btn_pl = tk.Button(self.root, text = "Replay", font = self.my_font, bg = btn_bg, fg = btn_fg, bd = 0)
        btn_pl.place(x=btn_w * 1, y=0, width=btn_w, height=btn_h)

        self.root.mainloop()


if __name__ == "__main__":
    ctl = Controller()
    ctl.main()