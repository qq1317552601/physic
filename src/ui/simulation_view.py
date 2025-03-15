import math
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QColorDialog, QInputDialog, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF, pyqtSignal

# 导入物理对象
from physics.objects import PhysicsObject, Box, Circle, Triangle, Spring, Rope, Ramp
from physics.simulator import PhysicsSimulator

# 导入渲染和相机模块
from rendering.camera import Camera
from rendering.renderer import Renderer

# 导入新的上下文菜单和对象工厂类
from .context_menu import ObjectContextMenu
from .object_factory import ObjectFactory

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
        
        # 初始化上下文菜单管理器
        self.context_menu = ObjectContextMenu(self)
        
        # 初始化对象工厂
        self.object_factory = ObjectFactory(self.simulator)
        
        # 网格和坐标系参数
        self.show_grid = True
        
        # 鼠标状态
        self.mouse_pressed = False
        self.last_mouse_pos = None
        self.selected_object = None
        self.hover_object = None  # 鼠标悬停的物体
        self.draw_mode = False
        self.select_mode = True  # 默认为选择模式
        self.current_object_type = "选择"  # 默认为选择工具
        
        # 拖动创建物体相关变量
        self.is_drawing_rect = False
        self.is_drawing_circle = False
        self.rect_start_pos = None
        self.circle_center = None
        
        # 访问相机属性的代理方法（为了兼容性）
        self.origin = self.camera.origin
        self.scale = self.camera.scale
        self.current_unit = self.camera.current_unit
        self.current_factor = self.camera.current_factor
    
    def showEvent(self, event):
        """处理视图显示事件，确保相机尺寸与实际视图尺寸一致"""
        super().showEvent(event)
        # 在视图首次显示时更新相机尺寸
        self.camera.resize(self.width(), self.height())
        # 更新代理属性
        self.origin = self.camera.origin
        self.scale = self.camera.scale
    
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
        
        # 根据当前模式处理鼠标事件
        if self.select_mode and event.button() == Qt.LeftButton:
            # 选择模式：选中或取消选中物体
            self.selected_object = self.simulator.get_object_at(phys_x, phys_y)
        elif self.select_mode and event.button() == Qt.RightButton:
            # 右键菜单：检查点击位置是否有物体
            obj = self.simulator.get_object_at(phys_x, phys_y)
            if obj:
                # 如果点击的物体与当前选中的物体不同，则先选中它
                if obj != self.selected_object:
                    self.selected_object = obj
                    self.update()  # 更新视图
                
                # 显示右键菜单
                self.context_menu.show_context_menu(event.globalPos(), obj, self.update)
        elif self.draw_mode and event.button() == Qt.LeftButton:
            # 绘制模式：开始创建物体
            if self.current_object_type == "矩形":
                # 记录矩形起始位置，但不立即创建
                self.is_drawing_rect = True
                self.rect_start_pos = (phys_x, phys_y)
            elif self.current_object_type == "圆形":
                # 记录圆心位置，但不立即创建
                self.is_drawing_circle = True
                self.circle_center = (phys_x, phys_y)
            else:
                # 其他对象仍然使用单击创建
                self.create_object(phys_x, phys_y)
        else:
            # 其他按钮或模式的处理
            pass
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        # 如果是选择模式，保持选中状态
        if self.select_mode:
            # 不重置选中对象，只更新鼠标状态
            self.mouse_pressed = False
            self.update()  # 更新视图
            return
            
        # 如果正在绘制矩形并释放左键，完成矩形创建
        if self.is_drawing_rect and event.button() == Qt.LeftButton and self.rect_start_pos:
            # 获取当前物理坐标作为矩形终点
            phys_x, phys_y = self.camera.from_screen_coords(event.x(), event.y())
            
            # 计算矩形的中心点、宽度和高度
            center_x = (self.rect_start_pos[0] + phys_x) / 2
            center_y = (self.rect_start_pos[1] + phys_y) / 2
            width = abs(phys_x - self.rect_start_pos[0])
            height = abs(phys_y - self.rect_start_pos[1])
            
            # 创建矩形（如果宽度和高度都大于0）
            if width > 0 and height > 0:
                self.object_factory.add_box(position=(center_x, center_y), width=width, height=height)
            
            # 重置绘制状态
            self.is_drawing_rect = False
            self.rect_start_pos = None
            
            # 强制更新视图以确保使用正确的边框样式
            self.update()
        
        # 如果正在绘制圆形并释放左键，完成圆形创建
        elif self.is_drawing_circle and event.button() == Qt.LeftButton and self.circle_center:
            # 获取当前物理坐标
            phys_x, phys_y = self.camera.from_screen_coords(event.x(), event.y())
            
            # 计算半径（圆心到当前点的距离）
            dx = phys_x - self.circle_center[0]
            dy = phys_y - self.circle_center[1]
            radius = math.sqrt(dx*dx + dy*dy)
            
            # 创建圆形（如果半径大于0）
            if radius > 0:
                self.object_factory.add_circle(position=self.circle_center, radius=radius)
            
            # 重置绘制状态
            self.is_drawing_circle = False
            self.circle_center = None
            
            # 强制更新视图以确保使用正确的边框样式
            self.update()
        
        # 更新鼠标状态
        self.mouse_pressed = False
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        # 获取物理坐标
        phys_x, phys_y = self.camera.from_screen_coords(event.x(), event.y())
        
        # 发送鼠标位置信号
        self.mousePositionChanged.emit(phys_x, phys_y)
        
        # 在选择模式下，始终检测鼠标悬停在哪个物体上
        if self.select_mode:
            obj = self.simulator.get_object_at(phys_x, phys_y)
            if obj != self.hover_object:  # 只有当悬停的物体发生变化时才更新
                self.hover_object = obj
                self.update()  # 重绘视图以显示悬停效果
        else:
            # 非选择模式下清除悬停对象
            if self.hover_object is not None:
                self.hover_object = None
                self.update()
        
        # 如果正在绘制物体，更新视图以显示预览
        if (self.is_drawing_rect and self.rect_start_pos) or (self.is_drawing_circle and self.circle_center):
            self.update()  # 触发重绘以显示预览
        
        # 如果鼠标按下且不在绘制模式，平移视图或移动选中对象
        if self.mouse_pressed and self.last_mouse_pos and not (self.is_drawing_rect or self.is_drawing_circle):
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
            elif event.buttons() & Qt.MiddleButton:
                # 平移视图（使用鼠标中键）
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
        
        # 如果正在绘制矩形，绘制预览
        if self.is_drawing_rect and self.rect_start_pos and self.last_mouse_pos:
            # 获取当前鼠标位置的物理坐标
            phys_x, phys_y = self.camera.from_screen_coords(self.last_mouse_pos.x(), self.last_mouse_pos.y())
            
            # 计算矩形的屏幕坐标
            start_x, start_y = self.camera.to_screen_coords(self.rect_start_pos[0], self.rect_start_pos[1])
            end_x, end_y = self.camera.to_screen_coords(phys_x, phys_y)
            
            # 计算矩形的左上角和尺寸
            rect_x = min(start_x, end_x)
            rect_y = min(start_y, end_y)
            rect_width = abs(end_x - start_x)
            rect_height = abs(end_y - start_y)
            
            # 设置半透明的填充颜色和边框
            painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.DashLine))
            painter.setBrush(QBrush(QColor(200, 200, 255, 128)))  # 半透明的浅蓝色
            
            # 绘制预览矩形
            painter.drawRect(int(rect_x), int(rect_y), int(rect_width), int(rect_height))
        
        # 如果正在绘制圆形，绘制预览
        elif self.is_drawing_circle and self.circle_center and self.last_mouse_pos:
            # 获取当前鼠标位置的物理坐标
            phys_x, phys_y = self.camera.from_screen_coords(self.last_mouse_pos.x(), self.last_mouse_pos.y())
            
            # 计算半径（物理单位）
            dx = phys_x - self.circle_center[0]
            dy = phys_y - self.circle_center[1]
            radius = math.sqrt(dx*dx + dy*dy)
            
            # 转换为屏幕坐标
            center_x, center_y = self.camera.to_screen_coords(self.circle_center[0], self.circle_center[1])
            screen_radius = radius * self.camera.scale
            
            # 设置半透明的填充颜色和边框
            painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.DashLine))
            painter.setBrush(QBrush(QColor(200, 200, 255, 128)))  # 半透明的浅蓝色
            
            # 绘制预览圆形
            painter.drawEllipse(int(center_x - screen_radius), int(center_y - screen_radius), 
                               int(screen_radius * 2), int(screen_radius * 2))
    
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
        box = self.object_factory.add_box(position, width, height, mass, velocity, color)
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
        circle = self.object_factory.add_circle(position, radius, mass, velocity, color)
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
        triangle = self.object_factory.add_triangle(position, size, mass, velocity, color)
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
        spring = self.object_factory.add_spring(start_pos, end_pos, k, width, color)
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
        rope = self.object_factory.add_rope(start_pos, end_pos, segments, width, color)
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
        ramp = self.object_factory.add_ramp(position, width, height, friction, color)
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
        
        # 根据选择的工具切换模式
        if object_type == "选择":
            self.select_mode = True
            self.draw_mode = False
        else:
            self.select_mode = False
            self.draw_mode = True  # 非选择模式则为绘制模式
            
        # 切换模式时清除悬停物体
        self.hover_object = None
        
        # 更新视图以反映变化
        self.update()
    
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
        obj = self.object_factory.create_object(self.current_object_type, x, y)
        if obj:
            self.update()  # 重绘视图
        return obj
    
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
            # 开始模拟前，确保所有物体的加速度重置为初始状态
            # 这样重力会在下一次更新中正确应用
            for obj in self.simulator.objects:
                if hasattr(obj, 'mass') and obj.mass > 0:
                    obj.acceleration = (0, 0)
            self.simulator.start()
        else:
            self.simulator.stop()
    
    def reset_simulation(self):
        """重置模拟"""
        self.simulator.reset()
        
        # 重置所有物体的速度和加速度
        for obj in self.simulator.objects:
            if hasattr(obj, 'velocity'):
                obj.velocity = (0, 0)
            if hasattr(obj, 'acceleration'):
                obj.acceleration = (0, 0)
                
        # 更新视图
        self.update()
    
    def set_time_scale(self, scale):
        """
        设置时间缩放系数
        
        参数:
            scale: 时间缩放系数
        """
        self.simulator.time_scale = scale
    
    def toggle_draw_mode(self, state):
        """
        切换绘制模式
        
        参数:
            state: 是否启用绘制模式
        """
        self.draw_mode = state
        
        # 如果启用绘制模式，则禁用选择模式并清除悬停物体
        if state:
            self.select_mode = False
            self.hover_object = None
        else:
            # 如果当前工具是"选择"，则启用选择模式
            self.select_mode = (self.current_object_type == "选择")
        
        # 更新视图以反映模式变化
        self.update()
