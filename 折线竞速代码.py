import RPi.GPIO as GPIO
import time
import threading
import numpy
import matplotlib.pyplot as plt
import cv2
import numpy as np
import math

''' GPIO 和 PWM 初始化 '''
EA, I2, I1, EB, I4, I3 = (16, 19, 26, 13, 20, 21) # changed
FREQUENCY = 100

GPIO.setmode(GPIO.BCM)
GPIO.setup([EA, I2, I1, EB, I4, I3], GPIO.OUT)
GPIO.output([EA, I2, EB, I3], GPIO.LOW)
GPIO.output([I1, I4], GPIO.HIGH)
    
pwma = GPIO.PWM(EA, FREQUENCY)
pwmb = GPIO.PWM(EB, FREQUENCY)
pwma.start(0)
pwmb.start(0)

''' 摄像头初始化 '''
cap = cv2.VideoCapture(0)

# 其中 sym_axis 是图像竖直对称轴位置，摄像头默认参数横向宽度是 640
sym_axis = 640 / 2
# 经实验，认为应直接将 speed 即占空比拉满，从而增加小车稳定性
speed = 100 # equivalent to PWM's duty

cmd = 0
ret, frame = cap.read()
# cv2.imshow('diplay', frame)
# cv2.imwrite("2.jpeg", frame) 调试代码，输出图片进行检查
print('Ready!')

''' 前进指令 '''
def Straight():
    pwma.ChangeDutyCycle(speed)
    pwmb.ChangeDutyCycle(speed)
    print("Go Straight")

# 决定敏感程度，可见后面两个函数
sensibility = 70

''' 左转指令 '''
# changed by lhc !
# suppose that pwma and pwmb is for the left and right respectively
# note that speed is 100
def TurnLeft(par):
    print("Turning Left!")
    nspeed = speed + par / 320.0 * sensibility
    if nspeed > 100.0:
        pwmb.ChangeDutyCycle(100.0)
        pwma.ChangeDutyCycle(speed*((320-par)/320))
    else:   
        pwmb.ChangeDutyCycle(nspeed)
        pwma.ChangeDutyCycle(speed)

''' 右转指令 '''
def TurnRight(par):
    print("Turning Right!")
    nspeed = speed + par / 320.0 * sensibility
    if nspeed > 100.0:
        pwma.ChangeDutyCycle(100.0)
        pwmb.ChangeDutyCycle(speed*((320-par)/320))
    else:
        pwma.ChangeDutyCycle(nspeed)
        pwmb.ChangeDutyCycle(speed)

def Stop():
    pwma.stop()
    pwmb.stop()
    GPIO.cleanup()
    print('Out of the Way')

# 获取最长黑色区间，将其视作图像这一行的引导线位置
def get_longest_interval(row, aimcolor, size = 640):
    i = 0
    j = 0
    mxlen = 0
    resl = -1
    resr = -1
    while i != size:
        if row[i] == aimcolor:
            j = i
            while j != size and row[j] == aimcolor:
                j += 1
            # print(aimcolor, "interval: ", i, j - 1)
            if j - i > mxlen:
                mxlen = j - i
                resl, resr = i, j
            i = j
        else:
            i = i + 1
    return resl, resr

# img is 480*640 2D-array
def calculate_center(img):
    # 转化至 YCrCb 色彩空间
    imgYCrCB = cv2.cvtColor (img , cv2.COLOR_BGR2YCrCb)
    # 提取 Cr 通道下的结果，据此进行黑白二值化
    Y, Cr, Cb = cv2.split(imgYCrCB)
    
    # 二值化时针对像素的阈值，经实验认为 133 最佳
    thres = 133 # to be changed when needed
    retval, binCr = cv2.threshold(Cr, thres, 255, cv2.THRESH_BINARY_INV)

    # 取某一行的结果，扫一遍计算引导线的中心
    # 195 考核时改了，具体可见报告
    row = binCr[195]
    wl, wr = get_longest_interval(row, 0)

    if wl == -1: # 防“意外”
        return sym_axis
    # 返回区间中点
    return (wl + wr) / 2

# cur_center = calculate_center(frame)
# print(cur_center)

cmd = 0

try:
    while (1):
        if (cmd == 0):
            cmd = input()
        else:
            ret, frame = cap.read()  # read one fps
            # cv2.imshow("display", frame)
            # 获取引导线中心
            cur_center = calculate_center(frame)
            # 计算偏离中心的程度，其中 sym_axis 是图像竖直对称轴位置
            delta = cur_center - sym_axis
            print("cur_center=%d, delta=%d" % (cur_center, delta))

            # 对于偏离中心是否要转向的阈值，经实验认为取 10 最佳
            thres = 10
            # 若偏离中心在这一范围内，则不控制转向
            # 否则相应地向右或向左转向
            if (delta < thres and delta > -thres):
                Straight()
            elif (delta > thres):
                TurnRight(delta)
            elif (delta < -thres):
                TurnLeft(-delta)
            time.sleep(0)
except KeyboardInterrupt:
    pass

cap.release()  # 释放摄像头
cv2.destroyAllWindows()  # 关闭所有显示窗体
pwma.stop()
pwmb.stop()
GPIO.cleanup()
