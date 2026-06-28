#!/usr/bin/env python3
"""macOS app and browser window placement helper for Codex."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
DISPLAY_SWIFT = SCRIPT_DIR / "macos_display_info.swift"
SCREEN_PERMISSION_SWIFT = SCRIPT_DIR / "macos_screen_permission.swift"
MODULE_CACHE = Path(tempfile.gettempdir()) / "codex-swift-module-cache"
REGIONS = {
    "left",
    "right",
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
    "center",
    "maximize",
}
DEFAULT_MENU_BAR_MARGIN = 25
MAGNET_BOUNDS_TOLERANCE = 32
DISPLAY_ALIASES = {
    "main": "laptop",
    "monitor-1": "external-monitor-1",
    "monitor-2": "external-monitor-2",
    "external-monitor 1": "external-monitor-1",
    "external-monitor 2": "external-monitor-2",
}
DISPLAY_CHOICES = [
    "laptop",
    "external-monitor-1",
    "external-monitor-2",
    "main",
    "monitor-1",
    "monitor-2",
]


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @property
    def area(self) -> int:
        return max(0, self.width) * max(0, self.height)

    def intersection_area(self, other: "Rect") -> int:
        left = max(self.x, other.x)
        top = max(self.y, other.y)
        right = min(self.x + self.width, other.x + other.width)
        bottom = min(self.y + self.height, other.y + other.height)
        return max(0, right - left) * max(0, bottom - top)

    def almost_equals(self, other: "Rect", tolerance: int = 24) -> bool:
        return (
            abs(self.x - other.x) <= tolerance
            and abs(self.y - other.y) <= tolerance
            and abs(self.width - other.width) <= tolerance
            and abs(self.height - other.height) <= tolerance
        )

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def center_y(self) -> int:
        return self.y + self.height // 2


@dataclass(frozen=True)
class Display:
    label: str
    id: int
    main: bool
    bounds: Rect
    usable_bounds: Rect | None = None


def display_orientation(bounds: Rect) -> str:
    return "horizontal" if bounds.width >= bounds.height else "vertical"


@dataclass(frozen=True)
class Window:
    app: str
    title: str
    bounds: Rect


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    status = payload.get("status", "ok")
    print(f"status: {status}")
    for key, value in payload.items():
        if key == "status":
            continue
        if isinstance(value, (dict, list)):
            print(f"{key}: {json.dumps(value, sort_keys=True)}")
        else:
            print(f"{key}: {value}")


def run_capture(cmd: list[str], timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)


def swift_json(script: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not shutil.which("swift"):
        return None, "swift not found; install Xcode command line tools"
    MODULE_CACHE.mkdir(parents=True, exist_ok=True)
    proc = run_capture(["swift", "-module-cache-path", str(MODULE_CACHE), str(script)], timeout=30)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return None, detail or f"swift failed with exit code {proc.returncode}"
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"swift returned non-JSON output: {exc}"


def explain_macos_error(error: str | None) -> str | None:
    if not error:
        return None
    if "-10827" in error:
        return (
            "System Events automation is unavailable from this process "
            "(macOS Automation/Accessibility permission or a non-GUI/sandboxed "
            f"session blocked it). Raw error: {error}"
        )
    if "not authorized" in error.lower() or "not allowed" in error.lower():
        return f"macOS privacy permissions blocked this operation. Raw error: {error}"
    return error


def label_displays(raw_displays: list[dict[str, Any]]) -> list[Display]:
    parsed = [
        Display(
            label="",
            id=int(item["id"]),
            main=bool(item.get("main")),
            bounds=Rect(
                int(item["x"]),
                int(item["y"]),
                int(item["width"]),
                int(item["height"]),
            ),
            usable_bounds=Rect(
                int(item.get("usableX", item["x"])),
                int(item.get("usableY", item["y"])),
                int(item.get("usableWidth", item["width"])),
                int(item.get("usableHeight", item["height"])),
            ),
        )
        for item in raw_displays
    ]
    main = [display for display in parsed if display.main]
    externals = sorted([display for display in parsed if not display.main], key=display_sort_key)
    labeled: list[Display] = []
    if main:
        display = main[0]
        labeled.append(Display("laptop", display.id, display.main, display.bounds, display.usable_bounds))
    used_ids = {display.id for display in labeled}
    horizontal = [display for display in externals if display_orientation(display.bounds) == "horizontal"]
    vertical = [display for display in externals if display_orientation(display.bounds) == "vertical"]
    if horizontal:
        display = horizontal[0]
        labeled.append(Display("external-monitor-1", display.id, display.main, display.bounds, display.usable_bounds))
        used_ids.add(display.id)
    if vertical:
        display = vertical[0]
        labeled.append(Display("external-monitor-2", display.id, display.main, display.bounds, display.usable_bounds))
        used_ids.add(display.id)
    for display in externals:
        if display.id in used_ids:
            continue
        next_label = "external-monitor-1" if not any(item.label == "external-monitor-1" for item in labeled) else "external-monitor-2"
        if any(item.label == next_label for item in labeled):
            break
        labeled.append(Display(next_label, display.id, display.main, display.bounds, display.usable_bounds))
        used_ids.add(display.id)
    if not labeled and parsed:
        display = sorted(parsed, key=display_sort_key)[0]
        labeled.append(Display("laptop", display.id, True, display.bounds, display.usable_bounds))
    return labeled


def display_sort_key(display: Display) -> tuple[int, int, int]:
    return (-display.bounds.area, display.bounds.x, display.bounds.y)


def get_displays() -> tuple[list[Display], str | None]:
    payload, error = swift_json(DISPLAY_SWIFT)
    if error:
        return [], error
    if not payload or not payload.get("ok"):
        return [], str((payload or {}).get("error") or "display discovery failed")
    displays = label_displays(payload.get("displays", []))
    if not displays:
        return [], (
            "CoreGraphics returned no active displays; this process may not have "
            "access to the visible GUI display session."
        )
    return displays, None


def find_display(displays: list[Display], label: str) -> Display:
    canonical_label = DISPLAY_ALIASES.get(label, label)
    for display in displays:
        if display.label == canonical_label:
            return display
    available = ", ".join(display.label for display in displays) or "none"
    raise SystemExit(f"display '{label}' is not available; detected: {available}")


def region_bounds(display: Rect, region: str) -> Rect:
    if region not in REGIONS:
        raise ValueError(f"unknown region: {region}")
    half_w = display.width // 2
    half_h = display.height // 2
    if region == "maximize":
        return display
    if region == "left":
        return Rect(display.x, display.y, half_w, display.height)
    if region == "right":
        return Rect(display.x + half_w, display.y, display.width - half_w, display.height)
    if region == "top-left":
        return Rect(display.x, display.y, half_w, half_h)
    if region == "top-right":
        return Rect(display.x + half_w, display.y, display.width - half_w, half_h)
    if region == "bottom-left":
        return Rect(display.x, display.y + half_h, half_w, display.height - half_h)
    if region == "bottom-right":
        return Rect(display.x + half_w, display.y + half_h, display.width - half_w, display.height - half_h)
    if region == "center":
        width = math.floor(display.width * 0.72)
        height = math.floor(display.height * 0.78)
        return Rect(display.x + (display.width - width) // 2, display.y + (display.height - height) // 2, width, height)
    raise AssertionError(region)


def usable_window_area(display: Rect) -> Rect:
    if display.height <= DEFAULT_MENU_BAR_MARGIN * 2:
        return display
    return Rect(
        display.x,
        display.y + DEFAULT_MENU_BAR_MARGIN,
        display.width,
        display.height - DEFAULT_MENU_BAR_MARGIN,
    )


def target_region_bounds(display: Rect, region: str) -> Rect:
    return region_bounds(usable_window_area(display), region)


def display_target_region_bounds(display: Display, region: str) -> Rect:
    # System Events window coordinates do not consistently match AppKit's
    # visibleFrame y-origin across external displays. Use raw display origin
    # plus a menu-bar-safe top inset, which matches observed Magnet-style
    # left/right placement in System Events coordinates.
    return region_bounds(usable_window_area(display.bounds), region)


def choose_region(display: Display, windows: list[Window]) -> tuple[str, Rect, int]:
    candidates = ["left", "right", "top-left", "top-right", "bottom-left", "bottom-right", "center"]
    best: tuple[str, Rect, int] | None = None
    for region in candidates:
        rect = display_target_region_bounds(display, region)
        overlap = sum(rect.intersection_area(window.bounds) for window in windows)
        if best is None or overlap < best[2] or (overlap == best[2] and rect.area > best[1].area):
            best = (region, rect, overlap)
    assert best is not None
    return best


def applescript_literal(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def run_osascript(script: str) -> tuple[str, str | None]:
    if not shutil.which("osascript"):
        return "", "osascript not found"
    try:
        proc = run_capture(["osascript", "-e", script], timeout=20)
    except subprocess.TimeoutExpired:
        return "", "osascript timed out after 20 seconds while querying System Events"
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return "", detail or f"osascript failed with exit code {proc.returncode}"
    return proc.stdout.strip(), None


def accessibility_status() -> tuple[bool, str | None]:
    output, error = run_osascript('tell application "System Events" to get UI elements enabled')
    if error:
        return False, explain_macos_error(error)
    return output.strip().lower() == "true", None if output.strip().lower() == "true" else "Accessibility UI scripting is disabled"


def screen_recording_message(granted: bool) -> str | None:
    return None if granted else "Screen Recording permission is not granted for this process."


def screen_recording_status() -> tuple[bool, str | None]:
    payload, error = swift_json(SCREEN_PERMISSION_SWIFT)
    if error:
        return False, error
    if not payload or not payload.get("ok"):
        return False, str((payload or {}).get("error") or "screen recording check failed")
    granted = bool(payload.get("screenRecording"))
    return granted, screen_recording_message(granted)


def parse_bounds_csv(line: str) -> Rect | None:
    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 4:
        return None
    try:
        x, y, w, h = (int(float(part)) for part in parts[:4])
    except ValueError:
        return None
    return Rect(x, y, w, h)


def list_windows(app: str | None = None) -> tuple[list[Window], str | None]:
    app_filter = app or ""
    script = f'''
set appFilter to {applescript_literal(app_filter)}
set outputLines to {{}}
tell application "System Events"
  if appFilter is "" then
    set targetProcesses to processes whose visible is true
  else
    set targetProcesses to processes whose name contains appFilter
  end if
  repeat with proc in targetProcesses
    set procName to name of proc as text
    repeat with win in windows of proc
      try
        set posn to position of win
        set siz to size of win
        set titleText to name of win as text
        set end of outputLines to procName & tab & titleText & tab & ((item 1 of posn) as text) & "," & ((item 2 of posn) as text) & "," & ((item 1 of siz) as text) & "," & ((item 2 of siz) as text)
      end try
    end repeat
  end repeat
end tell
set AppleScript's text item delimiters to linefeed
return outputLines as text
'''
    output, error = run_osascript(script)
    if error:
        return [], explain_macos_error(error)
    windows: list[Window] = []
    for line in output.splitlines():
        columns = line.split("\t")
        if len(columns) < 3:
            continue
        bounds = parse_bounds_csv(columns[2])
        if bounds and bounds.width > 40 and bounds.height > 40:
            windows.append(Window(columns[0], columns[1], bounds))
    return windows, None


def frontmost_app() -> tuple[str | None, str | None]:
    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
    output, error = run_osascript(script)
    if error:
        return None, explain_macos_error(error)
    return output.strip() or None, None


def select_target_app(app: str | None) -> str:
    if app:
        return app
    front, error = frontmost_app()
    if error or not front:
        raise SystemExit(f"could not determine frontmost app: {error or 'none'}")
    return front


def move_window(app: str, rect: Rect) -> str | None:
    script = f'''
tell application "System Events"
  set targetProc to first process whose name contains {applescript_literal(app)}
  set targetWindow to first window of targetProc
  set size of targetWindow to {{{rect.width}, {rect.height}}}
  delay 0.05
  set position of targetWindow to {{{rect.x}, {rect.y}}}
end tell
'''
    _, error = run_osascript(script)
    return explain_macos_error(error)


def open_app(app: str) -> str | None:
    proc = run_capture(["open", "-a", app], timeout=20)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return detail or f"open failed with exit code {proc.returncode}"
    return None


def activate_app(app: str) -> str | None:
    script = f'tell application {applescript_literal(app)} to activate'
    _, error = run_osascript(script)
    return explain_macos_error(error)


def wait_for_window(app: str, timeout: float = 12.0) -> str | None:
    deadline = time.time() + timeout
    last_error: str | None = None
    while time.time() < deadline:
        windows, error = list_windows(app)
        if error:
            last_error = error
        elif windows:
            return None
        time.sleep(0.5)
    return last_error or f"no visible window found for {app}"


def screenshot_path(app: str, output_dir: str | None = None) -> tuple[str | None, str | None]:
    if not shutil.which("screencapture"):
        return None, "screencapture not found"
    base = Path(output_dir).expanduser() if output_dir else Path(tempfile.gettempdir())
    base.mkdir(parents=True, exist_ok=True)
    safe_app = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in app).strip("-") or "window"
    path = base / f"codex-window-placement-{safe_app}-{int(time.time())}.png"
    proc = run_capture(["screencapture", "-x", str(path)], timeout=20)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return None, detail or f"screencapture failed with exit code {proc.returncode}"
    if not path.exists() or path.stat().st_size == 0:
        return None, "screenshot file was not created"
    return str(path), None


def actual_window_for_app(app: str) -> tuple[Window | None, str | None]:
    windows, error = list_windows(app)
    if error:
        return None, error
    if not windows:
        return None, f"no visible window found for {app}"
    return windows[0], None


def command_check(args: argparse.Namespace) -> dict[str, Any]:
    accessibility_ok, accessibility_error = accessibility_status()
    screen_ok, screen_error = screen_recording_status()
    displays, display_error = get_displays()
    windows, window_error = list_windows() if accessibility_ok else ([], accessibility_error)
    checks = {
        "platform": sys.platform,
        "commands": {
            "osascript": bool(shutil.which("osascript")),
            "open": bool(shutil.which("open")),
            "screencapture": bool(shutil.which("screencapture")),
            "swift": bool(shutil.which("swift")),
        },
        "automation": {
            "ok": accessibility_ok,
            "error": accessibility_error,
            "note": "System Events automation is required to inspect and move windows.",
        },
        "accessibility": {"ok": accessibility_ok, "error": accessibility_error},
        "screenRecording": {"ok": screen_ok, "error": screen_error},
        "displayDiscovery": {"ok": not display_error, "error": display_error, "count": len(displays)},
        "windowInventory": {"ok": not window_error, "error": window_error, "count": len(windows)},
    }
    ready = all(checks["commands"].values()) and accessibility_ok and screen_ok and not display_error and not window_error
    return {"status": "ready" if ready else "blocked", "ready": ready, "checks": checks}


def command_screens(args: argparse.Namespace) -> dict[str, Any]:
    displays, error = get_displays()
    if error:
        return {"status": "blocked", "error": error, "displays": []}
    return {"status": "ok", "displays": [asdict(display) for display in displays]}


def command_inventory(args: argparse.Namespace) -> dict[str, Any]:
    windows, error = list_windows(args.app)
    if error:
        return {"status": "blocked", "error": error, "windows": []}
    return {"status": "ok", "windows": [asdict(window) for window in windows]}


def resolve_target(args: argparse.Namespace, target_app: str) -> tuple[Display, str, Rect, int | None]:
    displays, display_error = get_displays()
    if display_error:
        raise SystemExit(display_error)
    display = find_display(displays, args.display or "laptop")
    if args.region:
        return display, args.region, display_target_region_bounds(display, args.region), None
    windows, error = list_windows()
    if error:
        raise SystemExit(error)
    other_windows = [window for window in windows if target_app not in window.app]
    chosen_region, rect, overlap = choose_region(display, other_windows)
    return display, chosen_region, rect, overlap


def verification_payload(
    app: str,
    display: str | None,
    region: str | None,
    expected: Rect | None,
    output_dir: str | None,
    allow_clamped: bool = False,
) -> dict[str, Any]:
    actual, actual_error = actual_window_for_app(app)
    shot, shot_error = screenshot_path(app, output_dir)
    magnet_spec_matched = bool(
        expected and actual and actual.bounds.almost_equals(expected, tolerance=MAGNET_BOUNDS_TOLERANCE)
    )
    edge_region_matched = bool(expected and actual and placement_matches(expected, actual.bounds, region))
    app_size_clamped = bool(edge_region_matched and not magnet_spec_matched)
    passed = bool(magnet_spec_matched or (allow_clamped and edge_region_matched))
    return {
        "status": "ok" if passed else "blocked",
        "passed": passed,
        "dimensionVerified": magnet_spec_matched,
        "magnetSpecMatched": magnet_spec_matched,
        "edgeRegionMatched": edge_region_matched,
        "appSizeClamped": app_size_clamped,
        "acceptedClamped": bool(allow_clamped and app_size_clamped),
        "app": app,
        "display": display,
        "region": region,
        "expectedBounds": asdict(expected) if expected else None,
        "actualBounds": asdict(actual.bounds) if actual else None,
        "screenshot": shot,
        "screenshotRequired": False,
        "errors": [item for item in [actual_error, shot_error] if item],
    }


def placement_matches(expected: Rect, actual: Rect, region: str | None, tolerance: int = 96) -> bool:
    if actual.almost_equals(expected, tolerance=tolerance):
        return True
    width_reasonable = actual.width >= expected.width * 0.5 and actual.width <= expected.width * 1.5
    height_reasonable = actual.height >= expected.height * 0.5 and actual.height <= expected.height * 1.5
    if not width_reasonable or not height_reasonable:
        return False
    if region == "left":
        return abs(actual.x - expected.x) <= tolerance and actual.center_x <= expected.right + tolerance
    if region == "right":
        return abs(actual.right - expected.right) <= tolerance or actual.x >= expected.x - tolerance
    if region == "top-left":
        return abs(actual.x - expected.x) <= tolerance and abs(actual.y - expected.y) <= tolerance
    if region == "top-right":
        return abs(actual.right - expected.right) <= tolerance and abs(actual.y - expected.y) <= tolerance
    if region == "bottom-left":
        return abs(actual.x - expected.x) <= tolerance and abs(actual.bottom - expected.bottom) <= tolerance
    if region == "bottom-right":
        return abs(actual.right - expected.right) <= tolerance and abs(actual.bottom - expected.bottom) <= tolerance
    if region == "center":
        return abs(actual.center_x - expected.center_x) <= tolerance and abs(actual.center_y - expected.center_y) <= tolerance
    if region == "maximize":
        return (
            abs(actual.x - expected.x) <= tolerance
            and abs(actual.y - expected.y) <= tolerance
            and actual.width >= expected.width * 0.75
            and actual.height >= expected.height * 0.75
        )
    return actual.almost_equals(expected, tolerance=tolerance)


def command_verify(args: argparse.Namespace) -> dict[str, Any]:
    app = select_target_app(args.app)
    expected = None
    if args.display and args.region:
        displays, display_error = get_displays()
        if display_error:
            return {"status": "blocked", "error": display_error}
        expected = display_target_region_bounds(find_display(displays, args.display), args.region)
    return verification_payload(app, args.display, args.region, expected, args.output_dir, args.allow_clamped)


def command_place(args: argparse.Namespace) -> dict[str, Any]:
    app = select_target_app(args.app)
    if args.activate:
        activate_error = activate_app(app)
        if activate_error:
            return {"status": "blocked", "app": app, "error": activate_error}
        wait_error = wait_for_window(app, timeout=args.timeout)
        if wait_error:
            return {"status": "blocked", "app": app, "error": wait_error}
    elif args.app:
        current_window, current_error = actual_window_for_app(app)
        if current_error or not current_window:
            return {
                "status": "blocked",
                "app": app,
                "error": current_error or "target app has no visible window in the current macOS Space",
                "hint": (
                    "If the app is open in another macOS Space, rerun with --activate "
                    "to intentionally switch to that app/window before placement."
                ),
            }
    display, region, rect, overlap = resolve_target(args, app)
    error = move_window(app, rect)
    if error:
        return {"status": "blocked", "app": app, "error": error}
    payload: dict[str, Any] = {
        "status": "ok",
        "app": app,
        "display": display.label,
        "region": region,
        "expectedBounds": asdict(rect),
    }
    if overlap is not None:
        payload["overlapScore"] = overlap
    if args.verify:
        payload["verification"] = verification_payload(
            app, display.label, region, rect, args.output_dir, args.allow_clamped
        )
        if payload["verification"]["status"] != "ok":
            payload["status"] = "blocked"
    return payload


def command_open_place(args: argparse.Namespace) -> dict[str, Any]:
    if not args.app:
        raise SystemExit("open-place requires --app")
    open_error = open_app(args.app)
    if open_error:
        return {"status": "blocked", "app": args.app, "error": open_error}
    wait_error = wait_for_window(args.app, timeout=args.timeout)
    if wait_error:
        return {"status": "blocked", "app": args.app, "error": wait_error}
    return command_place(args)


class GeometryTests(unittest.TestCase):
    def test_region_bounds(self) -> None:
        display = Rect(0, 0, 1440, 900)
        self.assertEqual(region_bounds(display, "left"), Rect(0, 0, 720, 900))
        self.assertEqual(region_bounds(display, "right"), Rect(720, 0, 720, 900))
        self.assertEqual(region_bounds(display, "bottom-right"), Rect(720, 450, 720, 450))

    def test_region_bounds_use_display_specific_size(self) -> None:
        horizontal = Rect(1440, 0, 2560, 1440)
        vertical = Rect(4000, 0, 1080, 1920)
        self.assertEqual(region_bounds(horizontal, "left"), Rect(1440, 0, 1280, 1440))
        self.assertEqual(region_bounds(vertical, "right"), Rect(4540, 0, 540, 1920))

    def test_target_region_uses_usable_window_area(self) -> None:
        monitor = Rect(1800, 0, 1920, 1080)
        self.assertEqual(target_region_bounds(monitor, "left"), Rect(1800, 25, 960, 1055))
        self.assertEqual(usable_window_area(monitor), Rect(1800, 25, 1920, 1055))

    def test_display_target_region_prefers_detected_usable_bounds(self) -> None:
        display = Display("external-monitor-1", 2, False, Rect(1800, 0, 1920, 1080), Rect(1800, 89, 1920, 1080))
        self.assertEqual(display_target_region_bounds(display, "left"), Rect(1800, 25, 960, 1055))

    def test_left_region_match_allows_app_size_clamping(self) -> None:
        expected = Rect(1800, 89, 960, 1080)
        actual = Rect(1800, 115, 1020, 922)
        self.assertTrue(placement_matches(expected, actual, "left"))
        self.assertFalse(actual.almost_equals(expected, tolerance=MAGNET_BOUNDS_TOLERANCE))

    def test_intersection(self) -> None:
        self.assertEqual(Rect(0, 0, 100, 100).intersection_area(Rect(50, 50, 100, 100)), 2500)
        self.assertEqual(Rect(0, 0, 100, 100).intersection_area(Rect(101, 101, 10, 10)), 0)

    def test_display_labels(self) -> None:
        displays = label_displays([
            {"id": 2, "main": False, "x": 1440, "y": 0, "width": 1920, "height": 1080},
            {"id": 1, "main": True, "x": 0, "y": 0, "width": 1440, "height": 900},
            {"id": 3, "main": False, "x": -1080, "y": 0, "width": 1080, "height": 1920},
        ])
        self.assertEqual([display.label for display in displays], ["laptop", "external-monitor-1", "external-monitor-2"])
        self.assertEqual(displays[1].id, 2)
        self.assertEqual(displays[2].id, 3)

    def test_vertical_only_external_keeps_monitor_2_label(self) -> None:
        displays = label_displays([
            {"id": 1, "main": True, "x": 0, "y": 0, "width": 1440, "height": 900},
            {"id": 3, "main": False, "x": 1440, "y": 0, "width": 1080, "height": 1920},
        ])
        self.assertEqual([display.label for display in displays], ["laptop", "external-monitor-2"])

    def test_legacy_display_aliases(self) -> None:
        displays = [
            Display("laptop", 1, True, Rect(0, 0, 1440, 900)),
            Display("external-monitor-1", 2, False, Rect(1440, 0, 1920, 1080)),
        ]
        self.assertEqual(find_display(displays, "main").label, "laptop")
        self.assertEqual(find_display(displays, "monitor-1").label, "external-monitor-1")

    def test_choose_region_least_overlap(self) -> None:
        display = Display("laptop", 1, True, Rect(0, 0, 1000, 800))
        windows = [Window("A", "", Rect(0, 0, 500, 800))]
        region, _, overlap = choose_region(display, windows)
        self.assertIn(region, {"right", "top-right", "bottom-right"})
        self.assertEqual(overlap, 0)

    def test_explain_macos_error(self) -> None:
        message = explain_macos_error("execution error: An error of type -10827 has occurred. (-10827)")
        self.assertIsNotNone(message)
        self.assertIn("System Events automation is unavailable", message or "")

    def test_screen_recording_false_has_reason(self) -> None:
        self.assertEqual(
            screen_recording_message(False),
            "Screen Recording permission is not granted for this process.",
        )
        self.assertIsNone(screen_recording_message(True))

    def test_activate_app_script_quoting(self) -> None:
        self.assertEqual(applescript_literal('Google "Chrome"'), '"Google \\"Chrome\\""')


def command_test(args: argparse.Namespace) -> dict[str, Any]:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GeometryTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return {"status": "ok" if result.wasSuccessful() else "blocked", "testsRun": result.testsRun, "failures": len(result.failures), "errors": len(result.errors)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check")

    subparsers.add_parser("screens")

    inventory = subparsers.add_parser("inventory")
    inventory.add_argument("--app", help="optional app-name substring")

    verify = subparsers.add_parser("verify")
    verify.add_argument("--app", help="target app-name substring; defaults to frontmost app")
    verify.add_argument("--display", choices=DISPLAY_CHOICES)
    verify.add_argument("--region", choices=sorted(REGIONS))
    verify.add_argument("--output-dir", help="directory for screenshot evidence")
    verify.add_argument("--allow-clamped", action="store_true", help="accept edge-aligned app-clamped bounds as a non-Magnet fallback")

    place = subparsers.add_parser("place")
    place.add_argument("--app", help="target app-name substring; defaults to frontmost app")
    place.add_argument("--display", choices=DISPLAY_CHOICES)
    place.add_argument("--region", choices=sorted(REGIONS))
    place.add_argument("--verify", action="store_true", help="capture screenshot and compare bounds after moving")
    place.add_argument("--output-dir", help="directory for screenshot evidence")
    place.add_argument("--allow-clamped", action="store_true", help="accept edge-aligned app-clamped bounds as a non-Magnet fallback")
    place.add_argument("--activate", action="store_true", help="activate the target app first; may switch macOS Spaces")
    place.add_argument("--timeout", type=float, default=12.0, help="seconds to wait for a visible window after --activate")

    open_place = subparsers.add_parser("open-place")
    open_place.add_argument("--app", required=True, help="application name to open")
    open_place.add_argument("--display", choices=DISPLAY_CHOICES)
    open_place.add_argument("--region", choices=sorted(REGIONS))
    open_place.add_argument("--verify", action="store_true", help="capture screenshot and compare bounds after moving")
    open_place.add_argument("--output-dir", help="directory for screenshot evidence")
    open_place.add_argument("--allow-clamped", action="store_true", help="accept edge-aligned app-clamped bounds as a non-Magnet fallback")
    open_place.add_argument("--timeout", type=float, default=12.0, help="seconds to wait for a visible window")

    subparsers.add_parser("test")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "check": command_check,
        "screens": command_screens,
        "inventory": command_inventory,
        "verify": command_verify,
        "place": command_place,
        "open-place": command_open_place,
        "test": command_test,
    }
    payload = handlers[args.command](args)
    emit(payload, args.json)
    return 0 if payload.get("status") == "ok" or payload.get("ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
