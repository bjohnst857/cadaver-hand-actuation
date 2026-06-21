"""
Interactive calibration and live tension readout for a Phidget load cell.

Walks the user through taring and a multi-point weight calibration, then streams
live mass, force, and cable tension. Tension is recovered from the measured force
using the entry/exit wrap angles of the cable over the load cell pulley.

Run directly and follow the prompts. Press '0' + Enter to re-zero, Ctrl+C to stop.
"""

from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput
import time
import numpy as np
import matplotlib.pyplot as plt
import threading
import math


def tare(bridge):
    """Record the no-load voltage ratio used as the zero offset."""
    print("=== Taring, nothing on the scale ===")
    time.sleep(1)
    tare_value = bridge.getVoltageRatio()
    print(f"Voltage offset: {tare_value:.6f}\n")
    return tare_value


def calibrate(bridge, tare_value):
    """
    Fit a linear voltage-to-grams calibration from five known weights.

    Returns:
        slope, intercept (float): grams = slope * adjusted_voltage + intercept
        measured_voltages (list of float): tare-adjusted readings used for the fit
    """
    print("=== Calibration ===")
    known_weights = []
    measured_voltages = []

    for i in range(5):
        weight = float(input(f"\nEnter known weight #{i+1} in grams: "))
        voltage = collect_voltage(f"Place {weight}g on the scale and press Enter...", tare_value, bridge)
        known_weights.append(weight)
        measured_voltages.append(voltage)
        print(f"Measured adjusted voltage: {voltage:.6f}")

    slope, intercept = np.polyfit(measured_voltages, known_weights, 1)
    print(f"\nCalibration complete: grams = {slope:.3f} * voltage + {intercept:.3f}\n")
    return slope, intercept, measured_voltages


def get_angles():
    """Prompt for the cable's entry and exit wrap angles and return them in radians."""
    print("For tension and force measurements:")
    theta1_deg = float(input("Enter entry angle 1 (degrees): "))
    theta2_deg = float(input("Enter exit angle 2 (degrees): "))
    return math.radians(theta1_deg), math.radians(theta2_deg)


def collect_voltage(prompt, tare_value, bridge):
    """Prompt the user, then return a single tare-adjusted voltage reading."""
    input(prompt)
    time.sleep(0.5)
    raw = bridge.getVoltageRatio()
    return raw - tare_value


def plot(timestamps, mass_data):
    """Plot recorded mass against time."""
    plt.figure()
    plt.plot(timestamps, mass_data, marker='o', linestyle='-')
    plt.xlabel("Time (s)")
    plt.ylabel("Mass (g)")
    plt.title("Measured Mass Over Time")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def input_listener(bridge, tare_value, slope, intercept, shared):
    """Background thread: pressing '0' + Enter re-zeros the live reading."""
    while True:
        command = input()
        if command.strip() == "0":
            raw = bridge.getVoltageRatio()
            adjusted = raw - tare_value
            shared["offset"] = slope * adjusted + intercept  # New zero in grams
            print("Re-zeroed.")


def main():
    bridge = VoltageRatioInput()
    bridge.setChannel(1)
    bridge.openWaitForAttachment(5000)

    tare_value = tare(bridge)
    slope, intercept, measured_voltages = calibrate(bridge, tare_value)
    theta1_rad, theta2_rad = get_angles()

    # Background re-zero listener shares its offset with the main loop
    shared = {"offset": 0.0}
    threading.Thread(
        target=input_listener,
        args=(bridge, tare_value, slope, intercept, shared),
        daemon=True
    ).start()

    print("Recording live mass (grams) and force (N). Type '0' and Enter to zero, Ctrl+C to quit.")
    mass_data = []
    timestamps = []
    start_time = time.time()

    try:
        while True:
            current_time = time.time() - start_time
            adjusted = bridge.getVoltageRatio() - tare_value
            grams = slope * adjusted + intercept - shared["offset"]
            force_N = grams * 9.8 / 1000

            # Tension from force balance across the cable's wrap over the pulley
            denom = math.sin(theta1_rad) + math.sin(theta2_rad)
            tension = force_N / denom if denom != 0 else float('inf')

            print(f"[{current_time:5.2f} s] Mass: {grams:.2f} g | Force: {force_N:.2f} N | Tension: {tension:.2f} N")

            mass_data.append(grams)
            timestamps.append(current_time)
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nRecording stopped.")

    bridge.close()
    plot(timestamps, mass_data)


if __name__ == '__main__':
    main()
