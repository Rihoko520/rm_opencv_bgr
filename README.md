# RM_OPENCV

---

## 使用传统视觉识别装甲板

---  
[关于 OpenCV](https://kdocs.cn/l/cesjy4EquE2h)

---

## 运行代码的准备工作

### 1. 克隆代码库
使用 Git 克隆代码仓库：
```bash
git clone https://github.com/Rihoko520/rm_opencv_bgr.git
```

### 2. 环境设置
- **安装 Python**: 确保已安装 Python 3.x。

### 3. 安装依赖库
运行以下命令安装所需库：
```bash
pip install opencv-python numpy 
```

---

## 功能模块介绍

### 1. [adjust.py](src/adjust.py) 功能介绍
`adjust.py` 通过调整 **阈值** 来实现图像的 **二值化** 处理，用于动态调整处理图像的 **二值化阈值**。

#### 使用说明
- 修改 `val` 变量以选择处理 **阈值**。
- 运行脚本后，通过滑动条调整阈值，以查看不同处理效果的实时结果。

---

### 2. [cam.py](src/cam.py) 功能介绍
`cam.py` 负责处理相机输入，支持实时目标检测和静态图像处理。它结合了 `adjust.py` 的参数调整功能，允许用户根据需要进行实时调节。

#### 使用说明
- 设置 `mode` 变量以选择不同的处理模式：
  - **0**: 视频流调试
  - **1**: 仅运行检测
  - **2**: 仅运行检测-无图
  - **3**: 静态图调试
- 在模式为 **0** ， **1** ，**2** 时，若 `video=True`，程序会使用指定的 URL 进行视频流处理；若 `video=False`，则使用可用的摄像头。
- `image_path` 变量用于指定静态图像的路径。
- `val` 变量用于设置静态值，可根据需要进行调整。

---

### 3. [detector.py](src/detector.py) 功能介绍
`detector.py` 提供主要的目标检测功能，负责装甲板的识别和处理。

#### 相关变量说明
- **val**: 
  - **说明**: 用于二值化处理的阈值。图像的灰度值大于此阈值的像素将被标记为白色（255），小于此值的像素将被标记为黑色（0）。调整此值可以影响二值化效果，选择合适的值可以更好地识别装甲板。

- **light_tol**:
  - **说明**: 光源之间的角度容忍度。用于判断两个灯条是否可以被视为同一组装甲。较小的值会使得只有几乎平行的灯条被视为相同组，较大的值则会允许更大角度差异。

- **angle_tol**:
  - **说明**: 旋转矩形的角度容忍度。用于判断两个旋转矩形的角度是否足够接近，以便被视为同一组装甲。此值越大，能够容忍的角度差异越大。

- **height_tol**:
  - **说明**: 用于判断两个装甲的高度差容忍度。此值限制了两装甲高度的最大差异，只有高度差在此范围内的装甲才会被视为接近。

- **width_tol**:
  - **说明**: 用于判断两个装甲的宽度差容忍度。与高度差类似，此值限制了两装甲宽度的最大差异，只有宽度差在此范围内的装甲才会被视为接近。

- **cy_tol**:
  - **说明**: 中心点垂直坐标差容忍度，用于判断两个旋转矩形的中心点在垂直方向上的接近程度。该值越小，要求越严格。
---

#### 主要函数：

1. **`img_processed(img, val, mode)`**：处理图像，返回调整大小和亮度的图像及二值化图像。
2. **`find_light(img_binary, img, mode)`**：查找图像中的光源并返回旋转矩形。
3. **`find_armor(img, lights_red, lights_blue, mode)`**：跟踪装甲并返回装甲字典。
4. **`is_armor(lights, light_tol=5, angle_tol=7, height_tol=10, width_tol=10, cy_tol=5)`**：匹配灯条，找装甲板。
5. **`armor_id(img, armors, class_id, mode)`**：为装甲矩形标记信息并在图像上绘制轮廓，并用于生成装甲字典内容。
6. **`find_armor(img, lights_red, lights_blue, mode)`**：跟踪装甲并返回装甲字典。

---

#### 辅助函数：

1. **`darker(img)`**：降低图像亮度并保留原图像色彩特征，提供给 `img_processed()` 使用。
2. **`adjust(rect)`**：将矩形转换为多边形，提供给 `find_armor()` 使用。
3. **`is_coincide(polygon1, polygon2)`**：判断两个多边形是否相交，用于 `is_armor()` 函数调用。
4. **`project(polygon, axis)`**：将多边形投影到给定的轴上，提供给 `is_coincide()` 使用。
5. **`is_close(rect1, rect2, light_tol, angle_tol, height_tol, width_tol, cy_tol)`**：判断两个矩形是否接近，用于 `find_armor()` 函数调用。

---

### 4. [square.py](src/square.py) 功能介绍
`square.py` 用于创建一个白色背景上的正方形图像。虽然功能不重要，但可以作为简单的图像生成示例。

#### 使用说明
- 运行 [square.py](src/square.py) 将生成一个 640x480 像素的白色背景图像，并在中心绘制一个边长为 84 的正方形。辅助调整识别装甲板在图像上显示的大小。

---

## 装甲板识别流程 *track_armor(img, val, mode)*

### 1. 图像处理
- **调用函数**: `img_processed(img, val, mode)`
  - **功能**: 调整图像大小、应用亮度调整、进行灰度转换并进行二值化处理。
  - **步骤**: 
    - 将图像调整为 `(640, 480)`。
    - 应用亮度调整以增强图像清晰度。
    - 将图像转换为灰度图。
    - 使用阈值 `val` 生成二值图像。

### 2. 查找光源
- **调用函数**: `find_light(img_binary, img, mode)`
  - **功能**: 查找图像中的光源并返回灯条，并根据 `mode` 进行光源的颜色识别。
  - **步骤**: 
    - 使用 `cv2.findContours` 查找图像中的轮廓，并返回灯条。
    - 过滤小面积的轮廓，确保只处理较大的轮廓。
    - 使用 `is_coincide` 检查轮廓之间是否相交，避免重复检测。
    - 筛选出符合特定条件的灯条，如颜色、形状等。

### 3. 跟踪装甲
- **调用函数**: `find_armor(img, lights_red, lights_blue, mode)`
  - **功能**: 识别装甲类型并返回装甲字典。
  - **步骤**: 
    - 将相近的灯条分组，以便合并处理。
    - 调用 `is_armor` 进行灯条的匹配，找出装甲板。
    - 使用 `is_coincide` 检查装甲板之间是否相交，避免重复检测。
    - 调用 `armor_id` 获取装甲的类 ID、高度和中心坐标，并在图像上绘制检测结果。

### 4. 返回结果
- 返回包含检测到的装甲信息的字典：
![armor](./photo/example.jpg)
```json
{'443': {'class_id': 7, 'height': 101, 'center': [443, 364]}, '264': {'class_id': 1, 'height': 31, 'center': [264, 241]}, '366': {'class_id': 1, 'height': 35, 'center': [366, 229]}}
```


---
