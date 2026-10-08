import time
from sos import analyze_sos

# Each test: a message and the answer key (what the correct output should be).
# Leave a field out of "expect" if you don't want to check it.
TESTS = [
    {
        "message": "Help! 5 people are trapped inside a house near Whitefield Main Road. My father is injured and we need an ambulance.",
        "expect": {"location_confidence": "medium", "people_count": 5, "situation": "trapped",
                   "urgency": 5, "needs": ["rescue", "ambulance"], "status": "open"},
    },
    {
        "message": "Water has entered our house near the temple. We are 4 people and need food and drinking water.",
        "expect": {"location_confidence": "low", "people_count": 4, "situation": "flooded_house",
                   "urgency": 3, "needs": ["food", "water"], "status": "open"},
    },
    {
        "message": "plzz help madi 😭 6 ppl stuck near KR Puram flyovr, amma injured, need amblnce fast",
        "expect": {"location_confidence": "high", "people_count": 6, "situation": "trapped",
                   "urgency": 5, "needs": ["rescue", "ambulance"], "status": "open"},
    },
    {
        "message": "Flood near Majestic bus stand, 3 people stuck, need boat",
        "expect": {"location_confidence": "high", "people_count": 3, "situation": "trapped",
                   "urgency": 5, "needs": ["rescue", "boat"], "status": "open"},
    },
    {
        "message": "Help us, we are stranded.",
        "expect": {"location_confidence": "none", "status": "open"},
    },
    {
        "message": "Everything is fine now, the water has gone down. No help required.",
        "expect": {"urgency": 1, "status": "closed"},
    },
    {
        "message": "Is the cricket match cancelled today?",
        "expect": {"status": "not_an_emergency"},
    },
    {
        "message": "Flooded road near the bus stand, nobody is trapped.",
        "expect": {"situation": "flooded_road", "status": "open"},
    },
        {
        "message": "5 ppl risky under water in kurubarahalli near government school road",
        "expect": {"location_confidence": "medium", "people_count": 5, "status": "open"},
    },
]

def check(result, expect):
    problems = []
    for field in ("location_confidence", "people_count", "situation", "status"):
        if field in expect and result.get(field) != expect[field]:
            problems.append(f"{field}: expected {expect[field]}, got {result.get(field)}")
    if "urgency" in expect:
        got = result.get("urgency") or 0
        if abs(got - expect["urgency"]) > 1:
            problems.append(f"urgency: expected {expect['urgency']}, got {got}")
    if "needs" in expect:
        got_needs = result.get("needs") or []
        missing = [n for n in expect["needs"] if n not in got_needs]
        if missing:
            problems.append(f"needs missing: {missing}")
    return problems

passed = 0
for i, test in enumerate(TESTS, start=1):
    result = analyze_sos(test["message"])
    if result is None:
        print(f"#{i} SKIPPED (AI unavailable): {test['message'][:50]}")
        continue
    problems = check(result, test["expect"])
    if problems:
        print(f"#{i} FAIL: {test['message'][:50]}")
        for p in problems:
            print("     -", p)
    else:
        passed += 1
        print(f"#{i} PASS: {test['message'][:50]}")
    time.sleep(3)

print(f"\nScore: {passed} of {len(TESTS)} correct ({round(100 * passed / len(TESTS))}%)")