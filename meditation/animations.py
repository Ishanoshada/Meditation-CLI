"""
Terminal animations.

Everything here is pure Python + `rich` (no native/GPU deps), so it
runs the same on Windows, Linux, macOS, Termux, and iOS terminal apps.

The centerpiece is `spin_wireframe()` - a genuine 3D wireframe object
(cube or octahedron) rotated with real rotation matrices and projected
to 2D each frame, rendered as colored terminal glyphs. It's not a
canned gif; the geometry is computed live every frame.
"""

from __future__ import annotations
import math
import time
from typing import List, Tuple

from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

# --------------------------------------------------------------------------
# A single, deliberate 4-color theme (not random per-letter noise).
# Inspired by monastic robes and calm water/sky - saffron, deep maroon,
# teal, and soft lavender. Every colored element in the app draws from
# exactly this palette, so nothing looks arbitrary.
# --------------------------------------------------------------------------
SAFFRON = "#f4a259"
MAROON = "#a13d63"
TEAL = "#2ec4b6"
LAVENDER = "#9d8df1"

THEME = [SAFFRON, MAROON, TEAL, LAVENDER]

# The banner title still gets a smooth gradient, but it now blends
# *through* the same four theme colors instead of a separate palette.
GRADIENT = THEME


def gradient_text(s: str) -> Text:
    """Render a string with a smooth left-to-right gradient across THEME."""
    t = Text()
    n = max(len(s) - 1, 1)
    for i, ch in enumerate(s):
        pos = i / n
        idx = pos * (len(GRADIENT) - 1)
        lo = int(idx)
        hi = min(lo + 1, len(GRADIENT) - 1)
        frac = idx - lo
        color = _blend(GRADIENT[lo], GRADIENT[hi], frac)
        t.append(ch, style=color)
    return t


def theme_text(s: str, idx: int, bold: bool = True) -> Text:
    """Render a string in ONE solid color, picked deterministically from
    THEME by `idx` (e.g. menu row number) - not random, not per-letter."""
    style = f"{'bold ' if bold else ''}{THEME[idx % len(THEME)]}"
    return Text(s, style=style)


def _blend(c1: str, c2: str, frac: float) -> str:
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * frac)
    g = int(g1 + (g2 - g1) * frac)
    b = int(b1 + (b2 - b1) * frac)
    return f"#{r:02x}{g:02x}{b:02x}"


# --------------------------------------------------------------------------
# Real 3D wireframe rotation
# --------------------------------------------------------------------------

_CUBE_VERTS: List[Tuple[float, float, float]] = [
    (x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)
]
_CUBE_EDGES = [
    (a, b)
    for a in range(8)
    for b in range(a + 1, 8)
    if sum(x != y for x, y in zip(_CUBE_VERTS[a], _CUBE_VERTS[b])) == 1
]

_OCTA_VERTS: List[Tuple[float, float, float]] = [
    (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)
]
_OCTA_EDGES = [
    (a, b)
    for a in range(6)
    for b in range(a + 1, 6)
    if _OCTA_VERTS[a][0] != -_OCTA_VERTS[b][0]
    or _OCTA_VERTS[a][1] != -_OCTA_VERTS[b][1]
    or _OCTA_VERTS[a][2] != -_OCTA_VERTS[b][2]
]

_SHADES = " .:-=+*#%@"


def _rotate(p, ax, ay):
    x, y, z = p
    # rotate around X
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    # rotate around Y
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    return x, y, z


def _render_frame(verts, edges, ax, ay, width=44, height=20, scale=8.0, dist=4.5):
    buf = [[" "] * width for _ in range(height)]
    depth = [[-1e9] * width for _ in range(height)]
    rotated = [_rotate(v, ax, ay) for v in verts]

    def project(p):
        x, y, z = p
        f = dist / (dist + z)
        px = int(x * f * scale + width / 2)
        py = int(y * f * scale * 0.5 + height / 2)
        return px, py, z

    for a, b in edges:
        x1, y1, z1 = project(rotated[a])
        x2, y2, z2 = project(rotated[b])
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for s in range(steps + 1):
            t = s / steps
            x = round(x1 + (x2 - x1) * t)
            y = round(y1 + (y2 - y1) * t)
            z = z1 + (z2 - z1) * t
            if 0 <= x < width and 0 <= y < height and z > depth[y][x]:
                depth[y][x] = z
                shade_idx = int((1 - (z + 2) / 4) * (len(_SHADES) - 1))
                shade_idx = max(0, min(len(_SHADES) - 1, shade_idx))
                buf[y][x] = _SHADES[shade_idx]

    return "\n".join("".join(row) for row in buf)


def spin_wireframe(seconds: float = 2.4, shape: str = "cube", label: str = ""):
    """Show a live-rotating 3D wireframe for `seconds`."""
    verts, edges = (_CUBE_VERTS, _CUBE_EDGES) if shape == "cube" else (_OCTA_VERTS, _OCTA_EDGES)
    start = time.time()
    with Live(console=console, refresh_per_second=20, transient=True) as live:
        while time.time() - start < seconds:
            t = time.time() - start
            frame = _render_frame(verts, edges, ax=t * 1.1, ay=t * 1.7)
            body = Text(frame, style=f"bold {LAVENDER}")
            panel = Panel(
                Align.center(body),
                title=gradient_text(label) if label else None,
                border_style=MAROON,
                padding=(0, 2),
            )
            live.update(panel)
            time.sleep(0.05)


# --------------------------------------------------------------------------
# Breathing circle
# --------------------------------------------------------------------------

def breathing_cycle(cycles: int = 3, inhale: float = 4.0, hold: float = 4.0, exhale: float = 4.0):
    """Animate a circle through inhale -> hold -> exhale, in sync with breath phases."""
    max_r = 9

    def circle(radius: float) -> str:
        lines = []
        for y in range(-max_r, max_r + 1):
            row = ""
            for x in range(-max_r * 2, max_r * 2 + 1):
                d = math.hypot(x / 2, y)
                row += "*" if d <= radius else " "
            lines.append(row)
        return "\n".join(lines)

    with Live(console=console, refresh_per_second=20, transient=True) as live:
        for cycle_num in range(1, cycles + 1):
            # 1) Inhale - circle grows from 1 to max_r.
            frames = max(int(inhale * 20), 1)
            for i in range(frames):
                radius = 1 + (i / frames) * (max_r - 1)
                art = Text(circle(radius), style=f"bold {TEAL}")
                panel = Panel(
                    Align.center(art),
                    title=gradient_text(f"  Breathe in...  (cycle {cycle_num}/{cycles})  "),
                    border_style=TEAL,
                    padding=(0, 2),
                )
                live.update(panel)
                time.sleep(1 / 20)

            # 2) Hold - stay at full size for `hold` seconds, with a gentle
            #    pulse so it still reads as "alive" rather than frozen.
            frames = max(int(hold * 20), 1)
            for i in range(frames):
                remaining = hold - i / 20
                pulse = max_r - 0.4 * abs(math.sin(i / 6))
                art = Text(circle(pulse), style=f"bold {LAVENDER}")
                panel = Panel(
                    Align.center(art),
                    title=gradient_text(f"  Hold...  {remaining:0.0f}s  (cycle {cycle_num}/{cycles})  "),
                    border_style=LAVENDER,
                    padding=(0, 2),
                )
                live.update(panel)
                time.sleep(1 / 20)

            # 3) Exhale - circle shrinks from max_r back to 1.
            frames = max(int(exhale * 20), 1)
            for i in range(frames):
                radius = max_r - (i / frames) * (max_r - 1)
                art = Text(circle(radius), style=f"bold {SAFFRON}")
                panel = Panel(
                    Align.center(art),
                    title=gradient_text(f"  Breathe out...  (cycle {cycle_num}/{cycles})  "),
                    border_style=SAFFRON,
                    padding=(0, 2),
                )
                live.update(panel)
                time.sleep(1 / 20)


def pulse_spinner(seconds: float, message: str):
    frames = ["◐", "◓", "◑", "◒"]
    start = time.time()
    i = 0
    with Live(console=console, refresh_per_second=10, transient=True) as live:
        while time.time() - start < seconds:
            remaining = max(0, seconds - (time.time() - start))
            txt = Text(f" {frames[i % len(frames)]}  {message}  ({remaining:0.0f}s)", style=f"bold {SAFFRON}")
            live.update(Align.center(txt))
            i += 1
            time.sleep(0.1)


def timer_with_progress(duration_seconds: int, message: str = "Meditating"):
    """A timer with a progress bar and remaining time display."""
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TextColumn("⏱️ {task.fields[remaining]}s"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(
            f"[bold {SAFFRON}]{message}",
            total=duration_seconds,
            remaining=duration_seconds
        )
        
        start_time = time.time()
        while not progress.finished:
            elapsed = time.time() - start_time
            remaining = max(0, duration_seconds - elapsed)
            progress.update(task, completed=elapsed, remaining=remaining)
            time.sleep(0.1)