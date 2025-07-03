import asyncio
import moteus
import math
import time

def start_multi(num_motors = 1):
    global motors
    motors = [
        moteus.Controller(id=1 + i)
        for i in range(num_motors)]
    async def clear_err():
        for m in motors:
            await m.set_stop()
    asyncio.run(clear_err())

def stop_multi():
    async def func():
        for m in motors:
            await m.set_stop()
    asyncio.run(func())


def move(num_motors, pos_cmds):
    async def func(pos_cmd):
        poss, trqs = [], []
        for i, m in enumerate(motors):
            state = await motors[i].set_position(position=pos_cmds[i], accel_limit=8, query=True)
            poss.append(state.values[moteus.Register.POSITION])
            trqs.append(state.values[moteus.Register.TORQUE])
        return poss, trqs
    poss, trqs = asyncio.run(func(pos_cmds))
    return poss, trqs

def torque(id, cmd= 0.0):
    async def func(id, cmd):
        state = await motors[id].set_position(position=math.nan, velocity=0,
                                              feedforward_torque=cmd, kp_scale=0,
                                              kd_scale=0, query=True)
        pos = (state.values[moteus.Register.POSITION])
        trq = (state.values[moteus.Register.TORQUE])
        return pos, trq
    pos, trq = asyncio.run(func(id, cmd))
    return [pos, trq]

def vel_trq(id, vel_cmd=0.0, trq_cmd=0.0):
    async def func(id, vel_cmd, trq_cmd):
        state = await motors[id].set_position(position=math.nan, velocity=vel_cmd,
                                              maximum_torque = trq_cmd, kp_scale=0,
                                              kd_scale=0, query=True)
        pos = (state.values[moteus.Register.POSITION])
        trq = (state.values[moteus.Register.TORQUE])
        return pos, trq
    pos, trq =asyncio.run(func(id, vel_cmd, trq_cmd))
    return [pos, trq]

if __name__ == '__main__':
    start_multi(2)
    start = time.monotonic()
    while start + 10 > time.monotonic():
        if round(time.monotonic() - start) % 2 ==0:
            pos, trq = move(2, [0, 1])
        else:
            pos, trq = move(2, [1, 0])
        
        time.sleep(0.05)
    stop_multi()