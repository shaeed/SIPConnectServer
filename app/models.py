from typing import List, Optional

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str

class User(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=10,
        description="User name (SIP user name, will be used to login to Asterisk from clients like ZoiPer).",
        examples=["iram"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=30,
        description="Password to access the SIP server"
    )
    audio_interface: str = Field(
        ...,
        description="Dongle Audio interface. [Please use 'ls /dev/ttyUSB*' to identify the interface]",
        examples=["/dev/ttyUSB1"]
    )
    data_interface: str = Field(
        ...,
        description="Dongle data interface. (to send the commands to dongle). [Please use 'ls /dev/ttyUSB*' "
                    "to identify the interface]",
        examples=["/dev/ttyUSB2"]
    )
    voicemail_number: Optional[str] = Field(None, description="Voicemail number")

class TokenPayload(BaseModel):
    device_id: str
    fcm_token: str
    username: str

class DeviceResponse(BaseModel):
    fcm_token: str

class CallPayload(BaseModel):
    username: str
    phone_number: str
    type: Optional[str] = None # call, missed

class SmsPayload(BaseModel):
    username: str
    phone_number: str
    body: str
    device_id: Optional[str] = Field(
        None, description="Device id from which this sms is being sent. [Will be used to filter the "
                          "devices to forward the notification to other devices]")
    forward_to_gsm: Optional[bool] = Field(
        None, description="Indicate forwarding the message to gsm via firebase notification")

class RestartPayload(BaseModel):
    username: str
    device_id: str = Field(
        None, description="Device id from which this restart request was sent.")

class FirebaseResponse(BaseModel):
    status: int
    data: dict

class SmsLogEntry(BaseModel):
    id: int
    user: str
    number: str
    message: str
    sms_type: str
    timestamp: str

class CallLogEntry(BaseModel):
    id: int
    user: str
    number: str
    timestamp: str

class SmsLogsResponse(BaseModel):
    data: List[SmsLogEntry]

class CallLogsResponse(BaseModel):
    data: List[CallLogEntry]

class UserResponse(BaseModel):
    username: str
    audio_interface: str
    data_interface: str
    voicemail_number: Optional[str]

class ConfigResponse(BaseModel):
    sa_configured: bool
    project_id: str
