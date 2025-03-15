import sys
import traceback
import logging
from PyQt5.QtWidgets import QMessageBox

class ErrorHandler:
    """
    错误处理类
    提供统一的异常处理和日志记录
    """
    def __init__(self, logger=None):
        """
        初始化错误处理器
        
        参数:
            logger: 日志记录器，如果为None则创建一个新的
        """
        self.logger = logger or logging.getLogger('physics_simulator')
    
    def handle_exception(self, exc_type, exc_value, exc_traceback, show_dialog=True):
        """
        处理未捕获的异常
        
        参数:
            exc_type: 异常类型
            exc_value: 异常值
            exc_traceback: 异常的回溯信息
            show_dialog: 是否显示错误对话框
            
        返回:
            是否处理了异常
        """
        # 记录异常信息到日志
        self.logger.error(
            f"未捕获的异常: {exc_type.__name__}: {exc_value}",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # 如果需要，显示错误对话框
        if show_dialog:
            error_text = f"{exc_type.__name__}: {exc_value}"
            traceback_text = ''.join(traceback.format_tb(exc_traceback))
            
            QMessageBox.critical(
                None,
                "发生错误",
                f"程序遇到了一个问题：\n\n{error_text}\n\n详细信息：\n{traceback_text}"
            )
        
        return True
    
    def log_error(self, message, exc_info=None):
        """
        记录错误到日志
        
        参数:
            message: 错误消息
            exc_info: 异常信息元组 (type, value, traceback)
        """
        self.logger.error(message, exc_info=exc_info)
    
    def log_warning(self, message):
        """
        记录警告到日志
        
        参数:
            message: 警告消息
        """
        self.logger.warning(message)
    
    def log_info(self, message):
        """
        记录信息到日志
        
        参数:
            message: 信息消息
        """
        self.logger.info(message)
    
    def show_error_dialog(self, title, message, details=None):
        """
        显示错误对话框
        
        参数:
            title: 对话框标题
            message: 错误消息
            details: 详细信息
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if details:
            msg_box.setDetailedText(details)
            
        msg_box.exec_()
    
    def install_global_handler(self):
        """
        安装全局异常处理器
        """
        sys.excepthook = self.handle_exception


# 创建全局错误处理器实例
error_handler = ErrorHandler() 