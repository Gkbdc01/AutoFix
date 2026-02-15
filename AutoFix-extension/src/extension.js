const vscode = require('vscode');
const axios = require('axios');

const activate = (context) => {
	console.log('AutoFix is activated !');
	const event = vscode.workspace.onDidSaveTextDocument(
	async (document) =>  {
		console.log('Document saved :',document.fileName);
		const text = document.getText();
		try{
			const response = await axios.post("http://localhost:5000/analyze", {
				language : document.languageId,
				code : text
			});
			if(response.status === 200 && response.data.hasError){
				highLightError(document,response.data.line,response.data.message);
			}
			console.log("Response from the server:", response.data);
		}
		catch(error){
			console.error("Error while sending request to the server:", error);
		}
	}
);
	context.subscriptions.push(event);
}

function highLightError(document,line,message){
	const editor = vscode.window.activeTextEditor;
	if(!editor){
		console.log("can not load the editor");
		return;
	}
	const change = vscode.window.createTextEditorDecorationType({
		backgroundColor: 'rgba(255,0,0, 0.3)',
		isWholeLine : true
	}
	)
	const range = new vscode.Range(line-1,0,line-1,document.lineAt(line-1).text.length);
	editor.setDecorations(change,[range]);
	vscode.window.showErrorMessage(`Error at line ${line} : ${message}`);
}

module.exports = {activate};