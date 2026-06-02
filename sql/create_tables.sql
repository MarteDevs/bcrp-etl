CREATE DATABASE bcrp_etl;
GO

USE bcrp_etl;
GO

CREATE TABLE bcrp_indicadores (
    id           INT IDENTITY(1,1) PRIMARY KEY,
    indicador    NVARCHAR(100)  NOT NULL,
    periodo      NVARCHAR(20)   NOT NULL,
    valor        FLOAT,
    nombre_api   NVARCHAR(300),
    fecha_carga  DATETIME       DEFAULT GETDATE(),
    CONSTRAINT uq_indicador_periodo UNIQUE (indicador, periodo)
);
GO