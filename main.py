import argparse
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
from config import SERIES, FECHA_FIN
from extractor import extract_all
from transformer import transform_all
from validator import validate
from loader import load, obtener_ultimos_periodos
from reporter import ReportCollector, generate_report
from periodos import FECHA_INICIO_DEFAULT, siguiente_periodo_api


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="BCRP ETL Pipeline — Carga indicadores económicos",
    )
    parser.add_argument(
        "--inicio", "-i",
        help="Fecha inicial YYYY-M (ej: 2023-1). Default: último periodo+1 ó 2020-1",
    )
    parser.add_argument(
        "--fin", "-f",
        help=f"Fecha final YYYY-M (ej: 2025-12). Default: {FECHA_FIN}",
    )
    parser.add_argument(
        "--modo", "-m",
        choices=["incremental", "full"],
        default="incremental",
        help="Modo: incremental (default) solo lo nuevo, full recarga todo",
    )
    parser.add_argument(
        "--indicador", "-ind",
        nargs="+",
        help="Indicador(es) a procesar (default: todos)",
    )
    return parser.parse_args(argv)


def run(args=None):
    if args is None:
        args = parse_args()

    collector = ReportCollector()

    try:
        logger.info("=== Iniciando pipeline ETL BCRP ===")
        logger.info(f"  Args: modo={args.modo}, inicio={args.inicio}, "
                     f"fin={args.fin}, indicador={args.indicador}")

        # -- Fase 0: determinar indicadores a procesar
        indicadores = (
            {k: v for k, v in SERIES.items() if k in args.indicador}
            if args.indicador
            else SERIES
        )
        logger.info(f"  Indicadores: {list(indicadores.keys())}")

        # -- Fase 0: determinar fecha de inicio
        if args.modo == "full":
            fecha_inicio = args.inicio or FECHA_INICIO_DEFAULT
            logger.info(f"  Modo full — fecha_inicio={fecha_inicio}")
            ultimos_periodos = {}
        else:
            logger.info("--- Fase 0: Consultar ultimo periodo cargado ---")
            ultimos_periodos = obtener_ultimos_periodos()
            if args.inicio:
                fecha_inicio = args.inicio
                logger.info(f"  Inicio forzado por CLI — fecha_inicio={fecha_inicio}")
            else:
                fecha_inicio = None

        fecha_fin = args.fin or FECHA_FIN

        # -- Fase 1: Extracción
        logger.info("--- Fase 1: Extraccion ---")
        raw = extract_all(
            indicadores=indicadores,
            ultimos_periodos=ultimos_periodos if not args.inicio else {},
            fecha_inicio_forced=fecha_inicio,
            fecha_fin=fecha_fin,
        )
        collector.extracted_counts = {
            nombre: len(data.get("periods", []))
            for nombre, data in raw.items()
        }

        # -- Fase 2: Transformación
        logger.info("--- Fase 2: Transformacion ---")
        df = transform_all(raw)

        if df.empty:
            logger.info("  -> No hay datos nuevos para cargar. Pipeline finalizado.")
            collector.df = df
            return

        # -- Fase 3: Validación
        logger.info("--- Fase 3: Validacion ---")
        df = validate(df)
        collector.df = df

        # -- Fase 4: Carga
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
