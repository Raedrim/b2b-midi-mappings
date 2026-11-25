# mapping.yaml format

One file describes each controller: `controllers/<slug>/mapping.yaml`. `python tools/b2bmap.py build` turns it into importable presets and mapping tables, and `check` validates it. You write no code. For a worked example, read [the DDJ-FLX4 mapping](../controllers/ddj-flx4/mapping.yaml).

To start fast, run `python tools/b2bmap.py new` and then `learn`, which writes most of this file as you press controls. If you already have a preset exported from B2B Studio, run `python tools/b2bmap.py import <file> <slug>` instead. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## A minimal file

```yaml
name: "Demo Pad"

profiles:
  default:
    title: "Demo Pad"
    port: "Demo Pad MIDI"     # the MIDI input name, exactly as B2B Studio lists it
    docs: true                # also write docs/MAPPING-default.md

# Keep 'bindings' as the last key: `learn` appends to the end of the file.
bindings:
  - target: "d0@cdj-3000x:play"
    msg: "note 0 0x0B"
    doc: "PLAY/PAUSE button. 1:1 with the CDJ PLAY/PAUSE."
  - target: "mx@djm-a9:ch0.fader"
    msg: "cc 0 0x13"
    doc: "Channel fader. 1:1."
```

This produces `presets/demo-pad-default.b2bmidi.json` and `docs/MAPPING-default.md`.

## Top-level keys

| Key | Required | Meaning |
|---|---|---|
| `name` | yes | Controller name, used in the docs. |
| `profiles` | yes | One or more variants of the preset. Most controllers need one. |
| `bindings` | yes | The mappings. Must be the last key. |
| `decks` | no | Variables for per-deck loops, see below. |
| `readme` | no | Lines for the `_readme` block at the top of every preset. Accepts `{port}`, `{profile}`, `{title}` and `{name}`. |
| `wake` | no | A SysEx message the controller needs before it talks (`sysex: "00 40 05 ..."`, `interval: 2`). `learn` sends it so the controller responds. |

### Profiles

Each profile becomes one preset file, `presets/<slug>-<profile>.b2bmidi.json`.

| Key | Meaning |
|---|---|
| `port` | Required. The MIDI input name. Every binding's source starts with it. |
| `title` | The preset name B2B Studio shows on import. |
| `docs` | `true` writes `docs/MAPPING-<profile>.md`. |
| `tags` | Names a binding can list in `only` to target several profiles at once. |
| `readme` | Extra `_readme` lines for this profile. |

Use several profiles when you use the same controller in different ways. The DDJ-FLX4 has a `direct` profile and two `bridge` profiles that differ only in the MIDI port name.

## A binding

```yaml
- target: "d0@cdj-3000x:hotcue3"
  msg: "note 7 3"
  doc: "Pad 4: hot cue D. 1:1 with CDJ HOT CUE D."
```

| Key | Meaning |
|---|---|
| `target` | The B2B Studio control to drive. See [B2B-STUDIO-MIDI.md](B2B-STUDIO-MIDI.md) or run `python tools/b2bmap.py targets <words>`. |
| `msg` | The controller's message: `note <channel> <number>`, `cc <channel> <number>` or `pb <channel>`. Channels start at 0. Numbers may be decimal or hex, and may add up: `note 7 0x20+3`. |
| `doc` | One line saying what the binding does. Use it when the controller has a matching control. |
| `why` | Use this instead of `doc` when you made a judgement call: the controller has no matching control, or you repurposed one. Give the reason. The docs flag it **custom**. |
| `opts` | Optional. `rel: 2c` (or `binoff`, `signed`) for endless encoders and jog wheels, `invert: true`, `sens: 5`. See [B2B-STUDIO-MIDI.md](B2B-STUDIO-MIDI.md#options). |
| `only` | Optional. A profile name or tag, or a list of them. The binding applies to those profiles only. |
| `share` | Optional. Set `true` when you deliberately bind one control to several targets, such as one browse knob serving both decks. |

Give exactly one of `doc` and `why`.

`check` enforces these rules:

- Every target exists in B2B Studio (`tools/targets.json`).
- Each profile binds a target once.
- A controller message drives one target, unless `share: true` is set.
- Channels run from 0 to 15 and numbers from 0 to 127.
- Unknown keys fail the check, so typos cannot slip through.

## Sections

A `section` line starts a heading in the generated docs and covers the bindings after it.

```yaml
- section: "Transport"
- target: ...
```

## Repeating yourself less

Two decks, eight pads or a list of values need no copy and paste. Nothing in these constructs is evaluated as code.

### `for: decks`

Define variables per deck, then repeat a block for each:

```yaml
decks:
  - {d: 0, n: 1, ch: 0, pad: 7}
  - {d: 1, n: 2, ch: 1, pad: 9}

bindings:
  - for: decks
    bindings:
      - section: "Deck {n} - transport"
      - target: "d{d}@cdj-3000x:play"
        msg: "note {ch} 0x0B"
        doc: "PLAY/PAUSE button."
```

`{name}` becomes the variable's value, and `{name:spec}` applies a Python format specification (`{v:g}` shortens `0.3333333333333333` to `0.333333`). Any other braces cause an error.

Inside a `for` block, a group with `only_decks` applies to some decks only:

```yaml
      - only_decks: [0]
        bindings:
          - target: ...
```

### `repeat` and `items`

`repeat: 8` repeats one binding eight times and supplies `{i}` (0 to 7), `{i1}` (1 to 8) and `{letter}` (A to H):

```yaml
- target: "d{d}@cdj-3000x:hotcue{i}"
  msg: "note {pad} {i}"
  repeat: 8
  doc: "Pad {i1}: hot cue {letter}."
```

`items` repeats a binding once per entry. An entry can be a plain value, available as `{v}`, or a small table whose keys become variables:

```yaml
- target: "d{d}@cdj-3000x:screen/loop={v}"
  msg: "note {pad} 0x60+{i}"
  items: [0.25, 0.5, 1, 2, 4, 8, 16, 32]
  why: "Pad {i1} sets a {v}-beat loop."
```

```yaml
  items:
    - {c: memory, t: "saves a memory cue"}
    - {c: slip, t: "toggles SLIP"}
  target: "d{d}@cdj-3000x:{c}"
  why: "Pad {i1} {t}."
```

## Generated files

| File | Source |
|---|---|
| `presets/<slug>-<profile>.b2bmidi.json` | Every profile. Import it into B2B Studio. |
| `docs/MAPPING-<profile>.md` | Profiles with `docs: true`. |

Commit the generated files with `mapping.yaml`. CI regenerates them and fails on any difference, so a stale file cannot merge.
