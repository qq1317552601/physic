import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF, pyqtSignal

# 导入物理对象
from physics.objects import PhysicsObject, Box, Circle, Triangle, Spring, Rope, Ramp
from physics.simulator import PhysicsSimulator

# 导入渲染和相机模块
from rendering.camera import Camera
from rendering.renderer import Renderer

class SimulationView(QWidget):
    """
    模拟视图区域
    显示物理模拟并处理用户交互
    """
    # 定义信号
    mousePositionChanged = pyqtSignal(float, float)
    scaleChanged = pyqtSignal(float, str)
    
    def __init__(self):
        """初始化模拟视图"""
        super().__init__()
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: white;")
        self.setMouseTracking(True)  # 启用鼠标跟踪
        self.setFocusPolicy(Qt.StrongFocus)  # 允许接收键盘焦点
        
        # 初始化相机
        self.camera = Camera()
        
        # 初始化渲染器
        self.renderer = Renderer(self)
        
        # 初始化物理模拟器
        self.simulator = PhysicsSimulator()
        
        # 网格和坐标系参数
        self.show_grid = True
        
        # 鼠标状态
        self.mouse_pressed = False
        self.last_mouse_pos = None
        self.selected_object = None
        self.draw_mode = False
        self.current_object_type = "长方体"
        
        # 访问相机属性的代理方法（为了兼容性）
        self.origin = self.camera.origin
        self.scale = self.camera.scale
        self.current_unit = self.camera.current_unit
        self.current_factor = self.camera.current_factor
    
    def resizeEvent(self, event):
        """处理视图大小改变事件"""
        super().resizeEvent(event)
        self.camera.resize(self.width(), self.height())
    
    def wheelEvent(self, event):
        """处理鼠标滚轮事件，缩放视图"""
        # 获取鼠标位置
        pos = event.pos()
        
        # 获取滚轮增量
        delta = event.angleDelta().y()
        
        # 根据滚轮方向确定缩放因子
        if delta > 0:
            zoom_factor = 1.25  # 放大
        else:
            zoom_factor = 0.8  # 缩小
            
        # 更新相机
        changed = self.camera.zoom(zoom_factor, pos.x(), pos.y())
        
        # 如果缩放改变，更新视图和发送信号
        if changed:
            # 更新代理属性
            self.origin = self.camera.origin
            self.scale = self.camera.scale
            self.current_unit = self.camera.current_unit
            self.current_factor = self.camera.current_factor
            
            # 发送比例变化信号
            self.scaleChanged.emit(self.scale, self.current_unit)
            
            # 重绘视图
            self.update()
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        # 记录鼠标状态
        self.mouse_pressed = True
        self.last_mouse_pos = event.pos()
        
        # 获取物理坐标
        phys_x, phys_y = self.camera.from_screen_coords(event.x(), event.y())
        
        # 如果是绘制模式，创建新对象
        if self.draw_mode and event.button() == Qt.LeftButton:
            self.create_object(phys_x, phys_y)
        else:
            # 否则，选择对象
            self.selected_object = self.simulator.get_object_at(phys_x, phys_y)
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        # 更新鼠标状态
        self.mouse_pressed = False
        self.selected_object = None
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        # 获取物理坐标
        phys_x, phys_y = self.camera.from_screen_coords(event.x(), event.y())
        
        # 发送鼠标位置信号
        self.mousePositionChanged.emit(phys_x, phys_y)
        
        # 如果鼠标按下且不在绘制模式，平移视图或移动选中对象
        if self.mouse_pressed and self.last_mouse_pos:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            if self.selected_object and event.buttons() & Qt.LeftButton:
                # 移动选中的对象
                phys_dx = dx / self.camera.scale
                phys_dy = -dy / self.camera.scale  # y轴方向相反
                
                # 更新对象位置
                old_pos = self.selected_object.position
                self.selected_object.position = (old_pos[0] + phys_dx, old_pos[1] + phys_dy)
                
                # 重绘视图
                self.update()
            elif event.buttons() & Qt.RightButton:
                # 平移视图
                self.camera.pan(dx, dy)
                
                # 更新代理属性
                self.origin = self.camera.origin
                
                # 重绘视图
                self.update()
                
        # 更新鼠标位置
        self.last_mouse_pos = event.pos()
    
    def paintEvent(self, event):
        """处理绘制事件"""
        # 创建QPainter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制网格和坐标轴
        if self.show_grid:
            self.renderer.draw_grid(painter)
            self.renderer.draw_axes(painter)
        
        # 绘制所有物理对象
        self.renderer.draw_objects(painter, self.simulator.objects)
    
    def add_box(self, position=(0, 0), width=1.0, height=1.0, mass=1.0, velocity=(0, 0), color=None):
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
        box = Box(position, (width, height), mass, velocity)
        if color:
            box.color = color
        self.simulator.add_object(box)
        self.update()
        return box
    
    def add_circle(self, position=(0, 0), radius=0.5, mass=1.0, velocity=(0, 0), color=None):
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
        circle = Circle(position, radius, mass, velocity)
        if color:
            circle.color = color
        self.simulator.add_object(circle)
        self.update()
        return circle
    
    def add_triangle(self, position=(0, 0), size=(1.0, 1.0), mass=1.0, velocity=(0, 0), color=None):
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
        # 计算三角形顶点
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
        self.simulator.add_object(triangle)
        self.update()
        return triangle
    
    def add_spring(self, start_pos=(0, 0), end_pos=(1, 0), k=10.0, width=0.1, color=None):
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
        spring = Spring(start_pos, end_pos, k, None, width)
        if color:
            spring.color = color
        self.simulator.add_object(spring)
        self.update()
        return spring
    
    def add_rope(self, start_pos=(0, 0), end_pos=(1, 0), segments=10, width=0.05, color=None):
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
        rope = Rope(start_pos, end_pos, segments, width)
        if color:
            rope.color = color
        self.simulator.add_object(rope)
        self.update()
        return rope
    
    def add_ramp(self, position=(0, 0), width=2.0, height=1.0, friction=0.5, color=None):
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
        ramp = Ramp(position, width, height, None, friction)
        if color:
            ramp.color = color
        self.simulator.add_object(ramp)
        self.update()
        return ramp
    
    def clear_objects(self):
        """清除所有物理对象"""
        self.simulator.clear_objects()
        self.update()
    
    def set_object_type(self, object_type):
        """
        设置当前对象类型
        
        参数:
            object_type: 对象类型名称
        """
        self.current_object_type = object_type
    
    def toggle_grid(self, show):
        """
        切换网格显示
        
        参数:
            show: 是否显示网格
        """
        self.show_grid = show
        self.update()
    
    def reset_view(self):
        """重置视图"""
        self.camera.reset()
        
        # 更新代理属性
        self.origin = self.camera.origin
        self.scale = self.camera.scale
        self.current_unit = self.camera.current_unit
        self.current_factor = self.camera.current_factor
        
        # 发送比例变化信号
        self.scaleChanged.emit(self.scale, self.current_unit)
        
        # 重绘视图
        self.update()
    
    def create_object(self, x, y):
        """
        在指定位置创建对象
        
        参数:
            x, y: 物理坐标
            
        返回:
            创建的对象
        """
        # 根据当前类型创建对象
        if self.current_object_type == "长方体":
            return self.add_box(position=(x, y))
        elif self.current_object_type == "圆形":
            return self.add_circle(position=(x, y))
        elif self.current_object_type == "三角形":
            return self.add_triangle(position=(x, y))
        elif self.current_object_type == "弹簧":
            return self.add_spring(start_pos=(x, y), end_pos=(x + 1, y))
        elif self.current_object_type == "轻绳":
            return self.add_rope(start_pos=(x, y), end_pos=(x + 1, y))
        elif self.current_object_type == "斜面":
            return self.add_ramp(position=(x, y))
        
        return None
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        # 删除选中的对象
        if event.key() == Qt.Key_Delete and self.selected_object:
            self.simulator.remove_object(self.selected_object)
            self.selected_object = None
            self.update()
        # 其他键盘操作可以在这里添加
        
    def update_simulation(self, dt=None):
        """
        更新物理模拟
        
        参数:
            dt: 时间步长，如果为None，则使用模拟器计算
            
        返回:
            实际模拟的时间步长
        """
        if dt is None:
            dt = self.simulator.update()
        else:
            # 手动更新物理对象
            for obj in self.simulator.objects:
                obj.update(dt)
                
        # 只有当模拟运行时才重绘
        if self.simulator.is_running:
            self.update()
            
        return dt
    
    def toggle_simulation(self, running):
        """
        切换模拟状态
        
        参数:
            running: 是否运行模拟
        """
        if running:
            self.simulator.start()
        else:
            self.simulator.stop()
    
    def reset_simulation(self):
        """重置模拟"""
        self.simulator.reset()
        # 可以在这里添加重置对象到初始状态的代码
        self.update()
    
    def set_time_scale(self, scale):
        """
        设置时间缩放系数
        
        参数:
            scale: 时间缩放系数
        """
        self.simulator.time_scale = scale
