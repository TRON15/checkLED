# 电路板LED检测程序开发者指南

此文档针对开发者，建议先阅读README4USER.pdf

> + 一个“模式”：控制版发出控制信号，到led板做出反应并被检测到的一个完整周期。
> + 最好将检测装置置于黑暗环境下，如加上一个盖子。

## 用户端

> 基于python2.7

### 启动

``` 
python GUI.py
``` 

### 重要依赖

```python
import PyQt4
import requests
import json
```

### 文件架构

> + web_func.py: 通过requests库向服务端发送请求。
> + GUI.py: 图形用户界面主程序。

### 重要参数

#### web_func.py

```python
error_limit = 1 # 认为不同曝光中两个点为同一个点的横/纵坐标误差极限，单位：像素，不建议轻易修改
server_address = '192.168.1.54' #注意保持与服务端IP相同
```

#### GUI.py
```python
grid.setSpacing(10) # 控件间隔，不建议随意修改
```


## 服务端（树梅派）

> 基于python2.7

### 启动

```
# IP may be 192.168.1.54
# passwd: hesaitech
ssh -Y pi@IP
cd PCB_test
python raspi_sever.py
```

TODO:写sh脚本自启动

### 重要依赖
```python
import cv2 #opencv
import subprocess
import bottle
```
### 文件架构

> + raspi_server.py: 服务端启动服务主程序。
> + server_func.py: 可调用的服务端函数库。
> + PCBconfig.py: 存储每个模式下标准的led亮灭情况。
> + myfunc.py: 图像处理和与控制版通信函数库
> + calibration.py: 单独运行的校准程序，能实时显示，用于debug。
> + check.py: 单独运行的测试程序，能实时现实，用于debug。

### 重要参数

#### raspi_server.py
```python
#　注意端口号需要与用户端的一致
run(app=app, host='0.0.0.0', port=18888)
```

TODO:在用户端增加选端口和IP的功能

#### myfunc.py

```python
'''
认为不同曝光中两个点为同一个点的横/纵坐标误差极限，单位：像素
不建议轻易修改,这里此参数只对calibration.py和check.py起作用
'''
error_limit = 1 
'''
初始曝光度范围，要求在此范围内，不同颜色，不同功率的led都能有发光面积在预设范围内的情况
'''
exp_range　= range(1,36) 
'''
每个pattern的测试次数
在测试中发现有的时候一些led由于过亮/过暗/过于紧挨而刚好触到边界条件
所以使每个pattern重复测试几次
'''
test_num = 3
'''
预设发光面积,每一帧中符合此预设面积的led的位置被添加到led序列中
等待和之前已经探测到的led位置取差集，与中exp_range有联动，需要联调
'''
area_bound = 15
'''
预设发光面积误差，与中exp_range有联动，需要联调
'''
area_error_limit = 4
'''
灰度图转二值化图像的阈值，高于此取1,低于此取0
由于系统在低曝光度下工作，所以取的偏低，不建议轻易修改
'''
binary_bound　= 100
'''
树梅派需要用到的IO口，采用BCM模式编号
'''
iolist = [17, 27, 22, 5, 6, ...]
'''
控制板通信函数
'''
def send_message_*():
'''
通信函数列表，添加新的模式需要更新此表
'''
send_message = [send_message_1, ...]
```
### 重要函数

#### findPos_frame() in myfunc.py

输入一帧的图像，转灰度图后二值化，用cv2.findContours()函数边缘检测，根据预设的边缘围成的面积筛选，当边缘的面积和预设面积的误差在一定范围内则认为是目标led。返回所有符合要求的边缘的重心和面积。

#### findPos_cap() in myfunc.py

输入要开启的摄像头的编号和这个时候pattern的编号，主循环将曝光度从低到高以1为步长提升，每次得到的图像传给findPos_frame(), 并用一个列表保存视频流中的亮的led的位置，将findPos_frame()返回的led的位置和自己的列表中的led位置比较， 超出误差范围的认为是一个新的led,添加到自己的led序列中，并实时显示已经探测到的亮的led的位置。在曝光度循环外还有一个测试次数循环，为保险起见，可设定测试次数，选择得到的亮的led数目最多的led序列返回，返回值为led序列和其长度。

### 其他
目前摄像头不支持opencv中的cap类修改其曝光度，所以其曝光度是开了个子进程去调用v4l2驱动改摄像头曝光度，对运行时间有一定影响。

TODO: 找到更好的改曝光度的方法。
