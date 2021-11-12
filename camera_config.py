import mvsdk
from logzero import logger

def setup_camera():
    DevList = mvsdk.CameraEnumerateDevice()
    nDev = len(DevList)
    if nDev < 1:
        print("No camera was found!")
        return

    for i, DevInfo in enumerate(DevList):
        logger.debug("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
    i = 0 if nDev == 1 else int(input("Select camera: "))
    DevInfo = DevList[i]
    # print(DevInfo)

    # 打开相机
    hCamera = 0
    try:
        hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
    except mvsdk.CameraException as e:
        print("CameraInit Failed({}): {}".format(e.error_code, e.message))
        return

    # 获取相机特性描述
    cap = mvsdk.CameraGetCapability(hCamera)

    # 判断是黑白相机还是彩色相机
    monoCamera = (cap.sIspCapacity.bMonoSensor != 0)

    # 黑白相机让ISP直接输出MONO数据，而不是扩展成R=G=B的24位灰度
    if monoCamera:
        mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
    else:
        mvsdk.CameraSetIspOutFormat(hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

    # 相机模式切换成连续采集
    mvsdk.CameraSetTriggerMode(hCamera, 0)

    # 手动曝光，曝光时间30ms
    # mvsdk.CameraSetAeState(hCamera, 0)
    # mvsdk.CameraSetExposureTime(hCamera, 30 * 1000)
    # mvsdk.CameraSetGamma(hCamera, 40)
    # mvsdk.CameraSetContrast(hCamera, 80)
    # mvsdk.CameraSetSaturation(hCamera, 40)
    # mvsdk.CameraSetSharpness(49)
    # mvsdk.CameraSetWhiteLevel(hCamera, 100)
    # mvsdk.CameraSetBlackLevel(hCamera, 199)
    # mvsdk.CameraSetLightFrequency(hCamera, 100)
    # logger.debug(f"OUTPUT: {mvsdk.CameraGetWhiteLevel(hCamera)}")
    # logger.debug(f"OUTPUT: {mvsdk.CameraGetBlackLevel(hCamera)}")
    # logger.debug(f"OUTPUT: {mvsdk.CameraGetLightFrequency(hCamera)}")
    # 旋转图像
    # mvsdk.CameraSetRotate(hCamera, 1)
    mvsdk.CameraReadParameterFromFile(hCamera, "test.Config")

    # 让SDK内部取图线程开始工作
    mvsdk.CameraPlay(hCamera)

    # 计算RGB buffer所需的大小，这里直接按照相机的最大分辨率来分配
    FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)

    # 分配RGB buffer，用来存放ISP输出的图像
    # 备注：从相机传输到PC端的是RAW数据，在PC端通过软件ISP转为RGB数据（如果是黑白相机就不需要转换格式，但是ISP还有其它处理，所以也需要分配这个buffer）
    pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 32)

    return hCamera, pFrameBuffer