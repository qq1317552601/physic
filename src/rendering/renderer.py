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
        hover_object = self.view.hover_object
        selected_object = self.view.selected_object
        
        for obj in objects:
            # 先绘制普通对象
            obj.draw(painter, self.view)
            
            # 如果是选中物体或悬停物体，添加边框高亮
            if (obj == hover_object or obj == selected_object) and hasattr(obj, 'get_bounding_box'):
                box = obj.get_bounding_box()
                
                # 转换为屏幕坐标
                min_x, min_y = self.view.camera.to_screen_coords(box[0], box[1])
                max_x, max_y = self.view.camera.to_screen_coords(box[2], box[3])
                
                # 计算矩形区域
                rect_x = min(min_x, max_x)
                rect_y = min(min_y, max_y)
                rect_width = abs(max_x - min_x)
                rect_height = abs(max_y - min_y)
                
                # 设置边框样式
                if obj == selected_object:
                    # 选中的物体使用更明显的边框 - 蓝色粗边框
                    painter.setPen(QPen(QColor(0, 120, 255), 4, Qt.SolidLine))
                    # 添加半透明的蓝色填充
                    painter.setBrush(QBrush(QColor(0, 120, 255, 30)))
                else:
                    # 悬停的物体使用更明显的边框 - 橙色粗边框
                    painter.setPen(QPen(QColor(255, 140, 0), 3, Qt.SolidLine))
                    # 添加半透明的橙色填充
                    painter.setBrush(QBrush(QColor(255, 140, 0, 20)))
                
                # 为不同类型的物体绘制不同形状的边框
                if hasattr(obj, 'radius'):  # 圆形
                    center_x, center_y = self.view.camera.to_screen_coords(obj.position[0], obj.position[1])
                    radius = obj.radius * self.view.scale
                    # 绘制圆形边框
                    painter.drawEllipse(int(center_x - radius), int(center_y - radius), 
                                       int(radius * 2), int(radius * 2))
                else:  # 矩形或其他
                    # 绘制矩形边框
                    painter.drawRect(int(rect_x), int(rect_y), int(rect_width), int(rect_height))
    
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
        
        # 计算合适的网格间隔 - 确保x和y方向使用相同的间隔以保持正方形
        x_interval = self._calculate_nice_tick_interval(max_x_phys - min_x_phys)
        y_interval = self._calculate_nice_tick_interval(max_y_phys - min_y_phys)
        
        # 选择较小的间隔，确保网格足够精细
        grid_interval = min(x_interval, y_interval)
        
        # 获取刻度位置
        x_positions = self._get_tick_positions(min_x_phys, max_x_phys, grid_interval)
        y_positions = self._get_tick_positions(min_y_phys, max_y_phys, grid_interval)
        
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
                elif abs(x / grid_interval - round(x / grid_interval)) < 1e-10:
                    painter.setPen(QPen(self.grid_major_color, 1))
                else:
                    painter.setPen(QPen(self.grid_color, 1))
                
                painter.drawLine(int(screen_x), 0, int(screen_x), view_height)
                
                # 在x轴上绘制刻度标签，但只在主要刻度上显示
                if abs(x) > 1e-10 and self._should_show_label(x, grid_interval):  # 不在原点绘制标签
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
                elif abs(y / grid_interval - round(y / grid_interval)) < 1e-10:
                    painter.setPen(QPen(self.grid_major_color, 1))
                else:
                    painter.setPen(QPen(self.grid_color, 1))
                
                painter.drawLine(0, int(screen_y), view_width, int(screen_y))
                
                # 在y轴上绘制刻度标签，但只在主要刻度上显示
                if abs(y) > 1e-10 and self._should_show_label(y, grid_interval):  # 不在原点绘制标签
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
        # 使用更精确的方法计算第一个刻度
        # 避免浮点数精度问题，先将值除以间隔，取整，再乘以间隔
        first_tick = math.ceil(min_val / interval) * interval
        
        # 修正可能的浮点数精度问题
        if abs(first_tick - min_val) < 1e-10:
            first_tick = min_val
            
        # 生成所有刻度位置，确保精确的间隔
        positions = []
        current = first_tick
        
        # 使用计数器而不是直接累加，避免浮点数累积误差
        i = 0
        while current <= max_val:
            # 使用精确计算，避免累积误差
            exact_position = first_tick + i * interval
            
            # 修正可能的浮点数精度问题
            if abs(exact_position) < 1e-10:
                exact_position = 0.0
                
            positions.append(exact_position)
            i += 1
            current = exact_position
            
        # 确保包含0刻度（如果在范围内）
        if min_val <= 0 <= max_val and not any(abs(pos) < 1e-10 for pos in positions):
            positions.append(0.0)
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
        typical_value = max(abs(min(positions) if positions else 0), abs(max(positions) if positions else 0))
        
        # 根据大小选择单位
        if typical_value == 0:
            return "m", 1.0
        elif typical_value < 1e-6:
            return "nm", 1e9
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
        # 特殊处理0值
        if abs(value) < 1e-10:
            return f"0{unit}"
            
        # 计算缩放后的值
        scaled_value = value * factor
        
        # 修正可能的浮点数精度问题
        # 例如，将49.999999变为50，99.999999变为100
        rounded_value = round(scaled_value)
        if abs(scaled_value - rounded_value) < 1e-5:
            scaled_value = rounded_value
        
        # 对于接近整数的值，不显示小数
        if abs(scaled_value - round(scaled_value)) < 1e-5:
            return f"{int(scaled_value)}{unit}"
        
        # 对于小数，限制小数位数
        decimal_places = max(0, min(2, -math.floor(math.log10(abs(scaled_value - int(scaled_value))))))
        return f"{scaled_value:.{decimal_places}f}{unit}"

    def _should_show_label(self, value, interval):
        """
        决定是否应该显示该刻度的标签
        
        参数:
            value: 刻度值
            interval: 刻度间隔
            
        返回:
            布尔值，表示是否应该显示标签
        """
        # 找到10的幂次
        exponent = math.floor(math.log10(interval)) if interval > 0 else 0
        
        # 对于不同的缩放级别，使用不同的标签显示策略
        if exponent >= 1:  # 大尺度（≥10单位）
            # 只在10的整数倍上显示标签
            return abs(value / (10 ** exponent) - round(value / (10 ** exponent))) < 1e-10
        elif exponent == 0:  # 中等尺度（1-10单位）
            # 在整数位置显示标签
            return abs(value - round(value)) < 1e-10
        elif exponent == -1:  # 小尺度（0.1-1单位）
            # 在0.5的倍数位置显示标签
            return abs(value * 2 - round(value * 2)) < 1e-10
        else:  # 更小的尺度
            # 在主要刻度位置显示标签（通常是间隔的整数倍）
            return abs(value / interval - round(value / interval)) < 1e-10
