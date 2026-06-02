import logging
import sys
import os
from datetime import datetime

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
from reporter import ReportCollector, generate_report

def run():
    collector = ReportCollector()

    try:
        logger.info("=== Iniciando pipeline ETL BCRP ===")

        logger.info("--- Fase 0: Consultar ultimo periodo cargado ---")
        collector.ultimos_periodos = obtener_ultimos_periodos()

        logger.info("--- Fase 1: Extraccion incremental ---")
        raw = extract_all(collector.ultimos_periodos)
        collector.extracted_counts = {
            nombre: len(data.get("periods", []))
            for nombre, data in raw.items()
        }

        logger.info("--- Fase 2: Transformacion ---")
        df = transform_all(raw)

        if df.empty:
            logger.info("  -> No hay datos nuevos para cargar. Pipeline finalizado.")
            collector.df = df
            return

        logger.info("--- Fase 3: Validacion ---")
        df = validate(df)
        collector.df = df

        logger.info("--- Fase 4: Carga (UPSERT) ---")
        load(df)
        collector.loaded_count = len(df)

    except Exception as e:
        collector.status = "FAILED"
        collector.add_error("Pipeline", str(e))
        logger.exception("Pipeline fallo")

    finally:
        collector.end_time = datetime.now()
        if collector.df is None:
            collector.df = df if "df" in dir() and df is not None else None
        ruta = generate_report(collector)
        logger.info(f"Reporte: {ruta}")

if __name__ == "__main__":
    run()
