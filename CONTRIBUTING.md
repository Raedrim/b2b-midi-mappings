# Contributing

Thanks for helping. A new controller mapping takes one YAML file and a short README, and the tools generate the rest. You write no code.

B2B Studio has no official MIDI documentation and can change at any time. The most useful contributions state what you tested.

## Reporting a problem

[Open an issue](../../issues) with the controller, your operating system, the B2B Studio version, the preset and script you used, what you expected and what happened. If a mapping broke after a B2B Studio update, say so, because a control ID may have changed.

A weekly check opens an issue labelled `b2b-drift` when B2B Studio removes a control. Check there first.

## Adding a controller

### Set up once

```bash
git clone https://github.com/Raedrim/b2b-midi-mappings.git
cd b2b-midi-mappings
pip install -r tools/requirements.txt
```

You need Python 3.9 or newer. The steps are the same on Windows and macOS.

### Already mapped it in B2B Studio?

If you built your mapping with B2B Studio's own MIDI Learn, you have most of the work done. Export the preset from the app and import it here:

```bash
python tools/b2bmap.py import my-export.json my-controller --name "Vendor Model"
```

The tool reads every binding, works out the options (endless encoders, inverted faders, sensitivity), marks controls that share one message, and writes `controllers/my-controller/mapping.yaml` plus a README stub. It also drafts a description for every control it recognises, such as `Deck 1: PLAY / PAUSE.` or `Deck 2: sets a 16-beat loop, or resizes the active one.` Those say what the control does in B2B Studio. Read through them and add the physical control where it helps, for example "Jog wheel". Anything it cannot name keeps a `TODO` description, and `check` fails until you replace it with a `doc:` or `why:` line. Pass `--no-autodoc` to get a `TODO` on every binding instead. If the export reads from several MIDI inputs, add `--port "name"` to pick one. Then run `build` and `check` as below.

No Python? Open an issue with the exported file attached, and a maintainer can run the import for you.

### Three steps

```bash
python tools/b2bmap.py new my-controller --name "Vendor Model" --port "MIDI input name"
python tools/b2bmap.py learn my-controller
python tools/b2bmap.py check
```

1. **`new`** creates `controllers/my-controller/` with a starter `mapping.yaml` and a README to fill in. Give the MIDI input name exactly as B2B Studio lists it. To find it, run `python -c "import mido; print(mido.get_input_names())"`.
2. **`learn`** listens to your controller. Press or turn a control, search for the B2B Studio control it should drive (type a few words like `crossfader` or `hot cue`), and answer one question. It appends the binding to `mapping.yaml`, detects endless encoders, and undoes the write if the result would be invalid. Close B2B Studio first, because Windows lets only one program read a MIDI device.
3. **`check`** validates everything. CI runs the same command.

When `check` passes, run `python tools/b2bmap.py build` to write the preset and the mapping table, and commit them next to `mapping.yaml`. CI rebuilds them and fails on any difference.

You can also edit `mapping.yaml` by hand to improve a description or to loop over two decks and eight pads. [docs/MAPPING-FORMAT.md](docs/MAPPING-FORMAT.md) describes the format, and the DDJ-FLX4 file is a full example. To find a target without the app, run `python tools/b2bmap.py targets <words>`.

### Doc or why

Every binding explains itself. Use `doc:` when the controller has a matching control. Use `why:` when you made a judgement call, such as mapping to a CDJ or mixer control your hardware lacks, moving a function to a Shift layer, or driving a differently named control with a knob. Give the reason in one sentence so the next person can decide whether they agree. The generated tables mark these rows **custom**.

### The README

Fill in the generated `controllers/my-controller/README.md` with what the preset gives you, any setup beyond importing it, what you verified on hardware and on which operating system, and known limitations. If the controller needs a wake-up message or host messages to switch modes or light up, document them in `docs/PROTOCOL.md` and put the wake-up message under `wake:` in `mapping.yaml` so `learn` can send it. Many B2B Studio users run macOS, so say which systems you tested.

### Scripts

Most controllers need only the preset. If yours needs a script, put it in the controller's folder, keep it cross-platform where possible, and add a launcher if a double-click helps. `controllers/ddj-flx4` shows one approach.

## YAML style

CI runs `yamllint` on every YAML file, including each `mapping.yaml`, with the rules in `.yamllint.yml`: two-space indents, no trailing spaces, no stray alignment padding. `.editorconfig` sets the same basics in most editors. To check before you push:

```bash
pip install yamllint
yamllint --strict .
```

## Fixing or changing a mapping

Edit `mapping.yaml`, run `build` and `check`, and commit the regenerated files. Never edit `presets/` or the `MAPPING-*.md` tables by hand, because the next build overwrites them.

If `check` reports an unknown control ID that the app does have, `tools/targets.json` is out of date. Run `python tools/sync_targets.py` to rebuild it from the live app, or add the ID by hand. Review the result with `git diff tools/targets.json` and include it in your pull request.

## Pull requests

- Send one controller or one fix per pull request.
- Describe what you tested, on which hardware and operating system. The pull request template has a place for it.
- CI must pass.

## Releases

Maintainers publish a release by pushing a tag such as `v1.0.0`. CI checks everything, builds one zip per controller plus a zip of all presets, and publishes them with notes grouped by pull request label. A tag with a dash, such as `v1.0.0-rc1`, becomes a pre-release.

## Credit and license

Contributions fall under the [MIT license](LICENSE). If you reuse the documentation or the format in your own project, credit Raedrim with a link to this repository.

Pioneer DJ and B2B Studio have no affiliation with this project, and nothing here should suggest otherwise.
