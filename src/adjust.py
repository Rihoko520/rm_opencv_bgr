import cv2

# 全局变量
val = 40  # 默认值

# 更新 val
def update_val(new_val):
    global val
    val = new_val

# 设置窗口和滑动条
def setup_windows():
    # 创建阈值窗口
    cv2.namedWindow('Threshold')
    cv2.createTrackbar('Threshold', 'Threshold', val, 255, update_val)  # 创建 val 滑动条

# 处理单张图片
def process_image(image_path):
    global current_frame
    current_frame = cv2.imread(image_path)
    if current_frame is None:
        print("错误: 无法读取图像。请检查路径:", image_path)
        return

    setup_windows()  # 设置窗口

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()