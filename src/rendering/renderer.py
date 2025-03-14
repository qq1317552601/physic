import math
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from PyQt5.QtCore import Qt, QPoint, QPointF, QRect

class Renderer:
    """
    渲染器类
    负责将物理对象渲染到视图上
    """
    def __init__(self, simulation_view):
        """
        初始化渲染器
        
        参数:
            simulation_view: SimulationView实例，提供坐标变换和视图信息
        """
        self.view = simulation_view
        # 网格线颜色和样式
        self.grid_color = QColor(230, 230, 230)
        self.grid_major_color = QColor(200, 200, 200)
        self.axis_color = QColor(0, 0, 0)
        self.text_color = QColor(80, 80, 80)
    
    def draw_objects(self, painter, objects):
        """
        绘制所有物理对象
        
        参数:
            painter: QPainter实例
            objects: 物理对象列表
        """
        for obj in objects:
            obj.draw(painter, self.view)
    
    def draw_grid(self, painter):
        """
        绘制网格
        
        参数:
            painter: QPainter实例
        """
        view_width = self.view.width()
        view_height = self.view.height()
        origin_x = self.view.origin.x()
        origin_y = self.view.origin.y()
        scale = self.view.scale
        
        # 物理坐标范围
        width_phys = view_width / scale
        height_phys = view_height / scale
        min_x_phys = (0 - origin_x) / scale
        max_x_phys = (view_width - origin_x) / scale
        min_y_phys = (origin_y - view_height) / scale  # y轴方向相反
        max_y_phys = origin_y / scale
        
        # 计算合适的网格间隔
        x_interval = self._calculate_nice_tick_interval(max_x_phys - min_x_phys)
        y_interval = self._calculate_nice_tick_interval(max_y_phys - min_y_phys)
        
        # 获取刻度位置
        x_positions = self._get_tick_positions(min_x_phys, max_x_phys, x_interval)
        y_positions = self._get_tick_positions(min_y_phys, max_y_phys, y_interval)
        
        # 确定单位和因子
        x_unit, x_factor = self._determine_unit_and_factor(x_positions)
        y_unit, y_factor = self._determine_unit_and_factor(y_positions)
        
        # 更新视图的当前单位信息
        self.view.current_unit = x_unit
        self.view.current_factor = x_factor
        
        # 绘制网格线
        painter.setPen(QPen(self.grid_color, 1, Qt.SolidLine))
        
        # 绘制垂直网格线
        for x in x_positions:
            screen_x = origin_x + x * scale
            if 0 <= screen_x <= view_width:
                # 如果是主要网格线，稍微加粗
                if abs(x) < 1e-10:  # x接近0，是y轴
                    painter.setPen(QPen(self.axis_color, 2))
                elif abs(x / x_interval - round(x / x_interval)) < 1e-10:
                    painter.setPen(QPen(self.grid_major_color, 1))
                else:
                    painter.setPen(QPen(self.grid_color, 1))
                
                painter.drawLine(int(screen_x), 0, int(screen_x), view_height)
                
                # 在x轴上绘制刻度标签
                if abs(x) > 1e-10:  # 不在原点绘制标签
                    label = self._format_tick_label(x, x_unit, x_factor)
                    painter.setPen(self.text_color)
                    painter.drawText(
                        int(screen_x) - 20, origin_y + 20, 
                        40, 20, 
                        Qt.AlignCenter, 
                        label
                    )
        
        # 绘制水平网格线
        for y in y_positions:
            screen_y = origin_y - y * scale  # 注意y轴方向是相反的
            if 0 <= screen_y <= view_height:
                # 如果是主要网格线，稍微加粗
                if abs(y) < 1e-10:  # y接近0，是x轴
                    painter.setPen(QPen(self.axis_color, 2))
                elif abs(y / y_interval - round(y / y_interval)) < 1e-10:
                    painter.setPen(QPen(self.grid_major_color, 1))
                else:
                    painter.setPen(QPen(self.grid_color, 1))
                
                painter.drawLine(0, int(screen_y), view_width, int(screen_y))
                
                # 在y轴上绘制刻度标签
                if abs(y) > 1e-10:  # 不在原点绘制标签
                    label = self._format_tick_label(y, y_unit, y_factor)
                    painter.setPen(self.text_color)
                    painter.drawText(
                        origin_x - 50, int(screen_y) - 10,
                        40, 20,
                        Qt.AlignRight | Qt.AlignVCenter,
                        label
                    )
    
    def draw_axes(self, painter):
        """
        绘制坐标轴
        
        参数:
            painter: QPainter实例
        """
        view_width = self.view.width()
        view_height = self.view.height()
        origin_x = self.view.origin.x()
        origin_y = self.view.origin.y()
        
        # 绘制坐标轴
        painter.setPen(QPen(self.axis_color, 2, Qt.SolidLine))
        
        # X轴
        painter.drawLine(0, origin_y, view_width, origin_y)
        
        # Y轴
        painter.drawLine(origin_x, 0, origin_x, view_height)
        
        # 原点标记
        painter.setPen(QPen(self.axis_color, 1))
        painter.setBrush(QBrush(self.axis_color))
        painter.drawEllipse(origin_x - 3, origin_y - 3, 6, 6)
        
        # 坐标轴标签
        painter.setPen(self.text_color)
        painter.setFont(QFont("Arial", 10))
        
        # X轴标签
        painter.drawText(
            view_width - 30, origin_y - 20,
            30, 20,
            Qt.AlignCenter,
            "x"
        )
        
        # Y轴标签
        painter.drawText(
            origin_x + 10, 10,
            20, 20,
            Qt.AlignCenter,
            "y"
        )
        
        # 单位信息
        unit_text = f"单位: 1格 = 1{self.view.current_unit}"
        painter.drawText(
            10, view_height - 20,
            200, 20,
            Qt.AlignLeft | Qt.AlignBottom,
            unit_text
        )
    
    def _calculate_nice_tick_interval(self, physical_range, target_count=10):
        """
        计算美观的刻度间隔
        
        参数:
            physical_range: 物理范围
            target_count: 目标刻度数量
            
        返回:
            刻度间隔
        """
        # 计算粗略的间隔
        rough_interval = physical_range / target_count
        
        # 找到10的幂次
        exponent = math.floor(math.log10(rough_interval))
        
        # 计算标准化的间隔
        normalized_interval = rough_interval / (10 ** exponent)
        
        # 选择美观的间隔（1, 2, 5, 10）
        if normalized_interval < 1.5:
            nice_interval = 1
        elif normalized_interval < 3:
            nice_interval = 2
        elif normalized_interval < 7:
            nice_interval = 5
        else:
            nice_interval = 10
            
        # 还原为原始尺度
        return nice_interval * (10 ** exponent)
    
    def _get_tick_positions(self, min_val, max_val, interval):
        """
        获取刻度位置
        
        参数:
            min_val: 最小值
            max_val: 最大值
            interval: 间隔
            
        返回:
            刻度位置列表
        """
        # 找到最小值之后的第一个刻度
        first_tick = math.ceil(min_val / interval) * interval
        
        # 生成所有刻度位置
        positions = []
        current = first_tick
        while current <= max_val:
            positions.append(current)
            current += interval
            
        # 确保包含0刻度（如果在范围内）
        if min_val <= 0 <= max_val and 0 not in positions:
            positions.append(0)
            positions.sort()
            
        return positions
    
    def _determine_unit_and_factor(self, positions):
        """
        确定适合的单位和缩放因子
        
        参数:
            positions: 刻度位置列表
            
        返回:
            (单位字符串, 缩放因子)
        """
        if not positions:
            return "m", 1.0
            
        # 计算典型值的大小
        typical_value = max(abs(min(positions)), abs(max(positions)))
        
        # 根据大小选择单位
        if typical_value == 0:
            return "m", 1.0
        elif typical_value < 1e-3:
            return "μm", 1e6
        elif typical_value < 1:
            return "mm", 1e3
        elif typical_value < 1e3:
            return "m", 1.0
        elif typical_value < 1e6:
            return "km", 1e-3
        else:
            return "Mm", 1e-6
    
    def _format_tick_label(self, value, unit, factor):
        """
        格式化刻度标签
        
        参数:
            value: 物理值
            unit: 单位
            factor: 缩放因子
            
        返回:
            格式化的标签
        """
        scaled_value = value * factor
        
        # 对于接近整数的值，不显示小数
        if abs(scaled_value - round(scaled_value)) < 1e-10:
            return f"{int(scaled_value)}"
        
        # 对于小数，限制小数位数
        decimal_places = max(0, min(2, -math.floor(math.log10(abs(scaled_value - int(scaled_value))))))
        return f"{scaled_value:.{decimal_places}f}"
