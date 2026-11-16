"""Tests de los scripts del plugin (hook de validación y texgen). Ejecutar: python -m unittest discover -s tests"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "minecraft-modding")
HOOK = os.path.join(PLUGIN, "hooks", "check_asset.py")
TEXGEN = os.path.join(PLUGIN, "skills", "pixel-art-16x16", "scripts", "texgen.py")
EXAMPLE = os.path.join(PLUGIN, "skills", "pixel-art-16x16", "examples", "ruby.json")
NEW_MOD = os.path.join(PLUGIN, "skills", "mc-new", "scripts", "new_mod.py")
EXPORT = os.path.join(PLUGIN, "skills", "mc-cloud-setup", "scripts", "export_to_repo.py")


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

    def test_rectangular_uv_texture_is_ok(self):
        from PIL import Image
        path = os.path.join(self.res, "assets/mymod/textures/block/jaula.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Image.new("RGBA", (1024, 512)).save(path)
        self.assertEqual(run_hook(path)[0], 0)

    def test_plural_data_folder_is_warning(self):
        code, out, _ = run_hook(self.write("data/mymod/tags/blocks/ores.json", '{"values": []}'))
        self.assertEqual(code, 0)
        self.assertIn("tags/block", out)

    def test_plural_data_folder_ok_for_1_20_project(self):
        with open(os.path.join(self.tmp.name, "build.gradle"), "w") as f:
            f.write("// forge")
        with open(os.path.join(self.tmp.name, "gradle.properties"), "w") as f:
            f.write("minecraft_version=1.20.1\n")
        code, out, err = run_hook(self.write("data/mymod/loot_tables/blocks/x.json", '{"pools": []}'))
        self.assertEqual((code, out, err), (0, "", ""))

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


class ExportTests(unittest.TestCase):
    def test_export_rewrites_paths_and_detects_repos(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "build.gradle"), "w") as f:
                f.write("plugins { id 'net.minecraftforge.gradle' version '6.0' }\n"
                        "java.toolchain.languageVersion = JavaLanguageVersion.of(17)\n"
                        "repositories { maven { url = 'https://maven.example.dev/' } }\n")
            os.makedirs(os.path.join(tmp, ".claude"))
            with open(os.path.join(tmp, ".claude", "settings.json"), "w") as f:
                json.dump({"permissions": {"allow": ["Bash(ls:*)"]}}, f)
            for _ in range(2):  # dos veces: no debe duplicar el hook
                subprocess.run([sys.executable, EXPORT, "--dest", tmp], check=True, capture_output=True)
            with open(os.path.join(tmp, ".claude", "settings.json")) as f:
                settings = json.load(f)
            self.assertEqual(settings["permissions"]["allow"], ["Bash(ls:*)"])
            self.assertEqual(len(settings["hooks"]["PostToolUse"]), 1)
            self.assertFalse(os.path.exists(os.path.join(tmp, ".claude", "skills", "mc-new")))
            for root, _, files in os.walk(os.path.join(tmp, ".claude")):
                for fn in files:
                    if fn.endswith(".md") and "cloud" not in root:
                        with open(os.path.join(root, fn), encoding="utf-8") as f:
                            txt = f.read()
                        self.assertNotIn("${CLAUDE_PLUGIN_ROOT}", txt, fn)
                        self.assertNotIn("minecraft-modding:", txt, fn)
            with open(os.path.join(tmp, ".claude", "cloud", "README.md"), encoding="utf-8") as f:
                cloud = f.read()
            self.assertIn("maven.example.dev", cloud)
            self.assertIn("maven.minecraftforge.net", cloud)
            self.assertIn("openjdk-17-jdk-headless", cloud)


class NewModTests(unittest.TestCase):
    def test_generates_renamed_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = os.path.join(tmp, "rubymod")
            subprocess.run([sys.executable, NEW_MOD, "--modid", "rubymod", "--name", "Ruby Mod", "--group",
                            "io.github.test", "--author", "Tester", "--dest", dest], check=True, capture_output=True)
            main = os.path.join(dest, "src/main/java/io/github/test/rubymod/RubyMod.java")
            self.assertTrue(os.path.exists(main))
            self.assertTrue(os.path.isdir(os.path.join(dest, "src/main/resources/assets/rubymod")))
            leftovers = []
            for root, _, files in os.walk(dest):
                for fn in files:
                    if fn.endswith((".java", ".json", ".toml", ".kts", ".properties")):
                        with open(os.path.join(root, fn), encoding="utf-8") as f:
                            if "examplemod" in f.read().lower():
                                leftovers.append(fn)
            self.assertEqual(leftovers, [])

    def test_rejects_bad_modid(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = subprocess.run([sys.executable, NEW_MOD, "--modid", "Bad-Id", "--name", "X", "--group", "a.b",
                                "--dest", os.path.join(tmp, "x")], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)


class TemplateVersionRangeTests(unittest.TestCase):
    """Cada jar debe declarar un rango de Minecraft con límite superior: sin él, el loader lo carga
    en versiones que no soporta y el juego crashea en vez de mostrar 'versión incompatible'."""

    TEMPLATE = os.path.join(PLUGIN, "templates", "mod")
    RES = os.path.join(TEMPLATE, "src", "main", "resources")
    DEPS = os.path.join(TEMPLATE, "versions", "dependencies")

    @staticmethod
    def vt(v):
        return tuple(int(x) for x in v.split("."))

    def assert_bounded_fabric(self, rng, where):
        rng = rng.strip()
        if re.fullmatch(r"[0-9][0-9.]*", rng) or rng.startswith("~"):
            return  # versión exacta o ~x.y.z (mismo parche)
        self.assertIn("<", rng, f"{where}: rango Fabric sin límite superior: {rng!r}")

    def assert_bounded_forge(self, rng, where):
        m = re.fullmatch(r"\s*[\[(]\s*([^,\])]*)\s*,\s*([^\])]*?)\s*[\])]\s*", rng)
        if m is None:
            self.assertRegex(rng, r"^\[[^,\]]+\]$", f"{where}: rango Maven no válido: {rng!r}")
            return
        self.assertTrue(m.group(2), f"{where}: rango Forge/NeoForge sin límite superior: {rng!r}")

    def test_metadata_does_not_use_open_minecraft_range(self):
        with open(os.path.join(self.RES, "fabric.mod.json"), encoding="utf-8") as f:
            mc = json.load(f)["depends"]["minecraft"]
        if "${" not in mc:
            self.assert_bounded_fabric(mc, "fabric.mod.json")
        else:
            self.assertNotRegex(mc, r">=\s*\$\{", "fabric.mod.json: usa '>=${...}' (rango abierto)")
        for toml in ("mods.toml", "neoforge.mods.toml"):
            with open(os.path.join(self.RES, "META-INF", toml), encoding="utf-8") as f:
                text = f.read()
            blocks = re.split(r"(?m)^\[\[", text)
            mc_blocks = [b for b in blocks if re.search(r'(?m)^modId\s*=\s*"minecraft"', b)]
            self.assertEqual(len(mc_blocks), 1, f"{toml}: falta la dependencia de minecraft")
            rng = re.search(r'(?m)^versionRange\s*=\s*"([^"]*)"', mc_blocks[0]).group(1)
            if "${" in rng:
                self.assertNotRegex(rng, r",\s*\)$", f"{toml}: rango abierto {rng!r}")
            else:
                self.assert_bounded_forge(rng, toml)

    def test_every_version_declares_bounded_ranges(self):
        files = sorted(f for f in os.listdir(self.DEPS) if f.endswith(".properties"))
        self.assertTrue(files)
        for fn in files:
            props = {}
            with open(os.path.join(self.DEPS, fn), encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.lstrip().startswith("#"):
                        k, v = line.split("=", 1)
                        props[k.strip()] = v.strip()
            for key in ("minecraft_version", "mc_range_fabric", "mc_range_forge"):
                self.assertIn(key, props, f"{fn}: falta {key}")
            self.assert_bounded_fabric(props["mc_range_fabric"], fn)
            self.assert_bounded_forge(props["mc_range_forge"], fn)
            # El rango Forge debe incluir la propia versión del target.
            m = re.fullmatch(r"([\[(])([^,]*),([^\])]*)([\])])", props["mc_range_forge"].replace(" ", ""))
            if m:
                v = self.vt(props["minecraft_version"])
                lo, hi = self.vt(m.group(2)), self.vt(m.group(3))
                self.assertTrue(lo < v or (lo == v and m.group(1) == "["), f"{fn}: {v} queda fuera del rango")
                self.assertTrue(v < hi or (v == hi and m.group(4) == "]"), f"{fn}: {v} queda fuera del rango")


if __name__ == "__main__":
    unittest.main()
