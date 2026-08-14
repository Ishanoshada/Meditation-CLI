"""
meditation - a colorful, animated, cross-platform terminal companion.

Run with:  meditation
    or:    python -m meditation
"""

from __future__ import annotations
import os
import random
import sys
import time

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich import box

from . import animations as anim
from .links import SITES, open_url
from .quotes import QUOTES
from .history import History

console = Console()

TITLE = "M E D I T A T I O N"

# Global history instance
_history = History()

def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner() -> None:
    clear()
    console.print()
    console.print(Align.center(anim.gradient_text(TITLE)))
    console.print(Align.center(Text("a quiet space in your terminal", style=f"italic {anim.LAVENDER}")))
    # Show session count if available
    sessions = len(_history.sessions)
    if sessions > 0:
        console.print(Align.center(Text(f"🧘 {sessions} sessions recorded", style=f"dim {anim.TEAL}")))
    console.print()


# --------------------------------------------------------------------------
# The footer every command ends with: links to your two sites.
# --------------------------------------------------------------------------

def show_links_menu() -> None:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_row(
        Text("[1]", style=f"bold {anim.SAFFRON}"),
        anim.gradient_text(SITES["1"][0]),
    )
    table.add_row(
        Text("[2]", style=f"bold {anim.SAFFRON}"),
        anim.gradient_text(SITES["2"][0]),
    )
    table.add_row(Text("[Enter]", style=f"bold {anim.TEAL}"), Text("Back to menu", style="dim"))

    console.print()
    console.print(
        Panel(
            table,
            title="[bold]🔗 Explore further[/bold]",
            border_style=f"{anim.MAROON}",
            padding=(1, 2),
        )
    )
    choice = Prompt.ask("Open a link", choices=["1", "2", ""], default="", show_choices=False)
    if choice in SITES:
        name, url = SITES[choice]
        console.print(f"[dim]Opening {name}...[/dim]")
        ok = open_url(url)
        if not ok:
            console.print(f"[yellow]Couldn't launch a browser automatically. Visit:[/yellow] {url}")
        time.sleep(0.6)


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_breathing() -> None:
    banner()
    console.print(Align.center(Text("Guided Breathing", style=f"bold {anim.SAFFRON}")))
    console.print(Align.center(Text("Inhale, hold, exhale — follow the circle. Ctrl+C to stop early.\n", style="dim")))
    try:
        cycles = IntPrompt.ask("How many breath cycles?", default=3)
    except Exception:
        cycles = 3
    try:
        anim.breathing_cycle(cycles=max(1, min(cycles, 10)))
        # Record the session (approximate duration)
        duration = cycles * (4 + 4 + 4)  # inhale + hold + exhale
        _history.add_session(duration, "breathing")
    except KeyboardInterrupt:
        pass
    console.print(Align.center(Text("\nWell done. Notice how you feel right now.", style=f"bold {anim.TEAL}")))


def cmd_timer() -> None:
    banner()
    console.print(Align.center(Text("Meditation Timer", style=f"bold {anim.SAFFRON}")))
    try:
        minutes = IntPrompt.ask("Minutes to sit for", default=5)
    except Exception:
        minutes = 5
    minutes = max(1, min(minutes, 120))
    duration_seconds = minutes * 60
    
    console.print(Align.center(Text(f"\nSettle in. Timer running for {minutes} minute(s)...", style="dim")))
    console.print(Align.center(Text("(Ctrl+C to stop early)\n", style="dim italic")))
    
    # Ask if user wants to view their stats before starting
    if _history.sessions:
        show_stats = Confirm.ask("View your session history before starting?", default=False)
        if show_stats:
            cmd_stats()
            console.print()
            console.print(Align.center(Text(f"Continuing with {minutes} minute timer...", style="dim")))
            time.sleep(1)
    
    try:
        # Use the progress-based timer
        anim.timer_with_progress(duration_seconds, f"🧘 Sitting for {minutes} minutes")
        # Record the session
        _history.add_session(duration_seconds, "timer")
    except KeyboardInterrupt:
        # If interrupted, still record the elapsed time
        console.print(Align.center(Text("\n⏸️ Session paused.", style=f"bold {anim.SAFFRON}")))
        # We don't record incomplete sessions
        return
    
    console.print(Align.center(Text("\n✨ Session complete. Slowly open your eyes.", style=f"bold {anim.TEAL}")))
    
    # Show a quick summary after the timer
    if _history.sessions:
        time.sleep(0.5)
        console.print()
        summary = _history.get_summary()
        table = Table(show_header=False, box=box.ROUNDED, border_style=anim.MAROON)
        table.add_row(Text("Today's total", style=f"bold {anim.TEAL}"), Text(f"{summary['today_minutes']:.1f} minutes"))
        table.add_row(Text("Week total", style=f"bold {anim.SAFFRON}"), Text(f"{summary['week_minutes']:.1f} minutes"))
        table.add_row(Text("Streak", style=f"bold {anim.LAVENDER}"), Text(f"{summary['streak_days']} days" if summary['streak_days'] > 0 else "Start your streak today! 🌱"))
        console.print(Align.center(table))


def cmd_stats() -> None:
    """Display comprehensive meditation statistics."""
    banner()
    console.print(Align.center(Text("📊 Session History & Statistics", style=f"bold {anim.SAFFRON}")))
    console.print()
    
    if not _history.sessions:
        console.print(Align.center(Text("No sessions recorded yet. Start your meditation journey today! 🌱", style=f"bold {anim.TEAL}")))
        time.sleep(2)
        return
    
    # Get all statistics
    summary = _history.get_summary()
    weekly_stats = _history.get_weekly_stats()
    monthly_stats = _history.get_monthly_stats()
    streak = summary['streak_days']
    
    # Overall summary
    summary_table = Table(show_header=False, box=box.ROUNDED, border_style=anim.MAROON, padding=(0, 2))
    summary_table.add_row(Text("📋 Overall Summary", style=f"bold {anim.SAFFRON}"), "")
    summary_table.add_row(Text("Total sessions", style=anim.TEAL), Text(f"{summary['total_sessions']}"))
    summary_table.add_row(Text("Total time", style=anim.TEAL), Text(f"{summary['total_minutes']:.1f} minutes"))
    summary_table.add_row(Text("Average session", style=anim.TEAL), Text(f"{summary['average_minutes']:.1f} minutes"))
    
    # Streak display with emoji
    if streak > 0:
        fire_emoji = "🔥" if streak >= 7 else "🌟"
        streak_text = f"{fire_emoji} {streak} day{'s' if streak != 1 else ''}"
    else:
        streak_text = "🌱 Start your streak today!"
    summary_table.add_row(Text("Current streak", style=anim.TEAL), Text(streak_text))
    
    # Recent sessions
    recent_sessions = _history.sessions[-5:] if len(_history.sessions) >= 5 else _history.sessions
    if recent_sessions:
        recent_text = ""
        for session in reversed(recent_sessions):
            recent_text += f"  • {session.timestamp.strftime('%m/%d %H:%M')} - {session.duration_minutes:.1f}m\n"
        summary_table.add_row(Text("Recent sessions", style=anim.TEAL), Text(recent_text.rstrip()))
    
    console.print(Align.center(summary_table))
    console.print()
    
    # Weekly breakdown
    console.print(Align.center(Text("📅 Last 7 Days", style=f"bold {anim.SAFFRON}")))
    week_table = Table(show_header=False, box=box.SIMPLE, border_style=anim.TEAL)
    week_table.add_row(Text("Day", style=f"bold {anim.LAVENDER}"), Text("Minutes", style=f"bold {anim.LAVENDER}"))
    
    for day, minutes in weekly_stats['daily_breakdown']:
        bar_length = int(minutes / (weekly_stats['total_minutes'] / 20 + 0.1)) if weekly_stats['total_minutes'] > 0 else 0
        bar = "█" * min(bar_length, 20)
        if minutes > 0:
            week_table.add_row(Text(day[:3], style=anim.TEAL), Text(f"{minutes:.1f}  {bar}", style=f"{anim.SAFFRON}"))
        else:
            week_table.add_row(Text(day[:3], style="dim"), Text("—", style="dim"))
    
    week_total = weekly_stats['total_minutes']
    week_avg = weekly_stats['average_minutes']
    week_count = weekly_stats['session_count']
    
    console.print(Align.center(week_table))
    console.print(Align.center(Text(f"Total: {week_total:.1f}m  |  Avg: {week_avg:.1f}m  |  Sessions: {week_count}", style=f"dim {anim.TEAL}")))
    console.print()
    
    # Monthly breakdown
    if monthly_stats['session_count'] > 0:
        console.print(Align.center(Text("📆 Last 30 Days", style=f"bold {anim.SAFFRON}")))
        month_table = Table(show_header=False, box=box.SIMPLE, border_style=anim.LAVENDER)
        month_table.add_row(Text("Period", style=f"bold {anim.TEAL}"), Text("Minutes", style=f"bold {anim.TEAL}"))
        
        for week, minutes in monthly_stats['weekly_breakdown']:
            bar_length = int(minutes / (monthly_stats['total_minutes'] / 20 + 0.1)) if monthly_stats['total_minutes'] > 0 else 0
            bar = "█" * min(bar_length, 20)
            if minutes > 0:
                month_table.add_row(Text(week, style=anim.LAVENDER), Text(f"{minutes:.1f}  {bar}", style=f"{anim.SAFFRON}"))
            else:
                month_table.add_row(Text(week, style="dim"), Text("—", style="dim"))
        
        console.print(Align.center(month_table))
        console.print(Align.center(Text(f"Total: {monthly_stats['total_minutes']:.1f}m  |  Avg: {monthly_stats['average_minutes']:.1f}m  |  Sessions: {monthly_stats['session_count']}", style=f"dim {anim.TEAL}")))
        console.print()
    
    # Options
    console.print(Align.center(Text("Options:", style=f"bold {anim.MAROON}")))
    console.print(Align.center(Text("[1] Clear all history   [Enter] Back to menu", style=f"dim {anim.TEAL}")))
    
    choice = Prompt.ask("", choices=["1", ""], default="", show_choices=False)
    if choice == "1":
        if Confirm.ask("Are you sure you want to clear all session history?", default=False):
            _history.clear_history()
            console.print(Align.center(Text("✨ History cleared.", style=f"bold {anim.SAFFRON}")))
            time.sleep(1)


def cmd_quote() -> None:
    banner()
    anim.spin_wireframe(seconds=1.6, shape=random.choice(["cube", "octa"]), label="drawing a reflection")
    q = random.choice(QUOTES)
    console.print()
    console.print(Align.center(Panel(anim.gradient_text(q), border_style=f"{anim.TEAL}", padding=(1, 4))))
    console.print()
    # Record a short reflection session (1 minute)
    _history.add_session(60, "reflection")


def cmd_about() -> None:
    banner()
    anim.spin_wireframe(seconds=2.0, shape="octa", label="meditation")
    info = Text()
    info.append("meditation", style=f"bold {anim.SAFFRON}")
    info.append("  —  a colorful terminal meditation companion.\n\n", style="dim")
    info.append("Works on Windows, Linux, macOS, Termux, and iOS terminal apps.\n", style="")
    info.append("Every session ends with links to further teachings.\n", style="")
    info.append(f"\n🧘 {len(_history.sessions)} sessions recorded so far.", style=f"dim {anim.TEAL}")
    console.print(Align.center(Panel(info, border_style=f"{anim.MAROON}", padding=(1, 3))))


# --------------------------------------------------------------------------
# Menu
# --------------------------------------------------------------------------

# (key, label, short description, action)
MENU = [
    ("1", "Guided breathing exercise", "follow the breath in and out, cycle by cycle", cmd_breathing),
    ("2", "Meditation timer", "sit quietly while a timer counts your session", cmd_timer),
    ("3", "View session history & stats", "see your progress and meditation patterns", cmd_stats),
    ("4", "A quiet reflection", "one short original line to sit with", cmd_quote),
    ("5", "About this tool", "what this app is and how it works", cmd_about),
    ("6", "Open Abhidhamma Teachings", "Buddha's deep teaching on the nature of mind", lambda: _open_direct("1")),
    ("7", "Open Lahari Mantras", "traditional chants for focus and devotion", lambda: _open_direct("2")),
    ("0", "Exit", "close the session and return to your shell", None),
]


def _open_direct(key: str) -> None:
    name, url = SITES[key]
    banner()
    console.print(Align.center(Text(f"Opening {name}...", style=f"bold {anim.SAFFRON}")))
    ok = open_url(url)
    if not ok:
        console.print(Align.center(Text(f"Couldn't launch a browser automatically. Visit: {url}", style="yellow")))
    time.sleep(0.6)


def print_menu() -> None:
    # Each row gets ONE solid color from the fixed 4-color theme, cycled
    # deterministically by row index - deliberate, not random per letter.
    table = Table(show_header=False, box=None, padding=(0, 1))
    for i, (key, label, desc, _) in enumerate(MENU):
        num_style = "bold red" if key == "0" else f"bold {anim.THEME[i % len(anim.THEME)]}"
        row_label = anim.theme_text(label, i)
        row_desc = Text(f" ({desc})", style="dim italic") if desc else Text("")
        table.add_row(Text(f"[{key}]", style=num_style), row_label + row_desc)
    console.print(Align.center(table))
    console.print()


def main() -> None:
    try:
        banner()
        anim.spin_wireframe(seconds=1.8, shape="cube", label="welcome")
        while True:
            banner()
            print_menu()
            choice = Prompt.ask(
                "Choose an option",
                choices=[k for k, _, _, _ in MENU],
                show_choices=False,
                default="0",
            )
            action = dict((k, fn) for k, _, _, fn in MENU)[choice]
            if action is None:
                banner()
                console.print(Align.center(anim.gradient_text("May you go in peace. 🙏")))
                console.print()
                break
            action()
            # Every command (except the two direct-open shortcuts, which
            # already are a link action) ends with the links footer.
            if choice not in ("6", "7"):
                show_links_menu()
    except KeyboardInterrupt:
        console.print()
        console.print(Align.center(Text("Interrupted. May you go in peace. 🙏", style=f"bold {anim.TEAL}")))


if __name__ == "__main__":
    main()