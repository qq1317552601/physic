#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
物理运动学可视化软件
主入口文件

这个程序允许用户创建和模拟各种物理单件（如长方体、小球、斜面、弹簧、轻绳）
并为这些模型设置各种参数（如质量、速度、加速度、摩擦因数、弹簧劲度系数），
从而能够复现大多数物理运动学练习题中的物理模拟动画。
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入主窗口
from ui.main_window import MainWindow

# 配置日志
def setup_logging():
    """配置日志系统"""
    log_dir = os.path.join(project_root, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'physics_simulator.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('physics_simulator')

def main():
    """应用程序主入口点"""
    # 设置日志
    logger = setup_logging()
    logger.info("启动物理运动学可视化软件")
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    app.setApplicationName("物理运动学可视化软件")
    app.setOrganizationName("PhysicsSimulator")
    
    # 设置应用程序图标
    # app.setWindowIcon(QIcon(os.path.join(project_root, 'resources', 'icon.png')))
    
    # 显示启动画面
    # splash_pix = QPixmap(os.path.join(project_root, 'resources', 'splash.png'))
    # splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    # splash.show()
    # app.processEvents()
    
    # 延迟创建主窗口，以显示启动画面
    # QTimer.singleShot(1000, lambda: initialize_main_window(app, splash, logger))
    
    # 直接创建主窗口（如果没有启动画面）
    window = MainWindow()
    window.show()
    logger.info("主窗口已显示")
    
    # 进入应用程序主循环
    sys.exit(app.exec_())

def initialize_main_window(app, splash, logger):
    """初始化并显示主窗口"""
    try:
        # 创建主窗口
        window = MainWindow()
        
        # 关闭启动画面并显示主窗口
        splash.finish(window)
        window.show()
        
        logger.info("主窗口已显示")
    except Exception as e:
        logger.error(f"初始化主窗口时出错: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
