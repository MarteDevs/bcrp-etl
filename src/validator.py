import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Rangos históricos razonables por indicador
RANGOS_ESPERADOS = {
    "tipo_cambio_usd_pen":      (2.5, 5.0),
    "inflacion_mensual_ipc":    (-2.0, 10.0),
    "reservas_internacionales": (20000, 100000),
    "tasa_referencia_bcrp":     (0.0, 20.0),
}

COLUMNAS_REQUERIDAS = {"indicador", "periodo", "valor", "nombre_api", "fecha_carga"}


class ValidationError(Exception):
    """Error crítico que detiene el pipeline."""
    pass


def _validar_estructura(df: pd.DataFrame):
    """Verifica que el DataFrame tenga las columnas esperadas y no esté vacío."""
    if df.empty:
        raise ValidationError("El DataFrame está vacío — no hay datos para cargar.")

    faltantes = COLUMNAS_REQUERIDAS - set(df.columns)
    if faltantes:
        raise ValidationError(f"Columnas faltantes: {faltantes}")

    logger.info(f"  -> Estructura OK — {len(df)} registros, {df['indicador'].nunique()} indicadores")


def _validar_nulos(df: pd.DataFrame):
    """Detecta valores nulos en columnas críticas."""
    nulos = df[["indicador", "periodo", "valor"]].isnull().sum()
    tiene_nulos = nulos[nulos > 0]

    if not tiene_nulos.empty:
        for col, cantidad in tiene_nulos.items():
            pct = cantidad / len(df) * 100
            if pct > 10:
                raise ValidationError(
                    f"Columna '{col}' tiene {cantidad} nulos ({pct:.1f}%) — supera el 10% permitido."
                )
            else:
                logger.warning(f"  -> Nulos en '{col}': {cantidad} registros ({pct:.1f}%)")
    else:
        logger.info("  -> Sin valores nulos en columnas críticas")


def _validar_rangos(df: pd.DataFrame):
    """Detecta valores fuera del rango histórico esperado."""
    alertas = 0
    for indicador, (minimo, maximo) in RANGOS_ESPERADOS.items():
        subset = df[df["indicador"] == indicador]
        if subset.empty:
            logger.warning(f"  -> Indicador '{indicador}' no encontrado en los datos")
            continue

        fuera = subset[(subset["valor"] < minimo) | (subset["valor"] > maximo)]
        if not fuera.empty:
            logger.warning(
                f"  -> '{indicador}': {len(fuera)} valores fuera del rango [{minimo}, {maximo}]"
            )
            for _, row in fuera.iterrows():
                logger.warning(f"      -> Periodo: {row['periodo']}, Valor: {row['valor']}")
            alertas += len(fuera)
        else:
            logger.info(f"  -> '{indicador}': todos los valores dentro del rango esperado")

    if alertas > 0:
        logger.warning(f"Total outliers detectados: {alertas} (se cargarán igual)")


def _validar_duplicados(df: pd.DataFrame):
    """Detecta registros duplicados por indicador + periodo."""
    dupes = df.duplicated(subset=["indicador", "periodo"])
    cantidad = dupes.sum()
    if cantidad > 0:
        logger.warning(f"  -> {cantidad} registros duplicados (indicador+periodo) — se eliminarán")
        return df.drop_duplicates(subset=["indicador", "periodo"])
    else:
        logger.info("  -> Sin duplicados")
        return df


def _resumen_estadistico(df: pd.DataFrame):
    """Imprime estadísticas del lote en el log."""
    logger.info("  -> Resumen por indicador:")
    for indicador in df["indicador"].unique():
        subset = df[df["indicador"] == indicador]
        logger.info(
            f"      {indicador}: "
            f"{len(subset)} registros | "
            f"min={subset['valor'].min():.4f} | "
            f"max={subset['valor'].max():.4f} | "
            f"promedio={subset['valor'].mean():.4f}"
        )


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ejecuta todas las validaciones sobre el DataFrame transformado.
    Retorna el DataFrame limpio o lanza ValidationError si algo es crítico.
    """
    logger.info("--- Validaciones ---")

    _validar_estructura(df)       # CRÍTICO — puede lanzar ValidationError
    _validar_nulos(df)            # CRÍTICO si > 10%, ADVERTENCIA si <= 10%
    
    df = _validar_duplicados(df)  # ADVERTENCIA — limpia y continúa
    _validar_rangos(df)           # ADVERTENCIA — registra y continúa
    _resumen_estadistico(df)      # INFO siempre

    logger.info("  -> Validación completada")
    return df