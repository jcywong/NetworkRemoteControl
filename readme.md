# 硬件信息
网口远程控制 CX-5104E-L
产品链接：http://www.corxnet.com/product/showproduct.php?id=132

# 项目内容
## ModbusTCP协议
### pymodbus库
使用pymodbus库创建一个ModbusTCP客户端，实现对设备的操作
1. 继电器正常开关
2. 继电器脉冲控制-05功能码
3. 继电器脉冲输出-06功能码
4. 继电器反转控制-05功能码
5. 继电器全开全关控制
6. 读取继电器状态-03功能码
7. 读取所有路继电器状态指令-01功能码

### socket库
使用socket库创建一个TCP客户端，实现对设备的操作
1. "AllRelayStatus": 0x01,  # 读取继电器状态指令-01功能码
2. "RelayStatu": 0x03,  # 读取继电器状态-03功能码-可单独读每个状态
3. "SwitchControl": 0x05,  # 继电器正常开关
4. "PulseControl": 0x05,  # 继电器脉冲控制 固定2s
5. "ReverseControl": 0x05,  # 继电器反转控制
6. "AllSwitchControl": 0x05,  # 继电器全开全关控制
7. "PulseControlWithTime": 0x06,  # 继电器脉冲输出-06功能码-可调时间

## TCP协议
### socket库
使用socket库创建一个TCP客户端，实现对设备的操作
1. "AllRelayStatus": 0xB3,  # 读取继电器状态
2. "SwitchControl": 0xA3,  # 继电器正常开关
3. "SequentialConnection": 0xA4,  # 顺序导通
4. "SequentialDisconnection": 0xA5,  # 顺序断开
5. "PulseControl": 0xD3,  # 点动 脉冲
6. "ReverseControl": 0xF3,  # 继电器反转控制
7. "AllSwitchStatus": 0xC3,  # 读取开关量状态