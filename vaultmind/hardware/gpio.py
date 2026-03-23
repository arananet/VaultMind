"""GPIO and hardware control for VaultMind domotics and automation.

Supports Raspberry Pi GPIO, USB relays, and MQTT-based home automation.
Designed for off-grid scenarios: solar charge monitoring, perimeter alarms,
environmental sensors, and automated lighting/ventilation.
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class PinMode(Enum):
    INPUT = "input"
    OUTPUT = "output"
    PWM = "pwm"


class PinState(Enum):
    HIGH = 1
    LOW = 0


@dataclass
class GPIOPin:
    """Representation of a GPIO pin."""

    number: int
    mode: PinMode
    label: str = ""
    state: PinState = PinState.LOW


@dataclass
class SensorReading:
    """A reading from a connected sensor."""

    sensor_id: str
    sensor_type: str  # "temperature", "humidity", "motion", "light", "voltage"
    value: float
    unit: str
    timestamp: str = ""


class HardwareController:
    """Hardware control interface for VaultMind automation.

    Supports:
    - Raspberry Pi GPIO (via gpiod/lgpio, not deprecated RPi.GPIO)
    - USB relay boards (via hidapi or serial)
    - I2C sensors (temperature, humidity, light)
    - ADC readings (solar voltage, battery monitoring)
    """

    def __init__(self):
        self._pins: dict[int, GPIOPin] = {}
        self._gpio_available = False
        self._chip = None
        self._try_init_gpio()

    def _try_init_gpio(self):
        """Initialize GPIO using the modern gpiod library."""
        try:
            import gpiod

            self._chip = gpiod.Chip("gpiochip0")
            self._gpio_available = True
            logger.info("GPIO initialized via gpiod")
        except (ImportError, FileNotFoundError, PermissionError):
            logger.info("GPIO not available (not running on supported hardware)")

    @property
    def gpio_available(self) -> bool:
        return self._gpio_available

    def setup_pin(self, pin: int, mode: PinMode, label: str = "") -> bool:
        """Configure a GPIO pin."""
        if not self._gpio_available:
            logger.warning("GPIO not available")
            return False

        try:
            import gpiod

            config = gpiod.LineSettings()
            if mode == PinMode.OUTPUT:
                config.direction = gpiod.line.Direction.OUTPUT
            else:
                config.direction = gpiod.line.Direction.INPUT

            self._pins[pin] = GPIOPin(number=pin, mode=mode, label=label)
            logger.info("Pin %d configured as %s (%s)", pin, mode.value, label)
            return True
        except Exception:
            logger.exception("Failed to setup pin %d", pin)
            return False

    def write_pin(self, pin: int, state: PinState) -> bool:
        """Set a GPIO output pin high or low."""
        if pin not in self._pins:
            logger.error("Pin %d not configured", pin)
            return False
        if self._pins[pin].mode != PinMode.OUTPUT:
            logger.error("Pin %d is not configured as output", pin)
            return False

        try:
            import gpiod

            line = self._chip.get_line(pin)
            line.set_value(state.value)
            self._pins[pin].state = state
            return True
        except Exception:
            logger.exception("Failed to write pin %d", pin)
            return False

    def read_pin(self, pin: int) -> PinState | None:
        """Read the state of a GPIO input pin."""
        if pin not in self._pins:
            logger.error("Pin %d not configured", pin)
            return None

        try:
            import gpiod

            line = self._chip.get_line(pin)
            value = line.get_value()
            return PinState(value)
        except Exception:
            logger.exception("Failed to read pin %d", pin)
            return None

    def read_i2c_sensor(self, bus: int, address: int, sensor_type: str) -> SensorReading | None:
        """Read from an I2C sensor (e.g., DHT22, BMP280, TSL2561)."""
        try:
            import smbus2

            i2c = smbus2.SMBus(bus)

            if sensor_type == "temperature_bmp280":
                # BMP280 temperature reading (simplified)
                data = i2c.read_i2c_block_data(address, 0xFA, 3)
                raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
                # Simplified conversion (actual requires calibration data)
                temp_c = raw / 100.0
                return SensorReading(
                    sensor_id=f"i2c_{bus}_{hex(address)}",
                    sensor_type="temperature",
                    value=temp_c,
                    unit="°C",
                )
            elif sensor_type == "light_tsl2561":
                # TSL2561 light sensor (simplified)
                data = i2c.read_i2c_block_data(address, 0x8C, 2)
                lux = data[1] << 8 | data[0]
                return SensorReading(
                    sensor_id=f"i2c_{bus}_{hex(address)}",
                    sensor_type="light",
                    value=float(lux),
                    unit="lux",
                )
            else:
                logger.warning("Unknown sensor type: %s", sensor_type)
                return None
        except (ImportError, OSError):
            logger.info("I2C not available")
            return None

    def read_adc(self, channel: int) -> float | None:
        """Read analog value from ADC (e.g., ADS1115 for solar/battery voltage)."""
        try:
            import board
            import busio
            import adafruit_ads1x15.ads1115 as ADS
            from adafruit_ads1x15.analog_in import AnalogIn

            i2c = busio.I2C(board.SCL, board.SDA)
            ads = ADS.ADS1115(i2c)
            chan = AnalogIn(ads, channel)
            return chan.voltage
        except (ImportError, OSError):
            logger.info("ADC not available")
            return None

    def get_pin_status(self) -> list[dict]:
        """Get status of all configured pins."""
        return [
            {
                "pin": p.number,
                "mode": p.mode.value,
                "label": p.label,
                "state": p.state.value,
            }
            for p in self._pins.values()
        ]


class USBRelayController:
    """Control USB relay boards for switching loads (lights, pumps, fans)."""

    def __init__(self, device_path: str = "/dev/hidraw0"):
        self.device_path = device_path
        self._num_relays = 0

    def detect(self) -> bool:
        """Detect USB relay board."""
        path = Path(self.device_path)
        if path.exists():
            self._num_relays = 8  # Common USB relay boards have 1-8 relays
            logger.info("USB relay detected at %s", self.device_path)
            return True
        return False

    def set_relay(self, relay_num: int, state: bool) -> bool:
        """Turn a relay on or off."""
        try:
            with open(self.device_path, "wb") as f:
                # HID relay protocol: [0x00, relay_num, 0xFF/0xFD for on/off]
                cmd = bytes([0x00, relay_num, 0xFF if state else 0xFD])
                f.write(cmd)
            logger.info("Relay %d set to %s", relay_num, "ON" if state else "OFF")
            return True
        except (OSError, PermissionError):
            logger.exception("Failed to set relay %d", relay_num)
            return False


@dataclass
class AutomationRule:
    """A simple automation rule for domotics."""

    name: str
    trigger_type: str  # "sensor", "time", "manual"
    trigger_condition: str  # e.g., "temperature > 30", "time == 06:00"
    action_type: str  # "gpio", "relay", "alert"
    action_target: int  # pin or relay number
    action_state: bool  # on/off
    enabled: bool = True


class AutomationEngine:
    """Simple rule-based automation engine for off-grid domotics.

    Example use cases:
    - Turn on ventilation fan when temperature > 30°C
    - Activate perimeter lights at sunset
    - Sound alarm when motion sensor triggers
    - Switch to battery backup when solar voltage drops
    """

    def __init__(self, hw: HardwareController):
        self.hw = hw
        self.rules: list[AutomationRule] = []

    def add_rule(self, rule: AutomationRule):
        self.rules.append(rule)
        logger.info("Automation rule added: %s", rule.name)

    def evaluate_rules(self, sensor_readings: dict[str, float]) -> list[str]:
        """Evaluate all rules against current sensor readings.

        Returns list of actions taken.
        """
        actions_taken = []
        for rule in self.rules:
            if not rule.enabled:
                continue

            if rule.trigger_type == "sensor":
                triggered = self._evaluate_condition(
                    rule.trigger_condition, sensor_readings
                )
                if triggered:
                    self._execute_action(rule)
                    actions_taken.append(
                        f"{rule.name}: {rule.action_type} "
                        f"pin {rule.action_target} -> "
                        f"{'ON' if rule.action_state else 'OFF'}"
                    )

        return actions_taken

    def _evaluate_condition(
        self, condition: str, readings: dict[str, float]
    ) -> bool:
        """Evaluate a simple condition like 'temperature > 30'."""
        try:
            parts = condition.split()
            if len(parts) != 3:
                return False
            sensor_name, op, threshold = parts
            value = readings.get(sensor_name)
            if value is None:
                return False
            threshold_f = float(threshold)
            if op == ">":
                return value > threshold_f
            elif op == "<":
                return value < threshold_f
            elif op == ">=":
                return value >= threshold_f
            elif op == "<=":
                return value <= threshold_f
            elif op == "==":
                return abs(value - threshold_f) < 0.01
            return False
        except (ValueError, IndexError):
            return False

    def _execute_action(self, rule: AutomationRule):
        """Execute the action defined by a rule."""
        state = PinState.HIGH if rule.action_state else PinState.LOW
        if rule.action_type == "gpio":
            self.hw.write_pin(rule.action_target, state)
        elif rule.action_type == "alert":
            logger.warning("AUTOMATION ALERT: %s", rule.name)

    def save_rules(self, path: str = "config/automation_rules.json"):
        """Persist automation rules to disk."""
        rules_data = [
            {
                "name": r.name,
                "trigger_type": r.trigger_type,
                "trigger_condition": r.trigger_condition,
                "action_type": r.action_type,
                "action_target": r.action_target,
                "action_state": r.action_state,
                "enabled": r.enabled,
            }
            for r in self.rules
        ]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(rules_data, indent=2))

    def load_rules(self, path: str = "config/automation_rules.json"):
        """Load automation rules from disk."""
        rules_path = Path(path)
        if not rules_path.exists():
            return
        data = json.loads(rules_path.read_text())
        self.rules = [AutomationRule(**r) for r in data]
        logger.info("Loaded %d automation rules", len(self.rules))
