# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas>=2.0", "pyarrow", "matplotlib>=3.8"]
# ///
"""Grafica la pobreza de la ENAHO por un corte, con reglas fijas.

Lee salidas/personas_<año>.parquet (lo arma la skill limpiando-enaho) y guarda:

    figuras/<indicador>_por_<corte>_<año>.png   barras, 200 dpi
    figuras/<indicador>_por_<corte>_<año>.csv   la tabla detrás del gráfico

Uso:
    uv run graficar.py --por area --anio 2024
    uv run graficar.py --por departamento --indicador extrema

Reglas: pondera con facpob07, barras desde cero y ordenadas, un solo color, el valor
escrito en cada barra, título con qué y cuándo, y la fuente al pie.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# Colores: un solo tono para las barras; el texto va en tinta, nunca en el color de la barra.
BARRA = "#2a78d6"
TINTA, TINTA_2, TENUE = "#0b0b0b", "#52514e", "#898781"
FONDO, EJE = "#fcfcfb", "#c3c2b7"

INDICADORES = {
    "pobreza": ("pobre", "Pobreza monetaria", "% de personas en situación de pobreza"),
    "extrema": ("pobre_extremo", "Pobreza extrema", "% de personas en pobreza extrema"),
}
CORTES = {
    "area": "por área de residencia",
    "sexo": "por sexo",
    "edad": "por grupo de edad",
    "departamento": "por departamento",
    "dominio": "por dominio geográfico",
}
DOMINIOS = {1: "Costa norte", 2: "Costa centro", 3: "Costa sur", 4: "Sierra norte",
            5: "Sierra centro", 6: "Sierra sur", 7: "Selva", 8: "Lima Metropolitana"}
EDADES = ([0, 18, 30, 45, 60, 200], ["0 a 17", "18 a 29", "30 a 44", "45 a 59", "60 y más"])


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


def agrupar(base: pd.DataFrame, por: str) -> tuple[pd.Series, bool]:
    """Devuelve la etiqueta de grupo de cada persona y si el orden es natural (ordinal)."""
    if por == "area":
        return base["urbano"].map({True: "Urbana", False: "Rural"}), False
    if por == "sexo":
        return base["p207"].map({1: "Hombre", 2: "Mujer"}), False
    if por == "edad":
        cortes, etiquetas = EDADES
        return pd.cut(base["p208a"], cortes, right=False, labels=etiquetas), True
    if por == "departamento":
        return base["nombre_departamento"], False
    if por == "dominio":
        return base["dominio"].map(DOMINIOS), False
    raise ValueError(por)


def tabla_ponderada(base: pd.DataFrame, grupo: pd.Series, variable: str, ordinal: bool) -> pd.DataFrame:
    d = pd.DataFrame({"grupo": grupo, "y": base[variable].astype(float), "w": base["facpob07"]})
    sin_grupo = d["grupo"].isna().sum()
    if sin_grupo:
        print(f"AVISO: {sin_grupo:,} personas sin dato para el corte; quedan fuera del gráfico.")
    d = d.dropna(subset=["grupo"])
    t = (d.assign(yw=d.y * d.w)
          .groupby("grupo", observed=True)
          .agg(encuestados=("y", "size"), poblacion=("w", "sum"), yw=("yw", "sum")))
    t["porcentaje"] = t["yw"] / t["poblacion"] * 100
    t = t.drop(columns="yw").reset_index()
    if not ordinal:
        t = t.sort_values("porcentaje", ascending=False)
    return t.reset_index(drop=True)


def estilo() -> None:
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    plt.rcParams.update({
        "font.family": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "figure.facecolor": FONDO, "axes.facecolor": FONDO, "savefig.facecolor": FONDO,
        "text.color": TINTA, "axes.edgecolor": EJE, "ytick.color": TINTA_2,
    })


def graficar(t: pd.DataFrame, titulo: str, subtitulo: str, fuente: str, destino: Path) -> None:
    estilo()
    n = len(t)
    alto = max(3.0, 0.4 * n + 1.7)                      # pulgadas
    fig, ax = plt.subplots(figsize=(8, alto))
    fig.subplots_adjust(left=0.22, right=0.95, top=1 - 1.0 / alto, bottom=0.55 / alto)

    y = range(n)
    ax.barh(y, t["porcentaje"], height=0.62, color=BARRA, zorder=2)
    ax.set_yticks(list(y), t["grupo"].astype(str), fontsize=10.5)
    ax.set_ylim(n - 0.5, -0.5)                          # el primero arriba, sin aire extra
    tope = t["porcentaje"].max()
    ax.set_xlim(0, tope * 1.14)                         # las barras empiezan en cero
    for yi, v in zip(y, t["porcentaje"]):
        ax.text(v + tope * 0.012, yi, f"{v:.1f} %", va="center", ha="left", fontsize=10, color=TINTA)

    ax.xaxis.set_visible(False)                         # el valor va escrito en cada barra
    for lado in ("top", "right", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.spines["left"].set_color(EJE)
    ax.tick_params(axis="y", length=0, pad=6)

    fig.text(0.02, 1 - 0.22 / alto, titulo, ha="left", va="top", fontsize=14, fontweight="bold")
    fig.text(0.02, 1 - 0.52 / alto, subtitulo, ha="left", va="top", fontsize=10, color=TINTA_2)
    fig.text(0.02, 0.16 / alto, fuente, ha="left", va="bottom", fontsize=8.5, color=TENUE)
    fig.savefig(destino, dpi=200)
    plt.close(fig)


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--por", required=True, choices=list(CORTES))
    ap.add_argument("--anio", type=int, default=2024)
    ap.add_argument("--indicador", default="pobreza", choices=list(INDICADORES))
    ap.add_argument("--raiz", type=Path, default=None)
    args = ap.parse_args()
    raiz = (args.raiz or buscar_raiz(Path.cwd())).resolve()

    base = cargar_base(raiz, args.anio)
    variable, nombre, unidad = INDICADORES[args.indicador]
    grupo, ordinal = agrupar(base, args.por)
    t = tabla_ponderada(base, grupo, variable, ordinal)
    total = float((base[variable] * base["facpob07"]).sum() / base["facpob07"].sum() * 100)

    titulo = f"{nombre} {CORTES[args.por]}, {args.anio}"
    subtitulo = f"{unidad}. Perú: {total:.1f} %"
    fuente = (f"Fuente: INEI, ENAHO {args.anio}. Residentes habituales, ponderado con el "
              f"factor de expansión de personas (facpob07).")

    carpeta = raiz / "figuras"
    carpeta.mkdir(exist_ok=True)
    nombre_archivo = f"{args.indicador}_por_{args.por}_{args.anio}"
    png, csv = carpeta / f"{nombre_archivo}.png", carpeta / f"{nombre_archivo}.csv"
    graficar(t, titulo, subtitulo, fuente, png)
    t.round({"porcentaje": 2, "poblacion": 0}).to_csv(csv, index=False, encoding="utf-8")

    print(titulo)
    print(f"Perú: {total:.2f} %")
    for _, fila in t.iterrows():
        print(f"  {str(fila.grupo):<22} {fila.porcentaje:6.2f} %   ({fila.encuestados:,} encuestados)")
    print(f"\nListo: {png.relative_to(raiz).as_posix()}")
    print(f"Listo: {csv.relative_to(raiz).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
