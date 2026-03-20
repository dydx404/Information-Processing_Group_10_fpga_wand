import cv2
import numpy as np

cap = cv2.VideoCapture(0)
# ... 初始化设置同上 ...

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame

    # 方法A：大津法自动全局阈值（基于图像直方图）
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 方法B：自适应阈值（考虑局部亮度变化）
    # binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                cv2.THRESH_BINARY, 11, 2)

    # 可选：形态学操作去除噪点
    kernel = np.ones((3,3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # 查找轮廓（斑点）
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 在原图上绘制斑点（用外接圆或边界框）
    result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) if len(frame.shape) != 3 else frame.copy()
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500 or area > 100000:  # 过滤面积
            continue
        # 计算最小外接圆（作为斑点位置和大小）
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        center = (int(x), int(y))
        radius = int(radius)
        cv2.circle(result, center, radius, (0, 0, 255), 2)
        print(f"斑点中心: ({x:.2f}, {y:.2f}), 半径: {radius}")

    cv2.imshow("Adaptive Threshold + Contours", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()