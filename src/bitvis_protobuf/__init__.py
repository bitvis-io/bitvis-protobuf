"""Bitvis Power Hub protobuf definitions."""

__version__ = "0.1.0"

# Re-export generated protobuf modules for convenience
from . import device_info_pb2, diagnostic_pb2, han_port_pb2, powerhub_pb2
from .listener import DatagramCallback, SharedListener
from .parse import PayloadDiagnostic, PayloadSample, parse_payload
from .utils import (
    InvalidMacAddressError,
    async_resolve_host,
    async_verify_udp_port_bindable,
    format_mac_address,
    get_mac_address_for_host,
    normalize_host,
)

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
    "InvalidMacAddressError",
    "async_resolve_host",
    "async_verify_udp_port_bindable",
    "format_mac_address",
    "get_mac_address_for_host",
    "normalize_host",
]
