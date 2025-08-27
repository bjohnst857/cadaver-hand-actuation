from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import moteus
import asyncio
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import math

# Handler called when a Phidget device is attached
def onAttach(self):
    print("Attach!")
    time.sleep(2)  # Wait for device to stabilize

# Handler called when a Phidget device is detached
def onDetach(self):
    print("Detach!")

# Handler called when a Phidget error occurs
def onError(self, code, description):
    print("Error: " + ErrorEventCode.getName(code) + ", " + str(description))

# Initializes and attaches a Phidget VoltageRatioInput channel
def phidget_start():
    global voltageRatioInput0
    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput0.setOnAttachHandler(onAttach)
    voltageRatioInput0.setOnDetachHandler(onDetach)
    voltageRatioInput0.setOnErrorHandler(onError)
    voltageRatioInput0.setHubPort(0)
    voltageRatioInput0.setDeviceSerialNumber(707604)
    voltageRatioInput0.openWaitForAttachment(5000)
    voltageRatioInput0.setDataRate(50)
    time.sleep(2)  # Delay to ensure device is ready

# Initializes the moteus motor controller and clears any errors
def moteus_start():
    global c1
    c1 = moteus.Controller(id = 1) # Change ID as needed to select different motor
    async def clear_err():
        await c1.set_stop()
    asyncio.run(clear_err())

# Stops the moteus motor controller
def moteus_stop():
    async def func():
        await c1.set_stop()
    asyncio.run(func())

# Main test routine
def main():
    # Initialize Phidget load cell and motor controller
    phidget_start()
    moteus_start()
    start = time.time()  # Record start time

    # Initialize empty lists for data collection
    times, pos, trqs, vlt_ratios, vels, cmd_vels = ([] for _ in range(6))

    # Asynchronous main loop for running the test
    async def main_loop():
        while True:
            runtime = time.time() - start  # Elapsed time
            print(runtime)  # Print elapsed time for monitoring

            # End test after 20 seconds
            if runtime > 20:
                print("Test completed")
                break

            # Calculate commanded velocity (step waveform)
            if runtime < 10:
                cmd_vel = 0.2
            else:
                cmd_vel = -0.2

            # Record time and commanded velocity
            times.append(runtime)
            cmd_vels.append(cmd_vel)

            # Send velocity command to motor and record feedback
            state = await c1.set_position(
                position=math.nan, velocity=cmd_vel, 
                maximum_torque=0.2, query=True
            )
            trqs.append(state.values[moteus.Register.TORQUE])      # Actual torque
            pos.append(state.values[moteus.Register.POSITION])      # Position
            vels.append(state.values[moteus.Register.VELOCITY])     # Velocity

            # Read load cell voltage ratio
            vlt_ratios.append(voltageRatioInput0.getVoltageRatio())

            time.sleep(0.01)  # Small delay for data rate

    # Run the asynchronous main loop
    asyncio.run(main_loop())

    # Close the load cell channel
    voltageRatioInput0.close()

    # Stop the motor controller
    moteus_stop()

    # Plotting results
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    axs[0, 0].plot(times, pos)
    axs[0, 0].set_title('Position')
    axs[0, 1].plot(times, vels, 'tab:red')
    axs[0, 1].set_title('Velocity')
    axs[1, 0].plot(times, trqs, 'tab:orange')
    axs[1, 0].set_title('Torque')
    axs[1, 1].plot(times, vlt_ratios, 'tab:green')
    axs[1, 1].set_title('Voltage Ratio (Load Cell Output)')

    fig.suptitle('Velocity Test Results', fontsize=16)

    # Save plot to file with timestamp
    current_time = datetime.now().strftime("%m-%d_%H-%M")
    plt.savefig(f'vel_test_plot_{current_time}.png')

    # Save data to CSV file
    # Columns: time, position, commanded velocity, velocity, torque, voltage ratio
    data = np.column_stack((times, pos, cmd_vels, vels, trqs, vlt_ratios))
    np.savetxt(f'vel_test_data_{current_time}.csv', data)

# Entry point for script execution
if __name__ == '__main__':
    main()