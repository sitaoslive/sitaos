"""
Alpha Vision AI Sales OS - GoHighLevel API v2 Client
Official integration client for LeadConnector API v2:
- Pipelines and Opportunities management (18 commercial stages)
- Custom fields provisioning
- Contact synchronization
- Calendar booking webhooks
"""
import urllib.request
import urllib.parse
import json
import logging
from typing import Dict, Any, List, Optional
from engine.config import config

logger = logging.getLogger("AV-GHLClient")

class GHLClient:
    def __init__(self, token: Optional[str] = None, location_id: Optional[str] = None):
        self.token = token or config.GHL_API_KEY
        self.location_id = location_id or config.GHL_LOCATION_ID
        self.base_url = "https://services.leadconnectorhq.com"
        self.version = "2021-07-28"

    @property
    def is_configured(self) -> bool:
        return bool(self.token and not self.token.startswith("your_") and self.location_id and not self.location_id.startswith("your_"))

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Version": self.version,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.is_configured:
            return {"error": "GHL client not configured with live credentials"}

        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"

        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=self._headers(), method=method)

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {"status": resp.status}
        except urllib.error.HTTPError as e:
            raw_err = e.read().decode("utf-8")
            logger.error(f"GHL API Error [{e.code}] on {method} {path}: {raw_err}")
            return {"error": f"HTTP {e.code}", "details": raw_err}
        except Exception as e:
            logger.error(f"GHL Network Error on {method} {path}: {e}")
            return {"error": str(e)}

    # 1. Location & Settings
    def get_location(self) -> Dict[str, Any]:
        return self._request("GET", f"/locations/{self.location_id}")

    # 2. Pipelines
    def list_pipelines(self) -> Dict[str, Any]:
        return self._request("GET", f"/opportunities/pipelines", params={"locationId": self.location_id})

    def create_pipeline(self, name: str, stages: List[str]) -> Dict[str, Any]:
        payload = {
            "name": name,
            "locationId": self.location_id,
            "stages": [{"name": stage} for stage in stages]
        }
        return self._request("POST", "/opportunities/pipelines", data=payload)

    # 3. Custom Fields
    def list_custom_fields(self) -> Dict[str, Any]:
        return self._request("GET", f"/locations/{self.location_id}/customFields")

    def create_custom_field(self, name: str, data_type: str = "TEXT") -> Dict[str, Any]:
        payload = {
            "name": name,
            "dataType": data_type,
            "model": "contact"
        }
        return self._request("POST", f"/locations/{self.location_id}/customFields", data=payload)

    # 4. Contacts & Opportunities
    def upsert_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "locationId": self.location_id,
            **contact_data
        }
        return self._request("POST", "/contacts/upsert", data=payload)

    def search_contacts(self, query: str, limit: int = 10) -> Dict[str, Any]:
        params = {"locationId": self.location_id, "query": query, "limit": limit}
        return self._request("GET", "/contacts/", params=params)

    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/contacts/{contact_id}")

    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"locationId": self.location_id, **contact_data}
        return self._request("POST", "/contacts/", data=payload)

    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._request("PUT", f"/contacts/{contact_id}", data=contact_data)

    def create_opportunity(self, pipeline_id: str, stage_id: str, contact_id: str, title: str, value: float = 0.0) -> Dict[str, Any]:
        payload = {
            "pipelineId": pipeline_id,
            "locationId": self.location_id,
            "contactId": contact_id,
            "name": title,
            "status": "open",
            "pipelineStageId": stage_id,
            "monetaryValue": value
        }
        return self._request("POST", "/opportunities/", data=payload)

ghl_client = GHLClient()
