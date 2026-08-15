"""
IPWho Python SDK v2.0.0
~~~~~~~~~~~~~~~~~~~~~~~

Enterprise-grade client for the IPWho IP Geolocation API.

Endpoints:
    - lookup(ip)     — geolocation for a specific IPv4/IPv6 address
    - me()           — geolocation for the caller's IP
    - bulk(ips)      — batch lookup for multiple IPs

API docs: https://api.ipwho.org
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import requests

__version__ = "2.0.0"
__all__ = [
    "IPWhoClient",
    "IpGeoResponse",
    "GeoData",
    "GeoLocation",
    "Timezone",
    "Flag",
    "Currency",
    "Connection",
    "Security",
    "UserAgent",
    "Browser",
    "Engine",
    "OS",
    "Device",
    "CPU",
    "ErrorResponse",
    "IPWhoError",
    "InvalidIPError",
    "RateLimitError",
    "APIResponseError",
]

# ═══════════════════════════════════════════════════════════════════════
# Exceptions
# ═══════════════════════════════════════════════════════════════════════


class IPWhoError(Exception):
    """Base exception for IPWho API errors."""


class InvalidIPError(IPWhoError):
    """IP address not found (404)."""


class RateLimitError(IPWhoError):
    """API rate limit exceeded (429)."""


class APIResponseError(IPWhoError):
    """General HTTP error or unexpected response."""


# ═══════════════════════════════════════════════════════════════════════
# Domain models  (mirrors OpenAPI components/schemas)
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class GeoLocation:
    """geoLocation object."""

    continent: Optional[str] = None
    continent_code: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    capital: Optional[str] = None
    region: Optional[str] = None
    region_code: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    dial_code: Optional[str] = None
    is_in_eu: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy_radius: Optional[float] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GeoLocation":
        return cls(
            continent=d.get("continent"),
            continent_code=d.get("continentCode"),
            country=d.get("country"),
            country_code=d.get("countryCode"),
            capital=d.get("capital"),
            region=d.get("region"),
            region_code=d.get("regionCode"),
            city=d.get("city"),
            postal_code=d.get("postal_Code"),
            dial_code=d.get("dial_code"),
            is_in_eu=d.get("is_in_eu"),
            latitude=d.get("latitude"),
            longitude=d.get("longitude"),
            accuracy_radius=d.get("accuracy_radius"),
        )


@dataclass
class Timezone:
    """timezone object."""

    time_zone: Optional[str] = None
    abbr: Optional[str] = None
    offset: Optional[int] = None
    is_dst: Optional[bool] = None
    utc: Optional[str] = None
    current_time: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Timezone":
        return cls(
            time_zone=d.get("time_zone"),
            abbr=d.get("abbr"),
            offset=d.get("offset"),
            is_dst=d.get("is_dst"),
            utc=d.get("utc"),
            current_time=d.get("current_time"),
        )


@dataclass
class Flag:
    """flag object."""

    flag_icon: Optional[str] = None
    flag_unicode: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Flag":
        return cls(
            flag_icon=d.get("flag_Icon"),
            flag_unicode=d.get("flag_unicode"),
        )


@dataclass
class Currency:
    """currency object."""

    code: Optional[str] = None
    symbol: Optional[str] = None
    name: Optional[str] = None
    name_plural: Optional[str] = None
    hex_unicode: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Currency":
        return cls(
            code=d.get("code"),
            symbol=d.get("symbol"),
            name=d.get("name"),
            name_plural=d.get("name_plural"),
            hex_unicode=d.get("hex_unicode"),
        )


@dataclass
class Connection:
    """connection object."""

    asn_number: Optional[int] = None
    asn_org: Optional[str] = None
    isp: Optional[str] = None
    org: Optional[str] = None
    domain: Optional[str] = None
    connection_type: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Connection":
        return cls(
            asn_number=d.get("asn_number"),
            asn_org=d.get("asn_org"),
            isp=d.get("isp"),
            org=d.get("org"),
            domain=d.get("domain"),
            connection_type=d.get("connection_type"),
        )


@dataclass
class Security:
    """security object."""

    is_vpn: Optional[bool] = None
    is_tor: Optional[bool] = None
    is_threat: Optional[str] = None  # "low" | "medium" | "high"

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Security":
        return cls(
            is_vpn=d.get("isVpn"),
            is_tor=d.get("isTor"),
            is_threat=d.get("isThreat"),
        )


@dataclass
class Browser:
    """userAgent > browser."""

    name: Optional[str] = None
    version: Optional[str] = None


@dataclass
class Engine:
    """userAgent > engine."""

    name: Optional[str] = None
    version: Optional[str] = None


@dataclass
class OS:
    """userAgent > os."""

    name: Optional[str] = None
    version: Optional[str] = None


@dataclass
class Device:
    """userAgent > device."""

    type: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None


@dataclass
class CPU:
    """userAgent > cpu."""

    architecture: Optional[str] = None


@dataclass
class UserAgent:
    """userAgent object."""

    browser: Optional[Browser] = None
    engine: Optional[Engine] = None
    os: Optional[OS] = None
    device: Optional[Device] = None
    cpu: Optional[CPU] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "UserAgent":
        return cls(
            browser=Browser(**(d.get("browser") or {})),
            engine=Engine(**(d.get("engine") or {})),
            os=OS(**(d.get("os") or {})),
            device=Device(**(d.get("device") or {})),
            cpu=CPU(**(d.get("cpu") or {})),
        )


@dataclass
class GeoData:
    """The ``data`` payload inside a successful IpGeoResponse."""

    ip: str
    geo_location: Optional[GeoLocation] = None
    timezone: Optional[Timezone] = None
    flag: Optional[Flag] = None
    currency: Optional[Currency] = None
    connection: Optional[Connection] = None
    security: Optional[Security] = None
    user_agent: Optional[UserAgent] = None
    response_array: Optional[List["IpGeoResponse"]] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GeoData":
        return cls(
            ip=d.get("ip", ""),
            geo_location=GeoLocation.from_dict(d["geoLocation"]) if "geoLocation" in d else None,
            timezone=Timezone.from_dict(d["timezone"]) if "timezone" in d else None,
            flag=Flag.from_dict(d["flag"]) if "flag" in d else None,
            currency=Currency.from_dict(d["currency"]) if "currency" in d else None,
            connection=Connection.from_dict(d["connection"]) if "connection" in d else None,
            security=Security.from_dict(d["security"]) if "security" in d else None,
            user_agent=UserAgent.from_dict(d["userAgent"]) if "userAgent" in d else None,
            response_array=(
                [IpGeoResponse.from_dict(item) for item in d["responseArray"]]
                if isinstance(d.get("responseArray"), list)
                else None
            ),
        )


@dataclass
class ErrorResponse:
    """Error payload returned on non-200 responses."""

    success: bool = False
    message: str = ""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ErrorResponse":
        return cls(success=d.get("success", False), message=d.get("message", ""))


@dataclass
class IpGeoResponse:
    """Top-level API response wrapper."""

    success: bool
    data: Optional[GeoData] = None
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "IpGeoResponse":
        return cls(
            success=d.get("success", False),
            data=GeoData.from_dict(d["data"]) if "data" in d and isinstance(d["data"], dict) else None,
            message=d.get("message"),
        )


# ═══════════════════════════════════════════════════════════════════════
# Client
# ═══════════════════════════════════════════════════════════════════════


class IPWhoClient:
    """Client for the IPWho API.

    Usage::

        client = IPWhoClient(api_key="sk.xxxx")
        resp = client.lookup("8.8.8.8")
        print(resp.data.city)

    Args:
        api_key: Your IPWho API key (required).
        base_url: Override the API base URL (default ``https://api.ipwho.org``).
        timeout: HTTP request timeout in seconds (default 30).
    """

    DEFAULT_BASE_URL = "https://api.ipwho.org"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": f"ipwho-python-sdk/{__version__}",
            }
        )

    # ── public API ──────────────────────────────────────────────────

    def lookup(
        self,
        ip: str,
        format: str = "json",
        fields: Optional[str] = None,
    ) -> IpGeoResponse:
        """Look up geolocation for *ip* (IPv4 or IPv6).

        Args:
            ip: The IP address.
            format: ``json``, ``xml``, or ``csv``.  Only ``json`` returns a
                typed ``IpGeoResponse``; other formats return a dict with
                raw string data.
            fields: Comma-separated list of specific fields/objects to
                include (e.g. ``"geoLocation,timezone"``).

        Returns:
            IpGeoResponse
        """
        params = _build_params(self._api_key, format, fields)
        return self._get(f"/ip/{ip}", params, format)

    def me(
        self,
        format: str = "json",
        fields: Optional[str] = None,
    ) -> IpGeoResponse:
        """Look up geolocation for the caller's own IP address.

        Args:
            format: Response format (see ``lookup``).
            fields: Fields filter (see ``lookup``).

        Returns:
            IpGeoResponse
        """
        params = _build_params(self._api_key, format, fields)
        return self._get("/me", params, format)

    def bulk(self, ips: List[str]) -> IpGeoResponse:
        """Batch-lookup multiple IP addresses.

        Args:
            ips: List of IPv4 or IPv6 addresses.

        Returns:
            IpGeoResponse whose ``data`` contains a ``responseArray``
            list of per-IP ``GeoData`` objects.
        """
        if not ips:
            raise ValueError("ips must not be empty")
        bulk_param = ",".join(ips)
        params = {"apiKey": self._api_key}
        return self._get(f"/bulk/{bulk_param}", params, "json")

    # ── internal ────────────────────────────────────────────────────

    def _get(
        self, path: str, params: Dict[str, str], format: str
    ) -> IpGeoResponse:
        url = f"{self._base_url}{path}"
        try:
            resp = self._session.get(url, params=params, timeout=self._timeout)
        except requests.RequestException as exc:
            raise APIResponseError(f"Request failed: {exc}") from exc

        # Rate limit
        if resp.status_code == 429:
            msg = _error_message(resp)
            raise RateLimitError(msg)

        # Not found / bad request
        if resp.status_code == 404:
            msg = _error_message(resp)
            raise InvalidIPError(msg)

        # Other HTTP errors
        if not resp.ok:
            msg = _error_message(resp)
            raise APIResponseError(f"HTTP {resp.status_code}: {msg}")

        # Non-JSON formats: wrap raw text in a lightweight response
        if format != "json":
            return IpGeoResponse(
                success=True,
                data=GeoData(ip=resp.text if format == "csv" else resp.text),
            )

        # JSON success path
        try:
            payload = resp.json()
        except json.JSONDecodeError as exc:
            raise APIResponseError("Invalid JSON response") from exc

        # Even 200s can carry a logical error
        if not payload.get("success", True):
            raise APIResponseError(
                payload.get("message", "API returned success=false")
            )

        # Bulk response: normalise the array
        if "data" in payload and "responseArray" in payload.get("data", {}):
            wrapper = IpGeoResponse.from_dict(payload)
            return wrapper

        return IpGeoResponse.from_dict(payload)


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def _build_params(
    api_key: str, format: str, fields: Optional[str]
) -> Dict[str, str]:
    params: Dict[str, str] = {"apiKey": api_key}
    if format != "json":
        params["format"] = format
    if fields:
        params["get"] = fields
    return params


def _error_message(resp: requests.Response) -> str:
    """Best-effort extraction of an API error message."""
    try:
        body = resp.json()
        return body.get("message", resp.text)
    except json.JSONDecodeError:
        return resp.text or f"HTTP {resp.status_code}"


# ═══════════════════════════════════════════════════════════════════════
# Example
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import os
    import sys

    api_key = os.getenv("IPWHO_API_KEY", "")
    if not api_key or api_key.startswith("sk.xx"):
        print("Set IPWHO_API_KEY to run the example.")
        sys.exit(0)

    client = IPWhoClient(api_key=api_key)

    # Single lookup
    resp = client.lookup("8.8.8.8")
    if resp.data and resp.data.geo_location:
        gl = resp.data.geo_location
        print(f"IP: {resp.data.ip}  |  {gl.city}, {gl.country} "
              f"({gl.latitude}, {gl.longitude})")
    if resp.data and resp.data.currency:
        print(f"Currency: {resp.data.currency.code} "
              f"({resp.data.currency.symbol})")

    # Self lookup
    me = client.me()
    print(f"\nMy IP: {me.data.ip if me.data else 'unknown'}")

    # Bulk
    bulk = client.bulk(["8.8.8.8", "1.1.1.1"])
    if bulk.data:
        print(f"\nBulk: {bulk.success=}")
