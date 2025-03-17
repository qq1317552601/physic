import math
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QToolBar, QAction, QDockWidget, QFormLayout, QLabel, QDoubleSpinBox,
                            QComboBox, QGroupBox, QSlider, QPushButton, QStatusBar, QSplitter,
                            QCheckBox, QButtonGroup, QRadioButton, QShortcut)
from PyQt5.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QFont, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from .simulation_view import SimulationView
from .property_panel import PropertyPanel
from .toolbox import ToolboxPanel
from utils.config import config
from utils.command_history import CommandHistory, MoveObjectCommand, ChangePropertyCommand, AddObjectCommand, RemoveObjectCommand

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
        
        # 确保窗口能捕获所有按键事件
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 创建命令历史管理器
        self.command_history = CommandHistory()
        
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
        
        # 设置快捷键
        self.setup_shortcuts()
        
        # 连接信号
        self.connect_signals()
        
        # 加载配置
        self.load_config()
        
        # 显示初始提示信息
        self.statusBar.showMessage("程序已启动. 使用Ctrl+Z撤销，Ctrl+Y重做", 5000)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 删除快捷键 (Delete)
        self.delete_shortcut = QShortcut(QKeySequence.Delete, self)
        self.delete_shortcut.activated.connect(self.delete_selected)
        
        # 注意：撤销和重做快捷键已在工具栏动作中设置
    
    def keyPressEvent(self, event):
        """处理键盘事件，确保快捷键正常工作"""
        # 处理撤销快捷键 (Ctrl+Z)
        if event.matches(QKeySequence.Undo):
            self.undo()
            event.accept()
            return
        
        # 处理重做快捷键 (Ctrl+Y 或 Ctrl+Shift+Z)
        if event.matches(QKeySequence.Redo):
            self.redo()
            event.accept()
            return
        
        # 继续传递事件给基类
        super().keyPressEvent(event)
    
    def undo(self):
        """撤销上一个操作"""
        if self.command_history.undo():
            self.simulation_view.update()
            # 更新状态栏
            self.statusBar.showMessage("已撤销操作", 2000)
    
    def redo(self):
        """重做下一个操作"""
        if self.command_history.redo():
            self.simulation_view.update()
            # 更新状态栏
            self.statusBar.showMessage("已重做操作", 2000)
    
    def delete_selected(self):
        """删除选中的物体"""
        if self.simulation_view.selected_object:
            obj = self.simulation_view.selected_object
            # 创建删除命令
            command = RemoveObjectCommand(self.simulation_view.simulator, obj)
            self.command_history.execute_command(command)
            # 清除选中状态
            self.simulation_view.selected_object = None
            self.property_panel.update_for_selected_object(None)
            self.simulation_view.update()
            # 更新状态栏
            self.statusBar.showMessage("已删除物体", 2000)
    
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
        
        # 添加撤销/重做按钮
        self.undo_action = QAction("撤销", self)
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setShortcut(QKeySequence.Undo)
        toolbar.addAction(self.undo_action)
        
        self.redo_action = QAction("重做", self)
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setShortcut(QKeySequence.Redo)
        toolbar.addAction(self.redo_action)
        
        toolbar.addSeparator()
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 连接模拟视图信号
        self.simulation_view.mousePositionChanged.connect(self.update_mouse_position)
        self.simulation_view.scaleChanged.connect(self.update_scale_info)
        self.simulation_view.objectSelected.connect(self.update_property_panel)
        
        # 连接工具箱面板信号
        self.toolbox_panel.objectTypeSelected.connect(self.set_object_type)
        self.toolbox_panel.simulationToggled.connect(self.toggle_simulation)
        self.toolbox_panel.simulationReset.connect(self.reset_simulation)
        self.toolbox_panel.drawModeToggled.connect(self.toggle_draw_mode)
        self.toolbox_panel.gridToggled.connect(self.toggle_grid)
        self.toolbox_panel.viewReset.connect(self.reset_view)
        self.toolbox_panel.timeScaleChanged.connect(self.set_time_scale)
        self.toolbox_panel.gravityChanged.connect(self.set_gravity)
        
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
            self.simulation_view.simulator.gravity = (0.0, gravity[1])  # X方向固定为0
            # 更新工具箱面板中的重力控件
            self.toolbox_panel.gravity_y.setValue(gravity[1])
        
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
    
    def clear_objects(self):
        """清除所有物理对象"""
        self.simulation_view.clear_objects()
    
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

    def set_gravity(self, gx, gy):
        """
        设置重力
        
        参数:
            gx, gy: 重力加速度分量
        """
        self.simulation_view.simulator.gravity = (gx, gy)
        
        # 重置所有物体的加速度，确保新的重力立即生效
        for obj in self.simulation_view.simulator.objects:
            if hasattr(obj, 'mass') and obj.mass > 0:
                # 只保留物体自身的加速度，不包括重力加速度
                # 下一次更新时会重新应用重力
                obj.acceleration = (0, 0)
        
        # 更新配置
        config.set("physics", "gravity", [gx, gy])
    
    def update_property_panel(self, obj):
        """
        更新属性面板以显示选中物体的属性
        
        参数:
            obj: 选中的物理对象
        """
        self.property_panel.update_for_selected_object(obj)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
