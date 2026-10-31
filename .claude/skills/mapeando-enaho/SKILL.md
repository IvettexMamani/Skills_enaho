---
name: mapeando-enaho
description: Hace el mapa de la pobreza monetaria o extrema por departamento del Perú con la ENAHO del INEI, uniendo por código de ubigeo con los límites de los 25 departamentos. Úsala cuando pidan un mapa o una coropleta de pobreza por departamento o región con la ENAHO.
argument-hint: "[año]"
---

# Mapear la ENAHO

1. El año es `$0`; si está vacío, usa 2024. Si piden pobreza extrema, agrega `--indicador extrema`.
2. Si no existe `salidas/personas_<año>.parquet`, usa primero la skill limpiando-enaho con ese año.
3. Corre exactamente: `uv run "${CLAUDE_SKILL_DIR}/scripts/mapear.py" --anio <año>`
   - Si dice FALTA BASE, usa la skill limpiando-enaho y vuelve a correr.
   - Si alguna línea dice FALLA, detente y muéstrala: la unión o las cifras no cuadran. Nunca unas por nombre ni completes un departamento a mano.
4. Abre el PNG con Read y míralo antes de responder.
5. Responde con la ruta del mapa y los tres departamentos con más y con menos pobreza que imprime el script.

## Reglas que fija el script

- Une `ubigeo[:2]` con `FIRST_IDDP`. Nunca por nombre: «APURIMAC» no es «Apurímac»
- Exige los 25 departamentos con dato; Lima (15) y Callao (07) van separados
- Un solo tono, de claro a oscuro, desde 0; nunca arcoíris
- Leyenda con la unidad: % de personas
- Ranking de los 25 al lado, para que Callao se lea aunque en el mapa no se vea
- En 2024 compara seis departamentos con la referencia: Cajamarca 45.0, Loreto 42.6, Puno 40.4, Ica 5.9, Moquegua 10.9 y Madre de Dios 11.1 %

Los límites están en `datos/peru_departamental_simple.geojson`; si faltan, el script los baja del repositorio del curso.
