#!/usr/bin/env python3
"""DDJ-FLX4 bridge for B2B Studio (Windows and macOS).

Does what the app can't do on its own:
  1. Wakes the controller and keeps it awake (SysEx every 2 s, as flx4_wake.py does).
  2. Switches the pad mode when you press a pad-mode button, and lights that button. The FLX4
     only changes what its pads send when the *host* tells it to.
  3. Windows only: forwards every controller message to a virtual MIDI port, because Windows
     lets only one program read the FLX4's input. Point B2B Studio at that virtual port.
     macOS lets programs share the controller, so nothing is forwarded there.

Windows setup (once): install loopMIDI and create a port called "FLX4 Bridge" (see README.md).
Run this BEFORE B2B Studio and leave it open. It asks which decks you want: for anything other than
1 and 2 it writes a matching preset into presets/ for you to import.

    python flx4_bridge.py                     # normal use (python3 on macOS)
    python flx4_bridge.py --forward off       # test modes/LEDs without loopMIDI
    python flx4_bridge.py --pad-lights all    # light every pad in every mode
    python flx4_bridge.py --decks 1,3         # no questions: left side Deck 1, right side Deck 3
"""
import argparse
import pathlib
import sys
import threading
import time

import mido

# Wake-up / keep-alive SysEx (without F0/F7 framing), reverse-engineered by the Mixxx team.
WAKE_BYTES = [0x00, 0x40, 0x05, 0x00, 0x00, 0x04, 0x05, 0x00, 0x50, 0x02]

# Pad-mode button note -> (name, first pad note). The same note, sent back with velocity 127 on
# the deck's channel (0 = deck 1, 1 = deck 2), switches the controller into that mode.
MODES = {
    0x1B: ("HOT CUE", 0x00),
    0x1E: ("PAD FX 1", 0x10),
    0x20: ("BEAT JUMP", 0x20),
    0x22: ("SAMPLER", 0x30),
    0x69: ("KEYBOARD", 0x40),
    0x6B: ("PAD FX 2", 0x50),
    0x6D: ("BEAT LOOP", 0x60),
    0x6F: ("KEY SHIFT", 0x70),
}
PAD_CHANNEL = {0: 7, 1: 9}      # channel the pads of deck 1 / deck 2 send (and take LEDs) on
DEFAULT_MODE = 0x1B
HOT_CUE = 0x1B
HEADPHONE_CUE = 0x54            # per-channel headphone CUE button (note on the deck's channel)


class Bridge:
    def __init__(self, physical_in, physical_out, forward, pad_lights):
        self.out = physical_out
        self.forward = forward
        self.pad_lights = pad_lights
        self.mode = {0: DEFAULT_MODE, 1: DEFAULT_MODE}
        self.cue_lit = {0: False, 1: False}
        self.lock = threading.RLock()      # every write to the controller goes through this
        self.inp = None
        self.physical_in = physical_in

    # -- output helpers ------------------------------------------------------
    def send(self, status, channel, note, velocity):
        with self.lock:
            self.out.send(mido.Message(status, channel=channel, note=note, velocity=velocity))

    def send_sysex(self, data):
        with self.lock:
            self.out.send(mido.Message("sysex", data=data))

    def static_pads(self, button):
        """Should this mode's pads be lit while idle?"""
        if self.pad_lights == "all":
            return True
        if self.pad_lights == "banks":
            # Hot cue pads stay dark: the bridge can't see which cues B2B Studio has set, and
            # eight lit pads would claim eight cues exist.
            return button != HOT_CUE
        return False

    def pad_leds(self, deck, base, on):
        for i in range(8):
            self.send("note_on", PAD_CHANNEL[deck], base + i, 127 if on else 0)

    def set_mode(self, deck, button, announce=True):
        with self.lock:
            prev = self.mode[deck]
            if prev != button:
                self.send("note_on", deck, prev, 0)                  # old mode button LED off
                self.pad_leds(deck, MODES[prev][1], False)
            self.send("note_on", deck, button, 127)                   # switch mode + light button
            if self.static_pads(button):
                self.pad_leds(deck, MODES[button][1], True)
            self.mode[deck] = button
        if announce:
            side = "left" if deck == 0 else "right"     # the side of the controller, whatever deck it drives
            print(f"{side} pads: {MODES[button][0]}", flush=True)

    def lights_off(self):
        for deck in (0, 1):
            self.send("note_on", deck, HEADPHONE_CUE, 0)
            self.cue_lit[deck] = False
            for button, (_, base) in MODES.items():
                self.send("note_on", deck, button, 0)
                self.pad_leds(deck, base, False)

    # -- input ---------------------------------------------------------------
    def on_message(self, msg):
        if msg.type in ("clock", "active_sensing", "sysex"):
            return
        if self.forward is not None:
            try:
                self.forward.send(msg)
            except Exception as exc:  # keep the controller alive even if the virtual port hiccups
                print(f"forward failed: {exc}", file=sys.stderr, flush=True)
        if msg.type != "note_on":
            return
        pressed = msg.velocity > 0
        if msg.channel in (0, 1) and msg.note == HEADPHONE_CUE and pressed:
            # B2B Studio's channel CUE is a latching button, so mirror it: flip the LED on every press.
            self.cue_lit[msg.channel] = not self.cue_lit[msg.channel]
            self.send("note_on", msg.channel, HEADPHONE_CUE, 127 if self.cue_lit[msg.channel] else 0)
            return
        if msg.channel in (0, 1) and msg.note in MODES:
            if pressed:
                self.set_mode(msg.channel, msg.note)
            return
        if self.pad_lights == "off":
            return
        # momentary feedback: a pad flips its idle state while it is held
        for deck, ch in PAD_CHANNEL.items():
            if msg.channel == ch:
                button = self.mode[deck]
                base = MODES[button][1]
                if base <= msg.note < base + 8:
                    idle_on = self.static_pads(button)
                    lit = (not idle_on) if pressed else idle_on
                    self.send("note_on", ch, msg.note, 127 if lit else 0)

    def start(self):
        self.lights_off()                  # clear anything a previous run left lit
        self.inp = mido.open_input(self.physical_in, callback=self.on_message)
        for deck in (0, 1):
            self.set_mode(deck, DEFAULT_MODE, announce=False)

    def stop(self):
        try:
            self.lights_off()
        except Exception:
            pass


def find(names, needle):
    return next((n for n in names if needle in n), None)


def load_assign_decks():
    """assign_decks.py sits next to this file in a release download, and in tools/ in the repository."""
    here = pathlib.Path(__file__).resolve().parent
    for folder in (here, here.parent.parent / "tools"):
        if (folder / "assign_decks.py").is_file():
            sys.path.insert(0, str(folder))
            import assign_decks
            return assign_decks
    return None


def claim_decks(decks=None, shared=True, interactive=True, ask=input, platform=sys.platform):
    """Write the preset for the decks the player wants. Never stops the bridge: problems are only printed."""
    if decks is None and not interactive:
        return None
    tool = load_assign_decks()
    if tool is None:
        print("assign_decks.py is missing, so other decks cannot be set up. Download the release again.", flush=True)
        return None
    name = "ddj-flx4-bridge-windows" if platform == "win32" else "ddj-flx4-bridge-mac"
    source = pathlib.Path(__file__).resolve().parent / "presets" / f"{name}{tool.SUFFIX}"
    try:
        if decks is None:
            while True:
                answer = ask("\nWhich decks are yours? Left and right, for example 1,3 [Enter = 1,2]: ").strip()
                try:
                    left, right = tool.parse_decks(answer or "1,2")
                    break
                except tool.DeckError as exc:
                    print(exc, flush=True)
            if (left, right) != (1, 2):
                reply = ask("Leave out crossfader, headphones and effects (someone else runs them)? [y/N]: ")
                shared = not reply.strip().lower().startswith("y")
        else:
            left, right = tool.parse_decks(decks)
        if (left, right) == (1, 2) and shared:
            print(f"Decks 1 and 2: use presets/{source.name}.", flush=True)
            return source
        target, count = tool.convert_file(source, left, right, shared)
    except EOFError:
        return None
    except (tool.DeckError, OSError) as exc:
        print(f"Could not set up the decks: {exc}", flush=True)
        return None
    print(f"Decks {left} and {right}: wrote presets/{target.name} ({count} bindings).\n"
          "Import that file in B2B Studio's MIDI settings.", flush=True)
    return target


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--virtual-port", default="FLX4 Bridge",
                    help='name of the loopMIDI port to forward to on Windows (default "FLX4 Bridge")')
    ap.add_argument("--forward", choices=["auto", "on", "off"], default="auto",
                    help="forward controller messages to the virtual port (auto: on for Windows, off elsewhere)")
    ap.add_argument("--pad-lights", choices=["banks", "all", "held", "off"], default="banks",
                    help="banks: pads lit in every mode except hot cue (default); all: every pad lit; "
                         "held: pads light only while pressed; off: no pad lights")
    ap.add_argument("--decks", help="left and right deck, for example 1,3 (default: ask when started)")
    ap.add_argument("--no-shared", action="store_true",
                    help="with --decks: leave crossfader, headphone and effect controls out of the preset")
    args = ap.parse_args()

    in_name = find(mido.get_input_names(), "DDJ-FLX4")
    out_name = find(mido.get_output_names(), "DDJ-FLX4")
    if not in_name or not out_name:
        sys.exit("DDJ-FLX4 not found. Plug it in and close B2B Studio, rekordbox and MIDI-OX.")

    do_forward = args.forward == "on" or (args.forward == "auto" and sys.platform == "win32")
    forward = None
    if do_forward:
        v_out = find(mido.get_output_names(), args.virtual_port)
        if not v_out:
            sys.exit(f'Virtual port "{args.virtual_port}" not found. Install loopMIDI and create a port with that name '
                     "(see README.md), or run with --forward off to test without it.")
        forward = mido.open_output(v_out)
        print(f"Forwarding controller messages to {v_out}.", flush=True)

    try:
        out = mido.open_output(out_name)
    except Exception as exc:
        sys.exit(f"Could not open {out_name}: {exc}\nClose B2B Studio and any other MIDI program, then try again.")

    bridge = Bridge(in_name, out, forward, args.pad_lights)

    def keepalive():
        while True:
            try:
                bridge.send_sysex(WAKE_BYTES)
            except Exception:
                return
            time.sleep(2)

    threading.Thread(target=keepalive, daemon=True).start()

    try:
        bridge.start()
    except Exception as exc:
        sys.exit(f"Could not open {in_name}: {exc}\nClose B2B Studio and any other MIDI program, then try again.")

    print(f"Keeping {out_name} awake and handling pad modes.", flush=True)
    try:
        # The controller already works here: messages are handled on another thread while we wait for an answer.
        claim_decks(args.decks, not args.no_shared, interactive=sys.stdin is not None and sys.stdin.isatty())
        print("Leave this window open; start B2B Studio now.", flush=True)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        bridge.stop()


if __name__ == "__main__":
    main()
