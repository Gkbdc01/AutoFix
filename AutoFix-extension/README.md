# AutoFix — VS Code Extension

AI-powered error detection and one-click fix for Visual Studio Code. Analyzes your code on every save using GPT-5-nano and highlights errors directly in the editor.

## Features

### Error Detection on Save
Save any file → AutoFix sends the code to the backend → errors are highlighted in red.

### One-Click Fix
When an error is detected, click **"🔧 Fix This"** in the notification → the LLM generates and applies the corrected code automatically.

### Multi-Language Support
Works with any language supported by VS Code — Python, JavaScript, TypeScript, Java, C++, Go, and more.

## Requirements

- **AutoFix Backend** must be running on `http://localhost:5000`
- Node.js 18+
- VS Code 1.96+

## Setup

```bash
cd AutoFix-extension
npm install
```

### Run in Development
1. Open this folder in VS Code
2. Press **F5** → launches Extension Development Host
3. In the new window, open any code file
4. Save (**Ctrl+S**) → errors will be highlighted

### Backend (required)
```bash
cd ../AutoFix-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 5000 --reload
```

## How It Works

1. **`onDidSaveTextDocument`** — listens for file saves
2. Sends `{ language, code }` to `POST http://localhost:5000/analyze`
3. If error found → highlights the line in red + shows hover message + toast notification
4. User clicks **"🔧 Fix This"** → sends to `POST http://localhost:5000/fix`
5. Receives corrected code → replaces file content → auto-saves → re-analyzes

## Extension Settings

Currently no configurable settings. Future versions will add:
- Configurable backend URL
- Toggle auto-fix on save
- Error severity filtering

## Known Limitations

- Detects one error at a time (most critical first)
- Requires backend server running locally
- LLM response time depends on network and Azure AI Foundry latency

---

## Working with Markdown

You can author your README using Visual Studio Code.  Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux)
* Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux)
* Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets

## For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**
