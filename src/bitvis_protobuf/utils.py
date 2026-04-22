"""Utility functions for Bitvis Power Hub host and device formatting."""


def normalize_host(host: str) -> str:
    """Strip surrounding brackets from IPv6 literals (e.g. '[2001:db8::10]')."""
    if host.startswith("[") and host.endswith("]"):
        return host[1:-1]
    return host


def format_unique_id(host: str, port: int) -> str:
    """Format a stable unique ID from host and port.

    IPv6 addresses are wrapped in brackets to produce a standard '[addr]:port'
    string that is unambiguous when the address itself contains colons.
    """
    if ":" in host and not host.startswith("["):
        return f"[{host}]:{port}"
    return f"{host}:{port}"


def format_mac_address(mac_bytes: bytes) -> str:
    """Format raw MAC address bytes as a colon-separated hex string."""
    return mac_bytes.hex(sep=":")
