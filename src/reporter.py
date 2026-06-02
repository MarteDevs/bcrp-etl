import os
import logging
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from config import SERIES, DB_NAME
from periodos import periodo_a_numero

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

RANGOS_ESPERADOS = {
    "tipo_cambio_usd_pen":      (2.5, 5.0),
    "inflacion_mensual_ipc":    (-2.0, 10.0),
    "reservas_internacionales": (20000, 100000),
    "tasa_referencia_bcrp":     (0.0, 20.0),
}


class ReportCollector:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.status = "SUCCESS"
        self.errors = []
        self.ultimos_periodos = {}
        self.extracted_counts = {}
        self.df = None
        self.loaded_count = 0

    def add_error(self, fase: str, msg: str):
        self.errors.append(f"[{fase}] {msg}")

    @property
    def duracion(self) -> str:
        fin = self.end_time or datetime.now()
        delta = fin - self.start_time
        total_s = int(delta.total_seconds())
        horas = total_s // 3600
        minutos = (total_s % 3600) // 60
        segundos = total_s % 60
        if horas:
            return f"{horas}h {minutos}m {segundos}s"
        if minutos:
            return f"{minutos}m {segundos}s"
        return f"{segundos}s"

    def _computar_outliers(self) -> dict[str, list]:
        if self.df is None or self.df.empty:
            return {}
        outliers = {}
        for indicador, (minimo, maximo) in RANGOS_ESPERADOS.items():
            subset = self.df[self.df["indicador"] == indicador]
            if subset.empty:
                continue
            fuera = subset[(subset["valor"] < minimo) | (subset["valor"] > maximo)]
            if not fuera.empty:
                outliers[indicador] = list(zip(fuera["periodo"], fuera["valor"]))
        return outliers

    def _computar_estadisticas(self) -> list[dict]:
        if self.df is None or self.df.empty:
            return []
        stats = []
        for nombre in SERIES:
            subset = self.df[self.df["indicador"] == nombre]
            outliers = self._computar_outliers()
            cnt_out = len(outliers.get(nombre, []))
            if subset.empty:
                stats.append({
                    "nombre": nombre,
                    "registros": 0,
                    "outliers": 0,
                    "minimo": None,
                    "maximo": None,
                    "promedio": None,
                })
            else:
                stats.append({
                    "nombre": nombre,
                    "registros": len(subset),
                    "outliers": cnt_out,
                    "minimo": subset["valor"].min(),
                    "maximo": subset["valor"].max(),
                    "promedio": subset["valor"].mean(),
                })
        return stats

    def _resumen_validaciones(self) -> dict:
        v = {
            "estructura_ok": True,
            "estructura_msg": "",
            "nulos_ok": True,
            "nulos_msg": "",
            "duplicados_ok": True,
            "duplicados_msg": "",
            "rangos_ok": True,
            "rangos_msg": "",
        }
        if self.df is None:
            v["estructura_msg"] = "Sin datos"
            return v
        v["estructura_msg"] = f"{len(self.df)} registros, {self.df['indicador'].nunique()} indicadores"
        nulos = self.df[["valor"]].isnull().sum().iloc[0]
        if nulos:
            v["nulos_ok"] = False
            v["nulos_msg"] = f"{nulos} valores nulos en 'valor'"
        else:
            v["nulos_msg"] = "Sin valores nulos en columnas críticas"
        dupes = self.df.duplicated(subset=["indicador", "periodo"]).sum()
        if dupes:
            v["duplicados_ok"] = False
            v["duplicados_msg"] = f"{dupes} registros duplicados eliminados"
        else:
            v["duplicados_msg"] = "Sin registros duplicados"
        outliers = self._computar_outliers()
        total_out = sum(len(v) for v in outliers.values())
        if total_out:
            v["rangos_ok"] = False
            v["rangos_msg"] = f"{total_out} valores fuera de rango"
        else:
            v["rangos_msg"] = "Todos los valores dentro del rango esperado"
        return v


def generate_report(collector: ReportCollector) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("report.html")
    timestamp = collector.start_time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"run_{timestamp}.html"
    filepath = REPORTS_DIR / filename
    outliers_detalle = collector._computar_outliers()
    total_out = sum(len(v) for v in outliers_detalle.values())
    html = template.render(
        titulo=f"Reporte {timestamp}",
        fecha_ejecucion=collector.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        duracion=collector.duracion,
        total_registros=len(collector.df) if collector.df is not None else 0,
        total_indicadores=collector.df["indicador"].nunique() if collector.df is not None else 0,
        total_outliers=total_out,
        estado=collector.status,
        ultimos_periodos=collector.ultimos_periodos,
        indicadores=collector._computar_estadisticas(),
        validaciones=collector._resumen_validaciones(),
        outliers_detalle=outliers_detalle,
        errores=collector.errors,
    )
    filepath.write_text(html, encoding="utf-8")
    logger.info(f"  -> Reporte generado: {filepath}")
    return str(filepath)
