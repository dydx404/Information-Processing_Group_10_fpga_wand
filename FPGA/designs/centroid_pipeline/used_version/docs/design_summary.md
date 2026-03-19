# FPGA Design Summary

## Overview

This is the FPGA design that was used in the working PYNQ + Wand Brain demo.
Its job is not to render or classify the image in hardware. Instead, it reduces
each thresholded camera frame into a small set of statistics that the PS can
read quickly:

- `sum_x`: sum of x-coordinates of bright pixels
- `sum_y`: sum of y-coordinates of bright pixels
- `count`: number of bright pixels
- `frame_id`: monotonically increasing frame counter
- `valid`: indicates that a fresh frame result has been latched

The centroid itself is computed in software on the PS as:

- `cx = sum_x / count`
- `cy = sum_y / count`

This partition keeps the PL simple and fast while leaving higher-level stroke
logic, filtering, networking, and UI behavior in software.

## Top-Level Architecture

The top-level block diagram is shown in [`../images/top.png`](../images/top.png).
The important blocks are:

- `processing_system7_0`
  Zynq PS block. It provides DDR access, the AXI master interface, the fabric
  clock, and the reset source for the programmable logic.
- `axi_dma_0`
  AXI DMA block used in memory-to-stream mode. It reads the thresholded frame
  buffer from DDR and sends it into the custom IP as an AXI4-Stream.
- `frame_centroid_axi_0`
  Custom AXI peripheral containing the centroid-reduction logic. It accepts the
  streaming pixel data and exposes the resulting statistics to the PS through
  AXI-Lite registers.
- `ps7_0_axi_periph`
  AXI interconnect between the PS master port and the AXI-Lite slave
  peripherals.
- `axi_mem_intercon`
  Memory interconnect between the DMA master and PS DDR.
- `rst_ps7_0_50M`
  Reset distribution block driven from the PS fabric clock/reset.

## Data Path

The deployed system uses the following end-to-end path:

1. The PS captures a frame from the USB camera.
2. The PS converts the frame to grayscale, resizes it to `640 x 480`, and
   thresholds it into an 8-bit binary image.
3. The binary image is written into a DMA buffer backed by DDR.
4. `axi_dma_0` streams that buffer into the custom IP using AXI4-Stream.
5. `frame_centroid_axi_0` scans the frame and accumulates centroid statistics.
6. At end-of-frame, the IP latches the results into AXI-Lite readable
   registers.
7. The PS reads those registers over MMIO and computes the centroid.
8. The PS then decides whether to accept the point, draw it locally, and send
   it over UDP to the EC2 backend.

This architecture avoids sending the whole frame back from PL to PS after the
reduction step. Only a few registers need to be read per frame.

## Custom IP Behavior

The core custom HDL is in [`../source/frame_centroid.v`](../source/frame_centroid.v).
Its main behavior is:

- input stream width: `32 bits`
- pixels per beat: `4` grayscale pixels
- expected frame size: `640 x 480`
- pixel test: `pixel >= THRESHOLD`
- accumulates:
  - bright-pixel count
  - sum of bright-pixel x coordinates
  - sum of bright-pixel y coordinates

Internally, the module keeps track of:

- current pixel coordinates `x` and `y`
- `pixel_count`
- running `bright_count`
- running `sum_x`
- running `sum_y`

At the end of a frame, detected either by `s_axis_tlast` or by reaching the
expected number of pixels, it:

- latches `o_sum_x`
- latches `o_sum_y`
- latches `o_count`
- increments `o_frame_id`
- asserts `o_valid`
- resets the running accumulators for the next frame

Because the PS already provides a binary frame, the threshold comparison inside
the IP is effectively selecting the foreground pixels with value `255`.

## PS / PL Split

The design intentionally splits work across PS and PL:

- PL responsibilities:
  - fast per-pixel streaming scan
  - coordinate accumulation
  - compact frame statistics output
- PS responsibilities:
  - camera capture
  - resize and threshold preprocessing
  - DMA management
  - MMIO register reads
  - centroid division
  - filtering and stroke logic
  - UDP transmission to Wand Brain

This was a practical design choice. The reduction step is highly regular and
fits hardware well, while the remaining logic changed often during integration
and was easier to keep in Python on the PYNQ board.

## Register Interface

The PS-side runtime reads the custom IP through AXI-Lite MMIO. The deployed
register map is documented in [`register_map.md`](./register_map.md).

The important design detail is that the PL returns raw sums and pixel count,
not the final centroid division. This keeps the IP smaller and makes the
software side easier to adjust.

## Timing Result

The implementation timing summary is captured in
[`../images/timing.png`](../images/timing.png). The screenshot shows:

- setup WNS: `11.636 ns`
- hold WHS: `0.045 ns`
- pulse width slack: `8.750 ns`
- total failing endpoints: `0`

So the implementation met the user timing constraints for the design version
that was used in the demo.

## Why This Version Was Used

This version was chosen because it matched the final system integration path:

- stable DMA-to-custom-IP streaming
- simple AXI-Lite register readback from the PS
- enough performance for real-time centroid extraction
- easy integration with the PYNQ notebook / script runtime
- simple debugging because the PL outputs interpretable statistics

Compared with a more complex hardware design, this version was easier to
validate end-to-end with the camera, local sketch display, UDP sender, and EC2
backend.

## Known Limitations

- The PL does not perform connected-component analysis. It treats all bright
  pixels in the frame as one combined blob.
- If there are multiple bright regions, the centroid will be the weighted
  average of all of them.
- The design depends on the PS preprocessing stage to produce a clean binary
  image.
- The frame dimensions are fixed by the HDL parameters used in this build.
- Final centroid division still happens in software, not hardware.

These limitations were acceptable for the project because the wand tip was
represented by a bright LED and the integration goal was robust centroid-based
tracking rather than full object segmentation.
