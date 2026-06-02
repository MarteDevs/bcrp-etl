USE bcrp_etl;
GO

-- ============================================================================
-- Vistas analíticas para Power BI
-- Consumo directo desde Power Query (SQL Server / Import)
-- Periodo almacenado como MMM.YYYY (ej: Ene.2020, Dic.2025)
-- ============================================================================

-- Helper: extraer año desde periodo MMM.YYYY
-- Helper: extraer número de mes desde abreviatura español
-- (Ambas se repiten inline ya que SQL Server no permite funciones en views)

-- ============================================================================
-- 1. vw_calendario — Dimensión temporal
-- ============================================================================
IF EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_calendario')
    DROP VIEW vw_calendario;
GO

CREATE VIEW vw_calendario AS
WITH cte AS (
    SELECT DISTINCT periodo
    FROM bcrp_indicadores
)
SELECT
    periodo,
    DATEFROMPARTS(
        CAST(RIGHT(periodo, 4) AS INT),
        CASE LEFT(periodo, 3)
            WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
            WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
            WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
            WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
        END,
        1
    )                                        AS fecha,
    CAST(RIGHT(periodo, 4) AS INT)           AS anio,
    CASE LEFT(periodo, 3)
        WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
        WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
        WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
        WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
    END                                      AS mes_numero,
    DATENAME(MONTH, DATEFROMPARTS(
        2000,
        CASE LEFT(periodo, 3)
            WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
            WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
            WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
            WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
        END,
        1
    ))                                       AS mes_nombre,
    CAST(
        RIGHT(periodo, 4)
        + RIGHT('0' + CAST(CASE LEFT(periodo, 3)
            WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
            WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
            WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
            WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
        END AS VARCHAR), 2)
        AS INT
    )                                        AS anio_mes
FROM cte;
GO

-- ============================================================================
-- 2. vw_indicadores_long — Tabla de hechos con fecha tipada
-- ============================================================================
IF EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_indicadores_long')
    DROP VIEW vw_indicadores_long;
GO

CREATE VIEW vw_indicadores_long AS
SELECT
    i.id,
    i.indicador,
    i.periodo,
    DATEFROMPARTS(
        CAST(RIGHT(i.periodo, 4) AS INT),
        CASE LEFT(i.periodo, 3)
            WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
            WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
            WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
            WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
        END,
        1
    )                                        AS fecha,
    CAST(RIGHT(i.periodo, 4) AS INT)         AS anio,
    i.valor,
    i.nombre_api,
    i.variacion_pct,
    i.media_movil_3m,
    i.fecha_carga
FROM bcrp_indicadores i;
GO

-- ============================================================================
-- 3. vw_indicadores_pivot — Series en columnas (ancho) para multi-línea
-- ============================================================================
IF EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_indicadores_pivot')
    DROP VIEW vw_indicadores_pivot;
GO

CREATE VIEW vw_indicadores_pivot AS
SELECT
    i.periodo,
    DATEFROMPARTS(
        CAST(RIGHT(i.periodo, 4) AS INT),
        CASE LEFT(i.periodo, 3)
            WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
            WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
            WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
            WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
        END,
        1
    )                                        AS fecha,
    CAST(RIGHT(i.periodo, 4) AS INT)         AS anio,
    MAX(CASE WHEN i.indicador = 'tipo_cambio_usd_pen'      THEN i.valor END) AS tc_usd_pen,
    MAX(CASE WHEN i.indicador = 'inflacion_mensual_ipc'    THEN i.valor END) AS inflacion_ipc,
    MAX(CASE WHEN i.indicador = 'reservas_internacionales' THEN i.valor END) AS reservas_intl,
    MAX(CASE WHEN i.indicador = 'tasa_referencia_bcrp'     THEN i.valor END) AS tasa_referencia
FROM bcrp_indicadores i
GROUP BY i.periodo;
GO

-- ============================================================================
-- 4. vw_tipo_cambio_anual — Estadísticas anuales del TC
-- ============================================================================
IF EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_tipo_cambio_anual')
    DROP VIEW vw_tipo_cambio_anual;
GO

CREATE VIEW vw_tipo_cambio_anual AS
SELECT
    CAST(RIGHT(i.periodo, 4) AS INT)         AS anio,
    COUNT(*)                                 AS meses_con_datos,
    AVG(i.valor)                             AS tc_promedio,
    MIN(i.valor)                             AS tc_minimo,
    MAX(i.valor)                             AS tc_maximo,
    STDEV(i.valor)                           AS tc_stddev,
    MAX(CASE
        WHEN i.periodo = agg.max_periodo THEN i.valor
    END)                                     AS tc_cierre_anual,
    MIN(CASE
        WHEN i.periodo = agg.min_periodo THEN i.valor
    END)                                     AS tc_apertura_anual
FROM bcrp_indicadores i
JOIN (
    SELECT
        CAST(RIGHT(periodo, 4) AS INT) AS anio,
        MAX(periodo) AS max_periodo,
        MIN(periodo) AS min_periodo
    FROM bcrp_indicadores
    WHERE indicador = 'tipo_cambio_usd_pen'
    GROUP BY CAST(RIGHT(periodo, 4) AS INT)
) agg ON CAST(RIGHT(i.periodo, 4) AS INT) = agg.anio
WHERE i.indicador = 'tipo_cambio_usd_pen'
GROUP BY CAST(RIGHT(i.periodo, 4) AS INT);
GO

-- ============================================================================
-- 5. vw_inflacion_vs_tasa — Comparación lado a lado para correlación
-- ============================================================================
IF EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_inflacion_vs_tasa')
    DROP VIEW vw_inflacion_vs_tasa;
GO

CREATE VIEW vw_inflacion_vs_tasa AS
WITH inflacion AS (
    SELECT periodo, valor
    FROM bcrp_indicadores
    WHERE indicador = 'inflacion_mensual_ipc'
),
tasa AS (
    SELECT periodo, valor
    FROM bcrp_indicadores
    WHERE indicador = 'tasa_referencia_bcrp'
)
SELECT
    COALESCE(i.periodo, t.periodo)           AS periodo,
    DATEFROMPARTS(
        CAST(RIGHT(COALESCE(i.periodo, t.periodo), 4) AS INT),
        CASE LEFT(COALESCE(i.periodo, t.periodo), 3)
            WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
            WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
            WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
            WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
        END,
        1
    )                                        AS fecha,
    i.valor                                  AS inflacion_ipc,
    t.valor                                  AS tasa_referencia,
    LAG(i.valor, 1) OVER (ORDER BY i.periodo) AS inflacion_lag_1m,
    LAG(i.valor, 3) OVER (ORDER BY i.periodo) AS inflacion_lag_3m,
    LAG(t.valor, 1) OVER (ORDER BY t.periodo) AS tasa_lag_1m,
    LAG(t.valor, 3) OVER (ORDER BY t.periodo) AS tasa_lag_3m
FROM inflacion i
FULL JOIN tasa t ON i.periodo = t.periodo;
GO

-- ============================================================================
-- 6. vw_reservas_tendencia — Variación y tendencia de RIN
-- ============================================================================
IF EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_reservas_tendencia')
    DROP VIEW vw_reservas_tendencia;
GO

CREATE VIEW vw_reservas_tendencia AS
WITH reservas AS (
    SELECT
        periodo,
        valor,
        DATEFROMPARTS(
            CAST(RIGHT(periodo, 4) AS INT),
            CASE LEFT(periodo, 3)
                WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
                WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
                WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
                WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
            END,
            1
        ) AS fecha
    FROM bcrp_indicadores
    WHERE indicador = 'reservas_internacionales'
)
SELECT
    periodo,
    fecha,
    valor                                    AS reservas_millon_usd,
    valor - LAG(valor, 1) OVER (ORDER BY fecha) AS variacion_absoluta,
    CASE
        WHEN LAG(valor, 1) OVER (ORDER BY fecha) IS NOT NULL
             AND LAG(valor, 1) OVER (ORDER BY fecha) <> 0
        THEN (valor - LAG(valor, 1) OVER (ORDER BY fecha))
             / LAG(valor, 1) OVER (ORDER BY fecha) * 100
    END                                      AS variacion_pct_mom,
    AVG(valor) OVER (ORDER BY fecha ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS media_movil_12m,
    CASE
        WHEN LAG(valor, 1) OVER (ORDER BY fecha) IS NOT NULL
             AND LAG(valor, 1) OVER (ORDER BY fecha) <> 0
             AND (valor - LAG(valor, 1) OVER (ORDER BY fecha))
                  / LAG(valor, 1) OVER (ORDER BY fecha) * 100 < -5
        THEN 1
        ELSE 0
    END                                      AS caida_significativa
FROM reservas;
GO

-- ============================================================================
-- BONUS 7. vw_outliers — Valores fuera de rango esperado
-- ============================================================================
IF EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_outliers')
    DROP VIEW vw_outliers;
GO

CREATE VIEW vw_outliers AS
SELECT
    id,
    indicador,
    periodo,
    DATEFROMPARTS(
        CAST(RIGHT(periodo, 4) AS INT),
        CASE LEFT(periodo, 3)
            WHEN 'Ene' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
            WHEN 'Abr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
            WHEN 'Jul' THEN 7 WHEN 'Ago' THEN 8 WHEN 'Sep' THEN 9
            WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dic' THEN 12
        END,
        1
    )                                        AS fecha,
    valor,
    nombre_api,
    CASE indicador
        WHEN 'tipo_cambio_usd_pen'      THEN 2.5
        WHEN 'inflacion_mensual_ipc'    THEN -2.0
        WHEN 'reservas_internacionales' THEN 20000
        WHEN 'tasa_referencia_bcrp'     THEN 0.0
    END                                      AS limite_inferior,
    CASE indicador
        WHEN 'tipo_cambio_usd_pen'      THEN 5.0
        WHEN 'inflacion_mensual_ipc'    THEN 10.0
        WHEN 'reservas_internacionales' THEN 100000
        WHEN 'tasa_referencia_bcrp'     THEN 20.0
    END                                      AS limite_superior
FROM bcrp_indicadores
WHERE
    (indicador = 'tipo_cambio_usd_pen'      AND (valor < 2.5   OR valor > 5.0))
    OR (indicador = 'inflacion_mensual_ipc' AND (valor < -2.0  OR valor > 10.0))
    OR (indicador = 'reservas_internacionales' AND (valor < 20000 OR valor > 100000))
    OR (indicador = 'tasa_referencia_bcrp'  AND (valor < 0.0   OR valor > 20.0));
GO

-- ============================================================================
-- BONUS 8. vw_ultima_carga — Metadatos de actualización
-- ============================================================================
IF EXISTS (SELECT 1 FROM sys.views WHERE name = 'vw_ultima_carga')
    DROP VIEW vw_ultima_carga;
GO

CREATE VIEW vw_ultima_carga AS
SELECT
    indicador,
    nombre_api,
    COUNT(*)                                 AS total_registros,
    MIN(periodo)                             AS periodo_min,
    MAX(periodo)                             AS periodo_max,
    MAX(fecha_carga)                         AS ultima_carga,
    DATEDIFF(DAY, MAX(fecha_carga), GETDATE()) AS dias_desde_ultima_carga,
    CASE
        WHEN DATEDIFF(DAY, MAX(fecha_carga), GETDATE()) <= 1 THEN 'Actualizado'
        WHEN DATEDIFF(DAY, MAX(fecha_carga), GETDATE()) <= 7 THEN 'Esta semana'
        WHEN DATEDIFF(DAY, MAX(fecha_carga), GETDATE()) <= 30 THEN 'Este mes'
        ELSE 'Desactualizado'
    END                                      AS estado_actualizacion
FROM bcrp_indicadores
GROUP BY indicador, nombre_api;
GO
