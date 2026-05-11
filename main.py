from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ICU Transition Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/demo")
async def demo():
    return FileResponse("static/index.html")

# Optional static folder mount
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- CONFIG ---
FHIR_BASE_URL = "https://launch.smarthealthit.org/v/r4/fhir"

from openai import OpenAI

import os

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# --- INPUT MODELS ---
class PatientData(BaseModel):
    patient_id: str
    name: str
    age: int
    diagnosis: str
    medications: list[str]
    labs: dict
    vitals: dict
    icu_days: int

class FHIRRequest(BaseModel):
    fhir_patient_id: str
    icu_days: int = 7

# --- GROQ HELPER ---
async def call_groq(prompt: str) -> str:

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# --- FHIR FETCHER ---
async def fetch_fhir_patient(patient_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        patient_resp = await client.get(f"{FHIR_BASE_URL}/Patient/{patient_id}", headers={"Accept": "application/json"}, timeout=15)
        conditions_resp = await client.get(f"{FHIR_BASE_URL}/Condition?patient={patient_id}", headers={"Accept": "application/json"}, timeout=15)
        meds_resp = await client.get(f"{FHIR_BASE_URL}/MedicationRequest?patient={patient_id}", headers={"Accept": "application/json"}, timeout=15)
        obs_resp = await client.get(f"{FHIR_BASE_URL}/Observation?patient={patient_id}&_count=10", headers={"Accept": "application/json"}, timeout=15)
        return {
            "patient": patient_resp.json(),
            "conditions": conditions_resp.json(),
            "medications": meds_resp.json(),
            "observations": obs_resp.json()
        }

def parse_fhir_to_patient(fhir_data: dict, patient_id: str, icu_days: int) -> PatientData:
    patient = fhir_data["patient"]
    try:
        name_obj = patient["name"][0]
        name = f"{name_obj.get('given', [''])[0]} {name_obj.get('family', '')}"
    except:
        name = "Unknown Patient"
    try:
        birth_year = int(patient["birthDate"][:4])
        age = 2026 - birth_year
    except:
        age = 65
    diagnoses = []
    try:
        for entry in fhir_data["conditions"].get("entry", []):
            code_text = entry["resource"]["code"].get("text", "")
            if code_text:
                diagnoses.append(code_text)
    except:
        pass
    diagnosis = ", ".join(diagnoses[:3]) if diagnoses else "ICU admission - severe illness"
    medications = []
    try:
        for entry in fhir_data["medications"].get("entry", []):
            med_text = entry["resource"]["medicationCodeableConcept"].get("text", "")
            if med_text:
                medications.append(med_text)
    except:
        pass
    if not medications:
        medications = ["See clinical notes"]
    labs = {}
    vitals = {}
    try:
        for entry in fhir_data["observations"].get("entry", []):
            res = entry["resource"]
            code_text = res.get("code", {}).get("text", "")
            value = res.get("valueQuantity", {})
            val_str = f"{value.get('value', '')} {value.get('unit', '')}".strip()
            if val_str and code_text:
                if any(x in code_text.lower() for x in ["pressure", "heart", "oxygen", "temperature", "respiratory"]):
                    vitals[code_text] = val_str
                else:
                    labs[code_text] = val_str
    except:
        pass
    if not labs:
        labs = {"Note": "Labs from FHIR record"}
    if not vitals:
        vitals = {"Note": "Vitals from FHIR record"}
    return PatientData(
        patient_id=patient_id,
        name=name.strip(),
        age=age,
        diagnosis=diagnosis,
        medications=medications[:5],
        labs=labs,
        vitals=vitals,
        icu_days=icu_days
    )

# --- AGENT 1: Clinical Summary ---
async def agent_clinical_summary(patient: PatientData) -> str:
    prompt = f"""You are a clinical summary agent. Based on this ICU patient data, write a concise clinical summary (3-4 sentences) suitable for handoff documentation.
Patient: {patient.name}, Age: {patient.age}
Diagnosis: {patient.diagnosis}
ICU Stay: {patient.icu_days} days
Medications: {', '.join(patient.medications)}
Labs: {patient.labs}
Vitals: {patient.vitals}
Write a professional clinical summary."""
    return await call_groq(prompt)

# --- AGENT 2: Risk Detection ---
async def agent_risk_detection(patient: PatientData) -> str:
    prompt = f"""You are a readmission risk detection agent. Analyze this ICU patient and identify the top 3 readmission risks.
Patient: {patient.name}, Age: {patient.age}
Diagnosis: {patient.diagnosis}
ICU Stay: {patient.icu_days} days
Medications: {', '.join(patient.medications)}
Labs: {patient.labs}
Vitals: {patient.vitals}
List exactly 3 specific risks with a severity level (High/Medium/Low) for each. Be clinical and specific."""
    return await call_groq(prompt)

# --- AGENT 3: Care Coordination ---
async def agent_care_coordination(patient: PatientData) -> str:
    prompt = f"""You are a care coordination agent. Based on this ICU discharge scenario, recommend the follow-up care plan.
Patient: {patient.name}, Age: {patient.age}
Diagnosis: {patient.diagnosis}
ICU Stay: {patient.icu_days} days
Medications: {', '.join(patient.medications)}
Vitals: {patient.vitals}
Recommend:
1. Which specialists need follow-up appointments
2. Any home care or rehab needs
3. Medication adjustments to flag
4. Timeline for follow-ups (within 48hrs / 1 week / 1 month)"""
    return await call_groq(prompt)

# --- AGENT 4: Prior Auth ---
async def agent_prior_auth(patient: PatientData, care_plan: str) -> str:
    prompt = f"""You are a prior authorization agent. Generate a concise insurance justification letter for post-ICU care needs.
Patient: {patient.name}, Age: {patient.age}
Diagnosis: {patient.diagnosis}
ICU Stay: {patient.icu_days} days
Recommended Care Plan: {care_plan}
Write a short, professional prior authorization justification (3-5 sentences) that explains medical necessity."""
    return await call_groq(prompt)

# --- FHIR ENDPOINT ---
# --- FHIR ENDPOINT ---
@app.post("/icu-discharge-fhir")
async def icu_discharge_fhir(request: FHIRRequest):
    try:
        print(f"[FHIR] Fetching patient {request.fhir_patient_id}...")

        fhir_data = await fetch_fhir_patient(request.fhir_patient_id)

        patient = parse_fhir_to_patient(
            fhir_data,
            request.fhir_patient_id,
            request.icu_days
        )

        print(f"[FHIR] Loaded: {patient.name}, {patient.age}y")
        print(patient.model_dump())

        print("[Agent 1] Clinical summary...")
        summary = await agent_clinical_summary(patient)

        print("[Agent 2] Risk detection...")
        risks = await agent_risk_detection(patient)

        print("[Agent 3] Care coordination...")
        care_plan = await agent_care_coordination(patient)

        print("[Agent 4] Prior auth...")
        prior_auth = await agent_prior_auth(patient, care_plan)

        return {
            "fhir_source": f"{FHIR_BASE_URL}/Patient/{request.fhir_patient_id}",
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "patient_age": patient.age,
            "diagnosis": patient.diagnosis,
            "discharge_packet": {
                "clinical_summary": summary,
                "readmission_risks": risks,
                "care_coordination_plan": care_plan,
                "prior_auth_justification": prior_auth
            },
            "status": "ICU Discharge Package Complete — Powered by FHIR + Multi-Agent AI"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# --- MANUAL ENDPOINT ---
@app.post("/icu-discharge")
async def icu_discharge(patient: PatientData):
    try:
        print(f"[Agent 1] Clinical summary for {patient.name}...")
        summary = await agent_clinical_summary(patient)
        print(f"[Agent 2] Risk detection...")
        risks = await agent_risk_detection(patient)
        print(f"[Agent 3] Care coordination...")
        care_plan = await agent_care_coordination(patient)
        print(f"[Agent 4] Prior auth...")
        prior_auth = await agent_prior_auth(patient, care_plan)
        return {
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "discharge_packet": {
                "clinical_summary": summary,
                "readmission_risks": risks,
                "care_coordination_plan": care_plan,
                "prior_auth_justification": prior_auth
            },
            "status": "ICU Discharge Package Complete"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- HEALTH CHECK ---
@app.get("/")
def root():
    return {
        "message": "ICU Transition Agent Running",
        "fhir_server": FHIR_BASE_URL,
        "endpoints": ["/icu-discharge", "/icu-discharge-fhir", "/tools"]
    }

# --- MCP TOOL MANIFEST ---
@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "icu_discharge_coordinator",
                "description": "Coordinates full ICU patient discharge including clinical summary, risk detection, care plan, and prior auth. Supports live FHIR patient data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "diagnosis": {"type": "string"},
                        "medications": {"type": "array", "items": {"type": "string"}},
                        "labs": {"type": "object"},
                        "vitals": {"type": "object"},
                        "icu_days": {"type": "integer"}
                    },
                    "required": ["patient_id", "name", "age", "diagnosis", "medications", "labs", "vitals", "icu_days"]
                }
            },
            {
                "name": "icu_discharge_fhir",
                "description": "Fetches real patient data from FHIR server and runs full ICU discharge coordination",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "fhir_patient_id": {"type": "string"},
                        "icu_days": {"type": "integer"}
                    },
                    "required": ["fhir_patient_id"]
                }
            }
        ]
    }