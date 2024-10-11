import cv2
import numpy as np
import math

def darker_img(img):
    """降低亮度，辅助函数"""
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 转换为 HSV 颜色空间
    hsv_image[:, :, 2] = hsv_image[:, :, 2] * 0.5  # 将 V 通道乘以 0.5
    darker_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)  # 转换回 BGR
    return darker_image

def img_processed(img, val):
    """处理图像，返回二值图像、调整大小和亮度的图像"""    
    img_resized = cv2.resize(img, (640, 480))  # 调整图像大小
    img_dark = cv2.convertScaleAbs(img_resized, alpha=0.5)  # 调整亮度
    image_darker = darker_img(img_dark)  # 降低亮度
    img_gray = cv2.cvtColor(image_darker, cv2.COLOR_BGR2GRAY)  # 转为灰度图
    _, img_binary = cv2.threshold(img_gray, val, 255, cv2.THRESH_BINARY)  # 二值化处理
    cv2.imshow("Binary Image", img_binary)  # 显示二值图像
    return img_dark, img_binary 

def adjust(rect):
    """调整旋转矩形的宽高和角度，使宽始终小于高。辅助函数"""
    c, (w, h), angle = rect
    if w > h:
        w, h = h, w  # 交换宽度和高度
        angle = (angle + 90) % 360  # 调整角度
        angle = angle - 360 if angle > 180 else angle - 180 if angle > 90 else angle  # 标准化角度
    return c, (w, h), angle

def project(polygon, axis):
    """将多边形投影到给定的轴上。辅助函数"""
    return np.dot(polygon, axis).min(), np.dot(polygon, axis).max()  # 计算最小值和最大值

def is_coincide(a, b):
    """使用分离轴定理检查两个多边形是否相交。辅助函数"""
    for polygon in (a, b):
        for i in range(len(polygon)):
            p1, p2 = polygon[i], polygon[(i + 1) % len(polygon)]  # 获取边的两个端点
            normal = (p2[1] - p1[1], p1[0] - p2[0])  # 计算法向量
            min_a, max_a = project(a, normal)  # 计算投影的最小值和最大值
            min_b, max_b = project(b, normal)  # 计算投影的最小值和最大值
            if max_a < min_b or max_b < min_a:  # 检查是否相交
                return False

def find_light(img_binary, img, mode):
    """查找图像中的光源并返回旋转矩形。"""
    contours, _ = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓
    
    # 过滤条件合并为一个列表理解式
    lights_filtered = [
        adjust(cv2.minAreaRect(contour)) for contour in contours 
        if cv2.contourArea(contour) > 5 and -30 <= adjust(cv2.minAreaRect(contour))[2] <= 30  # 过滤小轮廓
    ]
    
    # 进一步过滤重叠的光源
    lights_filtered = [
        rect for rect in lights_filtered 
        if not any(is_coincide(cv2.boxPoints(rect).astype(int), cv2.boxPoints(other_light).astype(int)) 
                           for other_light in lights_filtered if rect != other_light)  # 检查重叠
    ]

    lights_red, lights_blue = [], []  # 存放光源的列表
    img_drawn = img.copy()  # 复制原始图像
    
    for rect in lights_filtered:
        box = cv2.boxPoints(rect).astype(int)  # 获取旋转矩形的四个点
        mask = np.zeros(img_binary.shape, dtype=np.uint8)  # 创建掩膜
        cv2.drawContours(mask, [box], -1, 255, -1)  # 在掩膜上绘制轮廓
        masked_img = cv2.bitwise_and(img, img, mask=mask)  # 按掩膜提取区域
        sum_r, sum_b = np.sum(masked_img[:, :, 2]), np.sum(masked_img[:, :, 0])  # 计算红色和蓝色的总和

        if mode == 0 and sum_b > sum_r:       # 根据 mode 识别颜色
            lights_blue.append(rect)  # 添加蓝色光源
        elif mode == 1 and sum_r > sum_b:
            lights_red.append(rect)  # 添加红色光源
        elif mode == 2:
            (lights_red if sum_r > sum_b else lights_blue).append(rect)  # 根据颜色添加光源

    if mode in [0, 2]:  #根据 mode 绘制识别的光源,绘制蓝色光源
        for rect in lights_blue:
            box = cv2.boxPoints(rect).astype(int)  # 获取轮廓点
            cv2.drawContours(img_drawn, [box], 0, (255, 0, 0), 2)  # 绘制蓝色轮廓
            cv2.circle(img_drawn, tuple(map(int, rect[0])), 3, (255, 0, 0), -1)  # 绘制蓝色中心点

    if mode in [1, 2]:  # 绘制红色光源
        for rect in lights_red:
            box = cv2.boxPoints(rect).astype(int)  # 获取轮廓点
            cv2.drawContours(img_drawn, [box], 0, (0, 0, 255), 2)  # 绘制红色轮廓
            cv2.circle(img_drawn, tuple(map(int, rect[0])), 3, (0, 0, 255), -1)  # 绘制红色中心点
            
    return lights_red, lights_blue, img_drawn  # 返回红色和蓝色光源

def is_close(rect1, rect2, light_tol, angle_tol, height_tol, width_tol):
    """检查两个旋转矩形是否足够接近。辅助函数"""
    (cx1, cy1), (w1, h1), angle1 = rect1  # 获取第一个矩形的信息
    (cx2, cy2), (w2, h2), angle2 = rect2  # 获取第二个矩形的信息
    distance = math.sqrt((cx1 - cx2) ** 2 + (cy1 - cy2) ** 2)    # 计算中心点之间的距离
    
    if distance > 20:    # 首先判断距离是否大于20
        angle_diff = min(abs(angle1 - angle2), 360 - abs(angle1 - angle2))  # 计算角度差 # 判断旋转矩形的角度是否接近
        if angle_diff <= light_tol:  # 判断角度差是否在容忍范围内
            if abs(h1 - h2) <= height_tol and abs(w1 - w2) <= width_tol:  # 判断高宽差
                line_angle = math.degrees(math.atan2(cy2 - cy1, cx2 - cx1))  # 计算连线角度

                if line_angle > 90:    # 将角度标准化到 -90° 到 90° 之间
                    line_angle -= 180  # 标准化处理
                elif line_angle < -90:
                    line_angle += 180  # 标准化处理

                if (abs(line_angle - angle1) <= angle_tol or abs(line_angle - angle2) <= angle_tol):  # 检查是否垂直
                    return True                # 直接判断与旋转矩形的角度接近垂直
    return False

def is_armor(lights, light_tol=5, angle_tol=7, height_tol=15, width_tol=10):
    """匹配灯条，找装甲板"""
    lights_matched = []  # 存放匹配的光源组
    processed_indices = set()  # 用于存储已处理的矩形索引
    lights_count = len(lights)  # 存储列表长度，避免重复计算

    for i in range(lights_count):  # 使用 for 循环遍历 lights
        if i in processed_indices:  # 如果该矩形已处理，跳过
            continue
        
        light1 = lights[i]  # 取出当前矩形
        close_lights = [j for j in range(lights_count) 
                        if j != i and is_close(light1, lights[j], light_tol, angle_tol, height_tol, width_tol)]  # 找到接近的光源
        
        if close_lights:  # 如果找到接近的矩形
            group = [light1] + [lights[j] for j in close_lights]  # 将当前矩形和接近的矩形组合成一组
            lights_matched.append(group)  # 将当前组添加到所有组中
            
            # 将已处理的矩形索引添加到 processed_indices 中
            processed_indices.update([i] + close_lights)

    armor = []  # 存放装甲信息
    for light_matched in lights_matched:  # 遍历所有装甲组
        if light_matched:  # 如果组不为空
            points = np.concatenate([cv2.boxPoints(light) for light in light_matched])  # 获取所有矩形的四个顶点
            armor_raw = cv2.minAreaRect(points)  # 计算最小外接矩形

            if 200 <= armor_raw[1][0] * armor_raw[1][1] <= 10000 and 0 <= armor_raw[1][0] / armor_raw[1][1] <= 5:  # 判断面积和比例
                armor.append(adjust(armor_raw)) # 调整并添加到装甲矩形列表   
    return armor  # 返回装甲

def armor_id(img, armors, class_id):
    """为装甲矩形标记信息并在图像上绘制轮廓。"""
    armors_dict = {}  # 存储装甲信息的字典
    color_map = {0: (255, 255, 0), 1: (128, 0, 128)}  # 蓝色和红色的颜色映射
    class_map = {0: 1, 1: 7}  # 蓝色和红色的 class_id 映射

    if class_id not in color_map:    # 提前判断 class_id 是否在 color_map 中
        return armors_dict  # 如果不在，直接返回空的字典
    
    for armor in armors:  # 遍历所有装甲矩形
        center, (width, height), angle = armor  # 获取装甲矩形的中心、宽高和角度
        max_size = max(width, height)  # 计算最大尺寸
        box = cv2.boxPoints(((center[0], center[1]), (max_size, max_size), angle)).astype(int)  # 获取装甲的四个顶点

        armors_dict[f"{int(center[0])}"] = {        # 添加装甲信息到字典
            "class_id": class_map[class_id],  # 添加 class_id
            "height": int(max_size),  # 添加高度
            "center": [int(center[0]), int(center[1])]  # 添加中心点
        }

        cv2.drawContours(img, [box], 0, color_map[class_id], 2)  # 绘制装甲的轮廓
        cv2.circle(img, (int(center[0]), int(center[1])), 5, color_map[class_id], -1)  # 绘制装甲中心点
        center_x, center_y = map(int, armor[0])  # 获取中心坐标
        cv2.putText(img, f"({center_x}, {center_y})", (center_x, center_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # 在图像上标记坐标
    
    cv2.imshow("armor", img)  # 显示装甲图像
    return armors_dict  # 返回装甲信息字典

def find_armor(img, lights_red, lights_blue):
    """跟踪装甲并返回装甲字典。"""
    armors_dict, armors_red, armors_blue = {}, [], []  # 初始化装甲字典和列表
    armors_red = is_armor(lights_red)  # 查找红色装甲
    armors_blue = is_armor(lights_blue)  # 查找蓝色装甲
    armors_dict.update(armor_id(img, armors_red, 1))  # 红色装甲    # 合并红色和蓝色装甲的信息
    armors_dict.update(armor_id(img, armors_blue, 0))  # 蓝色装甲
    return armors_dict  # 返回装甲字典

def track_armor(img, val, mode):
    """跟踪装甲并返回装甲字典"""
    img_raw, img_binary = img_processed(img, val)  # 处理图像
    lights_red, lights_blue, img_drawn = find_light(img_binary, img_raw, mode)  # 查找光源
    armors_dict = find_armor(img_drawn, lights_red, lights_blue)  # 查找装甲
    return armors_dict  # 返回装甲字典
    
if __name__ == "__main__":
    img = cv2.imread('./photo/2.jpg')  # 读取图像
    val = 35  # 设置阈值
    mode = 2  # 1-red, 0-blue, 2-both
    armors_dict = track_armor(img, val, mode)  # 跟踪装甲
    print(armors_dict)  # 打印装甲字典
    cv2.waitKey(0)  # 等待按键