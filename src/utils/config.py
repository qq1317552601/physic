import os
import json
from PyQt5.QtCore import QSettings

class Config:
    """
    配置类
    负责管理应用程序的全局配置
    """
    def __init__(self):
        """初始化配置"""
        # 默认配置
        self.default_config = {
            # 视图设置
            "view": {
                "grid_visible": True,
                "axes_visible": True,
                "show_object_labels": True,
                "background_color": "#FFFFFF",
                "grid_color": "#E6E6E6",
                "axes_color": "#000000",
                "initial_scale": 50.0
            },
            
            # 物理设置
            "physics": {
                "gravity": [0.0, -9.8],
                "time_scale": 1.0,
                "collision_detection": True,
                "default_friction": 0.5,
                "default_restitution": 0.7
            },
            
            # 对象默认设置
            "object_defaults": {
                "box": {
                    "width": 1.0,
                    "height": 1.0,
                    "mass": 1.0,
                    "color": "#C8C8FF"
                },
                "circle": {
                    "radius": 0.5,
                    "mass": 1.0,
                    "color": "#FFC8C8"
                },
                "triangle": {
                    "size": [1.0, 1.0],
                    "mass": 1.0,
                    "color": "#C8FFC8"
                },
                "spring": {
                    "k": 10.0,
                    "width": 0.1,
                    "color": "#C8C8C8"
                },
                "rope": {
                    "segments": 10,
                    "width": 0.05,
                    "color": "#964B00"
                },
                "ramp": {
                    "width": 2.0,
                    "height": 1.0,
                    "friction": 0.5,
                    "color": "#E6E6E6"
                }
            },
            
            # UI设置
            "ui": {
                "property_panel_width": 250,
                "toolbox_panel_width": 200,
                "font_size": 10,
                "animation_fps": 60,
                "language": "zh_CN"
            },
            
            # 应用程序设置
            "app": {
                "auto_save": True,
                "auto_save_interval": 300,  # 秒
                "recent_files": []
            }
        }
        
        # 当前配置
        self.config = self.default_config.copy()
        
        # 创建QSettings对象
        self.settings = QSettings("PhysicsSimulator", "PhysicsSimulator")
        
        # 加载保存的配置
        self.load()
    
    def get(self, section, key=None):
        """
        获取配置项
        
        参数:
            section: 配置节
            key: 配置键，如果为None，则返回整个节
            
        返回:
            配置值
        """
        if key is None:
            return self.config.get(section, {})
        
        return self.config.get(section, {}).get(key, None)
    
    def set(self, section, key, value):
        """
        设置配置项
        
        参数:
            section: 配置节
            key: 配置键
            value: 配置值
            
        返回:
            是否设置成功
        """
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][key] = value
        return True
    
    def load(self):
        """
        从QSettings加载配置
        
        返回:
            是否加载成功
        """
        # 从QSettings中读取配置JSON
        config_json = self.settings.value("config", "")
        
        if not config_json:
            return False
            
        try:
            # 解析JSON
            loaded_config = json.loads(config_json)
            
            # 将加载的配置合并到当前配置
            self._merge_configs(self.config, loaded_config)
            
            return True
        except Exception as e:
            print(f"加载配置时出错: {str(e)}")
            return False
    
    def save(self):
        """
        保存配置到QSettings
        
        返回:
            是否保存成功
        """
        try:
            # 将配置转换为JSON
            config_json = json.dumps(self.config)
            
            # 保存到QSettings
            self.settings.setValue("config", config_json)
            self.settings.sync()
            
            return True
        except Exception as e:
            print(f"保存配置时出错: {str(e)}")
            return False
    
    def reset(self, section=None):
        """
        重置配置到默认值
        
        参数:
            section: 要重置的配置节，如果为None，则重置所有配置
            
        返回:
            是否重置成功
        """
        if section is None:
            # 重置所有配置
            self.config = self.default_config.copy()
        elif section in self.default_config:
            # 重置指定节的配置
            self.config[section] = self.default_config[section].copy()
        else:
            return False
            
        return True
    
    def add_recent_file(self, file_path):
        """
        添加最近使用的文件
        
        参数:
            file_path: 文件路径
            
        返回:
            是否添加成功
        """
        # 获取当前的最近文件列表
        recent_files = self.get("app", "recent_files") or []
        
        # 如果文件已经在列表中，先移除
        if file_path in recent_files:
            recent_files.remove(file_path)
            
        # 添加到列表前面
        recent_files.insert(0, file_path)
        
        # 保留最多10个文件
        recent_files = recent_files[:10]
        
        # 更新配置
        self.set("app", "recent_files", recent_files)
        
        return True
    
    def _merge_configs(self, target, source):
        """
        合并两个配置字典
        
        参数:
            target: 目标配置字典
            source: 源配置字典
        """
        for key, value in source.items():
            # 如果是字典，递归合并
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_configs(target[key], value)
            else:
                # 否则直接覆盖
                target[key] = value

# 创建全局配置实例
config = Config()
