from PIL import Image, ImageTk, ImageSequence
import PIL
import PySimpleGUI as sg
import mvsdk
import cv2
import numpy as np
from camera_config import setup_camera
from logzero import logger
import base64
from io import BytesIO
import io

hCamera, pFrameBuffer = setup_camera()

def start_get_mouse_coor():
    pass

def convert_to_bytes(img, resize=None):
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()

def display_window():
    layout = [
        [sg.Button("Record", expand_x=True), sg.Button("Replay", expand_x=True)],
        [sg.Graph((360, 640), (0, 640), (480, 0), key='IMAGE', enable_events=True, drag_submits=True)],
        # [sg.Image(key='IMAGE', enable_events=True)]
    ]
    window = sg.Window('Step Controller', layout, element_justification='c', margins=(0, 0), element_padding=(0, 0),
                       finalize=True)
    record_flag = False

    while True:
        # 从相机取一帧图片
        try:
            pRawData, FrameHead = mvsdk.CameraGetImageBuffer(hCamera, 200)
            mvsdk.CameraImageProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
            mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)

            # 此时图片已经存储在pFrameBuffer中，对于彩色相机pFrameBuffer=RGB数据，黑白相机pFrameBuffer=8位灰度数据
            # 把pFrameBuffer转换成opencv的图像格式以进行后续算法处理
            frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = frame.reshape(
                (FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3))

            frame = cv2.resize(frame, (480, 640), interpolation=cv2.INTER_LINEAR)
            frame = frame[::, 100:460]
            frame = cv2.flip(frame, 1, dst=None)
            frame = Image.fromarray(frame)
            img_data = convert_to_bytes(frame, resize = False)
            id = window['IMAGE'].draw_image(data=img_data, location=(0,0))

        except mvsdk.CameraException as e:
            if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:
                print("CameraGetImageBuffer failed({}): {}".format(e.error_code, e.message))

        event, values = window.read(timeout=10)
        window['IMAGE'].delete_figure(id)
        # logger.debug(f"{event} {values}")
        if event == sg.WIN_CLOSED:
            mvsdk.CameraUnInit(hCamera)
            mvsdk.CameraAlignFree(pFrameBuffer)
            exit(0)
        elif record_flag == False and event == "Record":
            # start record
            record_flag = True
        elif record_flag == True and event == "Record":
            # end record
            record_flag = False
        elif record_flag == True and event == "IMAGE":
            mouse = values['IMAGE']
            box_x = mouse[0]
            box_y = mouse[1]
            logger.debug(f"X: {box_x}, Y: {box_y}")
        elif event == "Replay":
            # start replay
            print(3)


display_window()