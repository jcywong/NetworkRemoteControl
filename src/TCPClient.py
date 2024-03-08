"""
通过tcpClient实现发送指令到TCP Server
网口远程控制 CX-5104E-L
产品链接：http://www.corxnet.com/product/showproduct.php?id=132
jcywong
2024/03/07
"""

import socket
from config import *

FuncCode = {
    "AllRelayStatus": 0xB3,  # 读取继电器状态
    "SwitchControl": 0xA3,  # 继电器正常开关
    "SequentialConnection": 0xA4,  # 顺序导通
    "SequentialDisconnection": 0xA5,  # 顺序断开
    # "ReverseDisconnection": 0xA6,  # 倒序断开
    "PulseControl": 0xD3,  # 点动 脉冲
    # "DelayedDisconnection": 0xD5,  # 延迟断开
    "ReverseControl": 0xF3,  # 继电器反转控制
    # "AllSwitchControl": 0x05,  # 继电器全开全关控制
    "AllSwitchStatus": 0xC3,  # 读取开关量状态
}


def pack_message(func_code: int, address: int, control: bytes, enabled: bytes, time: int, end: int, ) -> bytes:
    """
    创建报文
    :param end: 结束位
    :param time: 时间
    :param enabled: 使能位
    :param control: 控制位
    :param address:地址
    :param func_code:功能码
    :return:
    """
    message = bytearray([0xCC, 0xDD])  # 报文头
    message.append(func_code)  # 功能码
    message.append(address)  # 地址
    message.extend(control)
    message.extend(enabled)
    message.extend(time.to_bytes(2, byteorder='big'))
    message.extend(end.to_bytes(2, byteorder='big'))
    return message


def unpack_message(message: bytes):
    """
    解包
    :param message:报文
    :return:字典
    """
    data = {
        "header": message[:2],
        "func_code": message[2:3],
        "address": message[3:4],
        "status": message[4:10],
        "end": message[10:]
    }
    if not data:
        print("数据为空或不合法")
        return
    return data


def send_command(ip_address: str, port: int, message: bytes):
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
            response = client_socket.recv(2048)
            if response:
                print("指令发送成功")
                return response
            else:
                print("指令发送失败")
                return
    except Exception as e:
        print(f"发送指令时发生错误: {e}")
        raise e


def calculate_control_bits(relay_list):
    control_byte = bytearray(6)
    for relay in relay_list:
        byte_index = (relay - 1) // 8
        bit_index = (relay - 1) % 8
        control_bit = 1 << bit_index
        control_byte[5 - byte_index] |= control_bit
    return control_byte


def set_switch_control(do: list, func_code: int, time: int = 1000):
    """
    继电器正常开关
    :param time:mm
    :param func_code:
        "SwitchControl": 0xA3,  # 继电器正常开关
        "SequentialConnection": 0xA4,  # 顺序导通
        "SequentialDisconnection": 0xA5,  # 顺序断开
        "PulseControl": 0xD3,  # 点动 脉冲
        "ReverseControl": 0xF3,  # 继电器反转控制
    :param do:需要通的路
    :return:
    """
    for i in do:
        if i not in range(RELAY_DOs + 1):
            print("DO参数错误")
            return

    try:
        ret = pack_message(func_code=func_code,
                           address=RELAY_SLAVE,
                           control=calculate_control_bits(do),
                           enabled=bytes.fromhex("ff ff ff ff ff ff"),
                           time=time,
                           end=0xDDCC)
        response = send_command(RELAY_HOST, RELAY_PORT, ret)
        if response == b'OK!':
            print("指令执行成功")
            return True
        else:
            print("指令执行失败")
            return False
    except Exception as e:
        print(f"SwitchControl:{e}")
        raise e


def get_all_relay_status():
    """
    0xB3,  # 读取继电器状态
    :return:
    """
    try:
        message = bytes.fromhex("CC DD B3 01 00 00 0D BE 7C")
        response = send_command(RELAY_HOST, RELAY_PORT, message)
        date = unpack_message(response)
        if date:
            if (date["header"] == 0xAABB.to_bytes(2)
                    and date["func_code"] == FuncCode["AllRelayStatus"].to_bytes(1)
                    and date["address"] == RELAY_SLAVE.to_bytes(1)):
                relay_status = []
                for i in range(6):
                    byte = date["status"][i]
                    for j in range(8):
                        relay_status.append((byte >> (7 - j)) & 1)
                return relay_status[-RELAY_DOs:][::-1]
        return
    except Exception as e:
        print(f"SwitchControl:{e}")
        raise e


def get_read_switch_status():
    """
    0xC3,  # 读取开关量状态
    :return:
    """
    try:
        message = bytes.fromhex("CC DD C3 01 00 00 0D CE 9C")
        response = send_command(RELAY_HOST, RELAY_PORT, message)
        date = unpack_message(response)
        if date:
            if (date["header"] == 0xAABB.to_bytes(2)
                    and date["func_code"] == FuncCode["AllSwitchStatus"].to_bytes(1)
                    and date["address"] == RELAY_SLAVE.to_bytes(1)):
                switch_status = []
                for i in range(6):
                    byte = date["status"][i]
                    for j in range(8):
                        switch_status.append((byte >> (7 - j)) & 1)
                return switch_status[-SWITCH_DLs:][::-1]
        return
    except Exception as e:
        print(f"SwitchControl:{e}")
        raise e


if __name__ == '__main__':
    set_switch_control([1,2,4], FuncCode["SwitchControl"])

    list1 = get_all_relay_status()
    print(list1)
