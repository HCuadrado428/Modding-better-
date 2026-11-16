# Modding-better · Plugin de Claude Code para modding de Minecraft

Plugin para **Claude Code** que convierte a Claude en un equipo de modding de Minecraft:

- **Versiones:** 1.20.1 → 1.21.11
- **Loaders:** Forge · NeoForge · Fabric · Quilt
- **Arte:** pixel art 16×16 (incluido, sin instalar nada más) y modelado 3D con **Blockbench**; **Aseprite** opcional

---

## ¿Qué incluye?

| Tipo | Nombre | Para qué sirve |
|---|---|---|
| Comando | `/minecraft-modding:mc-init` | Crea el `CLAUDE.md` de tu proyecto detectando modid, versiones y loaders |
| Comando | `/minecraft-modding:mc-doctor` | Comprueba Java, Python, Pillow, Git, Blockbench y Aseprite |
| Skill | `version-matrix` | Cambios que rompen código entre 1.20.1 y 1.21.11 |
| Skill | `fabric-modding` · `neoforge-modding` · `forge-modding` | Cómo se hace cada cosa en cada loader |
| Skill | `mixins` | Buenas prácticas de Mixins multiloader |
| Skill | `pixel-art-16x16` | Dibujar, revisar, validar y recolorear texturas (script `texgen.py`) |
| Skill | `blockbench-models` | Modelos de bloques, items y entidades |
| Subagente | `build-fixer` | Arregla builds rotos hasta que compilen |
| Subagente | `mod-porter` | Porta mods entre loaders y versiones |
| Subagente | `mixin-reviewer` | Revisa mixins (solo lectura) |
| Subagente | `api-researcher` | Verifica APIs en las fuentes y la doc oficial |
| Subagente | `texture-artist` | Texturas pixel art |
| Subagente | `model-artist` | Modelos 3D con Blockbench |
| MCP | `blockbench` | Conexión con Blockbench (se activa cuando Blockbench está abierto) |

Claude carga las skills solo cuando las necesita y delega en los subagentes de forma automática. También puedes pedírselo tú: *"usa el subagente mixin-reviewer"*.

---

## Instalación paso a paso

### Paso 1 · Requisitos

| Programa | ¿Obligatorio? | Descarga |
|---|---|---|
| **Claude Code** | Sí | https://code.claude.com/docs (sigue la guía de instalación) |
| **Git** | Sí | https://git-scm.com/downloads |
| **Java 21** (Temurin) | Sí | https://adoptium.net/ · Para 1.20.1–1.20.4 hace falta Java 17 (Gradle puede descargarlo solo) |
| **Python 3** + **Pillow** | Sí, para las texturas | https://www.python.org/downloads/ (en Windows marca *"Add python.exe to PATH"*) |
| **IntelliJ IDEA** Community + plugin *Minecraft Development* | Recomendado | https://www.jetbrains.com/idea/ |
| **Blockbench** (escritorio) | Recomendado, para 3D | https://www.blockbench.net/ |
| **Aseprite** | Opcional | https://www.aseprite.org/ |

Instala Pillow:

```bash
# Windows
py -m pip install pillow

# macOS / Linux
python3 -m pip install pillow
```

### Paso 2 · Añadir el marketplace e instalar el plugin

En una terminal:

```bash
claude plugin marketplace add HCuadrado428/Modding-better-
claude plugin install minecraft-modding@modding-better
```

O desde dentro de Claude Code:

```
/plugin marketplace add HCuadrado428/Modding-better-
/plugin install minecraft-modding@modding-better
```

Comprueba que se ha instalado:

```bash
claude plugin list
claude plugin details minecraft-modding
```

Debe aparecer `minecraft-modding@modding-better` como **enabled**.

> Si el repositorio es privado, Claude Code usa tus credenciales de Git. Asegúrate de que `git clone https://github.com/HCuadrado428/Modding-better-` funciona en tu terminal.

### Paso 3 · Conectar Blockbench (3D y pintar texturas)

1. Instala y abre **Blockbench de escritorio** (la versión web no sirve).
2. Ve a **File → Plugins → Load Plugin from URL** y pega:
   ```
   https://jasonjgardner.github.io/blockbench-mcp-plugin/mcp.js
   ```
3. Revisa en **Settings → General** que el puerto MCP es `3000` y el endpoint `/bb-mcp` (son los valores por defecto).
4. Para entidades animadas instala también el plugin **GeckoLib Animation Utils** desde *File → Plugins*.
5. Con Blockbench abierto, en Claude Code escribe `/mcp`: el servidor **blockbench** debe aparecer conectado.

> El plugin ya trae configurada la conexión. Si Blockbench está cerrado, verás `blockbench` como desconectado: es normal y no afecta al resto.

### Paso 4 · (Opcional) Conectar Aseprite

Para pixel art más avanzado (dithering, sombreado, animaciones):

1. Instala Aseprite (de pago, o compílalo gratis desde https://github.com/aseprite/aseprite).
2. Instala el servidor MCP siguiendo su README: https://github.com/diivi/aseprite-mcp
3. Regístralo en Claude Code con el comando que indica ese README (`claude mcp add aseprite ...`).

Sin Aseprite, el plugin dibuja igualmente con su script incluido.

### Paso 5 · Crear el proyecto del mod

El plugin funciona mejor con un proyecto **multiloader + multiversión**:

- **Stonecraft** (Stonecutter + Architectury; Fabric, Forge y NeoForge): https://stonecraft.meza.gg/
- o cualquier *MultiLoader-Template* con Stonecutter.

Versiones ancla recomendadas:

| Minecraft | Loaders | Java |
|---|---|---|
| 1.20.1 | Forge, Fabric | 17 |
| 1.21.1 | NeoForge, Fabric | 21 |
| 1.21.11 | NeoForge, Fabric (Forge opcional) | 21 |

Quilt: el jar de Fabric funciona en Quilt Loader, así que no necesita un módulo propio.

### Paso 6 · Preparar el proyecto para Claude

Abre una terminal **en la carpeta del proyecto**, arranca `claude` y ejecuta:

```
/minecraft-modding:mc-init
/minecraft-modding:mc-doctor
```

`mc-init` crea el `CLAUDE.md` del proyecto (o lo amplía si ya existe) y `mc-doctor` te dice qué falta instalar.

### Paso 7 · ¡A trabajar!

Ejemplos de peticiones:

- *"Añade un mineral de rubí con su bloque, item, textura, receta y generación en el mundo para todos los targets"*
- *"Porta el sistema de energía de Forge 1.20.1 a NeoForge 1.21.1"*
- *"El build de 1.21.11-fabric falla, arréglalo"*
- *"Haz la textura de una espada de rubí estilo vanilla"*
- *"Modela en Blockbench una mesa de trabajo de 16×12×16"*

---

## Actualizar y desinstalar

```bash
claude plugin marketplace update modding-better   # descarga la última versión del catálogo
claude plugin update minecraft-modding@modding-better
claude plugin uninstall minecraft-modding@modding-better
```

Reinicia Claude Code (o usa `/reload-plugins`) después de actualizar.

## Solución de problemas

| Problema | Solución |
|---|---|
| `Plugin not found in marketplace` | Usa exactamente `minecraft-modding@modding-better` |
| `python3` no existe (Windows) | Usa `py` o `python`; Claude lo detecta solo si se lo dices |
| `No module named PIL` | Instala Pillow (paso 1) |
| `blockbench` desconectado en `/mcp` | Abre Blockbench de escritorio con el plugin MCP cargado y comprueba el puerto 3000 |
| Claude inventa métodos que no existen | Pídele que use el subagente `api-researcher` y añade el caso a la skill correspondiente |

## Estructura del repositorio

```
.claude-plugin/marketplace.json          ← catálogo (marketplace "modding-better")
plugins/minecraft-modding/
  .claude-plugin/plugin.json             ← manifiesto del plugin
  .mcp.json                              ← conexión con Blockbench
  agents/                                ← 6 subagentes
  skills/                                ← 9 skills (incluidas mc-init y mc-doctor)
  templates/CLAUDE.md                    ← plantilla para tu proyecto
```

## Desarrollo del plugin

```bash
git clone https://github.com/HCuadrado428/Modding-better-
claude plugin validate ./Modding-better-
claude --plugin-dir ./Modding-better-/plugins/minecraft-modding   # probar sin instalar
```

Si cambias algo, sube `version` en `plugins/minecraft-modding/.claude-plugin/plugin.json` para que los usuarios reciban la actualización.

## Licencia

MIT © HCuadrado428
