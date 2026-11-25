# B2B Studio MIDI preset format

B2B Studio publishes no specification for its MIDI presets. This page documents what the presets in this repository rely on. It comes from reading the app's web client and from testing in November 2026, so **it can go out of date at any time**. If something here no longer matches the app, [open an issue](../../../issues).

To double-check a target ID, bind the control with MIDI Learn in B2B Studio, export the preset, and read the key it produced.

## File layout

```json
{
  "app": "B2B Studio",
  "kind": "midi-preset",
  "version": 1,
  "name": "My controller",
  "bindings": {
    "d0@cdj-3000x:play": { "src": "My Controller|note|0|11" },
    "mx@djm-a9:ch0.fader": { "src": "My Controller|cc|0|19" }
  }
}
```

- `kind` must be `midi-preset`. The app ignores other top-level keys, which is why the presets here carry a `_readme` block.
- Each binding is `target: { src, ...options }`. The app reads only `src`, `rel`, `invert`, `sens` and `pos`, so a `doc` string per binding is safe. The app drops those strings when you re-export from it.
- The code enforces these limits: 2000 bindings per preset, target keys up to 120 characters, `src` up to 240 characters, files up to 1 MB, and five presets in total.

## `src`: the message source

```
<MIDI input name>|<kind>|<channel>|<number>
```

| Part | Values |
|---|---|
| input name | The MIDI input's name exactly as the app lists it, for example `DDJ-FLX4`. |
| kind | `note`, `cc`, or `pb` (pitch bend, where the number is always `0`). |
| channel | Zero-based. MIDI channel 1 is `0`. |
| number | Note or controller number, 0 to 127. |

Behaviour to know:

- A note-on with velocity above 0 is a press. A note-off, or a note-on with velocity 0, is a release.
- For a 14-bit control, where the controller sends CC *n* (0 to 31) as the coarse byte and CC *n*+32 as the fine byte, bind only CC *n*. The app pairs the fine byte itself.
- Several targets can share one `src`. A target takes only one `src`.

## Options

| Option | Meaning |
|---|---|
| `rel` | Marks an endless encoder or jog wheel. `"2c"` is two's complement (1 is +1, 127 is -1), `"binoff"` is binary offset (64 is centre), `"signed"` uses a sign bit. `true` means `"2c"`. |
| `invert` | Reverses the direction. Tempo faders use it. |
| `sens` | Multiplier for relative controls, 0.05 to 8. One step moves a knob by 1/64 of its range, so a knob that selects among 14 effects needs about 5. |
| `pos` | The app accepts it, and its own MIDI Learn sets it for some wheels. Hand-written presets do not need it. |

## Targets

```
<unit>@<spec>:<control id>
```

- **Decks:** unit `d0` to `d3`, spec `cdj-3000x`. The number is the deck index, so `d0` is Deck 1.
- **Mixer:** unit `mx`, spec `djm-a9`.
- A control id can carry a `/sub` part, for example `jog/touch` or `rotary/push`.

### CDJ-3000X (`dN@cdj-3000x:`)

| Group | Control ids |
|---|---|
| Transport | `play`, `cue`, `beatsync`, `master`, `keysync`, `quantize`, `slip` |
| Tempo | `tempo` (fader), `temporange`, `temporeset`, `mastertempo` |
| Hot cues | `hotcue0` to `hotcue7` (A to H), `calldelete` (hold, then tap a hot cue to delete it) |
| Loops | `loopin`, `loopout`, `reloop`, `beatloop4`, `beatloop8` (the CDJ's 4 BEAT / 1/2X and 8 BEAT / 2X buttons), `beatjumpl`, `beatjumpr` |
| Memory cues | `memory`, `delete`, `cuecall_l`, `cuecall_r` |
| Jog | `jog` (side ring), `jogtop` (platter top), `jog/touch`, `jogmode`, `vinylmode`, `cdjmode`, `jogfeel`, `vinylspeed` |
| Direction | `direction`, `direction/rev`, `direction/sliprev` |
| Search and nudge | `trackback`, `trackfwd`, `searchback`, `searchfwd`, `nudgeback`, `nudgefwd` |
| Browse | `rotary` (relative), `rotary/push`, `browse`, `back`, `source`, `taglist`, `playlist`, `searchbtn`, `menu`, `tagtrack`, `trackfilter`, `shortcut`, `usb1`, `usb2`, `usb1stop`, `usb2stop` |

### Screen targets

These targets take a number after `=`. They match the CDJ's on-screen shortcuts rather than physical buttons, and the app accepts any number, including ones its own screen never offers. Bind them to a note.

| Target | Does |
|---|---|
| `screen/loop=N` | Sets an N-beat loop, or resizes the active one. |
| `screen/jump=N` | Jumps N beats. A negative number jumps back. |
| `screen/key=N` | Shifts the key by N semitones. `screen/key=0` resets it. |
| `screen/time` | Toggles elapsed and remaining time. |
| `screen/needle` | Sets the absolute position along the track. Bind it to a CC. |

### DJM-A9 (`mx@djm-a9:`)

Channel controls use `ch0` to `ch3` (mixer channels 1 to 4): `ch0.trim`, `ch0.eqHi`, `ch0.eqMid`, `ch0.eqLo`, `ch0.color`, `ch0.fader`, `ch0.cue`, `ch0.cueB`, `ch0.xfassign`, `ch0.input`.

| Group | Control ids |
|---|---|
| Master and monitor | `xf.pos` (crossfader), `master.level`, `master.cue`, `booth.level`, `hpa.mix`, `hpa.level`, `hpb.mix`, `hpb.level` |
| Beat FX | `fx.select` (absolute knob, 14 effects), `fx.onoff`, `fx.depth`, `fx.time`, `fx.beatl`, `fx.beatr`, `fx.tap`, `fx.autotap`, `fx.quantize`, `fx.freqLow`, `fx.freqMid`, `fx.freqHi`, `fx.ch0` to `fx.ch3`, `fx.cfa`, `fx.cfb`, `fx.mst` |
| Sound Color FX | `scfx.space`, `scfx.dubecho`, `scfx.crush`, `scfx.sweep`, `scfx.noise`, `scfx.filter`, `scfx.lockLamp`, `scfx.param` |
| Microphone | `mic1.level`, `mic2.level`, `mic.eqHi`, `mic.eqLow`, `mic.on`, `mic.talkover`, `micfx.*`, `micrev.*` |

The app contains other mixers and players. To list their ids, learn a control, export the preset and read the key.

## Controller LEDs

B2B Studio can send lamp messages back to a controller, but only for developer accounts at the time of writing, and no preset can switch that on. For that reason the bridge in `controllers/ddj-flx4` lights the FLX4 itself.
