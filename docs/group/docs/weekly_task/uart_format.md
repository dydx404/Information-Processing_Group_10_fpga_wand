# UART Data Format 

The ESP32 sends simple text over UART at 115200 baud.

Gesture recordings are marked using clear text lines:
- `<START>` means a gesture has started
- `<END>` means the gesture has finished

While a gesture is active, the ESP32 sends lines such as:

DATA,t_ms,ax,ay,az,gx,gy,gz

Each line represents one sensor reading:
- `t_ms` - the time in milliseconds since the ESP32 started
- `ax, ay, az` - accelerometer values
- `gx, gy, gz` - gyroscope values

This format makes it very easy for the receiver to see where a gesture begins and ends and read the motion data in between.
