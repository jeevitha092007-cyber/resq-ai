from dotenv import load_dotenv
load_dotenv()

import json
import time
from google import genai
from google.genai import types

client = genai.Client()

MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.6-flash", "gemini-3.5-flash"]

SYSTEM_PROMPT = """
You are an emergency message analyzer for flood rescue in Bengaluru.
Read one SOS message and return ONLY a JSON object. No extra text.

Fields:
- location_text: the place exactly as mentioned (corrected for typos). null if none.
- location_confidence: "high" (a specific building, junction, bus stand, flyover or other single point, e.g. "Majestic bus stand", "KR Puram flyover"), "medium" (only a road, street or area name with no exact point, e.g. "Whitefield Main Road", "Yelahanka", "Jayanagar"), "low" (vague, like "the temple" or "behind the school"), "none"
- people_count: integer, or null if not mentioned
- situation: one of "trapped", "flooded_house", "flooded_road", "stranded_vehicle", "other"
- medical_details: short text, or null if no medical issue
- needs: list from "rescue", "ambulance", "food", "water", "boat", "shelter", "other"
- urgency: 1 to 5
- languages: list of language codes, e.g. ["en"], ["kn", "en"]
- status: "open" (someone needs help now), "closed" (a flood problem that is now resolved, or help is no longer needed), "not_an_emergency" (unrelated to a flood emergency, such as general questions or spam)

Urgency rules:
5 = life in danger (trapped, injured, medical emergency)
4 = water rising, or children/elderly at risk
3 = safe for now, needs essentials
2 = minor problem
1 = no help needed

Rules:
- NEVER invent a location. If the place is vague, use low confidence.
- If situation is "trapped", needs must include "rescue".
- Always write medical_details in simple English, even if the message is in another language.
- If the message names an area and also a vague landmark (e.g. "Kurubarahalli near the government school"), use the named area as location_text and set location_confidence to "medium".
"""

def analyze_sos(message):
    for attempt in range(4):
        for model_name in MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=message,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        temperature=0,
                    ),
                )
                return json.loads(response.text)
            except Exception as e:
                print(f"{model_name} failed: {str(e)[:100]}")
        time.sleep(3)
    return None

if __name__ == "__main__":
    messages = [
        "Help! 5 people are trapped inside a house near Whitefield Main Road. My father is injured and we need an ambulance.",
        "Water has entered our house near the temple. We are 4 people and need food and drinking water.",
        "plzz help madi 😭 6 ppl stuck near KR Puram flyovr, amma injured, need amblnce fast",
    ]

    for m in messages:
        print("MESSAGE:", m)
        print(json.dumps(analyze_sos(m), indent=2, ensure_ascii=False))
        print("-" * 40)