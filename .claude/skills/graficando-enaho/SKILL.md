---
name: graficando-enaho
description: Grafica la pobreza monetaria o extrema de la ENAHO del INEI en barras ponderadas por área urbana y rural, sexo, grupo de edad, departamento o dominio, siempre con las mismas reglas de diseño. Úsala cuando pidan un gráfico, una figura o barras de pobreza con la ENAHO.
argument-hint: "[corte] [año]"
---

# Graficar la ENAHO

1. Los argumentos son `$ARGUMENTS`: un corte y un año de 4 dígitos, en cualquier orden y ambos opcionales. Cortes: `area`, `sexo`, `edad`, `departamento`, `dominio`. Si falta el año, usa 2024. Si falta el corte, sácalo del pedido; si el pedido tampoco lo dice, haz los cinco. Si piden pobreza extrema, agrega `--indicador extrema`.
2. Si no existe `salidas/personas_<año>.parquet`, usa primero la skill limpiando-enaho con ese año.
3. Corre exactamente: `uv run "${CLAUDE_SKILL_DIR}/scripts/graficar.py" --por <corte> --anio <año>`
   - Si dice FALTA BASE, usa la skill limpiando-enaho y vuelve a correr.
4. Abre el PNG con Read y míralo antes de responder: etiquetas encimadas o cortadas son un error.
5. Responde con las cifras que imprime el script y la ruta de la figura.

## Si el pedido no cabe en el script

Para otro corte (por ejemplo, jefes de hogar o nivel educativo), hazlo tú con matplotlib a partir de la misma base, con estas reglas:

- Pondera siempre con `facpob07`; pobre es `pobre`, nunca un promedio de `pobreza`
- Barras que empiezan en cero, ordenadas de mayor a menor (las edades, en su orden natural)
- Un solo color (`#2a78d6`) y el valor escrito en cada barra
- El título dice qué y cuándo: «Pobreza monetaria por sexo, 2024»
- Nota al pie: «Fuente: INEI, ENAHO <año>»
- PNG a 200 dpi en `figuras/`, con la tabla en un .csv al lado

Las variables y sus códigos están en `.claude/skills/limpiando-enaho/reference.md`.
