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

class Struct_PD_VarIn(Structure):
    _fields_ = [("pubyIm", c_char_p), ("dwWidth", c_int), ("dwHeight", c_int), ("dwChannel", c_int)]

class Struct_PD_Rect(Structure):
    _fields_ = [("x", c_int), ("y", c_int), ("width", c_int), ("height", c_int)]

class Struct_PD_VarOut(Structure):
    _fields_ = [("pdwStatus", c_int * 64), ("pfScore", c_float * 64),("pdjPositon", Struct_PD_Rect * 64),("parkNum", c_int)]
    

class NL_ParkDetect:
    def __init__(self,libNamePath):
        # 目标动态库
        if not os.path.exists(libNamePath):
            print("library file not exit!",libNamePath)
            return -1001

        # 加载动态库so/dll文件
        self.PD_DLL = cdll.LoadLibrary(libNamePath)   # 使用 windll 模块的 LoadLibrary 导入动态链接库
        # 指定函数参数类型
        self.PD_DLL.NL_PD_Command.argtypes=(POINTER(Struct_Handle),c_char_p)
        self.PD_DLL.NL_PD_Command.restype = c_int	
        self.PD_DLL.NL_PD_Init.argtypes = (POINTER(Struct_Handle),)
        self.PD_DLL.NL_PD_Init.restype = c_int	
        self.PD_DLL.NL_PD_Process.argtypes = (POINTER(Struct_Handle), POINTER(Struct_PD_VarIn), POINTER(Struct_PD_VarOut))
        self.PD_DLL.NL_PD_Process.restype = c_int	
        self.PD_DLL.NL_PD_UnloadModel.argtypes = (POINTER(Struct_Handle),)
        self.PD_DLL.NL_PD_UnloadModel.restype = c_int	

        # 初始化结构体变量
        self.djPDHandle = Struct_Handle()        # 结构体变量定义
        self.djPDVarIn = Struct_PD_VarIn()       # 结构体变量定义
        self.djPDVarOut = Struct_PD_VarOut()     # 结构体变量定义

    def NL_PD_ComInit(self,modelPath) :
        if not os.path.exists(modelPath):
            print("Model file not exit!",modelPath)
            return -3501    
        else:   
            ret = self.PD_DLL.NL_PD_Command(self.djPDHandle, modelPath)
            if ret !=0:
                print("NL_PD_Command Error Code:",ret)
            return ret
        ret = self.PD_DLL.NL_PD_Init(self.djPDHandle)
        if ret !=0:
            print("Init Error Code:",ret)
        return ret

    
    def NL_PD_InitVarIn(self,srcBGR):
        # 输入参数设置
        h, w, c = srcBGR.shape
        self.djPDVarIn.dwChannel = c
        self.djPDVarIn.dwWidth = w
        self.djPDVarIn.dwHeight = h
        self.djPDVarIn.dwPreNum = 5      # 预测结果Top输出
        self.djPDVarIn.pubyIm = srcBGR.astype(np.uint8).tostring()   
        if h > 1:
            return 0
        else:
            print("Image VarIn Error!")
            return -1001

    def NL_PD_Process_C(self):
        # 处理函数
        ret = self.PD_DLL.NL_PD_Process(self.djPDHandle, self.djPDVarIn, self.djPDVarOut)
        if ret !=0:
            print("Process error code:",ret)
            return ret
        print(int(self.djPDVarOut.parkNum))
        return int(self.djPDVarOut.parkNum)

    def NL_PD_Exit(self):
        ret = self.PD_DLL.NL_PD_UnloadModel(self.djPDHandle)
        if ret != 0:
            print("Unload error code:",ret)
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
        # 设置图形显示窗口位置
        layout = QVBoxLayout()
        layout.addWidget(self.pictureLabel)
        layout.addLayout(control_box)
        self.setLayout(layout)

        # 调用检测类
        self.srcImage = srcImgPath
        self.modelPath = modelPath  # 模型放置路径信息
        self.libNamePath = libNamePath  # 模型名字
        self.nlParkDetect = NL_ParkDetect(self.libNamePath)
        # 初始化
        ret = self.nlParkDetect.NL_PD_ComInit(self.modelPath)
        if ret != 0:
            print('Init Error code:',ret)

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
        ret = self.nlParkDetect.NL_PD_InitVarIn(self.srcBGR)
        if ret != 0:
            print('InitVarIn error code:',ret)
        return ret
            


    def showframe(self):
        start_time = clock() #datetime.datetime.now()
        ret = self.nlParkDetect.NL_PD_Process_C()
        end_time = clock()   #datetime.datetime.now()
        s1 = 'Time cost is: {}. '.format(str(end_time - start_time))
        print(s1)   

        # 显示结果到图片上
        height, width, bytesPerComponent = self.srcBGR.shape
        bytesPerLine = bytesPerComponent * width
        rgb = cv2.cvtColor(self.srcBGR, cv2.COLOR_BGR2RGB)

        for i in range(int(self.nlParkDetect.djPDVarOut.parkNum)):
            PositionState = self.nlParkDetect.djPDVarOut.pdwStatus[i]
            print("Object ID:", i ,'Score :%0.2f,'%(self.nlParkDetect.djPDVarOut.pfScore[i]),"State: ", PositionState,
                'Position: %.2f,%.2f,%.2f,%.2f'%(self.nlParkDetect.djPDVarOut.pdjPositon[i].x , self.nlParkDetect.djPDVarOut.pdjPositon[i].y, 
                self.nlParkDetect.djPDVarOut.pdjPositon[i].width, self.nlParkDetect.djPDVarOut.pdjPositon[i].height ))
            if int(PositionState) == 0 :
                cv2.rectangle(rgb,(int(self.nlParkDetect.djPDVarOut.pdjPositon[i].x), int(self.nlParkDetect.djPDVarOut.pdjPositon[i].y)),
                    (int(self.nlParkDetect.djPDVarOut.pdjPositon[i].x + self.nlParkDetect.djPDVarOut.pdjPositon[i].width), 
                    int(self.nlParkDetect.djPDVarOut.pdjPositon[i].y +self.nlParkDetect.djPDVarOut.pdjPositon[i].height)),(0,255,0), 2)
            else:
                cv2.rectangle(rgb,(int(self.nlParkDetect.djPDVarOut.pdjPositon[i].x), int(self.nlParkDetect.djPDVarOut.pdjPositon[i].y)),
                    (int(self.nlParkDetect.djPDVarOut.pdjPositon[i].x + self.nlParkDetect.djPDVarOut.pdjPositon[i].width), 
                    int(self.nlParkDetect.djPDVarOut.pdjPositon[i].y +self.nlParkDetect.djPDVarOut.pdjPositon[i].height)),(255,0,0), 2)                

        showImage = QImage(rgb.data, width , height, bytesPerLine, QImage.Format_RGB888)
        self.pictureLabel.setPixmap(QPixmap.fromImage(showImage))

    def CloseImg(self):
        ret = self.nlParkDetect.NL_PD_Exit()
        if ret != 0:
            print('NL_PD_Exit Error code:',ret)
        quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    srcImg = '/system/AI_example/NL_ParkDetector_NNIE/data/3.jpg'
    modelPath = b"/system/AI_example/NL_ParkDetector_NNIE"
    libNamePath = '/system/AI_example/NL_ParkDetector_NNIE/lib/libNL_ParkDetectorEnc.so'
    box = ImageBox(srcImg, modelPath, libNamePath)
    box.showFullScreen()
    box.show()
    sys.exit(app.exec_())

    










