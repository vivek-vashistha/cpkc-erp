import os
import json
from typing import Any, Dict, Optional, List, Union
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv


# ---------- env & session ----------

load_dotenv()

BASE_URL = os.getenv("LOGI_API_URL", "").rstrip("/")
API_KEY  = os.getenv("LOGI_API_KEY", "")
TIMEOUT  = float(os.getenv("LOGI_TIMEOUT", "30"))
DEFAULT_LIMIT = int(os.getenv("LOGI_DEFAULT_LIMIT", "50"))
DEBUG = os.getenv("LOGI_DEBUG", "false").lower() == "true"

if not BASE_URL or not API_KEY:
    raise RuntimeError("Missing LOGI_API_URL or LOGI_API_KEY in .env")

_session: Optional[requests.Session] = None

def _get_session() -> requests.Session:
    """One global session with retries + header."""
    global _session
    if _session is None:
        s = requests.Session()
        retries = Retry(
            total=5, connect=5, read=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PATCH"],
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retries)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        s.headers.update({"x-api-key": API_KEY})
        _session = s
    return _session


def _request(method: str, path: str,
             params: Optional[Dict[str, Any]] = None,
             json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Calls:
      BASE_URL?path=<path>&key=<API_KEY>&...params
    Content-Type JSON only when body is present.
    """
    params = dict(params or {})
    params.setdefault("path", path)
    params.setdefault("key", API_KEY)

    if DEBUG:
        print(f"[LOGI] {method.upper()} {BASE_URL}?{urlencode(params)}")
        if json_body:
            print(f"[LOGI] payload: {json.dumps(json_body, indent=2)}")

    resp = _get_session().request(
        method=method.upper(),
        url=BASE_URL,
        params=params,
        json=json_body,
        timeout=TIMEOUT,
        headers={"Content-Type": "application/json"} if json_body else None
    )

    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text}

    if DEBUG:
        preview = json.dumps(data, indent=2)[:600] if isinstance(data, dict) else str(data)[:600]
        print(f"[LOGI] status={resp.status_code}\n[LOGI] body: {preview}{'...' if len(preview)==600 else ''}")

    if not resp.ok:
        msg = data.get("message") if isinstance(data, dict) else None
        raise requests.HTTPError(f"HTTP {resp.status_code} for {path} ({msg or 'no message'})", response=resp)
    return data


# ---------- endpoint wrappers (functions) ----------

def ping() -> Dict[str, Any]:
    """GET /ping"""
    return _request("GET", "ping")

def get_waybills(*, id: Optional[str] = None, customer_id: Optional[str] = None,
                 status: Optional[str] = None, origin: Optional[str] = None,
                 dest: Optional[str] = None, commodity: Optional[str] = None,
                 since: Optional[str] = None, limit: Optional[int] = None,
                 pageToken: Optional[str] = None) -> Dict[str, Any]:
    """GET /waybills (supports filters and pagination)"""
    params = {k: v for k, v in dict(
        id=id, customer_id=customer_id, status=status, origin=origin, dest=dest,
        commodity=commodity, since=since, limit=limit or DEFAULT_LIMIT, pageToken=pageToken
    ).items() if v is not None}
    return _request("GET", "waybills", params=params)

def get_contracts(*, customer_id: Optional[str] = None, origin: Optional[str] = None,
                  dest: Optional[str] = None, commodity: Optional[str] = None) -> Dict[str, Any]:
    """GET /contracts"""
    params = {k: v for k, v in dict(
        customer_id=customer_id, origin=origin, dest=dest, commodity=commodity
    ).items() if v is not None}
    return _request("GET", "contracts", params=params)

def match_contract(waybill_id: str) -> Dict[str, Any]:
    """GET /contract/match?waybill_id=..."""
    return _request("GET", "contract/match", params={"waybill_id": waybill_id})

def get_invoices(*, id: Optional[str] = None, status: Optional[str] = None,
                 due_before: Optional[str] = None, customer_id: Optional[str] = None,
                 waybill_id: Optional[str] = None) -> Dict[str, Any]:
    """GET /invoices (filters: id, status, due_before, customer_id, waybill_id)"""
    params = {k: v for k, v in dict(
        id=id, status=status, due_before=due_before, customer_id=customer_id, waybill_id=waybill_id
    ).items() if v is not None}
    return _request("GET", "invoices", params=params)

def create_invoice(waybill_id: str, currency: str = "CAD") -> Dict[str, Any]:
    """POST /invoices (auto-match contract)"""
    return _request("POST", "invoices", json_body={"waybill_id": waybill_id, "currency": currency})

def update_invoice_status(invoice_id: str, status: str) -> Dict[str, Any]:
    """PATCH /invoices with {"invoice_id": "...", "status": "..."}"""
    return _request("PATCH", "invoices", json_body={"invoice_id": invoice_id, "status": status})

def get_events(waybill_id: str) -> Dict[str, Any]:
    """GET /events for a waybill"""
    return _request("GET", "events", params={"waybill_id": waybill_id})

def get_customs(waybill_id: str) -> Dict[str, Any]:
    """GET /customs for a waybill"""
    return _request("GET", "customs", params={"waybill_id": waybill_id})

def get_assets_assignments(waybill_id: str) -> Dict[str, Any]:
    """GET /assets/assignments for a waybill"""
    return _request("GET", "assets/assignments", params={"waybill_id": waybill_id})

def get_locations(*, code: Optional[str] = None, codes: Optional[List[str]] = None) -> Dict[str, Any]:
    """GET /locations by single code or list of codes"""
    params: Dict[str, Union[str, List[str]]] = {}
    if code:
        params["code"] = code
    if codes:
        params["codes"] = ",".join(codes)     # CSV for Apps Script querystrings
    return _request("GET", "locations", params=params or None)


if __name__ == "__main__":
    print("PING:", ping())
    print("WAYBILLS (50):", get_waybills(limit=50))
    print("MATCH:", match_contract("WB3005"))
    print("CREATE INVOICE:", create_invoice("WB3005", currency="CAD"))
    print("INVOICES DUE:", get_invoices(due_before="2025-10-01"))
    # print("PATCH INVOICE:", update_invoice_status("INV123", "Paid"))
    print("EVENTS:", get_events("WB3005"))
    print("CUSTOMS:", get_customs("WB3005"))
    print("ASSETS:", get_assets_assignments("WB3005"))
