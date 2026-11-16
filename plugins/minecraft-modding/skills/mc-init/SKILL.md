---
name: mc-init
description: Prepara el proyecto de mod actual para el plugin minecraft-modding creando su CLAUDE.md a partir de la plantilla. Usar cuando el usuario ejecute /minecraft-modding:mc-init o pida configurar el proyecto para Claude.
disable-model-invocation: true
argument-hint: "[modid]"
---

# Inicializar el proyecto de mod

Plantilla: `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md`

1. Comprueba que estás en la raíz de un proyecto Gradle (`settings.gradle(.kts)` o `build.gradle(.kts)`). Si no lo estás, dilo y recomienda crear antes el proyecto desde un template (Stonecraft: https://stonecraft.meza.gg/ o un MultiLoader-Template).
2. Detecta automáticamente leyendo `gradle.properties`, `settings.gradle*`, `stonecutter.gradle*`, `fabric.mod.json`, `neoforge.mods.toml` / `mods.toml`:
   - modid, nombre del mod y paquete base (usa `$ARGUMENTS` como modid si se pasó),
   - versiones de Minecraft y loaders configurados,
   - los comandos reales de build / run / datagen de este template.
3. Si ya existe un `CLAUDE.md`, NO lo sobrescribas: añade al final una sección `## Plugin minecraft-modding` con las reglas de oro y la tabla de versiones de la plantilla.
4. Si no existe, copia la plantilla, sustituye `{{MODID}}`, `{{PACKAGE}}` y `{{MOD_NAME}}`, y ajusta la tabla de versiones ancla y la sección de comandos con lo detectado.
5. Asegúrate de que `.gitignore` incluye `build/tex-preview/`.
6. Termina con un resumen corto de lo detectado y sugiere ejecutar `/minecraft-modding:mc-doctor`.
