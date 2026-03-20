# Camera Hardware

This folder is reserved for the camera-side hardware notes.

Suggested contents:

- camera model and lens notes
- mounting photos
- field-of-view / placement observations
- lighting constraints
- calibration or positioning notes relative to the wand workspace

The goal is to keep the physical sensing setup documented separately from the
FPGA implementation and the EC2 software stack.
---

# Camera Hardware Notes – Arducam B0332 OV9281 Global Shutter UVC Camera

## Sensor & Key Parameters
- **Sensor Model**: OV9281  
- **Type**: Global shutter, monochrome  
- **Resolution**: 1 MP (1280 × 800)  
- **Pixel Size**: 3 μm × 3 μm  
- **Optical Format**: 1/4 inch  
- **Dynamic Range**: 68 dB  
- **Output Formats**: MJPG / YUY2  
- **Frame Rate**:
  - MJPG: 100 fps @ 1280 × 800
  - YUY2: 10 fps @ 1280 × 800

---

## Optics & Lens
- **Field of View (H)**: 70°  
- **Effective Focal Length (EFL)**: 2.8 mm  
- **Distortion**: < 1%  
- **Lens Mount**: M12 × P0.5 mm  
- **IR Sensitivity**: No IR cut filter; sensitive to near-infrared

> **Note**: The absence of an IR filter makes this camera suitable for low‑light or IR‑illuminated applications. Ambient light performance may require external IR control.

---


# IR Filter Note

- **Aperture**:49mm
- **Pass-Band**:85nm