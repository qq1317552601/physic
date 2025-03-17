import math
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QColorDialog, QInputDialog, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF, QKeySequence
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
    objectSelected = pyqtSignal(object)  # 新增选中物体信号
    
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
            prev_selected = self.selected_object
            self.selected_object = self.simulator.get_object_at(phys_x, phys_y)
            
            # 只有在选中物体变化时才发出信号
            if self.selected_object != prev_selected:
                # 如果选中了新物体，发出信号通知
                if self.selected_object:
                    self.objectSelected.emit(self.selected_object)
                # 如果取消选中，发出信号通知（传递None）
                elif prev_selected:
                    self.objectSelected.emit(None)
        elif self.select_mode and event.button() == Qt.RightButton:
            # 右键菜单：检查点击位置是否有物体
            obj = self.simulator.get_object_at(phys_x, phys_y)
            if obj:
                # 如果点击的物体与当前选中的物体不同，则先选中它
                if obj != self.selected_object:
                    self.selected_object = obj
                    self.objectSelected.emit(obj)
                    self.update()  # 更新视图
                
                # 显示右键菜单
                self.context_menu.show_context_menu(event.globalPos(), obj, self.update)
        elif self.draw_mode and event.button() == Qt.LeftButton:
            # 绘制模式：开始创建物体
            if self.current_object_type == "矩形":
                # 记录矩形起始位置（吸附到网格），但不立即创建
                self.is_drawing_rect = True
                self.rect_start_pos = self.snap_to_grid(phys_x, phys_y)
            elif self.current_object_type == "圆形":
                # 记录圆心位置（吸附到网格），但不立即创建
                self.is_drawing_circle = True
                self.circle_center = self.snap_to_grid(phys_x, phys_y)
            else:
                # 其他对象仍然使用单击创建（已经通过create_object方法实现了吸附）
                self.create_object(phys_x, phys_y)
        else:
            # 其他按钮或模式的处理
            pass
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        # 如果是选择模式，保持选中状态
        if self.select_mode:
            # 如果拖动了物体，创建移动命令
            if self.selected_object and hasattr(self, 'drag_start_position'):
                # 获取结束位置
                end_position = self.selected_object.position
                
                # 如果位置发生了变化，创建命令
                if self.drag_start_position != end_position:
                    # 获取主窗口引用
                    main_window = self.parent()
                    while main_window and not hasattr(main_window, 'command_history'):
                        main_window = main_window.parent()
                    
                    # 如果找到主窗口，创建移动命令
                    if main_window and hasattr(main_window, 'command_history'):
                        from utils.command_history import MoveObjectCommand
                        command = MoveObjectCommand(
                            self.selected_object, 
                            self.drag_start_position, 
                            end_position
                        )
                        main_window.command_history.execute_command(command)
                        
                # 清除拖动开始位置
                delattr(self, 'drag_start_position')
            
            # 不重置选中对象，只更新鼠标状态
            self.mouse_pressed = False
            self.update()  # 更新视图
            return
            
        # 如果正在绘制矩形并释放左键，完成矩形创建
        if self.is_drawing_rect and event.button() == Qt.LeftButton and self.rect_start_pos:
            # 获取当前物理坐标作为矩形终点，并吸附到网格
            phys_x, phys_y = self.camera.from_screen_coords(event.x(), event.y())
            end_pos = self.snap_to_grid(phys_x, phys_y)
            
            # 计算矩形的中心点、宽度和高度
            center_x = (self.rect_start_pos[0] + end_pos[0]) / 2
            center_y = (self.rect_start_pos[1] + end_pos[1]) / 2
            width = abs(end_pos[0] - self.rect_start_pos[0])
            height = abs(end_pos[1] - self.rect_start_pos[1])
            
            # 创建矩形（如果宽度和高度都大于0）
            if width > 0 and height > 0:
                # 吸附中心点到网格
                center_pos = self.snap_to_grid(center_x, center_y)
                self.object_factory.add_box(position=center_pos, width=width, height=height)
            
            # 重置绘制状态
            self.is_drawing_rect = False
            self.rect_start_pos = None
            
            # 强制更新视图以确保使用正确的边框样式
            self.update()
        
        # 如果正在绘制圆形并释放左键，完成圆形创建
        elif self.is_drawing_circle and event.button() == Qt.LeftButton and self.circle_center:
            # 获取当前物理坐标，并吸附到网格
            phys_x, phys_y = self.camera.from_screen_coords(event.x(), event.y())
            end_pos = self.snap_to_grid(phys_x, phys_y)
            
            # 计算半径（圆心到当前点的距离）
            dx = end_pos[0] - self.circle_center[0]
            dy = end_pos[1] - self.circle_center[1]
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
                # 保存原位置用于创建命令
                if not hasattr(self, 'drag_start_position'):
                    self.drag_start_position = old_pos
                
                # 取消吸附，直接使用计算出的位置
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
            # 获取当前鼠标位置的物理坐标，并应用吸附
            phys_x, phys_y = self.camera.from_screen_coords(self.last_mouse_pos.x(), self.last_mouse_pos.y())
            end_pos = self.snap_to_grid(phys_x, phys_y)
            
            # 计算矩形的屏幕坐标
            start_x, start_y = self.camera.to_screen_coords(self.rect_start_pos[0], self.rect_start_pos[1])
            end_x, end_y = self.camera.to_screen_coords(end_pos[0], end_pos[1])
            
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
            # 获取当前鼠标位置的物理坐标，并应用吸附
            phys_x, phys_y = self.camera.from_screen_coords(self.last_mouse_pos.x(), self.last_mouse_pos.y())
            end_pos = self.snap_to_grid(phys_x, phys_y)
            
            # 计算半径（物理单位）
            dx = end_pos[0] - self.circle_center[0]
            dy = end_pos[1] - self.circle_center[1]
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
    
    def snap_to_grid(self, x, y):
        """
        将坐标吸附到最近的网格点
        
        参数:
            x, y: 物理坐标
            
        返回:
            吸附后的坐标元组 (x, y)
        """
        # 获取当前渲染器中使用的网格间隔
        grid_interval = self.renderer._calculate_nice_tick_interval(
            max(self.width() / self.scale, self.height() / self.scale),
            target_count=10
        )
        
        # 计算标准化间隔
        exponent = math.floor(math.log10(grid_interval))
        normalized_interval = grid_interval / (10 ** exponent)
        
        # 确保只吸附到整数格子
        if normalized_interval == 5:  # 针对5的倍数间隔特殊处理
            # 使用更大的单位间隔（10的幂次）
            snapping_interval = 10 ** exponent
        elif normalized_interval == 2:  # 针对2的倍数间隔特殊处理
            # 使用2的倍数作为间隔
            snapping_interval = 2 * (10 ** exponent)
        else:
            # 使用整数倍的基本间隔
            snapping_interval = grid_interval
        
        # 吸附阈值（减小为网格间隔的5%，提高响应性）
        snap_threshold = grid_interval * 0.05
        
        # 计算最近的整数格点
        grid_x = round(x / snapping_interval) * snapping_interval
        grid_y = round(y / snapping_interval) * snapping_interval
        
        # 计算到网格点的距离
        dx = abs(x - grid_x)
        dy = abs(y - grid_y)
        
        # 如果距离小于阈值，则吸附到网格点
        snapped_x = grid_x if dx < snap_threshold else x
        snapped_y = grid_y if dy < snap_threshold else y
        
        return (snapped_x, snapped_y)
    
    def create_object(self, x, y):
        """
        在指定位置创建对象
        
        参数:
            x, y: 物理坐标
            
        返回:
            创建的对象
        """
        # 吸附坐标到网格
        snapped_x, snapped_y = self.snap_to_grid(x, y)
        
        obj = self.object_factory.create_object(self.current_object_type, snapped_x, snapped_y)
        if obj:
            self.update()
        return obj
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        # 处理撤销和重做快捷键
        if event.matches(QKeySequence.Undo) or event.matches(QKeySequence.Redo):
            # 将撤销/重做快捷键传递给主窗口
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'command_history'):
                main_window = main_window.parent()
            
            if main_window and hasattr(main_window, 'command_history'):
                if event.matches(QKeySequence.Undo):
                    main_window.undo()
                    event.accept()
                    return
                elif event.matches(QKeySequence.Redo):
                    main_window.redo()
                    event.accept()
                    return
        
        # 删除选中的对象
        if event.key() == Qt.Key_Delete and self.selected_object:
            # 获取主窗口以执行删除命令
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'command_history'):
                main_window = main_window.parent()
            
            if main_window and hasattr(main_window, 'command_history'):
                main_window.delete_selected()
                event.accept()
                return
            else:
                # 如果找不到主窗口，直接从模拟器中删除对象
                self.simulator.remove_object(self.selected_object)
                self.selected_object = None
                self.update()
                return
            
        # 当有选中物体时，处理方向键移动
        if self.selected_object:
            # 获取当前网格间隔（使用渲染器计算的当前可见网格大小）
            grid_interval = self.renderer._calculate_nice_tick_interval(
                max(self.width() / self.scale, self.height() / self.scale),
                target_count=10
            )
            
            # 当前物体位置
            curr_pos = self.selected_object.position
            new_pos = None
            
            # 根据按键移动物体，始终移动一个网格单位
            if event.key() == Qt.Key_Left:
                # 左移一个网格单位
                new_pos = (curr_pos[0] - grid_interval, curr_pos[1])
            elif event.key() == Qt.Key_Right:
                # 右移一个网格单位
                new_pos = (curr_pos[0] + grid_interval, curr_pos[1])
            elif event.key() == Qt.Key_Up:
                # 上移一个网格单位
                new_pos = (curr_pos[0], curr_pos[1] + grid_interval)
            elif event.key() == Qt.Key_Down:
                # 下移一个网格单位
                new_pos = (curr_pos[0], curr_pos[1] - grid_interval)
            
            # 如果位置改变，创建移动命令
            if new_pos:
                # 获取主窗口以执行移动命令
                main_window = self.parent()
                while main_window and not hasattr(main_window, 'command_history'):
                    main_window = main_window.parent()
                
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import MoveObjectCommand
                    command = MoveObjectCommand(self.selected_object, curr_pos, new_pos)
                    main_window.command_history.execute_command(command)
                else:
                    # 如果找不到主窗口，直接更新位置
                    self.selected_object.position = new_pos
                
                self.update()
                event.accept()
                return
    
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
