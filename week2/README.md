# Project Overview

This project builds a hybrid **data engineering + LLM pipeline system** that processes job listings and resumes to perform structured skill intelligence analysis.

The system combines:
- Local LLM inference (Ollama)
- Cloud LLM inference (Google Gemini API)
- Deterministic data processing pipelines
- SQLite-based structured storage

## Core Objectives:
- Enrich raw job data using LLM-based tagging
- Provide a unified interface for multiple LLM providers
- Extract structured skill gaps from resumes
- Demonstrate ETL + LLM orchestration patterns

---

# Setup Instructions

Run the following in your terminal:

## Clone Repository

git clone <git@github.com:jacey111/42kl-data-ai.git>

cd week2


## Initialize Virtual Environment

uv venv

source .venv/bin/activate


## Install Ollama

Go to: https://ollama.com

Download for your OS


OR run

curl -fsSL https://ollama.com/install.sh | sh


## Verify Installation and Ollama API

ollama -v

curl 127.0.0.1:11434


## Download Models

ollama pull llama3.1

ollama pull phi3

ollama pull deepseek-r1:1.5b


## Verify Models

ollama ls


## Create Google AI API Key

Go to: https://aistudio.google.com/

Login

Click “Get API Key”

Create API key

Copy it

## Store API Key

touch .env


Inside .env, include this:

GOOGLE_API_KEY=your_api_key


## Edit .gitignore

Add:

.env


## Edit rate_limits.txt

Go to your Google AI dashboard and find rate limits for:
- Gemini 2.5 Flash (`gemini-2.5-flash`)
- Gemini 2.5 Flash Lite (`gemini-2.5-flash-lite`)
- Gemini 3 Flash (`gemini-3-flash-preview`)

Edit the values in the file with this format:
gemini-2.5-flash <RPM> <TPM> <RPD>
gemini-2.5-flash-lite <RPM> <TPM> <RPD>
gemini-3-flash-preview <RPM> <TPM> <RPD>

---

# Usage

1. LLM Interface Layer

uv run prompt_model.py <model> "<prompt>"

Example:
    uv run prompt_model.py llama3.1 "Hello"
Purpose:
    Unified interface for:
    - Ollama (local models)
    - Google Gemini API (cloud models)
Output:
    Text response from selected model (llama3.1) with error handling and fallback support.

2. Data Tagging (LLM-based ETL enrichment)

uv run tag_data.py <database_path>

Purpose:
    - Reads raw job descriptions from SQLite
    - Uses LLM to extract structured technical skills
    - Writes back enriched tech_stack column
Output Example:
    Analyzed Job 123456: Python, SQL, AWS, Docker
    Analyzed Job 123775: Java, Spring Boot, Microservices

3. Skill Gap Analysis

uv run find_skill_gaps.py

Purpose:
    - Loads resume text
    - Loads enriched job market skills
    - Computes deterministic skill gaps
Output Example:
    {"gaps": ["aws", "docker", "kubernetes"],
    "resume_skills": ["python", "sql"],
    "market_skills": ["aws", "docker", "kubernetes", "python", "sql"]}

---

# API / Function Reference

## prompt_model.py
Unified LLM interface supporting Ollama models like llama3.1, phi3, and deepseek-r1:1.5b


Function:
    
    def prompt_model(model: str, prompt: str) -> str


Purpose:
    Prompt the model with the input prompt and return a text response. 
    It will select the model based on the input model. 
    
Input: 
    - model: the name of the model to use, must be in OLLAMA_MODELS
    - prompt: the text prompt to send to the model

Output: 
    - the text response from the model, or an error message if any issue occurs    

Key Features:
    - Ollama API integration (localhost:11434)
    - Google Gemini API integration
    - Model routing logic
    - Safe failure handling (no crashes)


## tag_data.py
LLM-powered ETL enrichment system for job postings


Function:

    def tag_data(db_url: str)


Purpose:
    Read jobs from SQLite and populate tech_stack.
    1. Read job descriptions from database
    2. Batch processing for efficiency
    3. Send prompts to LLM
    4. Parse structured skill output
    5. Write results back to database

Input: 
    - database URL (file path for SQLite)

Output: 
    - None (updates tech_stack column in jobs table, and prints the results to the console)

Key Features:
    - Batch processing (rate limit safe)
    - Retry mechanism
    - JSON-safe parsing
    - LLM error handling


## find_skill_gaps.py
Deterministic skill gap computation engine


Function:

    def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult


Purpose:
    Find skill gaps between the resume and the market.
    1. Load resume text and market skills
    2. Extract the skills from the resume that exist in the market skills
    3. Get the skill gaps as the difference between market skills and resume skills
    4. Return the results in a structured format using SkillGapResult
    5. Handle any exceptions and return empty results if any error occurs 
     
Input:
    - input_file_path: path to the resume text file
    - db_url: path to the SQLite database containing job postings 
    
Output:
    - SkillGapResult object containing the skill gaps, resume skills, and market skills

Key Features:
    - Regex-based skill extraction
    - Alias expansion (C/C++, AWS, etc.)
    - Set-based comparison for deterministic output

    
---

# Data / Assumptions

## Data Sources

SQLite database (jobs.db)
    Table: jobs
    Columns:
        source_id (unique id, primary key)
        job_title (text not null)
        company (text not null)
        description (text not null)
        tech_stack (text, comma-separated) 

Resume input (resume.txt)
    - Pre-extracted plain text

## Assumptions

- Job descriptions are LLM-parsable
- Skills are comma-separated after tagging
- Resume is already cleaned text
- Skill matching is deterministic in final stage

## Data Flow Architecture

Raw Job Data
    ↓
tag_data.py (LLM enrichment)
    ↓
SQLite jobs.db (structured skills)
    ↓
find_skill_gaps.py
    ↓
Resume comparison engine
    ↓
SkillGapResult output

---

# Testing

1. LLM Testing
- Compare outputs across models (llama3.1 vs phi3 vs deepseek-r1:1.5b) using sample database in data/jobs_d1.db
- Check JSON validity of responses

2. Tagging Validation
- Verify tech_stack is non-empty after processing in jobs.db
- Ensure batch processing completes without crashing

3. Deterministic Skill Gap Testing
- Verify all skills in 'resume.txt' is included in resume_skills
- Ensure no duplicating skills
- Verify every skill in resume_skills does not appear in gaps, and every skill in gaps must exist in market_skills
- Check skills in market_skills to improve ALIASES dictionary
- Ensure all skills are normalized (lowercase + trimmed)

---

# Limitations

- LLM outputs may vary across runs (tagging stage)
- Local LLM inference (via Ollama) may cause system slowdown under heavy load
- Regex-based skill extraction may miss contextual skills
- Alias dictionary is manually maintained. Therefore, some skill variations or inconsistent naming conventions in job data may not be fully captured, potentially leading to minor inaccuracies in gap detection
- No semantic embedding matching yet, only matches exact words or predefined aliases
- Model performance and system stability depend on batch size and local hardware constraints
- Larger batch sizes may lead to increased memory usage, slower response times, or request timeouts depending on system resources and model size

---

# Architecture Reflection

## Design Choices
Why you structured your system the way you did (modularity, separation of concerns, etc.)

**Answer:** 
This system is designed as a hybrid LLM + deterministic pipeline:
LLMs are used for:
    - data enrichment (tag_data.py)
    - model abstraction (prompt_model.py)
Deterministic logic is used for:
    - skill gap computation (find_skill_gaps.py)

This separation ensures flexibility in data generation, and stability in analytical output.

## Trade-offs    
What you chose to prioritize (e.g. simplicity vs scalability, speed vs accuracy)

**Answer:**
- I prioritized simplicity and determinism over semantic intelligence by using regex and set-based logic.
- Separated LLM usage (data tagging) from deterministic computation (skill gap analysis) to ensure reproducibility and reduce runtime variability.
- Chose batch-based LLM processing to balance API efficiency and rate limit constraints, at the cost of requiring mannual batch size tuning for stability.
- Focused on low-cost and explainable processing rather than fully AI-driven decision-making in the final analytical layer.

## Improvements
What you would change or extend if given more time (e.g. better architecture, optimizations, additional features)

**Answer:**
- Replace regex matching with embedding-based similarity.
- Replace manual alias dictionary with a scalable or learned skill normalization system.
- Add JSON schema validation for LLM outputs in the tagging pipeline.
- Implement skill importance scoring based on job market frequency and demand.