const vscode = require('vscode');
const axios = require('axios');
const crypto = require('crypto');
const DashboardProvider = require('./dashboard');

/**
 * In-memory cache for analysis results
 * Key: hash of file content, Value: { result, timestamp }
 */
const analysisCache = new Map();
const CACHE_TTL_MS = 300000; // 5 minutes

/**
 * Debounce timer for repeated saves
 */
let debounceTimer = null;
const DEBOUNCE_WAIT_MS = 500;

/**
 * Compute hash of file content for caching
 */
function hashCode(content) {
    return crypto.createHash('md5').update(content).digest('hex');
}

/**
 * Check if cached result is still valid
 */
function getCachedAnalysis(codeHash) {
    const cached = analysisCache.get(codeHash);
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL_MS) {
        return cached.result;
    }
    if (cached) analysisCache.delete(codeHash);
    return null;
}

/**
 * Store analysis result in cache
 */
function cacheAnalysis(codeHash, result) {
    analysisCache.set(codeHash, { result, timestamp: Date.now() });
}

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('AutoFix extension is now active!');

    // Register dashboard sidebar
    const dashboardProvider = new DashboardProvider();
    vscode.window.registerTreeDataProvider('autofixDashboard', dashboardProvider);

    const errorDecorationType = vscode.window.createTextEditorDecorationType({
        backgroundColor: 'rgba(255, 0, 0, 0.3)',
        isWholeLine: true,
        overviewRulerColor: 'red',
        overviewRulerLane: vscode.OverviewRulerLane.Full,
    });

    const warningDecorationType = vscode.window.createTextEditorDecorationType({
        backgroundColor: 'rgba(255, 165, 0, 0.2)',
        isWholeLine: true,
        overviewRulerColor: 'orange',
        overviewRulerLane: vscode.OverviewRulerLane.Right,
    });

    // Store last analysis result for fix command
    let lastAnalysisResult = null;
    let lastCode = null;
    let lastLanguage = null;

    // Analyze on save with debouncing
    const onSave = vscode.workspace.onDidSaveTextDocument(async (document) => {
        if (debounceTimer) {
            clearTimeout(debounceTimer);
        }

        debounceTimer = setTimeout(async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor || editor.document !== document) return;

            await performAnalysis(editor, document);
        }, DEBOUNCE_WAIT_MS);
    });

    async function performAnalysis(editor, document) {
        editor.setDecorations(errorDecorationType, []);
        editor.setDecorations(warningDecorationType, []);
        lastAnalysisResult = null;

        const code = document.getText();
        const language = document.languageId;
        const codeHash = hashCode(code);
        const filePath = document.fileName;

        // Check cache first
        const cached = getCachedAnalysis(codeHash);
        if (cached) {
            console.log('Using cached analysis result');
            await displayAnalysisResults(editor, cached, code, language, filePath);
            return;
        }

        try {
            const response = await axios.post('http://localhost:5000/analyze', {
                language,
                code,
                filePath,
            });

            const analysisResult = response.data;
            cacheAnalysis(codeHash, analysisResult);

            lastAnalysisResult = analysisResult;
            lastCode = code;
            lastLanguage = language;

            await displayAnalysisResults(editor, analysisResult, code, language, filePath);
        } catch (err) {
            console.error('AutoFix backend error:', err.message);
            vscode.window.showErrorMessage(
                'AutoFix: Backend unreachable — is the server running on port 5000?'
            );
        }
    }

    async function displayAnalysisResults(editor, result, code, language, filePath) {
        const { hasError, errors = [] } = result;

        if (!hasError || errors.length === 0) {
            vscode.window.showInformationMessage('AutoFix: No errors found ✅');
            dashboardProvider.refresh();
            return;
        }

        // Create decorations for all errors (up to first 5)
        const errorDecorations = [];
        const warningDecorations = [];

        for (const error of errors.slice(0, 5)) {
            const lineIndex = error.line - 1;
            const range = new vscode.Range(lineIndex, 0, lineIndex, Number.MAX_SAFE_INTEGER);
            const decoration = {
                range,
                hoverMessage: `⚠️ ${error.severity.toUpperCase()}: ${error.message}`,
            };

            if (error.severity === 'warning') {
                warningDecorations.push(decoration);
            } else {
                errorDecorations.push(decoration);
            }
        }

        editor.setDecorations(errorDecorationType, errorDecorations);
        editor.setDecorations(warningDecorationType, warningDecorations);

        // Refresh dashboard
        dashboardProvider.refresh();

        // Show first error in toast
        const firstError = errors[0];
        const errorCount = errors.length;
        const message = errorCount > 1 
            ? `AutoFix: Found ${errorCount} errors. First error on line ${firstError.line}: ${firstError.message}`
            : `AutoFix: Error on line ${firstError.line}: ${firstError.message}`;

        const action1 = await vscode.window.showWarningMessage(
            message,
            '📖 Show Explanation'
        );

        if (action1 === '📖 Show Explanation') {
            const action2 = await vscode.window.showInformationMessage(
                `Line ${firstError.line} → ${firstError.message}`,
                '🔧 Fix This',
                '📊 Show All'
            );
            
            if (action2 === '🔧 Fix This') {
                await applyFix(editor, firstError, code, language, filePath);
            } else if (action2 === '📊 Show All') {
                showAllErrors(errors);
            }
        }
    }

    async function applyFix(editor, errorInfo, code, language, filePath) {
        try {
            vscode.window.showInformationMessage('AutoFix: Generating fix... ⏳');

            const response = await axios.post('http://localhost:5000/fix', {
                language,
                code,
                line: errorInfo.line,
                message: errorInfo.message,
                filePath,
            });

            console.log('Fix response:', response.data);
            const { fixed, fixedCode, explanation, diff } = response.data;
            console.log('Extracted diff:', diff);

            if (fixed && fixedCode) {
                // Show diff preview in a side-by-side comparison
                const diffPreview = await showDiffPreview(code, fixedCode, diff);
                if (!diffPreview) {
                    return; // User cancelled
                }

                // Unescape literal \n, \t, \r from LLM response
                const cleanedCode = fixedCode
                    .replace(/\\n/g, '\n')
                    .replace(/\\t/g, '\t')
                    .replace(/\\r/g, '\r');

                const fullRange = new vscode.Range(
                    0, 0,
                    editor.document.lineCount - 1,
                    editor.document.lineAt(editor.document.lineCount - 1).text.length
                );

                await editor.edit((editBuilder) => {
                    editBuilder.replace(fullRange, cleanedCode);
                });

                editor.setDecorations(errorDecorationType, []);
                editor.setDecorations(warningDecorationType, []);

                vscode.window.showInformationMessage(
                    `AutoFix: Fixed! — ${explanation || 'Error resolved'} ✅`
                );

                // Auto-save to trigger re-analysis
                await editor.document.save();
            } else {
                vscode.window.showWarningMessage('AutoFix: Could not generate a fix.');
            }
        } catch (err) {
            console.error('AutoFix fix error:', err.message);
            vscode.window.showErrorMessage('AutoFix: Fix request failed.');
        }
    }

    async function showDiffPreview(original, fixed, diff) {
    const panel = vscode.window.createWebviewPanel(
        'autofixDiff',
        'AutoFix Diff Preview',
        vscode.ViewColumn.Beside,
        { 
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    panel.webview.html = getWebviewContent(original, fixed, diff);

    return new Promise((resolve) => {
        let resolved = false;
        
        const messageHandler = panel.webview.onDidReceiveMessage((message) => {
            console.log('Message received:', message);
            if (!resolved) {
                resolved = true;
                panel.dispose();
                messageHandler.dispose();
                resolve(message.command === 'accept');
            }
        });

        // Handle panel closure without button click
        const disposeHandler = panel.onDidDispose(() => {
            if (!resolved) {
                resolved = true;
                messageHandler.dispose();
                disposeHandler.dispose();
                resolve(false);
            }
        });
    });
}

    function getWebviewContent(original, fixed, diff) {
    // Escape the diff properly for JSON
    const diffJson = JSON.stringify(diff || '');
    
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { margin-bottom: 20px; font-size: 18px; }
        .debug-section { background: #2d2d30; padding: 10px; margin: 10px 0; border-radius: 4px; font-size: 12px; }
        .diff-container { 
            background: #252526; 
            border: 1px solid #3e3e42; 
            border-radius: 4px; 
            padding: 15px; 
            margin-bottom: 20px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            line-height: 1.5;
            max-height: 400px;
            overflow-y: auto;
            min-height: 100px;
        }
        .remove { color: #f48771; background: #3f2f2f; display: block; }
        .add { color: #89d185; background: #2f3f2f; display: block; }
        .neutral { display: block; }
        .buttons { display: flex; gap: 10px; margin-top: 20px; }
        button { 
            padding: 10px 20px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 14px;
            font-weight: bold;
        }
        .accept { background: #007c27; color: white; }
        .reject { background: #c72c0d; color: white; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Review Fix Changes</h1>
        <div class="debug-section" id="debugInfo">Loading...</div>
        <div class="diff-container" id="diffView">Preparing diff preview...</div>
        <div class="buttons">
            <button class="accept" onclick="acceptFix()">✅ Accept & Apply</button>
            <button class="reject" onclick="rejectFix()">❌ Reject</button>
        </div>
    </div>
    <script>
        const vscode = acquireVsCodeApi();
        
        function acceptFix() {
            console.log('Accept clicked');
            vscode.postMessage({ command: 'accept' });
        }
        
        function rejectFix() {
            console.log('Reject clicked');
            vscode.postMessage({ command: 'reject' });
        }

        function formatDiff(diffText) {
            console.log('formatDiff called with:', typeof diffText, diffText ? diffText.length : 'null');
            
            if (!diffText || diffText.trim() === '') {
                return '<p style="color: #999;">No diff available</p>';
            }
            
            const lines = diffText.split('\\n');
            console.log('Split into', lines.length, 'lines');
            
            return lines.map(line => {
                if (line.startsWith('-') && !line.startsWith('---')) {
                    return '<div class="remove">' + escapeHtml(line) + '</div>';
                } else if (line.startsWith('+') && !line.startsWith('+++')) {
                    return '<div class="add">' + escapeHtml(line) + '</div>';
                }
                return '<div class="neutral">' + escapeHtml(line) + '</div>';
            }).join('');
        }

        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        // Main execution
        try {
            const diff = ${diffJson};
            console.log('Diff value:', diff);
            console.log('Diff type:', typeof diff);
            console.log('Diff length:', diff ? diff.length : 'null/undefined');
            
            let debugHtml = '<strong>✓ Webview loaded successfully</strong><br>';
            debugHtml += 'Diff length: ' + (diff ? diff.length : 0) + ' chars<br>';
            debugHtml += 'Diff type: ' + typeof diff;
            
            document.getElementById('debugInfo').innerHTML = debugHtml;
            
            if (diff && diff.length > 0) {
                console.log('Formatting diff...');
                const formatted = formatDiff(diff);
                document.getElementById('diffView').innerHTML = formatted;
                console.log('Diff formatted successfully');
            } else {
                document.getElementById('diffView').innerHTML = '<p style="color: #999; padding: 20px;">No diff data received from backend</p>';
            }
        } catch (error) {
            console.error('Error in webview:', error);
            document.getElementById('diffView').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            document.getElementById('debugInfo').innerHTML = '<strong style="color: red;">✗ Error in webview</strong><br>' + error.message;
        }
    </script>
</body>
</html>
    `;
}

    function showAllErrors(errors) {
        const items = errors.slice(0, 10).map((e, i) => ({
            label: `Line ${e.line}: ${e.severity.toUpperCase()}`,
            description: e.message,
            detail: `Type: ${e.errorType}`,
        }));

        vscode.window.showQuickPick(items, {
            title: `Found ${errors.length} errors`,
        });
    }

    context.subscriptions.push(onSave);
    context.subscriptions.push(errorDecorationType);
    context.subscriptions.push(warningDecorationType);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate,
};