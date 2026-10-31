---
name: descargando-enaho
description: Descarga la ENAHO anual del portal de microdatos del INEI (módulo 34 sumaria y módulo 02 miembros, en Stata) y la deja descomprimida en datos/. Úsala cuando pidan bajar o descargar la ENAHO, cuando falten los zip o los .dta de la ENAHO en datos/, o antes de limpiar un año que todavía no está bajado.
argument-hint: "[año]"
---

# Descargar la ENAHO

1. El año es `$0`; si está vacío, usa 2024.
2. Corre exactamente: `uv run "${CLAUDE_SKILL_DIR}/scripts/descargar.py" --anio <año>`
3. Si termina con dos líneas «Listo», reporta las dos rutas. Si el usuario quería limpiar o analizar ese año, sigue con la skill limpiando-enaho.
4. Si dice NO PUBLICADO, dile al usuario que el INEI todavía no publica ese año. No inventes un código ni pruebes números en la URL.
5. Baja solo los módulos 34 y 02 en Stata. Otros módulos u otros formatos, solo si el usuario los pide: agrega `--modulos 34 02 05` o `--formato CSV` (o `SPSS`).

## Qué queda en datos/

| Ruta | Qué es |
|---|---|
| `datos/<código>-Modulo34/sumaria-<año>.dta` | Sumaria: una fila por hogar, con `pobreza` y `factor07` |
| `datos/<código>-Modulo02/enaho01-<año>-200.dta` | Miembros: una fila por persona, con `facpob07` |
| `datos/<código>-Modulo34/Diccionario<año>.pdf` | Diccionario de variables |
| `datos/<código>-ModuloNN.zip` | El zip original; si ya está completo, no se vuelve a bajar |

La sumaria trae también `sumaria-<año>-12g.dta` (12 grupos de gasto). No es la que se usa para la pobreza oficial.

## Códigos del INEI

Estos ya están verificados. Para otro año, el script consulta el portal (encuesta «Condiciones de Vida y Pobreza - ENAHO», período «Anual - (Ene-Dic)»):

| Año | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Código | 687 | 737 | 759 | 784 | 906 | 966 | 1031 |
