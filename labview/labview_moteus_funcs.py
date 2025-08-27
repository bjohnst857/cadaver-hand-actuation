import asyncio
import moteus
import math

# Global controller object, initialized in start()
# This allows other functions to access the same controller instance
def start():
    """
    Initialize the moteus motor controller and clear any errors.
    Must be called before using other functions.
    """
    global c
    c = moteus.Controller(id=1)  # Create controller for motor with ID 1

    async def clear_err():
        # Stop the motor to clear any errors
        await c.set_stop()
    asyncio.run(clear_err())  # Run the async error clearing function

def stop():
    """
    Stop the motor controller.
    """
    async def func():
        await c.set_stop()  # Send stop command to controller
    asyncio.run(func())  # Run the async stop function

def get_tel():
    """
    Query the motor controller for current position and torque.
    Returns:
        [position, torque] (list of floats)
    """
    async def func():
        state = await c.query()  # Query all registers from controller
        pos = state.values[moteus.Register.POSITION]  # Current position
        trq = state.values[moteus.Register.TORQUE]    # Current torque
        return pos, trq
    pos, trq = asyncio.run(func())  # Run the async query and get results
    return [pos, trq]

def hold():
    """
    Hold the motor at its current position (zero velocity).
    Returns:
        [position, torque] (list of floats)
    """
    async def func():
        # Set position to NaN (no change), velocity to 0 (hold), and query state
        state = await c.set_position(position=math.nan, velocity=0, query=True)
        pos = state.values[moteus.Register.POSITION]
        trq = state.values[moteus.Register.TORQUE]
        return pos, trq
    pos, trq = asyncio.run(func())
    return [pos, trq]

def move(cmd=math.nan):
    """
    Move the motor to a specified position.
    Args:
        cmd (float): Target position (radians or native units).
    Returns:
        [position, torque] (list of floats)
    """
    async def func():
        # Move to specified position with acceleration limit, and query state
        state = await c.set_position(position=cmd, accel_limit=8, query=True)
        pos = state.values[moteus.Register.POSITION]
        trq = state.values[moteus.Register.TORQUE]
        return pos, trq
    pos, trq = asyncio.run(func())
    return [pos, trq]

def torque(cmd=0.0):
    """
    Apply a feedforward torque to the motor (open-loop torque control).
    Args:
        cmd (float): Desired torque value.
    Returns:
        [position, torque] (list of floats)
    """
    async def func(cmd: float):
        # Set position to NaN (no change), velocity to 0, apply feedforward torque,
        # disable position/velocity control (kp_scale=0, kd_scale=0), and query state
        state = await c.set_position(
            position=math.nan,
            velocity=0,
            feedforward_torque=cmd,
            kp_scale=0,
            kd_scale=0,
            query=True
        )
        pos = state.values[moteus.Register.POSITION]
        trq = state.values[moteus.Register.TORQUE]
        return pos, trq
    pos, trq = asyncio.run(func(cmd))
    return [pos, trq]

def vel_trq(vel_cmd, trq_cmd):
    """
    Command the motor with a velocity and a maximum torque limit.
    Args:
        vel_cmd (float): Desired velocity.
        trq_cmd (float): Maximum allowed torque.
    Returns:
        [position, torque] (list of floats)
    """
    async def func(vel_cmd, trq_cmd):
        # Set velocity and torque limit, and query state
        state = await c.set_position(
            position=math.nan,
            velocity=vel_cmd,
            maximum_torque=trq_cmd,
            query=True
        )
        pos = state.values[moteus.Register.POSITION]
        trq = state.values[moteus.Register.TORQUE]
        return pos, trq
    pos, trq = asyncio.run(func(vel_cmd, trq_cmd))
    return [pos, trq]

