from dataclasses import dataclass
from typing import Optional
import struct

WB_MAGIC = 0x5742  # 'WB'
WB_VERSION = 1
WB_LEN = 24

PEN_DOWN = 0x01
STROKE_START = 0x02
STROKE_END = 0x04

WB_STRUCT = struct.Struct("<HBBHHIIhhI")  # 24 bytes

@dataclass
class PointEvent:
    device_number: int
    wand_id: int
    stroke_id: int
    packet_number: int
    x: float
    y: float
    timestamp_ms: int
    flags: int
    pen_down: bool
    stroke_start: bool
    stroke_end: bool

def parse_packet(raw: bytes) -> Optional[PointEvent]:
    # wb-point-v1 binary packet
    if len(raw) == WB_LEN:
        try:
            (magic, version, flags,
             device, wand,
             pkt_no, stroke_id,
             x_q, y_q, t_ms) = WB_STRUCT.unpack(raw)
        except struct.error:
            return None

        if magic != WB_MAGIC or version != WB_VERSION:
            return None
        if not (0 <= x_q <= 32767 and 0 <= y_q <= 32767):
            return None

        return PointEvent(
            device_number=device,
            wand_id=wand,
            stroke_id=stroke_id,
            packet_number=pkt_no,
            x=x_q / 32767.0,
            y=y_q / 32767.0,
            timestamp_ms=t_ms,
            flags=flags,
            pen_down=bool(flags & PEN_DOWN),
            stroke_start=bool(flags & STROKE_START),
            stroke_end=bool(flags & STROKE_END),
        )

    # Optional legacy CSV fallback for dev
    try:
        s = raw.decode("utf-8").strip()
        parts = s.split(",")
        if len(parts) == 4:
            x, y, t, wand = parts
            return PointEvent(
                device_number=0,
                wand_id=int(wand),
                stroke_id=0,
                packet_number=0,
                x=float(x),
                y=float(y),
                timestamp_ms=int(t),
                flags=PEN_DOWN,
                pen_down=True,
                stroke_start=False,
                stroke_end=False,
            )
    except Exception:
        pass

    return None
