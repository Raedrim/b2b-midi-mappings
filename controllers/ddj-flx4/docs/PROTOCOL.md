# DDJ-FLX4 MIDI notes

This page records what the FLX4 sends and expects, observed on one unit in November 2026 (Windows, USB MIDI mode). The note numbers come from the Mixxx and djay mappings credited in the main README. Hardware checks cover the "Host messages" section. Anything marked *unverified* has no hardware check.

Channels below are zero-based, as in the preset files. Channel 0 is "MIDI channel 1".

## Wake-up

The controller misbehaves until the host sends a SysEx message, and it needs the message repeated. The bridge sends this every 2 seconds:

```
F0 00 40 05 00 00 04 05 00 50 02 F7
```

The Mixxx team found the payload. While the controller waits for it, the green MIDI LED blinks. Once the controller wakes, the LED stops blinking.

## What the controller sends

| Area | Channel | Notes |
|---|---|---|
| Deck 1 / Deck 2 buttons | 0 / 1 | Play `0x0B`, Cue `0x0C`, Sync `0x58`, Loop In `0x10`, Loop Out `0x11`, headphone Cue `0x54`, platter touch `0x36`, pad-mode buttons (below). |
| Deck 1 pads | 7, shifted 8 | Note numbers depend on the pad mode (below). |
| Deck 2 pads | 9, shifted 10 | Same layout as deck 1. |
| Mixer knobs and faders | 0 / 1 | Trim `0x04`, EQ hi/mid/low `0x07`/`0x0B`/`0x0F`, channel fader `0x13`, tempo `0x00`, jog side `0x21`, jog platter `0x22` (vinyl on) or `0x23` (vinyl off). All send 14-bit pairs with the fine byte at +32, except the jogs. |
| Beat FX | 4 / 5 | Level/depth CC `0x02`, on/off `0x47`, beat left/right `0x4A`/`0x4B`, select `0x63`, CH select slider `0x10` and `0x11`. The channel is 4 or 5, depending on the slider position. |
| Global | 6 | Crossfader CC `0x1F`, filter knobs `0x17`/`0x18`, headphone mix and level `0x0C`/`0x0D`, browse turn CC `0x40`, browse push `0x41`, load `0x46`/`0x47`. |

Buttons send a note-on with velocity 127 on press and velocity 0 on release.

## Host messages

### Pad modes

A press on a pad-mode button leaves the pads unchanged until the host answers. Send the **same note back as a note-on with velocity 127 on the deck's channel** (`0x90` for deck 1, `0x91` for deck 2). The controller then switches mode, lights that button, and sends the new mode's notes from its pads. Velocity 0 turns the button's light off.

| Button | Note | First pad note | Verified |
|---|---|---|---|
| Hot cue | `0x1B` | `0x00` | yes (default mode) |
| Pad FX 1 | `0x1E` | `0x10` | button detected |
| Beat jump | `0x20` | `0x20` | yes, pad 1 sends `0x20` after the switch |
| Sampler | `0x22` | `0x30` | yes, pad 1 sends `0x30` after the switch |
| Keyboard (Shift + Hot cue) | `0x69` | `0x40` | button detected |
| Pad FX 2 (Shift + Pad FX 1) | `0x6B` | `0x50` | button detected |
| Beat loop (Shift + Beat jump) | `0x6D` | `0x60` | button detected |
| Key shift (Shift + Sampler) | `0x6F` | `0x70` | button detected |

"Button detected" means the button's press arrives on that note. The reference mappings supply the first pad note for those modes, and no hardware check confirms it. Pads 1 to 8 in each mode send consecutive notes from the first pad note.

### LEDs

Light an LED with a note-on to the channel and note the control sends, using velocity 127 for on and 0 for off. Hardware confirmed this for pad LEDs (channel 7 or 9, the pad's current note), the pad-mode buttons, the headphone Cue button (`0x54`), and the Play and Cue buttons. The bridge turns the old mode's pad LEDs off and the new mode's on at every mode switch.

Nobody has explored pad brightness and colour at other velocities.

## Windows port exclusivity

On Windows, only one program at a time can open the FLX4's MIDI input, and the same holds for the output. A second open fails:

```
MidiInWinMM::openPort: error creating Windows MM MIDI input port.
MidiOutWinMM::openPort: error creating Windows MM MIDI output port.
```

The wake-up and LEDs need the output, and B2B Studio needs the input, so the two programs cannot both talk to the real device. The bridge reads the input itself and forwards it to a virtual port. macOS has no such restriction.

## Not worked out

- The third position of the Beat FX CH select slider.
- The channel the Beat FX on/off button uses with the slider on CH2. It is probably 5, but the preset binds only 4.
- The vinyl-off platter message (`0x23`) has no binding, and the shift-touch message `0x67` is unused.
- Pad colours and the jog ring lights.
