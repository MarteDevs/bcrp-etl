import requests
import logging
from config import BCRP_BASE_URL, BCRP_FORMAT, SERIES, FECHA_INICIO, FECHA_FIN

logger = logging.getLogger(__name__)

def fetch_serie(nombre: str, codigo: str) -> dict:
    url = f"{BCRP_BASE_URL}/{codigo}/{BCRP_FORMAT}/{FECHA_INICIO}/{FECHA_FIN}"
    logger.info(f"Extrayendo: {nombre} ({codigo})")
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    logger.info(f"  -> {len(data['periods'])} periodos recibidos")
    return data

def extract_all() -> dict:
    resultados = {}
    for nombre, codigo in SERIES.items():
        try:
            resultados[nombre] = fetch_serie(nombre, codigo)
        except Exception as e:
            logger.error(f"Error al extraer {nombre}: {e}")
    return resultados