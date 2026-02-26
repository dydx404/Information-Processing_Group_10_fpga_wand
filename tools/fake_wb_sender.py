#!/usr/bin/env python3

import socket
import struct
import time

# ------------------------------------------------------------
# Protocol constants (wb-point-v1)
# ------------------------------------------------------------

WB_STRUCT = struct.Struct("<HBBHHIIhhI")  # 24 bytes, little-endian

MAGIC = 0x5742       # 'WB'
VERSION = 1

# Flags
PEN_DOWN      = 0x01
STROKE_START  = 0x02
STROKE_END    = 0x04

# ------------------------------------------------------------
# UDP target
# ------------------------------------------------------------

UDP_ADDR = ("127.0.0.1", 41000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ------------------------------------------------------------
# Identifiers
# ------------------------------------------------------------

device_number = 1
wand_id = 1
stroke_id = 42          # MVP meaning: attempt_id
packet_number = 0

# ------------------------------------------------------------
# Helper: current timestamp (low 32 bits, ms)
# ------------------------------------------------------------

def now_ms_u32() -> int:
    return int(time.time() * 1000) & 0xFFFFFFFF

# ------------------------------------------------------------
# Send a diagonal line while "button held"
# ------------------------------------------------------------

N_POINTS = 40

for i in range(N_POINTS):
    # Normalized coordinates in [0, 1]
    x_norm = i / (N_POINTS - 1)
    y_norm = i / (N_POINTS - 1)

    x_q = int(x_norm * 32767)
    y_q = int(y_norm * 32767)

    flags = PEN_DOWN
    if i == 0:
        flags |= STROKE_START

    payload = WB_STRUCT.pack(
        MAGIC,
        VERSION,
        flags,
        device_number,
        wand_id,
        packet_number,
        stroke_id,
        x_q,
        y_q,
        now_ms_u32()
    )

    sock.sendto(payload, UDP_ADDR)
    packet_number += 1
    time.sleep(0.03)   # ~33 Hz

# ------------------------------------------------------------
# Final packet: button released (STROKE_END)
# ------------------------------------------------------------

flags = STROKE_END   # PEN_DOWN = 0 on final packet

payload = WB_STRUCT.pack(
    MAGIC,
    VERSION,
    flags,
    device_number,
    wand_id,
    packet_number,
    stroke_id,
    x_q,              # repeat last valid point (per protocol)
    y_q,
    now_ms_u32()
)

sock.sendto(payload, UDP_ADDR)

print("Fake wb-point-v1 stroke sent successfully.")