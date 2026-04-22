"""Command-line listener for Bitvis Power Hub UDP packets."""

import argparse
import asyncio
import logging
import signal

from .listener import SharedListener
from .parse import PayloadDiagnostic, PayloadSample, parse_payload
from .utils import format_mac_address

DEFAULT_PORT = 58220

_LOGGER = logging.getLogger(__name__)


def _log_payload(payload: PayloadSample | PayloadDiagnostic, addr: tuple[str, int]) -> None:
    """Print a human-readable summary of a received payload."""
    src = f"{addr[0]}:{addr[1]}"
    if isinstance(payload, PayloadSample):
        s = payload.sample
        parts = [f"sample from {src}"]
        if s.HasField("power_active_delivered_to_client_kw"):
            parts.append(
                f"active_power_to_client={s.power_active_delivered_to_client_kw:.3f} kW"
            )
        if s.HasField("power_active_delivered_by_client_kw"):
            parts.append(
                f"active_power_by_client={s.power_active_delivered_by_client_kw:.3f} kW"
            )
        print("  ".join(parts))
    else:
        d = payload.diagnostic
        parts = [
            f"diagnostic from {src}",
            f"uptime={d.uptime_s}s",
            f"rssi={d.wifi_rssi_dbm} dBm",
        ]
        if d.HasField("device_info"):
            di = d.device_info
            parts.append(f"mac={format_mac_address(di.mac_address)}")
            parts.append(f"model={di.model_name}")
            parts.append(f"sw={di.sw_version}")
        print("  ".join(parts))


class _AllSourcesListener(SharedListener):
    """SharedListener variant that dispatches every datagram regardless of source IP."""

    def dispatch(self, data: bytes, addr: tuple[str, int]) -> None:
        payload = parse_payload(data)
        if payload is None:
            _LOGGER.debug("Unrecognised datagram from %s, ignoring", addr[0])
            return
        _log_payload(payload, addr)


async def _run(port: int, ip_filter: str | None) -> None:
    if ip_filter:
        listener: SharedListener = SharedListener()
    else:
        listener = _AllSourcesListener()

    try:
        await listener.start(port)
    except OSError as err:
        print(f"Failed to bind port {port}: {err}")
        return

    if ip_filter:
        listener.register({ip_filter}, _log_payload)
        print(f"Listening on port {port}, filtering to {ip_filter} ...")
    else:
        print(f"Listening on port {port} (all sources) ...")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    await listener.stop()
    print("Stopped.")


def main() -> None:
    """Entry point for the bitvis-listen CLI."""
    parser = argparse.ArgumentParser(
        description="Listen for Bitvis Power Hub UDP packets and print them."
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=DEFAULT_PORT,
        help=f"UDP port to listen on (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--ip",
        metavar="ADDRESS",
        default=None,
        help="Source IP address to filter on (default: all devices)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    asyncio.run(_run(args.port, args.ip))


if __name__ == "__main__":
    main()
