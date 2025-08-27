import asyncio
import moteus
import math
import time
import numpy as np

def start_multi(num_motors=1):
    """
    Initialize multiple moteus motor controllers and clear any errors.
    Creates a global list 'motors' containing Controller objects for each motor.
    Args:
        num_motors (int): Number of motors to initialize.
    """
    global motors
    motors = [
        moteus.Controller(id=1 + i)
        for i in range(num_motors)
    ]
    async def clear_err():
        # Stop all motors to clear any errors
        for m in motors:
            await m.set_stop()
    asyncio.run(clear_err())

def stop_multi():
    """
    Stop all motor controllers.
    Sends a stop command to each motor in the global 'motors' list.
    """
    async def func():
        for m in motors:
            await m.set_stop()
    asyncio.run(func())

def modes(num_motors, mode_list, pos_cmds, max_torques, vel_cmds, trq_cmds):
    """
    Set control mode and command for each motor independently.
    Allows each motor to be in a different mode (position, velocity, torque, telemetry).
    Args:
        num_motors (int): Number of motors.
        mode_list (list of int): Mode for each motor (0: telemetry, 1: position, 2: velocity+torque, 3: torque).
        pos_cmds (list of float): Position commands for motors.
        max_torques (list of float): Maximum torque limits for motors.
        vel_cmds (list of float): Velocity commands for motors.
        trq_cmds (list of float): Torque commands for motors.
    Returns:
        [positions, torques] (lists of floats for each motor)
    """
    async def func():
        poss, trqs = [], []
        for i, m in enumerate(motors):
            # Telemetry mode: query position and torque, no movement
            if mode_list[i] == 0:
                state = await m.set_position(position=math.nan, velocity=0,
                                             kp_scale=0, kd_scale=0, query=True)
            # Position mode: move to specified position
            elif mode_list[i] == 1:
                state = await m.set_position(position=pos_cmds[i], accel_limit=0.5,
                                             velocity_limit=0.1, query=True, maximum_torque=0.15)
            # Velocity + torque limit mode
            elif mode_list[i] == 2:
                state = await m.set_position(position=math.nan, velocity=vel_cmds[i],
                                             maximum_torque=max_torques[i], query=True)
            # Torque mode: apply feedforward torque
            elif mode_list[i] == 3:
                state = await m.set_position(position=math.nan, velocity=0,
                                             feedforward_torque=trq_cmds[i], kp_scale=0, kd_scale=0, query=True)
            else:
                raise ValueError("Invalid mode")
            poss.append(state.values[moteus.Register.POSITION])
            trqs.append(state.values[moteus.Register.TORQUE])
        return poss, trqs
    poss, trqs = asyncio.run(func())
    return [poss, trqs]

def move(pos_cmds):
    """
    Move all motors to specified positions.
    Args:
        pos_cmds (list of float): Target positions for each motor.
    Returns:
        [positions, torques] (lists of floats for each motor)
    Raises:
        TypeError: If pos_cmds is not a list.
        ValueError: If length of pos_cmds does not match number of motors.
    """
    if type(pos_cmds) is not list:
        raise TypeError("pos_cmds must be a list")
    if len(pos_cmds) != len(motors):
        raise ValueError("Length of pos_cmds must match number of motors")
    
    async def func():
        poss, trqs = [], []
        for i, m in enumerate(motors):
            state = await motors[i].set_position(position=pos_cmds[i], accel_limit=50,
                                                 velocity_limit=100, query=True)
            poss.append(state.values[moteus.Register.POSITION])
            trqs.append(state.values[moteus.Register.TORQUE])
        return poss, trqs
    poss, trqs = asyncio.run(func())
    return [poss, trqs]

def torque(id, cmd=0.0):
    """
    Apply a feedforward torque to a specific motor (open-loop torque control).
    Args:
        id (int): Index of the motor in the motors list.
        cmd (float): Desired torque value.
    Returns:
        [position, torque] (list of floats for the specified motor)
    """
    async def func(id, cmd):
        state = await motors[id].set_position(position=math.nan, velocity=0,
                                              feedforward_torque=cmd, kp_scale=0,
                                              kd_scale=0, query=True)
        pos = state.values[moteus.Register.POSITION]
        trq = state.values[moteus.Register.TORQUE]
        return pos, trq
    pos, trq = asyncio.run(func(id, cmd))
    return [pos, trq]

def vel_trq(id, vel_cmd=0.0, trq_cmd=0.0):
    """
    Command a specific motor with a velocity and a maximum torque limit.
    Args:
        id (int): Index of the motor in the motors list.
        vel_cmd (float): Desired velocity.
        trq_cmd (float): Maximum allowed torque.
    Returns:
        [position, torque] (list of floats for the specified motor)
    """
    async def func(id, vel_cmd, trq_cmd):
        state = await motors[id].set_position(position=math.nan, velocity=vel_cmd,
                                              maximum_torque=trq_cmd, query=True)
        pos = state.values[moteus.Register.POSITION]
        trq = state.values[moteus.Register.TORQUE]
        return pos, trq
    pos, trq = asyncio.run(func(id, vel_cmd, trq_cmd))
    return [pos, trq]

def just_tel(num_motors):
    """
    Query all motors for their current positions only (telemetry).
    Args:
        num_motors (int): Number of motors to query (not used, kept for compatibility).
    Returns:
        positions (list of floats for each motor)
    """
    async def func():
        poss = []
        for m in motors:
            state = await m.query()
            poss.append(state.values[moteus.Register.POSITION])
            # If needed, torque values can also be queried here
        return poss
    poss = asyncio.run(func())
    return poss
