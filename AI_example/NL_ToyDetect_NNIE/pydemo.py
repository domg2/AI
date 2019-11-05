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

class Struct_TD_VarIn(Structure):
    _fields_ = [("pubyIm", c_char_p), ("dwWidth", c_int), ("dwHeight", c_int), ("dwChannel", c_int)]

class Struct_TD_ObjInfor(Structure):
    _fields_ = [("dwClassID", c_int), ("dwLeft", c_int), ("dwTop", c_int), ("dwRight", c_int),
                ("dwBottom", c_int), ("fscore", c_float), ("className", c_char * 50)]

class Struct_TD_VarOut(Structure):
    _fields_ = [("dwObjectSize", c_int), ("pdjToyInfors", Struct_TD_ObjInfor * 128)]
    

def Process(inputImg, libNamePath,modelPath):
    # 目标动态库
    if not os.path.exists(libNamePath):
        print("Library file not exit!",libNamePath)
        return -1001
    else:
        TD_SO = cdll.LoadLibrary(libNamePath)    # linux版本
    # 指定函数参数类型
    TD_SO.NL_TD_Command.argtypes=(POINTER(Struct_Handle),c_char_p)
    TD_SO.NL_TD_Command.restype = c_int	
    TD_SO.NL_TD_Init.argtypes = (POINTER(Struct_Handle),)
    TD_SO.NL_TD_Init.restype = c_int	
    TD_SO.NL_TD_Process.argtypes = (POINTER(Struct_Handle), POINTER(Struct_TD_VarIn), POINTER(Struct_TD_VarOut))
    TD_SO.NL_TD_Process.restype = c_int	
    TD_SO.NL_TD_UnloadModel.argtypes = (POINTER(Struct_Handle),)
    TD_SO.NL_TD_UnloadModel.restype = c_int	

    # 初始化：结构体变量和函数
    ret = 0                            # 返回值
    djTDHandle = Struct_Handle()        # 结构体变量定义
    djTDVarIn = Struct_TD_VarIn()       # 结构体变量定义
    djTDVarOut = Struct_TD_VarOut()     # 结构体变量定义

    if not os.path.exists(modelPath):
        print("Model file not exit!",modelPath)
        return -3501
    ret = TD_SO.NL_TD_Command(djTDHandle, modelPath)
    if ret !=0:
        print("NL_TD_Command error code:",ret)
        return ret
    ret = TD_SO.NL_TD_Init(djTDHandle)
    if ret !=0:
        print("NL_TD_Init error code:",ret)
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
    djTDVarIn.dwChannel = c
    djTDVarIn.dwWidth = w
    djTDVarIn.dwHeight = h
    djTDVarIn.dwPreNum = 5      # 预测结果Top输出
    djTDVarIn.pubyIm = src_RGB.astype(np.uint8).tostring()

    # 处理函数
    # start_time = datetime.datetime.now()
    ret = TD_SO.NL_TD_Process(djTDHandle, djTDVarIn, djTDVarOut)
    # end_time = datetime.datetime.now()
    # s1 = 'Time cost is: {}. '.format(str(end_time - start_time))
    # print(s1)
    if ret !=0:
        print("NL_TD_Process error code:",ret)
        return ret
    # print(djTDVarOut.dwObjectSize)

    # 结果输出
    for i in range(djTDVarOut.dwObjectSize):
        outObject = djTDVarOut.pdjToyInfors[i]
        print("Object ID:",outObject.dwClassID ,"Object name : ",outObject.className,'Score :%0.2f,'%(outObject.fscore),
            'Position: %.2f,%.2f,%.2f,%.2f'%(outObject.dwLeft ,  outObject.dwTop , outObject.dwRight ,outObject.dwBottom ))
    
    ret = TD_SO.NL_TD_UnloadModel(djTDHandle)
    return ret

if __name__ == '__main__':
    srcImg = '/system/AI_example/NL_ToyDetect_NNIE/data/IMG_20190809_171030.jpg'
    modelPath = b"/system/AI_example/NL_ToyDetect_NNIE"
    libNamePath = "/system/AI_example/NL_ToyDetect_NNIE/lib/libNL_ToyDetectEnc.so"
    # start_time = datetime.datetime.now()
    ret = Process(srcImg,libNamePath, modelPath)
    # end_time = datetime.datetime.now()
    # s1 = 'Time cost is: {}. '.format(str(end_time - start_time))
    # print(s1)
    


