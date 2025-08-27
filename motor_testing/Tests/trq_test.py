from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import moteus
import asyncio
import time
import matplotlib.pyplot as plt
import math
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
    global voltageRatioInput0
    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput0.setOnAttachHandler(onAttach)
    voltageRatioInput0.setOnDetachHandler(onDetach)
    voltageRatioInput0.setOnErrorHandler(onError)
    voltageRatioInput0.setChannel(1)  # Set to channel 1
    voltageRatioInput0.setDeviceSerialNumber(782132)  # Set device serial number
    voltageRatioInput0.openWaitForAttachment(5000)  # Wait for device to attach
    voltageRatioInput0.setDataRate(1000)  # Set data rate in ms

# Initializes the moteus motor controller and clears any errors
def moteus_start():
    global c1
    c1 = moteus.Controller(id = 1) # Change ID as needed to select different motor
    async def clear_err():
        await c1.set_stop()
        # Optionally set initial position or other parameters here
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
    cmd_trqs = []
    times = []
    trqs = []
    pos = []
    vlt_ratios = []
    vels = []

    # Asynchronous main loop for running the test
    async def main_loop():
        while True:
            runtime = time.time() - start  # Elapsed time
            len_test = 5  # Duration of test in seconds

            # End test after specified duration
            if runtime > len_test:
                print("Test completed")
                break

            # Calculate commanded torque (triangle waveform)
            if runtime < len_test / 2:
                cmd_trq = runtime * 0.024 / len_test
            else:
                cmd_trq = 0.024 / len_test * (runtime - len_test)

            # Record time and commanded torque
            times.append(runtime)
            cmd_trqs.append(cmd_trq)

            # Send command to motor and record feedback
            state = await c1.set_position(
                position=float('nan'), velocity=0, 
                feedforward_torque=0, kp_scale=0, 
                kd_scale=0, query=True
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

    ## Get Tension value from load cell voltage ratios
    # Load cell calibration parameters
    offset = 0.00017916
    scale_factor = 16379000
    g_to_N = 0.009806650028639
    # Calculate tension in Newtons using calibration
    tensions = ((np.array(vlt_ratios) - offset) * scale_factor * g_to_N).tolist()

    # Plotting results
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    axs[0, 0].plot(times, pos)
    axs[0, 0].set_title('Position')
    axs[0, 1].plot(times, tensions, 'tab:red')
    axs[0, 1].set_title('Tension (N)')
    axs[1, 0].plot(times, trqs, 'tab:orange')
    axs[1, 0].plot(times, cmd_trqs, 'tab:blue', linestyle='--')
    axs[1, 0].legend(['tel_trq', 'cmd_trq'])
    axs[1, 0].set_title('Torque')
    axs[1, 1].plot(times, vlt_ratios, 'tab:green')
    axs[1, 1].set_title('Voltage Ratio (Load Cell Output)')

    fig.suptitle('Torque Test Results', fontsize=16)

    # Save plot to file with timestamp
    current_time = datetime.now().strftime("%m-%d_%H-%M")
    plt.savefig(f'trq_test_plot_{current_time}.png')

    # Save data to CSV file
    # Columns: time, position, commanded torque, velocity, actual torque, voltage ratio, tension
    data = np.column_stack((times, pos, cmd_trqs, vels, trqs, vlt_ratios, tensions))
    np.savetxt(f'trq_test_data_{current_time}.csv', data)

# Entry point for script execution
if __name__ == '__main__':
    main()