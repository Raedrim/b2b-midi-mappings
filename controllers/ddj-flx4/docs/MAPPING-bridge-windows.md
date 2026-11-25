# Mapping reference - FLX4 (bridge, Windows)

Generated from `mapping.yaml` by `tools/b2bmap.py`; do not edit by hand. MIDI input: `FLX4 Bridge`.

Channels are shown 1-based (ch1 is the controller's first MIDI channel). **Custom** rows are judgement calls: the controller has no matching control, or the target is repurposed.

## Deck 1 (left) - transport

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x0B ch1 | `d0@cdj-3000x:play` |  | PLAY/PAUSE button. 1:1 with the CDJ PLAY/PAUSE. |
| Note 0x0C ch1 | `d0@cdj-3000x:cue` |  | CUE button. 1:1 with the CDJ CUE. |
| Note 0x58 ch1 | `d0@cdj-3000x:beatsync` |  | SYNC button. 1:1 with the CDJ BEAT SYNC. |
| Note 0x5C ch1 | `d0@cdj-3000x:master` | custom | the FLX4 has no MASTER button. SYNC long-press (note 0x5C) makes this deck the sync master, which is what the CDJ MASTER button does. |
| Note 0x60 ch1 | `d0@cdj-3000x:temporange` | custom | SHIFT+SYNC cycles the tempo range, standing in for the CDJ TEMPO RANGE button. |
| Note 0x0E ch1 | `d0@cdj-3000x:direction/sliprev` | custom | the FLX4 has no reverse lever. SHIFT+PLAY (Pioneer's reverse roll / censor) drives the CDJ slip-reverse lever position. |
| Note 0x48 ch1 | `d0@cdj-3000x:trackback` | custom | SHIFT+CUE jumps to the start of the track, matching the CDJ TRACK SEARCH \|<< button (the FLX4 has no track search buttons). |
| Note 0x68 ch1 | `d0@cdj-3000x:calldelete` | custom | the CDJ CALL/DELETE modifier. Hold SHIFT+CUE (note 0x68), let go of SHIFT, then tap a hot cue pad to delete that hot cue. Needed because SHIFT+pad is a different MIDI channel and can't reach the hot cue itself. Not yet verified on hardware. |

## Deck 1 (left) - loops

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x10 ch1 | `d0@cdj-3000x:loopin` |  | LOOP IN / 4 BEAT button. 1:1 with the CDJ LOOP IN. |
| Note 0x11 ch1 | `d0@cdj-3000x:loopout` |  | LOOP OUT button. 1:1 with the CDJ LOOP OUT. |
| Note 0x4D ch1 | `d0@cdj-3000x:reloop` |  | RELOOP/EXIT button. 1:1 with the CDJ RELOOP/EXIT. |
| Note 0x51 ch1 | `d0@cdj-3000x:beatloop4` | custom | CUE/LOOP CALL < halves the active loop. On a CDJ this is the 4 BEAT LOOP (1/2X) button; the FLX4 has neither, so its CALL arrows take the halve/double job. |
| Note 0x53 ch1 | `d0@cdj-3000x:beatloop8` | custom | CUE/LOOP CALL > doubles the active loop (CDJ 8 BEAT LOOP / 2X). |
| Note 0x3E ch1 | `d0@cdj-3000x:cuecall_l` | custom | SHIFT+CUE/LOOP CALL < jumps to the previous memory cue (CDJ CUE/LOOP CALL <). |
| Note 0x3D ch1 | `d0@cdj-3000x:cuecall_r` | custom | SHIFT+CUE/LOOP CALL > jumps to the next memory cue (CDJ CUE/LOOP CALL >). |

## Deck 1 (left) - jog and tempo

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| CC 0x22 ch1 | `d0@cdj-3000x:jogtop` | rel=binoff | Jog platter top while VINYL mode is on (scratch). Relative, binary-offset (centre 64). The vinyl-off platter message (cc 0x23) is not bound. |
| CC 0x21 ch1 | `d0@cdj-3000x:jog` | rel=binoff | Jog side ring (pitch bend). Relative, binary-offset (centre 64). |
| Note 0x36 ch1 | `d0@cdj-3000x:jog/touch` |  | Platter touch sensor. Tells B2B Studio the platter is held so the top wheel scratches instead of bends. |
| CC 0x00 ch1 | `d0@cdj-3000x:tempo` | invert=True | TEMPO fader, 14-bit (B2B Studio pairs the LSB on cc 0x20 by itself). Inverted so pushing the fader up speeds up, like the app's own learn does. |

## Deck 1 (left) - browse and load

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| CC 0x40 ch7 | `d0@cdj-3000x:rotary` | custom, rel=2c | BROWSE knob turn, relative two's complement. The FLX4 has one browse knob shared by both decks, so the same message is bound to both decks' rotary and both browsers scroll if both are open. |
| Note 0x41 ch7 | `d0@cdj-3000x:browse` | custom | BROWSE knob push, opens the browser on both decks (shared control, see rotary). |
| Note 0x42 ch7 | `d0@cdj-3000x:back` | custom | SHIFT+BROWSE push steps back out of a folder (CDJ BACK). Shared by both decks. |
| Note 0x46 ch7 | `d0@cdj-3000x:rotary/push` | custom | the FLX4 LOAD 1 button. The CDJ has no LOAD button; it loads by pushing the rotary, so LOAD is bound to the rotary push. |

## Deck 1 (left) - HOT CUE mode

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x00 ch8 | `d0@cdj-3000x:hotcue0` |  | Pad 1: hot cue A. 1:1 with CDJ HOT CUE A. |
| Note 0x01 ch8 | `d0@cdj-3000x:hotcue1` |  | Pad 2: hot cue B. 1:1 with CDJ HOT CUE B. |
| Note 0x02 ch8 | `d0@cdj-3000x:hotcue2` |  | Pad 3: hot cue C. 1:1 with CDJ HOT CUE C. |
| Note 0x03 ch8 | `d0@cdj-3000x:hotcue3` |  | Pad 4: hot cue D. 1:1 with CDJ HOT CUE D. |
| Note 0x04 ch8 | `d0@cdj-3000x:hotcue4` |  | Pad 5: hot cue E. 1:1 with CDJ HOT CUE E. |
| Note 0x05 ch8 | `d0@cdj-3000x:hotcue5` |  | Pad 6: hot cue F. 1:1 with CDJ HOT CUE F. |
| Note 0x06 ch8 | `d0@cdj-3000x:hotcue6` |  | Pad 7: hot cue G. 1:1 with CDJ HOT CUE G. |
| Note 0x07 ch8 | `d0@cdj-3000x:hotcue7` |  | Pad 8: hot cue H. 1:1 with CDJ HOT CUE H. |

## Deck 1 (left) - BEAT JUMP mode

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x20 ch8 | `d0@cdj-3000x:screen/jump=-1` | custom | pad 1 jumps 1 beat back. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x21 ch8 | `d0@cdj-3000x:screen/jump=1` | custom | pad 2 jumps 1 beat forward. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x22 ch8 | `d0@cdj-3000x:screen/jump=-2` | custom | pad 3 jumps 2 beats back. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x23 ch8 | `d0@cdj-3000x:screen/jump=2` | custom | pad 4 jumps 2 beats forward. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x24 ch8 | `d0@cdj-3000x:screen/jump=-4` | custom | pad 5 jumps 4 beats back. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x25 ch8 | `d0@cdj-3000x:screen/jump=4` | custom | pad 6 jumps 4 beats forward. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x26 ch8 | `d0@cdj-3000x:screen/jump=-8` | custom | pad 7 jumps 8 beats back. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x27 ch8 | `d0@cdj-3000x:screen/jump=8` | custom | pad 8 jumps 8 beats forward. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x20 ch9 | `d0@cdj-3000x:screen/jump=-16` | custom | SHIFT+pad 1 jumps 16 beats back (bigger jumps and a half beat). |
| Note 0x21 ch9 | `d0@cdj-3000x:screen/jump=16` | custom | SHIFT+pad 2 jumps 16 beats forward (bigger jumps and a half beat). |
| Note 0x22 ch9 | `d0@cdj-3000x:screen/jump=-32` | custom | SHIFT+pad 3 jumps 32 beats back (bigger jumps and a half beat). |
| Note 0x23 ch9 | `d0@cdj-3000x:screen/jump=32` | custom | SHIFT+pad 4 jumps 32 beats forward (bigger jumps and a half beat). |
| Note 0x24 ch9 | `d0@cdj-3000x:screen/jump=-64` | custom | SHIFT+pad 5 jumps 64 beats back (bigger jumps and a half beat). |
| Note 0x25 ch9 | `d0@cdj-3000x:screen/jump=64` | custom | SHIFT+pad 6 jumps 64 beats forward (bigger jumps and a half beat). |
| Note 0x26 ch9 | `d0@cdj-3000x:screen/jump=-0.5` | custom | SHIFT+pad 7 jumps 0.5 beats back (bigger jumps and a half beat). |
| Note 0x27 ch9 | `d0@cdj-3000x:screen/jump=0.5` | custom | SHIFT+pad 8 jumps 0.5 beats forward (bigger jumps and a half beat). |

## Deck 1 (left) - BEAT LOOP mode

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x60 ch8 | `d0@cdj-3000x:screen/loop=0.25` | custom | pad 1 sets a 0.25-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x61 ch8 | `d0@cdj-3000x:screen/loop=0.5` | custom | pad 2 sets a 0.5-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x62 ch8 | `d0@cdj-3000x:screen/loop=1` | custom | pad 3 sets a 1-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x63 ch8 | `d0@cdj-3000x:screen/loop=2` | custom | pad 4 sets a 2-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x64 ch8 | `d0@cdj-3000x:screen/loop=4` | custom | pad 5 sets a 4-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x65 ch8 | `d0@cdj-3000x:screen/loop=8` | custom | pad 6 sets a 8-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x66 ch8 | `d0@cdj-3000x:screen/loop=16` | custom | pad 7 sets a 16-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x67 ch8 | `d0@cdj-3000x:screen/loop=32` | custom | pad 8 sets a 32-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |

## Deck 1 (left) - PAD FX 2 mode (odd loop sizes)

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x50 ch8 | `d0@cdj-3000x:screen/loop=0.0625` | custom | pad 1 sets a 0.0625-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x51 ch8 | `d0@cdj-3000x:screen/loop=0.125` | custom | pad 2 sets a 0.125-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x52 ch8 | `d0@cdj-3000x:screen/loop=0.3333333333333333` | custom | pad 3 sets a 0.333333-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x53 ch8 | `d0@cdj-3000x:screen/loop=0.75` | custom | pad 4 sets a 0.75-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x54 ch8 | `d0@cdj-3000x:screen/loop=1.5` | custom | pad 5 sets a 1.5-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x55 ch8 | `d0@cdj-3000x:screen/loop=3` | custom | pad 6 sets a 3-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x56 ch8 | `d0@cdj-3000x:screen/loop=6` | custom | pad 7 sets a 6-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x57 ch8 | `d0@cdj-3000x:screen/loop=9` | custom | pad 8 sets a 9-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |

## Deck 1 (left) - KEY SHIFT mode

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x70 ch8 | `d0@cdj-3000x:screen/key=-1` | custom | pad 1 shifts the key down 1 semitone. |
| Note 0x71 ch8 | `d0@cdj-3000x:screen/key=1` | custom | pad 2 shifts the key up 1 semitone. |
| Note 0x72 ch8 | `d0@cdj-3000x:screen/key=-2` | custom | pad 3 shifts the key down 2 semitones. |
| Note 0x73 ch8 | `d0@cdj-3000x:screen/key=2` | custom | pad 4 shifts the key up 2 semitones. |
| Note 0x74 ch8 | `d0@cdj-3000x:screen/key=-3` | custom | pad 5 shifts the key down 3 semitones. |
| Note 0x75 ch8 | `d0@cdj-3000x:screen/key=3` | custom | pad 6 shifts the key up 3 semitones. |
| Note 0x76 ch8 | `d0@cdj-3000x:screen/key=0` | custom | pad 7 resets the key. |
| Note 0x77 ch8 | `d0@cdj-3000x:keysync` | custom | pad 8 matches the key to the other deck, or resets it (CDJ KEY SYNC). |

## Deck 1 (left) - SAMPLER mode (deck utilities)

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x30 ch8 | `d0@cdj-3000x:memory` | custom | pad 1 saves a memory cue (or the active loop), the CDJ MEMORY button. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x31 ch8 | `d0@cdj-3000x:delete` | custom | pad 2 deletes the memory cue you are on, the CDJ DELETE button. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x32 ch8 | `d0@cdj-3000x:slip` | custom | pad 3 toggles SLIP. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x33 ch8 | `d0@cdj-3000x:quantize` | custom | pad 4 toggles QUANTIZE. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x34 ch8 | `d0@cdj-3000x:mastertempo` | custom | pad 5 toggles MASTER TEMPO (key lock). The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x35 ch8 | `d0@cdj-3000x:temporeset` | custom | pad 6 resets the tempo fader to 0%. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x36 ch8 | `d0@cdj-3000x:vinylmode` | custom | pad 7 switches the jog to VINYL mode. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x37 ch8 | `d0@cdj-3000x:cdjmode` | custom | pad 8 switches the jog to CDJ mode. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x30 ch9 | `d0@cdj-3000x:trackfwd` | custom | SHIFT+pad 1: next track (CDJ TRACK SEARCH >>\|). |
| Note 0x31 ch9 | `d0@cdj-3000x:searchback` | custom | SHIFT+pad 2: fast-scan back (CDJ SEARCH <<). |
| Note 0x32 ch9 | `d0@cdj-3000x:searchfwd` | custom | SHIFT+pad 3: fast-scan forward (CDJ SEARCH >>). |
| Note 0x33 ch9 | `d0@cdj-3000x:nudgeback` | custom | SHIFT+pad 4: nudge the tempo down (CDJ NUDGE -). |
| Note 0x34 ch9 | `d0@cdj-3000x:nudgefwd` | custom | SHIFT+pad 5: nudge the tempo up (CDJ NUDGE +). |
| Note 0x35 ch9 | `d0@cdj-3000x:direction/rev` | custom | SHIFT+pad 6: reverse playback while held (CDJ reverse lever). |
| Note 0x36 ch9 | `d0@cdj-3000x:screen/time` | custom | SHIFT+pad 7: switches the time display between elapsed and remaining. |

## Deck 1 (left) - PAD FX 1 mode (Beat FX toolbox)

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x10 ch8 | `mx@djm-a9:fx.freqLow` | custom | left deck PAD FX 1, pad 1: Beat FX LOW band on/off (A9 LOW). The mixer is shared, so each mixer control can only sit on one deck's pads: the left deck holds the Beat FX toolbox. |
| Note 0x11 ch8 | `mx@djm-a9:fx.freqMid` | custom | left deck PAD FX 1, pad 2: Beat FX MID band on/off (A9 MID). The mixer is shared, so each mixer control can only sit on one deck's pads: the left deck holds the Beat FX toolbox. |
| Note 0x12 ch8 | `mx@djm-a9:fx.freqHi` | custom | left deck PAD FX 1, pad 3: Beat FX HI band on/off (A9 HI). The mixer is shared, so each mixer control can only sit on one deck's pads: the left deck holds the Beat FX toolbox. |
| Note 0x13 ch8 | `mx@djm-a9:fx.quantize` | custom | left deck PAD FX 1, pad 4: Beat FX QUANTIZE on/off. The mixer is shared, so each mixer control can only sit on one deck's pads: the left deck holds the Beat FX toolbox. |
| Note 0x14 ch8 | `mx@djm-a9:fx.cfa` | custom | left deck PAD FX 1, pad 5: puts every channel on crossfader side A in the Beat FX (CH SELECT CF.A). The mixer is shared, so each mixer control can only sit on one deck's pads: the left deck holds the Beat FX toolbox. |
| Note 0x15 ch8 | `mx@djm-a9:fx.cfb` | custom | left deck PAD FX 1, pad 6: puts every channel on crossfader side B in the Beat FX (CH SELECT CF.B). The mixer is shared, so each mixer control can only sit on one deck's pads: the left deck holds the Beat FX toolbox. |
| Note 0x16 ch8 | `mx@djm-a9:fx.mst` | custom | left deck PAD FX 1, pad 7: puts the Beat FX on the master output (CH SELECT MST). The mixer is shared, so each mixer control can only sit on one deck's pads: the left deck holds the Beat FX toolbox. |

## Mixer channel 1 (DJM-A9 strip)

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| CC 0x04 ch1 | `mx@djm-a9:ch0.trim` |  | TRIM knob (14-bit). 1:1 with the A9 TRIM. |
| CC 0x07 ch1 | `mx@djm-a9:ch0.eqHi` |  | EQ HI knob (14-bit). 1:1. |
| CC 0x0B ch1 | `mx@djm-a9:ch0.eqMid` |  | EQ MID knob (14-bit). The A9 has a 2-band mid (HI MID / LO MID); this drives the app's single mid control. |
| CC 0x0F ch1 | `mx@djm-a9:ch0.eqLo` |  | EQ LOW knob (14-bit). 1:1. |
| CC 0x13 ch1 | `mx@djm-a9:ch0.fader` |  | Channel fader (14-bit). 1:1. |
| CC 0x17 ch7 | `mx@djm-a9:ch0.color` | custom | the FLX4's per-channel FILTER knob drives the A9 COLOR knob (same job, different name). |
| Note 0x54 ch1 | `mx@djm-a9:ch0.cue` |  | Headphone CUE button for this channel. 1:1 with the A9 CUE. |

## Deck 2 (right) - transport

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x0B ch2 | `d1@cdj-3000x:play` |  | PLAY/PAUSE button. 1:1 with the CDJ PLAY/PAUSE. |
| Note 0x0C ch2 | `d1@cdj-3000x:cue` |  | CUE button. 1:1 with the CDJ CUE. |
| Note 0x58 ch2 | `d1@cdj-3000x:beatsync` |  | SYNC button. 1:1 with the CDJ BEAT SYNC. |
| Note 0x5C ch2 | `d1@cdj-3000x:master` | custom | the FLX4 has no MASTER button. SYNC long-press (note 0x5C) makes this deck the sync master, which is what the CDJ MASTER button does. |
| Note 0x60 ch2 | `d1@cdj-3000x:temporange` | custom | SHIFT+SYNC cycles the tempo range, standing in for the CDJ TEMPO RANGE button. |
| Note 0x0E ch2 | `d1@cdj-3000x:direction/sliprev` | custom | the FLX4 has no reverse lever. SHIFT+PLAY (Pioneer's reverse roll / censor) drives the CDJ slip-reverse lever position. |
| Note 0x48 ch2 | `d1@cdj-3000x:trackback` | custom | SHIFT+CUE jumps to the start of the track, matching the CDJ TRACK SEARCH \|<< button (the FLX4 has no track search buttons). |
| Note 0x68 ch2 | `d1@cdj-3000x:calldelete` | custom | the CDJ CALL/DELETE modifier. Hold SHIFT+CUE (note 0x68), let go of SHIFT, then tap a hot cue pad to delete that hot cue. Needed because SHIFT+pad is a different MIDI channel and can't reach the hot cue itself. Not yet verified on hardware. |

## Deck 2 (right) - loops

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x10 ch2 | `d1@cdj-3000x:loopin` |  | LOOP IN / 4 BEAT button. 1:1 with the CDJ LOOP IN. |
| Note 0x11 ch2 | `d1@cdj-3000x:loopout` |  | LOOP OUT button. 1:1 with the CDJ LOOP OUT. |
| Note 0x4D ch2 | `d1@cdj-3000x:reloop` |  | RELOOP/EXIT button. 1:1 with the CDJ RELOOP/EXIT. |
| Note 0x51 ch2 | `d1@cdj-3000x:beatloop4` | custom | CUE/LOOP CALL < halves the active loop. On a CDJ this is the 4 BEAT LOOP (1/2X) button; the FLX4 has neither, so its CALL arrows take the halve/double job. |
| Note 0x53 ch2 | `d1@cdj-3000x:beatloop8` | custom | CUE/LOOP CALL > doubles the active loop (CDJ 8 BEAT LOOP / 2X). |
| Note 0x3E ch2 | `d1@cdj-3000x:cuecall_l` | custom | SHIFT+CUE/LOOP CALL < jumps to the previous memory cue (CDJ CUE/LOOP CALL <). |
| Note 0x3D ch2 | `d1@cdj-3000x:cuecall_r` | custom | SHIFT+CUE/LOOP CALL > jumps to the next memory cue (CDJ CUE/LOOP CALL >). |

## Deck 2 (right) - jog and tempo

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| CC 0x22 ch2 | `d1@cdj-3000x:jogtop` | rel=binoff | Jog platter top while VINYL mode is on (scratch). Relative, binary-offset (centre 64). The vinyl-off platter message (cc 0x23) is not bound. |
| CC 0x21 ch2 | `d1@cdj-3000x:jog` | rel=binoff | Jog side ring (pitch bend). Relative, binary-offset (centre 64). |
| Note 0x36 ch2 | `d1@cdj-3000x:jog/touch` |  | Platter touch sensor. Tells B2B Studio the platter is held so the top wheel scratches instead of bends. |
| CC 0x00 ch2 | `d1@cdj-3000x:tempo` | invert=True | TEMPO fader, 14-bit (B2B Studio pairs the LSB on cc 0x20 by itself). Inverted so pushing the fader up speeds up, like the app's own learn does. |

## Deck 2 (right) - browse and load

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| CC 0x40 ch7 | `d1@cdj-3000x:rotary` | custom, rel=2c | BROWSE knob turn, relative two's complement. The FLX4 has one browse knob shared by both decks, so the same message is bound to both decks' rotary and both browsers scroll if both are open. |
| Note 0x41 ch7 | `d1@cdj-3000x:browse` | custom | BROWSE knob push, opens the browser on both decks (shared control, see rotary). |
| Note 0x42 ch7 | `d1@cdj-3000x:back` | custom | SHIFT+BROWSE push steps back out of a folder (CDJ BACK). Shared by both decks. |
| Note 0x47 ch7 | `d1@cdj-3000x:rotary/push` | custom | the FLX4 LOAD 2 button. The CDJ has no LOAD button; it loads by pushing the rotary, so LOAD is bound to the rotary push. |

## Deck 2 (right) - HOT CUE mode

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x00 ch10 | `d1@cdj-3000x:hotcue0` |  | Pad 1: hot cue A. 1:1 with CDJ HOT CUE A. |
| Note 0x01 ch10 | `d1@cdj-3000x:hotcue1` |  | Pad 2: hot cue B. 1:1 with CDJ HOT CUE B. |
| Note 0x02 ch10 | `d1@cdj-3000x:hotcue2` |  | Pad 3: hot cue C. 1:1 with CDJ HOT CUE C. |
| Note 0x03 ch10 | `d1@cdj-3000x:hotcue3` |  | Pad 4: hot cue D. 1:1 with CDJ HOT CUE D. |
| Note 0x04 ch10 | `d1@cdj-3000x:hotcue4` |  | Pad 5: hot cue E. 1:1 with CDJ HOT CUE E. |
| Note 0x05 ch10 | `d1@cdj-3000x:hotcue5` |  | Pad 6: hot cue F. 1:1 with CDJ HOT CUE F. |
| Note 0x06 ch10 | `d1@cdj-3000x:hotcue6` |  | Pad 7: hot cue G. 1:1 with CDJ HOT CUE G. |
| Note 0x07 ch10 | `d1@cdj-3000x:hotcue7` |  | Pad 8: hot cue H. 1:1 with CDJ HOT CUE H. |

## Deck 2 (right) - BEAT JUMP mode

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x20 ch10 | `d1@cdj-3000x:screen/jump=-1` | custom | pad 1 jumps 1 beat back. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x21 ch10 | `d1@cdj-3000x:screen/jump=1` | custom | pad 2 jumps 1 beat forward. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x22 ch10 | `d1@cdj-3000x:screen/jump=-2` | custom | pad 3 jumps 2 beats back. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x23 ch10 | `d1@cdj-3000x:screen/jump=2` | custom | pad 4 jumps 2 beats forward. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x24 ch10 | `d1@cdj-3000x:screen/jump=-4` | custom | pad 5 jumps 4 beats back. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x25 ch10 | `d1@cdj-3000x:screen/jump=4` | custom | pad 6 jumps 4 beats forward. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x26 ch10 | `d1@cdj-3000x:screen/jump=-8` | custom | pad 7 jumps 8 beats back. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x27 ch10 | `d1@cdj-3000x:screen/jump=8` | custom | pad 8 jumps 8 beats forward. Pads come in back/forward pairs of 1, 2, 4, 8. |
| Note 0x20 ch11 | `d1@cdj-3000x:screen/jump=-16` | custom | SHIFT+pad 1 jumps 16 beats back (bigger jumps and a half beat). |
| Note 0x21 ch11 | `d1@cdj-3000x:screen/jump=16` | custom | SHIFT+pad 2 jumps 16 beats forward (bigger jumps and a half beat). |
| Note 0x22 ch11 | `d1@cdj-3000x:screen/jump=-32` | custom | SHIFT+pad 3 jumps 32 beats back (bigger jumps and a half beat). |
| Note 0x23 ch11 | `d1@cdj-3000x:screen/jump=32` | custom | SHIFT+pad 4 jumps 32 beats forward (bigger jumps and a half beat). |
| Note 0x24 ch11 | `d1@cdj-3000x:screen/jump=-64` | custom | SHIFT+pad 5 jumps 64 beats back (bigger jumps and a half beat). |
| Note 0x25 ch11 | `d1@cdj-3000x:screen/jump=64` | custom | SHIFT+pad 6 jumps 64 beats forward (bigger jumps and a half beat). |
| Note 0x26 ch11 | `d1@cdj-3000x:screen/jump=-0.5` | custom | SHIFT+pad 7 jumps 0.5 beats back (bigger jumps and a half beat). |
| Note 0x27 ch11 | `d1@cdj-3000x:screen/jump=0.5` | custom | SHIFT+pad 8 jumps 0.5 beats forward (bigger jumps and a half beat). |

## Deck 2 (right) - BEAT LOOP mode

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x60 ch10 | `d1@cdj-3000x:screen/loop=0.25` | custom | pad 1 sets a 0.25-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x61 ch10 | `d1@cdj-3000x:screen/loop=0.5` | custom | pad 2 sets a 0.5-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x62 ch10 | `d1@cdj-3000x:screen/loop=1` | custom | pad 3 sets a 1-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x63 ch10 | `d1@cdj-3000x:screen/loop=2` | custom | pad 4 sets a 2-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x64 ch10 | `d1@cdj-3000x:screen/loop=4` | custom | pad 5 sets a 4-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x65 ch10 | `d1@cdj-3000x:screen/loop=8` | custom | pad 6 sets a 8-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x66 ch10 | `d1@cdj-3000x:screen/loop=16` | custom | pad 7 sets a 16-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |
| Note 0x67 ch10 | `d1@cdj-3000x:screen/loop=32` | custom | pad 8 sets a 32-beat loop, or resizes the active loop. B2B Studio takes any loop length through the CDJ's screen target. |

## Deck 2 (right) - PAD FX 2 mode (odd loop sizes)

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x50 ch10 | `d1@cdj-3000x:screen/loop=0.0625` | custom | pad 1 sets a 0.0625-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x51 ch10 | `d1@cdj-3000x:screen/loop=0.125` | custom | pad 2 sets a 0.125-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x52 ch10 | `d1@cdj-3000x:screen/loop=0.3333333333333333` | custom | pad 3 sets a 0.333333-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x53 ch10 | `d1@cdj-3000x:screen/loop=0.75` | custom | pad 4 sets a 0.75-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x54 ch10 | `d1@cdj-3000x:screen/loop=1.5` | custom | pad 5 sets a 1.5-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x55 ch10 | `d1@cdj-3000x:screen/loop=3` | custom | pad 6 sets a 3-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x56 ch10 | `d1@cdj-3000x:screen/loop=6` | custom | pad 7 sets a 6-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |
| Note 0x57 ch10 | `d1@cdj-3000x:screen/loop=9` | custom | pad 8 sets a 9-beat loop, one of the odd sizes on the CDJ-3000's loop screen. |

## Deck 2 (right) - KEY SHIFT mode

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x70 ch10 | `d1@cdj-3000x:screen/key=-1` | custom | pad 1 shifts the key down 1 semitone. |
| Note 0x71 ch10 | `d1@cdj-3000x:screen/key=1` | custom | pad 2 shifts the key up 1 semitone. |
| Note 0x72 ch10 | `d1@cdj-3000x:screen/key=-2` | custom | pad 3 shifts the key down 2 semitones. |
| Note 0x73 ch10 | `d1@cdj-3000x:screen/key=2` | custom | pad 4 shifts the key up 2 semitones. |
| Note 0x74 ch10 | `d1@cdj-3000x:screen/key=-3` | custom | pad 5 shifts the key down 3 semitones. |
| Note 0x75 ch10 | `d1@cdj-3000x:screen/key=3` | custom | pad 6 shifts the key up 3 semitones. |
| Note 0x76 ch10 | `d1@cdj-3000x:screen/key=0` | custom | pad 7 resets the key. |
| Note 0x77 ch10 | `d1@cdj-3000x:keysync` | custom | pad 8 matches the key to the other deck, or resets it (CDJ KEY SYNC). |

## Deck 2 (right) - SAMPLER mode (deck utilities)

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x30 ch10 | `d1@cdj-3000x:memory` | custom | pad 1 saves a memory cue (or the active loop), the CDJ MEMORY button. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x31 ch10 | `d1@cdj-3000x:delete` | custom | pad 2 deletes the memory cue you are on, the CDJ DELETE button. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x32 ch10 | `d1@cdj-3000x:slip` | custom | pad 3 toggles SLIP. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x33 ch10 | `d1@cdj-3000x:quantize` | custom | pad 4 toggles QUANTIZE. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x34 ch10 | `d1@cdj-3000x:mastertempo` | custom | pad 5 toggles MASTER TEMPO (key lock). The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x35 ch10 | `d1@cdj-3000x:temporeset` | custom | pad 6 resets the tempo fader to 0%. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x36 ch10 | `d1@cdj-3000x:vinylmode` | custom | pad 7 switches the jog to VINYL mode. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x37 ch10 | `d1@cdj-3000x:cdjmode` | custom | pad 8 switches the jog to CDJ mode. The FLX4 has no sampler here, so these pads carry CDJ buttons it lacks. |
| Note 0x30 ch11 | `d1@cdj-3000x:trackfwd` | custom | SHIFT+pad 1: next track (CDJ TRACK SEARCH >>\|). |
| Note 0x31 ch11 | `d1@cdj-3000x:searchback` | custom | SHIFT+pad 2: fast-scan back (CDJ SEARCH <<). |
| Note 0x32 ch11 | `d1@cdj-3000x:searchfwd` | custom | SHIFT+pad 3: fast-scan forward (CDJ SEARCH >>). |
| Note 0x33 ch11 | `d1@cdj-3000x:nudgeback` | custom | SHIFT+pad 4: nudge the tempo down (CDJ NUDGE -). |
| Note 0x34 ch11 | `d1@cdj-3000x:nudgefwd` | custom | SHIFT+pad 5: nudge the tempo up (CDJ NUDGE +). |
| Note 0x35 ch11 | `d1@cdj-3000x:direction/rev` | custom | SHIFT+pad 6: reverse playback while held (CDJ reverse lever). |
| Note 0x36 ch11 | `d1@cdj-3000x:screen/time` | custom | SHIFT+pad 7: switches the time display between elapsed and remaining. |

## Deck 2 (right) - PAD FX 1 mode (Sound Color FX)

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x10 ch10 | `mx@djm-a9:scfx.space` | custom | right deck PAD FX 1, pad 1: Sound Color FX type SPACE. The mixer is shared, so each mixer control can only sit on one deck's pads: the right deck holds the Color FX bank. |
| Note 0x11 ch10 | `mx@djm-a9:scfx.dubecho` | custom | right deck PAD FX 1, pad 2: Sound Color FX type DUB ECHO. The mixer is shared, so each mixer control can only sit on one deck's pads: the right deck holds the Color FX bank. |
| Note 0x12 ch10 | `mx@djm-a9:scfx.crush` | custom | right deck PAD FX 1, pad 3: Sound Color FX type CRUSH. The mixer is shared, so each mixer control can only sit on one deck's pads: the right deck holds the Color FX bank. |
| Note 0x13 ch10 | `mx@djm-a9:scfx.sweep` | custom | right deck PAD FX 1, pad 4: Sound Color FX type SWEEP. The mixer is shared, so each mixer control can only sit on one deck's pads: the right deck holds the Color FX bank. |
| Note 0x14 ch10 | `mx@djm-a9:scfx.noise` | custom | right deck PAD FX 1, pad 5: Sound Color FX type NOISE. The mixer is shared, so each mixer control can only sit on one deck's pads: the right deck holds the Color FX bank. |
| Note 0x15 ch10 | `mx@djm-a9:scfx.filter` | custom | right deck PAD FX 1, pad 6: Sound Color FX type FILTER. The mixer is shared, so each mixer control can only sit on one deck's pads: the right deck holds the Color FX bank. |
| Note 0x16 ch10 | `mx@djm-a9:scfx.lockLamp` | custom | right deck PAD FX 1, pad 7: Sound Color FX type CENTER LOCK. The mixer is shared, so each mixer control can only sit on one deck's pads: the right deck holds the Color FX bank. |

## Mixer channel 2 (DJM-A9 strip)

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| CC 0x04 ch2 | `mx@djm-a9:ch1.trim` |  | TRIM knob (14-bit). 1:1 with the A9 TRIM. |
| CC 0x07 ch2 | `mx@djm-a9:ch1.eqHi` |  | EQ HI knob (14-bit). 1:1. |
| CC 0x0B ch2 | `mx@djm-a9:ch1.eqMid` |  | EQ MID knob (14-bit). The A9 has a 2-band mid (HI MID / LO MID); this drives the app's single mid control. |
| CC 0x0F ch2 | `mx@djm-a9:ch1.eqLo` |  | EQ LOW knob (14-bit). 1:1. |
| CC 0x13 ch2 | `mx@djm-a9:ch1.fader` |  | Channel fader (14-bit). 1:1. |
| CC 0x18 ch7 | `mx@djm-a9:ch1.color` | custom | the FLX4's per-channel FILTER knob drives the A9 COLOR knob (same job, different name). |
| Note 0x54 ch2 | `mx@djm-a9:ch1.cue` |  | Headphone CUE button for this channel. 1:1 with the A9 CUE. |

## Mixer - shared

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| CC 0x1F ch7 | `mx@djm-a9:xf.pos` |  | CROSSFADER (14-bit). 1:1. |
| CC 0x0C ch7 | `mx@djm-a9:hpa.mix` | custom | HEADPHONES MIXING knob drives the A9 phones A CUE/MIX. The A9 has a second headphone section that the FLX4 has no controls for. |
| CC 0x0D ch7 | `mx@djm-a9:hpa.level` | custom | HEADPHONES LEVEL knob drives the A9 phones A level (see above). |

## Beat FX

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| CC 0x02 ch5 | `mx@djm-a9:fx.depth` |  | BEAT FX LEVEL/DEPTH knob. 1:1 with the A9 LEVEL/DEPTH. |
| Note 0x47 ch5 | `mx@djm-a9:fx.onoff` |  | BEAT FX ON/OFF. Only the channel-4 message is bound; with the CH slider on CH2 the FLX4 may send channel 5 instead, which is not bound (one control can only have one source). |
| Note 0x4A ch5 | `mx@djm-a9:fx.beatl` |  | BEAT FX BEAT < (shorten the effect beat). 1:1 with the A9 BEAT <. |
| Note 0x4B ch5 | `mx@djm-a9:fx.beatr` |  | BEAT FX BEAT > (lengthen the effect beat). 1:1 with the A9 BEAT >. |
| Note 0x10 ch5 | `mx@djm-a9:fx.ch0` |  | BEAT FX CH SELECT slider at CH1 puts mixer channel 1 in the effect (exclusive). 1:1 with the A9 CH SELECT 1. |
| Note 0x11 ch6 | `mx@djm-a9:fx.ch1` |  | BEAT FX CH SELECT slider at CH2 puts mixer channel 2 in the effect (exclusive). The slider's third position is not bound because its message is unknown. |
| Note 0x63 ch5 | `mx@djm-a9:fx.tap` | custom | the FX SELECT button taps the effect tempo (A9 TAP). The A9 FX SELECT is a knob that takes an absolute position, so a button can't step through effects; see fx.select. |
| Note 0x64 ch5 | `mx@djm-a9:fx.autotap` | custom | SHIFT+FX SELECT toggles AUTO/TAP (A9 AUTO/TAP). |
| CC 0x64 ch7 | `mx@djm-a9:fx.select` | custom, rel=2c, sens=5 | SHIFT+BROWSE turn picks the effect, because the FLX4 has no FX select knob. Relative, sensitivity 5 so one click is about one of the 14 effects. |
