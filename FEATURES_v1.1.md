# AutoFix v1.1 — New Features Guide

## 🎯 Overview

AutoFix v1.1 introduces powerful new features for better error analysis, user control, and productivity:

- **Multi-Error Detection**: Find up to 5 errors per file, not just the critical one
- **Diff Preview**: Review changes before applying fixes
- **Smart Caching**: Reduce API calls with intelligent result caching
- **Error Dashboard**: Real-time statistics and error history
- **Custom Configuration**: Control severity levels and error filtering
- **Debouncing**: Prevent analysis spam during rapid saves

---

## 📊 Multi-Error Detection

### What's New?

Previously, AutoFix only showed the **single most critical error** per file. Now it can detect **up to 5 errors** with different types and severity levels:

- **Error Types**: `syntax`, `logic`, `performance`, `security`, `general`
- **Severity Levels**: `error` (red), `warning` (orange), `info` (blue)

### How It Works

1. Save your file → AutoFix analyzes and finds all errors
2. Errors are displayed with color-coded lines:
   - **Red**: Critical errors (must fix)
   - **Orange**: Warnings (should fix)
3. Toast shows first error + error count: `"Found 3 errors. First error on line 12..."`
4. Click "📊 Show All" to see all errors in a quick picker

### Example Response

```json
{
  "hasError": true,
  "errors": [
    {
      "line": 5,
      "message": "Unused variable 'temp'",
      "errorType": "general",
      "severity": "warning"
    },
    {
      "line": 8,
      "message": "Division by zero",
      "errorType": "logic",
      "severity": "error"
    }
  ]
}
```

---

## 🔀 Diff Preview Before Fixing

### What's New?

Fear of breaking your code? Now you can **preview the fix** before applying it!

When you click "🔧 Fix This":
1. A side-by-side diff panel opens
2. Shows **before/after** with line-by-line changes
3. **Red lines** = removed code
4. **Green lines** = added code
5. Choose to accept or reject the fix

### Example Workflow

```python
# BEFORE: Division by zero
result = x / 0

# AFTER: AutoFix suggests this fix
if y != 0:
    result = x / y
else:
    result = None
```

The diff preview shows:
```
--- original.txt
+++ fixed.txt
-result = x / 0
+if y != 0:
+    result = x / y
+else:
+    result = None
```

---

## ⚡ Smart Caching

### What's New?

AutoFix now **caches analysis results** to dramatically reduce API calls and speed up analysis:

- **Cache TTL**: 5 minutes per file hash
- **Debounce Wait**: 500ms to prevent repeated analysis during rapid saves
- **Cache Invalidation**: Automatic when file content changes

### How It Saves You

| Scenario | Without Cache | With Cache |
|----------|------------|-----------|
| Save file 5 times without changes | 5 API calls | 1 API call ✅ |
| Modify line 1 and save 3x | 3 API calls | 1 API call ✅ |
| Type rapidly (10 saves in 2 sec) | 10 API calls ⚠️ | 1-2 API calls ✅ |

**Result**: Faster response times + lower backend costs!

---

## 📊 Error Dashboard

### What's New?

A new **sidebar panel** in VS Code showing real-time error statistics:

**Location**: Explorer sidebar → "AutoFix Dashboard"

**Shows**:
- Total errors detected (session)
- Errors by type (syntax, logic, performance, security)
- Errors by severity (error, warning, info)
- File with most errors
- Recent 10 errors with timestamps

### Example Dashboard

```
📊 Error Statistics
  Total Errors: 42
  Most errors in: main.py
  
📈 Recent Errors
  ├── app.js:45 - Undefined variable (warning)
  ├── utils.py:12 - Division by zero (error)
  ├── config.js:8 - Missing import (error)
  └── ...
```

### Refresh Behavior

Dashboard updates **automatically** after each analysis. You can also use the command:

```
AutoFix: Reload Configuration
```

---

## ⚙️ Custom Configuration (`.autofixconfig.json`)

### What's New?

Control how AutoFix behaves with a project-level config file!

### Creating the Config File

Create `.autofixconfig.json` in your project root:

```json
{
  "enabled": true,
  "severity": {
    "syntax": "error",
    "logic": "error",
    "performance": "warning",
    "security": "error"
  },
  "ignoreRules": [],
  "debounceMs": 500,
  "maxErrors": 5
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable AutoFix for this project |
| `severity.syntax` | string | `"error"` | Severity for syntax errors |
| `severity.logic` | string | `"error"` | Severity for logic errors |
| `severity.performance` | string | `"warning"` | Severity for performance issues |
| `severity.security` | string | `"error"` | Severity for security issues |
| `ignoreRules` | array | `[]` | List of error types to ignore |
| `debounceMs` | number | `500` | Debounce time between saves (ms) |
| `maxErrors` | number | `5` | Max errors to report per file |

### Example Configurations

**Strict Mode** (catch everything):
```json
{
  "severity": {
    "syntax": "error",
    "logic": "error",
    "performance": "error",
    "security": "error"
  },
  "maxErrors": 10
}
```

**Permissive Mode** (only critical issues):
```json
{
  "severity": {
    "performance": "info",
    "security": "error"
  },
  "maxErrors": 3,
  "ignoreRules": ["general"]
}
```

**Fast Mode** (aggressive caching):
```json
{
  "debounceMs": 1000,
  "maxErrors": 2
}
```

---

## 🔄 Debouncing

### What's New?

AutoFix is now **smart about when to analyze**:

- **During rapid typing**: Analysis waits until you stop (500ms delay)
- **Multiple rapid saves**: Only analyzes once per batch
- **Customizable**: Set `debounceMs` in `.autofixconfig.json`

### Benefits

1. **Better Performance**: No lag during fast typing
2. **Lower API Cost**: Fewer redundant calls
3. **Cleaner UI**: Less flashing errors while typing

### Example

```python
# Scenario: You type and save rapidly

Write code → Save (less than 500ms) → Debounce waits
              Save again
              Save again
                            → Wait 500ms → Single analysis ✅
```

---

## 📈 Error History & Statistics

### New Endpoints

The backend now tracks all errors found in your session:

#### `GET /stats` — Error Statistics

```bash
curl http://localhost:5000/stats
```

**Response**:
```json
{
  "totalErrors": 42,
  "errorsByType": {
    "syntax": 8,
    "logic": 15,
    "performance": 12,
    "security": 7
  },
  "errorsBySeverity": {
    "error": 30,
    "warning": 12
  },
  "mostCommonFile": "/src/main.py",
  "recentErrors": [...]
}
```

#### `GET /history` — Recent Errors

```bash
curl http://localhost:5000/history?limit=20
```

Shows the 20 most recent errors with timestamps, file paths, and fix status.

#### `POST /history/clear` — Clear History

```bash
curl -X POST http://localhost:5000/history/clear
```

Clears all tracked errors (useful for fresh sessions).

---

## 🎮 Backend Configuration Endpoints

### Reload Config from Disk

```bash
POST /config/reload
```

Changes to `.autofixconfig.json` are automatically picked up, but you can force a reload with this endpoint.

### Get Current Config

```bash
GET /config
```

Returns the active configuration being used by the backend.

---

## 🚀 Usage Tips & Best Practices

### Tip 1: Use Diff Preview for Complex Fixes
Always use the preview when fixing large methods → more confident about changes

### Tip 2: Adjust Configuration Per Project
- CI/CD pipelines: Strict mode (`maxErrors: 10`, all severity: "error")
- Learning projects: Permissive mode (focus on critical errors only)
- Performance-sensitive: Aggressive caching (`debounceMs: 1000`)

### Tip 3: Monitor Error Patterns
Use the dashboard and `/stats` endpoint to find recurring issues:
- High % of logic errors? → Add code review process
- Many performance warnings? → Refactoring needed
- High security issues? → Security audit required

### Tip 4: Disable During Pair Programming
Set `enabled: false` in `.autofixconfig.json` to prevent analysis-spam during collaborative sessions

### Tip 5: Share Configs Across Team
Commit `.autofixconfig.json` to version control for consistent error detection across team

---

## ⚠️ Troubleshooting

### Issue: Diff preview looks empty

**Solution**: The diff format might not be rendering correctly. Try clearing cache:
```bash
POST /history/clear
```
Then save the file again.

### Issue: Dashboard not updating

**Solution**: Click the refresh icon, or use:
```
AutoFix: Reload Configuration
```

### Issue: Too many/too few errors appearing

**Solution**: Check `.autofixconfig.json`:
```json
{
  "maxErrors": 5,  // Increase this for more errors
  "ignoreRules": []  // Add error types to ignore
}
```

### Issue: Analysis feels slow

**Solution**: Check configuration for aggressive settings:
```json
{
  "maxErrors": 2,  // Reduce for faster analysis
  "debounceMs": 1000  // Increase debounce time
}
```

---

## 📚 API Reference Summary

### Extension ↔ Backend Communication

| Feature | Endpoint | Method |
|---------|----------|--------|
| **Analyze** | `/analyze` | POST |
| **Fix** | `/fix` | POST |
| **History** | `/history` | GET |
| **Stats** | `/stats` | GET |
| **Config** | `/config` | GET |
| **Reload Config** | `/config/reload` | POST |
| **Clear History** | `/history/clear` | POST |
| **Health Check** | `/health` | GET |

---

## 🔮 Future Enhancements

Planned features for v1.2+:

- ✨ **Batch Fix**: Fix multiple errors at once
- 🌐 **Multiple LLM Providers**: Support OpenAI, Claude, Ollama...
- 🔐 **Security Scanning**: Dedicated security error detection
- 📊 **Team Dashboard**: Web UI for team error analytics
- 🎓 **Learning Mode**: Explanations and documentation links
- 📝 **Export Reports**: CSV/PDF error reports for documentation

---

## 💬 Feedback & Contributions

Have ideas? Found a bug? Contributions welcome!

- GitHub: [Gkbdc01/AutoFix](https://github.com/Gkbdc01/AutoFix)
- Issues: Report bugs and feature requests
- Pull Requests: Community contributions appreciated

---

Happy fixing! 🔧✨
