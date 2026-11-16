---
name: mc-new
description: Crea un proyecto de mod nuevo multiloader y multiversión (Fabric, NeoForge, Forge; 1.20.1, 1.21.1, 1.21.11) desde la plantilla del plugin. Usar cuando el usuario ejecute /minecraft-modding:mc-new o pida empezar un mod desde cero.
disable-model-invocation: true
argument-hint: "<modid> [carpeta]"
---

# Crear un mod nuevo desde la plantilla

Plantilla: `${CLAUDE_PLUGIN_ROOT}/templates/mod/` (Stonecraft + Stonecutter, compilada en CI para los 6 targets).
Script: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/mc-new/scripts/new_mod.py"` (en Windows `python` o `py`).

## Pasos
1. Reúne los datos (pregunta solo lo que falte; `$ARGUMENTS` puede traer el modid y la carpeta):
   - **modid**: minúsculas, números y `_`, 2–64 caracteres, empieza por letra (p. ej. `rubymod`).
   - **nombre** visible (p. ej. "Ruby Mod"), **grupo/paquete** (p. ej. `io.github.usuario`), **autor**, **descripción** corta.
   - **carpeta** destino (por defecto `./<modid>`). Debe no existir o estar vacía.
2. Ejecuta el script:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/mc-new/scripts/new_mod.py" --modid rubymod --name "Ruby Mod" \
     --group io.github.usuario --author "Usuario" --description "Añade rubíes" --dest ./rubymod
   ```
   Copia la plantilla, renombra paquete/clase/carpetas de assets y sustituye todos los marcadores.
3. Entra en la carpeta, `git init`, y ejecuta `/minecraft-modding:mc-init` para crear su `CLAUDE.md`.
4. Explica al usuario cómo compilar: necesita **Java 25** para ejecutar Gradle (además de 17 y 21, que Gradle puede descargar solo):
   - `./gradlew buildAndCollect` (Windows: `gradlew.bat buildAndCollect`) → jars en `build/libs/`.
   - Abrir en IntelliJ IDEA: *Open* la carpeta → esperar la sincronización de Gradle.
   - Cambiar la versión/loader activa: tarea de Stonecutter "Set active project to 1.21.1-neoforge" (panel de Gradle → stonecutter).
5. Recuerda que el primer build descarga Minecraft para cada target y tarda varios minutos.

## Qué incluye el proyecto
- Targets: 1.20.1 (Fabric, Forge), 1.21.1 (Fabric, NeoForge), 1.21.11 (Fabric, NeoForge). Se cambian en `settings.gradle.kts` + `versions/dependencies/*.properties`.
- Item de ejemplo "ruby" con textura, modelo, definición de item (1.21.4+) y traducciones en/es: muestra los cambios `ResourceLocation`→`Identifier` y `setId` (1.21.2+).
- `.github/workflows/build.yml`: compila en cada push y publica en Modrinth/CurseForge al crear una Release (ver skill `minecraft-modding:publishing`).
