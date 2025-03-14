import math

class Constraint:
    """
    约束基类
    所有约束的基础类，定义共有属性和方法
    """
    def __init__(self):
        """初始化约束"""
        self.enabled = True
    
    def apply(self):
        """应用约束，子类必须实现此方法"""
        pass
    
    def enable(self):
        """启用约束"""
        self.enabled = True
    
    def disable(self):
        """禁用约束"""
        self.enabled = False

class FixedPositionConstraint(Constraint):
    """
    固定位置约束
    将物体固定在指定位置
    """
    def __init__(self, object, position=None):
        """
        初始化固定位置约束
        
        参数:
            object: 要约束的物理对象
            position: 固定位置，如果为None，则使用对象当前位置
        """
        super().__init__()
        self.object = object
        self.position = position if position is not None else object.position
    
    def apply(self):
        """应用约束，将物体位置重置为固定位置"""
        if self.enabled:
            self.object.position = self.position
            self.object.velocity = (0, 0)  # 固定位置意味着速度为零

class DistanceConstraint(Constraint):
    """
    距离约束
    保持两个物体之间的距离固定
    """
    def __init__(self, object1, object2, distance=None):
        """
        初始化距离约束
        
        参数:
            object1: 第一个物理对象
            object2: 第二个物理对象
            distance: 固定距离，如果为None，则使用初始距离
        """
        super().__init__()
        self.object1 = object1
        self.object2 = object2
        
        # 如果没有指定距离，计算当前距离
        if distance is None:
            dx = object2.position[0] - object1.position[0]
            dy = object2.position[1] - object1.position[1]
            self.distance = math.sqrt(dx*dx + dy*dy)
        else:
            self.distance = distance
    
    def apply(self):
        """应用约束，调整两个物体位置以保持固定距离"""
        if not self.enabled:
            return
            
        # 计算当前距离
        dx = self.object2.position[0] - self.object1.position[0]
        dy = self.object2.position[1] - self.object1.position[1]
        current_distance = math.sqrt(dx*dx + dy*dy)
        
        if current_distance == 0:
            # 避免除以零
            return
            
        # 计算需要调整的比例
        correction_factor = (self.distance - current_distance) / current_distance
        
        # 计算位置调整
        correction_x = dx * correction_factor * 0.5
        correction_y = dy * correction_factor * 0.5
        
        # 如果两个物体都可以移动
        total_mass = self.object1.mass + self.object2.mass
        if total_mass > 0:
            # 按质量比例分配调整
            mass_ratio1 = self.object2.mass / total_mass
            mass_ratio2 = self.object1.mass / total_mass
            
            # 调整第一个物体位置
            self.object1.position = (
                self.object1.position[0] - correction_x * mass_ratio1,
                self.object1.position[1] - correction_y * mass_ratio1
            )
            
            # 调整第二个物体位置
            self.object2.position = (
                self.object2.position[0] + correction_x * mass_ratio2,
                self.object2.position[1] + correction_y * mass_ratio2
            )

class PinJointConstraint(Constraint):
    """
    销钉关节约束
    允许两个物体绕一个固定点旋转
    """
    def __init__(self, object1, object2, pivot_point=None):
        """
        初始化销钉关节约束
        
        参数:
            object1: 第一个物理对象
            object2: 第二个物理对象
            pivot_point: 枢轴点，如果为None，则使用两个物体当前位置的中点
        """
        super().__init__()
        self.object1 = object1
        self.object2 = object2
        
        # 如果没有指定枢轴点，使用两个物体位置的中点
        if pivot_point is None:
            self.pivot_point = (
                (object1.position[0] + object2.position[0]) / 2,
                (object1.position[1] + object2.position[1]) / 2
            )
        else:
            self.pivot_point = pivot_point
        
        # 计算初始的相对位置
        self.relative_pos1 = (
            object1.position[0] - self.pivot_point[0],
            object1.position[1] - self.pivot_point[1]
        )
        
        self.relative_pos2 = (
            object2.position[0] - self.pivot_point[0],
            object2.position[1] - self.pivot_point[1]
        )
        
        # 计算初始的距离
        self.distance1 = math.sqrt(
            self.relative_pos1[0]**2 + self.relative_pos1[1]**2
        )
        
        self.distance2 = math.sqrt(
            self.relative_pos2[0]**2 + self.relative_pos2[1]**2
        )
    
    def apply(self):
        """应用约束，保持物体相对于枢轴点的距离"""
        if not self.enabled:
            return
            
        # 计算当前相对位置
        current_rel_pos1 = (
            self.object1.position[0] - self.pivot_point[0],
            self.object1.position[1] - self.pivot_point[1]
        )
        
        current_rel_pos2 = (
            self.object2.position[0] - self.pivot_point[0],
            self.object2.position[1] - self.pivot_point[1]
        )
        
        # 计算当前距离
        current_distance1 = math.sqrt(
            current_rel_pos1[0]**2 + current_rel_pos1[1]**2
        )
        
        current_distance2 = math.sqrt(
            current_rel_pos2[0]**2 + current_rel_pos2[1]**2
        )
        
        if current_distance1 == 0 or current_distance2 == 0:
            # 避免除以零
            return
            
        # 归一化当前相对位置
        norm_rel_pos1 = (
            current_rel_pos1[0] / current_distance1,
            current_rel_pos1[1] / current_distance1
        )
        
        norm_rel_pos2 = (
            current_rel_pos2[0] / current_distance2,
            current_rel_pos2[1] / current_distance2
        )
        
        # 计算应该在的位置
        target_pos1 = (
            self.pivot_point[0] + norm_rel_pos1[0] * self.distance1,
            self.pivot_point[1] + norm_rel_pos1[1] * self.distance1
        )
        
        target_pos2 = (
            self.pivot_point[0] + norm_rel_pos2[0] * self.distance2,
            self.pivot_point[1] + norm_rel_pos2[1] * self.distance2
        )
        
        # 调整物体位置
        self.object1.position = target_pos1
        self.object2.position = target_pos2

class SpringConstraint(Constraint):
    """
    弹簧约束
    使用弹簧力将两个物体连接起来
    """
    def __init__(self, object1, object2, k=10.0, rest_length=None):
        """
        初始化弹簧约束
        
        参数:
            object1: 第一个物理对象
            object2: 第二个物理对象
            k: 弹簧劲度系数
            rest_length: 弹簧自然长度，如果为None，则使用初始距离
        """
        super().__init__()
        self.object1 = object1
        self.object2 = object2
        self.k = k  # 弹簧劲度系数
        
        # 如果没有指定自然长度，计算当前距离
        if rest_length is None:
            dx = object2.position[0] - object1.position[0]
            dy = object2.position[1] - object1.position[1]
            self.rest_length = math.sqrt(dx*dx + dy*dy)
        else:
            self.rest_length = rest_length
    
    def apply(self):
        """应用约束，计算弹簧力并作用到两个物体上"""
        if not self.enabled:
            return
            
        # 计算当前距离向量
        dx = self.object2.position[0] - self.object1.position[0]
        dy = self.object2.position[1] - self.object1.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            # 避免除以零
            return
            
        # 计算弹簧力大小 F = k * (distance - rest_length)
        force_magnitude = self.k * (distance - self.rest_length)
        
        # 计算力的方向
        force_x = force_magnitude * dx / distance
        force_y = force_magnitude * dy / distance
        
        # 应用力到物体
        # 注意：此处简化了力的应用方式，实际应用中可能需要更复杂的计算
        if self.object1.mass > 0:
            self.object1.velocity = (
                self.object1.velocity[0] + force_x / self.object1.mass,
                self.object1.velocity[1] + force_y / self.object1.mass
            )
        
        if self.object2.mass > 0:
            self.object2.velocity = (
                self.object2.velocity[0] - force_x / self.object2.mass,
                self.object2.velocity[1] - force_y / self.object2.mass
            )

class FloorConstraint(Constraint):
    """
    地面约束
    防止物体穿过地面
    """
    def __init__(self, floor_y=0.0, restitution=0.5):
        """
        初始化地面约束
        
        参数:
            floor_y: 地面的y坐标
            restitution: 弹性系数
        """
        super().__init__()
        self.floor_y = floor_y
        self.restitution = restitution
    
    def apply(self, objects):
        """
        应用约束，检查所有物体是否穿过地面
        
        参数:
            objects: 物理对象列表
        """
        if not self.enabled:
            return
            
        for obj in objects:
            # 只处理有包围盒的物体
            if not hasattr(obj, 'get_bounding_box'):
                continue
                
            # 获取物体的包围盒
            bbox = obj.get_bounding_box()
            min_y = bbox[1]
            
            # 如果物体低于地面
            if min_y < self.floor_y:
                # 调整位置
                penetration = self.floor_y - min_y
                obj.position = (
                    obj.position[0],
                    obj.position[1] + penetration
                )
                
                # 如果物体有速度，应用反弹
                if hasattr(obj, 'velocity'):
                    # 反转y方向速度并应用弹性系数
                    obj.velocity = (
                        obj.velocity[0],
                        -obj.velocity[1] * self.restitution
                    )
                    
                    # 应用摩擦
                    if hasattr(obj, 'friction'):
                        obj.velocity = (
                            obj.velocity[0] * (1.0 - obj.friction),
                            obj.velocity[1]
                        )
