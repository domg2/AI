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

class Struct_TC_VarIn(Structure):
    _fields_ = [("pubyIm", c_char_p), ("dwWidth", c_int), ("dwHeight", c_int), ("dwChannel", c_int), ("dwPreNum", c_int)]

class Struct_TC_VarOut(Structure):
    _fields_ = [("dwNum", c_int),("dsClassName", c_char * 50 *5), ("dqScores", c_float * 5)]


def Process(inputImg, libNamePath,modelPath):
    # 目标动态库
    if not os.path.exists(libNamePath):
        print("library file not exit!",libNamePath)
        return -1001
    else:
        TC_SO = cdll.LoadLibrary(libNamePath)    # linux版本

    # 指定函数参数类型
    TC_SO.NL_TC_Command.argtypes=(POINTER(Struct_Handle),c_char_p)
    TC_SO.NL_TC_Init.argtypes = (POINTER(Struct_Handle),)
    TC_SO.NL_TC_Process.argtypes = (POINTER(Struct_Handle), POINTER(Struct_TC_VarIn), POINTER(Struct_TC_VarOut))
    TC_SO.NL_TC_UnloadModel.argtypes = (POINTER(Struct_Handle),)


    # 初始化：结构体变量和函数
    ret = 0                            # 返回值
    djTCHandle = Struct_Handle()        # 结构体变量定义
    djTCVarIn = Struct_TC_VarIn()       # 结构体变量定义
    djTCVarOut = Struct_TC_VarOut()     # 结构体变量定义
 
    if not os.path.exists(modelPath):
        print("Model file not exit!")
        return -3501     
    ret = TC_SO.NL_TC_Command(djTCHandle, modelPath)
    if ret !=0:
        print("NL_TC_Command error code:",ret)
        return ret

    ret = TC_SO.NL_TC_Init(djTCHandle)
    if ret !=0:
        print("NL_TC_Init error code:",ret)
        return ret

    # 输入参数设置
    if not os.path.exists(inputImg):
        print("Image file not exit!")
        return -3001
    else:
        img = cv2.imread(inputImg)
        img_len = len(img.shape)
        if img_len == 3:
            src_RGB = img
        else:
            src_RGB = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    h, w, c = src_RGB.shape
    djTCVarIn.dwChannel = c
    djTCVarIn.dwWidth = w
    djTCVarIn.dwHeight = h
    djTCVarIn.dwPreNum = 5      # 预测结果Top输出
    djTCVarIn.pubyIm = src_RGB.astype(np.uint8).tostring()

    # 处理函数
    ret = TC_SO.NL_TC_Process(djTCHandle, djTCVarIn, djTCVarOut)
    if ret !=0:
        print("NL_TC_Process error code:",ret)
        return ret
    # print(djTCVarOut.dwNum)

    # 结果输出
    for i in range(djTCVarOut.dwNum):
        print("Top ",int(i+1)," Class : ",str(djTCVarOut.dsClassName[i].value),"Accuracy: ",djTCVarOut.dqScores[i])

    ret = TC_SO.NL_TC_UnloadModel(djTCHandle)
    if ret !=0:
        print("NL_TC_UnloadModel error code:",ret)
    return ret


if __name__ == '__main__':
    srcImg = '/system/AI_example/NL_ToyClassify_NNIE/data/20190809_IMG_1355_2.jpg'
    libNamePath = "/system/AI_example/NL_ToyClassify_NNIE/lib/libNL_ToyClassifyEnc.so"
    modelPath = b"/system/AI_example/NL_ToyClassify_NNIE"
    ret = Process(srcImg,libNamePath, modelPath)
    print(ret)
    


