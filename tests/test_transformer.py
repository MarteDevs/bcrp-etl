import pandas as pd
import pytest
from transformer import parse_valor, transform_serie, transform_all


class TestParseValor:
    def test_numero_entero(self):
        assert parse_valor("123.45") == 123.45

    def test_numero_con_coma_decimal(self):
        assert parse_valor("123,45") == 123.45

    def test_cadena_vacia(self):
        assert parse_valor("") is None

    def test_no_disponible(self):
        assert parse_valor("n.d.") is None

    def test_espacios(self):
        assert parse_valor("  ") is None

    def test_texto_invalido(self):
        assert parse_valor("abc") is None

    def test_numero_negativo(self):
        assert parse_valor("-1.5") == -1.5


class TestTransformSerie:
    def test_transformacion_valida(self, raw_tc):
        df = transform_serie("tipo_cambio_usd_pen", raw_tc)
        assert len(df) == 3
        assert list(df.columns) == ["indicador", "periodo", "valor", "nombre_api", "fecha_carga"]
        assert df["indicador"].iloc[0] == "tipo_cambio_usd_pen"
        assert df["valor"].iloc[0] == 3.3784
        assert df["periodo"].iloc[1] == "Feb.2020"

    def test_sin_periodos_retorna_vacio(self, raw_vacio):
        df = transform_serie("vacia", raw_vacio)
        assert df.empty
        assert list(df.columns) == ["indicador", "periodo", "valor", "nombre_api", "fecha_carga"]

    def test_valores_nd_son_filtrados(self, raw_tc_con_nd):
        df = transform_serie("tipo_cambio_usd_pen", raw_tc_con_nd)
        assert len(df) == 2
        assert "Feb.2020" not in df["periodo"].values

    def test_tipo_dato_valor(self, raw_tc):
        df = transform_serie("tipo_cambio_usd_pen", raw_tc)
        assert df["valor"].dtype == float


class TestTransformAll:
    def test_multiples_series(self, raw_multiple):
        df = transform_all(raw_multiple)
        assert len(df) == 5
        assert df["indicador"].nunique() == 2

    def test_dict_vacio(self):
        df = transform_all({})
        assert df.empty

    def test_columna_fecha_carga_presente(self, raw_multiple):
        df = transform_all(raw_multiple)
        assert "fecha_carga" in df.columns
        assert df["fecha_carga"].notna().all()
