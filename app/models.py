from typing import Optional

from pydantic import BaseModel, Field


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
    sip_user: str

class CallPayload(BaseModel):
    sip_user: str
    phone_number: str
    type: Optional[str] = None

class SmsPayload(BaseModel):
    sip_user: str
    phone_number: str
    body: str
    device_id: Optional[str] = Field(
        None, description="Device id from which this sms is being sent. [Will be used to filter the "
                          "devices to forward the notification to other devices]")
