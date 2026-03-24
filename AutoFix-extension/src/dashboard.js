/**
 * Dashboard sidebar panel for viewing error history and statistics
 */
const vscode = require('vscode');

class DashboardProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.stats = null;
        this.history = [];
    }

    getTreeItem(element) {
        return element;
    }

    async getChildren(element) {
        if (!element) {
            return this.getRootItems();
        }
        return [];
    }

    async getRootItems() {
        const items = [];

        // Stats section
        const statsItem = new vscode.TreeItem('📊 Error Statistics');
        statsItem.collapsibleState = vscode.TreeItemCollapsibleState.Expanded;
        items.push(statsItem);

        try {
            const response = await require('axios').get('http://localhost:5000/stats');
            this.stats = response.data;

            if (this.stats && this.stats.totalErrors > 0) {
                const totalItem = new vscode.TreeItem(
                    `Total Errors: ${this.stats.totalErrors}`
                );
                totalItem.iconPath = new vscode.ThemeIcon('issues');
                items.push(totalItem);

                if (this.stats.mostCommonFile) {
                    const fileItem = new vscode.TreeItem(
                        `Most errors in: ${this.stats.mostCommonFile.split('/').pop()}`
                    );
                    fileItem.iconPath = new vscode.ThemeIcon('file');
                    items.push(fileItem);
                }
            }
        } catch (err) {
            console.log('Could not fetch stats:', err.message);
        }

        return items;
    }

    refresh() {
        this._onDidChangeTreeData.fire();
    }
}

module.exports = DashboardProvider;
