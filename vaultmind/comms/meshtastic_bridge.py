"""Meshtastic LoRa mesh network integration for off-grid messaging."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class MeshMessage:
    """A message received from the Meshtastic mesh network."""

    sender: str
    text: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    snr: float | None = None
    rssi: int | None = None


class MeshtasticBridge:
    """Bridge to a local Meshtastic LoRa node for mesh communication.

    Connects via serial (USB) to a Meshtastic-compatible radio
    (e.g., Heltec V3, T-Beam) for off-grid text messaging.
    """

    def __init__(self, serial_port: str | None = None):
        self._interface = None
        self._serial_port = serial_port
        self._message_log: list[MeshMessage] = []

    def connect(self) -> bool:
        """Connect to the local Meshtastic node."""
        try:
            import meshtastic.serial_interface

            if self._serial_port:
                self._interface = meshtastic.serial_interface.SerialInterface(
                    self._serial_port
                )
            else:
                self._interface = meshtastic.serial_interface.SerialInterface()
            logger.info("Connected to Meshtastic node")
            return True
        except Exception:
            logger.exception("Failed to connect to Meshtastic node")
            return False

    def send_message(self, text: str, destination: str | None = None) -> bool:
        """Send a text message over the mesh network."""
        if not self._interface:
            logger.error("Not connected to Meshtastic node")
            return False
        try:
            if destination:
                self._interface.sendText(text, destinationId=destination)
            else:
                self._interface.sendText(text)
            logger.info("Message sent: %s", text[:50])
            return True
        except Exception:
            logger.exception("Failed to send message")
            return False

    def get_node_info(self) -> dict:
        """Get information about the local node and visible mesh nodes."""
        if not self._interface:
            return {"error": "Not connected"}
        try:
            nodes = self._interface.nodes
            return {
                "local_node": str(self._interface.myInfo),
                "visible_nodes": len(nodes) if nodes else 0,
                "nodes": [
                    {
                        "id": node_id,
                        "name": info.get("user", {}).get("longName", "Unknown"),
                        "snr": info.get("snr"),
                    }
                    for node_id, info in (nodes or {}).items()
                ],
            }
        except Exception:
            logger.exception("Failed to get node info")
            return {"error": "Failed to read node info"}

    def disconnect(self):
        """Close the connection to the Meshtastic node."""
        if self._interface:
            self._interface.close()
            self._interface = None
            logger.info("Disconnected from Meshtastic node")
