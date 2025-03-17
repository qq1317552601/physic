from PyQt5.QtWidgets import QMenu, QAction, QColorDialog, QInputDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class ObjectContextMenu:
    """
    对象上下文菜单类
    负责创建和处理物理对象的上下文菜单
    """
    def __init__(self, parent=None):
        """
        初始化上下文菜单管理器
        
        参数:
            parent: 父组件
        """
        self.parent = parent
    
    def show_context_menu(self, pos, obj, update_callback=None):
        """
        显示上下文菜单
        
        参数:
            pos: 菜单显示位置（全局坐标）
            obj: 选中的物理对象
            update_callback: 更新UI的回调函数
        """
        # 创建菜单
        context_menu = QMenu(self.parent)
        
        # 设置菜单样式表，使悬停时文本颜色保持不变
        context_menu.setStyleSheet("""
            QMenu {
                background-color: #F5F5F5;
                border: 1px solid #C0C0C0;
            }
            QMenu::item {
                padding: 5px 20px 5px 20px;
                border: 1px solid transparent;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
                color: black; /* 悬停时保持文本为黑色 */
            }
        """)
        
        # 添加外观菜单项
        appearance_menu = context_menu.addMenu("外观")
        change_color_action = QAction("更改颜色", self.parent)
        change_color_action.triggered.connect(lambda: self.change_object_color(obj, update_callback))
        appearance_menu.addAction(change_color_action)
        
        # 添加速度菜单项
        velocity_menu = context_menu.addMenu("速度")
        set_velocity_x_action = QAction("设置X方向速度", self.parent)
        set_velocity_x_action.triggered.connect(lambda: self.set_object_velocity_x(obj))
        velocity_menu.addAction(set_velocity_x_action)
        
        set_velocity_y_action = QAction("设置Y方向速度", self.parent)
        set_velocity_y_action.triggered.connect(lambda: self.set_object_velocity_y(obj))
        velocity_menu.addAction(set_velocity_y_action)
        
        # 添加属性菜单项
        properties_menu = context_menu.addMenu("属性")
        set_mass_action = QAction("设置质量", self.parent)
        set_mass_action.triggered.connect(lambda: self.set_object_mass(obj))
        properties_menu.addAction(set_mass_action)
        
        # 为不同类型的物体添加不同的大小设置选项
        if hasattr(obj, 'radius'):  # 圆形
            set_radius_action = QAction("设置半径", self.parent)
            set_radius_action.triggered.connect(lambda: self.set_object_radius(obj, update_callback))
            properties_menu.addAction(set_radius_action)
        elif hasattr(obj, 'width') and hasattr(obj, 'height'):  # 矩形
            set_width_action = QAction("设置宽度", self.parent)
            set_width_action.triggered.connect(lambda: self.set_object_width(obj, update_callback))
            properties_menu.addAction(set_width_action)
            
            set_height_action = QAction("设置高度", self.parent)
            set_height_action.triggered.connect(lambda: self.set_object_height(obj, update_callback))
            properties_menu.addAction(set_height_action)
        
        # 几何形状菜单项
        geometry_menu = context_menu.addMenu("几何形为")
        
        # 碰撞检测选项
        collision_action = QAction("与其他物体碰撞", self.parent)
        collision_action.setCheckable(True)
        collision_action.setChecked(not hasattr(obj, 'no_collision') or not obj.no_collision)
        collision_action.triggered.connect(lambda checked: self.set_object_collision(obj, checked))
        geometry_menu.addAction(collision_action)
        
        # 固定位置选项
        fixed_action = QAction("黏附至背景", self.parent)
        fixed_action.setCheckable(True)
        fixed_action.setChecked(hasattr(obj, 'fixed') and obj.fixed)
        fixed_action.triggered.connect(lambda checked: self.set_object_fixed(obj, checked))
        geometry_menu.addAction(fixed_action)
        
        # 添加删除菜单项
        context_menu.addSeparator()  # 添加分隔线
        delete_action = QAction("删除物体", self.parent)
        delete_action.triggered.connect(lambda: self.delete_object(obj, update_callback))
        context_menu.addAction(delete_action)
        
        # 显示菜单
        context_menu.exec_(pos)
    
    def change_object_color(self, obj, update_callback=None):
        """
        更改物体颜色
        
        参数:
            obj: 物理对象
            update_callback: 更新UI的回调函数
        """
        current_color = obj.color
        color = QColorDialog.getColor(current_color, self.parent, "选择物体颜色")
        if color.isValid():
            obj.color = color
            if update_callback:
                update_callback()  # 更新视图
    
    def set_object_velocity_x(self, obj):
        """
        设置物体在X方向上的速度
        
        参数:
            obj: 物理对象
        """
        current_vx = obj.velocity[0]
        vx, ok = QInputDialog.getDouble(
            self.parent, "设置X方向速度", 
            "速度 (m/s):", current_vx,
            -100, 100, 2
        )
        if ok:
            obj.velocity = (vx, obj.velocity[1])
    
    def set_object_velocity_y(self, obj):
        """
        设置物体在Y方向上的速度
        
        参数:
            obj: 物理对象
        """
        current_vy = obj.velocity[1]
        vy, ok = QInputDialog.getDouble(
            self.parent, "设置Y方向速度", 
            "速度 (m/s):", current_vy,
            -100, 100, 2
        )
        if ok:
            obj.velocity = (obj.velocity[0], vy)
    
    def set_object_mass(self, obj):
        """
        设置物体质量
        
        参数:
            obj: 物理对象
        """
        current_mass = obj.mass
        mass, ok = QInputDialog.getDouble(
            self.parent, "设置质量", 
            "质量 (kg):", current_mass,
            0.1, 1000, 2
        )
        if ok and mass > 0:
            obj.mass = mass
    
    def set_object_radius(self, obj, update_callback=None):
        """
        设置圆形物体的半径
        
        参数:
            obj: 圆形物理对象
            update_callback: 更新UI的回调函数
        """
        current_radius = obj.radius
        radius, ok = QInputDialog.getDouble(
            self.parent, "设置半径", 
            "半径 (m):", current_radius,
            0.1, 10, 2
        )
        if ok and radius > 0:
            obj.radius = radius
            if update_callback:
                update_callback()  # 更新视图
    
    def set_object_width(self, obj, update_callback=None):
        """
        设置矩形物体的宽度
        
        参数:
            obj: 矩形物理对象
            update_callback: 更新UI的回调函数
        """
        current_width = obj.width
        width, ok = QInputDialog.getDouble(
            self.parent, "设置宽度", 
            "宽度 (m):", current_width,
            0.1, 10000, 2
        )
        if ok and width > 0:
            obj.width = width
            if update_callback:
                update_callback()  # 更新视图
    
    def set_object_height(self, obj, update_callback=None):
        """
        设置矩形物体的高度
        
        参数:
            obj: 矩形物理对象
            update_callback: 更新UI的回调函数
        """
        current_height = obj.height
        height, ok = QInputDialog.getDouble(
            self.parent, "设置高度", 
            "高度 (m):", current_height,
            0.1, 10000, 2
        )
        if ok and height > 0:
            obj.height = height
            if update_callback:
                update_callback()  # 更新视图
    
    def set_object_collision(self, obj, enabled):
        """
        设置物体是否与其他物体发生碰撞
        
        参数:
            obj: 物理对象
            enabled: 是否启用碰撞
        """
        obj.no_collision = not enabled
    
    def set_object_fixed(self, obj, fixed):
        """
        设置物体是否固定在背景上
        
        参数:
            obj: 物理对象
            fixed: 是否固定
        """
        obj.fixed = fixed
        
        # 如果固定物体，则重置其速度和加速度
        if fixed:
            obj.velocity = (0, 0)
            obj.acceleration = (0, 0)
    
    def delete_object(self, obj, update_callback=None):
        """
        删除物体
        
        参数:
            obj: 要删除的物理对象
            update_callback: 更新UI的回调函数
        """
        # 从物理模拟器中移除物体
        if hasattr(self.parent, 'simulator'):
            self.parent.simulator.remove_object(obj)
            # 如果有选中的物体，且是被删除的物体，则取消选中
            if hasattr(self.parent, 'selected_object') and self.parent.selected_object == obj:
                self.parent.selected_object = None
            # 更新视图
            if update_callback:
                update_callback() 