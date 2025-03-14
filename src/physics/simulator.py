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
                
                # 检查物体类型是否支持碰撞
                if not (hasattr(obj1, 'contains_point') and hasattr(obj2, 'contains_point')):
                    continue
                    
                # 简单的碰撞检测示例，可以扩展为更复杂的算法
                # 此处只是一个占位符，实际碰撞检测需要更多的物理计算
                collision = self._check_collision(obj1, obj2)
                if collision:
                    self._resolve_collision(obj1, obj2)
    
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
            
        # 更精确的碰撞检测可以在这里实现
        # 例如针对圆形、多边形等的专用碰撞检测
        return True
        
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
        
        # 计算物体之间的相对位置
        dx = obj2.position[0] - obj1.position[0]
        dy = obj2.position[1] - obj1.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            # 避免除以零
            return
            
        # 法向量
        nx = dx / distance
        ny = dy / distance
        
        # 计算相对速度的法向分量
        vx = obj2.velocity[0] - obj1.velocity[0]
        vy = obj2.velocity[1] - obj1.velocity[1]
        vn = vx*nx + vy*ny
        
        # 如果物体正在分离，不需要处理碰撞
        if vn > 0:
            return
            
        # 计算冲量
        m1 = obj1.mass
        m2 = obj2.mass
        
        if m1 <= 0 or m2 <= 0:
            # 静态物体或无质量物体
            return
            
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
        
        # 应用摩擦力
        # 可以在这里添加摩擦力的计算
        
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
