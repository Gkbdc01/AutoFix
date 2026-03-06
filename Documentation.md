# 🔧 AutoFix — AI-Driven Bug Detection & Code Debugger for VS Code

> AutoFix is a Visual Studio Code extension that **automatically detects bugs in your code on every save** and offers **one-click AI-powered fixes** — powered by a FastAPI backend connected to **Azure AI Foundry (GPT-5-nano)**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-66.8%25-blue)
![JavaScript](https://img.shields.io/badge/JavaScript-33.2%25-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Azure](https://img.shields.io/badge/Azure-AI%20Foundry-blue)

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Architecture](#3-architecture)
4. [Project Structure](#4-project-structure)
5. [Tech Stack](#5-tech-stack)
6. [Quick Start Guide](#6-quick-start-guide)
7. [API Endpoints](#7-api-endpoints)
8. [Security](#8-security)
9. [Future Scope](#9-future-scope)
10. [Team](#10-team)
11. [License](#11-license)

---

## 1. Project Overview

**AutoFix** is a developer productivity tool that brings real-time AI-powered bug detection directly into Visual Studio Code. Every time you save a file (`Ctrl+S`), AutoFix silently analyzes your code, highlights any errors inline, and offers a one-click fix — no context switching, no manual debugging.

### 🔄 Demo Flow

```
Write code  →  Save (Ctrl+S)  →  Error detected  →  Line highlighted red
                                        ↓
               Click "🔧 Fix This"  →  Code auto-corrected  →  ✅ No errors
```

AutoFix works with **any programming language** — Python, JavaScript, Java, C++, and more — making it a universal debugging companion for all developers.

### 🎯 Goals

- Detect bugs in real time on every file save inside VS Code
- Provide context-aware AI corrections using Azure AI Foundry (GPT-5-nano)
- Support any programming language — Python, JavaScript, Java, C++, and more
- Expose a clean, rate-limited REST API for seamless editor integration
- Keep the tool lightweight, local, and stateless — no database, no remote accounts required

### 📌 Key Highlights

| Attribute | Details |
|---|---|
| Project Type | VS Code Extension + FastAPI Backend |
| Primary Language | Python (66.8%) + JavaScript (33.2%) |
| AI Model | Azure AI Foundry — GPT-5-nano |
| Repository | https://github.com/Gkbdc01/AutoFix |
| License | MIT |
| Status | Active — Version 1.0 |

---

## 2. Features

AutoFix delivers a focused set of features designed to make real-time debugging frictionless. All core features are fully implemented in version 1.0.

| Feature | Status | Description |
|---|---|---|
| 🔍 Error Detection on Save | ✅ Implemented | Analyzes code via LLM every time a file is saved |
| 🔴 Error Line Highlighting | ✅ Implemented | Highlights the error line in red with hover details |
| 🔔 Toast Notifications | ✅ Implemented | Shows warning/info messages with error descriptions |
| 🩹 One-Click Fix | ✅ Implemented | "🔧 Fix This" button sends code to LLM and applies correction |
| 🌐 Multi-Language Support | ✅ Implemented | Works with Python, JavaScript, Java, C++, and any language |
| 🚦 Rate Limiting | ✅ Implemented | 30 requests/min per IP via SlowAPI to prevent abuse |
| ✅ Input Validation | ✅ Implemented | Pydantic v2 models validate all incoming API requests |
| 🔒 CORS Configuration | ✅ Implemented | Configured for seamless extension ↔ backend communication |

### Feature Details

#### 🔍 Error Detection on Save
Whenever you press `Ctrl+S` in VS Code, the AutoFix extension captures the active file content and language, then sends it to the backend for analysis. The LLM examines the code for syntax errors, missing tokens, invalid constructs, and logical issues — returning the result within milliseconds.

#### 🔴 Error Line Highlighting
When an error is found, the extension uses the VS Code Diagnostics API to draw a red underline on the specific line containing the error. Hovering over the line shows a tooltip with the exact error message and type, making it easy to understand what went wrong without leaving the editor.

#### 🩹 One-Click Fix
A "Fix This" button appears in a toast notification alongside the error message. Clicking it sends the code and error context to the backend's `/fix` endpoint. The AI returns corrected code which is automatically applied to the editor, replacing the file content with the fixed version.

#### 🌐 Multi-Language Support
Unlike traditional linters that are language-specific, AutoFix leverages an LLM that understands virtually every major programming language. The language is detected from the VS Code active file and included in the API request so the model can tailor its analysis accordingly.

---

## 3. Architecture

AutoFix is built on a two-component architecture: a lightweight VS Code Extension (JavaScript) that handles editor integration, and a FastAPI Backend (Python) that manages all AI processing and business logic.

### 3.1 Architecture Diagram

```
┌──────────────────────┐    POST /analyze    ┌───────────────────┐    ┌─────────────────────┐
│  VS Code Extension   │ ─────────────────▶  │  FastAPI Backend  │ ──▶│  Azure AI Foundry   │
│  (JavaScript)        │ ◀─────────────────  │  (Python)         │ ◀──│  GPT-5-nano         │
│                      │    POST /fix         │                   │    │                     │
│  • Error highlighting│                      │  • Input valid.   │    │  • Code analysis    │
│  • Toast messages    │                      │  • Rate limiting  │    │  • Error detection  │
│  • One-click fix     │                      │  • CORS config    │    │  • Code correction  │
└──────────────────────┘                      └───────────────────┘    └─────────────────────┘
```

### 3.2 Data Flow

The following steps describe the complete request lifecycle from editor action to code correction:

1. User saves a file in VS Code (`Ctrl+S`)
2. Extension captures the file content and language identifier
3. Extension sends a `POST /analyze` request to the FastAPI backend
4. Backend validates the input using Pydantic schemas
5. Backend checks rate limits (30 req/min per IP via SlowAPI)
6. Backend forwards the code to Azure AI Foundry (GPT-5-nano)
7. GPT-5-nano analyzes the code and returns error details (line, type, message)
8. Backend returns the structured response to the extension
9. If error found: extension highlights the line and shows a toast notification
10. User clicks "🔧 Fix This" — extension sends `POST /fix` to the backend
11. Backend calls GPT-5-nano with the code + error context
12. GPT-5-nano returns corrected code and explanation
13. Extension replaces the file content with the fixed code

### 3.3 Component Responsibilities

| Component | Technology | Responsibilities |
|---|---|---|
| VS Code Extension | JavaScript, VS Code API, Axios | Editor events, UI (highlights, toasts), HTTP calls to backend |
| FastAPI Backend | Python, FastAPI, Uvicorn | Request routing, validation, rate limiting, CORS, LLM orchestration |
| LLM Service | Azure AI Foundry, GPT-5-nano | Code analysis, error detection, code correction, explanations |
| Pydantic Models | Pydantic v2 | Request/response schema validation and serialization |
| Rate Limiter | SlowAPI | IP-based rate limiting at 30 requests per minute |

---

## 4. Project Structure

The repository is organized into two top-level folders — the VS Code extension and the FastAPI backend — each self-contained with its own dependencies and configuration.

```
AutoFix/
├── AutoFix-extension/            # VS Code extension (JavaScript)
│   ├── src/
│   │   └── extension.js          # Main extension logic (event listeners, API calls, UI)
│   ├── package.json              # Extension manifest, dependencies, activation events
│   └── README.md
│
├── AutoFix-backend/              # FastAPI backend (Python)
│   ├── app/
│   │   ├── main.py               # App entry point: FastAPI init, CORS, rate limiting
│   │   ├── routes/
│   │   │   ├── analyze.py        # POST /analyze — error detection endpoint
│   │   │   └── fix.py            # POST /fix — one-click correction endpoint
│   │   ├── services/
│   │   │   └── llm_service.py    # Azure AI Foundry integration (GPT-5-nano)
│   │   └── models/
│   │       └── schemas.py        # Pydantic request/response models
│   ├── .env.example              # Environment variable template (API keys)
│   ├── requirements.txt          # Python dependencies
│   └── README.md
│
├── Documentation.md              # Extended project documentation
├── .gitignore                    # Ignores .env, venv, node_modules, etc.
├── LICENSE                       # MIT License
└── README.md                     # Project overview and quick start
```

### Key Files Explained

| File | Purpose |
|---|---|
| `extension.js` | Core VS Code extension logic: handles onSave events, calls the backend, renders highlights and toasts, applies fixes |
| `main.py` | FastAPI application setup: registers routes, configures CORS middleware, initializes SlowAPI rate limiter |
| `analyze.py` | Defines the `POST /analyze` route: validates input and calls the LLM service to detect errors |
| `fix.py` | Defines the `POST /fix` route: validates input and calls the LLM service to generate corrected code |
| `llm_service.py` | Handles all Azure AI Foundry communication: builds prompts, sends requests, parses GPT-5-nano responses |
| `schemas.py` | Pydantic v2 models defining request and response shapes for all API endpoints |
| `.env.example` | Template for required environment variables — copy to `.env` and fill in your Azure API key |
| `requirements.txt` | Python package dependencies: fastapi, uvicorn, slowapi, pydantic, azure-ai-inference, etc. |

---

## 5. Tech Stack

AutoFix uses a modern, lightweight tech stack chosen for speed, simplicity, and ease of development. The backend is entirely Python-based, while the extension is pure JavaScript.

| Component | Technology | Notes |
|---|---|---|
| VS Code Extension | JavaScript | Uses VS Code Extension API for editor integration |
| HTTP Client (Extension) | Axios | Makes REST calls from extension to backend |
| Backend Framework | FastAPI | High-performance Python async API framework |
| ASGI Server | Uvicorn | Runs FastAPI with async support |
| AI / LLM | Azure AI Foundry (GPT-5-nano) | Handles code analysis and correction |
| Rate Limiting | SlowAPI | 30 req/min per IP |
| Input Validation | Pydantic v2 | Schema validation for all API requests |
| Backend Language | Python 3.9+ | Primary backend language |
| Extension Language | JavaScript | VS Code extension language |

---

## 6. Quick Start Guide

Follow this step-by-step guide to get AutoFix running locally. You will need to set up both the backend server and the VS Code extension.

### Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Python | 3.9+ | Required for the FastAPI backend |
| pip | Latest | For installing Python packages |
| Node.js | 16+ | Required for the VS Code extension |
| npm | Latest | For installing extension dependencies |
| Visual Studio Code | Latest | The target editor for the extension |
| Azure AI Foundry API Key | — | Required for GPT-5-nano access |

---

### 6.1 Backend Setup

**Step 1 — Clone the Repository**

```bash
git clone https://github.com/Gkbdc01/AutoFix.git
cd AutoFix
```

**Step 2 — Create and Activate a Virtual Environment**

```bash
cd AutoFix-backend

python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

**Step 3 — Install Python Dependencies**

```bash
pip install -r requirements.txt
```

**Step 4 — Configure Environment Variables**

```bash
cp .env.example .env
# Open .env and fill in your Azure AI Foundry API key
```

**Step 5 — Start the Backend Server**

```bash
uvicorn app.main:app --port 5000 --reload
```

> ✅ **Backend Running:** The API is now live at `http://localhost:5000`
> Visit `http://localhost:5000/docs` for the interactive Swagger UI.

---

### 6.2 Extension Setup

**Step 1 — Navigate to Extension Folder**

```bash
cd AutoFix-extension
```

**Step 2 — Install Dependencies**

```bash
npm install
```

**Step 3 — Launch the Extension**

Open the `AutoFix-extension` folder in VS Code, then press **F5** to launch the Extension Development Host. A new VS Code window will open with AutoFix active.

> ✅ **Extension Active:** Open any code file in the new window, make an error, and press `Ctrl+S`. AutoFix will detect the error and highlight the line automatically.

---

## 7. API Endpoints

The AutoFix backend exposes a simple REST API with two core endpoints for code analysis and fixing, plus a health check. All endpoints are available via Swagger UI at `/docs`.

**Base URL:** `http://localhost:5000`

### Endpoint Summary

| Method | Endpoint | Description | Returns |
|---|---|---|---|
| `POST` | `/analyze` | Analyze code for bugs | `{ hasError, line, message }` |
| `POST` | `/fix` | Fix a detected error | `{ fixed, fixedCode, explanation }` |
| `GET` | `/health` | Server health check | `{ status: "ok" }` |
| `GET` | `/docs` | Interactive Swagger UI | Browser documentation |

---

### 7.1 POST `/analyze`

Analyzes submitted source code and returns whether an error exists, the line number where it occurs, and a description of the error. This endpoint is called automatically on every file save.

**Request Body:**

```json
{
  "code": "def hello()\n    print('Hello')",
  "language": "python"
}
```

**Response — Error Found:**

```json
{
  "hasError": true,
  "line": 1,
  "message": "SyntaxError: Missing colon after function definition on line 1"
}
```

**Response — No Error:**

```json
{
  "hasError": false,
  "line": null,
  "message": null
}
```

---

### 7.2 POST `/fix`

Accepts code with a known error and returns a fully corrected version along with a plain-English explanation of what was changed. The corrected code is automatically applied to the editor.

**Request Body:**

```json
{
  "code": "def hello()\n    print('Hello')",
  "language": "python",
  "error": "SyntaxError: Missing colon after function definition on line 1"
}
```

**Response:**

```json
{
  "fixed": true,
  "fixedCode": "def hello():\n    print('Hello')",
  "explanation": "Added missing colon after the function definition on line 1."
}
```

---

### 7.3 GET `/health`

Simple health check to confirm the backend server is running and reachable.

**Response:**

```json
{
  "status": "ok"
}
```

---

### 7.4 GET `/docs`

Opens the automatically generated **Swagger UI** provided by FastAPI. From this browser interface you can explore all endpoints, view request/response schemas, and send live test requests to the API.

---

## 8. Security

AutoFix is designed as a local developer tool. The following security practices are implemented to ensure safe operation.

| Practice | Status | Implementation Details |
|---|---|---|
| Rate Limiting | ✅ Active | 30 requests/min per IP enforced via SlowAPI middleware |
| Input Validation | ✅ Active | All API inputs validated with Pydantic v2 schemas before processing |
| CORS | ✅ Configured | Cross-Origin headers scoped for extension ↔ backend communication |
| No Secrets in Repo | ✅ Safe | `.env` is gitignored; `.env.example` provided as a safe template |
| No Database | N/A | Stateless tool — no SQL/NoSQL, no persistent user data |
| No Authentication | N/A | Local-only extension — no remote users or accounts |

> 🔐 **Important:** Never commit your `.env` file to version control. Your Azure AI Foundry API key should only ever exist in your local `.env` file. The `.gitignore` in this repo already excludes `.env` by default.

---

## 9. Future Scope

The following enhancements are planned for future versions of AutoFix, based on user feedback and identified limitations of the current implementation.

| Feature | Priority | Description |
|---|---|---|
| Multi-error Detection | 🔴 High | Detect and highlight all errors simultaneously, not just the first one found |
| Error Severity Levels | 🔴 High | Distinguish between errors, warnings, and informational hints |
| Auto-fix on Save | 🟡 Medium | Optional setting to apply fixes automatically without clicking "🔧 Fix This" |
| Configurable Backend URL | 🟡 Medium | Allow users to set a custom backend URL through VS Code settings |
| Marketplace Publishing | 🟡 Medium | Publish AutoFix to the VS Code Extension Marketplace for wider distribution |
| Workspace-wide Analysis | 🟢 Low | Scan all files in a project, not just the currently active file |
| Diff View Before Fix | 🟢 Low | Show a side-by-side preview of what will change before applying the fix |

---

## 10. Team

AutoFix was built by a three-person team, each responsible for a distinct area of the project.

| Member | Role | Responsibilities |
|---|---|---|
| **Vivek Chaudhary** | Backend / AI Lead | FastAPI backend architecture, Azure AI Foundry integration, LLM service, Pydantic schemas |
| **Gaurav Kumar** | Frontend Lead | VS Code extension development, editor API integration, UI (highlights, toasts, fix button) |
| **Abhishek Narwar** | Testing & Documentation | End-to-end testing, bug reporting, project documentation, README and user guides |

---

## 11. License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Gkbdc01

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">Built with ❤️ by the AutoFix Team &nbsp;·&nbsp; Powered by FastAPI & Azure AI Foundry &nbsp;·&nbsp; <a href="https://github.com/Gkbdc01/AutoFix">github.com/Gkbdc01/AutoFix</a></p>
