from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QFormLayout, 
                             QLabel, QDoubleSpinBox, QComboBox, QGroupBox, 
                             QSlider, QPushButton, QCheckBox, QButtonGroup, 
                             QRadioButton, QColorDialog, QLineEdit)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSignal

class PropertyPanel(QDockWidget):
    """
    属性面板
    用于编辑物理对象的属性
    """
    # 定义信号
    objectTypeChanged = pyqtSignal(str)
    objectCreated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        初始化属性面板
        
        参数:
            parent: 父窗口
        """
        super().__init__("属性面板", parent)
        self.setMinimumWidth(250)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # 创建内容窗口
        content = QWidget()
        self.setWidget(content)
        
        # 主布局
        layout = QVBoxLayout(content)
        
        # 对象类型选择
        type_group = QGroupBox("对象类型")
        type_layout = QVBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["矩形", "圆形", "三角形", "弹簧", "轻绳", "斜面"])
        type_layout.addWidget(self.type_combo)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
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
        
        # 创建按钮
        self.create_button = QPushButton("创建对象")
        layout.addWidget(self.create_button)
        
        # 连接信号
        self.type_combo.currentIndexChanged.connect(self.update_ui_for_type)
        self.color_button.clicked.connect(self.choose_color)
        self.create_button.clicked.connect(self.create_object)
        
        # 初始化UI
        self.update_ui_for_type(0)
    
    def update_ui_for_type(self, index):
        """
        根据选择的对象类型更新UI
        
        参数:
            index: 选择的索引
        """
        # 清除特定属性布局
        while self.specific_layout.count():
            item = self.specific_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
        
        # 获取对象类型
        obj_type = self.type_combo.currentText()
        
        # 根据对象类型添加特定属性
        if obj_type == "矩形":
            self.specific_layout.addRow("宽度 (m):", self.box_width)
            self.specific_layout.addRow("高度 (m):", self.box_height)
            self.box_width.show()
            self.box_height.show()
        elif obj_type == "圆形":
            self.specific_layout.addRow("半径 (m):", self.circle_radius)
            self.circle_radius.show()
        elif obj_type == "三角形":
            self.specific_layout.addRow("宽度 (m):", self.triangle_width)
            self.specific_layout.addRow("高度 (m):", self.triangle_height)
            self.triangle_width.show()
            self.triangle_height.show()
        elif obj_type == "弹簧":
            self.specific_layout.addRow("弹性系数 (N/m):", self.spring_k)
            self.specific_layout.addRow("终点 X (m):", self.spring_end_x)
            self.specific_layout.addRow("终点 Y (m):", self.spring_end_y)
            self.spring_k.show()
            self.spring_end_x.show()
            self.spring_end_y.show()
        elif obj_type == "轻绳":
            self.specific_layout.addRow("分段数:", self.rope_segments)
            self.specific_layout.addRow("终点 X (m):", self.rope_end_x)
            self.specific_layout.addRow("终点 Y (m):", self.rope_end_y)
            self.rope_segments.show()
            self.rope_end_x.show()
            self.rope_end_y.show()
        elif obj_type == "斜面":
            self.specific_layout.addRow("宽度 (m):", self.ramp_width)
            self.specific_layout.addRow("高度 (m):", self.ramp_height)
            self.specific_layout.addRow("摩擦系数:", self.ramp_friction)
            self.ramp_width.show()
            self.ramp_height.show()
            self.ramp_friction.show()
        
        # 发送信号通知对象类型变更
        self.objectTypeChanged.emit(obj_type)
    
    def choose_color(self):
        """打开颜色选择对话框"""
        color = QColorDialog.getColor(self.color, self, "选择颜色")
        if color.isValid():
            self.color = color
    
    def create_object(self):
        """创建对象并发送信号"""
        # 基本属性
        props = {
            "type": self.type_combo.currentText(),
            "position": (self.pos_x.value(), self.pos_y.value()),
            "mass": self.mass.value(),
            "velocity": (self.vel_x.value(), self.vel_y.value()),
            "color": self.color
        }
        
        # 特定属性
        obj_type = self.type_combo.currentText()
        if obj_type == "矩形":
            props["width"] = self.box_width.value()
            props["height"] = self.box_height.value()
        elif obj_type == "圆形":
            props["radius"] = self.circle_radius.value()
        elif obj_type == "三角形":
            props["width"] = self.triangle_width.value()
            props["height"] = self.triangle_height.value()
        elif obj_type == "弹簧":
            props["k"] = self.spring_k.value()
            props["end_pos"] = (self.spring_end_x.value(), self.spring_end_y.value())
        elif obj_type == "轻绳":
            props["segments"] = self.rope_segments.value()
            props["end_pos"] = (self.rope_end_x.value(), self.rope_end_y.value())
        elif obj_type == "斜面":
            props["width"] = self.ramp_width.value()
            props["height"] = self.ramp_height.value()
            props["friction"] = self.ramp_friction.value()
        
        # 发送信号
        self.objectCreated.emit(props)
