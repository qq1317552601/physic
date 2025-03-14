import math
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF

class PhysicsObject:
    """
    物理对象基类
    所有物理单件的基础类，定义共有属性和方法
    """
    def __init__(self, position=(0, 0), mass=1.0, velocity=(0, 0), acceleration=(0, 0)):
        """
        初始化物理对象
        
        参数:
            position (tuple): 物体中心的物理坐标 (x, y)，单位：米
            mass (float): 物体质量，单位：kg
            velocity (tuple): 初始速度 (vx, vy)，单位：m/s
            acceleration (tuple): 初始加速度 (ax, ay)，单位：m/s²
        """
        self.position = position  # 物理坐标，单位：米
        self.mass = mass  # 质量，单位：kg
        self.velocity = velocity  # 速度，单位：m/s
        self.acceleration = acceleration  # 加速度，单位：m/s²
        self.color = QColor(200, 200, 255)  # 默认颜色
        self.friction = 0.5  # 摩擦系数，默认值
        self.restitution = 0.7  # 弹性系数，默认值
        
    def update(self, dt):
        """
        更新物体状态
        
        参数:
            dt (float): 时间步长，单位：秒
        """
        # 更新速度
        vx = self.velocity[0] + self.acceleration[0] * dt
        vy = self.velocity[1] + self.acceleration[1] * dt
        self.velocity = (vx, vy)
        
        # 更新位置
        x = self.position[0] + self.velocity[0] * dt
        y = self.position[1] + self.velocity[1] * dt
        self.position = (x, y)
    
    def draw(self, painter, view):
        """
        在视图中绘制物体
        
        参数:
            painter (QPainter): 用于绘制的画笔
            view (SimulationView): 模拟视图对象，用于坐标转换
        """
        # 在子类中实现
        pass
    
    def to_screen_coords(self, view, x, y):
        """
        将物理坐标转换为屏幕坐标
        
        参数:
            view (SimulationView): 模拟视图对象
            x, y (float): 物理坐标
            
        返回:
            tuple: 屏幕坐标 (screen_x, screen_y)
        """
        screen_x = view.origin.x() + x * view.scale
        screen_y = view.origin.y() - y * view.scale
        return screen_x, screen_y
    
    def from_screen_coords(self, view, screen_x, screen_y):
        """
        将屏幕坐标转换为物理坐标
        
        参数:
            view (SimulationView): 模拟视图对象
            screen_x, screen_y (float): 屏幕坐标
            
        返回:
            tuple: 物理坐标 (x, y)
        """
        x = (screen_x - view.origin.x()) / view.scale
        y = (view.origin.y() - screen_y) / view.scale  # 注意y轴方向相反
        return x, y
    
    def contains_point(self, x, y):
        """
        检查点是否在物体内部
        
        参数:
            x, y (float): 物理坐标
            
        返回:
            bool: 如果点在物体内部则返回True
        """
        # 在子类中实现
        return False
    
    def get_bounding_box(self):
        """
        获取物体的包围盒
        
        返回:
            tuple: (min_x, min_y, max_x, max_y)
        """
        # 在子类中实现
        return (0, 0, 0, 0)


class Box(PhysicsObject):
    """长方体物理对象"""
    def __init__(self, position=(0, 0), size=(1, 1), mass=1.0, velocity=(0, 0), acceleration=(0, 0)):
        """
        初始化长方体对象
        
        参数:
            position (tuple): 物体中心的物理坐标 (x, y)
            size (tuple): 长方体的尺寸 (width, height)，单位：米
            mass, velocity, acceleration: 同基类
        """
        super().__init__(position, mass, velocity, acceleration)
        self.width, self.height = size  # 宽度和高度，单位：米
        self.color = QColor(200, 200, 255)  # 默认为浅蓝色
    
    def draw(self, painter, view):
        """在视图中绘制长方体"""
        # 将物理坐标转换为屏幕坐标
        screen_x, screen_y = self.to_screen_coords(view, self.position[0], self.position[1])
        screen_width = self.width * view.scale
        screen_height = self.height * view.scale
        
        # 设置画笔和画刷
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(self.color))
        
        # 绘制长方体
        painter.drawRect(
            int(screen_x - screen_width/2),
            int(screen_y - screen_height/2),
            int(screen_width),
            int(screen_height)
        )
    
    def contains_point(self, x, y):
        """检查点是否在长方体内部"""
        half_width = self.width / 2
        half_height = self.height / 2
        
        return (abs(x - self.position[0]) <= half_width and 
                abs(y - self.position[1]) <= half_height)
    
    def get_bounding_box(self):
        """获取长方体的包围盒"""
        half_width = self.width / 2
        half_height = self.height / 2
        
        return (
            self.position[0] - half_width,
            self.position[1] - half_height,
            self.position[0] + half_width,
            self.position[1] + half_height
        )


class Circle(PhysicsObject):
    """圆形物理对象"""
    def __init__(self, position=(0, 0), radius=0.5, mass=1.0, velocity=(0, 0), acceleration=(0, 0)):
        """
        初始化圆形对象
        
        参数:
            position (tuple): 圆心的物理坐标 (x, y)
            radius (float): 圆的半径，单位：米
            mass, velocity, acceleration: 同基类
        """
        super().__init__(position, mass, velocity, acceleration)
        self.radius = radius  # 半径，单位：米
        self.color = QColor(255, 200, 200)  # 默认为浅红色
    
    def draw(self, painter, view):
        """在视图中绘制圆形"""
        # 将物理坐标转换为屏幕坐标
        screen_x, screen_y = self.to_screen_coords(view, self.position[0], self.position[1])
        screen_radius = self.radius * view.scale
        
        # 设置画笔和画刷
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(self.color))
        
        # 绘制圆形
        painter.drawEllipse(
            int(screen_x - screen_radius),
            int(screen_y - screen_radius),
            int(screen_radius * 2),
            int(screen_radius * 2)
        )
    
    def contains_point(self, x, y):
        """检查点是否在圆形内部"""
        dx = x - self.position[0]
        dy = y - self.position[1]
        distance_squared = dx*dx + dy*dy
        
        return distance_squared <= self.radius * self.radius
    
    def get_bounding_box(self):
        """获取圆形的包围盒"""
        return (
            self.position[0] - self.radius,
            self.position[1] - self.radius,
            self.position[0] + self.radius,
            self.position[1] + self.radius
        )


class Triangle(PhysicsObject):
    """三角形物理对象"""
    def __init__(self, position=(0, 0), vertices=None, mass=1.0, velocity=(0, 0), acceleration=(0, 0)):
        """
        初始化三角形对象
        
        参数:
            position (tuple): 三角形中心的物理坐标 (x, y)
            vertices (list): 三个顶点的相对坐标，例如 [(-0.5, -0.5), (0.5, -0.5), (0, 0.5)]
                            这些坐标是相对于position的偏移
            mass, velocity, acceleration: 同基类
        """
        super().__init__(position, mass, velocity, acceleration)
        
        # 如果没有提供顶点，则创建一个默认的等边三角形
        if vertices is None:
            # 创建一个边长为1的等边三角形
            side_length = 1.0
            height = side_length * math.sqrt(3) / 2
            vertices = [
                (-side_length/2, -height/3),  # 左下
                (side_length/2, -height/3),   # 右下
                (0, height*2/3)               # 顶部
            ]
        
        self.vertices = vertices  # 顶点相对坐标
        self.color = QColor(200, 255, 200)  # 默认为浅绿色
    
    def draw(self, painter, view):
        """在视图中绘制三角形"""
        x, y = self.position
        
        # 创建多边形对象
        polygon = QPolygonF()
        for vx, vy in self.vertices:
            # 计算顶点的绝对物理坐标
            abs_x, abs_y = x + vx, y + vy
            # 转换为屏幕坐标
            screen_x, screen_y = self.to_screen_coords(view, abs_x, abs_y)
            polygon.append(QPointF(screen_x, screen_y))
        
        # 设置画笔和画刷
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(self.color))
        
        # 绘制三角形
        painter.drawPolygon(polygon)
    
    def contains_point(self, x, y):
        """检查点是否在三角形内部（使用重心坐标法）"""
        # 获取三角形的三个顶点（绝对坐标）
        p0x, p0y = self.position[0] + self.vertices[0][0], self.position[1] + self.vertices[0][1]
        p1x, p1y = self.position[0] + self.vertices[1][0], self.position[1] + self.vertices[1][1]
        p2x, p2y = self.position[0] + self.vertices[2][0], self.position[1] + self.vertices[2][1]
        
        # 计算重心坐标
        area = 0.5 * (-p1y * p2x + p0y * (-p1x + p2x) + p0x * (p1y - p2y) + p1x * p2y)
        s = 1 / (2 * area) * (p0y * p2x - p0x * p2y + (p2y - p0y) * x + (p0x - p2x) * y)
        t = 1 / (2 * area) * (p0x * p1y - p0y * p1x + (p0y - p1y) * x + (p1x - p0x) * y)
        
        # 如果所有重心坐标都在[0,1]范围内，则点在三角形内部
        return s >= 0 and t >= 0 and 1 - s - t >= 0
    
    def get_bounding_box(self):
        """获取三角形的包围盒"""
        # 计算所有顶点的绝对坐标
        abs_vertices = [(self.position[0] + vx, self.position[1] + vy) for vx, vy in self.vertices]
        
        # 找出最小和最大的x、y坐标
        min_x = min(v[0] for v in abs_vertices)
        min_y = min(v[1] for v in abs_vertices)
        max_x = max(v[0] for v in abs_vertices)
        max_y = max(v[1] for v in abs_vertices)
        
        return (min_x, min_y, max_x, max_y)


class Spring(PhysicsObject):
    """弹簧物理对象"""
    def __init__(self, start_pos=(0, 0), end_pos=(1, 0), k=10.0, rest_length=None, width=0.1):
        """
        初始化弹簧对象
        
        参数:
            start_pos (tuple): 弹簧起点的物理坐标 (x, y)
            end_pos (tuple): 弹簧终点的物理坐标 (x, y)
            k (float): 弹簧劲度系数，单位：N/m
            rest_length (float): 弹簧的自然长度，如果为None则使用起点和终点之间的距离
            width (float): 弹簧的宽度，单位：米
        """
        # 计算弹簧中点作为位置
        position = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
        super().__init__(position, mass=0.0)  # 弹簧本身没有质量
        
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.k = k  # 弹簧劲度系数
        
        # 计算当前长度
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        current_length = math.sqrt(dx*dx + dy*dy)
        
        # 设置自然长度
        self.rest_length = rest_length if rest_length is not None else current_length
        
        self.width = width  # 弹簧的宽度
        self.color = QColor(255, 150, 0)  # 橙色
        self.coils = 10  # 弹簧的圈数
    
    def draw(self, painter, view):
        """在视图中绘制弹簧"""
        # 将物理坐标转换为屏幕坐标
        start_x, start_y = self.to_screen_coords(view, self.start_pos[0], self.start_pos[1])
        end_x, end_y = self.to_screen_coords(view, self.end_pos[0], self.end_pos[1])
        
        # 设置画笔
        painter.setPen(QPen(self.color, max(1, int(self.width * view.scale / 5))))
        
        # 计算弹簧方向向量
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length < 1:  # 防止除以零
            return
        
        # 单位方向向量
        ux, uy = dx / length, dy / length
        
        # 计算垂直于弹簧方向的单位向量
        vx, vy = -uy, ux
        
        # 弹簧的振幅（宽度）
        amplitude = min(length / 4, self.width * view.scale)
        
        # 绘制弹簧（正弦波形）
        path = []
        
        # 起点
        path.append((start_x, start_y))
        
        # 弹簧主体（正弦波）
        coil_length = length / (self.coils + 2)  # 每个弹簧圈的长度
        
        # 添加一小段直线
        path.append((start_x + ux * coil_length, start_y + uy * coil_length))
        
        # 添加弹簧圈
        for i in range(self.coils):
            t = (i + 1) / (self.coils + 1)
            x = start_x + dx * t
            y = start_y + dy * t
            
            # 添加正弦波形
            if i % 2 == 0:
                x += vx * amplitude
                y += vy * amplitude
            else:
                x -= vx * amplitude
                y -= vy * amplitude
            
            path.append((x, y))
        
        # 添加一小段直线
        path.append((end_x - ux * coil_length, end_y - uy * coil_length))
        
        # 终点
        path.append((end_x, end_y))
        
        # 绘制路径
        for i in range(len(path) - 1):
            painter.drawLine(int(path[i][0]), int(path[i][1]), int(path[i+1][0]), int(path[i+1][1]))
    
    def get_force(self):
        """
        计算弹簧产生的力
        
        返回:
            tuple: 作用在终点的力 (fx, fy)，单位：N
        """
        # 计算当前长度
        dx = self.end_pos[0] - self.start_pos[0]
        dy = self.end_pos[1] - self.start_pos[1]
        current_length = math.sqrt(dx*dx + dy*dy)
        
        if current_length < 0.001:  # 防止除以零
            return (0, 0)
        
        # 计算弹簧力大小 (F = -k * (x - x0))
        force_magnitude = self.k * (self.rest_length - current_length)
        
        # 计算力的方向（单位向量）
        force_x = force_magnitude * dx / current_length
        force_y = force_magnitude * dy / current_length
        
        return (force_x, force_y)


class Rope(PhysicsObject):
    """轻绳物理对象"""
    def __init__(self, start_pos=(0, 0), end_pos=(1, 0), segments=10, width=0.05):
        """
        初始化轻绳对象
        
        参数:
            start_pos (tuple): 绳子起点的物理坐标 (x, y)
            end_pos (tuple): 绳子终点的物理坐标 (x, y)
            segments (int): 绳子的分段数
            width (float): 绳子的宽度，单位：米
        """
        # 计算绳子中点作为位置
        position = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
        super().__init__(position, mass=0.0)  # 轻绳本身没有质量
        
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.segments = segments
        self.width = width
        self.color = QColor(139, 69, 19)  # 棕色
        
        # 计算绳子的总长度
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        self.length = math.sqrt(dx*dx + dy*dy)
        
        # 初始化绳子的分段点
        self.points = []
        for i in range(segments + 1):
            t = i / segments
            x = start_pos[0] + dx * t
            y = start_pos[1] + dy * t
            self.points.append((x, y))
    
    def draw(self, painter, view):
        """在视图中绘制轻绳"""
        # 设置画笔
        painter.setPen(QPen(self.color, max(1, int(self.width * view.scale))))
        
        # 绘制绳子的每一段
        for i in range(len(self.points) - 1):
            # 将物理坐标转换为屏幕坐标
            x1, y1 = self.to_screen_coords(view, self.points[i][0], self.points[i][1])
            x2, y2 = self.to_screen_coords(view, self.points[i+1][0], self.points[i+1][1])
            
            # 绘制线段
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))


class Ramp(PhysicsObject):
    """斜面物理对象"""
    def __init__(self, position=(0, 0), width=2.0, height=1.0, angle=None, friction=0.5):
        """
        初始化斜面对象
        
        参数:
            position (tuple): 斜面左下角的物理坐标 (x, y)
            width (float): 斜面的宽度，单位：米
            height (float): 斜面的高度，单位：米
            angle (float): 斜面的倾角，单位：弧度，如果为None则根据宽度和高度计算
            friction (float): 斜面的摩擦系数
        """
        super().__init__(position, mass=0.0)  # 斜面本身没有质量
        
        self.width = width
        self.height = height
        self.friction = friction
        self.color = QColor(150, 150, 150)  # 灰色
        
        # 计算斜面的倾角
        if angle is None:
            self.angle = math.atan2(height, width)
        else:
            self.angle = angle
            # 根据角度和宽度计算高度
            self.height = width * math.tan(angle)
        
        # 计算斜面的三个顶点
        self.vertices = [
            (0, 0),                  # 左下角
            (width, 0),              # 右下角
            (0, height)              # 左上角
        ]
    
    def draw(self, painter, view):
        """在视图中绘制斜面"""
        # 创建多边形对象
        polygon = QPolygonF()
        
        for vx, vy in self.vertices:
            # 计算顶点的绝对物理坐标
            abs_x, abs_y = self.position[0] + vx, self.position[1] + vy
            # 转换为屏幕坐标
            screen_x, screen_y = self.to_screen_coords(view, abs_x, abs_y)
            polygon.append(QPointF(screen_x, screen_y))
        
        # 设置画笔和画刷
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(self.color))
        
        # 绘制斜面
        painter.drawPolygon(polygon)
    
    def contains_point(self, x, y):
        """检查点是否在斜面上"""
        # 将点转换为相对于斜面左下角的坐标
        rel_x = x - self.position[0]
        rel_y = y - self.position[1]
        
        # 检查点是否在斜面的矩形范围内
        if rel_x < 0 or rel_x > self.width or rel_y < 0 or rel_y > self.height:
            return False
        
        # 检查点是否在斜面上方
        return rel_y <= self.height * (1 - rel_x / self.width)
    
    def get_normal_force(self, mass, gravity):
        """
        计算斜面提供的法向力
        
        参数:
            mass (float): 物体质量，单位：kg
            gravity (float): 重力加速度，单位：m/s²
            
        返回:
            float: 法向力大小，单位：N
        """
        return mass * gravity * math.cos(self.angle)
    
    def get_friction_force(self, mass, gravity):
        """
        计算斜面提供的摩擦力
        
        参数:
            mass (float): 物体质量，单位：kg
            gravity (float): 重力加速度，单位：m/s²
            
        返回:
            float: 摩擦力大小，单位：N
        """
        normal_force = self.get_normal_force(mass, gravity)
        return self.friction * normal_force
