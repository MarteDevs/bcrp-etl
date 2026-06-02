import pandas as pd
import logging

logger = logging.getLogger(__name__)

COLUMNAS_BASE = ["indicador", "periodo", "valor", "nombre_api", "fecha_carga"]

def parse_valor(valor_str: str) -> float | None:
    if not valor_str or valor_str.strip() == "n.d.":
        return None
    try:
        return float(valor_str.replace(",", "."))
    except ValueError:
        return None

def transform_serie(nombre: str, raw: dict) -> pd.DataFrame:
    if not raw.get("periods"):
        logger.info(f"  → {nombre}: 0 registros válidos")
        return pd.DataFrame(columns=COLUMNAS_BASE)
    registros = []
    for periodo in raw["periods"]:
        registros.append({
            "indicador":  nombre,
            "periodo":    periodo["name"],
            "valor":      parse_valor(periodo["values"][0]),
            "nombre_api": raw["config"]["series"][0]["name"],
        })
    df = pd.DataFrame(registros)
    df["fecha_carga"] = pd.Timestamp.now()
    df.dropna(subset=["valor"], inplace=True)
    logger.info(f"  -> {nombre}: {len(df)} registros válidos")
    return df

def _enriquecer(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.sort_values(["indicador", "periodo"]).reset_index(drop=True)
    df["variacion_pct"] = (
        df.groupby("indicador")["valor"].pct_change() * 100
    )
    df["media_movil_3m"] = (
        df.groupby("indicador")["valor"]
          .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )
    return df

def transform_all(raw_data: dict) -> pd.DataFrame:
    frames = []
    for nombre, raw in raw_data.items():
        frames.append(transform_serie(nombre, raw))
    if not frames:
        return pd.DataFrame(columns=COLUMNAS_BASE)
    df = pd.concat(frames, ignore_index=True)
    df = _enriquecer(df)
    return df