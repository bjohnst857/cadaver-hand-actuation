from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *

def phidget_start():
    """
    Initialize two Phidget load cell channels for simultaneous reading.
    Creates global VoltageRatioInput objects for each load cell.
    Sets channel numbers, opens connections, and sets data rates.
    """
    global in1
    global in2
    in1 = VoltageRatioInput()  # Load cell 1 input object
    in2 = VoltageRatioInput()  # Load cell 2 input object

    in1.setChannel(1)          # Assign channel 1 to in1
    in2.setChannel(2)          # Assign channel 2 to in2

    in1.openWaitForAttachment(5000)  # Wait up to 5 seconds for in1 to attach
    in2.openWaitForAttachment(5000)  # Wait up to 5 seconds for in2 to attach

    in1.setDataRate(1000)      # Set data rate for in1 (ms between samples)
    in2.setDataRate(1000)      # Set data rate for in2

def phidget_data():
    """
    Read voltage ratio from both load cells, convert to force (Newtons), and return.
    Uses calibration offsets and gains for each load cell.
    Returns:
        [force1, force2] (list of floats, force in Newtons for each load cell)
    """
    in1_value = in1.getVoltageRatio()  # Read voltage ratio from load cell 1
    in2_value = in2.getVoltageRatio()  # Read voltage ratio from load cell 2

    # Calibration offsets for each load cell
    offset1 = -0.00015446
    offset2 = -0.00017916

    # Calibration gains for each load cell
    gain1 = -17173000
    gain2 = 16379000

    def vlt_to_N(vlt, offset, gain):
        """
        Convert voltage ratio to force in Newtons using calibration.
        Args:
            vlt (float): Voltage ratio reading.
            offset (float): Calibration offset.
            gain (float): Calibration gain.
        Returns:
            Force in Newtons (float)
        """
        g_to_N = 0.009806650028639  # Conversion factor from grams to Newtons
        return gain * (vlt + offset) * g_to_N

    force1 = vlt_to_N(in1_value, offset1, gain1)  # Convert load cell 1 reading
    force2 = vlt_to_N(in2_value, offset2, gain2)  # Convert load cell 2 reading

    return [force1, force2]

def phidget_stop():
    """
    Close connections to both Phidget load cell channels.
    """
    in1.close()
    in2.close()