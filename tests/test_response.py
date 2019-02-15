import datetime
from pathlib import Path

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

from minisaml.errors import ResponseExpired, ResponseTooEarly
from minisaml.response import validate_response


@pytest.fixture
def read():
    def reader(filename: str) -> bytes:
        with Path(__file__).parent.joinpath(filename).open("rb") as fobj:
            return fobj.read()

    return reader


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=32,
        second=32,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_ok(read):
    data = read("response.xml.b64")
    certificate = load_pem_x509_certificate(read("cert.pem"), default_backend())
    response = validate_response(data=data, certificate=certificate)
    assert response.name_id == "user.name"
    assert response.audience == "https://sp.invalid"
    assert response.in_response_to == "8QmO2elg5T6-GPgr7dZI7v27M-wvMXc1k76B6jleNmM"
    assert response.issuer == "https://idp.invalid"
    assert response.attrs == {"attr name": "attr value"}
    assert response.attributes[0].extra_attributes == {"ExtraAttribute": "hoge"}


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=32,
        second=30,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_too_early(read):
    data = read("response.xml.b64")
    certificate = load_pem_x509_certificate(read("cert.pem"), default_backend())
    with pytest.raises(ResponseTooEarly):
        validate_response(data=data, certificate=certificate)


@pytest.mark.freeze_time(
    datetime.datetime(
        year=2020,
        month=1,
        day=16,
        hour=14,
        minute=34,
        second=32,
        tzinfo=datetime.timezone.utc,
    )
)
def test_saml_response_expired(read):
    data = read("response.xml.b64")
    certificate = load_pem_x509_certificate(read("cert.pem"), default_backend())
    with pytest.raises(ResponseExpired):
        validate_response(data=data, certificate=certificate)
