
dongle_header = """
[general]
interval=30
u2diag=-1
"""

dongle_template = """
[{dongle_id}]
audio={dongle_audio}  ; handles call audio
data={dongle_data}    ; handles control commands (AT)
imei=auto
imsi=auto
rssi=yes
context={dongle_context}
smscontext={dongle_smscontext}
group=0
rxgain=0
txgain=0
autodeletesms=yes
resetdongle=yes
"""

pjsip_header = """
[global]
type=global
endpoint_identifier_order=username,ip,anonymous

[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
"""

pjsip_template = """
[{pjsip_auth}]
type=auth
auth_type=userpass
username={pjsip_user}
password={pjsip_pass}

[{pjsip_user}]
type=aor
max_contacts=1
remove_existing=yes

[{pjsip_user}]
type=endpoint
transport=transport-udp
aors={pjsip_user}
auth={pjsip_auth}
context={pjsip_context}
disallow=all
allow=ulaw,alaw,gsm
direct_media=no
force_rport=yes
rewrite_contact=yes
rtp_symmetric=yes
rtcp_mux=yes
callerid={pjsip_callerid}<{pjsip_callerid}>
"""

extension_header = """
[general]
static=yes
writeprotect=no
clearglobalvars=no
"""

extension_template = """
[{ext_gsm_incoming}]
; === Incoming GSM call ===
exten => s,1,NoOp(Incoming GSM call from ${{CALLERID(num)}})
 same => n,Set(PHONE=${{CALLERID(num)}})
 same => n,System(curl -X POST http://localhost:8000/sip/alert/call -H "Content-Type: application/json" -d '{{"username": "{ext_sip_user}", "phone_number": "${{PHONE}}"}}')

 ; Wait loop: check Zoiper for up to 25 sec (2 sec interval)
 same => n,Set(TIMEOUT=25)
 same => n,Set(CHECK_INTERVAL=2)
 same => n,Set(ELAPSED=0)

 same => n(while_check),Set(STATUS=${{DEVICE_STATE(PJSIP/{ext_sip_user})}})
 same => n,NoOp(Current endpoint status: ${{STATUS}})
 same => n,GotoIf($["${{STATUS}}" = "NOT_INUSE"]?got_online)
 same => n,GotoIf($[${{ELAPSED}} >= ${{TIMEOUT}}]?fallback)
 same => n,Wait(${{CHECK_INTERVAL}})
 same => n,Set(ELAPSED=$[${{ELAPSED}} + ${{CHECK_INTERVAL}}])
 same => n,Goto(while_check)

; === If Zoiper comes online ===
 same => n(got_online),NoOp(Zoiper came online, dialing now)
 same => n,Dial(PJSIP/{ext_sip_user},20)
 same => n,GotoIf($["${{DIALSTATUS}}"="ANSWER"]?done)

; === If no answer, fallback ===
 same => n,NoOp(Zoiper did not answer or rejected call)
 same => n,Goto(fallback)

; === Fallback ===
 same => n(fallback),NoOp(Running fallback: push + voicemail)
 ; Missed call push
 same => n,System(curl -X POST http://localhost:8000/sip/alert/call -H "Content-Type: application/json" -d '{{"username": "{ext_sip_user}", "phone_number": "${{PHONE}}", "type": "missed"}}')
 ; Voicemail (make sure mailbox exists!)
 ;same => n,Voicemail({pjsip_callerid}@default,u)

 same => n(done),Hangup()

; Incoming SMS
exten => sms,1,NoOp(Incoming GSM SMS from ${{CALLERID(num)}} via {ext_dongle_id})
 same => n,Set(PHONE=${{CALLERID(num)}})
 same => n,Set(MESSAGE(body)=${{SMSMESSAGE}})
 same => n,System(curl -X POST http://localhost:8000/sip/alert/sms -H "Content-Type: application/json" -d '{{"username": "{ext_sip_user}", "phone_number": "${{PHONE}}", "body": "${{SMS}}"}}')
 same => n,NoOp(POST result: ${{RESULT}})
 same => n,MessageSend(pjsip:{ext_sip_user},sip:${{PHONE}}@localhost)
 same => n,Hangup()

; SMS delivery report (optional cleanup)
exten => report,1,Hangup()

[{ext_voip_incoming}]
; === Call to check own voicemail ===
;exten => *97,1,NoOp(Check Voicemail for current user)
; same => n,VoiceMailMain(${{CALLERID(num)}}@default)
; same => n,Hangup()

; Handle numbers with +91 prefix
exten => _+91X.,1,NoOp(Normalizing +91 number)
 same => n,Set(MYNUM=${{EXTEN:3}})         ; Strip +91
 same => n,GotoIf($["${{MESSAGE(body)}}" != ""]?{ext_gsm_outgoing_sms},${{MYNUM}},1)
 same => n,Goto({ext_gsm_outgoing},${{MYNUM}},1)

; Fallback for other + numbers (e.g., +1..., +44...) and Normal numbers without +
exten => _X.,1,GotoIf($["${{MESSAGE(body)}}" != ""]?{ext_gsm_outgoing_sms},${{EXTEN}},1)
 same => n,Goto({ext_gsm_outgoing},${{EXTEN}},1)

; === Voice call handler ===
[{ext_gsm_outgoing}]
exten => _X.,1,NoOp(Calling ${{EXTEN}} through {ext_dongle_id})
 same => n,Dial(Dongle/{ext_dongle_id}/${{EXTEN}},60)
 same => n,Hangup()

; === SMS handler === ZoiPer to GSM message
[{ext_gsm_outgoing_sms}]
exten => _X.,1,NoOp(Sending SMS to ${{EXTEN}} through {ext_dongle_id})
 same => n,System(/usr/sbin/asterisk -rx "dongle sms {ext_dongle_id} ${{EXTEN}} ${{MESSAGE(body)}}")
 same => n,Hangup()
"""
