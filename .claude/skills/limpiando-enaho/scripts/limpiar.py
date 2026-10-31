# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas>=2.0", "pyarrow"]
# ///
"""Limpia la ENAHO del INEI y arma una base de personas residentes con su pobreza.

Une el módulo 02 (miembros, una fila por persona) con el módulo 34 (sumaria, una fila
por hogar), valida el resultado contra la pobreza oficial del INEI y guarda:

    salidas/personas_<año>.parquet
    salidas/validacion.txt

Uso:
    uv run limpiar.py --anio 2024
    uv run limpiar.py --anio 2024 --raiz "ruta/al/proyecto"

Busca los .dta dentro de datos/ (por ejemplo datos/966-Modulo34/sumaria-2024.dta).
Si solo están los zip del INEI, los descomprime primero.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVES_PERSONA = LLAVES_HOGAR + ["codperso"]
# Las llaves son texto con ceros a la izquierda: conglome «015009», ubigeo «010101».
ANCHO = {"conglome": 6, "vivienda": 3, "hogar": 2, "codperso": 2, "ubigeo": 6}

# De la sumaria solo se trae lo que define la pobreza del hogar.
VARS_SUMARIA = ["pobreza", "mieperho", "factor07"]
VARS_SUMARIA_OPCIONALES = ["linea", "linpe", "gashog2d", "inghog2d"]

# Pobreza monetaria oficial del INEI, % de la población.
POBREZA_OFICIAL = {2019: 20.2, 2020: 30.1, 2021: 25.9, 2022: 27.5, 2023: 29.0, 2024: 27.6}
TOLERANCIA = 0.1

DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
    "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}


def buscar_raiz(inicio: Path) -> Path:
    """El proyecto es la primera carpeta, desde aquí hacia arriba, que tiene datos/."""
    for carpeta in [inicio, *inicio.parents]:
        if (carpeta / "datos").is_dir():
            return carpeta
    return inicio


def buscar_dta(datos: Path, nombre: str, modulo: str) -> Path:
    """Encuentra un .dta por nombre (sin importar mayúsculas); si falta, abre el zip."""
    def encontrados():
        return [p for p in datos.rglob("*.dta") if p.name.lower() == nombre.lower()]

    rutas = encontrados()
    if not rutas:
        for z in sorted(datos.glob(f"*-{modulo}.zip")):
            with zipfile.ZipFile(z) as zf:
                if any(Path(n).name.lower() == nombre.lower() for n in zf.namelist()):
                    print(f"Descomprimiendo {z.name}")
                    zf.extractall(datos)
        rutas = encontrados()
    if not rutas:
        sys.exit(f"ERROR: falta {nombre} en {datos}. Baja el zip {modulo} del INEI "
                 f"(proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/<código>-{modulo}.zip) "
                 f"y déjalo en datos/.")
    if len(rutas) > 1:
        sys.exit(f"ERROR: hay más de un {nombre}: {[str(r) for r in rutas]}. Deja solo uno.")
    return rutas[0]


# 1 · Leer -------------------------------------------------------------------------
def leer(ruta: Path) -> pd.DataFrame:
    """Lee el .dta con códigos, no etiquetas."""
    return pd.read_stata(ruta, convert_categoricals=False)


# 2 · Normalizar --------------------------------------------------------------------
def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    """Columnas en minúscula, «aÑo» (con la eñe rota) pasa a anio y llaves como texto."""
    df = df.rename(columns=lambda c: c.strip().lower())
    df = df.rename(columns=lambda c: "anio" if re.fullmatch(r"a[^a-z0-9_]{1,2}o", c) else c)
    for col, ancho in ANCHO.items():
        if col in df:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].astype("Int64").astype(str)
            df[col] = df[col].astype(str).str.strip().str.zfill(ancho)
    return df


# 3 · Filtrar -----------------------------------------------------------------------
def residentes(personas: pd.DataFrame) -> pd.DataFrame:
    """Residentes habituales, definición del INEI: miembros no ausentes 30 días o más
    (p204==1 & p205==2) y no miembros presentes 30 días o más (p204==2 & p206==1)."""
    filtro = ((personas.p204 == 1) & (personas.p205 == 2)) | \
             ((personas.p204 == 2) & (personas.p206 == 1))
    return personas.loc[filtro].copy()


def pct(valor: pd.Series, peso: pd.Series) -> float:
    return float((valor * peso).sum() / peso.sum() * 100)


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):    # tildes legibles en la consola de Windows
        flujo.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--raiz", type=Path, default=None, help="carpeta del proyecto (la que tiene datos/)")
    args = ap.parse_args()
    anio = args.anio
    raiz = (args.raiz or buscar_raiz(Path.cwd())).resolve()
    datos, salidas = raiz / "datos", raiz / "salidas"
    if not datos.is_dir():
        sys.exit(f"ERROR: no encuentro la carpeta datos/ en {raiz} ni más arriba.")

    ruta_sumaria = buscar_dta(datos, f"sumaria-{anio}.dta", "Modulo34")
    ruta_personas = buscar_dta(datos, f"enaho01-{anio}-200.dta", "Modulo02")
    print(f"Sumaria:  {ruta_sumaria.relative_to(raiz)}")
    print(f"Miembros: {ruta_personas.relative_to(raiz)}")

    # 1-2 · Leer y normalizar
    sumaria = normalizar(leer(ruta_sumaria))
    personas_todas = normalizar(leer(ruta_personas))

    # 3 · Filtrar
    personas = residentes(personas_todas)

    # 4 · Unir: muchas personas a un hogar; si no es m:1, pandas falla en vez de duplicar
    cols = LLAVES_HOGAR + VARS_SUMARIA + [c for c in VARS_SUMARIA_OPCIONALES if c in sumaria]
    faltan = [c for c in LLAVES_HOGAR + VARS_SUMARIA if c not in sumaria]
    if faltan:
        sys.exit(f"ERROR: a la sumaria le faltan {faltan}")
    base = personas.merge(sumaria[cols], on=LLAVES_HOGAR, how="left",
                          validate="m:1", indicator=True)

    # 5 · Construir
    base["departamento"] = base["ubigeo"].str[:2]
    base["nombre_departamento"] = base["departamento"].map(DEPARTAMENTOS)
    base["urbano"] = base["estrato"] <= 5
    base["pobre"] = base["pobreza"] <= 2           # 1 extremo, 2 no extremo, 3 no pobre
    base["pobre_extremo"] = base["pobreza"] == 1

    # 6 · Validar
    peso_hogar = sumaria["factor07"] * sumaria["mieperho"]
    pob_sumaria = pct(sumaria["pobreza"] <= 2, peso_hogar)
    ext_sumaria = pct(sumaria["pobreza"] == 1, peso_hogar)
    pob_personas = pct(base["pobre"], base["facpob07"])
    oficial = POBREZA_OFICIAL.get(anio)

    pruebas = [
        ("Llaves de hogar únicas en la sumaria",
         not sumaria.duplicated(LLAVES_HOGAR).any(), f"{len(sumaria):,} hogares"),
        ("Llaves de persona únicas",
         not personas.duplicated(LLAVES_PERSONA).any(), f"{len(personas):,} residentes habituales "
         f"de {len(personas_todas):,} filas del módulo 200"),
        ("La unión no perdió ni duplicó filas",
         len(base) == len(personas), f"{len(base):,} filas en la base"),
        ("Todas las personas encontraron su hogar",
         bool((base["_merge"] == "both").all()) and not base["pobreza"].isna().any(),
         f"{int((base['_merge'] != 'both').sum())} sin hogar"),
        ("Los 25 departamentos tienen dato",
         set(base["departamento"]) == set(DEPARTAMENTOS), f"{base['departamento'].nunique()} departamentos"),
    ]
    if oficial is not None:
        pruebas.append(("Pobreza igual a la oficial del INEI",
                        abs(pob_sumaria - oficial) < TOLERANCIA,
                        f"{pob_sumaria:.2f} % vs {oficial} % (tolerancia {TOLERANCIA} puntos)"))
    base = base.drop(columns="_merge")
    ok = all(p[1] for p in pruebas)

    lineas = [f"Validación ENAHO {anio}", ""]
    lineas += [f"[{'OK   ' if bien else 'FALLA'}] {nombre}: {detalle}" for nombre, bien, detalle in pruebas]
    if oficial is None:
        lineas.append(f"[AVISO] No hay cifra oficial cargada para {anio}: agrégala en POBREZA_OFICIAL "
                      f"de limpiar.py. Calculada: {pob_sumaria:.2f} %")
    lineas += [
        "",
        "Cifras",
        f"  Pobreza monetaria (sumaria, factor07 × mieperho): {pob_sumaria:.2f} %",
        f"  Pobreza monetaria (base de personas, facpob07):   {pob_personas:.2f} %",
        f"  Pobreza extrema (sumaria):                        {ext_sumaria:.2f} %",
        f"  Población que representa la base (facpob07):      {base['facpob07'].sum():,.0f}",
        "",
        f"RESULTADO: {'OK' if ok else 'FALLA, no uses la base'}",
    ]
    texto = "\n".join(lineas)
    salidas.mkdir(exist_ok=True)
    validacion = salidas / f"validacion_{anio}.txt"
    validacion.write_text(texto + "\n", encoding="utf-8")
    (salidas / "validacion.txt").write_text(texto + "\n", encoding="utf-8")  # la última corrida
    print(texto)

    if not ok:
        print(f"\nNo se guardó la base. Revisa {validacion}")
        return 1

    # 7 · Guardar
    destino = salidas / f"personas_{anio}.parquet"
    base.to_parquet(destino, index=False)
    print(f"\nListo: {destino}")
    print(f"Listo: {validacion}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
