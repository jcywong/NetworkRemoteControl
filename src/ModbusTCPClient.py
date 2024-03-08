"""
modbus tcp 协议 网口远程控制 CX-5104E-L
产品链接：http://www.corxnet.com/product/showproduct.php?id=132
jcywong
2024/03/06
"""
import asyncio
import pymodbus.client as modbusClient
from config import *


def setup_async_client(host, port):
    return modbusClient.AsyncModbusTcpClient(host, port)


async def set_switch_control(client, do: int, isOn: bool):
    """
    继电器正常开关
    :param do:1-4路
    :param isOn:True-开 False-关
    :param client:
    :return:
    """
    await client.connect()
    assert client.connected
    try:
        if do not in range(1, RELAY_DOs + 1):
            raise ValueError("DO参数错误")
        await client.write_coil(do - 1, isOn, slave=RELAY_SLAVE)
    except Exception as e:
        print(f"set_switch_control:{e}")
        raise e
    finally:
        client.close()


async def set_pulse_control(client, do: int, isOn: bool):
    """
    继电器脉冲控制-05功能码-固定2S
    :param client:
    :param do:1-4路
    :param isOn:True-开 False-关
    :return:
    """
    await client.connect()
    assert client.connected
    try:
        if do not in range(1, RELAY_DOs + 1):
            raise ValueError("DO参数错误")
        await client.write_coil(0x3000 + do - 1, isOn, slave=RELAY_SLAVE)
    except Exception as e:
        print(f"set_switch_control:{e}")
        raise e
    finally:
        client.close()


async def set_pulse_control_with_time(client, do: int, time: int = 1000):
    """
    继电器脉冲输出-06功能码-可调时间
    :param client:
    :param time: mm 默认1000mm
    :param do:1-4路
    :return:
    """
    await client.connect()
    assert client.connected
    try:
        if do not in range(1, RELAY_DOs + 1):
            raise ValueError("DO参数错误")
        await client.write_register(do - 1, time, slave=RELAY_SLAVE)
    except Exception as e:
        print(f"set_switch_control:{e}")
        raise e
    finally:
        client.close()


async def set_reverse_control(client, do: int):
    """
    继电器反转控制-05功能码
    :param client:
    :param do: 1-4路
    :return:
    """
    await client.connect()
    assert client.connected
    try:
        if do not in range(1, RELAY_DOs + 1):
            raise ValueError("DO参数错误")
        await client.write_coil(0x5000 + do - 1, True, slave=RELAY_SLAVE)
    except Exception as e:
        print(f"set_switch_control:{e}")
        raise e
    finally:
        client.close()


async def set_all_switch_control(client, isOn: bool):
    """
    继电器全开全关控制
    :param client:
    :param isOn:True-开 False-关
    :return:
    """
    await client.connect()
    assert client.connected
    try:
        if isOn:
            await client.write_coil(0x0032, False, slave=RELAY_SLAVE)
        else:
            await client.write_coil(0x0033, False, slave=RELAY_SLAVE)
    except Exception as e:
        print(f"set_switch_control:{e}")
        raise e
    finally:
        client.close()


async def get_relay_statu(client, do: int):
    """
    读取继电器状态-03功能码-可单独读每个状态
    :param client:
    :param do:1-4路
    :return:isOn
    """
    await client.connect()
    assert client.connected
    try:
        if do not in range(1, RELAY_DOs + 1):
            raise ValueError("DO参数错误")
        rr = await client.read_holding_registers(0x1000 + do - 1, slave=RELAY_SLAVE)
        return rr.registers[0] == 1
    except Exception as e:
        print(f"set_switch_control:{e}")
        raise e
    finally:
        client.close()


async def get_all_relay_status(client):
    """
    读取所有路继电器状态指令-01功能码
    :return:
    """
    await client.connect()
    assert client.connected
    try:
        rr = await client.read_coils(0, RELAY_DOs, slave=RELAY_SLAVE)
        device_status = {}
        for i in range(RELAY_DOs):
            print(f"relay{i + 1} state:{rr.bits[i]}")
            device_status[i + 1] = rr.bits[i]
        return device_status
    except Exception as e:
        print(f"set_switch_control:{e}")
        raise e
    finally:
        client.close()


async def main():
    test_client = setup_async_client(RELAY_HOST, RELAY_PORT)
    state = await get_all_relay_status(test_client)
    print(f"relay1 state:{state}")


if __name__ == "__main__":
    asyncio.run(main())
