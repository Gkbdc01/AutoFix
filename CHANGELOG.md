# Changelog

All notable changes to AutoFix will be documented in this file.

## [1.1.0] - 2024-03-24

### Added
- **Multi-Error Detection**: Detect up to 5 errors per file instead of just the most critical
- **Error Classification**: Errors now categorized by type (syntax, logic, performance, security) and severity (error, warning, info)
- **Diff Preview**: Side-by-side preview of fixes before applying them with accept/reject UI
- **Smart Caching**: 5-minute TTL caching with MD5 hash to reduce redundant API calls
- **Debouncing**: 500ms debounce prevents analysis spam during rapid saves
- **Error Dashboard**: Sidebar panel showing real-time error statistics and recent errors
- **Custom Configuration**: `.autofixconfig.json` support for severity customization and error filtering
- **Error History**: Backend error tracking with session-based statistics and analytics
- **Error Analytics**: New endpoints: `/history`, `/stats`, `/config`, `/config/reload`, `/history/clear`
- **Diff Generation**: Unified diff format for showing exact changes before/after fixes

### Technical Changes
- **Backend**: Added `error_history.py` and `config_service.py` services
- **Backend**: Updated LLM service to handle multiple errors and generate diffs
- **Backend**: New `dashboard.py` routes for analytics endpoints
- **Frontend**: Implemented caching system with automatic invalidation
- **Frontend**: Added debouncing for repeated analysis requests
- **Frontend**: Multi-error display with color-coded severity levels (red/orange)
- **Frontend**: HTML webview for diff preview with formatted changes
- **Frontend**: Dashboard provider for tree view sidebar

### Configuration
- **Project-level Configuration**: New `.autofixconfig.json` for team-wide settings
- **Severity Customization**: Override error severity per type
- **Rule Filtering**: Ignore specific error types per project
- **Performance Tuning**: Configurable debounce and max errors settings

### Backward Compatibility
- Maintains single-error response format for legacy clients
- Line and message fields still populated for first error
- Existing API contracts preserved

### Performance Improvements
- **Caching**: 5-10x faster repeated analysis on unchanged files
- **Debouncing**: Smooth typing experience with no analysis lag
- **Efficient Filtering**: Config-based rule filtering reduces unnecessary processing

### Documentation
- Comprehensive v1.1 features guide: `FEATURES_v1.1.md`
- Updated README with new features, architecture, and endpoints
- API endpoint documentation with examples
- Configuration guide with example setups

### Known Limitations
- In-memory error history (max 100 errors per session)
- Caching based on file content hash only
- Dashboard updates tied to analysis events
- Configuration reload requires endpoint call

## [1.0.0] - 2024-03-01

### Initial Release
- VS Code extension with error detection on save
- FastAPI backend integration with Azure AI Foundry
- Single error detection and correction
- Toast notifications with explanations
- Rate limiting (30 req/min per IP)
- Multi-language support
- CORS configuration
