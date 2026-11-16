"""Tests de los scripts del plugin (hook de validación y texgen). Ejecutar: python -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "minecraft-modding")
HOOK = os.path.join(PLUGIN, "hooks", "check_asset.py")
TEXGEN = os.path.join(PLUGIN, "skills", "pixel-art-16x16", "scripts", "texgen.py")
EXAMPLE = os.path.join(PLUGIN, "skills", "pixel-art-16x16", "examples", "ruby.json")


def run_hook(path):
    payload = {"tool_name": "Write", "tool_input": {"file_path": path}, "cwd": os.path.dirname(path)}
    p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class HookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.res = os.path.join(self.tmp.name, "src", "main", "resources")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, content):
        path = os.path.join(self.res, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(path, mode, **({} if mode == "wb" else {"encoding": "utf-8"})) as f:
            f.write(content)
        return path

    def test_ignores_non_resource_files(self):
        path = os.path.join(self.tmp.name, "README.md")
        open(path, "w").close()
        self.assertEqual(run_hook(path)[0], 0)

    def test_invalid_json_is_error(self):
        code, _, err = run_hook(self.write("assets/mymod/models/item/x.json", "{ broken"))
        self.assertEqual(code, 2)
        self.assertIn("JSON no válido", err)

    def test_uppercase_path_is_error(self):
        code, _, err = run_hook(self.write("assets/mymod/models/item/Ruby.json", "{}"))
        self.assertEqual(code, 2)
        self.assertIn("minúsculas", err)

    def test_element_out_of_bounds_is_error(self):
        model = {"elements": [{"from": [0, 0, 0], "to": [40, 16, 16]}]}
        code, _, err = run_hook(self.write("assets/mymod/models/block/x.json", json.dumps(model)))
        self.assertEqual(code, 2)
        self.assertIn("-16 y 32", err)

    def test_missing_texture_is_warning(self):
        model = {"parent": "minecraft:item/generated", "textures": {"layer0": "mymod:item/ruby"}}
        code, out, _ = run_hook(self.write("assets/mymod/models/item/ruby.json", json.dumps(model)))
        self.assertEqual(code, 0)
        self.assertIn("textures/item/ruby.png", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_valid_model_with_texture_is_silent(self):
        subprocess.run([sys.executable, TEXGEN, "draw", EXAMPLE,
                        os.path.join(self.res, "assets/mymod/textures/item/ruby.png")], check=True, capture_output=True)
        model = {"parent": "minecraft:item/generated", "textures": {"layer0": "mymod:item/ruby"}}
        code, out, err = run_hook(self.write("assets/mymod/models/item/ruby.json", json.dumps(model)))
        self.assertEqual((code, out, err), (0, "", ""))

    def test_blockstate_missing_model_is_warning(self):
        bs = {"variants": {"": {"model": "mymod:block/nothing"}}}
        code, out, _ = run_hook(self.write("assets/mymod/blockstates/x.json", json.dumps(bs)))
        self.assertEqual(code, 0)
        self.assertIn("models/block/nothing.json", out)

    def test_bad_texture_size_is_error(self):
        from PIL import Image
        path = os.path.join(self.res, "assets/mymod/textures/item/big.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Image.new("RGBA", (20, 20)).save(path)
        code, _, err = run_hook(path)
        self.assertEqual(code, 2)
        self.assertIn("20x20", err)

    def test_plural_data_folder_is_warning(self):
        code, out, _ = run_hook(self.write("data/mymod/tags/blocks/ores.json", '{"values": []}'))
        self.assertEqual(code, 0)
        self.assertIn("tags/block", out)

    def test_lang_non_string_is_error(self):
        code, _, _ = run_hook(self.write("assets/mymod/lang/es_es.json", '{"a": 1}'))
        self.assertEqual(code, 2)


class TexgenTests(unittest.TestCase):
    def test_draw_validate_inspect_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "ruby.png")
            prev = os.path.join(tmp, "prev.png")
            subprocess.run([sys.executable, TEXGEN, "draw", EXAMPLE, out, "--preview", prev], check=True, capture_output=True)
            self.assertTrue(os.path.exists(prev))
            v = subprocess.run([sys.executable, TEXGEN, "validate", "--strict", out], capture_output=True, text=True)
            self.assertEqual(v.returncode, 0, v.stdout)
            spec = json.loads(subprocess.run([sys.executable, TEXGEN, "inspect", out], check=True,
                                             capture_output=True, text=True).stdout)
            with open(EXAMPLE, encoding="utf-8") as f:
                original = json.load(f)
            self.assertEqual(len(spec["rows"]), 16)
            self.assertEqual(len(spec["palette"]), len(original["palette"]))

    def test_draw_rejects_wrong_row_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = os.path.join(tmp, "bad.json")
            with open(spec, "w") as f:
                json.dump({"size": [16, 16], "palette": {".": "transparent"}, "rows": ["." * 15] * 16}, f)
            p = subprocess.run([sys.executable, TEXGEN, "draw", spec, os.path.join(tmp, "o.png")], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)

    def test_ramp(self):
        p = subprocess.run([sys.executable, TEXGEN, "ramp", "#336699", "5"], check=True, capture_output=True, text=True)
        self.assertEqual(len(json.loads(p.stdout)), 5)


if __name__ == "__main__":
    unittest.main()
