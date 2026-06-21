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
    time.sleep(2)  # Wait for device to stabilize

# Handler called when a Phidget device is detached
def onDetach(self):
    print("Detach!")

# Handler called when a Phidget error occurs
def onError(self, code, description):
    print("Error: " + ErrorEventCode.getName(code) + ", " + str(description))

# Initializes and attaches two Phidget VoltageRatioInput channels
def phidget_start():
    # Declare global variables for both voltage ratio inputs
    global voltageRatioInput1, voltageRatioInput2

    # Initialize VoltageRatioInput for channel 1 (S-type load cell)
    voltageRatioInput1 = VoltageRatioInput()
    voltageRatioInput1.setOnAttachHandler(onAttach)
    voltageRatioInput1.setOnDetachHandler(onDetach)
    voltageRatioInput1.setOnErrorHandler(onError)
    voltageRatioInput1.setChannel(1)  # Set to channel 1
    voltageRatioInput1.openWaitForAttachment(5000)  # Wait for device to attach
    voltageRatioInput1.setDataRate(1000)  # Set data rate in ms

    # Initialize VoltageRatioInput for channel 2 (Inline load cell)
    voltageRatioInput2 = VoltageRatioInput()
    voltageRatioInput2.setOnAttachHandler(onAttach)
    voltageRatioInput2.setOnDetachHandler(onDetach)
    voltageRatioInput2.setOnErrorHandler(onError)
    voltageRatioInput2.setChannel(2)  # Set to channel 2
    voltageRatioInput2.openWaitForAttachment(5000)  # Wait for device to attach
    voltageRatioInput2.setDataRate(1000)  # Set data rate in ms

    time.sleep(2)  # Delay to ensure devices are ready

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
    # Key parameters to change for different tests
    len_test = 20  # Duration of test in seconds
    peak_trq = -.6 # Peak torque command in Nm

    # Initialize Phidget load cells and motor controller
    phidget_start()
    moteus_start()
    start = time.time()  # Record start time

    # Initialize empty lists for data collection
    cmd_trqs, times, trqs, pos, s_ratios, inline_ratios, vels = ([] for _ in range(7))

    # Asynchronous main loop for running the test
    async def main_loop():
        while True:
            runtime = time.time() - start  # Elapsed time
            slope = 2 * peak_trq / len_test  # Slope for torque ramp

            # End test after specified duration
            if runtime > len_test:
                print("Test completed")
                break

            # Calculate commanded torque (triangle waveform)
            if runtime < len_test / 2:
                cmd_trq = runtime * slope
            else:
                cmd_trq = slope * (len_test - runtime)

            # Record time and commanded torque
            times.append(runtime)
            cmd_trqs.append(cmd_trq)

            # Send command to motor and record feedback
            state = await c1.set_position(
                position=float('nan'), velocity=0, 
                feedforward_torque=cmd_trq, kp_scale=0, 
                kd_scale=0, query=True
            )
            trqs.append(state.values[moteus.Register.TORQUE])      # Actual torque
            pos.append(state.values[moteus.Register.POSITION])      # Position
            vels.append(state.values[moteus.Register.VELOCITY])     # Velocity

            # Read load cell voltage ratios
            inline_ratios.append(voltageRatioInput2.getVoltageRatio())  # Inline load cell
            s_ratios.append(voltageRatioInput1.getVoltageRatio())       # S-type load cell

            time.sleep(0.01)  # Small delay for data rate

    # Run the asynchronous main loop
    asyncio.run(main_loop())

    # Close the inline load cell channel
    voltageRatioInput2.close()
    
    # Stop the motor controller
    moteus_stop()

    ## Get Tension value from load cell voltage ratios
    # Load cell calibration parameters
    offset = 0.00017916
    scale_factor = 16379000
    # tension = (voltage_ratio - offset) * scale_factor * conversion to Newtons
    g_to_N = 0.009806650028639
    tensions = ((np.array(inline_ratios) - offset) * scale_factor * g_to_N).tolist() 

    # Plotting results
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    axs[0, 0].plot(times, pos)
    axs[0, 0].set_title('Position')
    axs[0, 1].plot(times, inline_ratios, 'tab:red')
    axs[0, 1].set_title('Inline Load Cell Ratio')
    axs[1, 0].plot(times, trqs, 'tab:orange')
    axs[1, 0].plot(times, cmd_trqs, 'tab:blue', linestyle='--')
    axs[1, 0].legend(['tel_trq', 'cmd_trq'])
    axs[1, 0].set_title('Torque')
    axs[1, 1].plot(times, s_ratios, 'tab:green')
    axs[1, 1].set_title('S-type Ratio')

    fig.suptitle('Torque Test Results', fontsize=16)

    # Timestamp shared by the plot and data filenames for this run
    current_time = datetime.now().strftime("%m-%d_%H-%M")
    plt.savefig(f'trq_test_plot_{current_time}.png')  # Save plot to file

    ## Save data to CSV
    data = np.column_stack((times, trqs, cmd_trqs, inline_ratios, tensions))
    np.savetxt(f'trq_test_data_{current_time}.csv', data)  # Save data to CSV
    
# Entry point for script execution
if __name__ == '__main__':
	main()