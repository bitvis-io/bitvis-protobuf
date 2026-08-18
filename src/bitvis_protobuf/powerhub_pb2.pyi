import han_port_pb2 as _han_port_pb2
import device_info_pb2 as _device_info_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    EVENT_TYPE_TIMER: _ClassVar[EventType]
    EVENT_TYPE_PROVISIONING_REQUESTED: _ClassVar[EventType]
    EVENT_TYPE_MQTT_CONNECTED: _ClassVar[EventType]
    EVENT_TYPE_REBOOT_REQUESTED: _ClassVar[EventType]
    EVENT_TYPE_BOOT_UNKNOWN: _ClassVar[EventType]
    EVENT_TYPE_BOOT_SOFTWARE: _ClassVar[EventType]
    EVENT_TYPE_BOOT_POWER_ON: _ClassVar[EventType]
    EVENT_TYPE_BOOT_WATCHDOG: _ClassVar[EventType]
EVENT_TYPE_UNSPECIFIED: EventType
EVENT_TYPE_TIMER: EventType
EVENT_TYPE_PROVISIONING_REQUESTED: EventType
EVENT_TYPE_MQTT_CONNECTED: EventType
EVENT_TYPE_REBOOT_REQUESTED: EventType
EVENT_TYPE_BOOT_UNKNOWN: EventType
EVENT_TYPE_BOOT_SOFTWARE: EventType
EVENT_TYPE_BOOT_POWER_ON: EventType
EVENT_TYPE_BOOT_WATCHDOG: EventType

class Diagnostic(_message.Message):
    __slots__ = ("type", "uptime_s", "wifi_rssi_dbm", "device_info", "han_msg_successfully_parsed", "han_msg_buffer_overflow")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UPTIME_S_FIELD_NUMBER: _ClassVar[int]
    WIFI_RSSI_DBM_FIELD_NUMBER: _ClassVar[int]
    DEVICE_INFO_FIELD_NUMBER: _ClassVar[int]
    HAN_MSG_SUCCESSFULLY_PARSED_FIELD_NUMBER: _ClassVar[int]
    HAN_MSG_BUFFER_OVERFLOW_FIELD_NUMBER: _ClassVar[int]
    type: EventType
    uptime_s: int
    wifi_rssi_dbm: int
    device_info: _device_info_pb2.DeviceInfo
    han_msg_successfully_parsed: int
    han_msg_buffer_overflow: int
    def __init__(self, type: _Optional[_Union[EventType, str]] = ..., uptime_s: _Optional[int] = ..., wifi_rssi_dbm: _Optional[int] = ..., device_info: _Optional[_Union[_device_info_pb2.DeviceInfo, _Mapping]] = ..., han_msg_successfully_parsed: _Optional[int] = ..., han_msg_buffer_overflow: _Optional[int] = ...) -> None: ...

class Payload(_message.Message):
    __slots__ = ("sample", "diagnostic", "mac_address")
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    DIAGNOSTIC_FIELD_NUMBER: _ClassVar[int]
    MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    sample: _han_port_pb2.HanPortSample
    diagnostic: Diagnostic
    mac_address: bytes
    def __init__(self, sample: _Optional[_Union[_han_port_pb2.HanPortSample, _Mapping]] = ..., diagnostic: _Optional[_Union[Diagnostic, _Mapping]] = ..., mac_address: _Optional[bytes] = ...) -> None: ...
