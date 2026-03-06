# AutoFix — AI-Driven Bug Detection & Code Debugger for VS Code

AutoFix is a Visual Studio Code extension that **automatically detects bugs in your code on every save** and offers **one-click AI-powered fixes**. It uses a FastAPI backend connected to Azure AI Foundry (GPT-5-nano) for real-time code analysis.

## Demo Flow

```
Write code → Save (Ctrl+S) → Error detected → Line highlighted red
                                    ↓
                         Click "🔧 Fix This" → Code auto-corrected → ✅ No errors
```

## Architecture

```
┌─────────────────────┐       POST /analyze          ┌──────────────────┐       ┌─────────────────┐
│   VS Code Extension │ ──────────────────────────▶ │  FastAPI Backend │ ────▶ │ Azure AI Foundry│
│   (TypeScript/JS)   │ ◀────────────────────────── │  (Python)        │ ◀──── │ GPT-5-nano      │
│                     │        POST /fix             │                  │       │                 │
│  • Error highlight  │                              │  • Input valid.  │       │ • Code analysis │
│  • Toast messages   │                              │  • Rate limiting │       │ • Error fixing  │
│  • One-click fix    │                              │  • CORS          │       │                 │
└─────────────────────┘                              └──────────────────┘       └─────────────────┘
```

## Project Structure

```
AutoFix/
├── AutoFix-extension/        # VS Code extension (JavaScript)
│   ├── src/
│   │   └── extension.js      # Main extension logic
│   ├── package.json           # Extension manifest
│   └── README.md
│
├── AutoFix-backend/           # FastAPI backend (Python)
│   ├── app/
│   │   ├── main.py            # App entry, CORS, rate limiting
│   │   ├── routes/
│   │   │   ├── analyze.py     # POST /analyze — error detection
│   │   │   └── fix.py         # POST /fix — one-click fix
│   │   ├── services/
│   │   │   └── llm_service.py # LLM integration (Azure AI Foundry)
│   │   └── models/
│   │       └── schemas.py     # Pydantic request/response models
│   ├── .env.example           # Environment template
│   ├── requirements.txt
│   └── README.md
│
└── README.md                  # This file
```

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Error detection on save | ✅ Implemented | Analyzes code via LLM every time a file is saved |
| Error line highlighting | ✅ Implemented | Highlights the error line in red with hover details |
| Toast notifications | ✅ Implemented | Shows warning/info messages with error descriptions |
| One-click fix | ✅ Implemented | "🔧 Fix This" button sends code to LLM, applies corrected code |
| Multi-language support | ✅ Implemented | Works with Python, JavaScript, Java, C++, and any language |
| Rate limiting | ✅ Implemented | 30 req/min per IP via SlowAPI |
| Input validation | ✅ Implemented | Pydantic models validate all API requests |
| CORS configuration | ✅ Implemented | Configured for extension ↔ backend communication |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Extension | JavaScript, VS Code API, Axios |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| LLM | Azure AI Foundry, GPT-5-nano |
| Rate Limiting | SlowAPI |
| Validation | Pydantic v2 |

## Quick Start

### Backend

```bash
cd AutoFix-backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # Add your API key
uvicorn app.main:app --port 5000 --reload
```

### Extension

```bash
cd AutoFix-extension
npm install
# Press F5 in VS Code to launch Extension Development Host
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Analyze code for errors — returns `{ hasError, line, message }` |
| `POST` | `/fix` | Fix a detected error — returns `{ fixed, fixedCode, explanation }` |
| `GET` | `/health` | Health check — returns `{ status: "ok" }` |
| `GET` | `/docs` | Swagger UI (interactive API docs) |

## Security

| Practice | Status |
|----------|--------|
| Rate Limiting | ✅ 30 req/min via SlowAPI |
| Input Validation | ✅ Pydantic schema validation |
| CORS | ✅ Configured |
| No secrets in repo | ✅ `.env` gitignored, `.env.example` provided |
| No database | N/A — stateless local tool, no SQL/NoSQL needed |
| No auth | N/A — local-only extension, no remote users |

## Future Scope

- [ ] Multi-error detection — highlight all errors at once, not just the first
- [ ] Error severity levels — warning vs error vs info
- [ ] Auto-fix on save (optional setting) — skip the button click
- [ ] Configurable backend URL via VS Code settings
- [ ] Extension marketplace publishing
- [ ] Support for workspace-wide analysis (not just active file)
- [ ] Diff view before applying fix — show what will change

## Team

| Member | Role |
|--------|------|
| Vivek Chaudhary | Backend/AI Lead — LLM Integration, FastAPI |
| Gaurav Kumar | Frontend Lead — VS Code Extension |
| Abhishek Narwar | Testing & Documentation |

## License

MIT
