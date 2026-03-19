# Register Map

The PS reads the centroid statistics from the custom IP through AXI-Lite MMIO.
In the deployed PYNQ runtime, the register access is implemented in
`FPGA/runtime/pynq_wand_brain_demo.py` inside `read_fpga_stats(...)`.

## Register Layout

| Offset | Name | Width | Description |
| --- | --- | --- | --- |
| `0x00` | `sum_x_lo` | 32 bits | Low word of accumulated x-coordinate sum |
| `0x04` | `sum_x_hi` | 8 bits used | High bits of accumulated x-coordinate sum |
| `0x08` | `sum_y_lo` | 32 bits | Low word of accumulated y-coordinate sum |
| `0x0C` | `sum_y_hi` | 8 bits used | High bits of accumulated y-coordinate sum |
| `0x10` | `count` | 32 bits | Number of bright pixels in the completed frame |
| `0x14` | `frame_id` | 32 bits | Incrementing frame counter |
| `0x18` | `valid` | 1 bit used | Indicates that a frame result is available |

## Software Reconstruction

The software reconstructs the 40-bit sums as:

```python
sum_x = (sum_x_hi << 32) | sum_x_lo
sum_y = (sum_y_hi << 32) | sum_y_lo
```

The centroid is then calculated on the PS:

```python
if count != 0:
    cx = sum_x // count
    cy = sum_y // count
else:
    cx = 0
    cy = 0
```

## Design Note

This register map shows an important architectural choice: the PL returns raw
statistics, while the PS performs the final arithmetic and all higher-level
decision making. That keeps the custom IP small and makes the software side
easier to tune during integration.
