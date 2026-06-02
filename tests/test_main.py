import pytest
from main import parse_args


class TestParseArgs:
    def test_defaults(self):
        args = parse_args([])
        assert args.modo == "incremental"
        assert args.inicio is None
        assert args.fin is None
        assert args.indicador is None

    def test_inicio_personalizado(self):
        args = parse_args(["--inicio", "2023-1"])
        assert args.inicio == "2023-1"

    def test_inicio_abreviado(self):
        args = parse_args(["-i", "2023-6"])
        assert args.inicio == "2023-6"

    def test_fin_personalizado(self):
        args = parse_args(["--fin", "2024-12"])
        assert args.fin == "2024-12"

    def test_fin_abreviado(self):
        args = parse_args(["-f", "2024-12"])
        assert args.fin == "2024-12"

    def test_inicio_y_fin(self):
        args = parse_args(["-i", "2021-1", "-f", "2024-12"])
        assert args.inicio == "2021-1"
        assert args.fin == "2024-12"

    def test_modo_full(self):
        args = parse_args(["--modo", "full"])
        assert args.modo == "full"

    def test_modo_incremental_explicito(self):
        args = parse_args(["--modo", "incremental"])
        assert args.modo == "incremental"

    def test_modo_abreviado(self):
        args = parse_args(["-m", "full"])
        assert args.modo == "full"

    def test_modo_invalido(self):
        with pytest.raises(SystemExit):
            parse_args(["--modo", "rapido"])

    def test_indicador_unico(self):
        args = parse_args(["--indicador", "tipo_cambio_usd_pen"])
        assert args.indicador == ["tipo_cambio_usd_pen"]

    def test_indicador_abreviado(self):
        args = parse_args(["-ind", "tc"])
        assert args.indicador == ["tc"]

    def test_indicador_multiple(self):
        args = parse_args(["--indicador", "tc", "inflacion"])
        assert args.indicador == ["tc", "inflacion"]

    def test_todo_combinado(self):
        args = parse_args(["-i", "2020-1", "-f", "2025-12", "-m", "full", "-ind", "tc"])
        assert args.inicio == "2020-1"
        assert args.fin == "2025-12"
        assert args.modo == "full"
        assert args.indicador == ["tc"]

    def test_help(self):
        with pytest.raises(SystemExit):
            parse_args(["--help"])
