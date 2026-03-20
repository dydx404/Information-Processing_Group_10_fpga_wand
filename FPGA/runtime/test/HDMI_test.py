from pynq.overlays.base import BaseOverlay
from pynq.lib.video import *
base = BaseOverlay("base.bit")
Mode = VideoMode(640,480,24)
hdmi_out = base.video.hdmi_out
hdmi_out.configure(Mode, PIXEL_BGR)
hdmi_out.start()

import os
os.environ["OPENCV_LOG_LEVEL"]="SILENT"
import cv2
import numpy as np

videoIn = cv2.VideoCapture(0)
# --- 关键步骤1：设置分辨率和格式 ---
videoIn.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
videoIn.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
videoIn.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# --- 关键步骤2：关闭自动曝光，以便手动控制 ---
# 注意：不同摄像头auto_exposure的值可能不同，常见为0.25或1表示手动模式
videoIn.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) 

# --- 关键步骤3：设置一个初始曝光值 (数值范围取决于摄像头) ---
initial_exposure = 100
videoIn.set(cv2.CAP_PROP_EXPOSURE, initial_exposure)

print("capture device is open: " + str(videoIn.isOpened()))

# 假设我们想要在某个时刻增加曝光
exposure_value = initial_exposure

while(True):
    ret, frame_vga = videoIn.read()
    if (ret):
        outframe = hdmi_out.newframe()
        outframe[:] = frame_vga
        hdmi_out.writeframe(outframe)

        # --- 示例：动态调整曝光（比如每100帧增加一点）---
        # 这里只是一个简单的例子，实际应用中可以根据图像亮度分析、外部命令等触发
        # if some_condition:
        #     exposure_value += 10
        #     videoIn.set(cv2.CAP_PROP_EXPOSURE, exposure_value)
        #     print(f"设置曝光为: {exposure_value}")

    else:
        # 如果偶尔读不到帧，不要直接抛出异常退出，可以加个continue或简单跳过
        # raise RuntimeError("Error while reading from camera.")
        pass 
