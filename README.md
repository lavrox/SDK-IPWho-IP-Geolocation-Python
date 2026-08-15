# IPWho ([ipwho.org](https://www.ipwho.org)) Python SDK

[![PyPI version](https://img.shields.io/pypi/v/ipwho-ip-geolocation-api?style=flat-square)](https://pypi.org/project/ipwho-ip-geolocation-api/) [![Python version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![license](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/lavrox/SDK-IPWho-Python/blob/main/LICENSE)

Official Python SDK for the [IPWho](https://www.ipwho.org) **IP geolocation API** — geoip lookup, IP location, IP to country / latitude / longitude, ASN/ISP, timezone, currency, flag, and proxy/VPN detection with typed responses. Works as an IP lookup / ip-geolocation client for IPv4 and IPv6 (`lookup`, `me`, `bulk`).

- Product: [ipwho.org](https://www.ipwho.org)
- API docs: [ipwho.org/docs](https://www.ipwho.org/docs)
- Get an API key: [ipwho.org/free-plan](https://www.ipwho.org/free-plan) (free [Lavrox](https://lavrox.com) account)
- Live API host: `https://api.ipwho.org`

## API key

Open a free [Lavrox](https://lavrox.com) account to get an API key for [IPWho](https://www.ipwho.org). Create your key at [ipwho.org/free-plan](https://www.ipwho.org/free-plan) — no credit card required.

## Installation

```bash
pip install ipwho-ip-geolocation-api
```

From source:

```bash
git clone https://github.com/lavrox/SDK-IPWho-Python.git
cd SDK-IPWho-Python
pip install -e .
```

Requires Python 3.8+ and `requests`.

## Quick Start

```python
import os
from ipwho import IPWhoClient

client = IPWhoClient(api_key=os.environ["IPWHO_API_KEY"])

resp = client.lookup("8.8.8.8")          # GET /ip/{ip}
me = client.me()                         # GET /me
bulk = client.bulk(["8.8.8.8", "1.1.1.1"])  # GET /bulk/{a,b,c}
```

Every successful JSON call returns an `IpGeoResponse`:

```
IpGeoResponse
├── success: bool
├── message: str | None          # errors only
└── data: GeoData
    ├── ip: str
    ├── geo_location: GeoLocation
    ├── timezone: Timezone
    ├── flag: Flag
    ├── currency: Currency
    ├── connection: Connection
    ├── security: Security
    ├── user_agent: UserAgent    # often present on /me
    └── response_array: list     # bulk only
```

## Reading the full response (8.8.8.8)

Values below match the live [IPWho](https://www.ipwho.org) API (Google DNS: United States, ASN 15169, timezone America/Chicago, dial code +1). Nested objects can be `None` for some IPs — always check.

```python
resp = client.lookup("8.8.8.8")
assert resp.success
data = resp.data

print(data.ip)  # "8.8.8.8"

geo = data.geo_location
print(geo.continent)         # e.g. "North America"
print(geo.continent_code)    # "NA"
print(geo.country)           # "United States"
print(geo.country_code)      # "US"
print(geo.capital)
print(geo.region)
print(geo.region_code)
print(geo.city)
print(geo.postal_code)
print(geo.dial_code)         # "+1"
print(geo.is_in_eu)          # False
print(geo.latitude, geo.longitude)
print(geo.accuracy_radius)   # e.g. 1000

tz = data.timezone
print(tz.time_zone)          # "America/Chicago"
print(tz.abbr, tz.offset, tz.is_dst, tz.utc, tz.current_time)

flag = data.flag
print(flag.flag_icon)        # "🇺🇸"
print(flag.flag_unicode)     # "U+1F1FA U+1F1F8"

cur = data.currency
print(cur.code, cur.symbol, cur.name)
print(cur.name_plural)       # "US dollars"
print(cur.hex_unicode)

conn = data.connection
print(conn.asn_number)       # 15169
print(conn.asn_org)          # "Google LLC"
print(conn.isp, conn.org, conn.domain)
print(conn.connection_type)  # "Corporate"

sec = data.security
print(sec.is_vpn, sec.is_tor, sec.is_threat)  # threat: "low" | "medium" | "high"

if data.user_agent:
    print(data.user_agent.browser.name, data.user_agent.os.name)
    print(data.user_agent.device.type, data.user_agent.cpu.architecture)

me = client.me()
print(me.data.ip)  # the caller's public IP

bulk = client.bulk(["8.8.8.8", "1.1.1.1"])
for item in bulk.data.response_array or []:
    print(item.data.ip, item.data.geo_location.country)
```

### Example JSON (mapped fields)

What `lookup("8.8.8.8")` looks like after the SDK maps the wire payload:

```json
{
  "success": true,
  "data": {
    "ip": "8.8.8.8",
    "geo_location": {
      "continent": "North America",
      "continent_code": "NA",
      "country": "United States",
      "country_code": "US",
      "capital": "Washington",
      "region": "California",
      "region_code": "CA",
      "city": null,
      "postal_code": null,
      "dial_code": "+1",
      "is_in_eu": false,
      "latitude": 37.751,
      "longitude": -97.822,
      "accuracy_radius": 1000
    },
    "timezone": {
      "time_zone": "America/Chicago",
      "abbr": "CDT",
      "offset": -18000,
      "is_dst": true,
      "utc": "UTC-05:00",
      "current_time": "2026-08-07T12:00:00-05:00"
    },
    "flag": {
      "flag_icon": "🇺🇸",
      "flag_unicode": "U+1F1FA U+1F1F8"
    },
    "currency": {
      "code": "USD",
      "symbol": "$",
      "name": "US Dollar",
      "name_plural": "US dollars",
      "hex_unicode": "0024"
    },
    "connection": {
      "asn_number": 15169,
      "asn_org": "Google LLC",
      "isp": "Google LLC",
      "org": "Google LLC",
      "domain": "google.com",
      "connection_type": "Corporate"
    },
    "security": {
      "is_vpn": false,
      "is_tor": false,
      "is_threat": "low"
    },
    "user_agent": null
  }
}
```

City/region on anycast DNS IPs may be empty; country, ASN, timezone, flag, and currency are populated. Exact coordinates vary.

## Migrating from v1

| v1 | v2 |
|----|----|
| `get_ip(ip)` / `get_location(ip)` | `lookup(ip)` then `resp.data.geo_location` |
| `get_me()` / `get_location()` | `me()` |
| `get_timezone(ip)` | `lookup(ip).data.timezone` |
| `get_connection(ip)` | `lookup(ip).data.connection` |
| `get_security(ip)` | `lookup(ip).data.security` |
| *(missing)* | `bulk(ips)` |

Client class is `IPWhoClient` (was `IPWho`). Calls are **synchronous**.

## API Reference

### `IPWhoClient(api_key, base_url=None, timeout=30.0)`

- **api_key**: [IPWho](https://www.ipwho.org) API key (sent as query `apiKey`). Required.
- **base_url**: default `https://api.ipwho.org`.
- **timeout**: seconds (default `30`).
- **Raises**: `ValueError` if the key is empty.

### `lookup(ip, format="json", fields=None) -> IpGeoResponse`

`GET /ip/{ip}`. `format`: `json` (typed), `xml`, or `csv`. `fields`: optional comma-separated objects, e.g. `"geoLocation,timezone"`.

### `me(format="json", fields=None) -> IpGeoResponse`

`GET /me` — same shape as `lookup`, for the caller's IP.

### `bulk(ips) -> IpGeoResponse`

`GET /bulk/{ip1,ip2,...}`. `ips` must be non-empty. Per-IP rows: `resp.data.response_array` (list of `IpGeoResponse`).

### Errors

- `InvalidIPError` — HTTP 404
- `RateLimitError` — HTTP 429
- `APIResponseError` — other HTTP / `success: false`
- `IPWhoError` — base class

## Type Definitions

```python
@dataclass
class IpGeoResponse:
    success: bool
    data: Optional[GeoData]
    message: Optional[str]

@dataclass
class GeoData:
    ip: str
    geo_location: Optional[GeoLocation]
    timezone: Optional[Timezone]
    flag: Optional[Flag]
    currency: Optional[Currency]
    connection: Optional[Connection]
    security: Optional[Security]
    user_agent: Optional[UserAgent]
    response_array: Optional[List[IpGeoResponse]]  # bulk

@dataclass
class GeoLocation:
    continent: Optional[str]
    continent_code: Optional[str]
    country: Optional[str]
    country_code: Optional[str]
    capital: Optional[str]
    region: Optional[str]
    region_code: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    dial_code: Optional[str]
    is_in_eu: Optional[bool]
    latitude: Optional[float]
    longitude: Optional[float]
    accuracy_radius: Optional[float]

@dataclass
class Timezone:
    time_zone: Optional[str]
    abbr: Optional[str]
    offset: Optional[int]
    is_dst: Optional[bool]
    utc: Optional[str]
    current_time: Optional[str]

@dataclass
class Flag:
    flag_icon: Optional[str]
    flag_unicode: Optional[str]

@dataclass
class Currency:
    code: Optional[str]
    symbol: Optional[str]
    name: Optional[str]
    name_plural: Optional[str]
    hex_unicode: Optional[str]

@dataclass
class Connection:
    asn_number: Optional[int]
    asn_org: Optional[str]
    isp: Optional[str]
    org: Optional[str]
    domain: Optional[str]
    connection_type: Optional[str]

@dataclass
class Security:
    is_vpn: Optional[bool]
    is_tor: Optional[bool]
    is_threat: Optional[str]  # "low" | "medium" | "high"

@dataclass
class UserAgent:
    browser: Optional[Browser]   # name, version
    engine: Optional[Engine]
    os: Optional[OS]
    device: Optional[Device]     # type, vendor, model
    cpu: Optional[CPU]           # architecture
```

The live JSON mixes camelCase and snake_case (`postal_Code`, `flag_Icon`, `isVpn`). The SDK maps those onto the fields above.

## Troubleshooting

- **API key is required**: create a key at [ipwho.org](https://www.ipwho.org).
- **HTTP 403**: blank User-Agent is rejected. This SDK sends `ipwho-python-sdk/2.0.0`.
- **HTTP 401 / invalid key**: `APIResponseError`.
- **HTTP 429**: `RateLimitError` — back off and retry.
- **HTTP 404**: `InvalidIPError`.
- **None nested objects**: not every IP has city, postal code, or user-agent.

## Testing

```bash
IPWHO_API_KEY=your_key python3 test_ipwho.py
```

The live check is `test_ipwho.py`.

## Changelog

### v2.0.0

- `lookup` / `me` / `bulk` matching [api.ipwho.org](https://api.ipwho.org)
- Full `IpGeoResponse` (geo, timezone, flag, currency, connection, security, user-agent)
- Breaking change from v1 `IPWho.get_location` / `get_ip`

## License

MIT License — see [LICENSE](LICENSE).

## Support

- Documentation: [ipwho.org/docs](https://www.ipwho.org/docs)
- Contact: [ipwho.org/contact](https://www.ipwho.org/contact)
- GitHub Issues: [lavrox/SDK-IPWho-Python](https://github.com/lavrox/SDK-IPWho-Python/issues)
- Website: [ipwho.org](https://www.ipwho.org)

---

[IPWho](https://www.ipwho.org) — a [Lavrox](https://lavrox.com) network API.

[Lavrox](https://lavrox.com) — Independent API infrastructure. Lower latency, lower cost.
