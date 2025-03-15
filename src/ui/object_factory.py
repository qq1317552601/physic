from physics.objects import Box, Circle, Triangle, Spring, Rope, Ramp
from utils.config import config

class ObjectFactory:
    """
    物理对象工厂类
    负责创建各种物理对象
    """
    def __init__(self, simulator):
        """
        初始化物理对象工厂
        
        参数:
            simulator: 物理模拟器实例
        """
        self.simulator = simulator
    
    def add_box(self, position=(0, 0), width=None, height=None, mass=None, velocity=(0, 0), color=None):
        """
        添加长方体
        
        参数:
            position: 位置坐标
            width, height: 宽度和高度
            mass: 质量
            velocity: 初始速度
            color: 颜色
            
        返回:
            创建的长方体对象
        """
        # 使用配置中的默认值或传入的值
        box_defaults = config.get("object_defaults", "box") or {}
        
        if width is None:
            width = box_defaults.get("width", 1.0)
        if height is None:
            height = box_defaults.get("height", 1.0)
        if mass is None:
            mass = box_defaults.get("mass", 1.0)
        
        box = Box(position, (width, height), mass, velocity)
        
        if color:
            box.color = color
        else:
            default_color = box_defaults.get("color", "#C8C8FF")
            if isinstance(default_color, str):
                from PyQt5.QtGui import QColor
                box.color = QColor(default_color)
        
        self.simulator.add_object(box)
        return box
    
    def add_circle(self, position=(0, 0), radius=None, mass=None, velocity=(0, 0), color=None):
        """
        添加圆形
        
        参数:
            position: 位置坐标
            radius: 半径
            mass: 质量
            velocity: 初始速度
            color: 颜色
            
        返回:
            创建的圆形对象
        """
        # 使用配置中的默认值或传入的值
        circle_defaults = config.get("object_defaults", "circle") or {}
        
        if radius is None:
            radius = circle_defaults.get("radius", 0.5)
        if mass is None:
            mass = circle_defaults.get("mass", 1.0)
        
        circle = Circle(position, radius, mass, velocity)
        
        if color:
            circle.color = color
        else:
            default_color = circle_defaults.get("color", "#FFC8C8")
            if isinstance(default_color, str):
                from PyQt5.QtGui import QColor
                circle.color = QColor(default_color)
        
        self.simulator.add_object(circle)
        return circle
    
    def add_triangle(self, position=(0, 0), size=None, mass=None, velocity=(0, 0), color=None):
        """
        添加三角形
        
        参数:
            position: 位置坐标
            size: 尺寸 (width, height)
            mass: 质量
            velocity: 初始速度
            color: 颜色
            
        返回:
            创建的三角形对象
        """
        # 使用配置中的默认值或传入的值
        triangle_defaults = config.get("object_defaults", "triangle") or {}
        
        if size is None:
            size = tuple(triangle_defaults.get("size", [1.0, 1.0]))
        if mass is None:
            mass = triangle_defaults.get("mass", 1.0)
        
        width, height = size
        half_width = width / 2
        
        vertices = [
            (position[0] - half_width, position[1]),
            (position[0] + half_width, position[1]),
            (position[0], position[1] + height)
        ]
        
        triangle = Triangle(position, vertices, mass, velocity)
        
        if color:
            triangle.color = color
        else:
            default_color = triangle_defaults.get("color", "#C8FFC8")
            if isinstance(default_color, str):
                from PyQt5.QtGui import QColor
                triangle.color = QColor(default_color)
        
        self.simulator.add_object(triangle)
        return triangle
    
    def add_spring(self, start_pos=(0, 0), end_pos=(1, 0), k=None, width=None, color=None):
        """
        添加弹簧
        
        参数:
            start_pos: 起点位置
            end_pos: 终点位置
            k: 弹性系数
            width: 线宽
            color: 颜色
            
        返回:
            创建的弹簧对象
        """
        # 使用配置中的默认值或传入的值
        spring_defaults = config.get("object_defaults", "spring") or {}
        
        if k is None:
            k = spring_defaults.get("k", 10.0)
        if width is None:
            width = spring_defaults.get("width", 0.1)
        
        spring = Spring(start_pos, end_pos, k, None, width)
        
        if color:
            spring.color = color
        else:
            default_color = spring_defaults.get("color", "#C8C8C8")
            if isinstance(default_color, str):
                from PyQt5.QtGui import QColor
                spring.color = QColor(default_color)
        
        self.simulator.add_object(spring)
        return spring
    
    def add_rope(self, start_pos=(0, 0), end_pos=(1, 0), segments=None, width=None, color=None):
        """
        添加轻绳
        
        参数:
            start_pos: 起点位置
            end_pos: 终点位置
            segments: 段数
            width: 线宽
            color: 颜色
            
        返回:
            创建的轻绳对象
        """
        # 使用配置中的默认值或传入的值
        rope_defaults = config.get("object_defaults", "rope") or {}
        
        if segments is None:
            segments = rope_defaults.get("segments", 10)
        if width is None:
            width = rope_defaults.get("width", 0.05)
        
        rope = Rope(start_pos, end_pos, segments, width)
        
        if color:
            rope.color = color
        else:
            default_color = rope_defaults.get("color", "#964B00")
            if isinstance(default_color, str):
                from PyQt5.QtGui import QColor
                rope.color = QColor(default_color)
        
        self.simulator.add_object(rope)
        return rope
    
    def add_ramp(self, position=(0, 0), width=None, height=None, friction=None, color=None):
        """
        添加斜面
        
        参数:
            position: 位置坐标
            width: 宽度
            height: 高度
            friction: 摩擦系数
            color: 颜色
            
        返回:
            创建的斜面对象
        """
        # 使用配置中的默认值或传入的值
        ramp_defaults = config.get("object_defaults", "ramp") or {}
        
        if width is None:
            width = ramp_defaults.get("width", 2.0)
        if height is None:
            height = ramp_defaults.get("height", 1.0)
        if friction is None:
            friction = ramp_defaults.get("friction", 0.5)
        
        ramp = Ramp(position, width, height, None, friction)
        
        if color:
            ramp.color = color
        else:
            default_color = ramp_defaults.get("color", "#E6E6E6")
            if isinstance(default_color, str):
                from PyQt5.QtGui import QColor
                ramp.color = QColor(default_color)
        
        self.simulator.add_object(ramp)
        return ramp
    
    def create_object(self, object_type, x, y):
        """
        根据类型创建对象
        
        参数:
            object_type: 对象类型
            x, y: 物理坐标
            
        返回:
            创建的对象，如果类型不支持则返回None
        """
        if object_type == "矩形":
            return self.add_box(position=(x, y))
        elif object_type == "圆形":
            return self.add_circle(position=(x, y))
        elif object_type == "三角形":
            return self.add_triangle(position=(x, y))
        elif object_type == "弹簧":
            return self.add_spring(start_pos=(x, y), end_pos=(x + 1, y))
        elif object_type == "轻绳":
            return self.add_rope(start_pos=(x, y), end_pos=(x + 1, y))
        elif object_type == "斜面":
            return self.add_ramp(position=(x, y))
        
        return None 