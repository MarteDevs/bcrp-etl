# 🇵🇪 Pipeline ETL — Indicadores Económicos BCRP

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL_Server-2019-red?logo=microsoftsqlserver&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.1-150458?logo=pandas&logoColor=white)
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
│   ├── transformer.py     # Limpieza, normalización y tipado de datos
│   ├── validator.py       # Validación de estructura, rangos y duplicados
│   └── loader.py          # Carga incremental (upsert) a SQL Server
├── sql/
│   └── create_tables.sql  # DDL del esquema de base de datos
├── logs/                  # Generado automáticamente en ejecución
├── .env.example           # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── main.py                # Orquestador del pipeline
```

---

## ⚙️ Instalación y uso

### Requisitos

- Python 3.10+
- SQL Server (local o remoto) con ODBC Driver 17
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/bcrp-etl.git
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
python main.py
```

### Salida esperada

```
2025-06-01 [INFO] main — === Iniciando pipeline ETL BCRP ===
2025-06-01 [INFO] main — --- Fase 1: Extracción ---
2025-06-01 [INFO] extractor — Extrayendo: tipo_cambio_usd_pen (PD04638PD)
2025-06-01 [INFO] extractor —   → 72 periodos recibidos
2025-06-01 [INFO] main — --- Fase 3: Validación ---
2025-06-01 [INFO] validator —   ✓ Estructura OK — 280 registros, 4 indicadores
2025-06-01 [INFO] validator —   ✓ Sin valores nulos en columnas críticas
2025-06-01 [INFO] validator —   📊 Resumen: tipo_cambio_usd_pen min=3.31 max=3.92
2025-06-01 [INFO] main — === Pipeline completado ===
```

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
    id           INT IDENTITY(1,1) PRIMARY KEY,
    indicador    NVARCHAR(100)  NOT NULL,   -- Nombre del indicador
    periodo      NVARCHAR(20)   NOT NULL,   -- Ej: "Ene.2024"
    valor        FLOAT,                     -- Valor numérico del indicador
    nombre_api   NVARCHAR(300),             -- Nombre oficial según la API BCRP
    fecha_carga  DATETIME DEFAULT GETDATE(),
    CONSTRAINT uq_indicador_periodo UNIQUE (indicador, periodo)
);
```

---

## 🛠️ Stack tecnológico

| Capa | Tecnología | Uso |
|---|---|---|
| Extracción | `requests` | Consumo de API REST BCRP |
| Transformación | `pandas` | Limpieza, normalización, tipado |
| Validación | `pandas` + lógica custom | Control de calidad de datos |
| Carga | `SQLAlchemy` + `pyodbc` | Upsert incremental a SQL Server |
| Configuración | `python-dotenv` | Variables de entorno seguras |
| Logging | `logging` (stdlib) | Trazabilidad completa en archivo + consola |

---

## 📈 Posibles extensiones

- [ ] Orquestación con Apache Airflow (DAG con schedule diario)
- [ ] Migración de destino a Azure SQL Database
- [ ] Dashboard en Power BI conectado directamente a SQL Server
- [ ] Cobertura de tests con `pytest`
- [ ] Contenedorización con Docker

---

## 👤 Autor

**Marco Rodrigo Polo Silva** — Data Engineer Jr.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Marco_Polo-0077B5?logo=linkedin)](https://linkedin.com/in/tu-perfil)
[![GitHub](https://img.shields.io/badge/GitHub-TU_USUARIO-181717?logo=github)](https://github.com/TU_USUARIO)

---

## 📄 Licencia

MIT License — libre para uso y modificación con atribución.
