# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas>=2.0", "pyarrow", "matplotlib>=3.8", "geopandas>=1.0", "truststore"]
# ///
"""Mapa de pobreza por departamento con la ENAHO, unido por código de ubigeo.

Lee salidas/personas_<año>.parquet (lo arma la skill limpiando-enaho) y los límites de
los 25 departamentos (datos/peru_departamental_simple.geojson; si falta, lo baja).
Guarda:

    mapas/<indicador>_departamento_<año>.png   mapa + ranking, 200 dpi
    mapas/<indicador>_departamento_<año>.csv   la tabla detrás del mapa

Uso:
    uv run mapear.py --anio 2024
    uv run mapear.py --anio 2024 --indicador extrema

Reglas: une ubigeo[:2] con FIRST_IDDP (nunca por nombre), exige los 25 departamentos
con dato, Lima (15) y Callao (07) separados, un solo tono de claro a oscuro desde 0,
leyenda con la unidad y la fuente al pie.
"""
from __future__ import annotations

import argparse
import logging
import math
import sys
import urllib.request
from pathlib import Path

try:  # certificados del sistema (antivirus o proxy que inspeccionan HTTPS)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import matplotlib

matplotlib.use("Agg")
import geopandas as gpd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, Normalize  # noqa: E402

GEOJSON = "peru_departamental_simple.geojson"
URL_GEOJSON = ("https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/"
               "sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson")
CODIGOS = [f"{i:02d}" for i in range(1, 26)]

# Un solo tono (azul), de claro (cerca de 0) a oscuro. Nunca arcoíris.
RAMPA = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
TINTA, TINTA_2, TENUE = "#0b0b0b", "#52514e", "#898781"
FONDO = "#fcfcfb"

INDICADORES = {
    "pobreza": ("pobre", "Pobreza monetaria", "% de personas en situación de pobreza"),
    "extrema": ("pobre_extremo", "Pobreza extrema", "% de personas en pobreza extrema"),
}
# Pobreza 2024 con la base de personas y facpob07 (los tres más y menos pobres).
REFERENCIA_2024 = {"06": 45.0, "16": 42.6, "21": 40.4, "11": 5.9, "18": 10.9, "17": 11.1}
TOLERANCIA = 0.15


def buscar_raiz(inicio: Path) -> Path:
    for carpeta in [inicio, *inicio.parents]:
        if any((carpeta / d).is_dir() for d in ("salidas", "datos", ".claude")):
            return carpeta
    return inicio


def cargar_base(raiz: Path, anio: int) -> pd.DataFrame:
    base = raiz / "salidas" / f"personas_{anio}.parquet"
    validacion = raiz / "salidas" / f"validacion_{anio}.txt"
    if not base.exists():
        print(f"FALTA BASE: no existe salidas/personas_{anio}.parquet. "
              f"Usa primero la skill limpiando-enaho con el año {anio}.")
        sys.exit(3)
    if not validacion.exists() or "RESULTADO: OK" not in validacion.read_text(encoding="utf-8"):
        print(f"FALTA BASE: salidas/validacion_{anio}.txt no dice RESULTADO: OK. "
              f"Vuelve a correr la skill limpiando-enaho con el año {anio}.")
        sys.exit(3)
    return pd.read_parquet(base)


def cargar_limites(raiz: Path) -> gpd.GeoDataFrame:
    ruta = raiz / "datos" / GEOJSON
    if not ruta.exists():
        print(f"Bajando {GEOJSON}...")
        ruta.parent.mkdir(exist_ok=True)
        req = urllib.request.Request(URL_GEOJSON, headers={"User-Agent": "mapeando-enaho"})
        with urllib.request.urlopen(req, timeout=120) as r:
            ruta.write_bytes(r.read())
    geo = gpd.read_file(ruta)
    geo["codigo"] = geo["FIRST_IDDP"].astype(str).str.strip().str.zfill(2)
    return geo


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--indicador", default="pobreza", choices=list(INDICADORES))
    ap.add_argument("--raiz", type=Path, default=None)
    args = ap.parse_args()
    anio = args.anio
    raiz = (args.raiz or buscar_raiz(Path.cwd())).resolve()
    variable, nombre, unidad = INDICADORES[args.indicador]

    base = cargar_base(raiz, anio)
    geo = cargar_limites(raiz)

    # Pobreza ponderada por departamento (código, no nombre)
    d = base.assign(yw=base[variable].astype(float) * base["facpob07"])
    t = (d.groupby("departamento")
          .agg(nombre=("nombre_departamento", "first"), encuestados=("pobre", "size"),
               poblacion=("facpob07", "sum"), yw=("yw", "sum")))
    t["porcentaje"] = t["yw"] / t["poblacion"] * 100
    t = t.drop(columns="yw").reset_index()

    # Unión por código: ubigeo[:2] con FIRST_IDDP, uno a uno
    mapa = geo.merge(t, left_on="codigo", right_on="departamento", how="left", validate="1:1")

    pruebas = [
        ("El GeoJSON trae los 25 departamentos, 01 a 25",
         sorted(geo["codigo"]) == CODIGOS, f"{len(geo)} polígonos"),
        ("Los 25 departamentos tienen dato",
         int(mapa["porcentaje"].notna().sum()) == 25,
         f"sin dato: {mapa.loc[mapa['porcentaje'].isna(), 'NOMBDEP'].tolist()}"),
        ("Lima (15) y Callao (07) van separados",
         {"07", "15"} <= set(mapa.loc[mapa["porcentaje"].notna(), "codigo"]), ""),
    ]
    if anio == 2024 and args.indicador == "pobreza":
        por_codigo = t.set_index("departamento")["porcentaje"]
        for codigo, ref in REFERENCIA_2024.items():
            valor = float(por_codigo.get(codigo, float("nan")))
            pruebas.append((f"{t.set_index('departamento').loc[codigo, 'nombre']} igual a la referencia",
                            abs(valor - ref) <= TOLERANCIA, f"{valor:.1f} % vs {ref} %"))
    ok = all(p[1] for p in pruebas)
    for texto, bien, detalle in pruebas:
        print(f"[{'OK   ' if bien else 'FALLA'}] {texto}{': ' + detalle if detalle else ''}")
    if not ok:
        print("\nNo se hizo el mapa: la unión o las cifras no cuadran. Nunca unas por nombre.")
        return 1

    # Dibujo
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    plt.rcParams.update({"font.family": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
                         "figure.facecolor": FONDO, "savefig.facecolor": FONDO, "text.color": TINTA})
    cmap = LinearSegmentedColormap.from_list("un_tono", RAMPA)
    tope = math.ceil(mapa["porcentaje"].max() / 10) * 10
    norma = Normalize(vmin=0, vmax=tope)                # la escala empieza en 0

    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_axes([0.0, 0.07, 0.64, 0.82])
    mapa.to_crs(32718).plot(ax=ax, color=[cmap(norma(v)) for v in mapa["porcentaje"]],
                            edgecolor=FONDO, linewidth=0.8)
    ax.set_axis_off()

    barra = ax.inset_axes([0.06, 0.1, 0.38, 0.025])    # sobre el océano, abajo a la izquierda
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norma, cmap=cmap), cax=barra, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=9, colors=TINTA_2, length=0)
    cb.set_label(unidad, fontsize=9.5, color=TINTA_2, labelpad=6)

    # Ranking a la derecha: el valor de cada departamento, también Callao
    lista = fig.add_axes([0.66, 0.07, 0.31, 0.82])
    lista.set_axis_off()
    orden = t.sort_values("porcentaje", ascending=False).reset_index(drop=True)
    paso = 1 / len(orden)
    for i, fila in orden.iterrows():
        y = 1 - (i + 0.5) * paso
        lista.add_patch(plt.Rectangle((0, y - paso * 0.32), 0.05, paso * 0.64,
                                      color=cmap(norma(fila.porcentaje)), transform=lista.transAxes))
        lista.text(0.09, y, fila.nombre, va="center", fontsize=9.5, color=TINTA, transform=lista.transAxes)
        lista.text(0.98, y, f"{fila.porcentaje:.1f} %", va="center", ha="right", fontsize=9.5,
                   color=TINTA, transform=lista.transAxes)

    total = float((base[variable] * base["facpob07"]).sum() / base["facpob07"].sum() * 100)
    fig.text(0.03, 0.965, f"{nombre} por departamento, {anio}", fontsize=16, fontweight="bold", va="top")
    fig.text(0.03, 0.925, f"{unidad}. Perú: {total:.1f} %", fontsize=10.5, color=TINTA_2, va="top")
    fig.text(0.03, 0.025, f"Fuente: INEI, ENAHO {anio}. Residentes habituales, ponderado con facpob07. "
                          f"Límites departamentales unidos por código de ubigeo.",
             fontsize=8.5, color=TENUE)

    carpeta = raiz / "mapas"
    carpeta.mkdir(exist_ok=True)
    nombre_archivo = f"{args.indicador}_departamento_{anio}"
    png, csv = carpeta / f"{nombre_archivo}.png", carpeta / f"{nombre_archivo}.csv"
    fig.savefig(png, dpi=200)
    plt.close(fig)
    orden.round({"porcentaje": 2, "poblacion": 0}).to_csv(csv, index=False, encoding="utf-8")

    print(f"\n{nombre} por departamento, {anio}. Perú: {total:.2f} %")
    print("  Más:   " + " · ".join(f"{f.nombre} {f.porcentaje:.1f} %" for f in orden.head(3).itertuples()))
    print("  Menos: " + " · ".join(f"{f.nombre} {f.porcentaje:.1f} %" for f in orden.tail(3)[::-1].itertuples()))
    print(f"\nListo: {png.relative_to(raiz).as_posix()}")
    print(f"Listo: {csv.relative_to(raiz).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
