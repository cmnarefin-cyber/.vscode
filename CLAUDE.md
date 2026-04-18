# Claude Code Project Memory

## Project Overview
This workspace is dedicated to the **Forensic Intelligence & Investigation Suite**. It provides high-stakes document forensic analysis and global intelligence integration tools.

## Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5, Vanilla CSS (Premium Dark Theme)
- **Monitoring**: PowerShell-based hardware telemetry
- **Integration**: GitHub OAuth, Remote Intel APIs

## Commands
- **Run Forensic Dashboard**: `python investigation_dashboard.py` (Server on http://localhost:5002)
- **Run File Validator**: `python file_validator.py` (Server on http://localhost:5001)
- **Run Auth Gateway**: `python github_app_auth.py` (Server on http://localhost:5000)

## Project Structure
- `investigation_dashboard.py`: Enterprise oversight dashboard.
- `forensic_engine.py`: Multi-stage forensic processing engine.
- `integrators.py`: Intelligence database interface.
- `file_validator.py`: standalone document verification module.
- `github_app_auth.py`: GitHub OAuth integration handler.
- `static/forensic.css`: Core design system for premium UI.
- `templates/forensic.html`: Main dashboard template.

## Development Guidelines
- **Aesthetics**: Maintain the "Senior Government Intelligence" visual style (Glassmorphism, Dark Mode).
- **Architecture**: Keep forensic logic modular (`forensic_engine.py`) and decoupled from the Flask UI.
- **Security**: Validate all inputs; use `.env` for all sensitive credentials.
- **Performance**: Monitor CPU/Memory load during heavy document analysis via the `telemetry` module.
