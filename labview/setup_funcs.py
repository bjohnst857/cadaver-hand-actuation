import asyncio
import moteus


def start(id):
    async def func(id):
        global c
        c = moteus.Controller(id=id)
        await c.set_stop()
    asyncio.run(func(id))
    
def just_tel():
    async def func():
        state = await c.query()
        pos = state.values[moteus.Register.POSITION]
        return pos
    pos = asyncio.run(func())
    return pos

def rezero():
    async def func():
        await c.set_output_exact()
        state = await c.query()
        pos = state.values[moteus.Register.POSITION]
        return pos
    pos = asyncio.run(func())
    return pos

def pos_lims(min, max):
    async def func(min, max):
        s = moteus.Stream(c)

        await s.write_message(b'tel stop')
        await s.flush_read()
        # old_min = float((await s.command(
        # b'conf get servopos.position_min',
        # allow_any_response=True)).decode('utf8'))

        await s.command(f'conf set servopos.position_min {min}'.encode('utf8'))
        await s.command(f'conf set servopos.position_max {max}'.encode('utf8'))
    asyncio.run(func(min, max))
