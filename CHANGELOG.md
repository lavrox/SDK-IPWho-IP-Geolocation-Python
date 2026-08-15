# Changelog

## [2.0.0] - 2026-08-15

### Breaking

- Replaced v1 `IPWho.get_location` / `get_ip` / `get_me` with `IPWhoClient.lookup` / `me` / `bulk`.
- Import path is `from ipwho import IPWhoClient` (no longer `from src import IPWho`).
- Responses are the full `IpGeoResponse` payload (geo, timezone, flag, currency, connection, security, user-agent).

## [1.0.2]

Previous PyPI release of the v1 getters client.
