# 🏥 ICU Transition Agent
### Interoperable Multi-Agent ICU Discharge Coordination System
**Agents Assemble Hackathon 2026 — Healthcare AI Endgame**

---

## 🚨 The Problem

Every year, 1 in 5 ICU patients is readmitted within 30 days of discharge. Not because medicine failed them — because **coordination** failed them.

When critically ill patients leave the ICU, a cascade of tasks must happen simultaneously:
- Discharge summaries must be written
- Readmission risks must be evaluated
- Specialist follow-ups must be arranged
- Insurance authorizations must be submitted

Today these workflows are **fragmented, manual, and error-prone.** Clinicians burn out. Patients fall through the cracks.

---

## 💡 The Solution

**ICU Transition Agent** is an interoperable multi-agent AI system that coordinates everything needed at ICU discharge — automatically, intelligently, and in seconds.

Input a FHIR patient ID. Four specialized AI agents assemble and collaborate to produce a complete discharge package.

---

## 🤖 The Four Agents

| Agent | Responsibility | Output |
|---|---|---|
| 🔹 **Clinical Summary Agent** | Synthesizes ICU stay from FHIR data | Handoff-ready clinical summary |
| 🔹 **Risk Detection Agent** | Analyzes labs, vitals, diagnoses | Top 3 readmission risks with severity |
| 🔹 **Care Coordination Agent** | Plans post-discharge follow-up | Specialist referrals + timeline |
| 🔹 **Prior Authorization Agent** | Generates insurance justification | Ready-to-submit auth letter |

Each agent passes its findings to the next — creating genuine chain-of-reasoning, not isolated prompts.

---

## 🔗 Interoperability Stack

| Standard | Implementation |
|---|---|
| **FHIR R4** | Live patient data from SMART Health IT sandbox |
| **MCP** | Tool manifest exposed at `/tools` for Prompt Opinion |
| **A2A** | Agent-to-agent context propagation through workflow |
| **Prompt Opinion** | Published to marketplace for ecosystem discovery |

---

## 🏗️ Architecture

```
FHIR R4 Server (SMART Health IT)
          ↓
   Patient Data Fetcher
   (demographics, conditions,
    medications, observations)
          ↓
┌─────────────────────────────────┐
│   ICU Transition Orchestrator   │
│                                 │
│  [Agent 1] Clinical Summary  ──►│
│  [Agent 2] Risk Detection    ──►│
│  [Agent 3] Care Coordination ──►│
│  [Agent 4] Prior Auth           │
└─────────────────────────────────┘
          ↓
  Complete Discharge Packet
  ✅ Summary  ✅ Risks
  ✅ Care Plan ✅ Auth Letter
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Groq API key (console.groq.com — free)

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/icu-transition-agent
cd icu-transition-agent

python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

pip install fastapi uvicorn httpx pydantic groq
```

### Configuration

Open `main.py` and set your API key:
```python
GROQ_API_KEY = "YOUR_GROQ_KEY_HERE"
```

### Run

```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/docs**

---

## 📡 API Endpoints

### `POST /icu-discharge-fhir`
Pulls live patient data from FHIR and runs all 4 agents.

```json
{
  "fhir_patient_id": "a74651a6-8141-4c7e-91b5-a43ce80e6b92",
  "icu_days": 7
}
```

### `POST /icu-discharge`
Manual input for testing with synthetic patient data.

```json
{
  "patient_id": "PT-2024-001",
  "name": "John Matthews",
  "age": 67,
  "diagnosis": "Severe pneumonia with septic shock, now stabilized",
  "medications": ["Metoprolol 25mg", "Lisinopril 10mg", "Furosemide 40mg"],
  "labs": {"WBC": "11.2", "Creatinine": "1.8", "Lactate": "1.4"},
  "vitals": {"HR": "98", "BP": "118/76", "SpO2": "94%"},
  "icu_days": 7
}
```

### `GET /tools`
MCP tool manifest for Prompt Opinion platform integration.

### `GET /`
Health check + endpoint listing.

---

## 📦 Sample Output

```json
{
  "patient_name": "John Matthews",
  "fhir_source": "https://launch.smarthealthit.org/v/r4/fhir/Patient/...",
  "discharge_packet": {
    "clinical_summary": "Mr. Matthews, 67, is being discharged after a 7-day ICU admission for severe pneumonia complicated by septic shock. He has been stabilized with improving oxygenation. Persistent mild tachycardia and elevated creatinine warrant close outpatient monitoring.",
    "readmission_risks": "1. Respiratory decompensation — HIGH\n2. Acute kidney injury recurrence — MEDIUM\n3. Medication non-adherence — MEDIUM",
    "care_coordination_plan": "Within 48hrs: PCP telehealth check-in\nWithin 1 week: Pulmonology + nephrology\nWithin 1 month: Cardiology evaluation",
    "prior_auth_justification": "Prior authorization requested for skilled nursing and pulmonary rehabilitation following 7-day ICU admission for septic shock..."
  },
  "status": "ICU Discharge Package Complete — Powered by FHIR + Multi-Agent AI"
}
```

---

## 🎯 Judging Criteria Alignment

| Criterion | Our Approach |
|---|---|
| **AI Factor** | Genuine multi-agent reasoning — not rule-based logic |
| **Potential Impact** | Targets $26B annual readmission cost in the US |
| **Feasibility** | FHIR-native, no PHI stored, deployable today |

---

## 🛠️ Tech Stack

- **Backend:** Python + FastAPI + Uvicorn
- **AI:** Groq API (LLaMA) — ultra-fast inference
- **FHIR:** SMART Health IT R4 Sandbox
- **Standards:** MCP tool manifest, A2A agent coordination
- **Platform:** Prompt Opinion Marketplace
- **Frontend:** HTML + CSS + JavaScript
- **Libraries:** HTTPX, Pydantic, Groq SDK

---

## 📁 Project Structure

```
icu-transition-agent/
├── main.py              # FastAPI backend + all 4 agents
├── index.html           # Frontend UI
├── style.css            # Styling
├── script.js            # Frontend logic
├── test.py              # Testing utilities
├── extract_ids.py       # FHIR patient ID extractor
├── patient_ids.txt      # 100 real FHIR patient IDs
└── README.md            # This file
```

---

## 🏆 Hackathon

- **Event:** Agents Assemble — Healthcare AI Endgame 2026
- **Track:** MCP Superpower + A2A Agent
- **Platform:** Prompt Opinion
- **Prize Pool:** $25,000

---

*Built in under 24 hours for the Agents Assemble Hackathon 2026*
