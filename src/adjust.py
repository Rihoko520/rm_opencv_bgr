import cv2

val = 35  # 动态调整的时候的默认值

def update_val(new_val):
    global val
    val = new_val

def setup_windows():
    cv2.namedWindow('Threshold')
    cv2.createTrackbar('Threshold', 'Threshold', val, 255, update_val)  # 创建 val 滑动条

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