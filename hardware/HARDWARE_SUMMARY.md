# Hardware Report

## 1. Introduction

This report summarizes the hardware work documented under
`fpga_wand/hardware/`. The purpose of this part of the repository is to record
the physical prototype used in the FPGA wand tracking system, including the
camera subsystem, the tracked wand, the node-level hardware arrangement, and
the supporting bill of materials.

The contents of this folder show that the project progressed beyond algorithm
and FPGA development into a working physical prototype with selected hardware,
custom mechanical parts, and a defined sensing configuration.

## 2. Hardware System Overview

The documented hardware is centered on a `PYNQ-Z1`-based node used for image
capture and system integration. At the top level, the hardware folder includes
general notes and a node layout diagram that describe how the main components
fit together.

The single-node layout indicates the following structure:

- a camera connected through a USB hub
- a WiFi adapter connected through the same USB hub
- the hub connected to the `PYNQ-Z1`
- the `PYNQ-Z1` connected to a host computer for power and Ethernet

This arrangement suggests a practical prototype architecture in which the FPGA
board acts as the central processing node while the camera and communications
hardware are attached as external peripherals.

## 3. Camera Subsystem

The camera subsystem is the most fully documented part of the hardware
directory. The current records identify the selected camera as the `Arducam
B0332`, based on the `OV9281` image sensor.

The documented sensor characteristics include:

- monochrome operation
- global shutter imaging
- `1280 x 800` resolution
- `1 MP` image size
- support for `MJPG` and `YUY2` output
- high-speed operation up to `100 fps` in `MJPG`

The camera choice appears to have been driven by the needs of fast optical
tracking. In particular, the use of a global shutter reduces image distortion
during rapid wand motion, while the high frame rate helps ensure that the
camera is not the main bottleneck in the tracking pipeline.

The optics notes further indicate a `2.8 mm` lens with an approximately
`70 deg` horizontal field of view and an `M12 x P0.5 mm` lens mount. The camera
is also described as having no IR cut filter, making it suitable for
near-infrared-sensitive operation.

Taken together, these details show that the selected camera was well matched to
the requirements of a motion-tracking system rather than a general-purpose
imaging task.

## 4. IR Filtering And Camera Mount Design

The repository contains dedicated camera mount assets under
`hardware/camera/CamMount/`, including CAD files, a rendered image, and a set
of design notes. These files provide strong evidence that the optical setup was
mechanically developed rather than left as a loose concept.

The documented design intent of the mount is to:

- position the IR filter directly in front of the camera
- reduce visible light leakage into the optical path
- keep the assembly easy to install, remove, and adjust
- support repeatable positioning during prototype testing

This mount design is important because the effectiveness of IR-assisted
tracking depends not only on the sensor itself, but also on how well the filter
is integrated into the physical camera assembly. The available documentation
shows that the project considered both optical performance and practical
assembly during this stage of development.

## 5. Wand Hardware

The hardware folder also documents the tracked wand used in the final project
direction. The available files include a wand model, a rendered image, and a
simple schematic.

These materials indicate that the final tracked target was a custom handheld
LED wand rather than a complex embedded device. The wand appears to include:

- a long narrow visible structure suitable for tracking
- a custom enclosure
- a pushbutton integrated into the handle
- a simple electrical arrangement using a `7.4V` supply, a red LED, and an IR
  LED

This suggests that the wand was intended to act as a bright and easily detected
optical target for the camera/FPGA pipeline, while keeping the hardware simple
and practical for demonstration purposes.

## 6. Bill Of Materials

The top-level bill of materials provides a first-pass procurement view of the
system. It includes the major camera, compute, optical, power, and enclosure
items needed to assemble the prototype.

The BOM covers:

- cameras and lenses
- USB and connectivity hardware
- `PYNQ-Z1` boards
- WiFi adapters
- LEDs and switches
- battery-related items
- custom 3D-printed mechanical parts

This is a useful foundation for prototype assembly, although it still reads as
a draft document rather than a fully finalized production BOM. Some entries are
generic, some are marked as optional, and a few text encoding issues remain in
the file.

## 7. Assessment Of Current Progress

Based on the files currently present in `hardware/`, the core hardware concept
for the project has already been established. The repository shows evidence of:

- camera selection based on tracking requirements
- definition of the node-level hardware arrangement
- mechanical design work for camera filtering and mounting
- development of a dedicated tracked wand form factor
- preparation of a bill of materials for the build

This means the hardware portion of the project is already beyond the idea stage.
The available documentation points to a real prototype effort with concrete
design decisions and supporting artifacts.

## 8. Remaining Gaps

Although the main hardware direction is clearly documented, the folder still
has some areas that would benefit from further reporting and cleanup.

The most obvious remaining gaps are:

- finalized supplier-ready BOM entries
- clearer assembly instructions
- dimensions and tolerances for the printed parts
- print settings and recommended materials
- fuller wand-side written documentation
- photos of the assembled prototype
- final placement, calibration, and validation notes for the camera setup

These are primarily documentation and refinement tasks rather than missing
fundamental hardware design work.

## 9. Conclusion

The `fpga_wand/hardware/` subtree documents a credible physical prototype for
the FPGA wand tracking project. The strongest elements are the selected global
shutter camera, the IR-aware camera mount design, the custom LED wand model,
and the single-node architecture built around the `PYNQ-Z1`.

In summary, the repository already captures the essential hardware design of the
system. The main next step is to improve completeness and presentation by
expanding assembly details, cleaning the BOM, and recording more evidence from
the final physical build.

