# AI Business Intelligence Assistant

> Transform organizational reports into actionable business insights using Artificial Intelligence, Prompt Engineering, and Business Intelligence techniques.

---

# Overview

AI Business Intelligence Assistant is an intelligent analytics platform that automates business report analysis. It accepts organizational reports such as Excel, CSV, PDF, and Word documents, processes the data, calculates Key Performance Indicators (KPIs), generates interactive dashboards, produces executive summaries, identifies business trends, and provides AI-powered strategic recommendations using locally hosted Large Language Models (LLMs) through Ollama.

The objective is to reduce manual reporting effort and enable faster, data-driven decision-making.

---

# Features

* Secure user authentication using JWT
* Upload CSV, Excel, PDF, and Word reports
* Automatic data cleaning and preprocessing
* KPI calculation
* Interactive Business Intelligence dashboards
* Executive Summary generation
* Trend Analysis
* Business Recommendations using AI
* Report history
* Downloadable reports (Future)
* Multiple dashboard templates (Future)

---

# Technology Stack

## Frontend

* HTML5
* Tailwind CSS
* Vanilla JavaScript
* Apache ECharts

---

## Backend

* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

---

## Artificial Intelligence

* Ollama
* Qwen 2.5 / Llama 3.1
* Prompt Engineering

---

## Data Processing

* Pandas
* NumPy

---

## File Parsing

* pandas
* openpyxl
* pdfplumber
* python-docx

---

## Database

* PostgreSQL

---

## Authentication

* JWT (JSON Web Tokens)

---

# System Architecture

```text
                    HTML + Tailwind + JavaScript
                               │
                               ▼
                        FastAPI Backend
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   File Upload        Data Processing     Authentication
        │                  │                  │
        ▼                  ▼                  ▼
 File Parsing        KPI Calculation       JWT Tokens
        │                  │
        └──────────────┬───┘
                       ▼
                Prompt Generator
                       │
                       ▼
                 Ollama AI Model
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 Executive Summary   Trend Analysis   Recommendations
                       │
                       ▼
                  PostgreSQL Database
                       │
                       ▼
              Interactive BI Dashboard
```

---

# Project Structure

```text
AI-Business-Intelligence-Assistant/

│
├── frontend/
│   ├── pages/
│   ├── css/
│   ├── js/
│   ├── assets/
│   └── components/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── prompts/
│   │   ├── analytics/
│   │   ├── upload/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── uploads/
├── reports/
├── README.md
└── LICENSE
```

---

# Workflow

1. User logs in.
2. Uploads a business report.
3. Backend validates the file.
4. Data is cleaned using Pandas.
5. KPIs are calculated.
6. Prompt is generated.
7. Ollama analyzes the report.
8. AI returns:

   * Executive Summary
   * Trend Analysis
   * Strategic Recommendations
9. Dashboard is generated.
10. Results are stored in PostgreSQL.

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/AI-Business-Intelligence-Assistant.git

cd AI-Business-Intelligence-Assistant
```

---

## Backend Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Install PostgreSQL

Create a database:

```sql
CREATE DATABASE business_intelligence;
```

---

## Install Ollama

Download and install Ollama.

Pull a model:

```bash
ollama pull qwen2.5:7b
```

or

```bash
ollama pull llama3.1:8b
```

Run the model:

```bash
ollama serve
```

---

## Run Backend

```bash
uvicorn app.main:app --reload
```

Backend:

```
http://127.0.0.1:8000
```

Swagger:

```
http://127.0.0.1:8000/docs
```

---

## Frontend

Open `index.html` using a local development server (such as VS Code Live Server), or configure your preferred static server.

---

# Roadmap

## Phase 1

* User Authentication
* File Upload
* Dashboard
* KPI Calculation

## Phase 2

* Executive Summary
* Trend Analysis
* Recommendations

## Phase 3

* Report Export
* Dashboard Templates
* Report History

## Phase 4

* Forecasting
* Natural Language Queries
* Scheduled Reports
* Role-Based Access Control

---

# Future Enhancements

* AI Chat with Reports
* Forecasting Models
* RAG Integration
* Multi-Organization Support
* Email Reports
* Real-Time Dashboards
* Business Alerts
* Data Connectors (ERP, CRM, APIs)

---

# License

This project is intended for educational and research purposes.
