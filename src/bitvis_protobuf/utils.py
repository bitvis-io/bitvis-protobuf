"""Utility functions for Bitvis Power Hub host and device formatting."""

import asyncio
import ipaddress
import logging
import socket

from getmac import get_mac_address as _get_mac_address

_LOGGER = logging.getLogger(__name__)


def format_mac_address(mac_address: bytes) -> str:
    """Format raw MAC address bytes as colon-separated hexadecimal octets."""
    if not mac_address:
        return "00:00:00:00:00:00"

    return ":".join(f"{octet:02x}" for octet in mac_address)


async def async_resolve_host(host: str) -> set[str]:
    """Resolve *host* to a set of IP address strings.

    Returns all addresses returned by getaddrinfo, plus the literal itself if
    *host* is already an IP address.  Raises OSError if the host cannot be
    resolved to any address.
    """
    ips: set[str] = set()

    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        ips.add(host)

    loop = asyncio.get_running_loop()
    try:
        addrinfo = await loop.getaddrinfo(host, None)
    except OSError:
        _LOGGER.debug("Could not resolve host %s to IP addresses", host)
    else:
        for *_, sockaddr in addrinfo:
            ips.add(sockaddr[0])

    if not ips:
        raise OSError(f"Could not resolve host {host!r} to an IP address")

    return ips


async def async_verify_udp_port_bindable(port: int) -> None:
    """Verify UDP *port* can be bound on IPv6 and IPv4 wildcard addresses.

    Creates ephemeral datagram endpoints on ``::`` and ``0.0.0.0`` to confirm the
    port can be acquired before starting a shared listener.

    Raises:
        OSError: If the port cannot be bound for every attempted address family.
    """
    loop = asyncio.get_running_loop()
    transports: list[asyncio.DatagramTransport] = []
    bind_errors: list[Exception] = []
    for family, local_addr in (
        (socket.AF_INET6, ("::", port)),
        (socket.AF_INET, ("0.0.0.0", port)),
    ):
        try:
            transport, _ = await loop.create_datagram_endpoint(
                asyncio.DatagramProtocol,
                local_addr=local_addr,
                family=family,
            )
        except (OSError, ValueError) as err:
            bind_errors.append(err)
        else:
            assert isinstance(transport, asyncio.DatagramTransport)
            transports.append(transport)

    if not transports:
        raise OSError("UDP port is unavailable or invalid") from bind_errors[0]

    for transport in transports:
        transport.close()


def normalize_host(host: str) -> str:
    """Strip surrounding brackets from IPv6 literals (e.g. '[2001:db8::10]')."""
    if host.startswith("[") and host.endswith("]"):
        return host[1:-1]
    return host


def get_mac_address_for_host(host: str) -> str:
    """Look up the MAC address for *host*.

    *host* may be an IPv4/IPv6 address or a resolvable hostname.
    Returns a normalized MAC string suitable for use as a unique ID, or
    00:00:00:00:00:00.
    """
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        mac = _get_mac_address(hostname=host)
    else:
        if ip.version == 4:
            mac = _get_mac_address(ip=host)
        else:
            mac = _get_mac_address(ip6=host)

    return mac if mac else "00:00:00:00:00:00"
