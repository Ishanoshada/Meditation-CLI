# meditation

A colorful, animated, cross-platform terminal meditation companion — with a
genuine (math-driven, not canned) rotating 3D wireframe animation, a guided
inhale-hold-exhale breathing exercise, a Tharataka (candle-gazing) meditation,
a session timer with progress tracking, **comprehensive session history and
statistics**, and quick links out to further teachings.

Works anywhere Python 3 runs: **Windows, Linux, macOS, Termux (Android),
and iOS terminal apps** (Pythonista, a-Shell).

## Install

```bash
pip install meditation
```

On **Termux**, install Python first, then pip install as usual:

```bash
pkg install python
pip install meditation
```

On **iOS** (a-Shell or Pythonista), open a shell and run the same `pip install meditation`.

## Usage

```bash
meditation
```

or

```bash
python -m meditation
```

## What each menu option does

| Option | What it is |
|---|---|
| **1. Guided breathing exercise** | An animated circle walks you through **inhale → hold (4s) → exhale**, repeated for as many cycles as you choose. Sessions are automatically recorded. |
| **2. Meditation timer** | Pick a number of minutes and sit quietly while a progress bar and timer count the session down. **Option to view stats before starting.** Sessions are automatically recorded. |
| **3. Tharataka meditation** | **🔴 NEW!** Ancient candle-gazing technique. Gaze at a **solid black circle on a pure white background** with a live countdown timer (MM:SS format). Perfect for focus and eye relaxation training. Recorded to your session history. |
| **4. View session history & stats** | **📊** See your complete meditation journey with: <br> • Total sessions and total time <br> • Average session duration <br> • Current streak tracking (🔥 for 7+ days) <br> • Last 7 days breakdown with visual bars <br> • Last 30 days weekly breakdown <br> • Recent sessions list <br> • Option to clear history |
| **5. A quiet reflection** | Shows one short, original line to sit with — a small prompt for reflection, not a lecture. Recorded as a 1-minute reflection session. |
| **6. About this tool** | A quick summary of what the app is and how it works, including total sessions recorded. |
| **7. Open Abhidhamma Teachings** | Opens https://abhidhamma.ishanoshada.com/ — Buddha's deep teaching on the nature of mind. |
| **8. Open Lahari Mantras** | Opens https://lahari-mantras.ishanoshada.com/ — traditional chants for focus and devotion. |
| **0. Exit** | Closes the session. |

## Session Tracking & Statistics

The app automatically tracks your meditation practice with:
- **Persistent storage**: All sessions saved to `~/.meditation_history.json`
- **Session types**: Timer sessions, breathing exercises, Tharataka sessions, and reflections are all tracked
- **Streak tracking**: Counts consecutive days of meditation
- **Weekly breakdown**: Visual chart showing your practice for the last 7 days
- **Monthly breakdown**: Weekly totals for the last 30 days
- **Progress bars**: Visual representation of your consistency

### How sessions are recorded:
| Session Type | What gets recorded |
|---|---|
| **Guided breathing** | Duration based on number of cycles (inhale+hold+exhale) |
| **Meditation timer** | Full session duration (if completed or stopped early) |
| **Tharataka meditation** | Full session duration with selected time |
| **Quiet reflection** | 1 minute reflection session |

### Statistics you can view:
- Total sessions and total minutes
- Average session length
- Current streak in days (with emoji indicators)
- Last 7 days with daily totals (visual bars)
- Last 30 days with weekly breakdown
- Recent sessions with timestamps

## Data Storage

Your meditation history is stored locally at:
```
~/.meditation_history.json
```

This file contains:
- All session records with timestamps and durations
- Session types (timer/breathing/tharataka/reflection)
- Last updated timestamp

You can clear your history from the statistics menu (option 4).

## Color theme

All colors come from one deliberate 4-color palette (not random per
character): saffron `#f4a259`, deep maroon `#a13d63`, teal `#2ec4b6`, and
soft lavender `#9d8df1` — inspired by monastic robes and calm water/sky.

## Recent Updates

**v2.2.0** — Tharataka Meditation
- Added Tharataka (candle-gazing) meditation mode
- Display: Full-screen white background with centered black circle
- Timer: Live countdown in MM:SS format at bottom of screen
- Fully integrates with session history and statistics
- Supports Ctrl+C to stop early

## Development

```bash
git clone https://github.com/ishanoshada/Meditation-CLI.git
cd Meditation-CLI
pip install -e .
meditation
```

Build and publish with either toolchain — both `pyproject.toml` and
`setup.py` are included:

```bash
python -m build
twine upload dist/*
```

## Roadmap

More companion web apps are on the way — keep an eye on the
[GitHub profile](https://github.com/ishanoshada) for what's coming next.

Planned features:
- [x] Session history tracking
- [x] Statistics dashboard
- [x] Streak tracking
- [x] Tharataka meditation
- [ ] Export data to CSV
- [ ] Daily goals and reminders
- [ ] Sound integration (where supported)

## Uninstall

```bash
pip uninstall meditation
```

## License

MIT License — Ishan Oshada (ic31908@gmail.com)
