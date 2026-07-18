# AI Business Intelligence Assistant

> **Transform organizational reports into actionable business insights
> using Artificial Intelligence, Prompt Engineering, and Business
> Intelligence techniques.**

------------------------------------------------------------------------

# Overview

AI Business Intelligence Assistant is a web-based analytics platform
that automates business report analysis. It enables organizations to
upload CSV, Excel, PDF, and Word reports, automatically process the
data, calculate Key Performance Indicators (KPIs), generate interactive
dashboards, and produce AI-powered executive summaries, trend analysis,
and strategic recommendations using locally hosted Large Language Models
(LLMs) through Ollama.

The platform is designed to reduce manual reporting effort while
enabling faster, data-driven decision-making while keeping all AI
processing local.

------------------------------------------------------------------------

# Features

-   Secure JWT Authentication
-   Upload CSV, Excel, PDF, and Word reports
-   Automatic data cleaning and preprocessing
-   KPI calculation engine
-   Interactive BI dashboards
-   Executive Summary generation
-   Trend Analysis
-   AI-powered Business Recommendations
-   Report history management
-   Responsive Bootstrap 5 interface
-   Fully local AI inference using Ollama

------------------------------------------------------------------------

# Technology Stack

## Frontend

-   HTML5
-   Bootstrap 5
-   Vanilla JavaScript (ES6)
-   Apache ECharts
-   Bootstrap Icons

## Backend

-   FastAPI
-   SQLAlchemy
-   Pydantic
-   Uvicorn

## Database

-   PostgreSQL

## Artificial Intelligence

-   Ollama
-   Qwen 2.5 (Primary)
-   Llama 3.1 (Secondary)
-   Prompt Engineering

## Data Processing

-   Pandas
-   NumPy

## File Parsing

-   openpyxl
-   pdfplumber
-   python-docx

## Authentication

-   JWT (JSON Web Tokens)

------------------------------------------------------------------------

# System Architecture

``` text
                HTML5 + Bootstrap 5 + JavaScript
                            │
                            ▼
                     FastAPI REST API
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
 Authentication      File Upload      Report History
        │                 │
        ▼                 ▼
      JWT          File Processing
                          │
                          ▼
                 Pandas Data Cleaning
                          │
                          ▼
                  KPI Calculation Engine
                          │
                          ▼
                  Prompt Engineering Layer
                          │
                          ▼
                Ollama (Qwen2.5 / Llama3.1)
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
 Executive Summary   Trend Analysis   Recommendations
                          │
                          ▼
                     PostgreSQL
                          │
                          ▼
              Apache ECharts Dashboard
```

------------------------------------------------------------------------

# Project Structure

``` text
AI-Business-Intelligence-Assistant/

├── frontend/
│   ├── assets/
│   ├── css/
│   ├── js/
│   ├── pages/
│   ├── components/
│   └── index.html
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── analytics/
│   │   ├── auth/
│   │   ├── database/
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── upload/
│   │   ├── utils/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
│
├── uploads/
├── reports/
├── README.md
└── LICENSE
```

------------------------------------------------------------------------

# Workflow

1.  User logs in using JWT authentication.
2.  Uploads a business report.
3.  Backend validates and parses the file.
4.  Data is cleaned using Pandas.
5.  KPIs are calculated.
6.  Prompt is generated.
7.  Ollama analyzes the processed data.
8.  AI returns:
    -   Executive Summary
    -   Trend Analysis
    -   Strategic Recommendations
9.  Dashboard is generated using Apache ECharts.
10. Results are stored in PostgreSQL.

------------------------------------------------------------------------

# Installation

## Clone Repository

``` bash
git clone https://github.com/yourusername/AI-Business-Intelligence-Assistant.git
cd AI-Business-Intelligence-Assistant
```

## Backend Setup

``` bash
python -m venv .venv
```

### Windows

``` bash
.venv\Scripts\activate
```

### Install Dependencies

``` bash
pip install -r requirements.txt
```

## PostgreSQL

Create a database named:

``` sql
CREATE DATABASE business_intelligence;
```

## Install Ollama

``` bash
ollama pull qwen2.5:7b
ollama pull llama3.1:8b
ollama serve
```

## Run Backend

``` bash
uvicorn app.main:app --reload
```

Open:

-   API: http://127.0.0.1:8000
-   Swagger: http://127.0.0.1:8000/docs

## Frontend

Open the project using a local web server (e.g., VS Code Live Server).

------------------------------------------------------------------------

# Roadmap

## Phase 1

-   Authentication
-   Project Setup
-   Frontend Layout
-   Database Configuration

## Phase 2

-   File Upload
-   File Parsing
-   KPI Calculation

## Phase 3

-   Interactive Dashboard
-   Charts
-   Report History

## Phase 4

-   AI Integration
-   Executive Summary
-   Trend Analysis
-   Business Recommendations

## Phase 5

-   Testing
-   Documentation
-   Deployment

------------------------------------------------------------------------

# Future Enhancements

-   AI Chat with Reports
-   Forecasting Models
-   RAG Integration
-   Multi-Organization Support
-   Email Reports
-   Real-Time Dashboards
-   Business Alerts
-   ERP / CRM Connectors

------------------------------------------------------------------------

# License

This project is intended for educational and research purposes.
