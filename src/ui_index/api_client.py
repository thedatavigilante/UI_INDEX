import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error


class APIClient:
    """
    Self-healing API client with retry, caching, and audit logging.
    """

    def __init__(self, cache_dir: Path = None, max_retries: int = 3, backoff: float = 2.0):
        self.cache_dir = cache_dir or Path(__file__).resolve().parents[2] / "data" / "raw"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.backoff = backoff
        self.audit_log = []

    def _log(self, method: str, url: str, status: int, message: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "url": url,
            "status": status,
            "message": message,
        }
        self.audit_log.append(entry)

    def fetch(self, url: str, cache_key: str = None, cache_ttl_hours: int = 168) -> Optional[Dict]:
        """
        Fetch with self-healing: retry, cache, validate.
        """
        if cache_key is None:
            cache_key = url.replace("/", "_").replace(":", "_")[:100] + ".json"

        cache_path = self.cache_dir / cache_key

        # Check cache
        if cache_path.exists():
            cache_mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - cache_mtime < timedelta(hours=cache_ttl_hours):
                with open(cache_path, "r") as f:
                    self._log("CACHE_HIT", url, 200, f"served from cache ({cache_path})")
                    return json.load(f)

        # Fetch with retry
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "UI-Index-Political-Layer/1.0"})
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    self._log("FETCH_SUCCESS", url, 200, f"attempt {attempt + 1}")
                    # Save to cache
                    with open(cache_path, "w") as f:
                        json.dump(data, f, indent=2)
                    return data
            except urllib.error.HTTPError as e:
                self._log("FETCH_ERROR", url, e.code, f"attempt {attempt + 1}: {e.reason}")
                if e.code == 403:
                    return None  # Blocked, don't retry
                time.sleep(self.backoff * (attempt + 1))
            except Exception as e:
                self._log("FETCH_ERROR", url, 0, f"attempt {attempt + 1}: {str(e)}")
                time.sleep(self.backoff * (attempt + 1))

        return None

    def save_audit_log(self, path: Path = None):
        if path is None:
            path = self.cache_dir / "audit_log.json"
        with open(path, "w") as f:
            json.dump(self.audit_log, f, indent=2)
        return path

    def get_audit_summary(self) -> Dict[str, Any]:
        total = len(self.audit_log)
        successes = sum(1 for e in self.audit_log if e["status"] == 200)
        failures = total - successes
        by_status: Dict[int, int] = {}
        for entry in self.audit_log:
            by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1
        return {
            "total_calls": total,
            "successes": successes,
            "failures": failures,
            "success_rate": round(successes / total * 100, 1) if total > 0 else 0,
            "by_status": dict(sorted(by_status.items())),
        }
