# human_detection

## 技术点

- 采用 CamShift 或者 meanShift 的运动跟踪
- 采用 KalmanFilter 滤波器进行轨迹预测
- 采用 KNN 背景分割器，抽离背景


## 程序逻辑

程序启动，先对背景区域进行特征提取(1000帧，约15s)。之后开始进行检测，跟踪，逻辑判断。

每一帧的处理逻辑：




frame --> findContours  -->  contours
  |                                  \
  |                                   \
  | --------------------------------> isNewObject


-----------------

将现有的 object 在当前 frame 进行卡尔曼滤波预测