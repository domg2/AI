# -*- coding: utf-8 -*- 
'''
颜色特征识别测试代码
'''
import numpy as np
import cv2
import serial
from color_feature import color_block_finder,draw_color_block_rect

def test_color_block_finder_01():
    '''
    色块识别测试样例1 从图片中读取并且识别
    '''
    # 图片路径
    img_path = "../image.png"
    # 颜色阈值下界(HSV) lower boudnary
    lowerb = (174, 150, 126) 
    # 颜色阈值上界(HSV) upper boundary
    upperb = (180, 183, 150)

    # 读入素材图片 BGR
    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    # 检查图片是否读取成功
    if img is None:
        print("Error: 请检查图片文件路径")
        exit(1)

    # 识别色块 获取矩形区域数组
    rects = color_block_finder(img, lowerb, upperb)
    # 绘制色块的矩形区域
    canvas = draw_color_block_rect(img, rects)
    # 在HighGUI窗口 展示最终结果
    cv2.namedWindow('result', flags=cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)
    cv2.imshow('result', canvas)

    # 等待任意按键按下
    cv2.waitKey(0)
    # 关闭其他窗口
    cv2.destroyAllWindows()

def wait_for_what(dev, what):
    while(True):
        line = dev.readline()
        print(line)
        if line.find(what) >= 0:
            break

def control_robot(tty, rect, color):
    (x, y, w, h) = rect
    yy = 7 - (x + w/4 - 155) * 0.64
    xx = 248 - (y + h/4 - 246) * 0.56
    #print("X:" + str(x) + " Y:" + str(y))
    #print("XX:" + str(int(xx)) + " YY:" + str(int(yy)))

    tty.write("G0 X" + str(int(xx)) + " Y" + str(int(yy)) + " Z110 F30000\n")
    wait_for_what(tty, "ok")

    tty.write("G0 X" + str(int(xx)) + " Y" + str(int(yy)) + " Z30 F30000\n")
    wait_for_what(tty, "ok")

    tty.write("M2231 V1\n")
    wait_for_what(tty, "ok")

    tty.write("G0 X" + str(int(xx)) + " Y" + str(int(yy)) + " Z110 F30000\n")
    wait_for_what(tty, "ok")

    if color == 0:
        tty.write("G0 X270 Y100 Z110 F30000\n")
    elif color == 1:
        tty.write("G0 X230 Y120 Z110 F30000\n")
    else:
        tty.write("G0 X100 Y240 Z110 F30000\n")
    wait_for_what(tty, "ok")

    tty.write("M2231 V0\n")
    wait_for_what(tty, "ok")

def test_color_block_finder_02():
    '''
    色块识别测试样例2 从视频流中读取并且识别
    '''
    # 视频路径
    #video_path = 'demo-video.mkv'
    # 颜色阈值下界(HSV) lower boudnary
	# red, green, blue, yellow
    lowerb = [(170, 0, 0), (70, 78, 108), (96, 114, 120), (14, 120, 184)]
    # 颜色阈值上界(HSV) upper boundary
    upperb = [(180, 255, 255), (84, 140, 156), (104, 168, 156), (24, 170, 220)]

    tty = serial.Serial("/dev/ttyACM0",115200)
    wait_for_what(tty, "@5 V1")
    
    # 读入视频流
    cap = cv2.VideoCapture(0)
    # 色块识别结果展示
    cv2.namedWindow('result', flags=cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)

    while(True):
        # 逐帧获取画面
        # ret ？ 画面是否获取成功
        ret, frame = cap.read()

        
        if ret:
            #img = frame
            img = cv2.transpose(frame)
            img = cv2.flip(img, 0)

            index = 0
            while (index < 4):
                # 识别色块 获取矩形区域数组
                # 同时设定最小高度还有宽度，过滤噪声
                rects = color_block_finder(img, lowerb[index], upperb[index],min_w=30,min_h=30)

                # 绘制色块的矩形区域
                canvas = draw_color_block_rect(img, rects)
                # 在HighGUI窗口 展示最终结果 更新画面
                cv2.imshow('result', canvas)

                if len(rects) != 0:
                    break
                index = index + 1

            if len(rects) == 0:
                tty.write("G0 X120 Y0 Z60 F30000\n")
                wait_for_what(tty, "ok")
            else:
                control_robot(tty, rects[0], index)

            count = 0
            while (count < 4):
                cap.read()
                count = count + 1

        else:
            print("视频读取完毕或者视频路径异常")
            break

        # 这里做一下适当的延迟，每帧延时0.1s钟
        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    tty.close()

def test_color_block_finder_03():
    tty = serial.Serial("/dev/ttyACM0",115200)
    wait_for_what(tty, "@5 V1")

    tty.write("G0 X250 Y0 Z130 F10000\n")
    wait_for_what(tty, "ok")

    tty.close()


if __name__ == "__main__":
    # 测试图片色块识别
    #test_color_block_finder_01()
    # 测试视频流色块识别
    test_color_block_finder_02()
	#test_color_block_finder_03()
