# ResQ-AI

AI-powered flood emergency triage for Bengaluru. A person in danger sends an SOS message in any language; ResQ-AI turns it into structured data and a map pin for emergency coordinators, who verify each incident.

Built for the Horizon AI Hackathon, problem statement: **AI for Disaster Response**.

> All data in this demo is simulated. In a real emergency in India, call 112.

## How it works
1. A person submits an SOS on the victim page (`/sos`).
2. An LLM extracts location, number of people, needs, urgency and language, and writes it as structured JSON.
3. The location is geocoded to map coordinates. Vague locations (e.g. "near the temple") are flagged for follow-up and are never guessed.
4. Reports within 300 m and 24 h are merged into one incident.
5. Coordinators see incidents on a live map (`/dashboard`) and verify each one before action.

## Third-party technologies
- Google Gemini API (extraction / AI)
- OpenStreetMap Nominatim (geocoding) and Leaflet (maps)
- FastAPI, Uvicorn, SQLite, Python

## Run it locally
1. Install Python 3.10 or newer.
2. `python -m pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your own free key from aistudio.google.com
4. `python -m uvicorn main:app --reload`
5. Open `http://127.0.0.1:8000/dashboard` (coordinator) and `http://127.0.0.1:8000/sos` (victim)

## Tests
`python tests.py` runs the extraction test set and prints an accuracy score.

## Limitations
- Locations are area-level, not exact.
- The prototype needs internet; SMS/WhatsApp intake and coordinator login are future work.
- Free-tier services (Gemini, Nominatim) have usage limits.
