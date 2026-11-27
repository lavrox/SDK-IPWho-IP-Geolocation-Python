"""Requests against a local stand-in server that replays recorded API responses.

No API key and no network access are needed.
"""

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from ipwho import APIResponseError, InvalidIPError, IPWhoClient, RateLimitError

KEY = "sk.test_secret_value"


def fixture(name):
    return (Path(__file__).parent / "fixtures" / f"{name}.json").read_text("utf-8")


class Stub:
    def __init__(self):
        self.requests = []
        self.reply(200, fixture("lookup"))

    def reply(self, status, body):
        self.status, self.body = status, body


@pytest.fixture
def stub():
    state = Stub()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            state.requests.append((self.path, dict(self.headers)))
            self.send_response(state.status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(state.body.encode("utf-8"))

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    state.url = f"http://127.0.0.1:{server.server_address[1]}"
    yield state
    server.shutdown()


@pytest.fixture
def client(stub, monkeypatch):
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    return IPWhoClient(KEY, base_url=stub.url)


def test_key_is_in_the_header_and_never_in_the_url(stub, client):
    client.lookup("8.8.8.8")
    client.me()
    stub.reply(200, fixture("bulk"))
    client.bulk(["8.8.8.8", "1.1.1.1"])
    assert len(stub.requests) == 3
    for path, headers in stub.requests:
        assert headers["Authorization"] == f"Bearer {KEY}"
        assert KEY not in path
        assert "apikey" not in path.lower()


def test_netrc_cannot_replace_the_key(stub, client, tmp_path, monkeypatch):
    netrc = tmp_path / "netrc"
    netrc.write_text("default login someone password else\n")
    netrc.chmod(0o600)
    monkeypatch.setenv("NETRC", str(netrc))
    client.lookup("8.8.8.8")
    assert stub.requests[0][1]["Authorization"] == f"Bearer {KEY}"


def test_lookup_maps_the_response(stub, client):
    data = client.lookup("8.8.8.8").data
    assert stub.requests[0][0] == "/ip/8.8.8.8"
    assert data.ip == "8.8.8.8"
    assert data.geo_location.country == "United States"
    assert data.geo_location.country_code == "US"
    assert data.geo_location.dial_code == "+1"
    assert data.connection.asn_number == 15169
    assert data.timezone.time_zone == "America/Chicago"
    assert data.currency.code == "USD"


def test_lookup_accepts_a_null_currency(stub, client):
    stub.reply(200, fixture("lookup-null-currency"))
    data = client.lookup("1.1.1.1").data
    assert data.ip == "1.1.1.1"
    assert data.currency is None
    assert data.connection.asn_number == 13335


def test_bulk_returns_the_data_for_every_address(stub, client):
    stub.reply(200, fixture("bulk"))
    rows = client.bulk(["8.8.8.8", "1.1.1.1", "192.168.0.1", "9.9.9.9"]).data.response_array
    assert len(rows) == 4

    assert rows[0].success and rows[0].data.ip == "8.8.8.8"
    assert rows[0].data.geo_location.country == "United States"
    assert rows[0].data.connection.asn_number == 15169

    assert rows[1].success and rows[1].data.ip == "1.1.1.1"
    assert rows[1].data.currency is None
    assert rows[1].data.connection.asn_number == 13335

    assert not rows[2].success
    assert rows[2].data.ip == "192.168.0.1"
    assert rows[2].data.geo_location is None
    assert rows[2].message == "Reserved range/Invalid IP address"

    assert not rows[3].success
    assert rows[3].data.ip == "9.9.9.9"
    assert "quota" in rows[3].message


def test_fields_and_format_are_the_only_query_parameters(stub, client):
    client.lookup("8.8.8.8", fields="geoLocation,timezone")
    assert stub.requests[0][0] == "/ip/8.8.8.8?get=geoLocation%2Ctimezone"
    stub.reply(200, "ip,8.8.8.8")
    assert client.lookup("8.8.8.8", format="csv").data.ip == "ip,8.8.8.8"
    assert stub.requests[1][0] == "/ip/8.8.8.8?format=csv"


@pytest.mark.parametrize(
    "status, body, error",
    [
        (404, '{"success":false,"message":"Reserved range/Invalid IP address"}', InvalidIPError),
        (429, '{"error":"rate_limit_exceeded"}', RateLimitError),
        (401, '{"error":"invalid_api_key"}', APIResponseError),
    ],
)
def test_http_errors(stub, client, status, body, error):
    stub.reply(status, body)
    with pytest.raises(error) as caught:
        client.lookup("8.8.8.8")
    assert KEY not in str(caught.value)


def test_connection_failure_does_not_reveal_the_key():
    unreachable = IPWhoClient(KEY, base_url="http://127.0.0.1:1")
    with pytest.raises(APIResponseError) as caught:
        unreachable.lookup("8.8.8.8")
    assert KEY not in str(caught.value)
    assert KEY not in repr(caught.value.__cause__)


def test_key_with_surrounding_whitespace_is_trimmed(stub, monkeypatch):
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    IPWhoClient(f"  {KEY}\n", base_url=stub.url).lookup("8.8.8.8")
    assert stub.requests[0][1]["Authorization"] == f"Bearer {KEY}"


def test_key_with_invalid_characters_is_rejected_without_repeating_it():
    with pytest.raises(ValueError) as caught:
        IPWhoClient("sk.secret_part\nmore")
    assert "secret_part" not in str(caught.value)
    with pytest.raises(ValueError, match="api_key is required"):
        IPWhoClient("  \n")
    with pytest.raises(ValueError, match="api_key is required"):
        IPWhoClient(123)
