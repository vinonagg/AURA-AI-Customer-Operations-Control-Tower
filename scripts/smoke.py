import json
import urllib.request

BASE = "http://127.0.0.1:8010"

for path in ["/health", "/ready", "/api/v1/analytics/kpis", "/api/v1/analytics/insights"]:
    with urllib.request.urlopen(BASE + path, timeout=5) as r:
        payload = json.loads(r.read())
        print(path, "OK", json.dumps(payload)[:240])

request = urllib.request.Request(
    BASE + "/api/v1/cases/resolve",
    data=json.dumps({"customer_id":"C10001","message":"My ₹85,000 order was supposed to arrive last week and nobody has helped me."}).encode(),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=30) as r:
    case = json.loads(r.read())
    print("/api/v1/cases/resolve", "OK", case["case_id"], case["action_status"], case["approval_required"])
