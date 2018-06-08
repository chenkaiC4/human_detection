# human_detection

## 技术点

- 采用 CamShift 或者 meanShift 的运动跟踪
- 采用 KalmanFilter 滤波器进行轨迹预测
- 采用 KNN 背景分割器，抽离背景


## 程序逻辑

程序启动，先对**背景区域**进行特征提取(20帧或者更多)。之后开始检测、跟踪、逻辑判断。

其中有两个类，`Human` 和 `HumanManager`。

-----------------------------

`Human` 类包含下面的数据：


- `int` ID
- `[]` 每一帧的中心点 centers
- 卡尔曼滤波器
- 运动跟踪器，meanShift 或者 camShift


----------------------------

`HumanManager` 类包含下面的数据：


- `[]` 检测到的 humans


`Main`函数负责从摄像头读取帧，逻辑处理，均在 `HumanManager` 中处理。


## 设置

在 `config.py` 中设置阈值参数。