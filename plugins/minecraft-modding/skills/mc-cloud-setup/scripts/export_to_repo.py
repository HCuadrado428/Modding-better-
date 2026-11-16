#!/usr/bin/env python3
"""Copia el plugin minecraft-modding dentro de la carpeta .claude/ de un repositorio de mod,
para que funcione en Claude Code en la web y en la app (las sesiones en la nube no instalan plugins,
pero sí cargan lo que hay en el repositorio).

Hace:
  - .claude/skills/<skill>/        skills del plugin (sin las de crear proyectos) con rutas reescritas
  - .claude/agents/*.md            subagentes
  - .claude/hooks/check_asset.py   validador de recursos + entrada en .claude/settings.json
  - .claude/cloud/README.md        dominios de red y setup script para el entorno de nube,
                                   detectados a partir de build.gradle / settings.gradle
  - .claude/minecraft-modding.json versión del plugin exportada (para saber cuándo actualizar)

Uso: export_to_repo.py --dest /ruta/al/mod [--force]
Se puede volver a ejecutar para actualizar: sobrescribe los ficheros del plugin y conserva el resto.
"""
import argparse
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SKIP_SKILLS = {"mc-new", "mc-init", "mc-cloud-setup"}
NS = "minecraft-modding:"
HOOK_CMD = ('PY=$(command -v python3 || command -v python || command -v py) || exit 0; '
            '"$PY" "$CLAUDE_PROJECT_DIR/.claude/hooks/check_asset.py"')

# Dominios que cualquier mod necesita además de la lista "Trusted" por defecto
BASE_DOMAINS = [
    "libraries.minecraft.net",
    "*.mojang.com",
    "resources.download.minecraft.net",
    "api.foojay.io",
]
LOADER_DOMAINS = {
    "forge": ["maven.minecraftforge.net"],
    "neoforge": ["maven.neoforged.net"],
    "fabric": ["maven.fabricmc.net"],
    "stonecraft": ["maven.kikugie.dev", "maven.architectury.dev", "maven.fabricmc.net",
                   "maven.neoforged.net", "maven.minecraftforge.net"],
}
# Ya incluidos en la lista Trusted por defecto: no hace falta añadirlos
TRUSTED = {"repo.maven.apache.org", "repo1.maven.org", "maven.org", "plugins.gradle.org",
           "services.gradle.org", "gradle.org", "maven.google.com", "jitpack.io"}


def rewrite(text):
    text = text.replace("${CLAUDE_PLUGIN_ROOT}/", ".claude/")
    text = text.replace(NS, "")
    text = text.replace("…:neoforge-modding", "neoforge-modding").replace("…:forge-modding", "forge-modding")
    text = text.replace("`<loader>-modding`", "`<loader>-modding`")
    return text


def copy_tree_rewritten(src, dst):
    for root, _, files in os.walk(src):
        if "__pycache__" in root:
            continue
        rel = os.path.relpath(root, src)
        out_dir = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(out_dir, exist_ok=True)
        for fn in files:
            s, d = os.path.join(root, fn), os.path.join(out_dir, fn)
            if fn.endswith(".md"):
                with open(s, encoding="utf-8") as f:
                    txt = rewrite(f.read())
                with open(d, "w", encoding="utf-8", newline="\n") as f:
                    f.write(txt)
            else:
                shutil.copy2(s, d)


def detect(dest):
    """Lee los ficheros de Gradle para deducir loader, versión de Java y repositorios Maven."""
    text = ""
    for fn in ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts", "gradle.properties"):
        p = os.path.join(dest, fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                text += f"\n# {fn}\n" + f.read()
    loaders = set()
    if "gg.meza.stonecraft" in text:
        loaders.add("stonecraft")
    if re.search(r"net\.minecraftforge\.gradle|forge_version|minecraftforge", text):
        loaders.add("forge")
    if re.search(r"net\.neoforged|neoforge_version", text):
        loaders.add("neoforge")
    if re.search(r"fabric-loom|fabric_version|net\.fabricmc", text):
        loaders.add("fabric")
    m = re.search(r"JavaLanguageVersion\.of\((\d+)\)", text)
    java = int(m.group(1)) if m else None
    gradle_jvm = 25 if "stonecraft" in loaders else None
    hosts = set()
    for url in re.findall(r"https?://([A-Za-z0-9.\-]+)", text):
        hosts.add(url.lower())
    hosts -= {"github.com", "www.github.com"}
    return loaders, java, gradle_jvm, sorted(hosts)


def cloud_readme(loaders, java, gradle_jvm, hosts, version):
    domains = list(BASE_DOMAINS)
    for l in sorted(loaders):
        domains += LOADER_DOMAINS.get(l, [])
    domains += [h for h in hosts if h not in TRUSTED]
    seen, uniq = set(), []
    for d in domains:
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    jdks = sorted({v for v in (java, gradle_jvm) if v and v != 21})
    apt = " ".join(f"openjdk-{v}-jdk-headless" for v in jdks)
    setup = ["#!/bin/bash", "# Setup script del entorno de nube (generado por minecraft-modding)"]
    if apt:
        setup.append(f"apt-get update -qq && apt-get install -y -qq {apt} || true")
    setup.append("python3 -m pip install -q pillow || pip install -q pillow || true")
    setup_txt = "\n".join(setup)
    lines = [
        "# Configurar el entorno de nube (claude.ai/code y app de Claude)",
        "",
        f"Generado por el plugin minecraft-modding {version}. Loaders detectados: {', '.join(sorted(loaders)) or 'ninguno'}"
        + (f" · Java del mod: {java}" if java else "") + ".",
        "",
        "Las sesiones en la nube cargan `.claude/` y `CLAUDE.md` del repositorio, pero la red y las herramientas",
        "del sistema se configuran en el **entorno**. Hazlo una vez:",
        "",
        "1. Abre https://claude.ai/code → selector de entorno → icono de ajustes del entorno (o crea uno nuevo, p. ej. \"Minecraft\").",
        "2. **Network access → Custom**, marca **\"Also include default list of common package managers\"** y pega en *Allowed domains*:",
        "",
        "```text",
        *uniq,
        "```",
        "",
        "3. **Setup script** (instala lo que no viene en la máquina; se guarda en caché si tarda menos de ~5 minutos):",
        "",
        "```bash",
        setup_txt,
        "```",
        "",
        "4. Usa ese entorno al crear sesiones de este repositorio (también desde la pestaña **Code** de la app).",
        "",
        "## Qué funciona en la nube",
        "",
        "| Funciona | No funciona (necesita tu PC) |",
        "|---|---|",
        "| Compilar (`./gradlew build`), datagen, GameTests en servidor | `runClient` (no hay pantalla) |",
        "| Skills, subagentes y hook de validación | Blockbench y Aseprite por MCP (están en tu PC) |",
        "| `texgen.py` para texturas | Probar el mod a mano en el juego |",
        "",
        "Para lo que no funciona en la nube, usa Claude Code en tu PC con el plugin instalado y, si quieres manejarlo",
        "desde el móvil, `/remote-control`.",
        "",
        "## Actualizar",
        "",
        "Cuando salga una versión nueva del plugin, vuelve a ejecutar desde tu PC (con el plugin instalado)",
        "`/minecraft-modding:mc-cloud-setup` en este repositorio y haz commit de los cambios en `.claude/`.",
    ]
    return "\n".join(lines) + "\n"


def merge_settings(path):
    data = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    hooks = data.setdefault("hooks", {})
    post = hooks.setdefault("PostToolUse", [])
    for entry in post:
        for h in entry.get("hooks", []):
            if "check_asset.py" in h.get("command", ""):
                h["command"] = HOOK_CMD
                break
        else:
            continue
        break
    else:
        post.append({"matcher": "Write|Edit|MultiEdit",
                     "hooks": [{"type": "command", "command": HOOK_CMD, "timeout": 30}]})
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", default=".", help="raíz del repositorio del mod")
    ap.add_argument("--force", action="store_true", help="no comprobar que es un proyecto Gradle")
    a = ap.parse_args()
    dest = os.path.abspath(a.dest)
    if not a.force and not any(os.path.exists(os.path.join(dest, f)) for f in ("build.gradle", "build.gradle.kts")):
        sys.exit(f"{dest} no parece un proyecto Gradle (no hay build.gradle). Usa --force si estás seguro.")

    with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f).get("version", "?")

    claude = os.path.join(dest, ".claude")
    os.makedirs(claude, exist_ok=True)
    copied = []
    for name in sorted(os.listdir(os.path.join(PLUGIN, "skills"))):
        if name in SKIP_SKILLS:
            continue
        target = os.path.join(claude, "skills", name)
        if os.path.isdir(target):
            shutil.rmtree(target)
        copy_tree_rewritten(os.path.join(PLUGIN, "skills", name), target)
        copied.append(f"skill {name}")
    for fn in sorted(os.listdir(os.path.join(PLUGIN, "agents"))):
        os.makedirs(os.path.join(claude, "agents"), exist_ok=True)
        with open(os.path.join(PLUGIN, "agents", fn), encoding="utf-8") as f:
            txt = rewrite(f.read())
        with open(os.path.join(claude, "agents", fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        copied.append(f"agente {fn[:-3]}")
    os.makedirs(os.path.join(claude, "hooks"), exist_ok=True)
    shutil.copy2(os.path.join(PLUGIN, "hooks", "check_asset.py"), os.path.join(claude, "hooks", "check_asset.py"))
    merge_settings(os.path.join(claude, "settings.json"))

    loaders, java, gradle_jvm, hosts = detect(dest)
    os.makedirs(os.path.join(claude, "cloud"), exist_ok=True)
    with open(os.path.join(claude, "cloud", "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(cloud_readme(loaders, java, gradle_jvm, hosts, version))
    with open(os.path.join(claude, "minecraft-modding.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"plugin": "minecraft-modding", "version": version,
                   "skills": sorted(c[6:] for c in copied if c.startswith("skill"))}, f, indent=2)
        f.write("\n")

    print(f"OK: plugin minecraft-modding {version} exportado a {claude}")
    print(f"  {sum(c.startswith('skill') for c in copied)} skills, {sum(c.startswith('agente') for c in copied)} agentes, hook en .claude/settings.json")
    print(f"  Loaders detectados: {', '.join(sorted(loaders)) or '?'} · Java del mod: {java or '?'}")
    print("  Configuración del entorno de nube: .claude/cloud/README.md")


if __name__ == "__main__":
    main()
