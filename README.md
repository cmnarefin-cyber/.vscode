# Forensic Intelligence & Investigation Suite

A premium, government-grade forensic dashboard and analysis engine built for high-stakes intelligence and document validation.

## 🚀 Features
- **Forensic Engine**: Multi-stage processing including ingestion, spectral analysis, and global database integration.
- **Investigation Dashboard**: A high-fidelity, real-time web interface for file auditing and intelligence gathering.
- **Global Integration**: Real-time querying against simulated global databases for authentication.
- **System Telemetry**: Embedded hardware status monitoring (CPU/Memory) for secure environments.
- **Premium UI**: Dark-themed, responsive interface designed for C-suite oversight.

## 🛠️ Project Structure
- `investigation_dashboard.py`: Main dashboard server (Port 5002).
- `forensic_engine.py`: Core logic for forensic analysis.
- `integrators.py`: External intelligence database connectors.
- `file_validator.py`: standalone secure file validation tool (Port 5001).
- `github_app_auth.py`: OAuth handler for GitHub App integration (Port 5000).
- `templates/` & `static/`: Frontend assets with rich aesthetics.

## 📋 Setup
1. **Dependencies**: `pip install -r requirements.txt`
2. **Environment**: Copy `.env.example` to `.env` and fill in your GitHub App credentials.
3. **Run**: 
   ```bash
   python investigation_dashboard.py
   ```

## 🔒 Security & Performance
- All local processing.
- Real-time telemetry monitoring.
- Built-in file size and extension validation.
- Secure session handling.
