from typing import List

from app.asterisk_confi_template import dongle_header, dongle_template, pjsip_header, pjsip_template, extension_header, \
    extension_template

# Config file location
dongle_file = r'/etc/asterisk/dongle.conf'
pjsip_file = r'/etc/asterisk/pjsip.conf'
extension_file = r'/etc/asterisk/extensions.conf'

edit_section_identifier = r';******** Auto generated lines below ********'

def update_file(header: str, content: List[str], path: str, replace: bool = False):
    if replace:
        file_content = ''
    else:
        with open(path, 'r') as file:
            file_content = file.read()

    # get the default config lines
    if edit_section_identifier in file_content:
        file_content = file_content.split(edit_section_identifier)[0]

    if not header: header = ''
    content_to_write = [file_content, edit_section_identifier, header, *content]
    content_to_write = [x for x in content_to_write if x]
    file_content = '\n\n'.join(content_to_write)
    with open(path, 'w') as file:
        file.write(file_content)

def update_dongle():
    pass


def generate():
    user_name = "shaeed" # "sipuser"
    user_pass = "z*0&D$!bjscU07RU"
    dongle_id = f"dongle_{user_name}"
    dongle_audio = "/dev/ttyUSB1"
    dongle_data = "/dev/ttyUSB2"
    voicemail_id = "100"

    gsm_incoming = f"gsmin_{dongle_id}" # "from-dongle"
    voip_incoming = f"voipin_{user_name}" # "from-internal"
    gsm_outgoing = f"gsmout_{dongle_id}" # "donglecall"
    gsm_outgoing_sms = f"smsout_{dongle_id}" # "send-sms"

    variables = {
        "dongle_id": dongle_id,
        "dongle_audio": dongle_audio,
        "dongle_data": dongle_data,
        "dongle_context": gsm_incoming,
        "dongle_smscontext": gsm_incoming,

        "pjsip_auth": f"{user_name}_auth",
        "pjsip_user": user_name,
        "pjsip_pass": user_pass,
        "pjsip_context": voip_incoming,
        "pjsip_callerid": voicemail_id,

        "ext_gsm_incoming": gsm_incoming,
        "ext_sip_user": user_name,
        "ext_dongle_id": dongle_id,
        "ext_voip_incoming": voip_incoming,
        "ext_gsm_outgoing": gsm_outgoing,
        "ext_gsm_outgoing_sms": gsm_outgoing_sms,
    }

    configs = [dongle_header,
              dongle_template.format(**variables),
              pjsip_header,
              pjsip_template.format(**variables),
              extension_header,
              extension_template.format(**variables)]
    return '\r\n'.join(configs)

print(generate())