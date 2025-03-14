from PyQt5.QtCore import QPoint, QPointF

class Camera:
    """
    相机类
    负责管理视图坐标系统，处理缩放和平移操作
    """
    def __init__(self, view_width=600, view_height=500):
        """
        初始化相机
        
        参数:
            view_width: 视图宽度（像素）
            view_height: 视图高度（像素）
        """
        self.view_width = view_width
        self.view_height = view_height
        self.origin = QPoint(view_width // 2, view_height // 2)  # 原点位置（屏幕坐标）
        self.scale = 50.0  # 缩放比例 (像素/米)
        self.min_scale = 0.01  # 最小缩放比例
        self.max_scale = 1000000  # 最大缩放比例
        
        # 当前单位信息
        self.current_unit = "m"  # 当前显示单位
        self.current_factor = 1.0  # 当前单位转换因子
    
    def resize(self, width, height):
        """
        当视图大小改变时更新相机
        
        参数:
            width: 新宽度（像素）
            height: 新高度（像素）
        """
        # 保持原点在视图中心
        self.origin = QPoint(width // 2, height // 2)
        self.view_width = width
        self.view_height = height
    
    def pan(self, dx, dy):
        """
        平移视图
        
        参数:
            dx: 水平移动距离（屏幕像素）
            dy: 垂直移动距离（屏幕像素）
        """
        self.origin = QPoint(self.origin.x() + dx, self.origin.y() + dy)
    
    def zoom(self, factor, center_x, center_y):
        """
        缩放视图，保持中心点不变
        
        参数:
            factor: 缩放因子
            center_x: 缩放中心x坐标（屏幕坐标）
            center_y: 缩放中心y坐标（屏幕坐标）
        """
        # 计算缩放中心的物理坐标
        phys_x = (center_x - self.origin.x()) / self.scale
        phys_y = (self.origin.y() - center_y) / self.scale
        
        # 应用缩放
        new_scale = self.scale * factor
        
        # 限制缩放范围
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        # 只有当缩放实际改变时才更新
        if abs(new_scale - self.scale) > 1e-10:
            # 计算新的原点位置，保持物理坐标中心不变
            new_origin_x = center_x - phys_x * new_scale
            new_origin_y = center_y + phys_y * new_scale
            
            self.origin = QPoint(int(new_origin_x), int(new_origin_y))
            self.scale = new_scale
            
            return True  # 缩放已更改
            
        return False  # 缩放未更改
    
    def reset(self):
        """
        重置相机到初始状态
        """
        self.origin = QPoint(self.view_width // 2, self.view_height // 2)
        self.scale = 50.0
    
    def to_screen_coords(self, phys_x, phys_y):
        """
        将物理坐标转换为屏幕坐标
        
        参数:
            phys_x: 物理x坐标（米）
            phys_y: 物理y坐标（米）
            
        返回:
            (screen_x, screen_y): 屏幕坐标（像素）
        """
        screen_x = self.origin.x() + phys_x * self.scale
        screen_y = self.origin.y() - phys_y * self.scale  # y轴方向相反
        return int(screen_x), int(screen_y)
    
    def to_screen_point(self, phys_x, phys_y):
        """
        将物理坐标转换为屏幕上的QPointF
        
        参数:
            phys_x: 物理x坐标（米）
            phys_y: 物理y坐标（米）
            
        返回:
            QPointF: 屏幕坐标点
        """
        screen_x = self.origin.x() + phys_x * self.scale
        screen_y = self.origin.y() - phys_y * self.scale  # y轴方向相反
        return QPointF(screen_x, screen_y)
    
    def from_screen_coords(self, screen_x, screen_y):
        """
        将屏幕坐标转换为物理坐标
        
        参数:
            screen_x: 屏幕x坐标（像素）
            screen_y: 屏幕y坐标（像素）
            
        返回:
            (phys_x, phys_y): 物理坐标（米）
        """
        phys_x = (screen_x - self.origin.x()) / self.scale
        phys_y = (self.origin.y() - screen_y) / self.scale  # y轴方向相反
        return phys_x, phys_y
    
    def screen_distance_to_physical(self, screen_distance):
        """
        将屏幕距离转换为物理距离
        
        参数:
            screen_distance: 屏幕距离（像素）
            
        返回:
            物理距离（米）
        """
        return screen_distance / self.scale
    
    def physical_distance_to_screen(self, physical_distance):
        """
        将物理距离转换为屏幕距离
        
        参数:
            physical_distance: 物理距离（米）
            
        返回:
            屏幕距离（像素）
        """
        return physical_distance * self.scale
