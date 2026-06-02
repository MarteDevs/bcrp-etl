import requests
import logging
from config import BCRP_BASE_URL, BCRP_FORMAT, SERIES, FECHA_FIN
from periodos import siguiente_periodo_api

logger = logging.getLogger(__name__)

def fetch_serie(nombre: str, codigo: str, fecha_inicio: str = None) -> dict:
    inicio = fecha_inicio or "2020-1"
    url = f"{BCRP_BASE_URL}/{codigo}/{BCRP_FORMAT}/{inicio}/{FECHA_FIN}"
    logger.info(f"Extrayendo: {nombre} ({codigo}) desde {inicio}")
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    logger.info(f"  -> {len(data['periods'])} periodos recibidos")
    return data

def extract_all(ultimos_periodos: dict[str, str | None] = None) -> dict:
    if ultimos_periodos is None:
        ultimos_periodos = {}
    resultados = {}
    for nombre, codigo in SERIES.items():
        try:
            fecha_inicio = siguiente_periodo_api(ultimos_periodos.get(nombre))
            resultados[nombre] = fetch_serie(nombre, codigo, fecha_inicio)
        except Exception as e:
            logger.error(f"Error al extraer {nombre}: {e}")
    return resultados
