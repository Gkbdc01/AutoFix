const vscode = require('vscode');
const axios = require('axios');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('AutoFix extension is now active!');

    const errorDecorationType = vscode.window.createTextEditorDecorationType({
        backgroundColor: 'rgba(255, 0, 0, 0.3)',
        isWholeLine: true,
        overviewRulerColor: 'red',
        overviewRulerLane: vscode.OverviewRulerLane.Full,
    });

    // Store last error for fix command
    let lastError = null;

    // Analyze on save
    const onSave = vscode.workspace.onDidSaveTextDocument(async (document) => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document !== document) return;

        editor.setDecorations(errorDecorationType, []);
        lastError = null;

        const code = document.getText();
        const language = document.languageId;

        try {
            const response = await axios.post('http://localhost:5000/analyze', {
                language,
                code,
            });

            const { hasError, line, message } = response.data;

            if (hasError && line) {
                const lineIndex = line - 1;
                const range = new vscode.Range(lineIndex, 0, lineIndex, Number.MAX_SAFE_INTEGER);

                editor.setDecorations(errorDecorationType, [
                    {
                        range,
                        hoverMessage: `⚠️ AutoFix: ${message}`,
                    },
                ]);

                // Store error for fix command
                lastError = { language, code, line, message };

                // Show toast with Fix button
                const action1 = await vscode.window.showWarningMessage(
                    'AutoFix: Error in the file. Would you like to see an explanation of the error?',
                    '📖 Show Explanation'
                );
                if (action1 === '📖 Show Explanation') {
                    action2 = await vscode.window.showInformationMessage(
                        `Explanation: Line ${line} -> ${message}`,
                        '🔧 Fix This'
                    );
                    if (action2 === '🔧 Fix This') {
                        await applyFix(editor, lastError);
                    }
                }
            } else {
                vscode.window.showInformationMessage('AutoFix: No errors found ✅');
            }
        } catch (err) {
            console.error('AutoFix backend error:', err.message);
            vscode.window.showErrorMessage(
                'AutoFix: Backend unreachable — is the server running on port 5000?'
            );
        }
    });

    // Apply fix function
    async function applyFix(editor, errorInfo) {
        try {
            vscode.window.showInformationMessage('AutoFix: Generating fix... ⏳');

            const response = await axios.post('http://localhost:5000/fix', {
                language: errorInfo.language,
                code: errorInfo.code,
                line: errorInfo.line,
                message: errorInfo.message,
            });

            const { fixed, fixedCode, explanation } = response.data;

            if (fixed && fixedCode) {
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
                lastError = null;

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

    context.subscriptions.push(onSave);
    context.subscriptions.push(errorDecorationType);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate,
};