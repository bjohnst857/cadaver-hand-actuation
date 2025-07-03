from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import moteus
import asyncio
import time
import matplotlib.pyplot as plt

import numpy as np
from datetime import datetime 



def onAttach(self):
	print("Attach!")

def onDetach(self):
	print("Detach!")

def onError(self, code, description):
	print("Error: " + ErrorEventCode.getName(code) + ", " + str(description))

def phidget_start():
	global voltageRatioInput0
	global voltageRatioInput1
	
	voltageRatioInput0 = VoltageRatioInput()
	voltageRatioInput1 = VoltageRatioInput()

	voltageRatioInput0.setChannel(0)
	voltageRatioInput1.setChannel(1)

	

	voltageRatioInput0.openWaitForAttachment(5000)
	voltageRatioInput1.openWaitForAttachment(5000)

	voltageRatioInput0.setDataRate(1000)
	voltageRatioInput1.setDataRate(1000)

def moteus_start():
	global c1
	c1 = moteus.Controller(id = 1)
	async def clear_err():
		await c1.set_stop()
		# state = await c1.set_position_wait_complete(position=0, velocity=0, 
		# 							  accel_limit=0.5, query=True)
		# global strt_trq
		# strt_trq = state.values[moteus.Register.TORQUE]
		# print(f'Starting Torque: {strt_trq}')
	asyncio.run(clear_err())

def moteus_stop():
    async def func():
        await c1.set_stop()
    asyncio.run(func())

def main():
	phidget_start()
	moteus_start()
	start = time.time()
	cmd_trqs = []
	times = []
	trqs = []
	pos = []
	s_ratios = []
	j_ratios = []
	cmd_vels = []
	vels = []
	async def main_loop():
		while True:
			runtime = time.time() - start
			# print(runtime)
			len_test = 20
			peak_trq = -.4
			slope = 2 * peak_trq/len_test
			if runtime > len_test:
				print("Test completed")
				break
			if runtime < len_test / 2:
				cmd_trq = runtime * slope
			else:
				cmd_trq = slope*(len_test - runtime)
			times.append(runtime)
			cmd_trqs.append(cmd_trq)
			state = await c1.set_position(position=float('nan'), velocity=0, 
										 feedforward_torque=cmd_trq, kp_scale=0, 
										 kd_scale=0, query=True)
			trqs.append(state.values[moteus.Register.TORQUE])
			pos.append(state.values[moteus.Register.POSITION])
			vels.append(state.values[moteus.Register.VELOCITY])
			j_ratios.append(voltageRatioInput0.getVoltageRatio())
			s_ratios.append(voltageRatioInput1.getVoltageRatio())
			# cmd_poss.append(cmd_pos)
			# cmd_vels.append(cmd_vel)
			time.sleep(0.01)
	asyncio.run(main_loop())
	voltageRatioInput0.close()
	voltageRatioInput1.close()
	moteus_stop()
	fig, axs = plt.subplots(2, 2, constrained_layout=True)
	axs[0, 0].plot(times, pos)
	axs[0, 0].set_title('Position')
	axs[0, 1].plot(times, j_ratios, 'tab:red')
	axs[0, 1].set_title('Inline Load Cell Ratio')
	axs[1, 0].plot(times, trqs, 'tab:orange')
	axs[1, 0].plot(times, cmd_trqs, 'tab:blue', linestyle='--')
	axs[1,0].legend(['tel_trq', 'cmd_trq'])
	axs[1, 0].set_title('Torque')
	axs[1, 1].plot(times, s_ratios, 'tab:green')
	
	axs[1, 1].set_title('S-Type Load Cell Output')
	
	
	data = np.column_stack((times, trqs, cmd_trqs, s_ratios, j_ratios))
	current_time = datetime.now().strftime("%m-%d_%H-%M")
	np.savetxt(f'trq_test_data_{current_time}.csv', data)
	
	fig.suptitle('Torque Test Results', fontsize=16)

	plt.savefig(f'trq_test_plot_{current_time}.png')
	
if __name__ == '__main__':
	main()