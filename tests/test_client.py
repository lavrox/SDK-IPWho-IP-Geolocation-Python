"""Constructor and mapping checks that do not call the live API."""

import pytest

from ipwho import GeoLocation, IPWhoClient, IpGeoResponse


def test_requires_api_key():
    with pytest.raises(ValueError, match="api_key is required"):
        IPWhoClient("")


def test_empty_bulk_rejected():
    client = IPWhoClient("sk.test")
    with pytest.raises(ValueError, match="ips must not be empty"):
        client.bulk([])


def test_geo_location_maps_mixed_keys():
    loc = GeoLocation.from_dict(
        {
            "continent": "North America",
            "continentCode": "NA",
            "country": "United States",
            "countryCode": "US",
            "postal_Code": "94105",
            "is_in_eu": False,
        }
    )
    assert loc.continent_code == "NA"
    assert loc.country_code == "US"
    assert loc.postal_code == "94105"
    assert loc.is_in_eu is False


def test_ip_geo_response_from_dict():
    resp = IpGeoResponse.from_dict(
        {
            "success": True,
            "data": {"ip": "8.8.8.8", "geoLocation": {"country": "United States"}},
        }
    )
    assert resp.success is True
    assert resp.data.ip == "8.8.8.8"
    assert resp.data.geo_location.country == "United States"
