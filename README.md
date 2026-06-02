# 🇵🇪 Pipeline ETL — Indicadores Económicos BCRP

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-2019-red?logo=microsoftsqlserver&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.1-150458?logo=pandas&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Estado](https://img.shields.io/badge/Estado-Activo-brightgreen)

Pipeline ETL de producción que extrae indicadores macroeconómicos del Banco Central de Reserva del Perú (BCRP), los transforma y valida automáticamente, y los carga en SQL Server para análisis posterior.

---

## 📊 Indicadores procesados

| Indicador | Fuente | Frecuencia |
|---|---|---|
| Tipo de cambio USD/PEN | BCRP API | Diaria |
| Inflación mensual (IPC) | BCRP API | Mensual |
| Reservas internacionales | BCRP API | Semanal |
| Tasa de interés de referencia | BCRP API | Mensual |

---

## 🏗️ Arquitectura

```
API BCRP (pública)
      │
      ▼
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐     ┌─────────────┐
│  Extractor  │────▶│  Transformer     │────▶│  Validator     │────▶│   Loader    │
│             │     │                  │     │                │     │             │
│ requests    │     │ Pandas           │     │ Rangos         │     │ SQLAlchemy  │
│ JSON → dict │     │ Limpieza/tipos   │     │ Nulos          │     │ Upsert      │
└─────────────┘     └──────────────────┘     │ Duplicados     │     └─────────────┘
                                             └────────────────┘
                                                     │
                                              logs/etl.log
```

---

## 📁 Estructura del proyecto

```
bcrp-etl/
├── src/
│   ├── config.py          # Configuración centralizada y variables de entorno
│   ├── extractor.py       # Consumo de la API REST del BCRP
│   ├── transformer.py     # Limpieza, normalización, tipado y enriquecimiento
│   ├── validator.py       # Validación de estructura, rangos y duplicados
│   ├── loader.py          # Carga incremental (upsert) a SQL Server
│   └── reporter.py        # Generación de reporte HTML
├── sql/
│   ├── create_tables.sql  # DDL del esquema de base de datos
│   └── views.sql          # Vistas analíticas para Power BI
├── templates/             # Plantilla Jinja2 para reportes
├── tests/                 # Suite de pruebas con pytest
├── logs/                  # Generado automáticamente en ejecución
├── reports/               # Reportes HTML de ejecución
├── Dockerfile             # Contenedor para ejecución portable
├── docker-compose.yml     # Orquestación del contenedor
├── .dockerignore
├── .env.example           # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── main.py                # Orquestador del pipeline (CLI)
```

---

## ⚙️ Instalación y uso

### Requisitos

- Python 3.10+
- SQL Server (local o remoto) con ODBC Driver 17
- Git

### 1. Clonar el repositorio

```bash
git clone git@github.com:MarteDevs/bcrp-etl.git
cd bcrp-etl
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=bcrp_etl
```

### 4. Crear la base de datos

Ejecuta el script en SQL Server Management Studio:

```bash
# Abre sql/create_tables.sql en SSMS y ejecútalo
```

### 5. Ejecutar el pipeline

```bash
# Incremental (solo datos nuevos, default)
python main.py

# Full reload con rango personalizado
python main.py --modo full --inicio 2020-1 --fin 2025-12

# Un solo indicador
python main.py -m full -i 2023-1 -f 2024-12 --indicador tipo_cambio_usd_pen

# Múltiples indicadores
python main.py -ind tc inflacion
```

#### Flags CLI

| Flag | Descripción | Default |
|---|---|---|
| `--inicio` / `-i` | Fecha inicial `YYYY-M` | Último periodo+1 ó `2020-1` |
| `--fin` / `-f` | Fecha final `YYYY-M` | `2025-12` |
| `--modo` / `-m` | `incremental` (solo nuevo) o `full` (recarga todo) | `incremental` |
| `--indicador` / `-ind` | Indicador(es) a procesar (separados por espacio) | Todos |

### 6. Ejecutar con Docker (sin instalar Python ni ODBC)

```bash
# 1. Editar .env: apuntar al SQL Server anfitrión
DB_SERVER=host.docker.internal
DB_USER=sa
DB_PASSWORD=tu_password

# 2. Construir y ejecutar
docker-compose up --build
```

El contenedor incluye Python 3.10 + msodbcsql17 + todas las dependencias. Los logs y reportes se escriben en tu máquina local (`./logs/`, `./reports/`).

---

## 🔍 Capa de validación

El pipeline incluye validación automática en 3 niveles antes de cada carga:

| Nivel | Qué verifica | Acción |
|---|---|---|
| **CRÍTICO** | DataFrame vacío, columnas faltantes, nulos > 10% | Detiene el pipeline |
| **ADVERTENCIA** | Outliers fuera de rango histórico, nulos < 10% | Registra en log y continúa |
| **INFO** | Estadísticas del lote (min, max, promedio por indicador) | Solo registra |

---

## 🗄️ Modelo de datos

```sql
CREATE TABLE bcrp_indicadores (
    id             INT IDENTITY(1,1) PRIMARY KEY,
    indicador      NVARCHAR(100)  NOT NULL,   -- Nombre del indicador
    periodo        NVARCHAR(20)   NOT NULL,   -- Ej: "Ene.2024"
    valor          FLOAT,                     -- Valor numérico del indicador
    nombre_api     NVARCHAR(300),             -- Nombre oficial según la API
    variacion_pct  FLOAT,                     -- Variación % respecto al mes anterior
    media_movil_3m FLOAT,                     -- Media móvil de 3 meses
    fecha_carga    DATETIME DEFAULT GETDATE(),
    CONSTRAINT uq_indicador_periodo UNIQUE (indicador, periodo)
);
```

---

## 📊 Vistas analíticas para Power BI

El archivo `sql/views.sql` expone 8 vistas listas para conectar desde Power BI:

| Vista | Filas | Propósito |
|---|---|---|
| `vw_calendario` | 72 | Dimensión tiempo con `fecha DATE`, `anio`, `mes`, `anio_mes` |
| `vw_indicadores_long` | 288 | Tabla de hechos con fecha tipada |
| `vw_indicadores_pivot` | 72 | TC, inflación, reservas y tasa en columnas por período |
| `vw_tipo_cambio_anual` | 6 | Promedio, min, max, cierre anual del tipo de cambio |
| `vw_inflacion_vs_tasa` | 72 | Inflación vs tasa referencia lado a lado con lags |
| `vw_reservas_tendencia` | 72 | Variación % MoM, media móvil 12m, alerta caída >5% |
| `vw_outliers` | — | Valores fuera de rango esperado |
| `vw_ultima_carga` | 4 | Metadatos de actualización por indicador |

Desde Power BI: `Sql.Database("localhost", "bcrp_etl")` → seleccionar vista.

---

## 🛠️ Stack tecnológico

| Capa | Tecnología | Uso |
|---|---|---|
| Extracción | `requests` | Consumo de API REST BCRP |
| Transformación | `pandas` | Limpieza, normalización, tipado |
| Validación | `pandas` + lógica custom | Control de calidad de datos |
| Carga | `SQLAlchemy` + `pyodbc` | Upsert incremental a SQL Server |
| Configuración | `python-dotenv` | Variables de entorno seguras |
| Reportes | `Jinja2` | Reporte HTML de cada ejecución |
| Contenedorización | Docker + Compose | Portabilidad sin instalación |
| Logging | `logging` (stdlib) | Trazabilidad completa en archivo + consola |

---

## 📈 Posibles extensiones

- [ ] Orquestación con Apache Airflow (DAG con schedule diario)
- [ ] Migración de destino a Azure SQL Database
- [ ] Dashboard en Power BI conectado directamente a SQL Server
- [ ] Cobertura de tests con `pytest`
- [x] Contenedorización con Docker

---

## 👤 Autor

**Marco Rodrigo Polo Silva** — Data Engineer Jr.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Marco_Polo-0077B5?logo=linkedin)](https://www.linkedin.com/in/noark-mps/)
[![GitHub](https://img.shields.io/badge/GitHub-TU_USUARIO-181717?logo=github)](https://github.com/MarteDevs)

---

## 📄 Licencia

MIT License — libre para uso y modificación con atribución.
