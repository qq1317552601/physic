import math
import time
from .objects import PhysicsObject, Box, Circle, Triangle, Spring, Rope, Ramp

class PhysicsSimulator:
    """
    物理模拟器类
    负责模拟物理对象的运动和交互
    """
    def __init__(self):
        """初始化物理模拟器"""
        self.objects = []  # 物理对象列表
        self.gravity = (0.0, -9.8)  # 重力加速度，单位：m/s²
        self.simulation_time = 0.0  # 模拟已经运行的总时间，单位：秒
        self.is_running = False  # 模拟是否正在运行
        self.time_scale = 1.0  # 时间缩放因子
        self.last_update_time = None  # 上次更新的时间
        self.collision_detection_enabled = True  # 是否启用碰撞检测
        self.constraints = []  # 约束条件列表
        
    def add_object(self, obj):
        """
        添加物理对象到模拟器
        
        参数:
            obj: PhysicsObject实例
        """
        if isinstance(obj, PhysicsObject):
            self.objects.append(obj)
            return True
        return False
        
    def remove_object(self, obj):
        """
        从模拟器中移除物理对象
        
        参数:
            obj: PhysicsObject实例
        """
        if obj in self.objects:
            self.objects.remove(obj)
            return True
        return False
        
    def clear_objects(self):
        """清除所有物理对象"""
        self.objects.clear()
        self.simulation_time = 0.0
        
    def start(self):
        """开始模拟"""
        self.is_running = True
        self.last_update_time = time.time()
        
    def stop(self):
        """停止模拟"""
        self.is_running = False
        
    def reset(self):
        """重置模拟状态"""
        self.simulation_time = 0.0
        self.is_running = False
        # 重置对象到初始状态可以在这里添加
        
    def update(self):
        """
        更新物理模拟
        
        返回:
            dt: 实际模拟的时间步长
        """
        if not self.is_running:
            return 0.0
            
        current_time = time.time()
        if self.last_update_time is None:
            self.last_update_time = current_time
            return 0.0
            
        # 计算真实经过的时间
        elapsed_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 应用时间缩放
        dt = elapsed_time * self.time_scale
        
        # 更新模拟时间
        self.simulation_time += dt
        
        # 应用物理更新
        self._update_physics(dt)
        
        return dt
        
    def _update_physics(self, dt):
        """
        更新所有物理对象的状态
        
        参数:
            dt: 时间步长，单位：秒
        """
        # 更新每个物体的位置和速度
        for obj in self.objects:
            # 跳过固定的物体
            if hasattr(obj, 'fixed') and obj.fixed:
                continue
                
            # 对于受重力影响的物体，添加重力加速度
            if hasattr(obj, 'mass') and obj.mass > 0:
                obj.acceleration = (
                    obj.acceleration[0] + self.gravity[0],
                    obj.acceleration[1] + self.gravity[1]
                )
                
            # 更新物体状态
            obj.update(dt)
            
        # 处理约束条件
        for constraint in self.constraints:
            constraint.apply()
            
        # 如果启用了碰撞检测，则检测和处理碰撞
        if self.collision_detection_enabled:
            self._handle_collisions()
            
    def _handle_collisions(self):
        """处理物体之间的碰撞"""
        # 遍历所有物体对，检测碰撞
        for i in range(len(self.objects)):
            for j in range(i + 1, len(self.objects)):
                obj1 = self.objects[i]
                obj2 = self.objects[j]
                
                # 检查物体是否设置为不参与碰撞
                if (hasattr(obj1, 'no_collision') and obj1.no_collision) or \
                   (hasattr(obj2, 'no_collision') and obj2.no_collision):
                    continue
                
                # 检查物体类型是否支持碰撞
                if not (hasattr(obj1, 'contains_point') and hasattr(obj2, 'contains_point')):
                    continue
                    
                # 检测碰撞并解决
                if self._check_collision(obj1, obj2):
                    self._resolve_collision(obj1, obj2)
                    # 添加位置修正，防止物体重叠导致的穿透问题
                    self._correct_position_overlap(obj1, obj2)
    
    def _check_collision(self, obj1, obj2):
        """
        检查两个物体是否碰撞
        
        参数:
            obj1, obj2: 物理对象
            
        返回:
            是否碰撞
        """
        # 简单的包围盒碰撞检测
        box1 = obj1.get_bounding_box()
        box2 = obj2.get_bounding_box()
        
        # 检查两个包围盒是否重叠
        if (box1[0] > box2[2] or box1[2] < box2[0] or
            box1[1] > box2[3] or box1[3] < box2[1]):
            return False
            
        # 更精确的碰撞检测 - 根据物体类型进行更详细的检测
        if hasattr(obj1, 'radius') and hasattr(obj2, 'radius'):
            # 两个圆形物体的碰撞检测
            dx = obj2.position[0] - obj1.position[0]
            dy = obj2.position[1] - obj1.position[1]
            distance_squared = dx*dx + dy*dy
            min_distance = obj1.radius + obj2.radius
            return distance_squared <= min_distance * min_distance
        
        # 默认情况下，如果包围盒重叠则认为发生碰撞
        return True
        
    def _get_collision_normal(self, obj1, obj2):
        """
        计算两个物体之间的碰撞法向量
        
        参数:
            obj1, obj2: 碰撞的物理对象
            
        返回:
            tuple: 归一化的法向量 (nx, ny)
        """
        # 处理特殊情况：正面碰撞
        # 对于矩形物体，计算最小穿透深度的方向作为法向量
        if hasattr(obj1, 'width') and hasattr(obj1, 'height') and \
           hasattr(obj2, 'width') and hasattr(obj2, 'height'):
            
            box1 = obj1.get_bounding_box()
            box2 = obj2.get_bounding_box()
            
            # 计算每个方向的穿透深度
            left_depth = box2[2] - box1[0]   # obj1左边进入obj2右边的深度
            right_depth = box1[2] - box2[0]  # obj1右边进入obj2左边的深度
            top_depth = box2[3] - box1[1]    # obj1上边进入obj2下边的深度
            bottom_depth = box1[3] - box2[1] # obj1下边进入obj2上边的深度
            
            # 找出最小穿透深度及其方向
            min_depth = min(left_depth, right_depth, top_depth, bottom_depth)
            
            # 根据最小穿透深度确定法向量方向
            if min_depth == left_depth:
                return (-1, 0)  # 向左
            elif min_depth == right_depth:
                return (1, 0)   # 向右
            elif min_depth == top_depth:
                return (0, -1)  # 向上
            else:  # bottom_depth
                return (0, 1)   # 向下
        
        # 圆形物体之间或其他类型物体之间使用中心连线作为法向量
        dx = obj2.position[0] - obj1.position[0]
        dy = obj2.position[1] - obj1.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.0001:  # 近似零的情况
            # 当距离极小时，对于从上到下的碰撞返回向上的法向量
            # 这有助于处理类似小球从上方掉落到平面上的场景
            if obj1.position[1] > obj2.position[1]:
                return (0, 1)  # obj1在上方，法向量向上
            elif obj1.position[1] < obj2.position[1]:
                return (0, -1) # obj1在下方，法向量向下
            else:
                # 如果在同一高度，基于x坐标决定
                if obj1.position[0] < obj2.position[0]:
                    return (1, 0)  # obj1在左，法向量向右
                else:
                    return (-1, 0) # obj1在右，法向量向左
        else:
            # 归一化向量
            return (dx / distance, dy / distance)
        
    def _resolve_collision(self, obj1, obj2):
        """
        解决两个物体之间的碰撞
        
        参数:
            obj1, obj2: 碰撞的物理对象
        """
        # 简化的碰撞响应，基于物体的弹性系数
        if not (hasattr(obj1, 'velocity') and hasattr(obj2, 'velocity')):
            return
            
        # 计算碰撞后的速度变化
        # 这里使用简化的弹性碰撞模型
        restitution = min(obj1.restitution, obj2.restitution)
        
        # 获取碰撞法向量
        nx, ny = self._get_collision_normal(obj1, obj2)
        
        # 计算相对速度的法向分量
        vx = obj2.velocity[0] - obj1.velocity[0]
        vy = obj2.velocity[1] - obj1.velocity[1]
        vn = vx*nx + vy*ny
        
        # 如果物体正在分离，不需要处理碰撞
        if vn > 0:
            return
            
        # 计算冲量
        m1 = 0 if (hasattr(obj1, 'fixed') and obj1.fixed) else obj1.mass
        m2 = 0 if (hasattr(obj2, 'fixed') and obj2.fixed) else obj2.mass
        
        # 如果两个物体都是固定的，不需要处理碰撞
        if m1 <= 0 and m2 <= 0:
            return
            
        # 处理一个物体固定的情况
        if m1 <= 0:  # obj1 is fixed
            # 只更新 obj2 的速度
            impulse = -(1 + restitution) * vn * m2
            obj2.velocity = (
                obj2.velocity[0] + impulse * nx / m2,
                obj2.velocity[1] + impulse * ny / m2
            )
            return
        elif m2 <= 0:  # obj2 is fixed
            # 只更新 obj1 的速度
            impulse = -(1 + restitution) * vn * m1
            obj1.velocity = (
                obj1.velocity[0] - impulse * nx / m1,
                obj1.velocity[1] - impulse * ny / m1
            )
            return
        
        # 两个物体都不是固定的情况
        reduced_mass = (m1 * m2) / (m1 + m2)
        impulse = -(1 + restitution) * vn * reduced_mass
        
        # 应用冲量
        obj1.velocity = (
            obj1.velocity[0] - impulse * nx / m1,
            obj1.velocity[1] - impulse * ny / m1
        )
        
        obj2.velocity = (
            obj2.velocity[0] + impulse * nx / m2,
            obj2.velocity[1] + impulse * ny / m2
        )
        
    def _correct_position_overlap(self, obj1, obj2):
        """
        修正物体之间的位置重叠问题
        
        参数:
            obj1, obj2: 碰撞的物理对象
        """
        # 检查物体是否有位置和半径属性
        if not (hasattr(obj1, 'position') and hasattr(obj2, 'position')):
            return
            
        # 获取物体是否固定
        fixed1 = hasattr(obj1, 'fixed') and obj1.fixed
        fixed2 = hasattr(obj2, 'fixed') and obj2.fixed
        
        # 如果两个物体都是固定的，不需要修正位置
        if fixed1 and fixed2:
            return
            
        # 获取碰撞法向量 - 使用与碰撞处理相同的法向量计算方法
        nx, ny = self._get_collision_normal(obj1, obj2)
        
        # 计算重叠量
        overlap = 0
        
        # 根据物体类型计算重叠量
        if hasattr(obj1, 'radius') and hasattr(obj2, 'radius'):
            # 两个圆形物体
            dx = obj2.position[0] - obj1.position[0]
            dy = obj2.position[1] - obj1.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            overlap = obj1.radius + obj2.radius - distance
        elif hasattr(obj1, 'width') and hasattr(obj1, 'height') and hasattr(obj2, 'width') and hasattr(obj2, 'height'):
            # 两个矩形物体 - 使用分离轴定理的简化版本
            box1 = obj1.get_bounding_box()
            box2 = obj2.get_bounding_box()
            
            # 计算各个方向的重叠
            left_overlap = box2[2] - box1[0]    # obj1左边与obj2右边的重叠
            right_overlap = box1[2] - box2[0]   # obj1右边与obj2左边的重叠
            top_overlap = box2[3] - box1[1]     # obj1上边与obj2下边的重叠
            bottom_overlap = box1[3] - box2[1]  # obj1下边与obj2上边的重叠
            
            # 找出最小重叠 - 这将是需要移动的距离
            if abs(nx) > abs(ny):  # 水平碰撞
                overlap = min(left_overlap, right_overlap) if nx > 0 else min(right_overlap, left_overlap)
            else:  # 垂直碰撞
                overlap = min(top_overlap, bottom_overlap) if ny > 0 else min(bottom_overlap, top_overlap)
        else:
            # 对于其他物体类型，使用简单的启发式方法
            dx = obj2.position[0] - obj1.position[0]
            dy = obj2.position[1] - obj1.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # 估计的对象大小
            size1 = 0.5  # 默认大小
            size2 = 0.5
            
            if hasattr(obj1, 'radius'):
                size1 = obj1.radius
            elif hasattr(obj1, 'width') and hasattr(obj1, 'height'):
                size1 = (obj1.width + obj1.height) / 4  # 估计平均大小
                
            if hasattr(obj2, 'radius'):
                size2 = obj2.radius
            elif hasattr(obj2, 'width') and hasattr(obj2, 'height'):
                size2 = (obj2.width + obj2.height) / 4
                
            overlap = size1 + size2 - distance
        
        # 如果有重叠，修正位置
        if overlap > 0:
            # 位移量 - 稍微多一点以确保分离
            correction_factor = 1.01  # 减少修正因子以避免过度校正
            correction = overlap * correction_factor
            
            if fixed1:
                # 只移动obj2
                obj2.position = (
                    obj2.position[0] + nx * correction,
                    obj2.position[1] + ny * correction
                )
            elif fixed2:
                # 只移动obj1
                obj1.position = (
                    obj1.position[0] - nx * correction,
                    obj1.position[1] - ny * correction
                )
            else:
                # 两个物体都移动，按质量比例分配
                total_mass = obj1.mass + obj2.mass
                ratio1 = obj2.mass / total_mass
                ratio2 = obj1.mass / total_mass
                
                obj1.position = (
                    obj1.position[0] - nx * correction * ratio1,
                    obj1.position[1] - ny * correction * ratio1
                )
                
                obj2.position = (
                    obj2.position[0] + nx * correction * ratio2,
                    obj2.position[1] + ny * correction * ratio2
                )
        
    def get_object_at(self, x, y):
        """
        获取指定物理坐标位置的物体
        
        参数:
            x, y: 物理坐标
            
        返回:
            找到的物理对象，如果没有找到则返回None
        """
        # 从上到下检查，以便先选择顶层物体
        for obj in reversed(self.objects):
            if hasattr(obj, 'contains_point') and obj.contains_point(x, y):
                return obj
        return None
