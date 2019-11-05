#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import cv2
import numpy as np
import datetime
from time import *
from ctypes import * #ctypes是Python的一个外部库，提供和C语言兼容的数据类型，可以很方便地调用C DLL中的函数。
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


# 第三方库,动态库
so = cdll.LoadLibrary("/usr/lib/libopencv_core.so")
# 结构体定义
#对应type https://blog.csdn.net/linda1000/article/details/12623527
class Struct_Handle(Structure):
    #地址，意义不明
    _fields_ = [("pvModel", c_void_p),("pvBuf", c_void_p), ("qwBufLen", c_longlong)]

class Struct_TC_VarIn(Structure):
    _fields_ = [("pubyIm", c_char_p), ("dwWidth", c_int), ("dwHeight", c_int), ("dwChannel", c_int), ("dwPreNum", c_int)]

class Struct_TC_VarOut(Structure):
    _fields_ = [("dwNum", c_int),("dsClassName", c_char * 50 *5), ("dqScores", c_float * 5)]


class NL_ToyClassify:
    #libNamePath = '/system/AI_example/NL_ToyClassify_NNIE/lib/libNL_ToyClassifyEnc.so'
    def __init__(self,libNamePath):
        # 目标动态库
        #os.path模块主要用于文件的属性获取,exists是“存在”的意思，
        # 所以顾名思义，os.path.exists()就是判断括号里的文件是否存在的意思，
        # 括号内的可以是文件路径。

        #不存在时打印libNamePath，返回-1001
        if not os.path.exists(libNamePath):
            print("Library file not exit!",libNamePath)
            return -1001
        else:
            # 加载动态库so/dll文件（'/system/AI_example/NL_ToyClassify_NNIE/lib/libNL_ToyClassifyEnc.so'）
            self.TC_SO = cdll.LoadLibrary(libNamePath)

        # 指定函数参数类型    POINTER指针
        self.TC_SO.NL_TC_Command.argtypes=(POINTER(Struct_Handle),c_char_p)
        self.TC_SO.NL_TC_Init.argtypes = (POINTER(Struct_Handle),)
        self.TC_SO.NL_TC_Process.argtypes = (POINTER(Struct_Handle), POINTER(Struct_TC_VarIn), POINTER(Struct_TC_VarOut))
        self.TC_SO.NL_TC_UnloadModel.argtypes = (POINTER(Struct_Handle),)

        # 初始化结构体变量
        self.djTCHandle = Struct_Handle()        # 结构体变量定义
        self.djTCVarIn = Struct_TC_VarIn()       # 结构体变量定义
        self.djTCVarOut = Struct_TC_VarOut()     # 结构体变量定义

    def NL_TC_ComInit(self,modelPath):
        if not os.path.exists(modelPath):
            print("Model file not exit!",modelPath)
            return -3501
        else:
            ret = self.TC_SO.NL_TC_Command(self.djTCHandle, modelPath)
            if ret !=0:
                print("NL_TC_Command Error Code:",ret)
                return ret
        ret = self.TC_SO.NL_TC_Init(self.djTCHandle)
        if ret !=0:
            print("NL_TC_Init Error Code:",ret)
            return ret
        return ret
    
    def NL_TC_InitVarIn(self,srcBGR):
        # 输入参数设置
        h, w, c = srcBGR.shape
        self.djTCVarIn.dwChannel = c
        self.djTCVarIn.dwWidth = w
        self.djTCVarIn.dwHeight = h
        self.djTCVarIn.dwPreNum = 5      # 预测结果Top输出
        self.djTCVarIn.pubyIm = srcBGR.astype(np.uint8).tostring()   
        if h > 1:
            return 0
        else:
            print("NL_TC_InitVarIn Error!")
            return -1001

    def NL_TC_Process_C(self):
        # 处理函数
        ret = self.TC_SO.NL_TC_Process(self.djTCHandle, self.djTCVarIn, self.djTCVarOut)
        if ret !=0:
            print("NL_TC_Process Error Code:",ret)
            return ret
        # print(self.djTCVarOut.dwNum)
        return int(self.djTCVarOut.dwNum)


    def NL_TC_Exit(self):
        ret = self.TC_SO.NL_TC_UnloadModel(self.djTCHandle)
        if ret !=0:
            print("NL_TC_UnloadModel Error Code:",ret)
            return ret       
        return ret
#继承QWidget类是所有用户界面对象的基类。
class ImageBox(QWidget):
    #构造函数接收，图片，本身，动态链接库
    def __init__(self, srcImgPath, modelPath, libNamePath):
       #https://blog.csdn.net/kilotwo/article/details/79238545
        QWidget.__init__(self)
        # 设置显示组件，PyQt5库
        #标题
        self.pictureLabel = QLabel()
        #Qt图片自适应窗口控件大小（使用setScaledContents）
        self.pictureLabel.setScaledContents(True)
        #标题的名字
        self.pictureLabel.setObjectName("image show")  
        # 设置按钮组件 QPushButton
        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.CloseImg)
        # 设置按键大小边框 QHBoxLayout
        control_box = QHBoxLayout()
        control_box.setContentsMargins(10, 10, 10, 10)
        control_box.setObjectName("Button show")
        control_box.addWidget(self.playButton)
        # 设置图形显示窗口未知
        layout = QVBoxLayout()
        layout.addWidget(self.pictureLabel)
        layout.addLayout(control_box)
        self.setLayout(layout)



        # 调用检测类
        #srcImgPath = 'data/20190809_IMG_1355_2.jpg'
        self.srcImage = srcImgPath
        #modelPath = b"/system/AI_example/NL_ToyClassify_NNIE"
        self.modelPath = modelPath  # 模型放置路径信息
        #libNamePath = '/system/AI_example/NL_ToyClassify_NNIE/lib/libNL_ToyClassifyEnc.so'
        self.libNamePath = libNamePath  # 模型名字
       #调用动态库的方法
        self.nlToyClassify = NL_ToyClassify(self.libNamePath)

        # 初始化，加载动态库或者没有动态库时返回1001
        ret = self.nlToyClassify.NL_TC_ComInit(self.modelPath)
        #实现初始化
        self.srcBGR=0
        # 调用读图
        if not os.path.exists(srcImgPath):
            #图片文件不存在
            print("Image file not exit!",srcImgPath)
            return -3001
        else:
            self.readImg(srcImgPath)
            #调用
            self.showframe()

    def readImg(self,srcImage):
        #用cv2.imread读取灰度图，发现获得的图片为3通道，经查证发现.，
        # cv2.imread()函数默认读取的是一副彩色图片，想要读取灰度图，则需要设置参数。
        srcImgMat = cv2.imread(srcImage)
       #图片长度
        img_len = len(srcImgMat.shape)
        #3个通道，直接使用
        if img_len == 3:
            self.srcBGR = srcImgMat
        #灰度图
        else:
            self.srcBGR = cv2.cvtcolor(srcImgMat, cv2.COLOR_GRAY2BGR)
        ret = self.nlToyClassify.NL_TC_InitVarIn(self.srcBGR)
        if ret != 0:
            print('NL_TC_InitVarIn Error code:',ret)


    def showframe(self):
        # start_time = clock() #datetime.datetime.now()
        ret = self.nlToyClassify.NL_TC_Process_C()
        # end_time = clock()   #datetime.datetime.now()
        # s1 = 'Time cost is: {}. '.format(str(end_time - start_time))
        # print(s1)   
        # 显示结果到图片上    
        height, width, bytesPerComponent = self.srcBGR.shape
        bytesPerLine = bytesPerComponent * width
        rgb = cv2.cvtColor(self.srcBGR, cv2.COLOR_BGR2RGB)
        for i in range(self.nlToyClassify.djTCVarOut.dwNum):
            print("Top ",int(i+1)," Class : ",str(self.nlToyClassify.djTCVarOut.dsClassName[i].value),"Accuracy: ",self.nlToyClassify.djTCVarOut.dqScores[i])
            font = cv2.FONT_HERSHEY_SIMPLEX  # 定义字体
            imgzi = cv2.putText(rgb, str(self.nlToyClassify.djTCVarOut.dsClassName[i].value), (int(20), int(20+i*20)), font, 0.8, (0, 0, 255), 1)
        #
        showImage = QImage(rgb.data, width , height, bytesPerLine, QImage.Format_RGB888)
        self.pictureLabel.setPixmap(QPixmap.fromImage(showImage))

    def CloseImg(self):
        ret = self.nlToyDetect.NL_TD_Exit()
        if ret != 0:
            print('NL_TD_Exit Error code:',ret)
        quit()

if __name__ == '__main__':
    #每一pyqt5应用程序必须创建一个应用程序对象。sys.argv参数是一个列表，从命令行输入参数。
    #http://code.py40.com/2439.html
    app = QApplication(sys.argv)
    #图片
    srcImg = 'data/20190809_IMG_1355_2.jpg'
    #查找自己本身
    modelPath = b"/system/AI_example/NL_ToyClassify_NNIE"
    #动态链接库
    #libNamePath = '/system/AI_example/NL_ToyClassify_NNIE/lib/libNL_ToyClassifyEnc.so'
    libNamePath ="lib/libNL_ToyClassifyEnc.so"
    #调用ImageBox传入图片，本身，动态链接库
    box = ImageBox(srcImg, modelPath, libNamePath)
    #box.showFullScreen()
    box.show()
    #，app.exet_()是指程序一直循环运行直到主窗口被关闭终止进程（如果没有这句话，程序运行时会一闪而过）
    #https://www.cnblogs.com/hexiaoqi/p/10160978.html
    sys.exit(app.exec_())

    










