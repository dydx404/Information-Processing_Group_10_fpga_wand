# Camera Hardware

This folder documents the camera-side hardware used in the FPGA wand tracking
setup. It covers the selected image sensor, lens characteristics, IR filtering
approach, and the mechanical mounting work used to support the sensing node.

## Purpose

The camera subsystem is responsible for reliably observing the tracked wand tip
under motion. The hardware choice emphasizes:

- fast image capture
- reduced motion distortion
- compatibility with IR-assisted tracking
- practical integration with the `PYNQ-Z1`-based node

## Selected Camera

The camera used for the project is the `Arducam B0332`, based on the `OV9281`
global shutter image sensor.

Relevant supporting files in this folder include:

- `B0332_OV9281_Global_Shutter_UVC_Camera_Datasheet.pdf`
- `CamMount/Design_Notes.md`
- the CAD and render files under `CamMount/`

## Sensor Characteristics

Key parameters of the selected camera are:

- `OV9281` monochrome sensor
- global shutter
- `1280 x 800` resolution
- `1 MP` image size
- `3 um x 3 um` pixel size
- `1/4 inch` optical format
- `68 dB` dynamic range
- UVC output support
- `MJPG` and `YUY2` output formats

## Frame Rate

Documented operating modes include:

- `100 fps` at `1280 x 800` in `MJPG`
- `10 fps` at `1280 x 800` in `YUY2`

For this project, the high frame rate is important because fast wand motion
should not be limited by camera capture speed.

## Why This Camera Was Chosen

This camera appears to have been selected for three main reasons:

- `Global shutter` reduces rolling-shutter distortion when the wand moves
  quickly.
- `High frame rate` supports motion tracking with less temporal blur and better
  responsiveness.
- `Monochrome + IR sensitivity` makes the sensor suitable for filtered or
  IR-assisted optical tracking.

Together, these characteristics make the camera a good fit for a tracking
system rather than a general-purpose imaging application.

## Optics And Lens

The current notes indicate the following lens characteristics:

- `2.8 mm` effective focal length
- approximately `70 deg` horizontal field of view
- distortion below `1%`
- `M12 x P0.5 mm` lens mount

This combination suggests a compact wide-angle configuration suitable for
watching the wand workspace from a fixed camera position.

## IR Sensitivity And Filtering

The camera is noted as having no IR cut filter, which means it is sensitive to
near-infrared light. That makes it suitable for use with IR illumination or IR
pass filtering.

This is useful for the project because:

- the tracked target can remain bright in the IR band
- background visible-light clutter can be reduced
- tracking can be made more robust under mixed lighting conditions

The camera mount work in `CamMount/` is intended to hold the IR filter in front
of the lens while minimizing visible light leakage.

## IR Filter Note

The current filter notes record:

- aperture: `49 mm`
- pass band: `85 nm`

These values should be confirmed and expanded later with the exact center
wavelength, supplier part number, and mounting dimensions.

## Mechanical Integration

Mechanical support for the camera is documented in the `CamMount/` folder,
including CAD files and design notes. The mount work appears to focus on:

- placing the filter securely in front of the camera
- reducing stray visible light
- keeping the assembly easy to build and service

This indicates the sensing setup was designed as a real prototype assembly, not
just a camera selection on paper.

