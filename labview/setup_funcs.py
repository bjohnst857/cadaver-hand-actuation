import asyncio
import moteus


def start(id):
    """Connect to a single moteus controller and clear any faults."""
    async def func(id):
        global c
        c = moteus.Controller(id=id)
        await c.set_stop()  # Stop clears latched errors
    asyncio.run(func(id))


def just_tel():
    """Query and return the controller's current position (revolutions)."""
    async def func():
        state = await c.query()
        pos = state.values[moteus.Register.POSITION]
        return pos
    pos = asyncio.run(func())
    return pos


def rezero():
    """Set the current shaft angle as the zero reference and return the new position."""
    async def func():
        await c.set_output_exact()
        state = await c.query()
        pos = state.values[moteus.Register.POSITION]
        return pos
    pos = asyncio.run(func())
    return pos


def pos_lims(min, max):
    """Write soft position limits (revolutions) to the controller's persistent config."""
    async def func(min, max):
        s = moteus.Stream(c)

        # Pause periodic telemetry so config commands return clean responses
        await s.write_message(b'tel stop')
        await s.flush_read()

        await s.command(f'conf set servopos.position_min {min}'.encode('utf8'))
        await s.command(f'conf set servopos.position_max {max}'.encode('utf8'))
    asyncio.run(func(min, max))
