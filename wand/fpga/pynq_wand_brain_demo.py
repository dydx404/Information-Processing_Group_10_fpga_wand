"""
Ready-to-use PYNQ notebook/script example for Wand-Brain UDP transmission.

This version is tuned for practical notebook use on the board:
- stable camera bring-up with backend fallback
- line-first local sketching instead of dot-heavy output
- longer stroke hold time so brief centroid dropouts do not fragment strokes
- simple hardware-valid gating that matches what worked on the board
"""

from __future__ import annotations

import os
import sys
import time

import cv2
import numpy as np
from IPython.display import clear_output, display
from PIL import Image
from pynq import MMIO, Overlay, allocate


# ------------------------------------------------------------------
# Repo import setup
# ------------------------------------------------------------------
REPO_ROOT = "/home/xilinx/Information-Processing_Group_10_fpga_wand"
FPGA_DIR = f"{REPO_ROOT}/wand/fpga"

for candidate in (REPO_ROOT, FPGA_DIR):
    if candidate not in sys.path:
        sys.path.append(candidate)

try:
    from wand.fpga.pynq_udp_bridge import WandBrainConfig, WandBrainUdpBridge
except ModuleNotFoundError:
    from pynq_udp_bridge import WandBrainConfig, WandBrainUdpBridge


# ============================================================
# Camera helpers
# ============================================================
def open_camera(camera_index=0, width=640, height=480):
    attempts = [
        ("V4L2", cv2.CAP_V4L2),
        ("ANY", cv2.CAP_ANY),
    ]
    last_error = None

    for backend_name, backend in attempts:
        print(f"Trying camera backend: {backend_name}")
        cap = cv2.VideoCapture(camera_index, backend)

        if not cap.isOpened():
            last_error = f"Could not open camera index {camera_index} with {backend_name}"
            cap.release()
            continue

        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        fourcc_str = "".join(chr((fourcc >> (8 * i)) & 0xFF) for i in range(4))

        warm_ok = False
        for _ in range(10):
            ret, _ = cap.read()
            if ret:
                warm_ok = True
                break
            time.sleep(0.05)

        if not warm_ok:
            last_error = f"Camera opened with {backend_name}, but no frames arrived during warm-up"
            cap.release()
            continue

        print("Camera opened.")
        print(f"Backend  : {backend_name}")
        print(f"Requested: {width}x{height}")
        print(f"Actual   : {actual_w}x{actual_h} @ {actual_fps:.2f} FPS")
        print(f"FOURCC   : {fourcc_str}")
        return cap

    raise RuntimeError(last_error or f"Could not open camera index {camera_index}")


def preprocess_frame(frame_bgr, out_w=640, out_h=480, threshold=200):
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (out_w, out_h), interpolation=cv2.INTER_LINEAR)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary


# ============================================================
# MMIO helpers for new register map
# ============================================================
def read_fpga_stats(mmio):
    sum_x_lo = mmio.read(0x00)
    sum_x_hi = mmio.read(0x04) & 0xFF

    sum_y_lo = mmio.read(0x08)
    sum_y_hi = mmio.read(0x0C) & 0xFF

    count = mmio.read(0x10)
    frame_id = mmio.read(0x14)
    valid = mmio.read(0x18) & 0x1

    sum_x = (sum_x_hi << 32) | sum_x_lo
    sum_y = (sum_y_hi << 32) | sum_y_lo

    if count != 0:
        cx = sum_x // count
        cy = sum_y // count
    else:
        cx = 0
        cy = 0

    return {
        "sum_x": sum_x,
        "sum_y": sum_y,
        "count": count,
        "frame_id": frame_id,
        "valid": valid,
        "cx": cx,
        "cy": cy,
    }


def map_point_to_sketch(x, y, src_w, src_h, dst_w, dst_h):
    xs = int(x * dst_w / src_w)
    ys = int(y * dst_h / src_h)
    xs = max(0, min(dst_w - 1, xs))
    ys = max(0, min(dst_h - 1, ys))
    return xs, ys


def smooth_point(prev_pt, current_pt, alpha):
    if prev_pt is None:
        return current_pt

    return (
        int(round((1.0 - alpha) * prev_pt[0] + alpha * current_pt[0])),
        int(round((1.0 - alpha) * prev_pt[1] + alpha * current_pt[1])),
    )


def new_sketch_canvas():
    return np.full((SKETCH_H, SKETCH_W), 255, dtype=np.uint8)


def calibrate_threshold(cap, width, height, sample_count=8):
    peaks = []

    for _ in range(sample_count):
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.05)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LINEAR)
        peaks.append(float(np.percentile(gray, 99.0)))
        time.sleep(0.02)

    if not peaks:
        raise RuntimeError("Calibration failed: no camera frames captured")

    ambient_peak = float(np.median(peaks))
    return int(max(120, min(250, round(ambient_peak + 15.0))))


def mode_defaults(mode):
    defaults = {
        "normal": {
            "threshold": THRESHOLD,
            "min_count": MIN_COUNT_TO_ACCEPT,
            "gap_timeout_ms": GAP_TIMEOUT_MS,
            "max_jump": MAX_JUMP,
            "smoothing_alpha": SMOOTHING_ALPHA,
        },
        "precision": {
            "threshold": min(255, THRESHOLD + 15),
            "min_count": max(2, MIN_COUNT_TO_ACCEPT + 1),
            "gap_timeout_ms": GAP_TIMEOUT_MS + 250,
            "max_jump": max(40, MAX_JUMP - 30),
            "smoothing_alpha": min(0.8, SMOOTHING_ALPHA + 0.20),
        },
        "fast": {
            "threshold": max(100, THRESHOLD - 10),
            "min_count": MIN_COUNT_TO_ACCEPT,
            "gap_timeout_ms": max(250, GAP_TIMEOUT_MS - 300),
            "max_jump": MAX_JUMP + 40,
            "smoothing_alpha": max(0.10, SMOOTHING_ALPHA - 0.15),
        },
        "noisy_room": {
            "threshold": min(255, THRESHOLD + 25),
            "min_count": max(2, MIN_COUNT_TO_ACCEPT + 2),
            "gap_timeout_ms": GAP_TIMEOUT_MS,
            "max_jump": max(50, MAX_JUMP - 20),
            "smoothing_alpha": min(0.8, SMOOTHING_ALPHA + 0.10),
        },
    }
    return dict(defaults.get(mode, defaults["normal"]))


def build_effective_control(control_payload):
    control_payload = control_payload or {}
    mode = str(control_payload.get("mode", "normal"))
    if mode not in {"normal", "precision", "fast", "noisy_room"}:
        mode = "normal"

    effective = mode_defaults(mode)

    vision = control_payload.get("vision") or {}
    stroke = control_payload.get("stroke") or {}
    commands = control_payload.get("commands") or {}

    if "threshold" in vision:
        effective["threshold"] = max(0, min(255, int(vision["threshold"])))
    if "min_count" in vision:
        effective["min_count"] = max(1, int(vision["min_count"]))
    if "gap_timeout_ms" in stroke:
        effective["gap_timeout_ms"] = max(100, int(stroke["gap_timeout_ms"]))
    if "max_jump" in stroke:
        effective["max_jump"] = max(1, int(stroke["max_jump"]))
    if "smoothing_alpha" in stroke:
        effective["smoothing_alpha"] = max(0.0, min(1.0, float(stroke["smoothing_alpha"])))

    effective["revision"] = max(0, int(control_payload.get("revision", 0)))
    effective["enabled"] = bool(control_payload.get("enabled", True))
    effective["armed"] = bool(control_payload.get("armed", True))
    effective["tx_enabled"] = bool(control_payload.get("tx_enabled", True))
    effective["mode"] = mode
    effective["apply_on"] = str(control_payload.get("apply_on", "next_attempt"))
    effective["commands"] = {
        "clear_sketch_token": max(0, int(commands.get("clear_sketch_token", 0))),
        "recalibrate_token": max(0, int(commands.get("recalibrate_token", 0))),
    }
    return effective


def should_apply_control_now(control, bridge):
    if control["apply_on"] == "immediate":
        return True
    return not bridge.has_active_stroke


def apply_control(control, runtime_state, bridge, cap, drawing_state):
    info = {
        "cleared_sketch": False,
        "recalibrated_threshold": None,
        "flushed_stroke": False,
    }

    if (not control["enabled"] or not control["armed"] or not control["tx_enabled"]) and bridge.has_active_stroke:
        info["flushed_stroke"] = bridge.flush()

    if control["commands"]["clear_sketch_token"] > runtime_state["command_tokens"]["clear_sketch_token"]:
        drawing_state["sketch"][:] = 255
        drawing_state["prev_draw_pt"] = None
        drawing_state["smooth_draw_pt"] = None
        info["cleared_sketch"] = True

    if control["commands"]["recalibrate_token"] > runtime_state["command_tokens"]["recalibrate_token"]:
        info["recalibrated_threshold"] = calibrate_threshold(cap, W, H)

    runtime_state["applied_revision"] = control["revision"]
    runtime_state["enabled"] = control["enabled"]
    runtime_state["armed"] = control["armed"]
    runtime_state["tx_enabled"] = control["tx_enabled"]
    runtime_state["mode"] = control["mode"]
    runtime_state["threshold"] = control["threshold"]
    runtime_state["min_count"] = control["min_count"]
    runtime_state["gap_timeout_ms"] = control["gap_timeout_ms"]
    runtime_state["max_jump"] = control["max_jump"]
    runtime_state["smoothing_alpha"] = control["smoothing_alpha"]
    runtime_state["command_tokens"] = dict(control["commands"])

    if info["recalibrated_threshold"] is not None:
        runtime_state["threshold"] = info["recalibrated_threshold"]

    if not runtime_state["enabled"] or not runtime_state["armed"]:
        drawing_state["prev_draw_pt"] = None
        drawing_state["smooth_draw_pt"] = None

    bridge.cfg.gap_timeout_ms = runtime_state["gap_timeout_ms"]
    return info


def post_control_ack(bridge, runtime_state, pending_control, last_error):
    return bridge.ack_node_control(
        {
            "applied_revision": runtime_state["applied_revision"],
            "active_stroke": bridge.has_active_stroke,
            "tx_active": runtime_state["tx_enabled"] and bridge.has_active_stroke,
            "mode": runtime_state["mode"],
            "pending_revision": None if pending_control is None else pending_control["revision"],
            "last_error": last_error,
            "command_tokens": runtime_state["command_tokens"],
        }
    )


# ============================================================
# Configuration
# ============================================================
BIT = "../design_1_wrapper.bit"
W = 640
H = 480
CAMERA_INDEX = 0
THRESHOLD = 200
MIN_COUNT_TO_ACCEPT = 1
N_FRAMES = 1_000_000
PRINT_EVERY = 5

SKETCH_W = 320
SKETCH_H = 240
DOT_RADIUS = 1
LINE_THICKNESS = 3
MAX_JUMP = 120
SMOOTHING_ALPHA = 0.35
DRAW_ISOLATED_POINTS = True
CONTROL_POLL_INTERVAL_MS = 500
ACK_INTERVAL_MS = 1000

# Wand-Brain settings
BRAIN_HOST = os.getenv("BRAIN_HOST", "13.51.156.87")
BRAIN_API_PORT = 8000
BRAIN_UDP_PORT = 41000
DEVICE_NUMBER = 1
WAND_ID = 1
STARTING_STROKE_ID = WAND_ID * 100000
STARTING_PACKET_NUMBER = 0
GAP_TIMEOUT_MS = 1000
MIRROR_X_FOR_BRAIN = True


def run_demo():
    print("Loading overlay...")
    ol = Overlay(BIT)
    print("Loaded overlay.")
    print("IPs found:", list(ol.ip_dict.keys()))

    dma_name = [k for k in ol.ip_dict if "dma" in k.lower()][0]
    cent_name = [k for k in ol.ip_dict if "frame_centroid_axi" in k.lower()][0]

    print("DMA IP:", dma_name)
    print("Centroid IP:", cent_name)

    dma = getattr(ol, dma_name)
    cent_mmio = MMIO(ol.ip_dict[cent_name]["phys_addr"], ol.ip_dict[cent_name]["addr_range"])

    print("Allocating DMA buffer...")
    buf = allocate(shape=(H * W,), dtype=np.uint8)

    print("Opening camera...")
    cap = open_camera(camera_index=CAMERA_INDEX, width=W, height=H)

    print("Opening Wand-Brain bridge...")
    bridge = WandBrainUdpBridge(
        WandBrainConfig(
            brain_host=BRAIN_HOST,
            brain_udp_port=BRAIN_UDP_PORT,
            brain_api_port=BRAIN_API_PORT,
            device_number=DEVICE_NUMBER,
            wand_id=WAND_ID,
            starting_stroke_id=STARTING_STROKE_ID,
            starting_packet_number=STARTING_PACKET_NUMBER,
            gap_timeout_ms=GAP_TIMEOUT_MS,
            mirror_x=MIRROR_X_FOR_BRAIN,
        )
    )

    print("Checking Wand-Brain health...")
    print("Brain health:", bridge.preflight_check())

    frame_counter = 0
    t0 = time.time()
    last_frame_id = None
    drawing_state = {
        "prev_draw_pt": None,
        "smooth_draw_pt": None,
        "sketch": new_sketch_canvas(),
    }
    runtime_state = {
        "applied_revision": 0,
        "enabled": True,
        "armed": True,
        "tx_enabled": True,
        "mode": "normal",
        "threshold": THRESHOLD,
        "min_count": MIN_COUNT_TO_ACCEPT,
        "gap_timeout_ms": GAP_TIMEOUT_MS,
        "max_jump": MAX_JUMP,
        "smoothing_alpha": SMOOTHING_ALPHA,
        "command_tokens": {
            "clear_sketch_token": 0,
            "recalibrate_token": 0,
        },
    }
    pending_control = None
    control_error = None
    control_status = "local defaults"
    last_control_poll_ms = 0
    last_ack_ms = 0

    try:
        initial_control_payload = bridge.get_node_control()
        control = build_effective_control(initial_control_payload.get("control"))
        apply_info = apply_control(control, runtime_state, bridge, cap, drawing_state)
        control_status = f"applied rev {runtime_state['applied_revision']}"
        if apply_info["recalibrated_threshold"] is not None:
            control_status += f", recalibrated threshold={runtime_state['threshold']}"
        post_control_ack(bridge, runtime_state, pending_control, control_error)
    except Exception as exc:
        control_error = f"initial control fetch failed: {exc}"
        control_status = "using local defaults"

    try:
        for _ in range(N_FRAMES):
            loop_ms = time.monotonic_ns() // 1_000_000

            if (loop_ms - last_control_poll_ms) >= CONTROL_POLL_INTERVAL_MS:
                try:
                    control_payload = bridge.get_node_control()
                    incoming_control = build_effective_control(control_payload.get("control"))
                    control_error = None

                    if incoming_control["revision"] != runtime_state["applied_revision"]:
                        if should_apply_control_now(incoming_control, bridge):
                            apply_info = apply_control(incoming_control, runtime_state, bridge, cap, drawing_state)
                            pending_control = None
                            control_status = f"applied rev {runtime_state['applied_revision']}"
                            if apply_info["cleared_sketch"]:
                                control_status += ", sketch cleared"
                            if apply_info["recalibrated_threshold"] is not None:
                                control_status += f", recalibrated threshold={runtime_state['threshold']}"
                            post_control_ack(bridge, runtime_state, pending_control, control_error)
                            last_ack_ms = loop_ms
                        else:
                            pending_control = incoming_control
                            control_status = f"queued rev {incoming_control['revision']} until idle"
                    last_control_poll_ms = loop_ms
                except Exception as exc:
                    control_error = f"control poll failed: {exc}"
                    last_control_poll_ms = loop_ms

            if pending_control is not None and should_apply_control_now(pending_control, bridge):
                try:
                    apply_info = apply_control(pending_control, runtime_state, bridge, cap, drawing_state)
                    control_status = f"applied queued rev {pending_control['revision']}"
                    if apply_info["cleared_sketch"]:
                        control_status += ", sketch cleared"
                    if apply_info["recalibrated_threshold"] is not None:
                        control_status += f", recalibrated threshold={runtime_state['threshold']}"
                    pending_control = None
                    control_error = None
                    post_control_ack(bridge, runtime_state, pending_control, control_error)
                    last_ack_ms = loop_ms
                except Exception as exc:
                    control_error = f"control apply failed: {exc}"

            ret, frame = cap.read()
            if not ret or frame is None:
                clear_output(wait=True)
                print("Warning: camera read failed")
                time.sleep(0.1)
                continue

            binary = preprocess_frame(frame, out_w=W, out_h=H, threshold=runtime_state["threshold"])

            buf[:] = binary.reshape(-1)
            dma.sendchannel.transfer(buf)
            dma.sendchannel.wait()

            stats = read_fpga_stats(cent_mmio)

            frame_counter += 1
            elapsed = time.time() - t0
            fps = frame_counter / elapsed if elapsed > 0 else 0.0

            frame_id = stats["frame_id"]
            new_result = (last_frame_id is None) or (frame_id != last_frame_id)
            last_frame_id = frame_id

            valid_hw = bool(stats["valid"]) and stats["count"] >= runtime_state["min_count"]
            tracking_enabled = runtime_state["enabled"] and runtime_state["armed"]
            valid_for_udp = tracking_enabled and runtime_state["tx_enabled"] and valid_hw
            valid_for_sketch = tracking_enabled and new_result and valid_hw

            if tracking_enabled and runtime_state["tx_enabled"]:
                udp_debug = bridge.process_point(
                    valid=valid_for_udp,
                    x_px=stats["cx"] if valid_for_udp else None,
                    y_px=stats["cy"] if valid_for_udp else None,
                    src_w=W,
                    src_h=H,
                    timestamp_ms=None,
                    frame_id=frame_id,
                )
            else:
                udp_debug = {
                    "action": "disabled" if not runtime_state["enabled"] else ("disarmed" if not runtime_state["armed"] else "tx_disabled"),
                    "stroke_id": bridge.active_stroke_id,
                    "packet_number_after": bridge.packet_number,
                }

            if udp_debug["action"] == "start":
                drawing_state["prev_draw_pt"] = None
                drawing_state["smooth_draw_pt"] = None

            if valid_for_sketch:
                cx_draw = (W - 1) - stats["cx"]
                cy_draw = stats["cy"]
                raw_draw_pt = map_point_to_sketch(cx_draw, cy_draw, W, H, SKETCH_W, SKETCH_H)
                current_draw_pt = smooth_point(
                    drawing_state["smooth_draw_pt"],
                    raw_draw_pt,
                    runtime_state["smoothing_alpha"],
                )
                drawing_state["smooth_draw_pt"] = current_draw_pt

                drew_line = False
                if drawing_state["prev_draw_pt"] is not None:
                    dx = current_draw_pt[0] - drawing_state["prev_draw_pt"][0]
                    dy = current_draw_pt[1] - drawing_state["prev_draw_pt"][1]
                    jump = (dx * dx + dy * dy) ** 0.5
                    if jump <= runtime_state["max_jump"]:
                        cv2.line(
                            drawing_state["sketch"],
                            drawing_state["prev_draw_pt"],
                            current_draw_pt,
                            color=0,
                            thickness=LINE_THICKNESS,
                        )
                        drew_line = True

                if not drew_line and DRAW_ISOLATED_POINTS:
                    cv2.circle(drawing_state["sketch"], current_draw_pt, DOT_RADIUS, color=0, thickness=-1)

                drawing_state["prev_draw_pt"] = current_draw_pt

            if udp_debug["action"] == "end":
                drawing_state["prev_draw_pt"] = None
                drawing_state["smooth_draw_pt"] = None

            if (loop_ms - last_ack_ms) >= ACK_INTERVAL_MS:
                try:
                    post_control_ack(bridge, runtime_state, pending_control, control_error)
                    last_ack_ms = loop_ms
                except Exception as exc:
                    control_error = f"ack failed: {exc}"

            if frame_counter % PRINT_EVERY == 0:
                clear_output(wait=True)
                print("=== FPGA Sketch + UDP TX ===")
                print(f"frame        : {frame_counter}")
                print(f"fps          : {fps:.2f}")
                print(f"control      : {control_status}")
                print(f"revision     : {runtime_state['applied_revision']}")
                print(f"pending rev  : {None if pending_control is None else pending_control['revision']}")
                print(f"enabled      : {runtime_state['enabled']}")
                print(f"armed        : {runtime_state['armed']}")
                print(f"tx_enabled   : {runtime_state['tx_enabled']}")
                print(f"mode         : {runtime_state['mode']}")
                print(f"threshold    : {runtime_state['threshold']}")
                print(f"min_count    : {runtime_state['min_count']}")
                print(f"gap_timeout  : {runtime_state['gap_timeout_ms']}")
                print(f"max_jump     : {runtime_state['max_jump']}")
                print(f"smoothing    : {runtime_state['smoothing_alpha']:.2f}")
                print(f"valid_hw     : {int(valid_hw)}")
                print(f"new_result   : {new_result}")
                print(f"valid_udp    : {valid_for_udp}")
                print(f"valid_sketch : {valid_for_sketch}")
                print(f"frame_id     : {frame_id}")
                print(f"count        : {stats['count']}")

                if valid_hw:
                    print(f"x, y         : ({stats['cx']}, {stats['cy']})")
                else:
                    print("x, y         : no valid blob")

                print(f"udp action   : {udp_debug['action']}")
                print(f"udp stroke   : {udp_debug['stroke_id']}")
                print(f"udp pkt next : {udp_debug['packet_number_after']}")
                if control_error:
                    print(f"control err  : {control_error}")
                display(Image.fromarray(drawing_state["sketch"]))

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        try:
            post_control_ack(bridge, runtime_state, pending_control, control_error)
        except Exception:
            pass
        bridge.flush()
        bridge.close()
        cap.release()
        buf.freebuffer()
        print("Cleaned up.")


if __name__ == "__main__":
    run_demo()
