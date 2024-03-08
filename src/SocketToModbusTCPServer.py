"""
通过tcp实现发送指令到ModbusTCP
网口远程控制 CX-5104E-L
产品链接：http://www.corxnet.com/product/showproduct.php?id=132
jcywong
2024/03/05
"""


import socket
from config import *


FuncCode = {
    "AllRelayStatus": 0x01,  # 读取继电器状态指令-01功能码
    # "ReadSwitchStatus": 0x02,  # 读取开关量状态
    "RelayStatu": 0x03,  # 读取继电器状态-03功能码-可单独读每个状态
    "SwitchControl": 0x05,  # 继电器正常开关
    "PulseControl": 0x05,  # 继电器脉冲控制 固定2s
    "ReverseControl": 0x05,  # 继电器反转控制
    "AllSwitchControl": 0x05,  # 继电器全开全关控制
    # "MakeBreak": 0x06,  # 继电器开关控制 执行导通 断开动作
    "PulseControlWithTime": 0x06,  # 继电器脉冲输出-06功能码-可调时间
}


def pack_message(address: int, func_code: int, register_address: bytes, data: int) -> bytes:
    """
    创建6字节报文
    :param address:地址
    :param func_code:功能码
    :param register_address:寄存器地址
    :param data:数据
    :return:
    """
    message = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x06])  # 报文头
    message.append(address)  # 地址
    message.append(func_code)  # 功能码
    message.extend(register_address)  # 寄存器地址
    message.extend(data.to_bytes(2, byteorder='big'))  # 数据
    return message


def send_command(ip_address: str, port: int, message: bytes) -> str:
    """
    发送指令
    :param ip_address:ip地址
    :param port:端口
    :param message:报文
    :return:响应数据的十六进制字符串
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            server_address = (ip_address, port)
            client_socket.connect(server_address)
            client_socket.sendall(message)
            response = client_socket.recv(1024)
            return response.hex()
    except Exception as e:
        print(f"发送指令时发生错误: {e}")
        raise e


def set_switch_control(do: int, isOn: bool):
    """
    继电器正常开关
    :param do:1-4路
    :param isOn:True-开 False-关
    :return:
    """
    if do not in range(RELAY_DOs + 1):
        print("DO参数错误")
        return
    register_address = (
        bytes([a ^ b for a, b in zip((do-1).to_bytes(2, byteorder='big'), 0x0000.to_bytes(2, byteorder='big'))]))
    if isOn:
        data = 0xFF00
    else:
        data = 0x0000
    try:
        ret = pack_message(RELAY_SLAVE, FuncCode["SwitchControl"], register_address, data)
        return send_command(RELAY_HOST, RELAY_PORT, ret)
    except Exception as e:
        print(f"SwitchControl:{e}")
        raise e


def set_pulse_control(do: int, isOn: bool):
    """
    继电器脉冲控制-05功能码-固定2S
    :param do:1-4路
    :param isOn:True-开 False-关
    :return:
    """
    if do not in range(RELAY_DOs + 1):
        print("DO参数错误")
        return
    register_address = (
        bytes([a ^ b for a, b in zip((do-1).to_bytes(2, byteorder='big'), 0x3000.to_bytes(2, byteorder='big'))]))
    if isOn:
        data = 0xFF00
    else:
        data = 0x0000
    try:
        ret = pack_message(RELAY_SLAVE, FuncCode["PulseControl"], register_address, data)
        return send_command(RELAY_HOST, RELAY_PORT, ret)
    except Exception as e:
        print(f"PulseControl:{e}")
        raise e


def set_pulse_control_with_time(do: int, time: int = 1000):
    """
    继电器脉冲输出-06功能码-可调时间
    :param time: mm 默认1000mm
    :param do:1-4路
    :return:
    """
    if do not in range(RELAY_DOs + 1):
        print("DO参数错误")
        return
    register_address = (
        bytes([a ^ b for a, b in zip((do - 1).to_bytes(2, byteorder='big'), 0x0000.to_bytes(2, byteorder='big'))]))
    try:
        ret = pack_message(RELAY_SLAVE, FuncCode["PulseControlWithTime"], register_address, time)
        return send_command(RELAY_HOST, RELAY_PORT, ret)
    except Exception as e:
        print(f"PulseControlWithTime:{e}")
        raise e


def set_reverse_control(do: int):
    """
    继电器反转控制-05功能码
    :param do: 1-4路
    :return:
    """

    if do not in range(RELAY_DOs + 1):
        print("DO参数错误")
        return
    register_address = (
        bytes([a ^ b for a, b in zip((do - 1).to_bytes(2, byteorder='big'), 0x5000.to_bytes(2, byteorder='big'))]))
    data = 0xFF00
    try:
        ret = pack_message(RELAY_SLAVE, FuncCode["ReverseControl"], register_address, data)
        return send_command(RELAY_HOST, RELAY_PORT, ret)
    except Exception as e:
        print(f"ReverseControl:{e}")
        raise e


def set_all_switch_control(isOn: bool):
    """
    继电器全开全关控制
    :param isOn:True-开 False-关
    :return:
    """
    if isOn:
        register_address = 0x0032
    else:
        register_address = 0x0033
    data = 0x0000
    try:
        ret = pack_message(RELAY_SLAVE, FuncCode["AllSwitchControl"], register_address.to_bytes(2, byteorder='big'), data)
        return send_command(RELAY_HOST, RELAY_PORT, ret)
    except Exception as e:
        print(f"AllSwitchControl:{e}")
        raise e


def get_relay_statu(do: int):
    """
    读取继电器状态-03功能码-可单独读每个状态
    :param do:1-4路
    :return:
    """
    if do not in range(RELAY_DOs + 1):
        print("DO参数错误")
        return
    register_address = (
        bytes([a ^ b for a, b in zip((do - 1).to_bytes(2, byteorder='big'), 0x1000.to_bytes(2, byteorder='big'))]))
    data = 0x0001
    try:
        ret = pack_message(RELAY_SLAVE, FuncCode["RelayStatu"], register_address, data)
        response = send_command(RELAY_HOST, RELAY_PORT, ret)
        last_byte = bytes.fromhex(response)[-1]
        if last_byte == 0:
            return False
        elif last_byte == 1:
            return True
        else:
            raise Exception("返回值错误")
    except Exception as e:
        print(f"RelayStatu:{e}")
        raise e


def get_all_relay_status():
    """
    读取4路继电器状态指令-01功能码
    :return:
    """
    register_address = 0x1000
    data = 0x0004  # 读取4路继电器状态
    try:
        ret = pack_message(RELAY_SLAVE, FuncCode["AllRelayStatus"], register_address.to_bytes(2, byteorder='big'), data)
        response = send_command(RELAY_HOST, RELAY_PORT, ret)
        last_Byte = bytes.fromhex(response)
        byte_list = bin(last_Byte[-1])[2:].zfill(4)
        device_status = {}
        for i in range(4):
            device_num = i + 1
            device_status[device_num] = True if byte_list[-device_num] == '1' else False
        return device_status
    except Exception as e:
        print(f"AllRelayStatus:{e}")
        raise e


if __name__ == "__main__":
    print(get_all_relay_status())
