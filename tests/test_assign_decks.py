"""Tests for tools/assign_decks.py and the bridge's deck question."""
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import assign_decks  # noqa: E402
import b2bmap  # noqa: E402

FLX4 = ROOT / "controllers" / "ddj-flx4"
PRESETS = sorted(p for p in (FLX4 / "presets").glob("*.b2bmidi.json") if "-decks-" not in p.name)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def preset(*targets):
    return {"name": "T", "bindings": {t: {"src": f"Dev|note|0|{i}"} for i, t in enumerate(targets)}}


class Reassign(unittest.TestCase):
    SAMPLE = preset("d0@cdj-3000x:play", "d1@cdj-3000x:play", "mx@djm-a9:ch0.fader", "mx@djm-a9:ch1.fader",
                    "mx@djm-a9:fx.ch0", "mx@djm-a9:fx.ch1", "mx@djm-a9:xf.pos", "mx@djm-a9:fx.depth")

    def moved(self, left, right, **kw):
        out = assign_decks.reassign(self.SAMPLE, left, right, **kw)
        return {body["src"].rsplit("|", 1)[1]: target for target, body in out["bindings"].items()}

    def test_decks_strips_and_fx_select_move_together(self):
        # (2, 4) is the trap: moving 1->2 and then 2->4 would put both decks on 4.
        for left, right in ((1, 3), (2, 4), (2, 1), (4, 1)):
            got = self.moved(left, right)
            a, b = left - 1, right - 1
            self.assertEqual([got[str(i)] for i in range(6)],
                             [f"d{a}@cdj-3000x:play", f"d{b}@cdj-3000x:play", f"mx@djm-a9:ch{a}.fader",
                              f"mx@djm-a9:ch{b}.fader", f"mx@djm-a9:fx.ch{a}", f"mx@djm-a9:fx.ch{b}"], (left, right))
            self.assertEqual((got["6"], got["7"]), ("mx@djm-a9:xf.pos", "mx@djm-a9:fx.depth"))

    def test_shared_controls_can_be_left_out(self):
        self.assertEqual(sorted(self.moved(2, 4, shared=False)), ["0", "1", "2", "3"])

    def test_input_is_not_modified(self):
        before = json.dumps(self.SAMPLE)
        assign_decks.reassign(self.SAMPLE, 3, 4)
        self.assertEqual(json.dumps(self.SAMPLE), before)

    def test_rejects(self):
        for args in ((1, 1), (0, 2), (1, 5)):
            with self.assertRaises(assign_decks.DeckError):
                assign_decks.reassign(self.SAMPLE, *args)
        for bad in ([], {"bindings": []}, preset("d0@cdj-3000x:play"),
                    preset("d0@cdj-3000x:play", "d1@cdj-3000x:play", "d2@cdj-3000x:play"),
                    preset("d0@cdj-3000x:play", "d1@cdj-3000x:play", "mx@djm-a9:ch0.fader", "mx@djm-a9:ch2.fader")):
            with self.assertRaises(assign_decks.DeckError):
                assign_decks.reassign(bad, 3, 4)

    def test_parse_decks(self):
        for text in ("1,3", "1 3", "1+3", "13", " 1, 3 "):
            self.assertEqual(assign_decks.parse_decks(text), (1, 3), text)
        for text in ("", "1", "1,1", "1,5", "123", "a,b", "1,3x"):
            with self.assertRaises(assign_decks.DeckError):
                assign_decks.parse_decks(text)

    def test_shipped_presets_stay_valid(self):
        registry = b2bmap.load_registry()
        for path in PRESETS:
            original = load(path)
            for left, right in ((1, 3), (2, 4)):
                out = assign_decks.reassign(original, left, right)
                self.assertEqual([b["src"] for b in out["bindings"].values()],
                                 [b["src"] for b in original["bindings"].values()])
                self.assertEqual([t for t in out["bindings"] if b2bmap.check_target(t, registry)[0]], [])
                self.assertEqual(assign_decks.source_decks(out["bindings"]), [left - 1, right - 1])

    def test_file_is_written_beside_the_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = pathlib.Path(tmp) / PRESETS[0].name
            shutil.copy(PRESETS[0], source)
            before = source.read_bytes()
            self.assertEqual(assign_decks.main([str(source), "--left", "1", "--right", "3"]), 0)
            stem = source.name[:-len(assign_decks.SUFFIX)]
            self.assertTrue((source.parent / f"{stem}-decks-1-3.b2bmidi.json").is_file())
            self.assertEqual(source.read_bytes(), before)


@unittest.skipUnless(importlib.util.find_spec("mido"), "mido is not installed")
class BridgeQuestion(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        folder = pathlib.Path(tmp.name)                              # laid out like a release download
        shutil.copytree(FLX4 / "presets", folder / "presets")
        shutil.copy(FLX4 / "flx4_bridge.py", folder)
        shutil.copy(ROOT / "tools" / "assign_decks.py", folder)
        spec = importlib.util.spec_from_file_location("bridge_copy", folder / "flx4_bridge.py")
        self.bridge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.bridge)

    def claim(self, *answers, **kw):
        queue = list(answers)
        return self.bridge.claim_decks(ask=lambda prompt: queue.pop(0), platform="win32", **kw)

    def test_enter_keeps_the_shipped_preset(self):
        self.assertEqual(self.claim("").name, "ddj-flx4-bridge-windows.b2bmidi.json")

    def test_asks_again_then_writes_the_preset(self):
        path = self.claim("1,1", "2,4", "y")
        self.assertEqual(path.name, "ddj-flx4-bridge-windows-decks-2-4.b2bmidi.json")
        self.assertNotIn("mx@djm-a9:xf.pos", load(path)["bindings"])

    def test_option_skips_the_questions(self):
        path = self.claim(decks="1,3")
        self.assertIn("mx@djm-a9:xf.pos", load(path)["bindings"])

    def test_never_stops_the_bridge(self):
        self.assertIsNone(self.claim(interactive=False))
        self.assertIsNone(self.claim(decks="7,8"))

        def closed(prompt):
            raise EOFError
        self.assertIsNone(self.bridge.claim_decks(ask=closed))


if __name__ == "__main__":
    unittest.main()
