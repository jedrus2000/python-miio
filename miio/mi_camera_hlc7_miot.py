"""Xiaomi Mi Camera - Model: isa.camera.hlc7 support."""

import enum
import ipaddress
import logging
import socket
from typing import Any, Dict
from urllib.parse import urlparse

import click

from .click_common import EnumType, command, format_output
from .miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)

SUPPORTED_MODELS = [
    "isa.camera.hlc7",
]

_MAPPING = {
    # from: https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:camera:0000A01C:isa-hlc7:2
    # Camera Control
    "power": {"siid": 2, "piid": 1},
    "image_rollover": {"siid": 2, "piid": 2},
    "night_shot": {"siid": 2, "piid": 3},
    "time_watermark": {"siid": 2, "piid": 4},
    "recording_mode": {"siid": 2, "piid": 7},
    # Indicator light
    "indicator_light": {"siid": 3, "piid": 1},
    # Memory Card Management
    "sdcard_status": {"siid": 4, "piid": 1},
    "sdcard_total_space": {"siid": 4, "piid": 2},
    "sdcard_free_space": {"siid": 4, "piid": 3},
    "sdcard_used_space": {"siid": 4, "piid": 4},
    "sdcard_format": {"siid": 4, "aiid": 1},
    "sdcard_pop_up": {"siid": 4, "aiid": 2},
    # Motion Detection
    "motion_detection_status": {"siid": 5, "piid": 1},
    "motion_alarm_interval": {"siid": 5, "piid": 2},
    "motion_detection_sensitivity": {"siid": 5, "piid": 3},
    "motion_detection_start_time": {"siid": 5, "piid": 4},
    "motion_detection_end_time": {"siid": 5, "piid": 5},
    # other functions
    "timezone": {"siid": 6, "piid": 2},
    "rect": {"siid": 6, "piid": 3},
    "custom_voice": {"siid": 6, "piid": 4},
    "set_custom_voice": {"siid": 6, "piid": 5},
    "download_voice": {"siid": 6, "piid": 6},
    "delete_voice": {"siid": 6, "piid": 7},
    "switch_voice": {"siid": 6, "piid": 8},
    "max_connect": {"siid": 6, "piid": 9},
    "restart_device": {"siid": 6, "aiid": 1},
    "upload_recode": {"siid": 6, "aiid": 2},
    "speaker_voice": {"siid": 6, "aiid": 3},
    "upload_log": {"siid": 6, "aiid": 4},
    # P2P stream
    "p2p_stream_start": {"siid": 7, "aiid": 1},
    "p2p_stream_stop": {"siid": 7, "aiid": 2},
    # Camera Stream Management for Amazon Alexa
    "alexa_video_stream_status": {"siid": 8, "piid": 9},
    "alexa_video_rtsp_stream_start": {"siid": 8, "aiid": 1},
    "alexa_video_rtsp_stream_stop": {"siid": 8, "aiid": 2},
    "alexa_video_rtsp_stream_configuration": {"siid": 8, "aiid": 3},
}

_MAPPINGS = {model: _MAPPING for model in SUPPORTED_MODELS}


class Direction(enum.Enum):
    """Rotation direction."""

    Left = 1
    Right = 2
    Up = 3
    Down = 4


class MotionDetectionSensitivity(enum.IntEnum):
    """Motion detection sensitivity."""

    High = 3
    Low = 1


class HomeMonitoringMode(enum.IntEnum):
    """Home monitoring mode."""

    Off = 0
    AllDay = 1
    Custom = 2


class NASState(enum.IntEnum):
    """NAS state."""

    Off = 2
    On = 3


class NASSyncInterval(enum.IntEnum):
    """NAS sync interval."""

    Realtime = 300
    Hour = 3600
    Day = 86400


class NASVideoRetentionTime(enum.IntEnum):
    """NAS video retention time."""

    Week = 604800
    Month = 2592000
    Quarter = 7776000
    HalfYear = 15552000
    Year = 31104000


CONST_HIGH_SENSITIVITY = [MotionDetectionSensitivity.High] * 32
CONST_LOW_SENSITIVITY = [MotionDetectionSensitivity.Low] * 32


class CameraStatus(DeviceStatus):
    """Container for status reports from the Xiaomi Mi Camera Hlc7."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        print(self.data)

    @property
    def power(self) -> str:
        """Camera power."""
        return "On" if self.data["power"] else "Off"

    @property
    def image_rollover(self) -> int:
        """Image rollover in arc degrees: 0-360"""
        return self.data["image_rollover"]

    @property
    def night_shot(self) -> int:
        """Night shot"""
        return self.data["night_shot"]

class MiCameraHlc7Miot(MiotDevice):
    """Main class representing the Xiaomi Mi Camera Hlc7."""

    _supported_models = SUPPORTED_MODELS
    _mappings = _MAPPINGS
    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Image Rollover: {result.image_rollover}\n"
            "\n",
        )
    )
    def status(self) -> CameraStatus:
        """Retrieve properties."""

        return CameraStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(default_output=format_output("Power on"))
    def on(self):
        """Power on."""
        return self.set_property("power", True)

    @command(default_output=format_output("Power off"))
    def off(self):
        """Power off."""
        return self.set_property("power", False)

    @command(default_output=format_output("Restart device"))
    def restart(self):
        """Restart device"""
        return self.call_action("restart_device")

    @command(default_output=format_output("Start P2P stream"))
    def p2p_stream_start(self):
        """Start P2P stream"""
        return self.call_action("p2p_stream_start")

    @command(default_output=format_output("Stop P2P stream"))
    def p2p_stream_stop(self):
        """Stop P2P stream"""
        return self.call_action("p2p_stream_stop")

    @command(default_output=format_output("Start Alexa RTSP video stream"))
    def alexa_video_rtsp_stream_start(self):
        """Start Alexa RTSP video stream"""
        return self.call_action("alexa_video_rtsp_stream_start", True)

    @command(default_output=format_output("Get Alexa RTSP video stream configuration"))
    def alexa_video_rtsp_stream_configuration(self):
        """Get Alexa RTSP video stream configuration"""
        return self.call_action("alexa_video_rtsp_stream_configuration")

    @command(default_output=format_output("test"))
    def test(self):
        """test"""
        return self.send("camera_stream_for_amazon_alexa", ["start_rtsp_stream"])









    @command(default_output=format_output("MotionRecord on"))
    def motion_record_on(self):
        """Start recording when motion detected."""
        return self.send("set_motion_record", ["on"])

    @command(default_output=format_output("MotionRecord off"))
    def motion_record_off(self):
        """Motion record off, always record video."""
        return self.send("set_motion_record", ["off"])

    @command(default_output=format_output("MotionRecord stop"))
    def motion_record_stop(self):
        """Motion record off, video recording stopped."""
        return self.send("set_motion_record", ["stop"])

    @command(default_output=format_output("Light on"))
    def light_on(self):
        """Light on."""
        return self.send("set_light", ["on"])

    @command(default_output=format_output("Light off"))
    def light_off(self):
        """Light off."""
        return self.send("set_light", ["off"])

    @command(default_output=format_output("FullColor on"))
    def full_color_on(self):
        """Full color on."""
        return self.send("set_full_color", ["on"])

    @command(default_output=format_output("FullColor off"))
    def full_color_off(self):
        """Full color off."""
        return self.send("set_full_color", ["off"])

    @command(default_output=format_output("Flip on"))
    def flip_on(self):
        """Flip image 180 degrees on."""
        return self.send("set_flip", ["on"])

    @command(default_output=format_output("Flip off"))
    def flip_off(self):
        """Flip image 180 degrees off."""
        return self.send("set_flip", ["off"])

    @command(default_output=format_output("ImproveProgram on"))
    def improve_program_on(self):
        """Improve program on."""
        return self.send("set_improve_program", ["on"])

    @command(default_output=format_output("ImproveProgram off"))
    def improve_program_off(self):
        """Improve program off."""
        return self.send("set_improve_program", ["off"])

    @command(default_output=format_output("Watermark on"))
    def watermark_on(self):
        """Watermark on."""
        return self.send("set_watermark", ["on"])

    @command(default_output=format_output("Watermark off"))
    def watermark_off(self):
        """Watermark off."""
        return self.send("set_watermark", ["off"])

    @command(default_output=format_output("WideDynamicRange on"))
    def wdr_on(self):
        """Wide dynamic range on."""
        return self.send("set_wdr", ["on"])

    @command(default_output=format_output("WideDynamicRange off"))
    def wdr_off(self):
        """Wide dynamic range off."""
        return self.send("set_wdr", ["off"])

    @command(default_output=format_output("NightMode auto"))
    def night_mode_auto(self):
        """Auto switch to night mode."""
        return self.send("set_night_mode", [0])

    @command(default_output=format_output("NightMode off"))
    def night_mode_off(self):
        """Night mode off."""
        return self.send("set_night_mode", [1])

    @command(default_output=format_output("NightMode on"))
    def night_mode_on(self):
        """Night mode always on."""
        return self.send("set_night_mode", [2])

    @command(
        click.argument("direction", type=EnumType(Direction)),
        default_output=format_output("Rotating to direction '{direction.name}'"),
    )
    def rotate(self, direction: Direction):
        """Rotate camera to given direction (left, right, up, down)."""
        return self.send("set_motor", {"operation": direction.value})

    @command()
    def alarm(self):
        """Sound a loud alarm for 10 seconds."""
        return self.send("alarm_sound")

    @command(
        click.argument("sensitivity", type=EnumType(MotionDetectionSensitivity)),
        default_output=format_output("Setting motion sensitivity '{sensitivity.name}'"),
    )
    def set_motion_sensitivity(self, sensitivity: MotionDetectionSensitivity):
        """Set motion sensitivity (high, low)."""
        return self.send(
            "set_motion_region",
            CONST_HIGH_SENSITIVITY
            if sensitivity == MotionDetectionSensitivity.High
            else CONST_LOW_SENSITIVITY,
        )

    @command(
        click.argument("mode", type=EnumType(HomeMonitoringMode)),
        click.argument("start-hour", default=10),
        click.argument("start-minute", default=0),
        click.argument("end-hour", default=17),
        click.argument("end-minute", default=0),
        click.argument("notify", default=1),
        click.argument("interval", default=5),
        default_output=format_output("Setting alarm config to '{mode.name}'"),
    )
    def set_home_monitoring_config(
            self,
            mode: HomeMonitoringMode = HomeMonitoringMode.AllDay,
            start_hour: int = 10,
            start_minute: int = 0,
            end_hour: int = 17,
            end_minute: int = 0,
            notify: int = 1,
            interval: int = 5,
    ):
        """Set home monitoring configuration."""
        return self.send(
            "setAlarmConfig",
            [mode, start_hour, start_minute, end_hour, end_minute, notify, interval],
        )

    @command(default_output=format_output("Clearing NAS directory"))
    def clear_nas_dir(self):
        """Clear NAS directory."""
        return self.send("nas_clear_dir", [[]])

    @command(default_output=format_output("Getting NAS config info"))
    def get_nas_config(self):
        """Get NAS config info."""
        return self.send("nas_get_config", {})

    @command(
        click.argument("state", type=EnumType(NASState)),
        click.argument("share", type=str),
        click.argument("sync-interval", type=EnumType(NASSyncInterval)),
        click.argument("video-retention-time", type=EnumType(NASVideoRetentionTime)),
        default_output=format_output("Setting NAS config to '{state.name}'"),
    )
    def set_nas_config(
            self,
            state: NASState,
            share=None,
            sync_interval: NASSyncInterval = NASSyncInterval.Realtime,
            video_retention_time: NASVideoRetentionTime = NASVideoRetentionTime.Week,
    ):
        """Set NAS configuration."""

        params: Dict[str, Any] = {
            "state": state,
            "sync_interval": sync_interval,
            "video_retention_time": video_retention_time,
        }

        share = urlparse(share)
        if share.scheme == "smb":
            ip = socket.gethostbyname(share.hostname)
            reversed_ip = ".".join(reversed(ip.split(".")))
            addr = int(ipaddress.ip_address(reversed_ip))

            params["share"] = {
                "type": 1,
                "name": share.hostname,
                "addr": addr,
                "dir": share.path.lstrip("/"),
                "group": "WORKGROUP",
                "user": share.username,
                "pass": share.password,
            }

        return self.send("nas_set_config", params)
