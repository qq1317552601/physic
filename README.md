# 物理运动学可视化软件

## 项目概述

这是一个用Python编写的物理运动学可视化软件，用于模拟和演示各种物理现象。

## 功能特性

- 创建和模拟各种物理对象（如长方体、小球、斜面、弹簧、轻绳）
- 设置各种物理参数（如质量、速度、加速度、摩擦因数、弹簧劲度系数）
- 实时交互式模拟
- 可视化物理现象和运动学过程
- 保存和加载模拟场景

## 项目结构

```
physics_simulator/
├── src/                    # 源代码目录
│   ├── ui/                 # 用户界面模块
│   │   ├── context_menu.py # 上下文菜单管理
│   │   ├── main_window.py  # 主窗口类
│   │   ├── object_factory.py # 物理对象工厂
│   │   ├── property_panel.py # 属性面板
│   │   ├── simulation_view.py # 模拟视图
│   │   └── toolbox.py      # 工具箱面板
│   ├── physics/            # 物理引擎模块
│   │   ├── constraints.py  # 约束条件类
│   │   ├── objects.py      # 物理对象类
│   │   └── simulator.py    # 物理模拟器
│   ├── rendering/          # 渲染模块
│   │   ├── camera.py       # 相机管理
│   │   └── renderer.py     # 渲染器
│   ├── utils/              # 工具模块
│   │   ├── config.py       # 配置管理
│   │   └── error_handler.py # 错误处理
│   └── main.py             # 程序入口
├── resources/              # 资源文件
├── docs/                   # 文档
└── tests/                  # 测试代码
```

## 设计模式

### MVC模式
- **模型(Model)**: `physics/`目录中的类负责管理数据和业务逻辑
- **视图(View)**: `ui/`和`rendering/`目录中的类负责界面展示
- **控制器(Controller)**: 主窗口和面板类连接模型和视图

### 工厂模式
- `object_factory.py`提供创建不同物理对象的统一接口

### 单例模式
- `config.py`和`error_handler.py`使用单例模式管理全局配置和错误处理

### 观察者模式
- 使用Qt信号与槽机制实现组件间通信

### 策略模式
- 不同的物理对象实现共同的接口，允许在运行时替换行为

## 依赖项

- Python 3.6+
- PyQt5
- Numpy (可选，用于高级计算)

## 安装与运行

1. 克隆代码库
2. 安装依赖：`pip install -r requirements.txt`
3. 运行程序：`python src/main.py`

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT许可证 