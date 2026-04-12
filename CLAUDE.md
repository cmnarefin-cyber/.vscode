# Claude Code Project Memory

## Project Overview
This project is a workspace for building and testing GitHub integrations and secure tools. It currently includes a file validation application and a GitHub App authentication handler.

## Tech Stack
- **Framework**: Flask (Python)
- **Frontend**: HTML5, Vanilla CSS (Premium Dark Mode)
- **Tools**: GitHub CLI (`gh`), Claude Code Extension

## Commands
- **Run File Validator**: `python file_validator.py` (Server on http://localhost:5001)
- **Run Auth Handler**: `python github_app_auth.py` (Server on http://localhost:5000)

## Project Structure
- `file_validator.py`: Main entry point for the secure file upload tool.
- `github_app_auth.py`: OAuth handler for GitHub App authentication.
- `static/`: Frontend assets (CSS).
- `templates/`: HTML templates.
- `docs/setup.md`: Setup guide for Claude Code Action.
- `.github/workflows/claude.yml`: CI/CD workflow for Claude Code.

## Development Rules
- Always use **Premium Aesthetics** for web interfaces.
- Ensure all file uploads are validated via extension and size (2MB limit).
- Keep secrets safe and use GitHub Secrets for Actions.
