from dataclasses import dataclass
from typing import Optional

@dataclass
class PointEvent:
    wand_id: int
    x: float
    y: float
    timestamp_ms: int
    flags: int = 0

def parse_packet(raw: bytes) -> Optional[PointEvent]:
    """
    TODO: replace this stub with real parsing using your UDP packet spec.
    For now, accept ASCII 'x,y,t,wand' demo format if you want quick tests.
    """
    try:
        s = raw.decode("utf-8", errors="strict").strip()
        parts = s.split(",")
        if len(parts) == 4:
            x = float(parts[0])
            y = float(parts[1])
            t = int(parts[2])
            wand = int(parts[3])
            return PointEvent(wand_id=wand, x=x, y=y, timestamp_ms=t, flags=0)
    except Exception:
        return None
    return None
