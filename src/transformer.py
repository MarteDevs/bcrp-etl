import pandas as pd
import logging

logger = logging.getLogger(__name__)

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
        return pd.DataFrame(columns=["indicador", "periodo", "valor", "nombre_api", "fecha_carga"])
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

def transform_all(raw_data: dict) -> pd.DataFrame:
    frames = []
    for nombre, raw in raw_data.items():
        frames.append(transform_serie(nombre, raw))
    if not frames:
        return pd.DataFrame(columns=["indicador", "periodo", "valor", "nombre_api", "fecha_carga"])
    return pd.concat(frames, ignore_index=True)