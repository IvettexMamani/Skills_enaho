# Referencia: base de personas de la ENAHO

## Qué hace `scripts/limpiar.py`

| Paso | Qué hace |
|---|---|
| 1 · Leer | `read_stata(convert_categoricals=False)`: códigos, no etiquetas |
| 2 · Normalizar | Columnas en minúscula; «aÑo» (llega como `a�o`) pasa a `anio`; llaves como texto con ceros |
| 3 · Filtrar | Residentes habituales: `(p204==1 & p205==2) \| (p204==2 & p206==1)` |
| 4 · Unir | `personas.merge(sumaria, on=["conglome","vivienda","hogar"], validate="m:1")` |
| 5 · Construir | `departamento`, `nombre_departamento`, `urbano`, `pobre`, `pobre_extremo` |
| 6 · Validar | Llaves únicas, ninguna fila perdida, 25 departamentos, pobreza = oficial ± 0.1 |
| 7 · Guardar | `salidas/personas_<año>.parquet` y `salidas/validacion_<año>.txt` (la base solo si todo da OK). `validacion.txt` es copia de la última corrida |

Busca los archivos dentro de `datos/`, donde los deja la skill descargando-enaho:
`datos/966-Modulo34/sumaria-2024.dta` y `datos/966-Modulo02/enaho01-2024-200.dta`.

## Variables de la base

Una fila por residente habitual. Trae todas las columnas del módulo 200 y, de la sumaria, las del hogar.

| Variable | Qué es |
|---|---|
| `conglome`, `vivienda`, `hogar`, `codperso` | Llaves, texto con ceros: «015009», «013», «11», «01» |
| `ubigeo` | Texto de 6 dígitos: «010101» |
| `departamento` | `ubigeo[:2]`, «01» a «25». Para unir con mapas, usa este código, no el nombre |
| `nombre_departamento` | Nombre con tildes, solo para mostrar |
| `urbano` | `estrato <= 5` |
| `pobre` | `pobreza <= 2` (pobre extremo o no extremo) |
| `pobre_extremo` | `pobreza == 1` |
| `pobreza` | 1 pobre extremo · 2 pobre no extremo · 3 no pobre |
| `facpob07` | Factor de expansión de personas. **Pondera toda cifra con este** |
| `factor07` | Factor de hogares (de la sumaria). No lo uses con la base de personas |
| `mieperho` | Miembros del hogar |
| `linea`, `linpe` | Línea de pobreza total y extrema del hogar (soles por persona al mes) |
| `gashog2d`, `inghog2d` | Gasto e ingreso anual del hogar |
| `p203` | Parentesco: 1 jefe/jefa · 2 esposo(a) · 3 hijo(a) · 4 yerno/nuera · 5 nieto(a) · 6 padres/suegros · 7 otros parientes · 8 trabajador del hogar · 9 pensionista · 10 otros no parientes · 11 hermano(a) |
| `p204`, `p205`, `p206` | ¿Miembro del hogar? · ¿Ausente 30 días o más? · ¿Presente 30 días o más? (1 sí, 2 no) |
| `p207` | Sexo: 1 hombre · 2 mujer |
| `p208a` | Edad en años |
| `dominio` | 1 costa norte · 2 costa centro · 3 costa sur · 4 sierra norte · 5 sierra centro · 6 sierra sur · 7 selva · 8 Lima Metropolitana |
| `estrato` | 1 a 5 urbano (de 500 000 a más hasta 2 000 habitantes) · 6 a 8 rural |
| `anio`, `mes` | Texto |

Si necesitas otra variable de la sumaria (163 columnas), únela por las llaves de hogar con `validate="m:1"`. El diccionario está en `datos/966-Modulo34/Diccionario2024.pdf`.

## Cómo ponderar

```python
import pandas as pd
base = pd.read_parquet("salidas/personas_2024.parquet")

def pobreza(d):
    return (d.pobre * d.facpob07).sum() / d.facpob07.sum() * 100

pobreza(base)                                   # 27.53 %
base.groupby("departamento").apply(pobreza, include_groups=False)
base.groupby("urbano").apply(pobreza, include_groups=False)
base.groupby("p207").apply(pobreza, include_groups=False)   # 1 hombre, 2 mujer
```

La cifra oficial del INEI se calcula con la sumaria, ponderando hogares por `factor07 × mieperho`: da 27.58 %. Con la base de personas y `facpob07` da 27.53 %. Las dos son correctas; di cuál usaste.

## Seis trampas

1. **Ceros a la izquierda.** `conglome` «015009», `ubigeo` «010101». Como número pierden el cero y las uniones fallan.
2. **Nombres rotos.** La columna del año llega como `a�o`. El script la renombra a `anio`.
3. **No todos son residentes.** 117,721 filas en el módulo 200; residentes habituales, 108,664.
4. **Uniones que duplican.** Sin `validate="m:1"`, un hogar repetido multiplica personas sin avisar.
5. **Encuestas no son personas.** 108,664 encuestados representan 34.1 millones de personas con `facpob07`. Nunca cuentes filas.
6. **Códigos, no números.** `pobreza` 1, 2 y 3 son categorías: pobre es `pobreza <= 2`, nunca un promedio.

## Cifras de referencia · ENAHO 2024

| Cifra | Sumaria (`factor07 × mieperho`) | Base de personas (`facpob07`) |
|---|---|---|
| Pobreza monetaria (oficial INEI: 27.6 %) | 27.58 % | 27.53 % |
| Pobreza extrema (oficial INEI: 5.5 %) | 5.50 % | — |
| Cusco | 18.5 % | 18.5 % |
| Urbano / rural | 24.8 % / 39.3 % | 24.7 % / 39.4 % |
| Más pobres | Cajamarca 45.0 · Loreto 43.0 · Puno 39.9 | Cajamarca 45.0 · Loreto 42.6 · Puno 40.4 |
| Menos pobres | Ica 6.0 · Moquegua 11.0 · Madre de Dios 11.1 | Ica 5.9 · Moquegua 10.9 · Madre de Dios 11.1 |

Si una cifra tuya se aleja más de unas décimas de estas, revisa el filtro, la unión o el peso.

## Otros años

`limpiar.py` valida contra la pobreza oficial de 2019 a 2024 (20.2, 30.1, 25.9, 27.5, 29.0 y 27.6 %).
Para otro año escribe un AVISO en `validacion.txt`: agrega la cifra del INEI a `POBREZA_OFICIAL`.
Códigos del INEI: 2019 = 687 · 2020 = 737 · 2021 = 759 · 2022 = 784 · 2023 = 906 · 2024 = 966 · 2025 = 1031.

Lima (15) incluye Lima Metropolitana y Lima Provincias; Callao (07) va aparte.
