from PIL import Image, ImageDraw

# 创建图像
image = Image.new('RGB', (640, 480), 'white')
side_length = int(7000 ** 0.5)  # 边长为45
draw = ImageDraw.Draw(image)

# 计算正方形位置并绘制
x1 = (640 - side_length) // 2
y1 = (480 - side_length) // 2
draw.rectangle([x1, y1, x1 + side_length, y1 + side_length], outline='black', width=2)

# 保存并显示图像
image.save('./photo/output_image.png')
image.show()