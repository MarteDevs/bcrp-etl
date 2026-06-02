import pandas as pd
import pytest
from validator import (
    validate,
    _validar_estructura,
    _validar_nulos,
    _validar_rangos,
    _validar_duplicados,
    ValidationError,
)


class TestValidarEstructura:
    def test_df_valido_pasa(self, df_valido):
        _validar_estructura(df_valido)

    def test_df_vacio_lanza_error(self):
        df = pd.DataFrame()
        with pytest.raises(ValidationError, match="vacío"):
            _validar_estructura(df)

    def test_columna_faltante_lanza_error(self, df_valido):
        df = df_valido.drop(columns=["valor"])
        with pytest.raises(ValidationError, match="faltantes"):
            _validar_estructura(df)


class TestValidarNulos:
    def test_sin_nulos_pasa(self, df_valido):
        _validar_nulos(df_valido)

    def test_menos_de_10_porciento_no_lanza(self, df_con_nulos):
        _validar_nulos(df_con_nulos)

    def test_mas_de_10_porciento_lanza_error(self):
        df = pd.DataFrame({
            "indicador": ["a", "b", "c"],
            "periodo":   ["Ene.2020", "Feb.2020", "Mar.2020"],
            "valor":     [1.0, None, None],
        })
        with pytest.raises(ValidationError, match="10%"):
            _validar_nulos(df)


class TestValidarRangos:
    def test_valores_en_rango(self, df_valido):
        _validar_rangos(df_valido)

    def test_outliers_no_lanzan_error(self, df_fuera_rango):
        _validar_rangos(df_fuera_rango)

    def test_indicador_desconocido(self, df_valido):
        df = df_valido.copy()
        df["indicador"] = "desconocido"
        _validar_rangos(df)


class TestValidarDuplicados:
    def test_sin_duplicados_retorna_mismo(self, df_valido):
        result = _validar_duplicados(df_valido)
        assert len(result) == len(df_valido)

    def test_con_duplicados_elimina(self, df_con_duplicados):
        result = _validar_duplicados(df_con_duplicados)
        assert len(result) == 2

    def test_duplicados_exactos(self, df_con_duplicados):
        result = _validar_duplicados(df_con_duplicados)
        assert result["periodo"].tolist() == ["Ene.2020", "Feb.2020"]


class TestValidate:
    def test_df_valido_retorna_dataframe(self, df_valido):
        result = validate(df_valido)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_df_vacio_lanza_error(self):
        with pytest.raises(ValidationError):
            validate(pd.DataFrame())

    def test_con_duplicados_limpia_y_retorna(self, df_con_duplicados):
        result = validate(df_con_duplicados)
        assert len(result) == 2
