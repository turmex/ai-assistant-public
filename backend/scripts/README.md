# Backend Scripts

Utility scripts for the AI Assistant backend.

## generate_ai_snapshot.py

Generates a token-efficient `PROJECT_SNAPSHOT.md` file that provides AI agents with a complete understanding of the project structure in ~900 tokens.

### Features

- **Automatic Scanning**: Analyzes all Python files in the backend directory
- **Smart Extraction**: Identifies purposes, key classes, functions, and dependencies
- **Token Optimization**: Targets 800-1000 tokens for efficient AI context loading
- **Endpoint Detection**: Automatically identifies FastAPI routes
- **AST-Based Analysis**: Uses Python's AST module for accurate code parsing

### Usage

**Manual execution:**
```bash
cd backend
python3 scripts/generate_ai_snapshot.py
```

**Automatic execution:**
The script runs automatically via pre-commit hook whenever backend Python files are modified.

### Output

Creates `PROJECT_SNAPSHOT.md` in the backend directory with:
- Project overview and architecture
- Core file summaries (purpose, classes, functions, dependencies)
- Complete API endpoint list
- Database model descriptions
- Development notes and workflows
- Project statistics

### Token Budget

- Target: 800-1000 tokens
- Current: ~935 tokens
- Warnings shown if outside target range

### Pre-Commit Hook

The script is integrated with Git via `.git/hooks/pre-commit`:
- Runs automatically when committing changes to backend Python files
- Regenerates `PROJECT_SNAPSHOT.md` with latest code structure
- Auto-stages the updated snapshot file

To disable the hook temporarily:
```bash
git commit --no-verify
```

### AI Agent Integration

AI agents can load `PROJECT_SNAPSHOT.md` to instantly understand:
- What each file does
- Available API endpoints
- Database schema
- Code organization
- Key functions and classes

This eliminates the need for agents to read multiple files or ask clarifying questions about project structure.
