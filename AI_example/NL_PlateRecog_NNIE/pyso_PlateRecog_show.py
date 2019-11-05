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
class Struct_PD_Rect(Structure):
    _fields_ = [("left", c_int), ("top", c_int), ("right", c_int), ("bottom", c_int)]

class Struct_PD_VarIn(Structure):
    _fields_ = [("pubyIm", c_char_p), ("dwWidth", c_int), ("dwHeight", c_int), ("dwChannel", c_int),("dwThredTime", c_int),("djObjRect", Struct_PD_Rect)]

class Struct_PD_VarOut(Structure):
    _fields_ = [("license", c_char * 16), ("color", c_char * 8),("nTime", c_int)]
    

class NL_PlateRecog:
    def __init__(self,libNamePath):

        # 目标动态库
        if not os.path.exists(libNamePath):
            print("Library file not exit!",libNamePath)
            return -1001
        else:
            self.PR_SO = cdll.LoadLibrary(libNamePath) 

        # 指定函数参数类型
        self.PR_SO.LPR_InitEx.argtypes=(c_char_p,)
        self.PR_SO.LPR_InitEx.restype = c_int	
        self.PR_SO.LPR_FileEx.argtypes = (POINTER(Struct_PD_VarIn),POINTER(Struct_PD_VarOut),POINTER(c_int))
        self.PR_SO.LPR_FileEx.restype = c_int	
        self.PR_SO.LPR_UnInitEx.restype = c_int	

        # 初始化结构体变量
        self.djPDVarIn = Struct_PD_VarIn()       # 结构体变量定义
        self.djPDVarOut = Struct_PD_VarOut()     # 结构体变量定义
        self.nRecogNum = c_int(0) 
    
    def NL_PR_ComInit(self,modelPath) :
        ret = self.PR_SO.LPR_InitEx(modelPath)
        if ret !=0:
            print("LPR_InitEx Error Code:",ret)
        return ret
    
    def NL_PR_InitVarIn(self,srcBGR):
        # 输入参数设置
        h, w, c = srcBGR.shape
        self.djPDVarIn.dwChannel = c
        self.djPDVarIn.dwWidth = w
        self.djPDVarIn.dwHeight = h
        self.djPDVarIn.pubyIm = srcBGR.astype(np.uint8).tostring()
        self.djPDVarIn.dwThredTime = 1000
        self.djPDVarIn.djObjRect.left = 10
        self.djPDVarIn.djObjRect.top = 10
        self.djPDVarIn.djObjRect.right = 80
        self.djPDVarIn.djObjRect.bottom = 80   
        if h > 1:
            return 0
        else:
            print("Init VarIn Error!")
            return -3001

    def NL_PR_Process(self):
        # 处理函数
        PointRecogNum = pointer(self.nRecogNum)
        ret = self.PR_SO.LPR_FileEx(self.djPDVarIn, self.djPDVarOut, PointRecogNum)
        if ret !=0:
            print("LPR_FileEx Error Code:",ret)
            return ret
        return int(self.nRecogNum.value)

    def NL_PR_Exit(self):
        ret = self.PR_SO.LPR_UnInitEx()
        if ret !=0:
            print("LPR_UnInitEx Error Code:",ret)
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
        self.nlPlateRecog = NL_PlateRecog(self.libNamePath)
        # 初始化
        ret = self.nlPlateRecog.NL_PR_ComInit(self.modelPath)
        if ret != 0:
            print('NL_PR_ComInit Error code:',ret)

        self.srcBGR=0
        # 调用读图
        if not os.path.exists(srcImgPath):
            print("Image file not exit!",srcImgPath)
            return -3001
        else:
            self.readImg(srcImgPath)
            self.showframe()

    def readImg(self,srcImage):
        # 图片路径信息
        srcImgMat = cv2.imread(srcImage)
        img_len = len(srcImgMat.shape)
        if img_len == 3:
            self.srcBGR = srcImgMat
        else:
            self.srcBGR = cv2.cvtcolor(srcImgMat, cv2.COLOR_GRAY2BGR)
        ret = self.nlPlateRecog.NL_PR_InitVarIn(self.srcBGR)
        if ret != 0:
            print('NL_PR_InitVarIn Error code:',ret)


    def showframe(self):
        # start_time = clock() #datetime.datetime.now()
        ret = self.nlPlateRecog.NL_PR_Process()
        # end_time = clock()   #datetime.datetime.now()
        # s1 = 'Time cost is: {}. '.format(str(end_time - start_time))
        # print(s1)   
        # 显示结果到图片上 
        height, width, bytesPerComponent = self.srcBGR.shape
        bytesPerLine = bytesPerComponent * width
        rgb = cv2.cvtColor(self.srcBGR, cv2.COLOR_BGR2RGB)
        for i in range(self.nlPlateRecog.nRecogNum.value):
            print("Color :",self.nlPlateRecog.djPDVarOut.color , "plate number :",self.nlPlateRecog.djPDVarOut.license.decode())
            font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体
            imgzi = cv2.putText(rgb, str(self.nlPlateRecog.djPDVarOut.color), (int(20), int(50+i*20)), font, 0.8, (0, 0, 255), 1)
            imgzi = cv2.putText(rgb, str(self.nlPlateRecog.djPDVarOut.license.decode()), (int(20), int(100+i*20)), font, 0.8, (0, 0, 255), 1)

        showImage = QImage(rgb.data, width , height, bytesPerLine, QImage.Format_RGB888)
        self.pictureLabel.setPixmap(QPixmap.fromImage(showImage))

    def CloseImg(self):
        ret = self.nlPlateRecog.NL_PR_Exit()
        if ret != 0:
            print('NL_PR_Exit Error code:',ret)     
        quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    srcImg = '/system/AI_example/NL_PlateRecog_NNIE/testDate/5.jpg'
    modelPath = b"/system/AI_example/NL_PlateRecog_NNIE"
    libNamePath = '/system/AI_example/NL_PlateRecog_NNIE/lib/libPlateRecognationEnc.so'
    box = ImageBox(srcImg, modelPath, libNamePath)
    #box.showFullScreen()
    box.show()
    sys.exit(app.exec_())

    










