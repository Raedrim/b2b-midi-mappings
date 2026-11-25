# Mapping reference - FLX4 (direct)

Generated from `mapping.yaml` by `tools/b2bmap.py`; do not edit by hand. MIDI input: `DDJ-FLX4`.

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

## Deck 1 (left) - pads (controller stays in HOT CUE mode)

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
| Note 0x00 ch9 | `d0@cdj-3000x:screen/loop=1` | custom | SHIFT+pad 1 sets a 1-beat loop (resizes it if one is already active). Stands in for the FLX4's BEAT LOOP pad mode, which can't be reached without the bridge. |
| Note 0x01 ch9 | `d0@cdj-3000x:screen/loop=2` | custom | SHIFT+pad 2 sets a 2-beat loop (resizes it if one is already active). Stands in for the FLX4's BEAT LOOP pad mode, which can't be reached without the bridge. |
| Note 0x02 ch9 | `d0@cdj-3000x:screen/loop=4` | custom | SHIFT+pad 3 sets a 4-beat loop (resizes it if one is already active). Stands in for the FLX4's BEAT LOOP pad mode, which can't be reached without the bridge. |
| Note 0x03 ch9 | `d0@cdj-3000x:screen/loop=8` | custom | SHIFT+pad 4 sets a 8-beat loop (resizes it if one is already active). Stands in for the FLX4's BEAT LOOP pad mode, which can't be reached without the bridge. |
| Note 0x04 ch9 | `d0@cdj-3000x:screen/jump=-4` | custom | SHIFT+pad 5 jumps 4 beats back. Stands in for the FLX4's BEAT JUMP pad mode, which can't be reached without the bridge. |
| Note 0x05 ch9 | `d0@cdj-3000x:screen/jump=4` | custom | SHIFT+pad 6 jumps 4 beats forward. Stands in for the FLX4's BEAT JUMP pad mode, which can't be reached without the bridge. |
| Note 0x06 ch9 | `d0@cdj-3000x:screen/jump=-16` | custom | SHIFT+pad 7 jumps 16 beats back. Stands in for the FLX4's BEAT JUMP pad mode, which can't be reached without the bridge. |
| Note 0x07 ch9 | `d0@cdj-3000x:screen/jump=16` | custom | SHIFT+pad 8 jumps 16 beats forward. Stands in for the FLX4's BEAT JUMP pad mode, which can't be reached without the bridge. |

## Deck 1 (left) - pad-mode buttons reused as plain buttons

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x1B ch1 | `d0@cdj-3000x:memory` | custom | HOT CUE mode button saves a memory cue (or the active loop). Without the bridge the pad modes can't be switched, but the buttons still send a note, so they're free for the CDJ MEMORY job. |
| Note 0x1E ch1 | `d0@cdj-3000x:slip` | custom | PAD FX 1 mode button toggles SLIP (CDJ SLIP). |
| Note 0x20 ch1 | `d0@cdj-3000x:beatjumpl` | custom | BEAT JUMP mode button jumps back by the app's current beat-jump size (CDJ BEAT JUMP <). |
| Note 0x22 ch1 | `d0@cdj-3000x:beatjumpr` | custom | SAMPLER mode button jumps forward by the app's current beat-jump size (CDJ BEAT JUMP >). |
| Note 0x69 ch1 | `d0@cdj-3000x:screen/key=-1` | custom | SHIFT+HOT CUE mode button (KEYBOARD) shifts the key down one semitone. |
| Note 0x6B ch1 | `d0@cdj-3000x:screen/key=1` | custom | SHIFT+PAD FX 1 mode button (PAD FX 2) shifts the key up one semitone. |
| Note 0x6D ch1 | `d0@cdj-3000x:quantize` | custom | SHIFT+BEAT JUMP mode button (BEAT LOOP) toggles QUANTIZE (CDJ QUANTIZE). |
| Note 0x6F ch1 | `d0@cdj-3000x:keysync` | custom | SHIFT+SAMPLER mode button (KEY SHIFT) matches the key to the other deck, or resets it (CDJ KEY SYNC). |

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

## Deck 2 (right) - pads (controller stays in HOT CUE mode)

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
| Note 0x00 ch11 | `d1@cdj-3000x:screen/loop=1` | custom | SHIFT+pad 1 sets a 1-beat loop (resizes it if one is already active). Stands in for the FLX4's BEAT LOOP pad mode, which can't be reached without the bridge. |
| Note 0x01 ch11 | `d1@cdj-3000x:screen/loop=2` | custom | SHIFT+pad 2 sets a 2-beat loop (resizes it if one is already active). Stands in for the FLX4's BEAT LOOP pad mode, which can't be reached without the bridge. |
| Note 0x02 ch11 | `d1@cdj-3000x:screen/loop=4` | custom | SHIFT+pad 3 sets a 4-beat loop (resizes it if one is already active). Stands in for the FLX4's BEAT LOOP pad mode, which can't be reached without the bridge. |
| Note 0x03 ch11 | `d1@cdj-3000x:screen/loop=8` | custom | SHIFT+pad 4 sets a 8-beat loop (resizes it if one is already active). Stands in for the FLX4's BEAT LOOP pad mode, which can't be reached without the bridge. |
| Note 0x04 ch11 | `d1@cdj-3000x:screen/jump=-4` | custom | SHIFT+pad 5 jumps 4 beats back. Stands in for the FLX4's BEAT JUMP pad mode, which can't be reached without the bridge. |
| Note 0x05 ch11 | `d1@cdj-3000x:screen/jump=4` | custom | SHIFT+pad 6 jumps 4 beats forward. Stands in for the FLX4's BEAT JUMP pad mode, which can't be reached without the bridge. |
| Note 0x06 ch11 | `d1@cdj-3000x:screen/jump=-16` | custom | SHIFT+pad 7 jumps 16 beats back. Stands in for the FLX4's BEAT JUMP pad mode, which can't be reached without the bridge. |
| Note 0x07 ch11 | `d1@cdj-3000x:screen/jump=16` | custom | SHIFT+pad 8 jumps 16 beats forward. Stands in for the FLX4's BEAT JUMP pad mode, which can't be reached without the bridge. |

## Deck 2 (right) - pad-mode buttons reused as plain buttons

| Controller message | B2B Studio target | Notes | What it does |
|---|---|---|---|
| Note 0x1B ch2 | `d1@cdj-3000x:memory` | custom | HOT CUE mode button saves a memory cue (or the active loop). Without the bridge the pad modes can't be switched, but the buttons still send a note, so they're free for the CDJ MEMORY job. |
| Note 0x1E ch2 | `d1@cdj-3000x:slip` | custom | PAD FX 1 mode button toggles SLIP (CDJ SLIP). |
| Note 0x20 ch2 | `d1@cdj-3000x:beatjumpl` | custom | BEAT JUMP mode button jumps back by the app's current beat-jump size (CDJ BEAT JUMP <). |
| Note 0x22 ch2 | `d1@cdj-3000x:beatjumpr` | custom | SAMPLER mode button jumps forward by the app's current beat-jump size (CDJ BEAT JUMP >). |
| Note 0x69 ch2 | `d1@cdj-3000x:screen/key=-1` | custom | SHIFT+HOT CUE mode button (KEYBOARD) shifts the key down one semitone. |
| Note 0x6B ch2 | `d1@cdj-3000x:screen/key=1` | custom | SHIFT+PAD FX 1 mode button (PAD FX 2) shifts the key up one semitone. |
| Note 0x6D ch2 | `d1@cdj-3000x:quantize` | custom | SHIFT+BEAT JUMP mode button (BEAT LOOP) toggles QUANTIZE (CDJ QUANTIZE). |
| Note 0x6F ch2 | `d1@cdj-3000x:keysync` | custom | SHIFT+SAMPLER mode button (KEY SHIFT) matches the key to the other deck, or resets it (CDJ KEY SYNC). |

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
