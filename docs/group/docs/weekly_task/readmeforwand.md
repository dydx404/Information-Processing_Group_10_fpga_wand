# ESP32 Motion Wand

ESP32 firmware and breadboard prototype for a handheld motion-sensing wand using an MPU6050 IMU.

The wand detects a quick flick, rotation or swing gestures using gyroscope data, then triggers:
- an IR LED output for tracking
- a vibration motor for haptic feedback

## Features

- ESP32-based motion sensing
- MPU6050 IMU over I2C
- Flick detection using gyroscope values
- IR LED trigger output
- Haptic vibration motor output
- Separate hardware test files for IR LED and motor

---

## Hardware

- ESP32 dev board
- MPU6050 IMU module
- IR LED
- Resistor for IR LED
- Small vibration motor
- Breadboard
- Jumper wires
- USB cable for ESP32 programming/power

---

## Pin Connections

### MPU6050 -> ESP32

- VCC -> 3V3
- GND -> GND
- SDA -> GPIO21
- SCL -> GPIO22

### IR LED -> ESP32

- GPIO25 -> resistor -> long leg of IR LED
- short leg of IR LED -> GND

### Vibration Motor -> ESP32

- red wire -> GPIO26
- blue wire -> GND

---

## Important Breadboard Notes

Make sure connected parts share the same breadboard strip only when they are supposed to be electrically connected.

For the IR LED circuit:
- one resistor leg must share a strip with the LED long leg
- the other resistor leg must share a strip with the wire from GPIO25
- the LED short leg must share a strip with GND

The LED and resistor must form a complete path:

GPIO25 -> resistor -> LED -> GND

---

## Arduino IDE Setup

1. Open Arduino IDE
2. Select the correct ESP32 board, e.g. **ESP32 Dev Module**
3. Select the correct port
4. Install the required libraries:
   - `Wire.h`
   - `MPU6050.h`

If needed, install the MPU6050 library through Library Manager.

---

## Files

### `esp32_wand_controller.ino`
Main wand code. Detects flick gestures using gyro data and triggers the IR LED and motor.

### `ir_led_test.ino`
Simple test file for the IR LED. Turns the IR LED on for 2 seconds, then off for 2 seconds.

### `motor_test.ino`
Simple test file for the vibration motor. Turns the motor on for 1 second, then off for 2 seconds.

---

## How to Use

### 1. Test the motor
Upload `motor_test.ino`.

Expected behaviour:
- motor vibrates for 1 second
- motor stops for 2 seconds
- repeats

### 2. Test the IR LED
Upload `ir_led_test.ino`.

Expected behaviour:
- IR LED turns on for 2 seconds
- IR LED turns off for 2 seconds
- repeats

Note:
IR light is usually not visible to the eye. Use a phone camera to check whether the IR LED is turning on.

### 3. Run the main wand code
Upload `esp32_wand_controller.ino`.

Open Serial Monitor at:
`115200 baud`

Expected Serial output:
- gyroscope values
- gyro motion score
- `FLICK DETECTED` when a flick gesture is recognised

To trigger the wand:
- use a quick wrist flick
- use a short swish motion
- do not move it very slowly

When a flick is detected:
- the motor vibrates briefly
- the IR LED output is set HIGH briefly

---

## Tuning

In `esp32_wand_controller.ino`:

### Threshold sensitivity
```cpp
const int gyroThreshold = 9000;
