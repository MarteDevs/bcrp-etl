from dotenv import load_dotenv
import os

load_dotenv()

BCRP_BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
BCRP_FORMAT = "json"

SERIES = {
    "tipo_cambio_usd_pen":     "PN01215PM",
    "inflacion_mensual_ipc":   "PN01273PM",
    "reservas_internacionales":"PN01051MM",
    "tasa_referencia_bcrp":    "PN07819NM",
}

DB_SERVER   = os.getenv("DB_SERVER", "localhost")
DB_NAME     = os.getenv("DB_NAME", "bcrp_etl")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER   = "ODBC Driver 17 for SQL Server"

FECHA_FIN = "2025-12"