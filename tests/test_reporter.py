import os
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from reporter import ReportCollector, generate_report


@pytest.fixture
def collector_vacio():
    return ReportCollector()


@pytest.fixture
def collector_con_datos():
    c = ReportCollector()
    c.ultimos_periodos = {"tipo_cambio_usd_pen": "Sep.2025"}
    c.df = pd.DataFrame({
        "indicador": ["tipo_cambio_usd_pen", "tipo_cambio_usd_pen", "inflacion_mensual_ipc"],
        "periodo":   ["Oct.2025", "Nov.2025", "Oct.2025"],
        "valor":     [3.37, 3.38, 0.25],
        "nombre_api": ["TC Venta", "TC Venta", "IPC"],
        "fecha_carga": [pd.Timestamp.now()] * 3,
    })
    c.loaded_count = 3
    return c


@pytest.fixture
def collector_con_outliers():
    c = ReportCollector()
    c.df = pd.DataFrame({
        "indicador": ["tipo_cambio_usd_pen"],
        "periodo":   ["Ene.2020"],
        "valor":     [999.0],
        "nombre_api": ["TC Venta"],
        "fecha_carga": [pd.Timestamp.now()],
    })
    c.loaded_count = 1
    return c


@pytest.fixture
def collector_con_error():
    c = ReportCollector()
    c.status = "FAILED"
    c.errors = ["[Fase 3] ValidationError: Columna 'valor' no encontrada"]
    return c


class TestReportCollector:
    def test_init(self, collector_vacio):
        assert collector_vacio.status == "SUCCESS"
        assert collector_vacio.errors == []
        assert collector_vacio.df is None

    def test_add_error(self, collector_vacio):
        collector_vacio.add_error("Test", "algo fallo")
        assert len(collector_vacio.errors) == 1
        assert "[Test]" in collector_vacio.errors[0]

    def test_duracion_corta(self, collector_vacio):
        d = collector_vacio.duracion
        assert "s" in d

    def test_sin_datos_devuelve_vacio(self, collector_vacio):
        assert collector_vacio._computar_outliers() == {}
        assert collector_vacio._computar_estadisticas() == []

    def test_computar_estadisticas(self, collector_con_datos):
        stats = collector_con_datos._computar_estadisticas()
        assert len(stats) == 4
        tc = [s for s in stats if s["nombre"] == "tipo_cambio_usd_pen"][0]
        assert tc["registros"] == 2
        assert tc["outliers"] == 0
        assert tc["minimo"] == 3.37

    def test_outliers_detectados(self, collector_con_outliers):
        outliers = collector_con_outliers._computar_outliers()
        assert "tipo_cambio_usd_pen" in outliers
        assert len(outliers["tipo_cambio_usd_pen"]) == 1

    def test_resumen_validaciones_sin_datos(self, collector_vacio):
        v = collector_vacio._resumen_validaciones()
        assert v["estructura_msg"] == "Sin datos"

    def test_resumen_validaciones_con_datos(self, collector_con_datos):
        v = collector_con_datos._resumen_validaciones()
        assert v["estructura_ok"] is True
        assert v["nulos_ok"] is True
        assert v["duplicados_ok"] is True
        assert v["rangos_ok"] is True

    def test_resumen_validaciones_con_outliers(self, collector_con_outliers):
        v = collector_con_outliers._resumen_validaciones()
        assert v["rangos_ok"] is False


class TestGenerateReport:
    def test_genera_archivo_html_sin_datos(self, collector_vacio):
        ruta = generate_report(collector_vacio)
        assert Path(ruta).exists()
        assert ruta.endswith(".html")
        contenido = Path(ruta).read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in contenido
        assert "SUCCESS" in contenido
        os.remove(ruta)

    def test_genera_archivo_con_datos(self, collector_con_datos):
        ruta = generate_report(collector_con_datos)
        contenido = Path(ruta).read_text(encoding="utf-8")
        assert "tipo_cambio_usd_pen" in contenido
        assert "3.3700" in contenido
        os.remove(ruta)

    def test_genera_archivo_con_errores(self, collector_con_error):
        ruta = generate_report(collector_con_error)
        contenido = Path(ruta).read_text(encoding="utf-8")
        assert "FAILED" in contenido
        assert "Fase 3" in contenido
        os.remove(ruta)

    def test_genera_archivo_con_outliers(self, collector_con_outliers):
        ruta = generate_report(collector_con_outliers)
        contenido = Path(ruta).read_text(encoding="utf-8")
        assert "999.0000" in contenido
        os.remove(ruta)
