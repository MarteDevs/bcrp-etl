import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text, inspect

from config import DB_SERVER, DB_NAME, DB_DRIVER

logger = logging.getLogger(__name__)

def get_engine():
    conn_str = (
        f"mssql+pyodbc://{DB_SERVER}/{DB_NAME}"
        f"?driver={DB_DRIVER.replace(' ', '+')}&trusted_connection=yes"
    )
    return create_engine(conn_str)

def ensure_table(engine):
    inspector = inspect(engine)
    if not inspector.has_table("bcrp_indicadores"):
        logger.info("  -> Tabla bcrp_indicadores no existe, creando...")
        sql_path = os.path.join(os.path.dirname(__file__), "..", "sql", "create_tables.sql")
        with open(sql_path, encoding="utf-8") as f:
            script = f.read()
        for statement in script.split("GO"):
            stripped = statement.strip()
            if stripped and not stripped.upper().startswith("CREATE DATABASE"):
                with engine.begin() as conn:
                    conn.execute(text(stripped))
        logger.info("  -> Tabla bcrp_indicadores creada")

def load(df: pd.DataFrame):
    engine = get_engine()
    ensure_table(engine)
    with engine.begin() as conn:
        for indicador in df["indicador"].unique():
            conn.execute(text(
                "DELETE FROM bcrp_indicadores WHERE indicador = :ind"
            ), {"ind": indicador})
        df.to_sql("bcrp_indicadores", conn, if_exists="append", index=False)
        logger.info(f"  -> {len(df)} registros cargados en SQL Server")