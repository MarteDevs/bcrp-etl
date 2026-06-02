import logging
import sys
import os

# Setup de logging — crea la carpeta si no existe
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

# Importar módulos del proyecto
sys.path.insert(0, "src")
from extractor import extract_all
from transformer import transform_all
from validator import validate
from loader import load

def run():
    logger.info("=== Iniciando pipeline ETL BCRP ===")
    
    logger.info("--- Fase 1: Extracción ---")
    raw = extract_all()
    
    logger.info("--- Fase 2: Transformación ---")
    df = transform_all(raw)
    
    logger.info("--- Fase 3: Validación ---")
    df = validate(df)
    
    logger.info("--- Fase 4: Carga ---")
    load(df)
    
    logger.info("=== Pipeline completado ===")

if __name__ == "__main__":
    run()