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

def obtener_ultimos_periodos() -> dict[str, str | None]:
    engine = get_engine()
    inspector = inspect(engine)
    if not inspector.has_table("bcrp_indicadores"):
        logger.info("  -> Tabla bcrp_indicadores no existe — se cargará todo el historial")
        return {}
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT indicador, MAX(periodo) FROM bcrp_indicadores GROUP BY indicador")
        )
        ultimos = {row[0]: row[1] for row in result}
        if ultimos:
            logger.info(f"  -> Últimos periodos cargados: {ultimos}")
        else:
            logger.info("  -> BD vacía — se cargará todo el historial")
    return ultimos

def load(df: pd.DataFrame):
    engine = get_engine()
    ensure_table(engine)
    merge_sql = text("""
        MERGE bcrp_indicadores AS target
        USING (SELECT :indicador AS indicador, :periodo AS periodo,
                      :valor AS valor, :nombre_api AS nombre_api) AS source
        ON (target.indicador = source.indicador AND target.periodo = source.periodo)
        WHEN MATCHED THEN
            UPDATE SET valor = source.valor, fecha_carga = GETDATE()
        WHEN NOT MATCHED THEN
            INSERT (indicador, periodo, valor, nombre_api, fecha_carga)
            VALUES (source.indicador, source.periodo, source.valor, source.nombre_api, GETDATE());
    """)
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(merge_sql, {
                "indicador": row["indicador"],
                "periodo":   row["periodo"],
                "valor":     row["valor"],
                "nombre_api": row["nombre_api"],
            })
        logger.info(f"  -> {len(df)} registros upsertados en SQL Server")
