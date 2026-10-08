import time
import requests

ALIASES = {
    "kr puram": "Krishnarajapura",
}

GENERIC_WORDS = {"flyover", "bridge", "junction", "circle", "bus", "stand",
                 "stop", "station", "road", "underpass", "signal", "cross"}

CACHE = {}

def search_place(query):
    if query in CACHE:
        return CACHE[query]
    for attempt in range(2):
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query + ", Bengaluru",
                    "format": "json",
                    "limit": 1,
                    "viewbox": "77.45,13.15,77.80,12.80",
                    "bounded": 1,
                },
                headers={"User-Agent": "resq-ai-hackathon"},
                timeout=10,
            )
            data = response.json()
            if data:
                result = {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
                CACHE[query] = result
                return result
            return None
        except Exception as e:
            print("Geocoding failed:", e)
            time.sleep(2)
    return None

def make_candidates(place):
    candidates = []
    if " near " in place:
        candidates.append(place.split(" near ")[0].strip())
    candidates.append(place)
    words = place.split()
    while len(words) > 1 and words[-1] in GENERIC_WORDS:
        words = words[:-1]
    stripped = " ".join(words)
    if stripped not in candidates:
        candidates.append(stripped)
    if stripped in ALIASES:
        candidates.append(ALIASES[stripped])
    return [c for c in candidates if c]

def geocode(location_text, confidence):
    if not location_text or confidence in ("low", "none"):
        return None

    place = location_text.lower().strip()
    for prefix in ("near the ", "near "):
        if place.startswith(prefix):
            place = place[len(prefix):]

    for query in make_candidates(place):
        result = search_place(query)
        if result:
            return result
        time.sleep(1)
    return None