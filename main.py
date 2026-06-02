import logging
import sys
import os

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler("logs/etl.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

sys.path.insert(0, "src")
from extractor import extract_all
from transformer import transform_all
from validator import validate
from loader import load, obtener_ultimos_periodos

def run():
    logger.info("=== Iniciando pipeline ETL BCRP ===")

    logger.info("--- Fase 0: Consultar último periodo cargado ---")
    ultimos_periodos = obtener_ultimos_periodos()

    logger.info("--- Fase 1: Extracción incremental ---")
    raw = extract_all(ultimos_periodos)

    logger.info("--- Fase 2: Transformación ---")
    df = transform_all(raw)

    if df.empty:
        logger.info("  -> No hay datos nuevos para cargar. Pipeline finalizado.")
        return

    logger.info("--- Fase 3: Validación ---")
    df = validate(df)

    logger.info("--- Fase 4: Carga (UPSERT) ---")
    load(df)

    logger.info("=== Pipeline completado ===")

if __name__ == "__main__":
    run()
