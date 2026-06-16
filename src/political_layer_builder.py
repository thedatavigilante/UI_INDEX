import json
from src import DATA, POLITICAL, FIGURES  # repo-root-anchored paths
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from src.api_client import APIClient

load_dotenv()

CONGRESS_GOV_BASE = "https://api.congress.gov/v3"
CENSUS_BASE = "https://api.census.gov/data/2022/acs/acs5"
CENSUS_KEY = os.environ.get("CENSUS_API_KEY", "")
if not CENSUS_KEY:
    print("⚠️  CENSUS_API_KEY not found in environment. Set it in .env file or export CENSUS_API_KEY=your_key")
    print("   Get a key at: https://api.census.gov/data/key_signup.html")
    CENSUS_KEY = "DEMO_KEY"  # Fallback for limited testing

FIPS_MAP = {
    "MD": "24",
    "VA": "51",
    "DC": "11",
}

STATE_NAMES = {
    "24": "Maryland",
    "51": "Virginia",
    "11": "District of Columbia",
}


@dataclass
class MemberRecord:
    bioguide_id: str
    name: str
    state: str
    state_name: str
    district: Optional[int]
    chamber: str
    party: str
    start_year: int
    current: bool
    committees: List[str] = None
    constituent_median_income: Optional[int] = None
    is_nonvoting: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


class PoliticalLayerBuilder:
    """
    Builds the political accountability layer using real API data.
    Self-healing: validates counts, cross-references, audits all calls.
    """

    def __init__(self, cache_dir: Path = None):
        self.client = APIClient(cache_dir=cache_dir)
        self.members: List[MemberRecord] = []
        self.validation_errors: List[str] = []

    def _fetch_members_for_state(self, state_code: str) -> List[Dict]:
        """Fetch all members (House + Senate) for a state."""
        url = f"{CONGRESS_GOV_BASE}/member?api_key=DEMO_KEY&format=json&limit=250&filter=state:{state_code}"
        data = self.client.fetch(url, cache_key=f"members_{state_code}.json")
        if not data or "members" not in data:
            self.validation_errors.append(f"Failed to fetch members for state {state_code}")
            return []
        return data.get("members", [])

    def _fetch_member_details(self, bioguide_id: str) -> Optional[Dict]:
        """Fetch detailed member info including committees."""
        url = f"{CONGRESS_GOV_BASE}/member/{bioguide_id}?api_key=DEMO_KEY&format=json"
        data = self.client.fetch(url, cache_key=f"member_{bioguide_id}.json", cache_ttl_hours=720)
        return data

    def _fetch_census_income(self) -> Dict[str, int]:
        """Fetch median household income by congressional district."""
        states = ",".join(FIPS_MAP.values())
        url = (
            f"{CENSUS_BASE}?get=B19013_001E&for=congressional%20district:*"
            f"&in=state:{states}&key={CENSUS_KEY}"
        )
        data = self.client.fetch(url, cache_key="census_income_2022.json", cache_ttl_hours=720)
        if not data or len(data) < 2:
            self.validation_errors.append("Failed to fetch Census income data")
            return {}

        income_map = {}
        for row in data[1:]:
            income, state_fips, district = row[0], row[1], row[2]
            if income and income.strip():
                key = f"{state_fips}-{district}"
                income_map[key] = int(income)
        return income_map

    def _is_ui_relevant_committee(self, committee_name: str) -> bool:
        """Check if a committee has jurisdiction over UI/SUI policy."""
        ui_keywords = [
            "ways and means", "labor", "education", "workforce",
            "finance", "budget", "appropriations", "social security",
            "employment", "unemployment", "insurance",
        ]
        name_lower = committee_name.lower()
        return any(kw in name_lower for kw in ui_keywords)

    def build(self) -> List[MemberRecord]:
        """
        Full build pipeline with self-healing validation.
        """
        print("🔍 Phase 1: Fetching Census median income data...")
        income_map = self._fetch_census_income()
        print(f"   ✅ Fetched {len(income_map)} district income records")

        print("\n🔍 Phase 2: Fetching member metadata from Congress.gov...")
        all_members = []
        for state_code, fips in FIPS_MAP.items():
            raw_members = self._fetch_members_for_state(fips)
            print(f"   📍 {state_code}: {len(raw_members)} members found")
            for m in raw_members:
                all_members.append((m, fips, state_code))

        print(f"\n🔍 Phase 3: Enriching {len(all_members)} members with committees and income...")
        for idx, (m, fips, state_code) in enumerate(all_members, 1):
            bioguide = m.get("bioguideId", "")
            name = m.get("name", "")
            district = m.get("district")
            chamber = m.get("terms", {}).get("item", [{}])[0].get("chamber", "")
            party = m.get("partyName", "")
            start_year = m.get("terms", {}).get("item", [{}])[0].get("startYear", 0)

            is_nonvoting = (state_code == "DC" and chamber == "House of Representatives")
            chamber_short = "Senate" if "Senate" in chamber else "House"

            committees = []
            details = self._fetch_member_details(bioguide)
            if details and "member" in details:
                committee_data = details["member"].get("committees", {}).get("committee", [])
                for c in committee_data:
                    c_name = c.get("name", "")
                    if c_name:
                        committees.append(c_name)

            district_key = str(district) if district else ""
            income_key = f"{fips}-{district_key}"
            income = income_map.get(income_key)

            if state_code == "DC" and not income:
                income = income_map.get(f"11-98")

            record = MemberRecord(
                bioguide_id=bioguide,
                name=name,
                state=state_code,
                state_name=STATE_NAMES.get(fips, state_code),
                district=district,
                chamber=chamber_short,
                party=party,
                start_year=start_year,
                current=True,
                committees=committees,
                constituent_median_income=income,
                is_nonvoting=is_nonvoting,
            )
            self.members.append(record)
            print(f"   [{idx}/{len(all_members)}] {name} ({state_code}) - {len(committees)} committees")

        print("\n🔍 Phase 4: Validating member counts...")
        md_count = sum(1 for m in self.members if m.state == "MD")
        va_count = sum(1 for m in self.members if m.state == "VA")
        dc_count = sum(1 for m in self.members if m.state == "DC")

        print(f"   MD: {md_count} members (expected: 10 = 8 reps + 2 senators)")
        print(f"   VA: {va_count} members (expected: 13 = 11 reps + 2 senators)")
        print(f"   DC: {dc_count} members (expected: 1 = delegate)")

        if md_count != 10:
            self.validation_errors.append(f"MD count mismatch: got {md_count}, expected 10")
        if va_count != 13:
            self.validation_errors.append(f"VA count mismatch: got {va_count}, expected 13")
        if dc_count != 1:
            self.validation_errors.append(f"DC count mismatch: got {dc_count}, expected 1")

        print("\n🔍 Phase 5: Identifying UI-relevant committee members...")
        ui_members = [m for m in self.members if any(self._is_ui_relevant_committee(c) for c in (m.committees or []))]
        print(f"   {len(ui_members)} members serve on UI-relevant committees")
        for m in ui_members:
            relevant = [c for c in m.committees if self._is_ui_relevant_committee(c)]
            print(f"   - {m.name} ({m.state}): {relevant}")

        return self.members

    def save(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = POLITICAL
        output_dir.mkdir(parents=True, exist_ok=True)

        data = [m.to_dict() for m in self.members]
        with open(output_dir / "members.json", "w") as f:
            json.dump(data, f, indent=2)

        audit_path = self.client.save_audit_log(output_dir / "audit_log.json")
        print(f"\n💾 Saved {len(data)} member records to {output_dir / 'members.json'}")
        print(f"💾 Saved audit log to {audit_path}")

        from datetime import datetime
        summary = {
            "total_members": len(self.members),
            "by_state": {
                "MD": sum(1 for m in self.members if m.state == "MD"),
                "VA": sum(1 for m in self.members if m.state == "VA"),
                "DC": sum(1 for m in self.members if m.state == "DC"),
            },
            "ui_relevant_committee_members": len([m for m in self.members if any(self._is_ui_relevant_committee(c) for c in (m.committees or []))]),
            "validation_errors": self.validation_errors,
            "api_calls": self.client.get_audit_summary(),
            "data_source": {
                "members": "Congress.gov API v3 (DEMO_KEY)",
                "income": "Census ACS 2022 5-Year (B19013_001E)",
                "committees": "Congress.gov member details endpoint",
            },
            "timestamp": datetime.now().isoformat(),
        }
        with open(output_dir / "validation_report.json", "w") as f:
            json.dump(summary, f, indent=2)
        print(f"💾 Saved validation report to {output_dir / 'validation_report.json'}")

        return summary


if __name__ == "__main__":
    from datetime import datetime
    print("=" * 60)
    print("POLITICAL LAYER BUILDER - SELF-HEALING API PIPELINE")
    print("=" * 60)
    print("\nData sources:")
    print("  - Congress.gov API v3 (member list + details)")
    print("  - Census ACS 2022 (median household income by district)")
    print("  - OpenSecrets: NOT AVAILABLE (403 blocked, documented as future)")
    print("\n")

    builder = PoliticalLayerBuilder()
    builder.build()
    summary = builder.save()

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total members: {summary['total_members']}")
    print(f"MD: {summary['by_state']['MD']} | VA: {summary['by_state']['VA']} | DC: {summary['by_state']['DC']}")
    print(f"UI-relevant committee members: {summary['ui_relevant_committee_members']}")
    print(f"API calls: {summary['api_calls']['total_calls']} (success rate: {summary['api_calls']['success_rate']}%)")
    if summary['validation_errors']:
        print(f"⚠️ Validation errors: {len(summary['validation_errors'])}")
        for e in summary['validation_errors']:
            print(f"   - {e}")
    else:
        print("✅ All validation checks passed")
    print("=" * 60)
