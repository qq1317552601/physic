import math
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QToolBar, QAction, QDockWidget, QFormLayout, QLabel, QDoubleSpinBox,
                            QComboBox, QGroupBox, QSlider, QPushButton, QStatusBar, QSplitter,
                            QCheckBox, QButtonGroup, QRadioButton)
from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from .simulation_view import SimulationView
from .property_panel import PropertyPanel
from .toolbox import ToolboxPanel
from utils.config import config

class MainWindow(QMainWindow):
    """
    主窗口类
    应用程序的主界面
    """
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.setWindowTitle("物理运动学可视化软件")
        self.resize(1200, 800)
        
        # 创建中央组件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建布局
        self.layout = QVBoxLayout(self.central_widget)
        
        # 创建模拟视图
        self.simulation_view = SimulationView()
        self.layout.addWidget(self.simulation_view)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建属性面板
        self.property_panel = PropertyPanel(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.property_panel)
        
        # 创建工具箱面板
        self.toolbox_panel = ToolboxPanel(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toolbox_panel)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 更新状态栏 - 修复状态栏标签创建方式
        self.mouse_pos_label = QLabel("位置: (0.00, 0.00)")
        self.statusBar.addPermanentWidget(self.mouse_pos_label)
        
        self.scale_label = QLabel("比例: 50.0 像素/m")
        self.statusBar.addPermanentWidget(self.scale_label)
        
        self.fps_label = QLabel("FPS: 0.0")
        self.statusBar.addPermanentWidget(self.fps_label)
        
        # 创建模拟计时器
        self.simulation_timer = QTimer()
        self.simulation_timer.setInterval(16)  # 约60FPS
        self.simulation_timer.timeout.connect(self.update_simulation)
        
        # 上次更新时间
        self.last_update_time = None
        self.fps_count = 0
        self.fps_timer = 0
        self.current_fps = 0
        
        # 连接信号
        self.connect_signals()
        
        # 加载配置
        self.load_config()
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 添加动作
        new_action = QAction("新建", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 连接模拟视图信号
        self.simulation_view.mousePositionChanged.connect(self.update_mouse_position)
        self.simulation_view.scaleChanged.connect(self.update_scale_info)
        
        # 连接属性面板信号
        self.property_panel.objectTypeChanged.connect(self.update_object_type)
        self.property_panel.objectCreated.connect(self.create_object)
        
        # 连接工具箱面板信号
        self.toolbox_panel.objectTypeSelected.connect(self.set_object_type)
        self.toolbox_panel.simulationToggled.connect(self.toggle_simulation)
        self.toolbox_panel.simulationReset.connect(self.reset_simulation)
        self.toolbox_panel.drawModeToggled.connect(self.toggle_draw_mode)
        self.toolbox_panel.gridToggled.connect(self.toggle_grid)
        self.toolbox_panel.viewReset.connect(self.reset_view)
        self.toolbox_panel.timeScaleChanged.connect(self.set_time_scale)
        
        # 清除对象按钮连接
        self.toolbox_panel.clear_objects_button.clicked.connect(self.clear_objects)
    
    def load_config(self):
        """加载配置"""
        # 加载视图设置
        self.simulation_view.show_grid = config.get("view", "grid_visible")
        self.simulation_view.scale = config.get("view", "initial_scale")
        
        # 加载物理设置
        gravity = config.get("physics", "gravity")
        if gravity and len(gravity) == 2:
            self.simulation_view.simulator.gravity = (gravity[0], gravity[1])
        
        self.simulation_view.simulator.time_scale = config.get("physics", "time_scale")
        
        # 更新UI
        self.simulation_view.update()
    
    def save_config(self):
        """保存配置"""
        # 保存视图设置
        config.set("view", "grid_visible", self.simulation_view.show_grid)
        config.set("view", "initial_scale", self.simulation_view.scale)
        
        # 保存物理设置
        config.set("physics", "gravity", list(self.simulation_view.simulator.gravity))
        config.set("physics", "time_scale", self.simulation_view.simulator.time_scale)
        
        # 保存配置到文件
        config.save()
    
    def update_mouse_position(self, x, y):
        """
        更新鼠标位置显示
        
        参数:
            x, y: 物理坐标
        """
        self.mouse_pos_label.setText(f"位置: ({x:.2f}, {y:.2f})")
    
    def update_scale_info(self, scale, unit="m"):
        """
        更新比例尺信息
        
        参数:
            scale: 比例尺
            unit: 单位
        """
        self.scale_label.setText(f"比例: {scale:.1f} 像素/{unit}")
    
    def create_object(self, props):
        """
        创建物理对象
        
        参数:
            props: 对象属性字典
        """
        obj_type = props["type"]
        position = props["position"]
        mass = props["mass"]
        velocity = props["velocity"]
        color = props["color"]
        
        if obj_type == "长方体":
            width = props["width"]
            height = props["height"]
            self.simulation_view.add_box(position, width, height, mass, velocity, color)
        elif obj_type == "圆形":
            radius = props["radius"]
            self.simulation_view.add_circle(position, radius, mass, velocity, color)
        elif obj_type == "三角形":
            width = props["width"]
            height = props["height"]
            self.simulation_view.add_triangle(position, (width, height), mass, velocity, color)
        elif obj_type == "弹簧":
            k = props["k"]
            end_pos = props["end_pos"]
            self.simulation_view.add_spring(position, end_pos, k, 0.1, color)
        elif obj_type == "轻绳":
            segments = props["segments"]
            end_pos = props["end_pos"]
            self.simulation_view.add_rope(position, end_pos, segments, 0.05, color)
        elif obj_type == "斜面":
            width = props["width"]
            height = props["height"]
            friction = props["friction"]
            self.simulation_view.add_ramp(position, width, height, friction, color)
    
    def clear_objects(self):
        """清除所有物理对象"""
        self.simulation_view.clear_objects()
    
    def update_object_type(self, type_name):
        """
        更新对象类型
        
        参数:
            type_name: 对象类型名称
        """
        self.simulation_view.set_object_type(type_name)
    
    def toggle_draw_mode(self, state):
        """
        切换绘制模式
        
        参数:
            state: 是否启用绘制模式
        """
        self.simulation_view.draw_mode = state
    
    def toggle_grid(self, state):
        """
        切换网格显示
        
        参数:
            state: 是否显示网格
        """
        self.simulation_view.toggle_grid(state)
    
    def reset_view(self):
        """重置视图"""
        self.simulation_view.reset_view()
    
    def toggle_simulation(self, running):
        """
        切换模拟状态
        
        参数:
            running: 是否运行模拟
        """
        self.simulation_view.toggle_simulation(running)
        
        if running:
            self.simulation_timer.start()
        else:
            self.simulation_timer.stop()
    
    def reset_simulation(self):
        """重置模拟"""
        self.simulation_timer.stop()
        self.simulation_view.reset_simulation()
    
    def update_simulation(self):
        """更新模拟"""
        dt = self.simulation_view.update_simulation()
        
        # 计算FPS
        self.fps_count += 1
        self.fps_timer += dt
        
        if self.fps_timer >= 1.0:  # 每秒更新一次FPS
            self.current_fps = self.fps_count / self.fps_timer
            self.fps_label.setText(f"FPS: {self.current_fps:.1f}")
            self.fps_count = 0
            self.fps_timer = 0
    
    def set_object_type(self, type_name):
        """
        设置当前对象类型
        
        参数:
            type_name: 对象类型名称
        """
        self.property_panel.type_combo.setCurrentText(type_name)
        self.simulation_view.set_object_type(type_name)
    
    def set_time_scale(self, scale):
        """
        设置时间缩放系数
        
        参数:
            scale: 时间缩放系数
        """
        self.simulation_view.set_time_scale(scale)
    
    def new_file(self):
        """创建新文件"""
        self.simulation_view.clear_objects()
        self.reset_simulation()
        self.statusBar.showMessage("已创建新文件")
    
    def open_file(self):
        """打开文件"""
        # 此处添加打开文件对话框和文件读取逻辑
        self.statusBar.showMessage("打开文件功能尚未实现")
    
    def save_file(self):
        """保存文件"""
        # 此处添加保存文件对话框和文件写入逻辑
        self.statusBar.showMessage("保存文件功能尚未实现")
    
    def show_about(self):
        """显示关于对话框"""
        # 此处添加关于对话框
        self.statusBar.showMessage("物理运动学可视化软件 v1.0")
    
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        # 保存配置
        self.save_config()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
