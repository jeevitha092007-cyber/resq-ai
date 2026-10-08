from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sos import analyze_sos
from geo import geocode
from db import init_db, save_request, get_all_requests, find_match, merge_into, approve_request

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

class SOSRequest(BaseModel):
    message: str

@app.post("/request")
def create_request(req: SOSRequest):
    result = analyze_sos(req.message)
    if result is None:
        return {"error": "AI unavailable, please try again"}
    coords = geocode(result["location_text"], result["location_confidence"])
    result["coordinates"] = coords

    match_id = None
    if coords and result.get("status") == "open":
        match_id = find_match(coords["lat"], coords["lng"])

    if match_id:
        save_request(req.message, result, duplicate_of=match_id)
        merge_into(match_id, result)
        result["id"] = match_id
        result["merged"] = True
    else:
        result["id"] = save_request(req.message, result)
        result["merged"] = False
    return result

@app.get("/requests")
def list_requests():
    return get_all_requests()

@app.post("/requests/{request_id}/approve")
def approve(request_id: int):
    approve_request(request_id)
    return {"ok": True}

@app.get("/dashboard")
def dashboard():
    return FileResponse("index.html")

@app.get("/sos")
def sos_page():
    return FileResponse("sos.html")