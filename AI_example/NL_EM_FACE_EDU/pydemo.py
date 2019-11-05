#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import cv2
import numpy as np
from ctypes import *
import datetime

so = cdll.LoadLibrary("/usr/lib/libopencv_core.so")

# 结构体定义
class FaceRect(Structure):
    _fields_ = [("x1", c_float), ("y1", c_float), ("x2", c_float), ("y2", c_float), ("score", c_float)]

class FacePts(Structure):
    _fields_ = [("x", c_float*5 ), ("y", c_float*5)]

class FaceInfo(Structure):
    _fields_ = [("bbox", FaceRect ), ("regression", c_float*4), ("facePts", FacePts),("quality", c_float),("good", c_bool),
                ("track", c_bool), ("chn", c_int), ("dev", c_int) ,("src", c_char_p),("img_w", c_int),("img_h", c_int)]

class NLDJ_EM_Handle(Structure):
    _fields_ = [("fdModel", c_void_p),("faModel", c_void_p), ("fd_nnie_id", c_int) , ("fe_nnie_id", c_int) ]

class NLDJ_ED_VarIn(Structure):
    _fields_ = [("imgaddr", c_char_p), ("imgWidth", c_int),("imgHeight", c_int),("pyramid", c_char_p),
                ("pydWidth", c_int), ("pydHeight", c_int),("chn", c_int),("dev", c_int)]

class NLDJ_ED_VarOut(Structure):
    _fields_ = [("num", c_uint), ("chn", c_int), ("dev", c_int),("faceInfos", FaceInfo * 255)] 

class NLDJ_EA_VarIn(Structure):
    _fields_ = [("faces", FaceInfo * 255), ("num", c_uint)] 

class NLDJ_EA_VarOut(Structure):
    _fields_ = [("faces", FaceInfo * 255), ("num", c_uint)] 

class NLDJ_ER_VarIn(Structure):
    _fields_ = [("faces", FaceInfo * 255), ("num", c_uint)] 

class NLDJ_ER_VarOut(Structure):
    _fields_ = [("faces", FaceInfo * 255), ("features", c_float * 512 *255), ("num", c_uint)] 


############################################################################
def Process(inputImg, libNamePath ,configPath):
    # 目标动态库
    if not os.path.exists(libNamePath):
        print("library file not exit!",libNamePath)
        return -1001
    FD_SO = cdll.LoadLibrary(libNamePath) 
    # 指定函数参数类型
    FD_SO.NL_EA_Init.argtypes=(POINTER(NLDJ_EM_Handle),)
    FD_SO.NL_EA_Init.restype = c_int	
    FD_SO.NL_EA_Process.argtypes = (POINTER(NLDJ_EM_Handle),POINTER(NLDJ_EA_VarIn), POINTER(NLDJ_EA_VarOut))
    FD_SO.NL_EA_Process.restype = c_int	

    FD_SO.NL_EM_Command.argtypes=(POINTER(NLDJ_EM_Handle),c_char_p)
    FD_SO.NL_EM_Command.restype = c_int	
    FD_SO.NL_EM_Exit.argtypes = (POINTER(NLDJ_EM_Handle),)
    FD_SO.NL_EM_Exit.restype = c_int	
    FD_SO.NL_EM_UnloadModel.argtypes = (POINTER(NLDJ_EM_Handle),)
    FD_SO.NL_EM_UnloadModel.restype = c_int	

    FD_SO.NL_ED_Init.argtypes=(POINTER(NLDJ_EM_Handle),)
    FD_SO.NL_ED_Init.restype = c_int	
    FD_SO.NL_ED_Process.argtypes = (POINTER(NLDJ_EM_Handle),POINTER(NLDJ_ED_VarIn), POINTER(NLDJ_ED_VarOut))
    FD_SO.NL_ED_Process.restype = c_int	

    FD_SO.NL_ER_Init.argtypes=(POINTER(NLDJ_EM_Handle),)
    FD_SO.NL_ER_Init.restype = c_int	
    FD_SO.NL_ER_Process.argtypes = (POINTER(NLDJ_EM_Handle),POINTER(NLDJ_ER_VarIn), POINTER(NLDJ_ER_VarOut))
    FD_SO.NL_ER_Process.restype = c_int	

    FD_SO.NL_EC_Process.argtypes=((c_float* 512), (c_float* 512), POINTER(c_float))
    FD_SO.NL_EC_Process.restype = c_int	

    # 初始化：结构体变量和函数
    ret = 0                            # 返回值
    djEMHandle = NLDJ_EM_Handle()     # 结构体变量定义
    djEAVarIn = NLDJ_EA_VarIn()       # 结构体变量定义
    djEAVarOut = NLDJ_EA_VarOut()     # 结构体变量定义
    djEDVarIn = NLDJ_ED_VarIn()       # 结构体变量定义
    djEDVarOut = NLDJ_ED_VarOut()     # 结构体变量定义
    djERVarIn = NLDJ_ER_VarIn()       # 结构体变量定义
    djERVarOut = NLDJ_ER_VarOut()     # 结构体变量定义

    if not os.path.exists(configPath):
        print("Config file not exit!",configPath)
        return -2501
    ret = FD_SO.NL_EM_Command(djEMHandle, configPath)
    if ret !=0:
        print("Command Error Code:",ret)
        FD_SO.NL_EM_Exit(djEMHandle)
        FD_SO.NL_EM_UnloadModel(djEMHandle)
        return ret

    ret = FD_SO.NL_ED_Init(djEMHandle)
    if ret !=0:
        print("ED Init Error Code:",ret)
        FD_SO.NL_EM_Exit(djEMHandle)
        FD_SO.NL_EM_UnloadModel(djEMHandle)        
        return ret

    ret = FD_SO.NL_EA_Init(djEMHandle)
    if ret !=0:
        print("EA Init Error Code:",ret)
        FD_SO.NL_EM_Exit(djEMHandle)
        FD_SO.NL_EM_UnloadModel(djEMHandle)        
        return ret
        
    ret = FD_SO.NL_ER_Init(djEMHandle)
    if ret !=0:
        print("ER Init Error Code:",ret)
        FD_SO.NL_EM_Exit(djEMHandle)
        FD_SO.NL_EM_UnloadModel(djEMHandle)        
        return ret

    # 输入参数设置
    if not os.path.exists(inputImg):
        print("Image file not exit:",ret)
        return -3001
    else:
        img = cv2.imread(inputImg)
        img_len = len(img.shape)
        if img_len == 3:
            src_RGB = img
        else:
            src_RGB = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # *****************************人脸检测*****************************
    img_h, img_w, img_c = src_RGB.shape
    djEDVarIn.imgaddr = src_RGB.astype(np.uint8).tostring()
    djEDVarIn.imgWidth = img_w
    djEDVarIn.imgHeight = img_h
    djEDVarIn.pyramid = None
    djEDVarIn.chn = 9
    djEDVarIn.dev = 1

    ret = FD_SO.NL_ED_Process(djEMHandle, djEDVarIn, djEDVarOut)
    if ret !=0:
        print("ED Process Error Code:",ret)
        FD_SO.NL_EM_Exit(djEMHandle)
        FD_SO.NL_EM_UnloadModel(djEMHandle)        
        return ret
    else:
        print("NL_ED_Process done!", djEDVarOut.num)
    # 人脸检测结果输出
    for i in range(djEDVarOut.num):
        print("Total face:",djEDVarOut.num ," ID: ",i, 'face box :%0.2f,%0.2f,%0.2f,%0.2f'%(djEDVarOut.faceInfos[i].bbox.x1,
        djEDVarOut.faceInfos[i].bbox.y1, djEDVarOut.faceInfos[i].bbox.x2, djEDVarOut.faceInfos[i].bbox.y2),
            'Scores: %f'%(djEDVarOut.faceInfos[i].bbox.score),"quality: ",djEDVarOut.faceInfos[i].quality,
    	djEDVarOut.faceInfos[i].good,djEDVarOut.faceInfos[i].track,djEDVarOut.faceInfos[i].chn,djEDVarOut.faceInfos[i].dev,
    	" imgw: ",djEDVarOut.faceInfos[i].img_w," imgh: ",djEDVarOut.faceInfos[i].img_h)
    
    # *************************** 人脸对齐 *****************************
    djEAVarIn.num = djEDVarOut.num
    for i in range(djEDVarOut.num):
        djEAVarIn.faces[i] = djEDVarOut.faceInfos[i]
    
    ret = FD_SO.NL_EA_Process(djEMHandle, djEAVarIn, djEAVarOut)
    if ret !=0:
        print("EA Process Error Code:",ret)
        FD_SO.NL_EM_Exit(djEMHandle)
        FD_SO.NL_EM_UnloadModel(djEMHandle)        
        return ret
    else:
        print("NL_EA_Process done!")

    # ***************************  提特征模块  *************************** 
    djERVarIn.num = djEAVarOut.num
    for i in range(djEAVarOut.num):
        djERVarIn.faces[i] = djEAVarOut.faces[i]

    ret = FD_SO.NL_ER_Process(djEMHandle, djERVarIn, djERVarOut)

    if ret !=0:
        print("ER Process Error Code:",ret)
        FD_SO.NL_EM_Exit(djEMHandle)
        FD_SO.NL_EM_UnloadModel(djEMHandle)        
        return ret
    else:
        print("NL_ER_Process done!")

    # ***************************  特征对比  *************************** 
    FaceSimily = c_float(0)
    PointSimily= pointer(FaceSimily)
    ret = FD_SO.NL_EC_Process(djERVarOut.features[0], djERVarOut.features[1], PointSimily)
    print(FaceSimily)

    if ret !=0:
        print("EC Process Error Code:",ret)
        FD_SO.NL_EM_Exit(djEMHandle)
        FD_SO.NL_EM_UnloadModel(djEMHandle)        
        return ret

    FD_SO.NL_EM_Exit(djEMHandle)
    FD_SO.NL_EM_UnloadModel(djEMHandle)        
    return ret

if __name__ == '__main__':
    srcImg = '/system/AI_example/NL_EM_FACE_EDU/data/01010000211000000_32570.jpg'
    configPath = b"/system/AI_example/NL_EM_FACE_EDU/config/config.ini"
    libNamePath = '/system/AI_example/NL_EM_FACE_EDU/lib/libNL_faceEnc.so'  # 模型名字
    # start_time = datetime.datetime.now()
    ret = Process(srcImg,libNamePath, configPath)
    # end_time = datetime.datetime.now()
    # s1 = 'Time cost is: {}. '.format(str(end_time - start_time))
    # print(s1)
    

