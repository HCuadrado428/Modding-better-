# Modding-better · Plugin de Claude Code para modding de Minecraft

Plugin para **Claude Code** que convierte a Claude en un equipo de modding de Minecraft:

- **Versiones:** 1.20.1 → 1.21.11
- **Loaders:** Forge · NeoForge · Fabric · Quilt
- **Arte:** pixel art 16×16 (incluido, sin instalar nada más) y modelado 3D con **Blockbench**; **Aseprite** opcional

---

## ¿Qué incluye?

| Tipo | Nombre | Para qué sirve |
|---|---|---|
| Comando | `/minecraft-modding:mc-new` | Crea un mod nuevo multiloader y multiversión desde la plantilla incluida |
| Comando | `/minecraft-modding:mc-init` | Crea el `CLAUDE.md` de tu proyecto detectando modid, versiones y loaders |
| Comando | `/minecraft-modding:mc-doctor` | Comprueba Java, Python, Pillow, Git, Blockbench y Aseprite |
| Skill | `version-matrix` | Cambios que rompen código entre 1.20.1 y 1.21.11 |
| Skill | `fabric-modding` · `neoforge-modding` · `forge-modding` | Cómo se hace cada cosa en cada loader |
| Skill | `mixins` | Buenas prácticas de Mixins multiloader |
| Skill | `pixel-art-16x16` | Dibujar, revisar, validar y recolorear texturas (script `texgen.py`) |
| Skill | `blockbench-models` | Modelos de bloques, items y entidades |
| Skill | `worldgen` | Minerales, features, biome modifiers y estructuras |
| Skill | `datagen` | Generar modelos, recetas, tags, loot y traducciones por código |
| Skill | `gui-screens` | Pantallas y menús con inventario |
| Skill | `networking` | Paquetes cliente-servidor en cada loader y versión |
| Skill | `geckolib` | Entidades, bloques e items animados con GeckoLib 4/5 |
| Skill | `mod-config` | Ficheros y pantallas de configuración |
| Skill | `gametests` | Tests automáticos dentro del juego (incluido el sistema de 1.21.5+) |
| Skill | `publishing` | Publicar en Modrinth y CurseForge con GitHub Actions |
| Subagente | `build-fixer` | Arregla builds rotos hasta que compilen |
| Subagente | `mod-porter` | Porta mods entre loaders y versiones |
| Subagente | `mixin-reviewer` | Revisa mixins (solo lectura) |
| Subagente | `api-researcher` | Verifica APIs en las fuentes y la doc oficial |
| Subagente | `texture-artist` | Texturas pixel art |
| Subagente | `model-artist` | Modelos 3D con Blockbench |
| Hook | Validación automática | Cada PNG o JSON de recursos que Claude escribe se revisa al momento (ver abajo) |
| MCP | `blockbench` | Conexión con Blockbench (se activa cuando Blockbench está abierto) |
| Plantilla | `templates/mod` | Proyecto Stonecraft para 1.20.1 / 1.21.1 / 1.21.11 con Fabric, Forge y NeoForge, compilado en CI |

### Validación automática (hook)

Cada vez que Claude crea o edita un fichero dentro de `assets/` o `data/`, el plugin lo revisa sin que tengas que pedirlo:

| Comprobación | Resultado si falla |
|---|---|
| Ruta con mayúsculas o caracteres no válidos | Error: Claude debe corregirlo |
| JSON mal formado, valores de `lang` que no son texto | Error |
| Textura de item/bloque que no mide 16, 32, 64… o tira de animación sin `.mcmeta` | Error / aviso |
| Modelo con cubos fuera de -16…32 o rotaciones no estándar | Error / aviso |
| Modelo, blockstate o definición de item que apunta a una textura/modelo que no existe | Aviso |
| Carpetas de `data/` en plural (`tags/blocks`, `recipes`…) que en 1.21+ van en singular | Aviso |

Necesita Python (y Pillow para las imágenes). Si no hay Python, el hook no hace nada y no molesta.

Claude carga las skills solo cuando las necesita y delega en los subagentes de forma automática. También puedes pedírselo tú: *"usa el subagente mixin-reviewer"*.

---

## Instalación paso a paso

### Paso 1 · Requisitos

| Programa | ¿Obligatorio? | Descarga |
|---|---|---|
| **Claude Code** | Sí | https://code.claude.com/docs (sigue la guía de instalación) |
| **Git** | Sí | https://git-scm.com/downloads |
| **Java 25** (Temurin) | Sí | https://adoptium.net/ · Ejecuta Gradle en la plantilla. Los targets compilan con Java 21 (1.20.5+) y 17 (1.20.1); instálalos también o deja que Gradle los descargue |
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

Abre una terminal en la carpeta donde guardas tus proyectos, arranca `claude` y escribe:

```
/minecraft-modding:mc-new rubymod
```

Claude te pedirá nombre, paquete, autor y descripción, y creará la carpeta `rubymod/` con un proyecto **multiloader + multiversión** (Stonecraft + Stonecutter) ya preparado: un ítem de ejemplo con textura, CI de GitHub y publicación en Modrinth/CurseForge.

Primer build (tarda varios minutos porque descarga Minecraft para cada target):

```bash
cd rubymod
./gradlew buildAndCollect        # Windows: gradlew.bat buildAndCollect
```

Los `.jar` aparecen en `build/libs/`. Para abrirlo en IntelliJ IDEA: *File → Open* → la carpeta del proyecto.

¿Prefieres otra base? También puedes usar el generador web de Stonecraft (https://stonecraft.meza.gg/) o un *MultiLoader-Template*; el resto del plugin funciona igual.

Versiones de la plantilla:

| Minecraft | Loaders | Java |
|---|---|---|
| 1.20.1 | Forge, Fabric | 17 |
| 1.21.1 | NeoForge, Fabric | 21 |
| 1.21.11 | NeoForge, Fabric (Forge opcional) | 21 |

Quilt: el jar de Fabric funciona en Quilt Loader, así que no necesita un módulo propio.

### Paso 6 · Preparar el proyecto para Claude

Abre una terminal **en la carpeta del proyecto** (`cd rubymod`), arranca `claude` y ejecuta:

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
- *"Haz que el mineral de rubí aparezca entre las capas -32 y 48"*
- *"Crea una máquina con inventario de 1 entrada y 1 salida y su pantalla"*
- *"Prepara la publicación en Modrinth y CurseForge"*

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
| `Dependency requires at least JVM runtime version 25` | Gradle se está ejecutando con Java 21 o anterior: instala Java 25 y ponlo en `JAVA_HOME` (o en IntelliJ: *Settings → Gradle → Gradle JVM*) |
| El primer build tarda mucho | Normal: descarga y prepara Minecraft para los 6 targets. Los siguientes van mucho más rápido |
| Un aviso del hook que no aplica a tu versión | Los avisos de carpetas plural/singular dependen del target: si tu mod solo es para 1.20.1, ignóralo |

## Estructura del repositorio

```
.claude-plugin/marketplace.json          ← catálogo (marketplace "modding-better")
plugins/minecraft-modding/
  .claude-plugin/plugin.json             ← manifiesto del plugin
  .mcp.json                              ← conexión con Blockbench
  hooks/                                 ← validación automática de recursos
  agents/                                ← 6 subagentes
  skills/                                ← 18 skills (incluidas mc-new, mc-init y mc-doctor)
  templates/CLAUDE.md                    ← plantilla de CLAUDE.md para tu proyecto
  templates/mod/                         ← plantilla de proyecto Stonecraft (compilada en CI)
tests/                                   ← tests de los scripts y del hook
.github/workflows/ci.yml                 ← valida el plugin, pasa los tests y compila la plantilla
```

## Desarrollo del plugin

```bash
git clone https://github.com/HCuadrado428/Modding-better-
claude plugin validate ./Modding-better-
python -m unittest discover -s Modding-better-/tests   # tests de scripts y hook
claude --plugin-dir ./Modding-better-/plugins/minecraft-modding   # probar sin instalar
```

Si cambias algo, sube `version` en `plugins/minecraft-modding/.claude-plugin/plugin.json` para que los usuarios reciban la actualización.

## Licencia

MIT © HCuadrado428
