import asyncio
import moteus
import math
import time



def start():
    global c
    c = moteus.Controller()
    async def clear_err():
        await c.set_stop()
    asyncio.run(clear_err())


def stop():
    async def func():
        await c.set_stop()
    asyncio.run(func())

def get_tel():
    async def func():
        state = await c.query()
        pos = (state.values[moteus.Register.POSITION])
        trq = (state.values[moteus.Register.TORQUE])
        return pos, trq      
    pos, trq = asyncio.run(func())
    return [pos, trq]


def hold():
    async def func():
        state = await c.set_position(position = math.nan,velocity = 0,  query = True)
        pos = (state.values[moteus.Register.POSITION])
        trq = (state.values[moteus.Register.TORQUE])
        return pos, trq      
    pos, trq = asyncio.run(func())
    return [pos, trq]

def move(cmd = math.nan):
    async def func():
        state = await c.set_position(position = cmd, accel_limit = 8, query = True)
        pos = (state.values[moteus.Register.POSITION])
        trq = (state.values[moteus.Register.TORQUE])
        return pos, trq      
    pos, trq = asyncio.run(func())
    return [pos, trq]

def torque(cmd=0.0):
    async def func(cmd:float):
        state = await c.set_position(position=math.nan, velocity = 0, 
                                         feedforward_torque = cmd, kp_scale = 0, 
                                         kd_scale = 0, query=True)
        pos = (state.values[moteus.Register.POSITION])
        trq = (state.values[moteus.Register.TORQUE])
        return pos, trq      
    pos, trq = asyncio.run(func(cmd))
    return [pos, trq]

def vel_trq(vel_cmd, trq_cmd):
    async def func(vel_cmd, trq_cmd):
        state = await c.set_position(position=math.nan, velocity=vel_cmd,
                                         maximum_torque = trq_cmd, query=True)
        pos = (state.values[moteus.Register.POSITION])  
        trq = (state.values[moteus.Register.TORQUE])
        return pos, trq
    pos, trq = asyncio.run(func(vel_cmd, trq_cmd))
    return [pos, trq]

if __name__ == '__main__':
    start()
    start_time = time.time()
    while start_time + 10 > time.time():
        [pos, trq] = vel_trq(-0.2, 0.3)
        print(f"pos: {pos}, trq: {trq}")
        time.sleep(0.05)
    stop()