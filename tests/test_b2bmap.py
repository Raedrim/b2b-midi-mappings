"""Tests for tools/b2bmap.py. Run with: python -m unittest discover tests"""
import importlib.util
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import b2bmap  # noqa: E402

REGISTRY = b2bmap.load_registry()


def mapping(bindings, decks=None, ports=None):
    return {"name": "T", "profiles": ports or {"p": {"port": "Dev"}}, "decks": decks or [], "bindings": bindings}


class Templates(unittest.TestCase):
    def test_fills_names_and_format_specs(self):
        self.assertEqual(b2bmap.fmt("a{x}b{y:g}", {"x": 1, "y": 0.5}, "t"), "a1b0.5")

    def test_unknown_variable_is_an_error_not_a_crash(self):
        with self.assertRaises(b2bmap.MappingError):
            b2bmap.fmt("{nope}", {}, "t")

    def test_no_attribute_access(self):
        with self.assertRaises(b2bmap.MappingError):
            b2bmap.fmt("{x.__class__}", {"x": 1}, "t")


class Messages(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(b2bmap.parse_msg("note 0 0x0B", "t"), ("note", 0, 11))
        self.assertEqual(b2bmap.parse_msg("cc 6 64", "t"), ("cc", 6, 64))
        self.assertEqual(b2bmap.parse_msg("note 7 0x20+3", "t"), ("note", 7, 35))
        self.assertEqual(b2bmap.parse_msg("note 7 0x20 + 3", "t"), ("note", 7, 35))
        self.assertEqual(b2bmap.parse_msg("pb 2", "t"), ("pb", 2, 0))

    def test_rejects(self):
        for bad in ("note 16 1", "note 0 128", "key 0 1", "note 0", "note x 1", "pb"):
            with self.assertRaises(b2bmap.MappingError, msg=bad):
                b2bmap.parse_msg(bad, "t")


class Targets(unittest.TestCase):
    def ok(self, t):
        err, _ = b2bmap.check_target(t, REGISTRY)
        self.assertIsNone(err, t)

    def bad(self, t):
        err, _ = b2bmap.check_target(t, REGISTRY)
        self.assertIsNotNone(err, t)

    def test_known(self):
        for t in ("d0@cdj-3000x:play", "d3@cdj-3000x:hotcue7", "d0@cdj-3000x:jog/touch", "d1@cdj-3000x:rotary/push",
                  "d0@cdj-3000x:direction/rev", "d0@cdj-3000x:jogtop", "d0@cdj-3000x:screen/loop=0.25",
                  "d0@cdj-3000x:screen/jump=-16", "d0@cdj-3000x:screen/key=0", "d0@cdj-3000x:screen/time",
                  "mx@djm-a9:ch2.eqHi", "mx@djm-a9:fx.ch1", "mx@djm-a9:fx.mst", "mx@djm-a9:scfx.lockLamp",
                  "mx@djm-a9:xf.pos"):
            self.ok(t)

    def test_unknown(self):
        for t in ("d0@cdj-3000x:plya", "d9@cdj-3000x:play", "d0@cdj-3000x:play/touch", "mx@djm-a9:ch0.nope",
                  "d0@cdj-3000x:screen/loop=abc", "d0@cdj-3000x:screen/time=3", "d0@cdj-3000x:screen/zoom=1",
                  "play", "d0@djm-a9:xf.pos",
                  # mixer controls must not leak into the CDJ list (an extraction bug once allowed this)
                  "d0@cdj-3000x:xf.pos", "d0@cdj-3000x:ch0.fader", "d0@cdj-3000x:fx.onoff"):
            self.bad(t)

    def test_unknown_spec_is_only_a_warning(self):
        err, warn = b2bmap.check_target("mx@djm-v10:xf.pos", REGISTRY)
        self.assertIsNone(err)
        self.assertIsNotNone(warn)


class Expansion(unittest.TestCase):
    def test_for_decks_repeat_and_items(self):
        m = mapping([{"for": "decks", "bindings": [
            {"target": "d{d}@cdj-3000x:hotcue{i}", "msg": "note {pad} {i}", "repeat": 3, "doc": "{letter}"},
            {"target": "d{d}@cdj-3000x:screen/loop={v}", "msg": "note {pad} 0x10+{i}", "items": [1, 2], "why": "x{v}"},
        ]}], decks=[{"d": 0, "pad": 7}, {"d": 1, "pad": 9}])
        got = b2bmap.expand(m)
        self.assertEqual(len(got), 10)
        self.assertEqual((got[0].target, got[0].ch, got[0].num, got[0].doc), ("d0@cdj-3000x:hotcue0", 7, 0, "A"))
        self.assertEqual((got[4].target, got[4].num, got[4].custom), ("d0@cdj-3000x:screen/loop=2", 0x11, True))
        self.assertEqual(got[5].ch, 9)

    def test_deck_filter_group(self):
        m = mapping([{"for": "decks", "bindings": [
            {"only_decks": [1], "bindings": [{"target": "mx@djm-a9:fx.tap", "msg": "note 0 1", "doc": "x"}]}]}],
            decks=[{"d": 0}, {"d": 1}])
        self.assertEqual(len(b2bmap.expand(m)), 1)

    def test_doc_xor_why(self):
        for node in ({"target": "mx@djm-a9:xf.pos", "msg": "cc 0 1"},
                     {"target": "mx@djm-a9:xf.pos", "msg": "cc 0 1", "doc": "a", "why": "b"}):
            with self.assertRaises(b2bmap.MappingError):
                b2bmap.expand(mapping([node]))

    def test_unknown_keys_and_options(self):
        with self.assertRaises(b2bmap.MappingError):
            b2bmap.expand(mapping([{"target": "t", "msg": "cc 0 1", "doc": "x", "typo": 1}]))
        with self.assertRaises(b2bmap.MappingError):
            b2bmap.expand(mapping([{"target": "t", "msg": "cc 0 1", "doc": "x", "opts": {"rel": "wat"}}]))


class Validation(unittest.TestCase):
    def run_validate(self, bindings, ports=None):
        m = mapping(bindings, ports=ports)
        return b2bmap.validate(m, b2bmap.expand(m), REGISTRY, "t")

    def test_duplicate_target(self):
        errs, _ = self.run_validate([
            {"target": "d0@cdj-3000x:play", "msg": "note 0 1", "doc": "a"},
            {"target": "d0@cdj-3000x:play", "msg": "note 0 2", "doc": "b"}])
        self.assertTrue(any("bound twice" in e for e in errs))

    def test_shared_source_needs_share_flag(self):
        two = [{"target": "d0@cdj-3000x:play", "msg": "note 0 1", "doc": "a"},
               {"target": "d1@cdj-3000x:play", "msg": "note 0 1", "doc": "b"}]
        errs, _ = self.run_validate(two)
        self.assertTrue(any("share: true" in e for e in errs))
        errs, _ = self.run_validate([dict(b, share=True) for b in two])
        self.assertEqual(errs, [])

    def test_same_target_in_different_profiles_is_fine(self):
        errs, _ = self.run_validate([
            {"target": "d0@cdj-3000x:play", "msg": "note 0 1", "doc": "a", "only": "a"},
            {"target": "d0@cdj-3000x:play", "msg": "note 0 2", "doc": "b", "only": "b"}],
            ports={"a": {"port": "D"}, "b": {"port": "D"}})
        self.assertEqual(errs, [])

    def test_tag_filter(self):
        m = mapping([{"target": "d0@cdj-3000x:play", "msg": "note 0 1", "doc": "a", "only": "grp"}],
                    ports={"a": {"port": "D", "tags": ["grp"]}, "b": {"port": "D"}})
        e = b2bmap.expand(m)[0]
        self.assertTrue(e.applies_to("a", m["profiles"]["a"]))
        self.assertFalse(e.applies_to("b", m["profiles"]["b"]))


class Learn(unittest.TestCase):
    def test_guess_relative(self):
        self.assertEqual(b2bmap.guess_relative([1, 1, 2, 127, 126, 1]), "2c")
        self.assertEqual(b2bmap.guess_relative([65, 66, 63, 62, 65, 66]), "binoff")
        self.assertEqual(b2bmap.guess_relative([1, 2, 65, 66, 1, 66]), "signed")
        self.assertIsNone(b2bmap.guess_relative([3, 40, 90, 127, 10]))
        self.assertIsNone(b2bmap.guess_relative([5, 6]))

    def test_append_validates_and_rolls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "mapping.yaml"
            path.write_text(b2bmap.TEMPLATE.format(slug="x", name="X", port="X Port"), encoding="utf-8")
            good = b2bmap.binding_text("d0@cdj-3000x:cue", "note", 0, 12, "CUE button.", False, {})
            b2bmap.append_binding(path, good)
            self.assertIn("d0@cdj-3000x:cue", path.read_text(encoding="utf-8"))
            before = path.read_text(encoding="utf-8")
            bad = '  - target: "x"\n    msg: "note 99 1"\n    doc: "bad channel"\n'
            with self.assertRaises(b2bmap.MappingError):
                b2bmap.append_binding(path, bad)
            self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_learn_rejects_what_check_would_reject(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "mapping.yaml"
            path.write_text(b2bmap.TEMPLATE.format(slug="x", name="X", port="X Port"), encoding="utf-8")
            first = b2bmap.binding_text("d0@cdj-3000x:play", "note", 0, 11, "PLAY.", False, {})
            b2bmap.append_binding(path, first, REGISTRY)     # a fresh scaffold has no bindings to collide with
            before = path.read_text(encoding="utf-8")
            for text in (b2bmap.binding_text("d0@cdj-3000x:play", "note", 0, 99, "twice", False, {}),       # same target
                         b2bmap.binding_text("d0@cdj-3000x:cue", "note", 0, 11, "same message", False, {}),  # same source
                         b2bmap.binding_text("d0@cdj-3000x:nope", "note", 0, 12, "unknown target", False, {})):
                with self.assertRaises(b2bmap.MappingError):
                    b2bmap.append_binding(path, text, REGISTRY)
                self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_binding_text_round_trips(self):
        text = b2bmap.binding_text("d0@cdj-3000x:jog", "cc", 0, 0x21, 'side "ring"', True, {"rel": "binoff"})
        data = b2bmap.yaml.safe_load(text)[0]
        self.assertEqual(data["msg"], "cc 0 0x21")
        self.assertEqual(data["opts"], {"rel": "binoff"})
        self.assertEqual(data["why"], 'side "ring"')

    def test_new_template_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "mapping.yaml"
            path.write_text(b2bmap.TEMPLATE.format(slug="x", name="X", port="X Port"), encoding="utf-8")
            m = b2bmap.load_mapping(path)
            errs, _ = b2bmap.validate(m, b2bmap.expand(m), REGISTRY, "x")
            self.assertEqual(errs, [])


def exported(bindings, name="Their Pad"):
    return {"app": "B2B Studio", "kind": "midi-preset", "version": 1, "name": name, "bindings": bindings}


class Import(unittest.TestCase):
    def convert(self, preset, port=None):
        name, port, text, count, notes = b2bmap.convert_preset(preset, port)
        doc = b2bmap.TEMPLATE.format(slug="x", name=name, port=port) + text
        return doc, count, notes

    def test_parse_src(self):
        self.assertEqual(b2bmap.parse_src("DDJ-FLX4|note|7|32", "t"), ("DDJ-FLX4", "note", 7, 32))
        self.assertEqual(b2bmap.parse_src("A|B port|pb|2|0", "t"), ("A|B port", "pb", 2, 0))
        for bad in ("DDJ|note|0", "DDJ|sysex|0|1", "DDJ|note|16|1", "DDJ|cc|0|128", "DDJ|cc|x|1"):
            with self.assertRaises(b2bmap.MappingError):
                b2bmap.parse_src(bad, "t")

    def test_options_use_the_yaml_spelling(self):
        self.assertEqual(b2bmap.import_options({"rel": True, "invert": True, "sens": 5}),
                         {"rel": "2c", "invert": True, "sens": 5})
        self.assertEqual(b2bmap.import_options({"rel": "binoff", "invert": False, "pos": 1}),
                         {"rel": "binoff", "pos": 1})
        self.assertEqual(b2bmap.import_options({"rel": False, "bogus": 1, "sens": "x"}), {})

    def test_every_binding_starts_as_a_todo_that_check_rejects(self):
        doc, count, _ = self.convert(exported({"d0@cdj-3000x:play": {"src": "Pad|note|0|11"},
                                               "mx@djm-a9:ch0.fader": {"src": "Pad|cc|0|19"}}))
        self.assertEqual(count, 2)
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "mapping.yaml"
            path.write_text(doc, encoding="utf-8")
            m = b2bmap.load_mapping(path)
            errs, _ = b2bmap.validate(m, b2bmap.expand(m), REGISTRY, "x")
            self.assertEqual(len(errs), 2)
            self.assertTrue(all("TODO" in e for e in errs))
            path.write_text(doc.replace(b2bmap.TODO_DOC, "Done."), encoding="utf-8")
            m = b2bmap.load_mapping(path)
            self.assertEqual(b2bmap.validate(m, b2bmap.expand(m), REGISTRY, "x")[0], [])

    def test_shared_messages_are_marked(self):
        doc, _, notes = self.convert(exported({"d0@cdj-3000x:rotary": {"src": "Pad|cc|6|64", "rel": True},
                                               "d1@cdj-3000x:rotary": {"src": "Pad|cc|6|64", "rel": True}}))
        self.assertEqual(doc.count("share: true"), 2)
        self.assertTrue(any("share" in n for n in notes))
        m = b2bmap.yaml.safe_load(doc.replace(b2bmap.TODO_DOC, "Browse."))
        self.assertEqual(b2bmap.validate(m, b2bmap.expand(m), REGISTRY, "x")[0], [])

    def test_several_inputs_need_a_choice(self):
        preset = exported({"d0@cdj-3000x:play": {"src": "Pad|note|0|11"}, "d0@cdj-3000x:cue": {"src": "Other|note|0|12"}})
        with self.assertRaises(b2bmap.MappingError) as ctx:
            b2bmap.convert_preset(preset)
        self.assertIn("--port", str(ctx.exception))
        doc, count, notes = self.convert(preset, "Other")
        self.assertEqual(count, 1)
        self.assertNotIn("play", doc.split("bindings:")[-1])
        self.assertTrue(any("left out" in n for n in notes))
        with self.assertRaises(b2bmap.MappingError):
            b2bmap.convert_preset(preset, "Missing")

    def test_rejects_things_that_are_not_presets(self):
        for bad in ([], {"bindings": []}, {"bindings": {}}, exported({"d0@cdj-3000x:play": {}})):
            with self.assertRaises(b2bmap.MappingError):
                b2bmap.convert_preset(bad)

    def test_shipped_presets_survive_the_round_trip(self):
        """Import a generated preset, describe every binding, rebuild it: same sources and options."""
        import json
        for f in sorted((b2bmap.CONTROLLERS / "ddj-flx4" / "presets").glob("*.json")):
            original = json.loads(f.read_text(encoding="utf-8"))
            _, port, text, _, _ = b2bmap.convert_preset(original)
            doc = (b2bmap.TEMPLATE.format(slug="x", name="X", port=port) + text).replace(b2bmap.TODO_DOC, "d")
            m = b2bmap.yaml.safe_load(doc)
            entries = b2bmap.expand(m)
            self.assertEqual(b2bmap.validate(m, entries, REGISTRY, "x")[0], [], f.name)
            rebuilt = {e.target: ({"src": e.src(port)}, e.opts) for e in entries}
            self.assertEqual(set(rebuilt), set(original["bindings"]), f.name)
            for target, body in original["bindings"].items():
                src, opts = rebuilt[target]
                want = {k: v for k, v in body.items() if k in b2bmap.OPTION_KEYS}
                self.assertEqual(src["src"], body["src"], target)
                self.assertEqual(opts, want, target)

    def test_autodoc_describes_the_app_control(self):
        cases = {
            "d0@cdj-3000x:play": "Deck 1: PLAY / PAUSE.",
            "d1@cdj-3000x:jog/touch": "Deck 2: JOG WHEEL (touch).",
            "mx@djm-a9:ch2.fader": "Mixer channel 3: CHANNEL FADER.",
            "d1@cdj-3000x:hotcue3": "Deck 2: HOT CUE D.",
            "d0@cdj-3000x:cuecall_l": "Deck 1: CUE/LOOP CALL (left).",
            "mx@djm-a9:fx.ch1": "Mixer: BEAT FX channel 2 select.",
            "mx@djm-a9:ch1.input": "Mixer channel 2: INPUT SELECT · CH 2.",
            "d0@cdj-3000x:screen/loop=0.3333333333333333": "Deck 1: sets a 1/3-beat loop, or resizes the active one.",
            "d1@cdj-3000x:screen/loop=16": "Deck 2: sets a 16-beat loop, or resizes the active one.",
            "d0@cdj-3000x:screen/jump=-0.5": "Deck 1: jumps 1/2 beat(s) back.",
            "d0@cdj-3000x:screen/key=-2": "Deck 1: shifts the key by -2 semitone(s).",
            "d0@cdj-3000x:screen/key=0": "Deck 1: resets the key shift.",
        }
        for target, want in cases.items():
            self.assertEqual(b2bmap.autodoc(target, REGISTRY), want, target)

    def test_every_autodoc_survives_the_template_engine(self):
        """A drafted description is parsed as a template, so it must never contain stray braces."""
        for spec_name, spec in REGISTRY["specs"].items():
            unit = "mx" if spec["units"] == "mx" else "d0"
            for cid in list(spec["controls"]) + list(spec.get("extra", {})):
                target = f"{unit}@{spec_name}:{cid.replace('{n}', '1')}"
                text = b2bmap.autodoc(target, REGISTRY)
                if text:
                    self.assertEqual(b2bmap.fmt(text, {}, target), text)

    def test_autodoc_stays_quiet_when_unsure(self):
        for target in ("d0@cdj-3000x:nope", "x@unknown:thing", "not a target",
                       "d0@cdj-3000x:screen/loop=abc", "d0@cdj-3000x:screen/needle"):
            self.assertIsNone(b2bmap.autodoc(target, REGISTRY), target)

    def test_import_drafts_what_it_can_and_leaves_a_todo_for_the_rest(self):
        preset = exported({"d0@cdj-3000x:play": {"src": "Pad|note|0|11"}, "d0@cdj-3000x:screen/needle": {"src": "Pad|note|0|12"}})
        _, _, text, _, notes = b2bmap.convert_preset(preset, registry=REGISTRY)
        self.assertIn("Deck 1: PLAY / PAUSE.", text)
        self.assertEqual(text.count(b2bmap.TODO_DOC), 1)
        self.assertTrue(any("drafted" in n for n in notes))
        _, _, plain, _, _ = b2bmap.convert_preset(preset)
        self.assertEqual(plain.count(b2bmap.TODO_DOC), 2)

    def test_command_writes_the_controller_folder(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            preset = tmp / "export.json"
            preset.write_text(json.dumps(exported({"d0@cdj-3000x:play": {"src": "Pad|note|0|11"},
                                                   "d0@cdj-3000x:nope": {"src": "Pad|note|0|12"}})), encoding="utf-8")
            saved = b2bmap.CONTROLLERS
            b2bmap.CONTROLLERS = tmp / "controllers"
            try:
                self.assertEqual(b2bmap.main(["import", str(preset), "their-pad"]), 0)
                d = b2bmap.CONTROLLERS / "their-pad"
                self.assertTrue((d / "README.md").exists())
                m = b2bmap.load_mapping(d / "mapping.yaml")
                self.assertEqual((m["name"], m["profiles"]["default"]["port"]), ("Their Pad", "Pad"))
                self.assertEqual(len(m["bindings"]), 2)
                self.assertEqual(b2bmap.main(["import", str(preset), "their-pad"]), 1)     # will not overwrite
                self.assertEqual(b2bmap.main(["import", str(preset), "Bad Slug"]), 1)
            finally:
                b2bmap.CONTROLLERS = saved


@unittest.skipUnless(importlib.util.find_spec("mido"), "mido is not installed")
class LearnCapture(unittest.TestCase):
    """The parts of `learn` that talk to the controller, driven by scripted messages."""

    @staticmethod
    def feed(*messages):
        queue = list(messages)
        return lambda timeout: queue.pop(0) if queue else None

    def test_note_press_is_captured_and_release_ignored(self):
        mido = __import__("mido")
        feed = self.feed(mido.Message("note_off", channel=0, note=11), mido.Message("note_on", channel=0, note=11, velocity=0),
                         mido.Message("note_on", channel=1, note=12, velocity=127))
        self.assertEqual(b2bmap.capture(feed), ("note", 1, 12, []))

    def test_cc_stream_is_collected_and_fine_byte_ignored(self):
        mido = __import__("mido")
        cc = lambda n, v: mido.Message("control_change", channel=0, control=n, value=v)
        feed = self.feed(cc(4, 100), cc(36, 7), cc(4, 101), cc(4, 102))
        kind, ch, num, values = b2bmap.capture(feed)
        self.assertEqual((kind, ch, num), ("cc", 0, 4))
        self.assertEqual(values, [100, 101, 102])

    def test_timeout_returns_none(self):
        self.assertIsNone(b2bmap.capture(self.feed(), timeout=0.3))

    def test_ask_target_accepts_a_full_id_and_rejects_a_bad_one(self):
        from unittest import mock
        answers = iter(["d0@cdj-3000x:nope", "d0@cdj-3000x:play"])
        with mock.patch("builtins.input", lambda prompt="": next(answers)):
            self.assertEqual(b2bmap.ask_target(REGISTRY), "d0@cdj-3000x:play")

    def test_ask_target_search_fills_placeholders(self):
        from unittest import mock
        answers = iter(["hot cue", "1", "1", "3"])      # words, pick #1, deck index, hot cue number
        with mock.patch("builtins.input", lambda prompt="": next(answers)):
            self.assertEqual(b2bmap.ask_target(REGISTRY), "d1@cdj-3000x:hotcue3")

    def test_enter_skips(self):
        from unittest import mock
        with mock.patch("builtins.input", lambda prompt="": ""):
            self.assertIsNone(b2bmap.ask_target(REGISTRY))


class Repository(unittest.TestCase):
    """The checked-in controllers must be valid and their generated files up to date."""

    def test_check_passes(self):
        self.assertEqual(b2bmap.main(["check"]), 0)

    def test_flx4_counts(self):
        d = b2bmap.CONTROLLERS / "ddj-flx4"
        m, entries = b2bmap.compile_controller(d)
        counts = {n: sum(e.applies_to(n, p) for e in entries) for n, p in m["profiles"].items()}
        self.assertEqual(counts, {"direct": 120, "bridge-windows": 212, "bridge-mac": 212})


if __name__ == "__main__":
    unittest.main()
