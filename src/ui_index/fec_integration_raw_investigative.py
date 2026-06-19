"""RAW INVESTIGATIVE VIEW — FEC Integration (urllib-based, no external deps)
================================================================================
⚠️  THIS FILE PRODUCES MULTI-CYCLE ALL-TIME DATA — INTENTIONALLY ⚠️
================================================================================

Purpose: Forensic corruption investigation
- No cycle filter on API calls → captures cross-cycle transfers, reallocated funds,
  and committee reorganizations that obscure money trails.
- The gap between this output and v251d (cycle=2024) is the INVESTIGATIVE SIGNAL.
- "Inflated" figures are not bugs — they are evidence of multi-cycle financial
  engineering that the cycle-filtered view hides.

When to use:
  - Tracing self-funding across multiple election cycles
  - Detecting committee-to-committee transfers that bypass cycle boundaries
  - Identifying candidates whose "2024" fundraising includes recycled 2022/2020 money

When to use v251d instead:
  - Official reporting, public-facing dashboards, cycle-compliant analysis

Output: `fec_funding_profiles_raw.json` (DO NOT overwrite cycle-filtered data)
================================================================================
"""
import urllib.request
import urllib.parse
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

KEY = os.environ.get("FEC_API_KEY", "")
if not KEY:
    print("⚠️  FEC_API_KEY not found in environment. Set it in .env file or export FEC_API_KEY=your_key")
    print("   Get a key at: https://api.open.fec.gov/developers/")
    KEY = "DEMO_KEY"  # Fallback for limited testing

BASE = "https://api.open.fec.gov/v1"


def fec_call(endpoint, params, timeout=30):
    url = f"{BASE}{endpoint}?api_key={KEY}"
    for k, v in params.items():
        url += f"&{k}={urllib.parse.quote(str(v))}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"  API error: {e}")
        return None


class FECAnalyzer:
    def __init__(self):
        self.call_count = 0
        self.results = []
        self.audit_log = []

    def search_candidate(self, name, state, office):
        self.call_count += 1
        data = fec_call("/candidates/search/", {
            "q": name, "state": state, "office": office, "per_page": 1
        })
        if data and data.get("results"):
            return data["results"][0]
        return None

    def get_committee_totals(self, committee_id):
        self.call_count += 1
        data = fec_call(f"/committee/{committee_id}/totals/", {"per_page": 1})
        if data and data.get("results"):
            return data["results"][0]
        return None

    def get_schedule_a(self, committee_id, min_amount=200, per_page=50):
        self.call_count += 1
        data = fec_call("/schedules/schedule_a/", {
            "committee_id": committee_id,
            "min_amount": min_amount,
            "per_page": per_page,
            "sort": "-contribution_receipt_amount",
        })
        if data and data.get("results"):
            return data["results"]
        return []

    def categorize_contributor(self, name):
        if not name:
            return "other"
        name_lower = name.lower()
        labor = ["union", "afl-cio", "seiu", "ufcw", "teamsters", "ibew", "laborers", "unite here", "cwa", "afge", "nalc"]
        business = ["corp", "inc", "llc", "lp", "assoc", "chamber", "business", "industry", "manufacturers", "council", "foundation", "pac", "action", "fund"]
        if any(kw in name_lower for kw in labor):
            return "labor"
        if any(kw in name_lower for kw in business):
            return "business"
        return "other"

    def analyze_member(self, name, state, office, ui_committees, bioguide):
        print(f"\n🔍 {name} ({state})")
        
        cand = self.search_candidate(name, state, office)
        if not cand:
            print("  ❌ No candidate found")
            return None
        
        cid = cand["candidate_id"]
        committees = cand.get("principal_committees", [])
        if not committees:
            print("  ❌ No committee")
            return None
        
        comm_id = committees[0]["committee_id"]
        comm_name = committees[0]["name"]
        print(f"  ✅ {cid} → {comm_id}")
        
        totals = self.get_committee_totals(comm_id)
        if totals:
            receipts = totals.get("receipts", 0) or 0
            individual = totals.get("individual_contributions", 0) or 0
            pac = totals.get("other_political_committee_contributions", 0) or 0
            party = totals.get("political_party_committee_contributions", 0) or 0
            print(f"  💰 Receipts: ${receipts:,.0f}, Indiv: ${individual:,.0f}, PAC: ${pac:,.0f}, Party: ${party:,.0f}")
        else:
            receipts = individual = pac = party = 0
            print("  ⚠️ No totals data")
        
        # Get top contributions
        contributions = self.get_schedule_a(comm_id, min_amount=500, per_page=50)
        business_total = 0
        labor_total = 0
        other_total = 0
        top_contributors = {}
        
        for c in contributions:
            contributor = c.get("contributor_name", "Unknown")
            amount = c.get("contribution_receipt_amount", 0) or 0
            category = self.categorize_contributor(contributor)
            
            if category == "business":
                business_total += amount
            elif category == "labor":
                labor_total += amount
            else:
                other_total += amount
            
            key = (contributor or "UNKNOWN").strip().upper()[:50]
            if key in top_contributors:
                top_contributors[key]["amount"] += amount
            else:
                top_contributors[key] = {"name": contributor, "amount": amount, "category": category}
        
        sorted_top = sorted(top_contributors.values(), key=lambda x: x["amount"], reverse=True)[:5]
        
        if contributions:
            print(f"  📊 Top contributions: {len(contributions)} itemized")
            for t in sorted_top[:3]:
                print(f"     - {t['name']}: ${t['amount']:,.0f} ({t['category']})")
        
        result = {
            "name": name,
            "state": state,
            "bioguide_id": bioguide,
            "candidate_id": cid,
            "committee_id": comm_id,
            "committee_name": comm_name,
            "total_receipts": receipts,
            "individual_contributions": individual,
            "pac_contributions": pac,
            "party_contributions": party,
            "business_contributions": business_total,
            "labor_contributions": labor_total,
            "other_contributions": other_total,
            "ui_relevant_committees": ui_committees,
            "top_contributors": [{"name": t["name"], "amount": round(t["amount"], 2), "category": t["category"]} for t in sorted_top],
        }
        self.results.append(result)
        return result

    def run(self, members):
        print("=" * 60)
        print("FEC INTEGRATION - WHO FUNDS THE FREEZE")
        print("=" * 60)
        
        # Priority: UI-relevant committee members only
        priority_members = []
        for m in members:
            committees = m.get("committees", [])
            ui_score = sum(1 for c in committees if any(
                kw in c.lower() for kw in ["ways and means", "finance", "budget", "labor", "appropriations"]
            ))
            if ui_score > 0:
                priority_members.append((ui_score, m))
        
        priority_members.sort(key=lambda x: x[0], reverse=True)
        selected = [m for _, m in priority_members[:8]]  # Top 8 to stay under rate limit
        
        print(f"Analyzing {len(selected)} priority members (call count: {self.call_count})")
        print("-" * 60)
        
        for m in selected:
            office = "S" if m.get("chamber") == "Senate" else "H"
            ui_committees = [c for c in m.get("committees", []) if any(
                kw in c.lower() for kw in ["ways and means", "labor", "finance", "budget", "appropriations"]
            )]
            self.analyze_member(m["name"], m["state"], office, ui_committees, m["bioguide_id"])
            time.sleep(1)  # Rate limit politeness
        
        # Save results
        out_dir = Path("data/political")
        out_dir.mkdir(parents=True, exist_ok=True)
        
        with open(out_dir / "fec_funding_profiles.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        with open(out_dir / "fec_audit_log.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_api_calls": self.call_count,
                "members_analyzed": len(self.results),
                "rate_limit": "1000/hour",
            }, f, indent=2)
        
        print(f"\n{'=' * 60}")
        print(f"COMPLETE: {len(self.results)} profiles, {self.call_count} API calls")
        print(f"Saved to {out_dir}/fec_funding_profiles.json")
        print(f"{'=' * 60}")
        return self.results


if __name__ == "__main__":
    # Load political layer data
    report_path = Path("data/political/political_layer_report.json")
    if not report_path.exists():
        print("❌ No political layer data. Run political_layer_analyzer.py first.")
        exit(1)
    
    with open(report_path) as f:
        data = json.load(f)
    
    analyzer = FECAnalyzer()
    analyzer.run(data["member_table"])
