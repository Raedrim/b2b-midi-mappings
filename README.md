# B2B Studio MIDI mappings

Community MIDI presets and helper tools for [B2B Studio](https://b2bstudio.live). They let a physical controller drive the CDJ and mixer panels.

| Controller | Status |
|---|---|
| [Pioneer DDJ-FLX4](controllers/ddj-flx4) | Works on Windows. Untested on macOS. |

Use a different controller? See [Contributing](#contributing). You can reuse the documentation here.

## Not affiliated

This project is independent and unofficial. Pioneer DJ and B2B Studio do not endorse or support it. Product names belong to their owners.

The presets depend on how B2B Studio behaves today, and its developers can change control IDs or MIDI handling at any time. If a preset breaks after an app update, [open an issue](../../issues) with your B2B Studio version.

## DDJ-FLX4 quick start

Plugging in the FLX4 and importing a preset is not enough. The controller waits for a wake-up message, and it switches pad modes and lights buttons only when the computer tells it to. A small script, the bridge, handles both.

1. Download the latest `ddj-flx4` zip from [Releases](../../releases) and unzip it. If there is no release yet, click **Code**, then **Download ZIP**, and open `controllers/ddj-flx4`.
2. On Windows, install Python 3 and [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html), then create a loopMIDI port named `FLX4 Bridge`. On macOS, install Python 3.
3. Double-click `start-bridge.bat` (Windows) or `start-bridge.command` (macOS) and leave the window open.
4. Start B2B Studio and import the preset from the `presets` folder.

Start the bridge before B2B Studio every time. [controllers/ddj-flx4/README.md](controllers/ddj-flx4/README.md) has the full steps, a troubleshooting table, a control reference and a setup without loopMIDI. The same file ships inside the release zip. The macOS setup is untested.

## Repository layout

```
controllers/<controller>/    one folder per controller: mapping.yaml, generated presets, docs, scripts
docs/MAPPING-FORMAT.md       how to write a mapping.yaml
docs/B2B-STUDIO-MIDI.md      B2B Studio's preset format and control IDs, as far as they are known
tools/                       b2bmap.py (build, check, learn, targets), the control registry, drift check
tests/                       tests for the tools
CONTRIBUTING.md              how to add a controller
```

## Contributing

We welcome mappings for other controllers and fixes to this one. You describe a controller in one YAML file, and the tools generate the presets and docs and check them. Three commands cover the workflow (`new`, `learn`, `check`), and `learn` writes most of the file while you press controls.

- [CONTRIBUTING.md](CONTRIBUTING.md) walks through the process.
- [docs/MAPPING-FORMAT.md](docs/MAPPING-FORMAT.md) is the format reference.
- [docs/B2B-STUDIO-MIDI.md](docs/B2B-STUDIO-MIDI.md) documents what B2B Studio expects from a preset.

If you build on these docs, credit Raedrim. A link back is plenty.

CI builds and checks every pull request on Windows and Linux. A weekly job looks for controls B2B Studio has removed. Pushing a version tag packages the release and publishes it.

## Credits

- The **Mixxx team** found the FLX4 wake-up message and wrote the [Pioneer DDJ-FLX4 mapping](https://mixxx.discourse.group/t/pioneer-ddj-flx4) that serves as the main MIDI reference.
- The unofficial djay Pro DDJ-FLX4 mapping (3.0) served as a second reference for note numbers.

## License

[MIT](LICENSE). Copyright (c) 2026 Raedrim.
