# ALPHA VISION AUTONOMOUS REVENUE OS — PRODUCTION RUNBOOK
**System:** Alpha Vision Autonomous Revenue OS  
**Environment:** Production / Google Antigravity  

---

## 1. STARTING THE PLATFORM
To start the Executive Command Center and all API endpoints:
```powershell
python server.py
```
- Web Application: `http://localhost:8000`
- WhatsApp Integration Center: `http://localhost:8000/whatsapp`
- System Health Check: `http://localhost:8000/api/v1/health`
- WhatsApp Telemetry: `http://localhost:8000/api/whatsapp/status`

---

## 2. EXECUTING TEST SUITES
To run the complete automated test suite across all engines:
```powershell
python -m pytest tests/ -v
```

---

## 3. RUNNING THE AUTONOMOUS SIMULATION
To execute a synthetic end-to-end commercial journey:
```powershell
python scratch/test_e2e_unified_journey.py
```

---

## 4. EMERGENCY CONTROLS
- **Emergency Kill-Switch:** Toggle `KILL_SWITCH_ACTIVE = True` in `.env` or click "Pause Operations" in the Command Center. Immediately halts all outbound messaging and payments.
- **Human Takeover:** Tag any contact in GHL with `avm_human_takeover`. AI auto-responses are instantly locked.
