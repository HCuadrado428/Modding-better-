#!/usr/bin/env python3
"""Crea un proyecto de mod nuevo a partir de templates/mod del plugin minecraft-modding.

Uso:
  new_mod.py --modid rubymod --name "Ruby Mod" --group io.github.usuario \
             --author "Usuario" --description "Añade rubíes" [--dest ./rubymod]
"""
import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.normpath(os.path.join(HERE, "..", "..", "..", "templates", "mod"))
TEXT_EXT = {".java", ".kts", ".properties", ".json", ".toml", ".md", ".yml", ".yaml", ".txt", ".mcmeta", ".gitignore"}
JAVA_KEYWORDS = {"abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const",
                 "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float",
                 "for", "goto", "if", "implements", "import", "instanceof", "int", "interface", "long", "native",
                 "new", "package", "private", "protected", "public", "return", "short", "static", "strictfp",
                 "super", "switch", "synchronized", "this", "throw", "throws", "transient", "try", "void",
                 "volatile", "while", "true", "false", "null", "record", "var", "yield"}


def class_name(name, modid):
    words = re.findall(r"[A-Za-z0-9]+", name) or re.findall(r"[a-z0-9]+", modid)
    cls = "".join(w[:1].upper() + w[1:] for w in words)
    if not cls or not cls[0].isalpha():
        cls = "Mod" + cls
    return cls


def validate(a):
    errors = []
    if not re.fullmatch(r"[a-z][a-z0-9_]{1,63}", a.modid):
        errors.append("modid: minúsculas, números y _, 2-64 caracteres, empezando por letra")
    if a.modid in ("minecraft", "forge", "neoforge", "fabric", "fabricloader", "java"):
        errors.append(f"modid '{a.modid}' está reservado")
    parts = a.group.split(".")
    if not all(re.fullmatch(r"[a-z_][a-z0-9_]*", p) and p not in JAVA_KEYWORDS for p in parts):
        errors.append("group: paquete Java en minúsculas, p. ej. io.github.usuario")
    if a.modid in JAVA_KEYWORDS:
        errors.append("modid no puede ser una palabra reservada de Java")
    return errors


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modid", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--group", required=True)
    p.add_argument("--author", default="Unknown")
    p.add_argument("--description", default="")
    p.add_argument("--dest")
    a = p.parse_args()

    errors = validate(a)
    if errors:
        sys.exit("ERRORES:\n  " + "\n  ".join(errors))
    dest = os.path.abspath(a.dest or os.path.join(os.getcwd(), a.modid))
    if os.path.exists(dest) and os.listdir(dest):
        sys.exit(f"La carpeta {dest} ya existe y no está vacía.")
    if not os.path.isdir(TEMPLATE):
        sys.exit(f"No se encuentra la plantilla en {TEMPLATE}")

    cls = class_name(a.name, a.modid)
    package = f"{a.group}.{a.modid}"
    desc = a.description or f"{a.name} - mod de Minecraft."

    shutil.copytree(TEMPLATE, dest, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".gradle", "build", "run", "versions/*-*"))

    replacements = [
        ("com.example.examplemod", package),
        ("com/example/examplemod", package.replace(".", "/")),
        ("mod.group=com.example", f"mod.group={a.group}"),
        ("mod.description=Mod de ejemplo generado con el plugin minecraft-modding.", f"mod.description={desc}"),
        ("Example Mod", a.name),
        ("ExampleMod", cls),
        ("ExampleAuthor", a.author),
        ("examplemod", a.modid),
    ]

    for root, _, files in os.walk(dest):
        for fn in files:
            path = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1] if fn != ".gitignore" else ".gitignore"
            if ext not in TEXT_EXT:
                continue
            with open(path, encoding="utf-8") as f:
                s = f.read()
            new = s
            for old, rep in replacements:
                new = new.replace(old, rep)
            if new != s:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new)

    # Mover el paquete Java y renombrar la clase principal
    old_pkg_dir = os.path.join(dest, "src", "main", "java", "com", "example", "examplemod")
    new_pkg_dir = os.path.join(dest, "src", "main", "java", *package.split("."))
    if os.path.normpath(old_pkg_dir) != os.path.normpath(new_pkg_dir):
        os.makedirs(os.path.dirname(new_pkg_dir), exist_ok=True)
        shutil.move(old_pkg_dir, new_pkg_dir)
        # limpiar com/example si quedó vacío
        for d in (os.path.join(dest, "src", "main", "java", "com", "example"), os.path.join(dest, "src", "main", "java", "com")):
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
    os.rename(os.path.join(new_pkg_dir, "ExampleMod.java"), os.path.join(new_pkg_dir, f"{cls}.java"))

    # Carpeta de assets
    assets = os.path.join(dest, "src", "main", "resources", "assets")
    os.rename(os.path.join(assets, "examplemod"), os.path.join(assets, a.modid))

    if os.name != "nt":
        os.chmod(os.path.join(dest, "gradlew"), 0o755)

    print(f"OK: proyecto creado en {dest}")
    print(f"  modid={a.modid}  clase={package}.{cls}")
    print("  Siguiente: cd a la carpeta, git init, y /minecraft-modding:mc-init")


if __name__ == "__main__":
    main()
