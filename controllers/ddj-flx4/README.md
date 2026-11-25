# Pioneer DDJ-FLX4

Maps a DDJ-FLX4 onto two decks and a DJM-A9 mixer in B2B Studio: transport, loops, jog, EQ and faders, headphones, Beat FX, and eight pad modes with working lights.

This project is independent and unofficial. Pioneer DJ and B2B Studio do not endorse or support it. It depends on how B2B Studio behaves today, and its developers can change that at any time. If something breaks after an app update, open an issue on the project's GitHub page with your B2B Studio version.

## Setup

Plugging in the FLX4 and importing a preset is not enough. The controller waits for a wake-up message, and it switches pad modes and lights buttons only when the computer tells it to. A small script, the bridge, handles both. These steps set up the bridge, which gives you all eight pad modes and working lights.

Every file mentioned below sits in this folder, the unzipped `ddj-flx4` folder from the release download.

### Windows

1. Install [Python 3](https://www.python.org/downloads/). In the installer, tick **Add python.exe to PATH**.
2. Install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html). Open it, type `FLX4 Bridge` in the port-name box at the bottom, and click **+**. Leave loopMIDI running. The tray is fine.
3. Plug in the FLX4. Close B2B Studio and any other program that uses the controller (rekordbox, Serato, MIDI-OX).
4. Double-click `start-bridge.bat`. The first run installs its dependencies. Leave the window open.
5. The green MIDI LED on the controller stops blinking, and the pad-mode buttons light when you press them.
6. Start B2B Studio, open its MIDI settings and import `presets/ddj-flx4-bridge-windows.b2bmidi.json`.

Start the bridge before B2B Studio every time.

Windows lets only one program read the FLX4 at a time. The bridge reads it and passes everything to the loopMIDI port, and B2B Studio reads that port instead. Tobias Erichsen makes loopMIDI, which is free for private non-commercial use. Its license forbids redistribution, so this project does not include it.

### macOS (untested)

macOS lets several programs share a MIDI device, so you need no virtual port.

1. Install [Python 3](https://www.python.org/downloads/).
2. Plug in the FLX4.
3. Double-click `start-bridge.command`. If macOS refuses to open it, right-click it and choose **Open**. If it still will not run, make it executable with `chmod +x start-bridge.command`. The first run installs its dependencies. Leave the window open.
4. Start B2B Studio and import `presets/ddj-flx4-bridge-mac.b2bmidi.json`.

Only Windows has been tested. The preset assumes B2B Studio names the controller `DDJ-FLX4`. If it shows another name, replace `DDJ-FLX4|` with that name throughout the preset file, or open an issue.

### Without loopMIDI

To skip loopMIDI, run `pip install -r requirements.txt` in this folder, then `python flx4_wake.py`, and import `presets/ddj-flx4-direct.b2bmidi.json`. The pads stay in hot cue mode and the controller has no lights. You still get the deck, mixer and Beat FX controls, plus a second bank of loops and jumps on Shift + pads.

### If something goes wrong

| What you see | What to do |
|---|---|
| `DDJ-FLX4 not found` | Plug the controller in again and close other MIDI programs. |
| `Virtual port "FLX4 Bridge" not found` | Create the port in loopMIDI with exactly that name, and keep loopMIDI running. |
| `error creating Windows MM MIDI ... port` | Another program holds the controller. Quit B2B Studio completely, including its tray icon and the `b2b-engine-x64` process, then start the bridge first. |
| B2B Studio says it could not open DDJ-FLX4 | Expected. The bridge holds the real device. |
| The green LED keeps blinking | The wake-up message did not arrive. Restart the bridge. |
| Controls do nothing in B2B Studio | Confirm you imported the preset for your setup and started the bridge before B2B Studio. |

## Contents

| File | Purpose |
|---|---|
| `start-bridge.bat`, `start-bridge.command` | Double-click launchers for Windows and macOS. |
| `flx4_bridge.py` | Wakes the controller, switches pad modes, lights buttons and, on Windows, forwards MIDI to loopMIDI. |
| `flx4_wake.py` | Sends the wake-up message only. Pairs with the direct preset. |
| `presets/` | The importable presets. |
| `docs/MAPPING-bridge-windows.md`, `docs/MAPPING-direct.md` | Every binding, with its message, target and effect. |
| `docs/PROTOCOL.md` | What the FLX4 sends and expects. |
| `mapping.yaml` | The source of truth. The presets and mapping tables come from it. |

## Presets

| Preset | Use it with | Pad modes | Controller lights |
|---|---|---|---|
| `ddj-flx4-bridge-windows.b2bmidi.json` | `flx4_bridge.py`, loopMIDI port `FLX4 Bridge` | all eight | yes |
| `ddj-flx4-bridge-mac.b2bmidi.json` | `flx4_bridge.py` | all eight | yes |
| `ddj-flx4-direct.b2bmidi.json` | `flx4_wake.py` | hot cue only | no |

The presets differ in the MIDI input name each binding reads from and in how they use the pads and pad-mode buttons. Everything else is identical.

## Controls

The left deck is Deck 1 and the right deck is Deck 2. Mixer channel strips follow the same channels.

| Control | Does |
|---|---|
| Play, Cue, Sync | CDJ play, cue and beat sync. A long press on Sync makes the deck sync master. Shift + Sync cycles the tempo range. |
| Shift + Play | Reverse roll while held. |
| Shift + Cue | Jump to the start of the track. |
| Loop In, Loop Out, Reloop | CDJ loop controls. |
| Cue/Loop Call ◀ ▶ | Halve and double the loop. With Shift, jump to the previous or next memory cue. |
| Jog | The platter top scratches in vinyl mode, the side ring bends pitch, and touch works. |
| Tempo fader | Deck pitch. |
| Browse, Load | Scroll and load tracks. Load acts as the CDJ's rotary push. |
| Trim, EQ, fader, filter, headphone cue | A9 channel strip. The FLX4 filter knob drives the A9 COLOR knob. |
| Crossfader, headphone mix and level | A9 crossfader and headphone section A. |
| Beat FX | On/off, level/depth, beat ◀ ▶, channel select and tap. Shift + Browse turn picks the effect. |

### Pad modes (bridge presets)

Press a pad-mode button to switch. Hold Shift for the second row of modes.

| Pad mode | Pads 1–8 | Shift + pads |
|---|---|---|
| Hot cue | Hot cues A–H | none |
| Beat jump | ◀1 1▶ ◀2 2▶ ◀4 4▶ ◀8 8▶ | ◀16 16▶ ◀32 32▶ ◀64 64▶ ◀½ ½▶ |
| Beat loop | Loops of ¼ ½ 1 2 4 8 16 32 beats | none |
| Pad FX 2 (Shift + Pad FX 1) | Odd loop sizes: 1/16 1/8 1/3 3/4 3/2 3 6 9 | none |
| Key shift (Shift + Sampler) | −1 +1 −2 +2 −3 +3 semitones, reset, key sync | none |
| Sampler | Memory, delete, slip, quantize, master tempo, tempo reset, vinyl, CDJ jog | Next track, search ◀◀ ▶▶, nudge − +, reverse, elapsed/remain |
| Pad FX 1 | Left deck: Beat FX toolbox (low/mid/hi, quantize, CF.A, CF.B, MST). Right deck: Sound Color FX (space, dub echo, crush, sweep, noise, filter, center lock). | none |

The mixer is shared, so each mixer control can sit on only one deck's pads. That is why Pad FX 1 differs between the decks.

The direct preset has fewer functions. The pads are hot cues. Shift + pads 1–4 set 1, 2, 4 and 8 beat loops, and Shift + pads 5–8 jump ◀4 4▶ ◀16 16▶. The pad-mode buttons act as plain buttons (memory, slip, beat jump ◀ ▶, key −1/+1, quantize, key sync).

### Deleting a hot cue

Hold Shift + Cue, release Shift, then tap the hot cue pad. Shift + pad sends on a different MIDI channel and cannot reach the hot cue itself. Nobody has verified this on hardware yet.

## Bridge options

```bash
python flx4_bridge.py --pad-lights banks   # default: pads lit in every mode except hot cue
python flx4_bridge.py --pad-lights all     # every pad lit in every mode
python flx4_bridge.py --pad-lights held    # pads light only while pressed
python flx4_bridge.py --pad-lights off     # no pad lights
python flx4_bridge.py --forward off        # no forwarding, for testing without loopMIDI
python flx4_bridge.py --virtual-port NAME  # use a differently named loopMIDI port
```

The launchers pass options through. For example, run `start-bridge.bat --pad-lights held`.

Hot cue pads stay dark when idle by default. The bridge cannot see which cues B2B Studio has set, so lighting all eight would imply eight cues exist. The same limit applies to play and loop state. The bridge mirrors only the headphone Cue button, flipping its light on each press, so it drifts out of step if you also click that button on screen.

## Known limitations

- Lights that depend on B2B Studio's state (cues set, deck playing, loop active) are impossible, because B2B Studio sends lamp messages to controllers only for developer accounts.
- Beat FX on/off may not respond with the channel slider on CH2. The controller sends two messages and a control can have only one source, so the preset binds one.
- The preset leaves the Beat FX channel slider's third position and the platter's vinyl-off message unbound.
- The macOS setup is untested.

## Claiming other decks

The presets use `d0` and `d1` with mixer channels `ch0` and `ch1`. Deck number N is `d(N-1)`. To use Deck 3 on the left and Deck 4 on the right, find and replace in this order so nothing collides:

1. `d1@` → `d3@` and `mx@djm-a9:ch1.` → `mx@djm-a9:ch3.`
2. `d0@` → `d2@` and `mx@djm-a9:ch0.` → `mx@djm-a9:ch2.`

Leave the shared controls (crossfader, Beat FX, headphones) alone. Each preset file carries the same note at the top.

## Changing the preset

You need a clone of the project's repository for this, not the release zip. Edit `mapping.yaml`, then regenerate and check from the repository root:

```bash
python tools/b2bmap.py build
python tools/b2bmap.py check
```

This rewrites the three presets and the mapping tables. Do not edit the generated files by hand. The repository's `docs/MAPPING-FORMAT.md` describes the file format.
