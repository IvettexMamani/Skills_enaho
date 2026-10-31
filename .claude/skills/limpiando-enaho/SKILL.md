---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma una base de personas con pobreza y factor de expansión, validada contra la pobreza oficial. Úsala cuando pidan limpiar, unir o analizar la ENAHO, o calcular pobreza por región, departamento, área, sexo o edad.
argument-hint: "[año]"
---

# Limpiar la ENAHO

1. El año es `$0`; si está vacío, usa 2024. Si ya existen `salidas/personas_<año>.parquet` y `salidas/validacion_<año>.txt` termina en `RESULTADO: OK`, salta al paso 4.
2. Corre exactamente: `uv run "${CLAUDE_SKILL_DIR}/scripts/limpiar.py" --anio <año>`
   - Si dice que faltan los .dta, usa la skill descargando-enaho para bajar ese año y vuelve a correr. Si no está instalada, pide al usuario bajar los zip del INEI a `datos/`. No escribas otra limpieza a mano.
3. Lee `salidas/validacion_<año>.txt`. Si alguna línea dice FALLA, o la pobreza difiere del INEI en más de 0.1 puntos, detente y muéstrale al usuario la validación.
4. Responde con `salidas/personas_<año>.parquet`; toda cifra va ponderada con `facpob07`. Pobre es `pobre` (pobreza ≤ 2), nunca un promedio del código.
5. Antes de usar una variable que no está en la base, o para comparar con las cifras de referencia, lee [reference.md](reference.md).
