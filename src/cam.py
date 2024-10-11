import cv2
from detector import track_armor
import adjust  # 导入调试代码

# 设置模式：0 - 处理视频流，1 - 仅运行检测，2 - 实时处理静态图像
global mode 
mode = 0  # 0: 处理视频流, 1: 仅运行检测, 2: 实时处理静态图像
global image_path   
image_path = './photo/2.jpg'  # 替换为你的图像路径
global url
url = "photo/test.mp4"

def main():
    if mode == 0:
        # 处理视频流
        video_stream = cv2.VideoCapture(url)

        if not video_stream.isOpened():
            print("错误: 无法打开视频流。")
            return
        
        adjust.setup_windows()  # 创建滑动条窗口

        while True:
            ret, frame = video_stream.read()
            if not ret:
                print("错误: 无法读取帧")
                break
            
            # 处理帧并获取当前调节的 val
            val = adjust.val  # 获取当前的 val 值
            
            # 目标检测，传入原图和 val
            armors_dict = track_armor(frame, val,2)
            
            if armors_dict:
                print(armors_dict)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        video_stream.release()
        cv2.destroyAllWindows()
    
    elif mode == 1:
        # 仅运行检测
        video_stream = cv2.VideoCapture(url)

        if not video_stream.isOpened():
            print("错误: 无法打开视频流。")
            return
        
        adjust.setup_windows()  # 创建滑动条窗口
        
        while True:
            ret, frame = video_stream.read()
            if not ret:
                print("错误: 无法读取帧")
                break
            
            # 目标检测，传入原图和 val
            val = adjust.val  # 获取当前的 val 值
            armors_dict = track_armor(frame, val,2)
            
            if armors_dict:
                print(armors_dict)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        video_stream.release()
        cv2.destroyAllWindows()
    
    elif mode == 2:
        # 实时处理静态图像
        current_frame = cv2.imread(image_path)
        if current_frame is None:
            print("错误: 无法读取图像。请检查路径:", image_path)
            return
        
        adjust.setup_windows()  # 创建滑动条窗口
        
        while True:
            # 获取当前调节的 val
            val = adjust.val  # 获取当前的 val 值
            
            # 进行目标检测
            armors_dict = track_armor(current_frame, val,2)
            if armors_dict:
                print(armors_dict)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
    else:
        print("无效的模式，程序结束。")

if __name__ == "__main__":
    main()