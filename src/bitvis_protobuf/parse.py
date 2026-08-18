"""Discriminated payload types and parser for Bitvis Power Hub UDP datagrams."""

from dataclasses import dataclass

from google.protobuf.message import DecodeError

from .han_port_pb2 import HanPortSample
from .powerhub_pb2 import Diagnostic, Payload
from .utils import format_mac_address


@dataclass(frozen=True)
class PayloadSample:
    """A parsed HAN port sample payload."""

    mac_address: str
    sample: HanPortSample


@dataclass(frozen=True)
class PayloadDiagnostic:
    """A parsed diagnostic payload."""

    mac_address: str
    diagnostic: Diagnostic


def parse_payload(data: bytes) -> PayloadSample | PayloadDiagnostic | None:
    """Parse raw UDP bytes into a typed payload.

    Returns a PayloadSample or PayloadDiagnostic on success, or None if the
    data cannot be decoded or contains an unrecognised payload type.
    """
    payload = Payload()
    try:
        payload.ParseFromString(data)
    except DecodeError:
        return None

    if payload.HasField("sample"):
        return PayloadSample(
            mac_address=format_mac_address(payload.mac_address), sample=payload.sample
        )
    if payload.HasField("diagnostic"):
        return PayloadDiagnostic(
            mac_address=format_mac_address(payload.mac_address),
            diagnostic=payload.diagnostic,
        )
    return None
