#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import cv2
import numpy as np
from ctypes import *
# from ctypes import windll
import datetime

so = cdll.LoadLibrary("/usr/lib/libopencv_core.so")

# 结构体定义
class Struct_Handle(Structure):
    _fields_ = [("pvModel", c_void_p),("pvBuf", c_void_p), ("qwBufLen", c_longlong)]

class Struct_PD_VarIn(Structure):
    _fields_ = [("pubyIm", c_char_p), ("dwWidth", c_int), ("dwHeight", c_int), ("dwChannel", c_int)]

class Struct_PD_Rect(Structure):
    _fields_ = [("x", c_int), ("y", c_int), ("width", c_int), ("height", c_int)]

class Struct_PD_VarOut(Structure):
    _fields_ = [("pdwStatus", c_int * 64), ("pfScore", c_float * 64),("pdjPositon", Struct_PD_Rect * 64),("parkNum", c_int)]
    

def Process(inputImg, libNamePath,modelPath,configPath):
    # 目标动态库
    if not os.path.exists(libNamePath):
        print("library file not exit!",libNamePath)
        return -1001
    else:
        PD_SO = cdll.LoadLibrary(libNamePath)    # linux版本

    showResult = False
    # 指定函数参数类型
    PD_SO.NL_PD_Command.argtypes=(POINTER(Struct_Handle),c_char_p)
    PD_SO.NL_PD_Command.restype = c_int	
    PD_SO.NL_PD_Init.argtypes = (POINTER(Struct_Handle),)
    PD_SO.NL_PD_Init.restype = c_int	
    PD_SO.NL_PD_Process.argtypes = (POINTER(Struct_Handle), POINTER(Struct_PD_VarIn), POINTER(Struct_PD_VarOut))
    PD_SO.NL_PD_Process.restype = c_int	
    PD_SO.NL_PD_UnloadModel.argtypes = (POINTER(Struct_Handle),)
    PD_SO.NL_PD_UnloadModel.restype = c_int	

    # 初始化：结构体变量和函数
    ret = 0                            # 返回值
    djPDHandle = Struct_Handle()        # 结构体变量定义
    djPDVarIn = Struct_PD_VarIn()       # 结构体变量定义
    djPDVarOut = Struct_PD_VarOut()     # 结构体变量定义

    if not os.path.exists(configPath) or not os.path.exists(modelPath):
        print("Config or model file not exit!")
        return -2501
    ret = PD_SO.NL_PD_Command(djPDHandle, modelPath, configPath, int(1))
    if ret !=0:
        print("Command error code:",ret)
        return ret
    ret = PD_SO.NL_PD_Init(djPDHandle)
    if ret !=0:
        print("Init error code:",ret)
        return ret

    # 输入参数设置
    if not os.path.exists(inputImg):
        print("Image not exit!")
        return -3001
    else:
        img = cv2.imread(inputImg)
        img_len = len(img.shape)
        if img_len == 3:
            src_RGB = img
        else:
            src_RGB = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    h, w, c = src_RGB.shape
    djPDVarIn.dwChannel = c
    djPDVarIn.dwWidth = w
    djPDVarIn.dwHeight = h
    djPDVarIn.pubyIm = src_RGB.astype(np.uint8).tostring()

    # 处理函数
    ret = PD_SO.NL_PD_Process(djPDHandle, djPDVarIn, djPDVarOut)
    if ret !=0:
        print("Process Error code:",ret)
        return ret
    print(int(djPDVarOut.parkNum))

    # 结果输出
    for i in range(int(djPDVarOut.parkNum)):
        PositionState = djPDVarOut.pdwStatus[i]
        print("Object ID:", i ,'Score :%0.2f,'%(djPDVarOut.pfScore[i]),"State: ", PositionState,
            'Position: %.2f,%.2f,%.2f,%.2f'%(djPDVarOut.pdjPositon[i].x , djPDVarOut.pdjPositon[i].y, 
            djPDVarOut.pdjPositon[i].width, djPDVarOut.pdjPositon[i].height ))
        if(showResult):
            cv2.rectangle(src_RGB,(int(djPDVarOut.pdjPositon[i].x), int(djPDVarOut.pdjPositon[i].y)),
            (int(djPDVarOut.pdjPositon[i].x + djPDVarOut.pdjPositon[i].width), int(djPDVarOut.pdjPositon[i].y +djPDVarOut.pdjPositon[i].height)),(0,255,0), 2)
    if(showResult):
        cv2.imshow("Image", src_RGB)
        cv2.waitKey() 

    ret = PD_SO.NL_PD_UnloadModel(djPDHandle)
    if ret !=0:
        print("UnloadModel Error code:",ret)
        return ret
    return ret

if __name__ == '__main__':
    srcImg = '/system/AI_example/NL_ParkDetector_NNIE/data/3.jpg'
    libNamePath = "/system/AI_example/NL_ParkDetector_NNIE/lib/libNL_ParkDetectorEnc.so"
    modelPath = b"/system/AI_example/NL_ParkDetector_NNIE"
    configPath = b"/system/AI_example/NL_ParkDetector_NNIE/config"
    ret = Process(srcImg,libNamePath, modelPath,configPath)
    print(ret)
    


