"""Fixtures compartidas por las pruebas de la aplicación de empleados."""
import os

import pytest

URL_API = os.environ.get("URL_API", "http://localhost:8000")
URL_WEB = os.environ.get("URL_WEB", "http://localhost:8080")


@pytest.fixture
def url_api() -> str:
    return URL_API


@pytest.fixture
def url_web() -> str:
    return URL_WEB
