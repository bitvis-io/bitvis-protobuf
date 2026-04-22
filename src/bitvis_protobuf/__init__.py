"""Bitvis Power Hub protobuf definitions."""

__version__ = "0.1.0"

# Re-export generated protobuf modules for convenience
from . import device_info_pb2, diagnostic_pb2, han_port_pb2, powerhub_pb2
from .listener import DatagramCallback, SharedListener
from .parse import PayloadDiagnostic, PayloadSample, parse_payload
from .utils import format_mac_address, format_unique_id, normalize_host

__all__ = [
    "device_info_pb2",
    "diagnostic_pb2",
    "han_port_pb2",
    "powerhub_pb2",
    "DatagramCallback",
    "SharedListener",
    "PayloadDiagnostic",
    "PayloadSample",
    "parse_payload",
    "format_mac_address",
    "format_unique_id",
    "normalize_host",
]
