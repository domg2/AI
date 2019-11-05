#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import cv2
import os
import numpy as np
import datetime
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore ,QtWidgets
from threading import Timer,Thread,Event
from ctypes import *


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
            return -3001
        else:
            self.TD_DLL = cdll.LoadLibrary(libNamePath) 

        # self.TD_DLL = windll.LoadLibrary(libNamePath)   # 使用 windll 模块的 LoadLibrary 导入动态链接库
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
            return -1001

    def NL_TD_Process_C(self):
        # 处理函数
        ret = self.TD_DLL.NL_TD_Process(self.djTDHandle, self.djTDVarIn, self.djTDVarOut)
        if ret !=0:
            print("NL_TD_Process error code:",ret)
            return ret
        else:
            print("NL_TD_Process_C done!")
            return int(self.djTDVarOut.dwObjectSize)



    def NL_TD_Exit(self):
        ret = self.TD_DLL.NL_TD_UnloadModel(self.djTDHandle)
        if ret !=0:
            print("NL_TD_UnloadModel error code:",ret)
        return ret




# 线程，算法处理
class workerThread2(QThread):
    updatedImage = QtCore.pyqtSignal(int)
    def __init__(self,mw):
        self.mw = mw
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):        
        QApplication.processEvents()
        while self.mw.isRun:
            if self.mw.AlgIsbasy == False and not (self.mw.limg is None):
                self.mw.AlgIsbasy = True  
                limg = self.mw.limg
                ret = self.mw.nlToyDetect.NL_TD_InitVarIn(limg)
                if ret == 0 :
                    ret = self.mw.nlToyDetect.NL_TD_Process_C() # 返回值是目标个数
                    if ret > 0 :
                        # 显示结果到图片上
                        height, width, bytesPerComponent = limg.shape
                        bytesPerLine = bytesPerComponent * width
                        rgb = cv2.cvtColor(limg, cv2.COLOR_BGR2RGB)
                        for i in range(self.mw.nlToyDetect.djTDVarOut.dwObjectSize):
                            outObject = self.mw.nlToyDetect.djTDVarOut.pdjToyInfors[i]
                            # print("Object ID:",outObject.dwClassID ,"Object name : ",outObject.className,'Score :%0.2f,'%(outObject.fscore),
                            #     'Position: %.2f,%.2f,%.2f,%.2f'%(outObject.dwLeft ,  outObject.dwTop , outObject.dwRight ,outObject.dwBottom ))
                            font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体
                            imgzi = cv2.putText(rgb, str(outObject.className), (int(outObject.dwLeft), int(outObject.dwBottom)), font, 0.8, (255, 0, 0), 2)
                            cv2.rectangle(rgb,(int(outObject.dwLeft), int(outObject.dwTop)),(int(outObject.dwRight),int(outObject.dwBottom )),(0,0,255), 2)     
                        showImage = QImage(rgb.data, width , height, bytesPerLine, QImage.Format_RGB888)
                        self.mw.showImage = QPixmap.fromImage(showImage)
                        self.updatedImage.emit(self.mw.frameID)  
   
                    else:
                        # 显示结果到图片上
                        print('No object:',ret)
                        # print('image shape',limg.shape)
                        height, width, bytesPerComponent = limg.shape
                        bytesPerLine = bytesPerComponent * width
                        rgb = cv2.cvtColor(limg, cv2.COLOR_BGR2RGB)
                        showImage = QImage(rgb.data, width , height, bytesPerLine, QImage.Format_RGB888)
                        self.mw.showImage = QPixmap.fromImage(showImage) 
                        self.updatedImage.emit(self.mw.frameID) 
                else:
                    print('Var Init Error code:',ret)
                    sleep(0.001)
                self.mw.AlgIsbasy = False  
            else:
                sleep(0.001)


# 线程读取摄像机            
class workerThread(QThread): 
    updatedM = QtCore.pyqtSignal(int)
    def __init__(self,mw):
        self.mw = mw
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):    
        QApplication.processEvents()
        while self.mw.isRun:
            if self.mw.CapIsbasy == False :               
                # 采集图像的过程中
                self.mw.CapIsbasy = True              
                ret, image = self.mw.cap.read()     # 获取新的一帧图片
                if ret == False:
                    print("Capture Image Failed")
                    self.mw.isthreadActiv = False
                    self.mw.CapIsbasy = False
                    continue                            
                # print(image.shape)
                img_len = len(image.shape)
                if img_len == 3:
                    self.mw.limg = image
                else:
                    self.mw.limg = cv2.cvtcolor(image, cv2.COLOR_GRAY2BGR)  
                # 可以直接显示线程1的摄像头采集图像，不用线程2             
                # nchannel = image.shape[2]
                # limg2 = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  
                # limage = QtGui.QImage(limg2.data, limg2.shape[1], limg2.shape[0], nchannel*limg2.shape[1], QtGui.QImage.Format_RGB888)  
                # self.mw.showImage = QPixmap.fromImage(limage)     
                self.mw.CapIsbasy=False 
                self.updatedM.emit(self.mw.frameID)
            else:
                sleep(1.0/50)

# 设置qt显示窗口
class VideoBox(QWidget):
    def __init__(self,modelPath,libNamePath,capWidth,capHeight):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.move(0, 0)
        self.pictureLabel = QLabel()
        self.pictureLabel.setObjectName("Picture")
        self.pictureLabel.setScaledContents (True) 

        # 设置按钮组件 QPushButton
        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.stopButtonPressed)

        # 设置按键大小边框 QHBoxLayout
        control_box = QHBoxLayout()
        control_box.setContentsMargins(0, 0, 0, 0)
        control_box.addWidget(self.playButton)

        layout = QVBoxLayout()
        layout.addWidget(self.pictureLabel)
        layout.addLayout(control_box)
        self.setLayout(layout)

        # 设置双线程
        self.frameID = 0   
        self.isRun=True   
        self.CapIsbasy = False
        self.AlgIsbasy = False

        # 设计视频采集参数
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, capWidth)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, capHeight)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.showImage = None
        self.limg = None

        # 调用算法类
        self.modelPath = modelPath  # 模型放置路径信息
        self.libNamePath = libNamePath  # 模型名字
        self.nlToyDetect = NL_ToyDetect(self.libNamePath)
        self.nlToyDetect.NL_TD_ComInit(self.modelPath)    # 初始化


        # 线程1相机采集
        self.wthread = workerThread(self)        
        # self.wthread.updatedM.connect(self.showframe)        
        self.wthread.start()  

        # 线程2算法处理
        self.wthread2 = workerThread2(self)        
        self.wthread2.updatedImage.connect(self.showframe)       
        self.wthread2.start() 

    def showframe(self):
        self.pictureLabel.setPixmap(self.showImage)

    def stopButtonPressed(self):         
        self.isRun = False
        self.cap.release()
        ret = self.nlToyDetect.NL_TD_Exit()    # 初始化
        if ret != 0:
            print('NL_TD_Exit Error code:',ret)
        quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    modelPath = b"/system/AI_example/NL_ToyDetect_NNIE"
    libNamePath = '/system/AI_example/NL_ToyDetect_NNIE/lib/libNL_ToyDetectEnc.so'
    box = VideoBox(modelPath,libNamePath,1280,720)
    # box.showFullScreen()
    box.show()
    sys.exit(app.exec_())
