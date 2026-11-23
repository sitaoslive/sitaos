import pytest
from engine.ghl_api_client import GHLClient

def test_ghl_client_initialization_defaults():
    client = GHLClient(token="pit-test-token-123456", location_id="n4sb0M0P3oQhIux2e1Um")
    assert client.is_configured is True
    assert client.location_id == "n4sb0M0P3oQhIux2e1Um"
    headers = client._headers()
    assert headers["Authorization"] == "Bearer pit-test-token-123456"
    assert headers["Version"] == "2021-07-28"

def test_ghl_client_unconfigured_guard():
    client = GHLClient(token="your_ghl_token", location_id="your_location")
    assert client.is_configured is False
    res = client.get_location()
    assert "error" in res
