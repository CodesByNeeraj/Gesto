# Gesto

Your gestures, your rules. Gesto is a local macOS app for mapping hand gestures
you train yourself to useful computer actions.

## Setup on macOS

Gesto is built and tested on macOS with Python 3.12. Its media, tab-navigation,
and lock-screen actions use Apple's `swift` command. This one-time command
installs Swift as part of Xcode Command Line Tools:

```bash
xcode-select --install
```

Follow the macOS installer prompt until it completes. Then run:

```bash
/usr/bin/swift --version
```

If it prints a Swift version, continue. If it does not, the Apple installer has
not finished or needs to be run again.

Then build the app bundle:

```bash
git clone https://github.com/CodesByNeeraj/Gesto.git
cd Gesto
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-build.txt
scripts/build-macos-app.sh
open dist/Gesto.app
```

On the first **Start Detection**, macOS asks for Camera access. Choose
**Allow**. If you previously denied it, enable Gesto in **System Settings >
Privacy & Security > Camera**. macOS may also request Accessibility access for
media controls, browser-tab navigation, and locking the screen. Screenshot
capture may require Screen Recording access. Enable the relevant setting if an
action does not respond.

## Who it is for

Gesto is for people who repeat small computer actions all day: developers,
students, creators, and anyone who wants a personalised shortcut layer without
memorising more key combinations.

## What it solves

Opening an app, pausing media, switching tabs, or taking a screenshot is quick
once. Repeating those interruptions breaks focus. Gesto lets you define a
gesture that feels natural to you, map it to one action, and trigger it from
your laptop camera.

## Features

- Train named static gestures from 40 hand-landmark samples.
- Retrain or remove a gesture without rebuilding the rest of your mappings.
- Map one gesture to open an app, play or pause media, take a screenshot, lock
  the screen, or switch to the next or previous browser tab.
- Pick an installed app or type its name when creating an open-app mapping.
- Use confidence thresholds and a cooldown to reduce accidental triggers.
- Keep camera frames, landmarks, trained models, and mappings on your Mac.

## How it works

MediaPipe extracts 21 hand landmarks from each camera frame. Gesto stores the
samples for gestures you train locally and uses a scikit-learn KNN classifier to
recognise them. A background detection loop looks up the matched gesture in a
local JSON mapping file and executes its assigned macOS action.

## Tech stack

Python 3.12, CustomTkinter, MediaPipe, OpenCV, scikit-learn, PyInstaller,
pytest, Flake8, Bandit, and GitHub Actions.

## Privacy

Camera frames, landmarks, and trained models stay on your Mac. Gesto neither
collects nor uploads them to backend servers. Detection runs only after you
start it.

## OpenAI Build Week Hackathon

Built for the **OpenAI Build Week Hackathon** in **Apps for Your Life**:
consumer apps for everyday life, across productivity, creativity, home, family,
travel, health, and personal finance.

## Building with Codex

Gesto was developed through an ongoing collaboration between the project owner
and Codex, powered by GPT-5.6. The project owner set the product direction and
made the key calls on the gesture-first workflow, custom training, local-only
privacy, supported actions, and UI behaviour. Codex accelerated delivery by
turning those decisions into small, tested pull requests, investigating runtime
bugs, improving macOS packaging, and maintaining the test, lint, and security
checks. GPT-5.6 and Codex helped move quickly from product requirements to a
working local desktop application, while the final product and design decisions
remained human-led.

## Codex feedback

The core functionality was built in the following Codex project thread:

```text
Codex Session ID: 019f70e4-4789-7070-916b-cc7bc7e1fea3
```
