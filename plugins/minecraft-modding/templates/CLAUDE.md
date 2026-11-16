# Proyecto de mod de Minecraft (multiloader / multiversión)

## Objetivo
- Versiones de Minecraft: **1.20.1 → 1.21.11** (todas ofuscadas; NO hay versiones 26.x en este proyecto).
- Loaders: **Fabric**, **NeoForge**, **Forge**. **Quilt** = el jar de Fabric probado en Quilt Loader (sin QSL).
- Versiones ancla (rellenar/ajustar):
  | MC | Loaders | Java |
  |----|---------|------|
  | 1.20.1 | Forge, Fabric | 17 |
  | 1.21.1 | NeoForge, Fabric | 21 |
  | 1.21.11 | NeoForge, Fabric (Forge opcional) | 21 |

## Estructura
- `common/` → lógica en vanilla (sin imports de ningún loader).
- `fabric/`, `neoforge/`, `forge/` → solo registro, eventos, entrypoints y metadatos.
- Multiversión con **Stonecutter** (comentarios `//? if >=1.21 {` … `//?}`), o Stonecraft si se usa Architectury.
- Mappings: **Mojang (official) + Parchment** en todos los loaders. En Fabric NO usar Yarn salvo que el proyecto ya lo use.

## Comandos
- Compilar todo: `./gradlew build`
- Compilar un target: `./gradlew :<version>-<loader>:build` (ajustar a tu template)
- Cambiar versión activa de Stonecutter: `./gradlew "Set active project to <version>-<loader>"`
- Probar: `runClient`, `runServer`, `runGameTestServer`
- Texturas: skill `minecraft-modding:pixel-art-16x16` (incluye el script texgen.py)

## Reglas de oro
1. **Nunca inventes una API.** Antes de usar una clase/método, compruébalo en las fuentes decompiladas de ESA versión (`./gradlew genSources` en Fabric; las fuentes de NeoForge/Forge se adjuntan en el IDE) o en la doc oficial.
2. Consulta la skill `minecraft-modding:version-matrix` antes de escribir código que dependa de la versión.
3. Un cambio no está terminado hasta que `./gradlew build` pasa en **todos** los targets afectados.
4. Lógica nueva → en `common/`. Si necesitas algo del loader, crea una interfaz en `common/` e impleméntala en cada loader.
5. Texturas: 16×16 PNG RGBA, revisa siempre la preview ampliada antes de darla por buena.
6. Delega en los subagentes del plugin: compilación rota → `minecraft-modding:build-fixer`; portar → `minecraft-modding:mod-porter`; mixins → `minecraft-modding:mixin-reviewer`; dudas de API → `minecraft-modding:api-researcher`; texturas → `minecraft-modding:texture-artist`; modelos 3D → `minecraft-modding:model-artist`.

## Mod
- modid: `{{MODID}}`
- paquete base: `{{PACKAGE}}`
- nombre: `{{MOD_NAME}}`
