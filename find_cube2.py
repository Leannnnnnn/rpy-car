import cv2
import numpy as np

def detect_color(frame):
    # 将BGR图像转换为HSV图像
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 定义颜色范围
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([255, 30, 255])

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    lower_orange = np.array([10, 100, 100])
    upper_orange = np.array([20, 255, 255])

    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([120, 255, 255])

    lower_green = np.array([40, 100, 100])
    upper_green = np.array([80, 255, 255])

    # 根据颜色范围创建掩膜
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # 合并所有颜色的掩膜
    mask = mask_red + mask_orange

    # 使用掩膜找到颜色块
    _,contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 初始化最大颜色块的信息
    max_area = 0
    max_contour = None

    # 遍历找到的颜色块
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 250:  # 只考虑宽度大于250的颜色块
            if area > max_area:
                max_area = area
                max_contour = contour

    # 绘制最大颜色块
    if max_contour is not None:
        x, y, w, h = cv2.boundingRect(max_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 获取颜色块的中心坐标
        cx = int(x + w / 2)
        cy = int(y + h / 2)
	
        color_id = 0
        # 根据中心坐标判断颜色
        if mask_yellow[cy, cx] != 0:
            color_id = 1
        elif mask_white[cy, cx] != 0:
            color_id = 2
        elif mask_red[cy, cx] != 0:
            color_id = 3
        elif mask_orange[cy, cx] != 0:
            color_id = 4
        elif mask_blue[cy, cx] != 0:
            color_id = 5
        elif mask_green[cy, cx] != 0:
            color_id = 6

        # 在图像上标注颜色编号
        cv2.putText(frame, str(color_id), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)

    return frame

# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # 调用检测颜色块的函数
    result_frame = detect_color(frame)

    # 显示结果
    cv2.imshow('Color Detection', result_frame)

    # 按ESC键退出循环
    if cv2.waitKey(1) == 27:
        break

# 释放摄像头并关闭窗口
cap.release()
cv2.destroyAllWindows()