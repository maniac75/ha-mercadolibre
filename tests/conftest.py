"""Compatibility for aioresponses 0.7.9 with HA 2026.10's aiohttp.

Only the synthetic ClientResponse constructor is adapted. Requests, status codes,
payloads, exceptions and the integration under test retain their normal behavior.
"""

import inspect
from unittest.mock import Mock

import aiohttp
import aioresponses.core
import pytest


@pytest.fixture(autouse=True)
def aiohttp_mock_response_constructor(monkeypatch):
    if "stream_writer" not in inspect.signature(aiohttp.ClientResponse).parameters:
        return

    class SyntheticResponse(aiohttp.ClientResponse):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("stream_writer", Mock())
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(aioresponses.core, "ClientResponse", SyntheticResponse)
