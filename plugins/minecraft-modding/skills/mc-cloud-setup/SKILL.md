---
name: mc-cloud-setup
description: Prepara un repositorio de mod para usar el plugin minecraft-modding en Claude Code en la web (claude.ai/code) y en la app, copiando skills, subagentes y hook a .claude/ y generando la configuración del entorno de nube. Usar cuando el usuario ejecute /minecraft-modding:mc-cloud-setup o quiera usar el plugin desde la web o el móvil.
disable-model-invocation: true
---

# Usar el plugin en la web y en la app

Las sesiones en la nube **no instalan plugins** (ni los de tu PC ni los declarados en `.claude/settings.json`), pero **sí cargan** lo que hay en el repositorio: `CLAUDE.md`, `.claude/skills`, `.claude/agents` y los hooks de `.claude/settings.json`. Este comando copia el plugin ahí.

## Pasos
1. Comprueba que estás en la raíz del repositorio del mod (hay `build.gradle` o `build.gradle.kts`) y que el árbol de git está limpio (`git status`).
2. Ejecuta:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/mc-cloud-setup/scripts/export_to_repo.py" --dest .
   ```
   (en Windows `python` o `py`). Copia skills (sin `mc-new`, `mc-init` ni este), subagentes y el hook; reescribe las rutas del plugin a `.claude/...`; añade el hook a `.claude/settings.json` sin borrar lo que ya hubiera; y genera `.claude/cloud/README.md` con los dominios Maven detectados en los ficheros de Gradle y el setup script de Java.
3. Si el proyecto no tiene `CLAUDE.md`, créalo como lo haría `/minecraft-modding:mc-init` (lee la plantilla `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md` y adáptala al proyecto real: loader, versión, Java, convenciones de registro, tamaño de texturas, ramas y CI). Si ya existe, añade solo una sección corta que mencione las skills y subagentes disponibles.
4. Añade `.claude/settings.local.json` al `.gitignore` si no está.
5. Revisa `git status`, enseña al usuario el resumen y haz commit (en una rama si está en la rama principal).
6. Dile al usuario que configure el **entorno de nube** siguiendo `.claude/cloud/README.md` (red Custom con los dominios listados + setup script). Eso no se puede hacer desde el repositorio: se hace una vez en claude.ai/code.

## Notas
- Si el plugin también está instalado en el PC, en ese repo el hook se ejecutará dos veces (plugin + proyecto). Es inofensivo; si molesta, desactiva el plugin solo en ese repo con `claude plugin disable minecraft-modding@modding-better --scope local`.
- Para actualizar tras una versión nueva del plugin: vuelve a ejecutar este comando y haz commit.
