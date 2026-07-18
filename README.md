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

# Installation & Local Run (Phase 1)

Follow these steps to set up and run the Phase 1 implementation locally.

## 1. Prerequisites
- **Python**: Version 3.10 or higher.
- **PostgreSQL**: Local database instance running.
- **Static Web Server**: Visual Studio Code Live Server extension or Python's built-in `http.server`.

---

## 2. Database Creation
Connect to your local PostgreSQL instance and execute the SQL command below to create the database:
```sql
CREATE DATABASE business_intelligence;
```

---

## 3. Backend Setup
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```
4. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure environment variables:
   - Copy `.env.example` to a new file named `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and fill in your local database credentials under `DATABASE_URL`, and optionally customize `JWT_SECRET`.

---

## 4. Run Backend
Start the FastAPI server using `uvicorn`:
```bash
uvicorn app.main:app --reload
```
Once started, the backend API will run on `http://127.0.0.1:8000`. You can inspect endpoints and use interactive testing via Swagger at `http://127.0.0.1:8000/docs`.

---

## 5. Serve Frontend
The frontend consists of static vanilla HTML/JS/CSS assets.
1. Open the project root or `frontend` directory in VS Code.
2. Launch the **Live Server** extension (typically hosts on `http://127.0.0.1:5500`).
3. Alternatively, serve the files using python in a terminal from the `frontend/` directory:
   ```bash
   cd frontend
   python -m http.server 5500
   ```
4. Visit `http://127.0.0.1:5500/index.html` (or `http://localhost:5500`) in your web browser.


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
