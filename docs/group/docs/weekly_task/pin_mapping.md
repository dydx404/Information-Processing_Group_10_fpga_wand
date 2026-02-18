# Pin Mapping

The ESP32 is connected to a motion sensor, a button, a switch, an IR LED, and a UART connection to the PYNQ board.

Power:
- The ESP32 3.3V pin is used to power the sensor
- All components share a common ground (GND)

Motion sensor (IMU):
- GPIO21 connects to the sensor SDA pin
- GPIO22 connects to the sensor SCL pin

Inputs:
- GPIO18 is connected to a push button (pressed when connected to ground)
- GPIO19 is connected to an on/off switch (on when connected to ground)

Output:
- GPIO23 drives the infrared LED (through appropriate hardware)

UART output:
- GPIO17 sends data from the ESP32 to the PYNQ board
- Ground is shared between the ESP32 and PYNQ
