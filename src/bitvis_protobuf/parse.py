"""Discriminated payload types and parser for Bitvis Power Hub UDP datagrams."""

from dataclasses import dataclass

from google.protobuf.message import DecodeError

from .han_port_pb2 import HanPortSample
from .powerhub_pb2 import Diagnostic, Payload


@dataclass(frozen=True)
class PayloadSample:
    """A parsed HAN port sample payload."""

    sample: HanPortSample


@dataclass(frozen=True)
class PayloadDiagnostic:
    """A parsed diagnostic payload."""

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
        return PayloadSample(sample=payload.sample)
    if payload.HasField("diagnostic"):
        return PayloadDiagnostic(diagnostic=payload.diagnostic)
    return None
