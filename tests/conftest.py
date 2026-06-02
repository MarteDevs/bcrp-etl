import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd
import pytest


@pytest.fixture
def raw_tc() -> dict:
    return {
        "config": {
            "title": "Tipo de cambio",
            "series": [{"name": "TC Interbancario Venta", "dec": "4"}],
        },
        "periods": [
            {"name": "Ene.2020", "values": ["3.3784"]},
            {"name": "Feb.2020", "values": ["3.4500"]},
            {"name": "Mar.2020", "values": ["3.5200"]},
        ],
    }


@pytest.fixture
def raw_tc_con_nd() -> dict:
    return {
        "config": {
            "title": "Tipo de cambio",
            "series": [{"name": "TC Interbancario Venta", "dec": "4"}],
        },
        "periods": [
            {"name": "Ene.2020", "values": ["3.3784"]},
            {"name": "Feb.2020", "values": ["n.d."]},
            {"name": "Mar.2020", "values": ["3.5200"]},
        ],
    }


@pytest.fixture
def raw_vacio() -> dict:
    return {
        "config": {
            "title": "Serie vacía",
            "series": [{"name": "Vacia", "dec": "2"}],
        },
        "periods": [],
    }


@pytest.fixture
def raw_multiple(raw_tc) -> dict:
    raw_inflacion = {
        "config": {
            "title": "Inflación",
            "series": [{"name": "IPC", "dec": "2"}],
        },
        "periods": [
            {"name": "Ene.2020", "values": ["0.25"]},
            {"name": "Feb.2020", "values": ["0.30"]},
        ],
    }
    return {
        "tipo_cambio_usd_pen": raw_tc,
        "inflacion_mensual_ipc": raw_inflacion,
    }


@pytest.fixture
def df_valido() -> pd.DataFrame:
    return pd.DataFrame({
        "indicador": ["tipo_cambio_usd_pen", "tipo_cambio_usd_pen", "inflacion_mensual_ipc"],
        "periodo":   ["Ene.2020", "Feb.2020", "Ene.2020"],
        "valor":     [3.3784, 3.4500, 0.25],
        "nombre_api": ["TC Venta", "TC Venta", "IPC"],
        "fecha_carga": [pd.Timestamp.now()] * 3,
    })


@pytest.fixture
def df_con_nulos() -> pd.DataFrame:
    return pd.DataFrame({
        "indicador": ["tipo_cambio_usd_pen"] * 15 + ["inflacion_mensual_ipc"] * 5,
        "periodo":   [f"Mes.{i}" for i in range(20)],
        "valor":     [3.3784] * 15 + [None] + [0.25] * 4,
        "nombre_api": ["TC Venta"] * 15 + ["IPC"] * 5,
        "fecha_carga": [pd.Timestamp.now()] * 20,
    })


@pytest.fixture
def df_con_duplicados() -> pd.DataFrame:
    return pd.DataFrame({
        "indicador": ["tipo_cambio_usd_pen", "tipo_cambio_usd_pen", "tipo_cambio_usd_pen"],
        "periodo":   ["Ene.2020", "Ene.2020", "Feb.2020"],
        "valor":     [3.3784, 3.3784, 3.4500],
        "nombre_api": ["TC Venta", "TC Venta", "TC Venta"],
        "fecha_carga": [pd.Timestamp.now()] * 3,
    })


@pytest.fixture
def df_fuera_rango() -> pd.DataFrame:
    return pd.DataFrame({
        "indicador": ["tipo_cambio_usd_pen"],
        "periodo":   ["Ene.2020"],
        "valor":     [999.0],
        "nombre_api": ["TC Venta"],
        "fecha_carga": [pd.Timestamp.now()],
    })
