from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QFormLayout, 
                             QLabel, QDoubleSpinBox, QComboBox, QGroupBox, 
                             QSlider, QPushButton, QCheckBox, QButtonGroup, 
                             QRadioButton, QColorDialog, QLineEdit)
from PyQt5.QtGui import QColor, QKeySequence
from PyQt5.QtCore import Qt, pyqtSignal

class PropertyPanel(QDockWidget):
    """
    属性面板
    用于编辑物理对象的属性
    """
    
    def __init__(self, parent=None):
        """
        初始化属性面板
        
        参数:
            parent: 父窗口
        """
        super().__init__("属性面板", parent)
        self.setMinimumWidth(250)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # 当前选中的物体
        self.selected_object = None
        
        # 创建内容窗口
        content = QWidget()
        self.setWidget(content)
        
        # 主布局
        layout = QVBoxLayout(content)
        
        # 标题标签 - 表示当前状态
        self.title_label = QLabel("未选中物体")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
        layout.addWidget(self.title_label)
        
        # 基本属性组
        basic_group = QGroupBox("基本属性")
        self.basic_layout = QFormLayout()
        
        # 位置
        self.pos_x = QDoubleSpinBox()
        self.pos_x.setRange(-1000, 1000)
        self.pos_x.setValue(0.0)
        self.pos_x.setSingleStep(0.1)
        self.basic_layout.addRow("位置 X (m):", self.pos_x)
        
        self.pos_y = QDoubleSpinBox()
        self.pos_y.setRange(-1000, 1000)
        self.pos_y.setValue(0.0)
        self.pos_y.setSingleStep(0.1)
        self.basic_layout.addRow("位置 Y (m):", self.pos_y)
        
        # 质量
        self.mass = QDoubleSpinBox()
        self.mass.setRange(0.01, 1000)
        self.mass.setValue(1.0)
        self.mass.setSingleStep(0.1)
        self.basic_layout.addRow("质量 (kg):", self.mass)
        
        # 初始速度
        self.vel_x = QDoubleSpinBox()
        self.vel_x.setRange(-100, 100)
        self.vel_x.setValue(0.0)
        self.vel_x.setSingleStep(0.1)
        self.basic_layout.addRow("速度 X (m/s):", self.vel_x)
        
        self.vel_y = QDoubleSpinBox()
        self.vel_y.setRange(-100, 100)
        self.vel_y.setValue(0.0)
        self.vel_y.setSingleStep(0.1)
        self.basic_layout.addRow("速度 Y (m/s):", self.vel_y)
        
        # 颜色选择按钮
        self.color_button = QPushButton("选择颜色...")
        self.color = QColor(200, 200, 255)  # 默认颜色
        self.basic_layout.addRow("颜色:", self.color_button)
        
        basic_group.setLayout(self.basic_layout)
        layout.addWidget(basic_group)
        
        # 特定对象属性组
        specific_group = QGroupBox("特定属性")
        self.specific_layout = QFormLayout()
        specific_group.setLayout(self.specific_layout)
        layout.addWidget(specific_group)
        
        # 创建特定对象的控件
        # 长方体特定属性
        self.box_width = QDoubleSpinBox()
        self.box_width.setRange(0.1, 100)
        self.box_width.setValue(1.0)
        self.box_width.setSingleStep(0.1)
        
        self.box_height = QDoubleSpinBox()
        self.box_height.setRange(0.1, 100)
        self.box_height.setValue(1.0)
        self.box_height.setSingleStep(0.1)
        
        # 圆形特定属性
        self.circle_radius = QDoubleSpinBox()
        self.circle_radius.setRange(0.1, 100)
        self.circle_radius.setValue(0.5)
        self.circle_radius.setSingleStep(0.1)
        
        # 三角形特定属性
        self.triangle_width = QDoubleSpinBox()
        self.triangle_width.setRange(0.1, 100)
        self.triangle_width.setValue(1.0)
        self.triangle_width.setSingleStep(0.1)
        
        self.triangle_height = QDoubleSpinBox()
        self.triangle_height.setRange(0.1, 100)
        self.triangle_height.setValue(1.0)
        self.triangle_height.setSingleStep(0.1)
        
        # 弹簧特定属性
        self.spring_k = QDoubleSpinBox()
        self.spring_k.setRange(0.1, 1000)
        self.spring_k.setValue(10.0)
        self.spring_k.setSingleStep(1.0)
        
        self.spring_end_x = QDoubleSpinBox()
        self.spring_end_x.setRange(-1000, 1000)
        self.spring_end_x.setValue(1.0)
        self.spring_end_x.setSingleStep(0.1)
        
        self.spring_end_y = QDoubleSpinBox()
        self.spring_end_y.setRange(-1000, 1000)
        self.spring_end_y.setValue(0.0)
        self.spring_end_y.setSingleStep(0.1)
        
        # 轻绳特定属性
        self.rope_segments = QSlider(Qt.Horizontal)
        self.rope_segments.setRange(2, 20)
        self.rope_segments.setValue(10)
        
        self.rope_end_x = QDoubleSpinBox()
        self.rope_end_x.setRange(-1000, 1000)
        self.rope_end_x.setValue(1.0)
        self.rope_end_x.setSingleStep(0.1)
        
        self.rope_end_y = QDoubleSpinBox()
        self.rope_end_y.setRange(-1000, 1000)
        self.rope_end_y.setValue(0.0)
        self.rope_end_y.setSingleStep(0.1)
        
        # 斜面特定属性
        self.ramp_width = QDoubleSpinBox()
        self.ramp_width.setRange(0.1, 100)
        self.ramp_width.setValue(2.0)
        self.ramp_width.setSingleStep(0.1)
        
        self.ramp_height = QDoubleSpinBox()
        self.ramp_height.setRange(0.1, 100)
        self.ramp_height.setValue(1.0)
        self.ramp_height.setSingleStep(0.1)
        
        self.ramp_friction = QDoubleSpinBox()
        self.ramp_friction.setRange(0.0, 1.0)
        self.ramp_friction.setValue(0.5)
        self.ramp_friction.setSingleStep(0.05)
        
        # 更新按钮
        self.update_button = QPushButton("更新物体属性")
        self.update_button.setEnabled(False)  # 初始禁用
        layout.addWidget(self.update_button)
        
        # 连接信号
        self.connect_signals()
        
        # 初始化禁用所有控件
        self.enable_controls(False)
    
    def connect_signals(self):
        """连接控件信号"""
        # 基本属性
        self.pos_x.valueChanged.connect(self.update_position)
        self.pos_y.valueChanged.connect(self.update_position)
        self.mass.valueChanged.connect(self.update_mass)
        self.vel_x.valueChanged.connect(self.update_velocity)
        self.vel_y.valueChanged.connect(self.update_velocity)
        self.color_button.clicked.connect(self.choose_color)
        
        # 特定属性
        self.box_width.valueChanged.connect(self.update_box_size)
        self.box_height.valueChanged.connect(self.update_box_size)
        self.circle_radius.valueChanged.connect(self.update_circle_radius)
        self.triangle_width.valueChanged.connect(self.update_triangle_size)
        self.triangle_height.valueChanged.connect(self.update_triangle_size)
        self.spring_k.valueChanged.connect(self.update_spring_properties)
        self.spring_end_x.valueChanged.connect(self.update_spring_properties)
        self.spring_end_y.valueChanged.connect(self.update_spring_properties)
        self.rope_segments.valueChanged.connect(self.update_rope_properties)
        self.rope_end_x.valueChanged.connect(self.update_rope_properties)
        self.rope_end_y.valueChanged.connect(self.update_rope_properties)
        self.ramp_width.valueChanged.connect(self.update_ramp_properties)
        self.ramp_height.valueChanged.connect(self.update_ramp_properties)
        self.ramp_friction.valueChanged.connect(self.update_ramp_properties)
        
        # 更新按钮
        self.update_button.clicked.connect(self.apply_updates)
    
    def enable_controls(self, enabled=True):
        """启用或禁用所有控件"""
        # 基本属性控件
        self.pos_x.setEnabled(enabled)
        self.pos_y.setEnabled(enabled)
        self.mass.setEnabled(enabled)
        self.vel_x.setEnabled(enabled)
        self.vel_y.setEnabled(enabled)
        self.color_button.setEnabled(enabled)
        
        # 更新按钮
        self.update_button.setEnabled(enabled)
    
    def update_position(self):
        """更新物体位置"""
        if self.selected_object and hasattr(self.selected_object, 'position'):
            old_position = self.selected_object.position
            new_position = (self.pos_x.value(), self.pos_y.value())
            
            # 如果位置发生变化，创建命令
            if old_position != new_position:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import MoveObjectCommand
                    command = MoveObjectCommand(
                        self.selected_object,
                        old_position,
                        new_position
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.position = new_position
                    
                # 更新视图
                if hasattr(self.parent(), 'simulation_view'):
                    self.parent().simulation_view.update()
                
    def update_mass(self):
        """更新物体质量"""
        if self.selected_object and hasattr(self.selected_object, 'mass'):
            old_value = self.selected_object.mass
            new_value = self.mass.value()
            
            # 如果值发生变化，创建命令
            if abs(old_value - new_value) > 1e-10:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import ChangePropertyCommand
                    command = ChangePropertyCommand(
                        self.selected_object,
                        'mass',
                        old_value,
                        new_value
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.mass = new_value
                
    def update_velocity(self):
        """更新物体速度"""
        if self.selected_object and hasattr(self.selected_object, 'velocity'):
            old_value = self.selected_object.velocity
            new_value = (self.vel_x.value(), self.vel_y.value())
            
            # 如果值发生变化，创建命令
            if old_value != new_value:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import ChangePropertyCommand
                    command = ChangePropertyCommand(
                        self.selected_object,
                        'velocity',
                        old_value,
                        new_value
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.velocity = new_value
                
    def update_box_size(self):
        """更新矩形大小"""
        if self.selected_object and hasattr(self.selected_object, 'width') and hasattr(self.selected_object, 'height'):
            # 确保不是斜面或三角形
            if not (hasattr(self.selected_object, 'is_ramp') and self.selected_object.is_ramp) and \
               not (hasattr(self.selected_object, 'is_triangle') and self.selected_object.is_triangle):
                old_width = self.selected_object.width
                old_height = self.selected_object.height
                new_width = self.box_width.value()
                new_height = self.box_height.value()
                
                # 如果值发生变化，创建命令
                if abs(old_width - new_width) > 1e-10 or abs(old_height - new_height) > 1e-10:
                    # 获取主窗口
                    main_window = self.parent()
                    if main_window and hasattr(main_window, 'command_history'):
                        # 创建宽度命令
                        from utils.command_history import ChangePropertyCommand
                        if abs(old_width - new_width) > 1e-10:
                            width_command = ChangePropertyCommand(
                                self.selected_object,
                                'width',
                                old_width,
                                new_width
                            )
                            main_window.command_history.execute_command(width_command)
                        
                        # 创建高度命令
                        if abs(old_height - new_height) > 1e-10:
                            height_command = ChangePropertyCommand(
                                self.selected_object,
                                'height',
                                old_height,
                                new_height
                            )
                            main_window.command_history.execute_command(height_command)
                    else:
                        # 如果无法获取主窗口，直接更新
                        self.selected_object.width = new_width
                        self.selected_object.height = new_height
                    
                    # 更新视图
                    if hasattr(self.parent(), 'simulation_view'):
                        self.parent().simulation_view.update()
                
    def update_circle_radius(self):
        """更新圆形半径"""
        if self.selected_object and hasattr(self.selected_object, 'radius'):
            old_value = self.selected_object.radius
            new_value = self.circle_radius.value()
            
            # 如果值发生变化，创建命令
            if abs(old_value - new_value) > 1e-10:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import ChangePropertyCommand
                    command = ChangePropertyCommand(
                        self.selected_object,
                        'radius',
                        old_value,
                        new_value
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.radius = new_value
                
                # 更新视图
                if hasattr(self.parent(), 'simulation_view'):
                    self.parent().simulation_view.update()
                
    def update_triangle_size(self):
        """更新三角形大小"""
        if self.selected_object and hasattr(self.selected_object, 'is_triangle') and self.selected_object.is_triangle:
            old_width = self.selected_object.width
            old_height = self.selected_object.height
            new_width = self.triangle_width.value()
            new_height = self.triangle_height.value()
            
            # 如果值发生变化，创建命令
            if abs(old_width - new_width) > 1e-10 or abs(old_height - new_height) > 1e-10:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    # 创建宽度命令
                    from utils.command_history import ChangePropertyCommand
                    if abs(old_width - new_width) > 1e-10:
                        width_command = ChangePropertyCommand(
                            self.selected_object,
                            'width',
                            old_width,
                            new_width
                        )
                        main_window.command_history.execute_command(width_command)
                    
                    # 创建高度命令
                    if abs(old_height - new_height) > 1e-10:
                        height_command = ChangePropertyCommand(
                            self.selected_object,
                            'height',
                            old_height,
                            new_height
                        )
                        main_window.command_history.execute_command(height_command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.width = new_width
                    self.selected_object.height = new_height
            
            # 更新视图
            if hasattr(self.parent(), 'simulation_view'):
                self.parent().simulation_view.update()
    
    def update_spring_properties(self):
        """更新弹簧属性"""
        if self.selected_object and hasattr(self.selected_object, 'k'):
            old_k = self.selected_object.k
            new_k = self.spring_k.value()
            
            # 如果k值发生变化，创建命令
            if abs(old_k - new_k) > 1e-10:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import ChangePropertyCommand
                    command = ChangePropertyCommand(
                        self.selected_object,
                        'k',
                        old_k,
                        new_k
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.k = new_k
            
            # 更新端点位置
            if hasattr(self.selected_object, 'end_pos'):
                old_end_pos = self.selected_object.end_pos
                new_end_pos = (self.spring_end_x.value(), self.spring_end_y.value())
                
                # 如果端点位置发生变化，创建命令
                if old_end_pos != new_end_pos:
                    # 获取主窗口
                    main_window = self.parent()
                    if main_window and hasattr(main_window, 'command_history'):
                        from utils.command_history import ChangePropertyCommand
                        command = ChangePropertyCommand(
                            self.selected_object,
                            'end_pos',
                            old_end_pos,
                            new_end_pos
                        )
                        main_window.command_history.execute_command(command)
                    else:
                        # 如果无法获取主窗口，直接更新
                        self.selected_object.end_pos = new_end_pos
            
            # 更新视图
            if hasattr(self.parent(), 'simulation_view'):
                self.parent().simulation_view.update()
                
    def update_rope_properties(self):
        """更新轻绳属性"""
        if self.selected_object and hasattr(self.selected_object, 'segments'):
            old_segments = self.selected_object.segments
            new_segments = self.rope_segments.value()
            
            # 如果分段数发生变化，创建命令
            if old_segments != new_segments:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import ChangePropertyCommand
                    command = ChangePropertyCommand(
                        self.selected_object,
                        'segments',
                        old_segments,
                        new_segments
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.segments = new_segments
            
            # 更新端点位置
            if hasattr(self.selected_object, 'end_pos'):
                old_end_pos = self.selected_object.end_pos
                new_end_pos = (self.rope_end_x.value(), self.rope_end_y.value())
                
                # 如果端点位置发生变化，创建命令
                if old_end_pos != new_end_pos:
                    # 获取主窗口
                    main_window = self.parent()
                    if main_window and hasattr(main_window, 'command_history'):
                        from utils.command_history import ChangePropertyCommand
                        command = ChangePropertyCommand(
                            self.selected_object,
                            'end_pos',
                            old_end_pos,
                            new_end_pos
                        )
                        main_window.command_history.execute_command(command)
                    else:
                        # 如果无法获取主窗口，直接更新
                        self.selected_object.end_pos = new_end_pos
            
            # 更新视图
            if hasattr(self.parent(), 'simulation_view'):
                self.parent().simulation_view.update()
                
    def update_ramp_properties(self):
        """更新斜面属性"""
        if self.selected_object and hasattr(self.selected_object, 'is_ramp') and self.selected_object.is_ramp:
            # 更新宽度
            old_width = self.selected_object.width
            new_width = self.ramp_width.value()
            
            # 如果宽度发生变化，创建命令
            if abs(old_width - new_width) > 1e-10:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import ChangePropertyCommand
                    command = ChangePropertyCommand(
                        self.selected_object,
                        'width',
                        old_width,
                        new_width
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.width = new_width
            
            # 更新高度
            old_height = self.selected_object.height
            new_height = self.ramp_height.value()
            
            # 如果高度发生变化，创建命令
            if abs(old_height - new_height) > 1e-10:
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import ChangePropertyCommand
                    command = ChangePropertyCommand(
                        self.selected_object,
                        'height',
                        old_height,
                        new_height
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.height = new_height
            
            # 更新摩擦系数
            if hasattr(self.selected_object, 'friction'):
                old_friction = self.selected_object.friction
                new_friction = self.ramp_friction.value()
                
                # 如果摩擦系数发生变化，创建命令
                if abs(old_friction - new_friction) > 1e-10:
                    # 获取主窗口
                    main_window = self.parent()
                    if main_window and hasattr(main_window, 'command_history'):
                        from utils.command_history import ChangePropertyCommand
                        command = ChangePropertyCommand(
                            self.selected_object,
                            'friction',
                            old_friction,
                            new_friction
                        )
                        main_window.command_history.execute_command(command)
                    else:
                        # 如果无法获取主窗口，直接更新
                        self.selected_object.friction = new_friction
            
            # 更新视图
            if hasattr(self.parent(), 'simulation_view'):
                self.parent().simulation_view.update()
    
    def choose_color(self):
        """打开颜色选择对话框"""
        if not self.selected_object:
            return
            
        color = QColorDialog.getColor(self.color, self, "选择颜色")
        if color.isValid():
            self.color = color
            # 如果有选中的物体，更新其颜色
            if self.selected_object and hasattr(self.selected_object, 'color'):
                old_color = self.selected_object.color
                
                # 获取主窗口
                main_window = self.parent()
                if main_window and hasattr(main_window, 'command_history'):
                    from utils.command_history import ChangePropertyCommand
                    command = ChangePropertyCommand(
                        self.selected_object,
                        'color',
                        old_color,
                        color
                    )
                    main_window.command_history.execute_command(command)
                else:
                    # 如果无法获取主窗口，直接更新
                    self.selected_object.color = color
                
                # 更新视图
                if hasattr(self.parent(), 'simulation_view'):
                    self.parent().simulation_view.update()
    
    def apply_updates(self):
        """应用所有属性更新到选中的物体"""
        if not self.selected_object:
            return
            
        # 更新基本属性
        self.update_position()
        self.update_mass()
        self.update_velocity()
        
        # 根据对象类型更新特定属性
        if hasattr(self.selected_object, 'radius'):  # 圆形
            self.update_circle_radius()
        elif hasattr(self.selected_object, 'is_triangle') and self.selected_object.is_triangle:  # 三角形
            self.update_triangle_size()
        elif hasattr(self.selected_object, 'is_ramp') and self.selected_object.is_ramp:  # 斜面
            self.update_ramp_properties()
        elif hasattr(self.selected_object, 'width') and hasattr(self.selected_object, 'height'):  # 矩形
            self.update_box_size()
        elif hasattr(self.selected_object, 'k'):  # 弹簧
            self.update_spring_properties()
        elif hasattr(self.selected_object, 'segments'):  # 轻绳
            self.update_rope_properties()
        
        # 更新视图
        if hasattr(self.parent(), 'simulation_view'):
            self.parent().simulation_view.update()
            
        # 显示更新成功提示
        if hasattr(self.parent(), 'statusBar'):
            self.parent().statusBar.showMessage("物体属性已更新", 2000)
    
    def clear_specific_layout(self):
        """清除特定属性布局中的所有控件"""
        while self.specific_layout.count():
            item = self.specific_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
        
    def update_for_selected_object(self, obj):
        """
        根据选中的物体更新属性面板
        
        参数:
            obj: 选中的物理对象
        """
        # 暂时断开所有控件的信号连接，避免在更新面板时触发物体更新
        controls = [
            self.pos_x, self.pos_y, self.mass, 
            self.vel_x, self.vel_y, 
            self.box_width, self.box_height,
            self.circle_radius,
            self.triangle_width, self.triangle_height,
            self.spring_k, self.spring_end_x, self.spring_end_y,
            self.rope_segments, self.rope_end_x, self.rope_end_y,
            self.ramp_width, self.ramp_height, self.ramp_friction
        ]
        
        # 保存所有控件的信号状态并阻断信号
        signals_blocked = [control.blockSignals(True) for control in controls]
        
        self.selected_object = obj
        
        # 清除特定属性布局
        self.clear_specific_layout()
        
        if obj is None:
            # 设置标题
            self.title_label.setText("未选中物体")
            # 禁用所有控件
            self.enable_controls(False)
            # 恢复所有控件的信号状态
            for i, control in enumerate(controls):
                control.blockSignals(signals_blocked[i])
            return
        
        try:
            # 启用控件
            self.enable_controls(True)
            
            # 设置标题显示选中的物体类型
            obj_type = "未知"
            
            # 改进对象类型识别逻辑
            if hasattr(obj, 'radius'):
                obj_type = "圆形"
            elif hasattr(obj, 'is_triangle') and obj.is_triangle:
                obj_type = "三角形"
            elif hasattr(obj, 'is_ramp') and obj.is_ramp:
                obj_type = "斜面"
            elif hasattr(obj, 'width') and hasattr(obj, 'height'):
                obj_type = "矩形"
            elif hasattr(obj, 'k'):
                obj_type = "弹簧"
            elif hasattr(obj, 'segments'):
                obj_type = "轻绳"
            
            self.title_label.setText(f"选中物体: {obj_type}")
                
            # 更新基本属性
            if hasattr(obj, 'position'):
                self.pos_x.setValue(obj.position[0])
                self.pos_y.setValue(obj.position[1])
            
            if hasattr(obj, 'mass'):
                self.mass.setValue(obj.mass)
                
            if hasattr(obj, 'velocity'):
                self.vel_x.setValue(obj.velocity[0])
                self.vel_y.setValue(obj.velocity[1])
                
            if hasattr(obj, 'color'):
                self.color = obj.color
                
            # 根据对象类型更新特定属性
            if hasattr(obj, 'radius'):  # 圆形
            self.specific_layout.addRow("半径 (m):", self.circle_radius)
                self.circle_radius.setValue(obj.radius)
            self.circle_radius.show()
            elif hasattr(obj, 'is_ramp') and obj.is_ramp:  # 斜面
                self.specific_layout.addRow("宽度 (m):", self.ramp_width)
                self.specific_layout.addRow("高度 (m):", self.ramp_height)
                self.specific_layout.addRow("摩擦系数:", self.ramp_friction)
                
                self.ramp_width.setValue(obj.width)
                self.ramp_height.setValue(obj.height)
                if hasattr(obj, 'friction'):
                    self.ramp_friction.setValue(obj.friction)
                
                self.ramp_width.show()
                self.ramp_height.show()
                self.ramp_friction.show()
            elif hasattr(obj, 'width') and hasattr(obj, 'height'):  # 矩形或三角形
                if hasattr(obj, 'is_triangle') and obj.is_triangle:
            self.specific_layout.addRow("宽度 (m):", self.triangle_width)
            self.specific_layout.addRow("高度 (m):", self.triangle_height)
                    
                    self.triangle_width.setValue(obj.width)
                    self.triangle_height.setValue(obj.height)
                    
            self.triangle_width.show()
            self.triangle_height.show()
                else:  # 矩形
                    self.specific_layout.addRow("宽度 (m):", self.box_width)
                    self.specific_layout.addRow("高度 (m):", self.box_height)
                    
                    self.box_width.setValue(obj.width)
                    self.box_height.setValue(obj.height)
                    
                    self.box_width.show()
                    self.box_height.show()
            elif hasattr(obj, 'k'):  # 弹簧
            self.specific_layout.addRow("弹性系数 (N/m):", self.spring_k)
            self.specific_layout.addRow("终点 X (m):", self.spring_end_x)
            self.specific_layout.addRow("终点 Y (m):", self.spring_end_y)
                
                self.spring_k.setValue(obj.k)
                if hasattr(obj, 'end_pos'):
                    self.spring_end_x.setValue(obj.end_pos[0])
                    self.spring_end_y.setValue(obj.end_pos[1])
                
            self.spring_k.show()
            self.spring_end_x.show()
            self.spring_end_y.show()
            elif hasattr(obj, 'segments'):  # 轻绳
            self.specific_layout.addRow("分段数:", self.rope_segments)
            self.specific_layout.addRow("终点 X (m):", self.rope_end_x)
            self.specific_layout.addRow("终点 Y (m):", self.rope_end_y)
                
                self.rope_segments.setValue(obj.segments)
                if hasattr(obj, 'end_pos'):
                    self.rope_end_x.setValue(obj.end_pos[0])
                    self.rope_end_y.setValue(obj.end_pos[1])
                
            self.rope_segments.show()
            self.rope_end_x.show()
            self.rope_end_y.show()
        finally:
            # 确保在任何情况下都恢复所有控件的信号状态
            for i, control in enumerate(controls):
                control.blockSignals(signals_blocked[i])

    def keyPressEvent(self, event):
        """处理键盘事件，确保快捷键能够正常工作"""
        # 处理撤销和重做快捷键
        if event.matches(QKeySequence.Undo) or event.matches(QKeySequence.Redo):
            # 将撤销/重做快捷键传递给主窗口
            main_window = self.parent()
            
            if main_window and hasattr(main_window, 'command_history'):
                if event.matches(QKeySequence.Undo):
                    main_window.undo()
                    event.accept()
                    return
                elif event.matches(QKeySequence.Redo):
                    main_window.redo()
                    event.accept()
                    return
        
        # 继续传递事件给基类
        super().keyPressEvent(event)
