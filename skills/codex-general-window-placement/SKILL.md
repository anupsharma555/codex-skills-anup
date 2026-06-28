---
name: codex-general-window-placement
description: Open, place, inspect, or verify visible macOS app and browser windows across the laptop display and external monitors. Use when Codex is asked to arrange desktop windows, avoid covering existing windows, place an app/browser on laptop/external-monitor-1/external-monitor-2, use Magnet-like regions such as left/right/top-left/center/maximize, or confirm placement with screenshots. Do not use for in-page browser content validation alone; use Playwright for page content and this skill for visible desktop window placement.
---

# Codex General Window Placement

Use this skill to make visible macOS desktop window placement deterministic. Prefer the bundled helper over Magnet hotkeys so Codex can inspect displays, choose a region, move a window by bounds, and verify with screenshot evidence.

## Quick Start

From the skill directory:

```sh
python3 scripts/window_placement.py check
python3 scripts/window_placement.py screens
python3 scripts/window_placement.py inventory
python3 scripts/window_placement.py open-place --app TextEdit --display laptop --region left --verify
python3 scripts/window_placement.py place --app "Google Chrome" --display external-monitor-1 --region left --verify
```

Use `--json` for machine-readable output.

## Workflow

1. Run `check` before first use in a session. If Accessibility, Automation, Screen Recording, display discovery, or window inventory fails, report the exact failing capability and stop before moving windows.
2. If the user names a display and region, use them exactly.
3. If either display or region is missing, run `inventory` and let the helper choose the least disruptive available region. Do not move unrelated existing windows.
4. If the target app is open in another macOS Space, do not assume it is placeable from the current desktop. Use `place --app "<App>" --activate ...` only when intentionally bringing that app/Space forward is acceptable.
5. For browsers, separate tab/page work from visible window placement:
   - use browser/Playwright tools for tabs, navigation, forms, and page screenshots
   - use this helper for the actual Chrome/Safari/Codex app window bounds on the desktop
6. Use `--verify` when placement matters. Verification should inspect the actual app-window dimensions first; screenshots are supporting evidence, not the primary pass/fail signal.

## Display And Region Names

Displays:

- `laptop`: the macOS main display, usually the laptop screen
- `external-monitor-1`: the primary horizontal external monitor when present
- `external-monitor-2`: the primary vertical external monitor when present

Legacy aliases `main`, `monitor-1`, and `monitor-2` are accepted for compatibility, but prefer the names above in new commands and answers.

The helper computes each region from the selected display's actual detected bounds. Do not assume laptop, horizontal monitor, and vertical monitor dimensions match.
For actual placement, the helper uses a usable window area rather than raw display pixels so normal app windows do not land partly behind the menu bar or a macOS-reserved desktop edge.
Monitor geometry is dynamic. Do not hard-code coordinates from one setup; rerun `screens` before placement when monitors may have changed, been unplugged, rotated, rearranged, or replaced.

Regions:

- `left`: exact left half of the selected display's usable window area, matching Magnet-style left placement
- `right`: exact right half of the selected display's usable window area, matching Magnet-style right placement
- `top-left`
- `top-right`
- `bottom-left`
- `bottom-right`
- `center`
- `maximize`

## Helper Commands

- `check`: report readiness for Swift/CoreGraphics display discovery, Accessibility/System Events window control, Screen Recording/screenshot capture, and required commands.
- `screens`: list display labels and bounds.
- `inventory`: list visible app windows and current bounds.
- `place`: move a named app or the frontmost app to a display/region.
- `place --verify`: require Magnet-style bounds for the requested region. If the app clamps its own minimum size, report `appSizeClamped: true` and fail verification.
- `place --allow-clamped --verify`: accept an app-constrained fallback only when the user explicitly wants edge alignment despite non-Magnet dimensions.
- `place --activate`: activate the target app first, which may switch macOS Spaces, then place the visible window.
- `open-place`: open an app, wait for a visible window, then place it.
- `verify`: inspect current bounds and capture screenshot evidence without moving the window.
- `test`: run the helper unit tests.

## Verification Rules

- Prefer OS-level screenshot proof for desktop placement. The helper uses `screencapture`; the separate screenshot skill remains the broader fallback for app/window screenshot needs.
- Use Playwright screenshots only to confirm browser page content after the desktop browser window is already placed.
- A verification report must include the target app/window, requested display/region, expected bounds, actual bounds, `magnetSpecMatched`, `appSizeClamped`, screenshot path when captured, and final pass/fail status.
- Default verification should fail when an app is only edge-aligned but does not match the Magnet-style target dimensions. Do not call this true `left` or `right`; call it an app-clamped fallback.
- If Screen Recording or Accessibility permission is missing, fail closed with the exact permission gap rather than guessing from stale state.
- If the helper reports `System Events automation is unavailable` or `CoreGraphics returned no active displays`, treat the current Codex process as lacking visible desktop access. Retry from a GUI-capable terminal/session or with the required macOS privacy permissions before attempting placement.

## Safety Rules

- Never rearrange other windows unless the user explicitly asks.
- Treat macOS Spaces as a visibility boundary. A background Space on the right side of Mission Control is not equivalent to a visible window on the laptop or attached monitor.
- Do not activate or switch Spaces implicitly. Use `--activate` only when the user request or workflow clearly permits bringing that app forward.
- Prefer direct placement in the current visible Space. Avoid activation when the user wants the target monitor to stay in the foreground and not slide to another Space.
- Treat missing monitors as a clean failure: if `external-monitor-2` is requested but absent, report it and stop.
- Treat monitor labels as live labels derived from current geometry: `external-monitor-1` is the current primary horizontal external monitor, not a permanent hardware identity.
- Keep Magnet as a manual fallback only. Do not simulate Magnet hotkeys unless the user explicitly requests that method.
- Store verification screenshots in the temp directory by default unless the user provides an output path.
