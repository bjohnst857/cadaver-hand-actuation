from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import moteus
import asyncio
import time
import matplotlib.pyplot as plt



def onAttach(self):
	print("Attach!")

def onDetach(self):
	print("Detach!")

def onError(self, code, description):
	print("Error: " + ErrorEventCode.getName(code) + ", " + str(description))

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

def moteus_start():
	global c1
	c1 = moteus.Controller(id = 1)
	async def clear_err():
		await c1.set_stop()
		await c1.set_position_wait_complete(position=0, velocity=0, accel_limit=0.5)
	asyncio.run(clear_err())

def moteus_stop():
    async def func():
        await c1.set_stop()
    asyncio.run(func())

def main():
	phidget_start()
	moteus_start()
	start = time.time()
	cmd_poss = []
	times = []
	trqs = []
	pos = []
	vels = []
	vlt_ratios = []
	async def main_loop():
		
		while True:
			runtime = time.time() - start
			print(runtime)
			if runtime > 20:
				break
			if runtime <10:
				cmd_pos = 0.2 * runtime
			else:
				cmd_pos = 0.2 * (20 - runtime)
			times.append(runtime)
			# cmd_trqs.append(cmd_trq)
			state = await c1.set_position(position=cmd_pos, velocity=0, 
										 maximum_torque = 0.2, query=True)
			trqs.append(state.values[moteus.Register.TORQUE])
			pos.append(state.values[moteus.Register.POSITION])
			vels.append(state.values[moteus.Register.VELOCITY])
			vlt_ratios.append(voltageRatioInput0.getVoltageRatio())
			cmd_poss.append(cmd_pos)
			time.sleep(0.01)
	asyncio.run(main_loop())
	voltageRatioInput0.close()
	moteus_stop()
	
	fig, axs = plt.subplots(2, 2, constrained_layout=True)
	axs[0, 0].plot(times, pos)
	axs[0, 0].set_title('Position')
	axs[0, 1].plot(times, vels, 'tab:red')
	axs[0, 1].set_title('Velocity')
	axs[1, 0].plot(times, trqs, 'tab:orange')
	axs[1, 0].set_title('Torque')
	axs[1, 1].plot(times, vlt_ratios, 'tab:green')
	axs[1, 1].set_title('Voltage Ratio(Load Cell Output)')
	

	fig.suptitle('Pos Test Results', fontsize=16)

	plt.savefig('pos_test_results.png')

if __name__ == '__main__':
	main()