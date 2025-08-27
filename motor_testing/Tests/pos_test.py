from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import moteus
import asyncio
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Handler called when a Phidget device is attached
def onAttach(self):
    print("Attach!")

# Handler called when a Phidget device is detached
def onDetach(self):
    print("Detach!")

# Handler called when a Phidget error occurs
def onError(self, code, description):
    print("Error: " + ErrorEventCode.getName(code) + ", " + str(description))

# Initializes and attaches a Phidget VoltageRatioInput channel
def phidget_start():
    # Declare global variable for voltage ratio input
    global voltageRatioInput1

    # Initialize VoltageRatioInput for channel 1 (S-type load cell)
    voltageRatioInput1 = VoltageRatioInput()
    voltageRatioInput1.setOnAttachHandler(onAttach)
    voltageRatioInput1.setOnDetachHandler(onDetach)
    voltageRatioInput1.setOnErrorHandler(onError)
    voltageRatioInput1.setChannel(1)  # Set to channel 1
    voltageRatioInput1.openWaitForAttachment(5000)  # Wait for device to attach
    voltageRatioInput1.setDataRate(1000)  # Set data rate in ms

    time.sleep(2)  # Delay to ensure device is ready

# Initializes the moteus motor controller and clears any errors
def moteus_start():
    global c1
    c1 = moteus.Controller(id = 1) # Change ID as needed to select different motor
    async def clear_err():
        await c1.set_stop()
        await c1.set_position_wait_complete(position=0, velocity=0, accel_limit=0.5)
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
    cmd_poss, times, trqs, pos, vels, vlt_ratios = ([] for _ in range(6))

    # Asynchronous main loop for running the test
    async def main_loop():
        while True:
            runtime = time.time() - start  # Elapsed time
            print(runtime)  # Print elapsed time for monitoring

            # End test after 20 seconds
            if runtime > 20:
                print("Test completed")
                break

            # Calculate commanded position (triangle waveform)
            if runtime < 10:
                cmd_pos = 0.2 * runtime
            else:
                cmd_pos = 0.2 * (20 - runtime)

            # Record time and commanded position
            times.append(runtime)
            cmd_poss.append(cmd_pos)

            # Send position command to motor and record feedback
            state = await c1.set_position(
                position=cmd_pos, velocity=0, 
                maximum_torque=0.2, query=True
            )
            trqs.append(state.values[moteus.Register.TORQUE])      # Actual torque
            pos.append(state.values[moteus.Register.POSITION])      # Position
            vels.append(state.values[moteus.Register.VELOCITY])     # Velocity

            # Read load cell voltage ratio
            vlt_ratios.append(voltageRatioInput1.getVoltageRatio())

            time.sleep(0.01)  # Small delay for data rate

    # Run the asynchronous main loop
    asyncio.run(main_loop())

    # Close the load cell channel
    voltageRatioInput1.close()

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

    fig.suptitle('Pos Test Results', fontsize=16)

    # Save plot to file with timestamp
    current_time = datetime.now().strftime("%m-%d_%H-%M")
    plt.savefig(f'pos_test_plot_{current_time}.png')

    # Save data to CSV file
    # Columns: time, position, commanded position, velocity, torque, voltage ratio
    data = np.column_stack((times, pos, cmd_poss, vels, trqs, vlt_ratios))
    np.savetxt(f'pos_test_data_{current_time}.csv', data)

# Entry point for script execution
if __name__ == '__main__':
	main()