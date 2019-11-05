#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import cv2
import os
import numpy as np
import datetime
from time import sleep
from ctypes import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore ,QtWidgets
from threading import Timer,Thread,Event

# 第三方库
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

############################################################################

class NL_FaceDetect:
    def __init__(self,libNamePath):
        # 目标动态库
        if not os.path.exists(libNamePath):
            print("Library file not exit!",libNamePath)
            return -3001

        # 加载动态库so/dll文件
        self.FD_SO = cdll.LoadLibrary(libNamePath) 
        # 指定函数参数类型
        self.FD_SO.NL_EM_Command.argtypes=(POINTER(NLDJ_EM_Handle),c_char_p)
        self.FD_SO.NL_EM_Command.restype = c_int	
        self.FD_SO.NL_EM_Exit.argtypes = (POINTER(NLDJ_EM_Handle),)
        self.FD_SO.NL_EM_Exit.restype = c_int	
        self.FD_SO.NL_EM_UnloadModel.argtypes = (POINTER(NLDJ_EM_Handle),)
        self.FD_SO.NL_EM_UnloadModel.restype = c_int	

        self.FD_SO.NL_ED_Init.argtypes=(POINTER(NLDJ_EM_Handle),)
        self.FD_SO.NL_ED_Init.restype = c_int	
        self.FD_SO.NL_ED_Process.argtypes = (POINTER(NLDJ_EM_Handle),POINTER(NLDJ_ED_VarIn), POINTER(NLDJ_ED_VarOut))
        self.FD_SO.NL_ED_Process.restype = c_int	

        # 初始化结构体变量
        self.djEMHandle = NLDJ_EM_Handle()     # 结构体变量定义
        self.djEDVarIn = NLDJ_ED_VarIn()       # 结构体变量定义
        self.djEDVarOut = NLDJ_ED_VarOut()     # 结构体变量定义

    def NL_FD_ComInit(self,modelPath) :
        if not os.path.exists(modelPath):
            print("Config file not exit!",modelPath)
            return -2501
        else:
            ret = self.FD_SO.NL_EM_Command(self.djEMHandle, modelPath)
            if ret !=0:
                print("EM Command Error Code:",ret)
                self.FD_SO.NL_EM_Exit(self.djEMHandle)
                self.FD_SO.NL_EM_UnloadModel(self.djEMHandle)
                return ret
        ret = self.FD_SO.NL_ED_Init(self.djEMHandle)
        if ret !=0:
            print("ED Init Error Code:",ret)
            self.FD_SO.NL_EM_Exit(self.djEMHandle)
            self.FD_SO.NL_EM_UnloadModel(self.djEMHandle)        
            return ret

    
    def NL_FD_InitVarIn(self,srcBGR):
        # 输入参数设置
        h, w, c = srcBGR.shape
        self.djEDVarIn.imgaddr = srcBGR.astype(np.uint8).tostring()
        self.djEDVarIn.imgWidth = w
        self.djEDVarIn.imgHeight = h
        self.djEDVarIn.pyramid = None
        self.djEDVarIn.chn = 9
        self.djEDVarIn.dev = 1   
        if h > 1:
            return 0
        else:
            print("NL_FD_InitVarIn Error!")
            return -1001

    def NL_FD_Process_C(self):
        # 处理函数
        ret = self.FD_SO.NL_ED_Process(self.djEMHandle, self.djEDVarIn, self.djEDVarOut)
        if ret !=0:
            print("ED Process Error Code:",ret)
            self.FD_SO.NL_EM_Exit(self.djEMHandle)
            self.FD_SO.NL_EM_UnloadModel(self.djEMHandle)        
            return ret
        else:
            print("NL_ED_Process done!")
            return int(self.djEDVarOut.num)


    def NL_FD_Exit(self):
        ret1 = self.FD_SO.NL_EM_Exit(self.djEMHandle)
        ret2 = self.FD_SO.NL_EM_UnloadModel(self.djEMHandle) 
        if  ret1 or ret2:
            print("NL_TD_UnloadModel error code:",ret1,ret2)
        return (ret1 or ret2)



# 线程，算法处理
class workerThread2(QThread):
    updatedImage = QtCore.pyqtSignal(int)
    def __init__(self,mw):
        self.mw = mw
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):        
        # QApplication.processEvents()
        while self.mw.isRun:
            if self.mw.AlgIsbasy == False and not (self.mw.limg is None):
                self.mw.AlgIsbasy = True  
                limg = self.mw.limg
                ret = self.mw.nlFaceDetect.NL_FD_InitVarIn(limg)
                if ret == 0 :
                    ret = self.mw.nlFaceDetect.NL_FD_Process_C() # 返回值是目标个数
                    if ret > 0 :
                        # 显示结果到图片上
                        height, width, bytesPerComponent = limg.shape
                        bytesPerLine = bytesPerComponent * width
                        rgb = cv2.cvtColor(limg, cv2.COLOR_BGR2RGB)                         
                        # 人脸检测结果输出
                        for i in range(self.mw.nlFaceDetect.djEDVarOut.num):
                            outObject = self.mw.nlFaceDetect.djEDVarOut.faceInfos[i].bbox
                            print("Total face:",self.mw.nlFaceDetect.djEDVarOut.num ," ID: ",i)
                            print('face box :%0.2f,%0.2f,%0.2f,%0.2f'%(self.mw.nlFaceDetect.djEDVarOut.faceInfos[i].bbox.x1,
                                self.mw.nlFaceDetect.djEDVarOut.faceInfos[i].bbox.y1, 
                                self.mw.nlFaceDetect.djEDVarOut.faceInfos[i].bbox.x2, 
                                self.mw.nlFaceDetect.djEDVarOut.faceInfos[i].bbox.y2))
                            print('Scores: %f'%(self.mw.nlFaceDetect.djEDVarOut.faceInfos[i].bbox.score),
                                " imgw: ",self.mw.nlFaceDetect.djEDVarOut.faceInfos[i].img_w,
                                " imgh: ",self.mw.nlFaceDetect.djEDVarOut.faceInfos[i].img_h )

                            font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体
                            imgzi = cv2.putText(rgb, str('Face'), (int(outObject.x1), int(outObject.y1)), font, 0.8, (255, 0, 0), 2)
                            cv2.rectangle(rgb,(int(outObject.x1), int(outObject.y1)),(int(outObject.x2),int(outObject.y2 )),(0,0,255), 2)                       
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
    def __init__(self, libNamePath,configPath, capWidth,capHeight):
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
        self.configPath = configPath  # 配置文件路径
        self.libNamePath = libNamePath        # 动态库
        self.nlFaceDetect = NL_FaceDetect(self.libNamePath)
        self.nlFaceDetect.NL_FD_ComInit(self.configPath)    # 初始化
    

        # 线程1相机采集
        self.wthread = workerThread(self)        
        # self.wthread.updatedM.connect(self.showframe)        
        self.wthread.start()  

        # 线程2算法处理
        self.wthread2 = workerThread2(self)        
        self.wthread2.updatedImage.connect(self.showframe)       
        self.wthread2.start() 

    def showframe(self):
        self.pictureLabel.setPicture(self.showImage)

    def stopButtonPressed(self):         
        self.isRun = False
        self.cap.release()
        ret = self.nlFaceDetect.NL_FD_Exit()    # 初始化
        if ret != 0:
            print('NL_FD_Exit Error code:',ret)
        quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    configPath = b"/system/AI_example/NL_EM_FACE_EDU/config/config.ini"
    libNamePath = '/system/AI_example/NL_EM_FACE_EDU/lib/libNL_faceEnc.so'  # 模型名字
    box = VideoBox(libNamePath, configPath, 1280, 720)
    # box.showFullScreen()
    box.show()
    sys.exit(app.exec_())
