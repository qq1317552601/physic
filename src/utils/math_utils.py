import math

def distance(p1, p2):
    """
    计算两点之间的欧几里得距离
    
    参数:
        p1: 点1的坐标 (x1, y1)
        p2: 点2的坐标 (x2, y2)
        
    返回:
        两点之间的距离
    """
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def dot_product(v1, v2):
    """
    计算两个向量的点积
    
    参数:
        v1: 向量1 (x1, y1)
        v2: 向量2 (x2, y2)
        
    返回:
        点积 v1·v2
    """
    return v1[0] * v2[0] + v1[1] * v2[1]

def cross_product(v1, v2):
    """
    计算两个二维向量的叉积
    
    参数:
        v1: 向量1 (x1, y1)
        v2: 向量2 (x2, y2)
        
    返回:
        叉积 v1×v2 (标量值，表示垂直于xy平面的分量)
    """
    return v1[0] * v2[1] - v1[1] * v2[0]

def normalize(v):
    """
    归一化向量，使其长度为1
    
    参数:
        v: 向量 (x, y)
        
    返回:
        归一化后的向量
    """
    length = math.sqrt(v[0]**2 + v[1]**2)
    if length < 1e-10:  # 避免除以零
        return (0, 0)
    return (v[0] / length, v[1] / length)

def angle_between(v1, v2):
    """
    计算两个向量之间的角度
    
    参数:
        v1: 向量1 (x1, y1)
        v2: 向量2 (x2, y2)
        
    返回:
        角度 (弧度)
    """
    dot = dot_product(v1, v2)
    len1 = math.sqrt(v1[0]**2 + v1[1]**2)
    len2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    # 处理零向量情况
    if len1 < 1e-10 or len2 < 1e-10:
        return 0
        
    # 使用点积公式: cos(θ) = (v1·v2) / (|v1|·|v2|)
    cos_angle = dot / (len1 * len2)
    
    # 由于浮点数精度问题，cos_angle可能略大于1或略小于-1
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    return math.acos(cos_angle)

def rotate_vector(v, angle):
    """
    将向量旋转指定角度
    
    参数:
        v: 向量 (x, y)
        angle: 旋转角度 (弧度)，正值表示逆时针旋转
        
    返回:
        旋转后的向量
    """
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    return (
        v[0] * cos_angle - v[1] * sin_angle,
        v[0] * sin_angle + v[1] * cos_angle
    )

def project_point_to_line(point, line_start, line_end):
    """
    将点投影到直线上
    
    参数:
        point: 点的坐标 (x, y)
        line_start: 直线起点 (x1, y1)
        line_end: 直线终点 (x2, y2)
        
    返回:
        投影点的坐标 (x, y)
    """
    # 直线向量
    line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    
    # 点到直线起点的向量
    point_vec = (point[0] - line_start[0], point[1] - line_start[1])
    
    # 计算线段长度的平方
    line_length_squared = line_vec[0]**2 + line_vec[1]**2
    
    # 如果线段长度接近零，则返回线段起点
    if line_length_squared < 1e-10:
        return line_start
        
    # 计算投影点的参数 t
    # t表示投影点在线段上的位置，0表示起点，1表示终点
    t = max(0, min(1, dot_product(point_vec, line_vec) / line_length_squared))
    
    # 计算投影点坐标
    return (
        line_start[0] + t * line_vec[0],
        line_start[1] + t * line_vec[1]
    )

def point_line_distance(point, line_start, line_end):
    """
    计算点到直线的距离
    
    参数:
        point: 点的坐标 (x, y)
        line_start: 直线起点 (x1, y1)
        line_end: 直线终点 (x2, y2)
        
    返回:
        点到直线的距离
    """
    # 计算投影点
    proj_point = project_point_to_line(point, line_start, line_end)
    
    # 计算点到投影点的距离
    return distance(point, proj_point)

def is_point_in_triangle(point, v1, v2, v3):
    """
    判断点是否在三角形内部
    
    参数:
        point: 点的坐标 (x, y)
        v1, v2, v3: 三角形三个顶点的坐标
        
    返回:
        如果点在三角形内部，返回True，否则返回False
    """
    # 使用重心坐标法
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        
    d1 = sign(point, v1, v2)
    d2 = sign(point, v2, v3)
    d3 = sign(point, v3, v1)
    
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    
    # 如果所有符号都相同（都是正或都是负），则点在三角形内部
    return not (has_neg and has_pos)

def line_line_intersection(line1_start, line1_end, line2_start, line2_end):
    """
    计算两条线段的交点
    
    参数:
        line1_start, line1_end: 第一条线段的起点和终点
        line2_start, line2_end: 第二条线段的起点和终点
        
    返回:
        如果线段相交，返回交点坐标，否则返回None
    """
    # 线段1的向量
    x1, y1 = line1_start
    x2, y2 = line1_end
    
    # 线段2的向量
    x3, y3 = line2_start
    x4, y4 = line2_end
    
    # 计算分母
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    
    # 如果分母为0，则线段平行或共线
    if abs(denom) < 1e-10:
        return None
        
    # 计算ua和ub
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    
    # 如果ua和ub都在[0,1]范围内，则线段相交
    if 0 <= ua <= 1 and 0 <= ub <= 1:
        # 计算交点坐标
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        return (x, y)
    
    return None
