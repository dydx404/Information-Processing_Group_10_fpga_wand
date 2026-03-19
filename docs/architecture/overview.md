# Architecture Overview

The current system is best understood as two coordinated planes:

- a UDP point-stream data plane
- an HTTP control and dashboard plane

## Data Plane

1. PYNQ captures camera frames.
2. The FPGA design computes centroid statistics for bright pixels.
3. PS software filters those results and emits one `wb-point-v1` UDP packet per
   valid point.
4. The cloud backend parses packets and reconstructs live strokes in memory.
5. Finalized strokes are rasterized, scored, and persisted.

## Control Plane

The same PYNQ node also polls the cloud service over HTTP for revisioned control
state:

- `enabled`
- `armed`
- `tx_enabled`
- `mode`
- threshold and stroke-profile settings
- one-shot commands such as `clear_sketch` and `recalibrate`

The browser dashboard also uses HTTP polling for:

- health
- live wand status
- latest attempt
- score
- node control
- recent attempts
- leaderboards

## Responsibility Split

### PL

- centroid-style hardware acceleration

### PS

- camera handling
- preprocessing
- DMA and MMIO orchestration
- validity decisions
- local sketching
- UDP sending
- HTTP control polling and ack

### Cloud Runtime

- UDP receive and parse
- in-memory live attempt state
- rasterization
- scoring
- persistence on finalize
- frontend APIs
