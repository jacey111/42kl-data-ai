# Project Description

This project implements a local ETL (Extract, Transform, Load) pipeline for processing job listing data stored in '.mhtml' web archive files.

The pipeline follows a Medallion Architecture design pattern:
- **Bronze Layer ('1_bronze')**: raw extracted HTML
- **Silver Layer ('2_silver')**: cleaned and structured JSON
- **Gold Layer ('3_gold')**: SQLite database

The pipeline performs:
1. Extraction of HTML from MHTML files
2. Cleaning and structuring of job listing data
3. Validation using Pydantic models
4. Saving to JSON files
5. Loading into SQLite database
6. Data quality profiling and reporting

The project demonstrates foundational data engineering concepts including:
- ETL pipelines
- Data validation
- Idempotent processing
- Medallion architecture
- Data profiling
- CLI orchestration

---

# Setup Instructions

Install the following:
- Python 3.14
- Git
- Visual Studio Code
- 'uv' package manager

## Install Python

Create a '.python-version' file, and include:
3.14

## Install 'uv'

Follow the installation guide:
https://docs.astral.sh/uv/getting-started/installation/ 

Example (macOS):
curl -LsSf https://astral.sh/uv/install.sh | sh

Run 'uv python install', proceed with 'uv init', and 'uv venv' to setup virtual environment

Run 'uv add bs4 ruff pydantic' to add the BeautifulSoup, Ruff linter/formatter, and pydantic package

## Clone Repository

git clone <git@github.com:jacey111/42kl-data-ai.git>
cd week1

---

# Usage

1. Extract HTML, run:
'python main.py ingest'

2. Clean & Structure Data, run:
'python main.py process'

3. Load into SQLite, run:
'python main.py load'

4. Data Quality Report, run:
'python main.py profile'

OR

Run full pipeline, run :
'python main.py all'

---

# Technical Reflections

### Module 1: The Extractor (Medallion & Lakehouses)

**What We Did:** Setup folder-based Medallion Architecture `(0_source to 3_gold)`. Extracted raw `.mhtml` files to `1_bronze/`.
**Industry Context:** Modern data platforms often use ***Data Lakes*** to store raw files before transforming them into structured, query-ready data in a ***Data Warehouse**.*
**Reflection:** Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?
- **Answer:** Keeping raw HTML files preserves the original source of truth, which is critical for debugging and data recovery. If parsing logic changes or bugs are discovered later, the pipeline can be re-run without needing to re-download or re-scrape data. It also allows engineers to compare raw vs processed outputs to identify where transformation errors occurred, making debugging significantly easier and more transparent.

---

### Module 2: Treatment Plant (ETL vs ELT & Scale)

**What We Did:** Clean HTML `(transform into 2_silver/)` before database load `(load into 3_gold/)` (ETL).
**Industry Context:** Cloud platforms ***(Snowflake/BigQuery)*** often store raw data first then transform later ***(ELT)***. Enterprise systems use ***Apache Spark*** to process large amounts of data in parallel instead of one file at a time.
**Reflection:** Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?
- **Answer:** Cloud systems prefer ELT because storing raw data is cheap and flexible, while transformation logic may change over time. Loading raw data first allows multiple transformations to be applied later without losing information. Sequential processing becomes slow and inefficient at scale because files are processed one by one. Distributed processing frameworks solve this by splitting data across multiple nodes and processing in parallel, improving speed and scalability.

---

### Module 3: The Blueprint & The Vault (Storage & Contracts)

**What We Did:** Used SQLite as Gold “warehouse” layer. Enforced basic data integrity via idempotency during load.
**Industry Context:** Production systems often separate databases used for day-to-day application operations ***(OLTP)*** from databases optimized for analytics and reporting ***(OLAP)***. Strict Data Contracts help ensure incomplete or corrupted data does not break dashboards, analytics, or downstream systems.
**Reflection:** What should happen if an important field like `job_title` disappears? Why fail early instead of silently inserting `nulls` into DB? How does `INSERT OR IGNORE` help prevent duplicate records?
- **Answer:** If a critical field like 'job_title' is missing, the pipeline should reject the record during validation instead of inserting incomplete data. Failing early prevents corrupted data from spreading into downstream analytics systems, which could lead to incorrect insights or decisions. 'INSERT OR IGNORE' prevents duplicate records by discarding new rows that violate unique constraints or primary keys, rather than crashing or stopping the insertion process.

---

### Module 4: The QA Inspector & Orchestrator (Orchestration & DAGs)

**What We Did:** `main.py` acts as manual orchestrator, `all` command finalizes sequence
**Industry Context:** Real-world pipelines usually use orchestration tools like ***Airflow***, which automate execution, retries, scheduling, and dependency management.
**Reflection:** What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?
- **Answer:** If 'processor.py' crashes during execution, a manual pipeline requires human intervention to identify the failure point and restart the process. Automated orchestration tools are more reliable than manual retries with Python scripts because they offer centralized monitoring, intelligent error handling (retries with backoff), and automated dependency management, ensuring workflows complete without manual intervention.