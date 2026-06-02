import logging

logger = logging.getLogger(__name__)

MESES_ES = {
    "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Ago": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12,
}

MES_NUM_A_TEXTO = {v: k for k, v in MESES_ES.items()}

FECHA_INICIO_DEFAULT = "2020-1"


def periodo_a_numero(periodo: str) -> tuple[int, int]:
    partes = periodo.split(".")
    if len(partes) != 2:
        raise ValueError(f"Formato de periodo inválido: {periodo}")
    mes_str, anio_str = partes
    anio = int(anio_str)
    mes = MESES_ES.get(mes_str)
    if mes is None:
        raise ValueError(f"Mes desconocido: {mes_str}")
    return anio, mes


def numero_a_periodo(anio: int, mes: int) -> str:
    mes_txt = MES_NUM_A_TEXTO.get(mes)
    if mes_txt is None:
        raise ValueError(f"Número de mes inválido: {mes}")
    return f"{mes_txt}.{anio}"


def siguiente_periodo_api(ultimo_periodo: str | None) -> str:
    if ultimo_periodo is None:
        return FECHA_INICIO_DEFAULT
    anio, mes = periodo_a_numero(ultimo_periodo)
    mes += 1
    if mes > 12:
        mes = 1
        anio += 1
    return f"{anio}-{mes}"
