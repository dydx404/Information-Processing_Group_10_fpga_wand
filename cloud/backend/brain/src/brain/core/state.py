from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from brain.ingest.parser import PointEvent

Point = Tuple[float, float, int]  # (x, y, timestamp_ms)

@dataclass
class BrainState:
    buffers: Dict[int, List[Point]] = field(default_factory=dict)
    last_event: Optional[PointEvent] = None
    last_render_path: Dict[int, str] = field(default_factory=dict)

    def add_event(self, ev: PointEvent):
        self.last_event = ev
        self.buffers.setdefault(ev.wand_id, []).append((ev.x, ev.y, ev.timestamp_ms))
        if len(self.buffers[ev.wand_id]) > 5000:
            self.buffers[ev.wand_id] = self.buffers[ev.wand_id][-5000:]

    def snapshot(self):
        return {
            "last_event": None if self.last_event is None else self.last_event.__dict__,
            "buffer_sizes": {str(k): len(v) for k, v in self.buffers.items()},
            "last_render_path": self.last_render_path,
        }
