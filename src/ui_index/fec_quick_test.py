"""Quick FEC test for 3 priority members using urllib (no requests dependency)"""
import urllib.request
import urllib.parse
import json
import time
from pathlib import Path

import os
from dotenv import load_dotenv

load_dotenv()

KEY = os.environ.get("FEC_API_KEY", "")
if not KEY:
    print("⚠️  FEC_API_KEY not found in environment. Set it in .env file or export FEC_API_KEY=your_key")
    print("   Get a key at: https://api.open.fec.gov/developers/")
    KEY = "DEMO_KEY"  # Fallback for limited testing

BASE = "https://api.open.fec.gov/v1"

def call(endpoint, params):
    url = f"{BASE}{endpoint}?api_key={KEY}"
    for k, v in params.items():
        url += f"&{k}={urllib.parse.quote(str(v))}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"  API error: {e}")
        return None

members = [
    {"name": "Chris Van Hollen", "state": "MD", "office": "S", "bioguide": "V000128"},
    {"name": "Mark Warner", "state": "VA", "office": "S", "bioguide": "W000805"},
    {"name": "Don Beyer", "state": "VA", "office": "H", "bioguide": "B001292"},
]

results = []
for m in members:
    print(f"\n🔍 {m['name']} ({m['state']})")
    cand = call("/candidates/search/", {"q": m["name"], "state": m["state"], "office": m["office"], "per_page": 1})
    if not cand or not cand.get("results"):
        print("  ❌ No candidate found")
        continue
    
    result = cand["results"][0]
    cid = result["candidate_id"]
    committees = result.get("principal_committees", [])
    if not committees:
        print("  ❌ No committee")
        continue
    
    comm_id = committees[0]["committee_id"]
    comm_name = committees[0]["name"]
    print(f"  ✅ Candidate: {cid}, Committee: {comm_id} ({comm_name})")
    
    totals = call(f"/committee/{comm_id}/totals/", {"per_page": 1})
    if totals and totals.get("results"):
        t = totals["results"][0]
        receipts = t.get("receipts", 0) or 0
        individual = t.get("individual_contributions", 0) or 0
        pac = t.get("political_party_committee_contributions", 0) or 0
        other = t.get("other_receipts", 0) or 0
        print(f"  💰 Receipts: ${receipts:,.2f}, Individual: ${individual:,.2f}, PAC: ${pac:,.2f}")
        results.append({
            "name": m["name"],
            "state": m["state"],
            "candidate_id": cid,
            "committee_id": comm_id,
            "committee_name": comm_name,
            "total_receipts": receipts,
            "individual_contributions": individual,
            "pac_contributions": pac,
            "other_receipts": other,
        })
    time.sleep(0.5)

out = Path("data/political/fec_quick_results.json")
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\n💾 Saved {len(results)} results to {out}")
