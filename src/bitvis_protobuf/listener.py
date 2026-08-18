"""Shared async UDP listener for Bitvis Power Hub devices."""

import asyncio
import ipaddress
import logging
import socket
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass

from .parse import PayloadDiagnostic, PayloadSample, parse_payload

_LOGGER = logging.getLogger(__name__)

DatagramCallback = Callable[[PayloadSample | PayloadDiagnostic, tuple[str, int]], None]


class _SharedProtocol(asyncio.DatagramProtocol):
    """Internal UDP protocol that forwards datagrams to a SharedListener."""

    def __init__(self, listener: "SharedListener") -> None:
        """Initialize the protocol."""
        self._listener = listener
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Handle connection made."""
        assert isinstance(transport, asyncio.DatagramTransport)
        self.transport = transport
        _LOGGER.debug(
            "Shared UDP listener started on %s", transport.get_extra_info("sockname")
        )

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Forward datagram to the shared listener for dispatch."""
        self._listener.dispatch(data, addr)

    def error_received(self, exc: Exception) -> None:
        """Handle protocol error."""
        _LOGGER.debug("UDP protocol error: %s", exc)

    def connection_lost(self, exc: Exception | None) -> None:
        """Handle connection lost."""
        if exc:
            _LOGGER.debug("UDP connection lost: %s", exc)
        else:
            _LOGGER.debug("UDP connection closed")


@dataclass(frozen=True)
class Filter(ABC):
    @abstractmethod
    def match(sample: PayloadSample | PayloadDiagnostic, host: str):
        pass


class FilterAny(Filter):
    def __init__(self):
        pass

    def match(self, sample: PayloadSample | PayloadDiagnostic, host: str):
        return True


class FilterMac(Filter):
    def __init__(self, mac_address: str):
        self.mac_address = mac_address

    def match(self, sample: PayloadSample | PayloadDiagnostic, host: str):
        return sample.mac_address.lower() == self.mac_address.lower()


class FilterIp(Filter):
    def __init__(self, ip: str):
        self.ip = ip

    def match(self, sample: PayloadSample | PayloadDiagnostic, host: str):
        return host == self.ip


class SharedListener:
    """Single UDP socket for one port, dispatching parsed payloads by source IP.

    One listener is kept per UDP port. Multiple callers on the same port share
    the socket, avoiding the SO_REUSEPORT load-balancing problem where the OS
    could deliver a datagram to the wrong socket.
    """

    def __init__(self) -> None:
        """Initialize the shared listener."""
        self._transports: list[asyncio.DatagramTransport] = []
        self._callbacks: dict[Filter, DatagramCallback] = {}

    async def start(self, port: int) -> None:
        """Bind UDP sockets (IPv4 and IPv6) and start receiving datagrams."""
        loop = asyncio.get_running_loop()
        bind_errors: list[Exception] = []
        for family, local_addr in (
            (socket.AF_INET6, ("::", port)),
            (socket.AF_INET, ("0.0.0.0", port)),
        ):
            try:
                sock = socket.socket(family, socket.SOCK_DGRAM)
                if family == socket.AF_INET6:
                    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind(local_addr)
                transport, _ = await loop.create_datagram_endpoint(
                    lambda: _SharedProtocol(self),
                    sock=sock,
                )
            except OSError as err:
                sock.close()
                bind_errors.append(err)
            else:
                assert isinstance(transport, asyncio.DatagramTransport)
                self._transports.append(transport)

        if not self._transports:
            raise OSError("Unable to bind UDP listener") from (
                bind_errors[0] if bind_errors else None
            )
        _LOGGER.debug("Started shared UDP listener on port %s", port)

    async def stop(self) -> None:
        """Close all UDP sockets."""
        for transport in self._transports:
            transport.close()
        self._transports = []
        _LOGGER.debug("Stopped shared UDP listener")

    @property
    def is_empty(self) -> bool:
        """Return True when no callbacks are registered."""
        return not self._callbacks

    def register(self, filt: Filter, callback: DatagramCallback) -> None:
        """Register callback for a matching filter

        Raises RuntimeError if a filter is already registered to a different
        callback, so misconfigured callers fail fast.
        """

        if filt in self._callbacks:
            raise RuntimeError(f"Filter already registered: {filt}")

        self._callbacks[filt] = callback

    def unregister(self, filt: Filter) -> None:
        """Remove source-IP mappings."""
        self._callbacks.pop(filt, None)

    def dispatch(self, data: bytes, addr: tuple[str, int]) -> None:
        """Parse a datagram and invoke the registered callback for addr[0]."""
        host = addr[0]
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            normalized_host = host
        else:
            if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
                normalized_host = str(ip.ipv4_mapped)
            else:
                normalized_host = host

        payload = parse_payload(data)
        if payload is None:
            _LOGGER.debug(
                "Received unrecognised or undecodable datagram from %s, ignoring",
                normalized_host,
            )
            return

        for filt, callback in self._callbacks.items():
            if filt.match(payload, host):
                callback(payload, addr)
