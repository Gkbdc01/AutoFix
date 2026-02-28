# AutoFix Backend

FastAPI backend for the AutoFix VS Code extension. Receives source code from the extension on every file save, sends it to an LLM (Azure AI Foundry / OpenAI) for error analysis, and returns structured results. Also supports one-click error fixing.

## Architecture

```
VS Code Extension  ──POST /analyze──▶  FastAPI  ──▶  LLM (GPT-5-nano)  ──▶  JSON response
                   ──POST /fix─────▶  FastAPI  ──▶  LLM (GPT-5-nano)  ──▶  Fixed code
```

## Quick Start

### 1. Create a virtual environment

```bash
cd AutoFix-backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy the example env file and add your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-5-nano
AZURE_BASE_URL=https://your-resource.cognitiveservices.azure.com/openai/v1/
```

### 4. Run the server

```bash
uvicorn app.main:app --port 5000 --reload
```

The server will start at `http://localhost:5000`. The extension is hardcoded to call this address.

### 5. Verify

- **Health check:** `GET http://localhost:5000/health`
- **API docs:** `http://localhost:5000/docs` (Swagger UI)
- **Redoc:** `http://localhost:5000/redoc`

## API

### `POST /analyze`

Analyzes code for the single most critical error.

**Request:**

```json
{
  "language": "python",
  "code": "def foo():\n  return 1\n  print('unreachable')"
}
```

**Response (error found):**

```json
{
  "hasError": true,
  "line": 3,
  "message": "Unreachable code after return statement.",
  "source": "llm"
}
```

**Response (no error):**

```json
{
  "hasError": false,
  "line": null,
  "message": null,
  "source": "llm"
}
```

### `POST /fix`

Accepts code along with the detected error and returns the corrected source code.

**Request:**

```json
{
  "language": "python",
  "code": "def add(a, b):\n    return a +\n",
  "line": 2,
  "message": "Syntax error: '+' operator is missing its right-hand operand."
}
```

**Response (fix applied):**

```json
{
  "fixed": true,
  "fixedCode": "def add(a, b):\n    return a + b\n",
  "explanation": "Added missing right-hand operand 'b' to the '+' operator on line 2.",
  "source": "llm"
}
```

**Response (fix failed):**

```json
{
  "fixed": false,
  "fixedCode": null,
  "explanation": "LLM call failed: ...",
  "source": "error"
}
```

### `GET /health`

Returns `{"status": "ok"}`.

## Response `source` Field

Both `/analyze` and `/fix` include a `source` field to help with debugging:

| Value | Meaning |
|-------|---------|
| `llm` | LLM responded successfully — result is real |
| `error` | LLM call failed — check `message` or `explanation` for details |
| `fallback` | API key or base URL not configured |

## Project Structure

```
AutoFix-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic request/response models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analyze.py       # POST /analyze endpoint
│   │   └── fix.py           # POST /fix endpoint
│   └── services/
│       ├── __init__.py
│       └── llm_service.py   # LLM integration (analyze + fix)
├── .env                      # Your local config (gitignored)
├── .env.example              # Template for teammates
├── requirements.txt
└── README.md
```
