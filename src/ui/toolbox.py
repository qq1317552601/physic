from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QGroupBox, 
                             QPushButton, QCheckBox, QButtonGroup, QRadioButton,
                             QSlider, QLabel, QFormLayout, QHBoxLayout, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal

class ToolboxPanel(QDockWidget):
    """
    工具箱面板
    提供模拟控制和对象选择工具
    """
    # 定义信号
    objectTypeSelected = pyqtSignal(str)
    simulationToggled = pyqtSignal(bool)
    simulationReset = pyqtSignal()
    drawModeToggled = pyqtSignal(bool)
    gridToggled = pyqtSignal(bool)
    viewReset = pyqtSignal()
    timeScaleChanged = pyqtSignal(float)
    gravityChanged = pyqtSignal(float, float)  # 新增重力变化信号
    
    def __init__(self, parent=None):
        """
        初始化工具箱面板
        
        参数:
            parent: 父窗口
        """
        super().__init__("工具箱", parent)
        self.setMinimumWidth(200)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # 创建内容窗口
        content = QWidget()
        self.setWidget(content)
        
        # 主布局
        layout = QVBoxLayout(content)
        
        # 模拟控制组
        simulation_group = QGroupBox("模拟控制")
        sim_layout = QVBoxLayout()
        
        # 开始/暂停按钮
        self.sim_toggle_button = QPushButton("开始模拟")
        self.sim_toggle_button.setCheckable(True)
        sim_layout.addWidget(self.sim_toggle_button)
        
        # 重置按钮
        self.reset_button = QPushButton("重置模拟")
        sim_layout.addWidget(self.reset_button)
        
        # 时间比例尺滑块
        time_layout = QFormLayout()
        self.time_scale_slider = QSlider(Qt.Horizontal)
        self.time_scale_slider.setRange(1, 200)
        self.time_scale_slider.setValue(100)
        self.time_scale_label = QLabel("时间比例: 1.0x")
        time_layout.addRow(self.time_scale_label, self.time_scale_slider)
        sim_layout.addLayout(time_layout)
        
        # 添加重力控制
        gravity_layout = QFormLayout()
        self.gravity_y = QDoubleSpinBox()
        self.gravity_y.setRange(-100, 100)
        self.gravity_y.setValue(-9.8)
        self.gravity_y.setSingleStep(0.1)
        self.gravity_y.setDecimals(2)
        gravity_layout.addRow("重力 (m/s²):", self.gravity_y)
        
        sim_layout.addLayout(gravity_layout)
        
        simulation_group.setLayout(sim_layout)
        layout.addWidget(simulation_group)
        
        # 视图控制组
        view_group = QGroupBox("视图控制")
        view_layout = QVBoxLayout()
        
        # 显示网格选项
        self.grid_checkbox = QCheckBox("显示网格")
        self.grid_checkbox.setChecked(True)
        view_layout.addWidget(self.grid_checkbox)
        
        # 绘制模式选项
        self.draw_mode_checkbox = QCheckBox("绘制模式")
        view_layout.addWidget(self.draw_mode_checkbox)
        
        # 重置视图按钮
        self.reset_view_button = QPushButton("重置视图")
        view_layout.addWidget(self.reset_view_button)
        
        # 清除所有对象按钮
        self.clear_objects_button = QPushButton("清除所有对象")
        view_layout.addWidget(self.clear_objects_button)
        
        view_group.setLayout(view_layout)
        layout.addWidget(view_group)
        
        # 对象类型选择组
        objects_group = QGroupBox("对象选择")
        objects_layout = QVBoxLayout()
        
        # 创建对象类型按钮组
        self.object_type_group = QButtonGroup(self)
        
        # 创建各种对象类型的单选按钮
        object_types = [
            ("选择", "select"),
            ("矩形", "box"),
            ("圆形", "circle"),
            ("三角形", "triangle"),
            ("弹簧", "spring"),
            ("轻绳", "rope"),
            ("斜面", "ramp")
        ]
        
        for i, (label, obj_type) in enumerate(object_types):
            radio = QRadioButton(label)
            self.object_type_group.addButton(radio, i)
            objects_layout.addWidget(radio)
            
            # 默认选择第一个
            if i == 0:
                radio.setChecked(True)
        
        objects_group.setLayout(objects_layout)
        layout.addWidget(objects_group)
        
        # 连接信号
        self.sim_toggle_button.toggled.connect(self.toggle_simulation)
        self.reset_button.clicked.connect(self.reset_simulation)
        self.grid_checkbox.toggled.connect(self.toggle_grid)
        self.draw_mode_checkbox.toggled.connect(self.toggle_draw_mode)
        self.reset_view_button.clicked.connect(self.reset_view)
        self.object_type_group.buttonClicked.connect(self.set_object_type)
        self.time_scale_slider.valueChanged.connect(self.update_time_scale)
        self.gravity_y.valueChanged.connect(self.update_gravity)
    
    def toggle_simulation(self, checked):
        """
        切换模拟状态
        
        参数:
            checked: 是否选中
        """
        if checked:
            self.sim_toggle_button.setText("暂停模拟")
        else:
            self.sim_toggle_button.setText("开始模拟")
        
        # 发送信号
        self.simulationToggled.emit(checked)
    
    def reset_simulation(self):
        """重置模拟"""
        # 确保模拟按钮状态为未选中
        self.sim_toggle_button.setChecked(False)
        self.sim_toggle_button.setText("开始模拟")
        
        # 发送信号
        self.simulationReset.emit()
    
    def toggle_grid(self, checked):
        """
        切换网格显示
        
        参数:
            checked: 是否选中
        """
        # 发送信号
        self.gridToggled.emit(checked)
    
    def toggle_draw_mode(self, checked):
        """
        切换绘制模式
        
        参数:
            checked: 是否选中
        """
        # 发送信号
        self.drawModeToggled.emit(checked)
    
    def reset_view(self):
        """重置视图"""
        # 发送信号
        self.viewReset.emit()
    
    def set_object_type(self, button):
        """
        设置对象类型
        
        参数:
            button: 选中的按钮
        """
        # 获取对象类型
        index = self.object_type_group.id(button)
        object_types = ["选择", "矩形", "圆形", "三角形", "弹簧", "轻绳", "斜面"]
        obj_type = object_types[index]
        
        # 发送信号
        self.objectTypeSelected.emit(obj_type)
    
    def update_time_scale(self, value):
        """
        更新时间比例
        
        参数:
            value: 滑块值
        """
        # 计算实际比例值 (0.1x - 2.0x)
        scale = value / 100.0
        
        # 更新标签
        self.time_scale_label.setText(f"时间比例: {scale:.1f}x")
        
        # 发送信号
        self.timeScaleChanged.emit(scale)
    
    def update_gravity(self):
        """更新重力设置"""
        # 发送重力变化信号，X方向固定为0
        self.gravityChanged.emit(0.0, self.gravity_y.value())
