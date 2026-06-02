import pytest
from periodos import (
    periodo_a_numero,
    numero_a_periodo,
    siguiente_periodo_api,
    MESES_ES,
    FECHA_INICIO_DEFAULT,
)


class TestPeriodoANumero:
    def test_enero_2020(self):
        assert periodo_a_numero("Ene.2020") == (2020, 1)

    def test_diciembre_2025(self):
        assert periodo_a_numero("Dic.2025") == (2025, 12)

    def test_abril_2024(self):
        assert periodo_a_numero("Abr.2024") == (2024, 4)

    def test_formato_invalido(self):
        with pytest.raises(ValueError):
            periodo_a_numero("invalido")

    def test_mes_desconocido(self):
        with pytest.raises(ValueError):
            periodo_a_numero("Xxx.2024")


class TestNumeroAPeriodo:
    def test_enero_2020(self):
        assert numero_a_periodo(2020, 1) == "Ene.2020"

    def test_diciembre_2025(self):
        assert numero_a_periodo(2025, 12) == "Dic.2025"

    def test_mes_invalido(self):
        with pytest.raises(ValueError):
            numero_a_periodo(2020, 13)


class TestSiguientePeriodoAPI:
    def test_con_ultimo_periodo_normal(self):
        assert siguiente_periodo_api("Abr.2025") == "2025-5"

    def test_diciembre_devuelve_enero_siguiente(self):
        assert siguiente_periodo_api("Dic.2025") == "2026-1"

    def test_sin_ultimo_periodo_devuelve_default(self):
        assert siguiente_periodo_api(None) == FECHA_INICIO_DEFAULT

    def test_enero_devuelve_febrero(self):
        assert siguiente_periodo_api("Ene.2023") == "2023-2"


class TestMesesCompletos:
    def test_todos_los_meses_presentes(self):
        assert len(MESES_ES) == 12
        assert set(MESES_ES.keys()) == {
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
        }
