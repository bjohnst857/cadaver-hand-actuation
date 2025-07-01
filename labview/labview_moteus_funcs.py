import asyncio
import moteus
import math
import time

def get_pos():
    async def func():
        state = await c.query()
        global pos
        pos = (state.values[moteus.Register.POSITION])
        print(type(pos))
        
    asyncio.run(func())
    return pos

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

def hold():
    async def func():
        state = await c.set_position(position = math.nan,velocity = 0,  query = True)
        global pos
        pos = (state.values[moteus.Register.POSITION])      
    asyncio.run(func())
    return pos

def move(cmd = math.nan):
    async def func():
        state = await c.set_position(position = cmd, accel_limit = 8, query = True)
        global pos
        pos = (state.values[moteus.Register.POSITION])      
    asyncio.run(func())
    return pos

def torque(cmd:float):
    if type(cmd) != float:
        raise "input must be convertable to a float"
    async def func(cmd:float):
        state = await c.set_position(position=math.nan, velocity = 0, 
                                         feedforward_torque = cmd, kp_scale = 0, 
                                         kd_scale = 0, query=True)
        global pos, trq
        pos = (state.values[moteus.Register.POSITION])  
        trq = (state.values[moteus.Register.TORQUE])
    asyncio.run(func(cmd))
    return [pos,trq]
