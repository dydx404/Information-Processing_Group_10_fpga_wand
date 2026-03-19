from __future__ import annotations

import copy
import json
import threading
import time
from pathlib import Path
from typing import Any


ALLOWED_MODES = {"normal", "precision", "fast", "noisy_room"}
ALLOWED_APPLY_ON = {"immediate", "next_attempt"}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _default_control(device_number: int) -> dict[str, Any]:
    return {
        "device_number": device_number,
        "revision": 0,
        "enabled": True,
        "armed": True,
        "tx_enabled": True,
        "mode": "normal",
        "apply_on": "next_attempt",
        "vision": {
            "threshold": 200,
            "min_count": 1,
        },
        "stroke": {
            "gap_timeout_ms": 1000,
            "max_jump": 120,
            "smoothing_alpha": 0.35,
        },
        "commands": {
            "clear_sketch_token": 0,
            "recalibrate_token": 0,
        },
        "updated_at_ms": 0,
    }


def _default_ack(device_number: int) -> dict[str, Any]:
    return {
        "device_number": device_number,
        "applied_revision": 0,
        "active_stroke": False,
        "tx_active": False,
        "mode": "unknown",
        "pending_revision": None,
        "last_error": None,
        "command_tokens": {
            "clear_sketch_token": 0,
            "recalibrate_token": 0,
        },
        "last_seen_ms": 0,
    }


class NodeControlStore:
    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.RLock()
        self.nodes: dict[int, dict[str, Any]] = {}
        self.acks: dict[int, dict[str, Any]] = {}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return

        try:
            payload = json.loads(self.path.read_text())
        except Exception:
            return

        for key, value in payload.get("nodes", {}).items():
            device_number = int(key)
            control = _default_control(device_number)
            self._merge_control(control, value)
            self.nodes[device_number] = control

        for key, value in payload.get("acks", {}).items():
            device_number = int(key)
            ack = _default_ack(device_number)
            self._merge_ack(ack, value)
            self.acks[device_number] = ack

    def _save_locked(self) -> None:
        payload = {
            "nodes": {str(k): v for k, v in sorted(self.nodes.items())},
            "acks": {str(k): v for k, v in sorted(self.acks.items())},
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
        tmp.replace(self.path)

    def _merge_control(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        for key in ("revision", "enabled", "armed", "tx_enabled", "mode", "apply_on", "updated_at_ms"):
            if key in source:
                target[key] = source[key]

        if isinstance(source.get("vision"), dict):
            target["vision"].update(source["vision"])
        if isinstance(source.get("stroke"), dict):
            target["stroke"].update(source["stroke"])
        if isinstance(source.get("commands"), dict):
            target["commands"].update(source["commands"])

    def _merge_ack(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        for key in ("applied_revision", "active_stroke", "tx_active", "mode", "pending_revision", "last_error", "last_seen_ms"):
            if key in source:
                target[key] = source[key]
        if isinstance(source.get("command_tokens"), dict):
            target["command_tokens"].update(source["command_tokens"])

    def _control_locked(self, device_number: int) -> dict[str, Any]:
        control = self.nodes.get(device_number)
        if control is None:
            control = _default_control(device_number)
            self.nodes[device_number] = control
        return control

    def _ack_locked(self, device_number: int) -> dict[str, Any]:
        ack = self.acks.get(device_number)
        if ack is None:
            ack = _default_ack(device_number)
            self.acks[device_number] = ack
        return ack

    def get_control(self, device_number: int) -> dict[str, Any]:
        with self.lock:
            return copy.deepcopy(self._control_locked(device_number))

    def get_node_payload(self, device_number: int) -> dict[str, Any]:
        with self.lock:
            return {
                "control": copy.deepcopy(self._control_locked(device_number)),
                "ack": copy.deepcopy(self._ack_locked(device_number)),
            }

    def list_nodes(self) -> list[dict[str, Any]]:
        with self.lock:
            device_numbers = sorted(set(self.nodes) | set(self.acks))
            return [
                {
                    "control": copy.deepcopy(self._control_locked(device_number)),
                    "ack": copy.deepcopy(self._ack_locked(device_number)),
                }
                for device_number in device_numbers
            ]

    def update_control(self, device_number: int, payload: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            current = copy.deepcopy(self._control_locked(device_number))
            updated = copy.deepcopy(current)

            if "enabled" in payload:
                updated["enabled"] = bool(payload["enabled"])
            if "armed" in payload:
                updated["armed"] = bool(payload["armed"])
            if "tx_enabled" in payload:
                updated["tx_enabled"] = bool(payload["tx_enabled"])
            if "mode" in payload:
                mode = str(payload["mode"])
                if mode not in ALLOWED_MODES:
                    raise ValueError(f"unsupported mode: {mode}")
                updated["mode"] = mode
            if "apply_on" in payload:
                apply_on = str(payload["apply_on"])
                if apply_on not in ALLOWED_APPLY_ON:
                    raise ValueError(f"unsupported apply_on: {apply_on}")
                updated["apply_on"] = apply_on

            if "vision" in payload:
                vision = payload["vision"]
                if not isinstance(vision, dict):
                    raise ValueError("vision must be an object")
                if "threshold" in vision:
                    updated["vision"]["threshold"] = max(0, min(255, int(vision["threshold"])))
                if "min_count" in vision:
                    updated["vision"]["min_count"] = max(1, int(vision["min_count"]))

            if "stroke" in payload:
                stroke = payload["stroke"]
                if not isinstance(stroke, dict):
                    raise ValueError("stroke must be an object")
                if "gap_timeout_ms" in stroke:
                    updated["stroke"]["gap_timeout_ms"] = max(100, int(stroke["gap_timeout_ms"]))
                if "max_jump" in stroke:
                    updated["stroke"]["max_jump"] = max(1, int(stroke["max_jump"]))
                if "smoothing_alpha" in stroke:
                    alpha = float(stroke["smoothing_alpha"])
                    updated["stroke"]["smoothing_alpha"] = max(0.0, min(1.0, alpha))

            if "commands" in payload:
                commands = payload["commands"]
                if not isinstance(commands, dict):
                    raise ValueError("commands must be an object")
                if commands.get("clear_sketch") is True:
                    updated["commands"]["clear_sketch_token"] += 1
                if commands.get("recalibrate") is True:
                    updated["commands"]["recalibrate_token"] += 1
                if "clear_sketch_token" in commands:
                    updated["commands"]["clear_sketch_token"] = max(
                        updated["commands"]["clear_sketch_token"],
                        int(commands["clear_sketch_token"]),
                    )
                if "recalibrate_token" in commands:
                    updated["commands"]["recalibrate_token"] = max(
                        updated["commands"]["recalibrate_token"],
                        int(commands["recalibrate_token"]),
                    )

            changed = updated != current
            if changed:
                updated["revision"] = current["revision"] + 1
                updated["updated_at_ms"] = _now_ms()
                self.nodes[device_number] = updated
                self._save_locked()
                return copy.deepcopy(updated)

            return copy.deepcopy(current)

    def update_ack(self, device_number: int, payload: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            ack = copy.deepcopy(self._ack_locked(device_number))

            if "applied_revision" in payload:
                ack["applied_revision"] = max(0, int(payload["applied_revision"]))
            if "active_stroke" in payload:
                ack["active_stroke"] = bool(payload["active_stroke"])
            if "tx_active" in payload:
                ack["tx_active"] = bool(payload["tx_active"])
            if "mode" in payload:
                ack["mode"] = str(payload["mode"])
            if "pending_revision" in payload:
                pending = payload["pending_revision"]
                ack["pending_revision"] = None if pending is None else max(0, int(pending))
            if "last_error" in payload:
                last_error = payload["last_error"]
                ack["last_error"] = None if last_error in (None, "") else str(last_error)
            if "command_tokens" in payload:
                tokens = payload["command_tokens"]
                if not isinstance(tokens, dict):
                    raise ValueError("command_tokens must be an object")
                if "clear_sketch_token" in tokens:
                    ack["command_tokens"]["clear_sketch_token"] = max(0, int(tokens["clear_sketch_token"]))
                if "recalibrate_token" in tokens:
                    ack["command_tokens"]["recalibrate_token"] = max(0, int(tokens["recalibrate_token"]))

            ack["last_seen_ms"] = _now_ms()
            self.acks[device_number] = ack
            self._save_locked()
            return copy.deepcopy(ack)
