#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import cv2
import numpy as np
import datetime
from time import *
from ctypes import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# 第三方库
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
    

class NL_ToyDetect:
    def __init__(self,libNamePath):

        # 目标动态库
        if not os.path.exists(libNamePath):
            print("Library file not exit!",libNamePath)
            return -1001
        else:
            self.TD_DLL = cdll.LoadLibrary(libNamePath) 

        # 指定函数参数类型
        self.TD_DLL.NL_TD_Command.argtypes=(POINTER(Struct_Handle),c_char_p)
        self.TD_DLL.NL_TD_Command.restype = c_int	
        self.TD_DLL.NL_TD_Init.argtypes = (POINTER(Struct_Handle),)
        self.TD_DLL.NL_TD_Init.restype = c_int	
        self.TD_DLL.NL_TD_Process.argtypes = (POINTER(Struct_Handle), POINTER(Struct_TD_VarIn), POINTER(Struct_TD_VarOut))
        self.TD_DLL.NL_TD_Process.restype = c_int	
        self.TD_DLL.NL_TD_UnloadModel.argtypes = (POINTER(Struct_Handle),)
        self.TD_DLL.NL_TD_UnloadModel.restype = c_int	

        # 初始化结构体变量
        self.djTDHandle = Struct_Handle()        # 结构体变量定义
        self.djTDVarIn = Struct_TD_VarIn()       # 结构体变量定义
        self.djTDVarOut = Struct_TD_VarOut()     # 结构体变量定义
    
    def NL_TD_ComInit(self,modelPath) :
        if not os.path.exists(modelPath):
            print("Model file not exit!",modelPath)
            return -3501    
        else:  
            ret = self.TD_DLL.NL_TD_Command(self.djTDHandle, modelPath)
            if ret !=0:
                print("NL_TD_Command error code:",ret)
                return ret
        ret = self.TD_DLL.NL_TD_Init(self.djTDHandle)
        if ret !=0:
            print("NL_TD_Init error code:",ret)
            return ret
        return ret
    
    def NL_TD_InitVarIn(self,srcBGR):
        # 输入参数设置
        h, w, c = srcBGR.shape
        self.djTDVarIn.dwChannel = c
        self.djTDVarIn.dwWidth = w
        self.djTDVarIn.dwHeight = h
        self.djTDVarIn.dwPreNum = 5      # 预测结果Top输出
        self.djTDVarIn.pubyIm = srcBGR.astype(np.uint8).tostring()   
        if h > 1:
            return 0
        else:
            print("NL_TD_InitVarIn Error!")
            return -3001

    def NL_TD_Process_C(self):
        # 处理函数
        ret = self.TD_DLL.NL_TD_Process(self.djTDHandle, self.djTDVarIn, self.djTDVarOut)
        if ret !=0:
            print("NL_TD_Process error code:",ret)
            return ret
        # print(self.djTDVarOut.dwObjectSize)
        return int(self.djTDVarOut.dwObjectSize)


    def NL_TD_Exit(self):
        ret = self.TD_DLL.NL_TD_UnloadModel(self.djTDHandle)
        if ret !=0:
            print("NL_TD_UnloadModel error code:",ret)
            return ret
        return ret

class ImageBox(QWidget):
    def __init__(self, srcImgPath, modelPath, libNamePath):
        QWidget.__init__(self)
        # 设置显示组件
        self.pictureLabel = QLabel()
        self.pictureLabel.setScaledContents(True)  
        self.pictureLabel.setObjectName("image show")  
        # 设置按钮组件 QPushButton
        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.CloseImg)
        # 设置按键大小边框 QHBoxLayout
        control_box = QHBoxLayout()
        control_box.setContentsMargins(0, 0, 0, 0)
        control_box.addWidget(self.playButton)
        # 设置图形显示窗口未知
        layout = QVBoxLayout()
        layout.addWidget(self.pictureLabel)
        layout.addLayout(control_box)
        self.setLayout(layout)

        # 调用检测类
        self.srcImage = srcImgPath
        self.modelPath = modelPath  # 模型放置路径信息
        self.libNamePath = libNamePath  # 模型名字
        self.nlToyDetect = NL_ToyDetect(self.libNamePath)
        # 初始化
        ret = self.nlToyDetect.NL_TD_ComInit(self.modelPath)
        
        self.srcBGR=0
        # 调用读图
        if not os.path.exists(srcImgPath):
            print("Image file not exit!",srcImgPath)
            return -3001
        else:
            self.readImg(srcImgPath)
            self.showframe()


    def readImg(self,srcImage):
        srcImgMat = cv2.imread(srcImage)
        img_len = len(srcImgMat.shape)
        if img_len == 3:
            self.srcBGR = srcImgMat
        else:
            self.srcBGR = cv2.cvtcolor(srcImgMat, cv2.COLOR_GRAY2BGR)
        ret = self.nlToyDetect.NL_TD_InitVarIn(self.srcBGR)
        if ret != 0:
            print('NL_TD_InitVarIn Error code:',ret)


    def showframe(self):
        # start_time = clock() #datetime.datetime.now()
        ret = self.nlToyDetect.NL_TD_Process_C()
        # end_time = clock()   #datetime.datetime.now()
        # s1 = 'Time cost is: {}. '.format(str(end_time - start_time))
        # print(s1)   
        # 显示结果到图片上
        height, width, bytesPerComponent = self.srcBGR.shape
        bytesPerLine = bytesPerComponent * width
        rgb = cv2.cvtColor(self.srcBGR, cv2.COLOR_BGR2RGB)
        for i in range(self.nlToyDetect.djTDVarOut.dwObjectSize):
            outObject = self.nlToyDetect.djTDVarOut.pdjToyInfors[i]
            print("Object ID:",outObject.dwClassID ,"Object name : ",outObject.className,'Score :%0.2f,'%(outObject.fscore),
                'Position: %.2f,%.2f,%.2f,%.2f'%(outObject.dwLeft ,  outObject.dwTop , outObject.dwRight ,outObject.dwBottom ))
            font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体
            imgzi = cv2.putText(rgb, str(outObject.className), (int(outObject.dwLeft), int(outObject.dwBottom)), font, 0.8, (255, 0, 0), 2)
            green = 50 * ((outObject.dwClassID + 1) % 5)
            blue = 80 * ((outObject.dwClassID +1)% 3)
            red = 30 * ((outObject.dwClassID + 1) % 7)
            cv2.rectangle(rgb,(int(outObject.dwLeft), int(outObject.dwTop)),(int(outObject.dwRight),int(outObject.dwBottom )),(blue,green,red), 2)

        showImage = QImage(rgb.data, width , height, bytesPerLine, QImage.Format_RGB888)
        self.pictureLabel.setPixmap(QPixmap.fromImage(showImage))

    def CloseImg(self):
        ret = self.nlToyDetect.NL_TD_Exit()
        if ret != 0:
            print('NL_TD_Exit Error code:',ret)
        quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    srcImg = '/system/AI_example/NL_ToyDetect_NNIE/data/IMG_20190809_171030.jpg'
    modelPath = b"/system/AI_example/NL_ToyDetect_NNIE"
    libNamePath = '/system/AI_example/NL_ToyDetect_NNIE/lib/libNL_ToyDetectEnc.so'
    box = ImageBox(srcImg, modelPath, libNamePath)
    #box.showFullScreen()
    box.show()
    sys.exit(app.exec_())

    










