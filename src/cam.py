import cv2
from detector import track_armor
import adjust  # 导入调试代码

global mode, image_path, url, val, video
mode = 0  # 模式设置 0: 视频流调试 1: 仅运行检测 2: 仅运行检测-无图 3: 静态图调试
video = True # 是否识别视频
url = "photo/test.mp4"
image_path = './photo/red_2.jpg'  # 图像路径
val = 35  # 静态值


def get_first_available_camera():
    """获取第一个可用的摄像头索引"""
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cap.release()
            return 0
    return None  # 没有可用摄像头

def main():
    global val
    camera_index = get_first_available_camera()  # 获取可用摄像头
    if camera_index is None:
        print("错误: 没有找到可用的摄像头。")
        return
    
    if video:
        camera_index = url
    
    if mode == 0:  # 处理视频流
        video_stream = cv2.VideoCapture(camera_index)
        if not video_stream.isOpened():
            print("错误: 无法打开视频流。")
            return
        adjust.setup_windows()  # 创建滑动条窗口
        while True:
            ret, frame = video_stream.read()
            if not ret:
                print("错误: 无法读取帧")
                break
            current_val = cv2.getTrackbarPos('Threshold', 'Threshold')
            armors_dict = track_armor(frame, current_val, 2)
            if armors_dict:
                print(armors_dict)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_stream.release()
        cv2.destroyAllWindows()
    
    elif mode in {1, 2}:  # 仅运行检测或仅运行检测-无图
        video_stream = cv2.VideoCapture(camera_index)  # 使用可用摄像头
        if not video_stream.isOpened():
            print("错误: 无法打开摄像头。")
            return       
        while True:
            ret, frame = video_stream.read()
            if not ret:
                print("错误: 无法读取帧")
                break           
            armors_dict = track_armor(frame, val, 3 if mode == 2 else 2)   
            if armors_dict:
                print(armors_dict)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_stream.release()
        cv2.destroyAllWindows()
    
    elif mode == 3:  # 实时处理静态图像
        current_frame = cv2.imread(image_path)
        if current_frame is None:
            print("错误: 无法读取图像。请检查路径:", image_path)
            return
        adjust.setup_windows()  # 创建滑动条窗口
        while True:
            current_val = cv2.getTrackbarPos('Threshold', 'Threshold')
            armors_dict = track_armor(current_frame, current_val, 2)
            if armors_dict:
                print(armors_dict)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    
    else:
        print("无效的模式，程序结束。")

if __name__ == "__main__":
    main()