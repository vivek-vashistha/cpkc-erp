import os
import json
from urllib.parse import urlencode
from typing import Any, Dict, Optional, List, Union

import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

BASE_URL = os.getenv("LOGI_API_URL", "").rstrip("/")
API_KEY = os.getenv("LOGI_API_KEY", "")
TIMEOUT = float(os.getenv("LOGI_TIMEOUT", "30"))
DEFAULT_LIMIT = int(os.getenv("LOGI_DEFAULT_LIMIT", "50"))
DEBUG = os.getenv("LOGI_DEBUG", "false").lower() == "true"

if not BASE_URL or not API_KEY:
    raise RuntimeError("Missing LOGI_API_URL or LOGI_API_KEY in .env")

def _request(method: str, path: str,
             params: Optional[Dict[str, Any]] = None,
             json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = dict(params or {})
    params.setdefault("path", path)
    params.setdefault("key", API_KEY)

    url = BASE_URL + "?" + urlencode(params)
    if DEBUG:
        print(f"[LOGI] {method} {url}")
        if json_body:
            print(f"[LOGI] payload: {json.dumps(json_body, indent=2)}")

    response = requests.request(
        method=method.upper(),
        url=BASE_URL,
        params=params,
        json=json_body,
        timeout=TIMEOUT,
        headers={"x-api-key": API_KEY, "Content-Type": "application/json"} if json_body else {"x-api-key": API_KEY},
    )

    try:
        data = response.json()
    except ValueError:
        data = {"raw": response.text}

    if DEBUG:
        preview = json.dumps(data, indent=2)[:500] if isinstance(data, dict) else str(data)[:500]
        print(f"[LOGI] status={response.status_code}, body: {preview}{'...' if len(preview)==500 else ''}")

    response.raise_for_status()
    return data

# Endpoint functions (same clear names, no class)

def ping() -> Dict[str, Any]:
    return _request("GET", "ping")

def get_waybills(*, id: Optional[str] = None, customer_id: Optional[str] = None,
                 status: Optional[str] = None, origin: Optional[str] = None,
                 dest: Optional[str] = None, commodity: Optional[str] = None,
                 since: Optional[str] = None, limit: Optional[int] = None,
                 pageToken: Optional[str] = None) -> Dict[str, Any]:
    params = {k: v for k, v in dict(
        id=id, customer_id=customer_id, status=status, origin=origin,
        dest=dest, commodity=commodity, since=since,
        limit=limit or DEFAULT_LIMIT, pageToken=pageToken
    ).items() if v is not None}
    return _request("GET", "waybills", params=params)

def get_contracts(*, customer_id: Optional[str] = None, origin: Optional[str] = None,
                  dest: Optional[str] = None, commodity: Optional[str] = None) -> Dict[str, Any]:
    params = {k: v for k, v in dict(
        customer_id=customer_id, origin=origin, dest=dest, commodity=commodity
    ).items() if v is not None}
    return _request("GET", "contracts", params=params)

def match_contract(waybill_id: str) -> Dict[str, Any]:
    return _request("GET", "contract/match", params={"waybill_id": waybill_id})

def get_invoices(*, id: Optional[str] = None, status: Optional[str] = None,
                 due_before: Optional[str] = None, customer_id: Optional[str] = None,
                 waybill_id: Optional[str] = None) -> Dict[str, Any]:
    params = {k: v for k, v in dict(
        id=id, status=status, due_before=due_before,
        customer_id=customer_id, waybill_id=waybill_id
    ).items() if v is not None}
    return _request("GET", "invoices", params=params)

def create_invoice(waybill_id: str, currency: str = "CAD") -> Dict[str, Any]:
    return _request("POST", "invoices", json_body={"waybill_id": waybill_id, "currency": currency})

def update_invoice_status(invoice_id: str, status: str) -> Dict[str, Any]:
    return _request("PATCH", "invoices", json_body={"invoice_id": invoice_id, "status": status})

def get_events(waybill_id: str) -> Dict[str, Any]:
    return _request("GET", "events", params={"waybill_id": waybill_id})

def get_customs(waybill_id: str) -> Dict[str, Any]:
    return _request("GET", "customs", params={"waybill_id": waybill_id})

def get_assets_assignments(waybill_id: str) -> Dict[str, Any]:
    return _request("GET", "assets/assignments", params={"waybill_id": waybill_id})

def get_locations(*, code: Optional[str] = None, codes: Optional[List[str]] = None) -> Dict[str, Any]:
    params = {}
    if code:
        params["code"] = code
    if codes:
        params["codes"] = ",".join(codes)
    return _request("GET", "locations", params=params or None)

if __name__ == "__main__":
    print("PING:", ping())
    print("\nWAYBILLS (50):", get_waybills(limit=50))
    print("\nMATCH:", match_contract("WB3005"))
    print("\nCREATE INVOICE:", create_invoice("WB3005", currency="CAD"))
    print("\nINVOICES DUE:", get_invoices(due_before="2025-10-01"))
    # print("PATCH INVOICE:", update_invoice_status("INV123", "Paid"))
    print("\nEVENTS:", get_events("WB3005"))
    print("\nCUSTOMS:", get_customs("WB3005"))
    print("\nASSETS:", get_assets_assignments("WB3005"))

