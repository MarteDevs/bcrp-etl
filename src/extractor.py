import requests
import logging
from config import BCRP_BASE_URL, BCRP_FORMAT
from periodos import siguiente_periodo_api

logger = logging.getLogger(__name__)

def fetch_serie(nombre: str, codigo: str, fecha_inicio: str, fecha_fin: str) -> dict:
    url = f"{BCRP_BASE_URL}/{codigo}/{BCRP_FORMAT}/{fecha_inicio}/{fecha_fin}"
    logger.info(f"Extrayendo: {nombre} ({codigo}) [{fecha_inicio} -> {fecha_fin}]")
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    logger.info(f"  -> {len(data['periods'])} periodos recibidos")
    return data

def extract_all(
    indicadores: dict,
    ultimos_periodos: dict[str, str | None] = None,
    fecha_inicio_forced: str | None = None,
    fecha_fin: str = "2025-12",
) -> dict:
    if ultimos_periodos is None:
        ultimos_periodos = {}
    resultados = {}
    for nombre, codigo in indicadores.items():
        try:
            if fecha_inicio_forced:
                inicio = fecha_inicio_forced
            else:
                inicio = siguiente_periodo_api(ultimos_periodos.get(nombre))
            resultados[nombre] = fetch_serie(nombre, codigo, inicio, fecha_fin)
        except Exception as e:
            logger.error(f"Error al extraer {nombre}: {e}")
    return resultados
