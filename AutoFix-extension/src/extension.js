const vscode = require('vscode');
const axios = require('axios');

const activate = (context) => {
    console.log('✅ AutoFix Spy Mode Activated!');

    const event = vscode.workspace.onDidSaveTextDocument(
        async (document) => {
            console.log('📂 File Saved:', document.fileName);
            
            // 1. Get the data
            const text = document.getText();
            
            // 2. Package the data
            const payload = {
                language: document.languageId,
                code: text
            };

            // ============================================================
            // 🕵️ SPY CODE STARTS HERE (This is what you asked for)
            // ============================================================
            
            // 1. Visual Popup: Shows you the data on screen
            vscode.window.showInformationMessage(
                `📦 PACKING DATA: Lang=${payload.language}, Length=${payload.code.length} chars`
            );
            
            // 2. Console Log: Prints full JSON to the Debug Console
            console.log("🚀 PAYLOAD READY:", JSON.stringify(payload, null, 2));

            // ============================================================
            // 🕵️ SPY CODE ENDS HERE
            // ============================================================

            try {
                console.log("📡 Attempting to upload to http://localhost:5000/analyze...");
                
                // 3. Attempt Upload
                const response = await axios.post("http://localhost:5000/analyze", payload);
                
                // If server is ON, this runs:
                if (response.status === 200 && response.data.found_bug) {
                    highLightError(document, response.data.line, response.data.message);
                }

            } catch (error) {
                // Fix 1: Actually use the 'error' variable by logging it
                console.error("❌ Upload failed:", error.message);
                
                // 4. Verify Attempt
                // If you see this popup, it means the logic TRIED to send it.
                vscode.window.showWarningMessage("AutoFix: Data packaged successfully, but Server is offline.");
            }
        }
    );

    context.subscriptions.push(event);
}

function highLightError(document, line, message) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const change = vscode.window.createTextEditorDecorationType({
        backgroundColor: 'rgba(255,0,0, 0.3)',
        isWholeLine: true
    });

    if (line < 0) line = 0;
    const range = document.lineAt(line).range;
    editor.setDecorations(change, [range]);
    
    // Fix 2: Actually use the 'message' variable by showing it to the user!
    vscode.window.showErrorMessage(`AutoFix Error (Line ${line + 1}): ${message}`);
}

activate();
// module.exports = { activate };