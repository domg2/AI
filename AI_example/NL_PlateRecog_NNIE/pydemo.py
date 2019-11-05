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


class Struct_PD_Rect(Structure):
    _fields_ = [("left", c_int), ("top", c_int), ("right", c_int), ("bottom", c_int)]

class Struct_PD_VarIn(Structure):
    _fields_ = [("pubyIm", c_char_p), ("dwWidth", c_int), ("dwHeight", c_int), ("dwChannel", c_int),("dwThredTime", c_int),("djObjRect", Struct_PD_Rect)]

class Struct_PD_VarOut(Structure):
    _fields_ = [("license", c_char * 16), ("color", c_char * 8),("nTime", c_int)]
    

def Process(inputImg, libNamePath,modelPath):
    # 目标动态库
    if not os.path.exists(libNamePath):
        print("library file not exit!",libNamePath)
        return -1001
    else:
        PR_SO = cdll.LoadLibrary(libNamePath)    # linux版本

    # 指定函数参数类型
    PR_SO.LPR_InitEx.argtypes=(c_char_p,)
    PR_SO.LPR_InitEx.restype = c_int	
    PR_SO.LPR_FileEx.argtypes = (POINTER(Struct_PD_VarIn),POINTER(Struct_PD_VarOut),POINTER(c_int))
    PR_SO.LPR_FileEx.restype = c_int	
    # PR_SO.LPR_UnInitEx.argtypes = (POINTER(Struct_Handle),)
    PR_SO.LPR_UnInitEx.restype = c_int	

    # 初始化：结构体变量和函数
    ret = 0                            # 返回值
    djPDVarIn = Struct_PD_VarIn()       # 结构体变量定义
    djPDVarOut = Struct_PD_VarOut()     # 结构体变量定义

    if not os.path.exists(modelPath):
        print("Model file not exit!",modelPath)
        return -3501
    ret = PR_SO.LPR_InitEx(modelPath)
    if ret !=0:
        return ret

    # 输入参数设置
    if not os.path.exists(inputImg):
        print("Image file not exit!",inputImg)
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
    djPDVarIn.dwThredTime = 1000
    djPDVarIn.djObjRect.left = 10
    djPDVarIn.djObjRect.top = 10
    djPDVarIn.djObjRect.right = 80
    djPDVarIn.djObjRect.bottom = 80        
    # 处理函数
    nRecogNum = c_int(0) 
    # start_time = datetime.datetime.now()
    ret = PR_SO.LPR_FileEx(djPDVarIn, djPDVarOut, nRecogNum)
    # end_time = datetime.datetime.now()
    # s1 = 'Time cost is: {}. '.format(str(end_time - start_time))
    # print(s1)
    if ret !=0:
        print("LPR_FileEx Error Code:",ret)
        return ret
    # 结果输出
    for i in range(nRecogNum.value):
        print("Color :",djPDVarOut.color , "plate number :",djPDVarOut.license.decode())

    ret = PR_SO.LPR_UnInitEx()
    if ret !=0:
        print("LPR_UnInitEx Error Code:",ret)
        return ret
    return ret

if __name__ == '__main__':
    srcImg = '/system/AI_example/NL_PlateRecog_NNIE/testDate/5.jpg'
    libNamePath = "/system/AI_example/NL_PlateRecog_NNIE/lib/libPlateRecognationEnc.so"
    modelPath = b"/system/AI_example/NL_PlateRecog_NNIE"
    ret = Process(srcImg,libNamePath, modelPath)
    print(ret)
    

