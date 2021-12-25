
from twilio_ctrl import TwilioControl
from config import twilio_sid, twilio_secret, credential_list_sid, username, password, sip_domain


def main():
    twilio_control = TwilioControl(twilio_sid, twilio_secret)

    available_numbers = twilio_control.get_available_numbers('US')

    new_number_sid = twilio_control.create_incoming_number(available_numbers[0])
    new_sip_domain_sid = twilio_control.create_sip_domain(sip_domain)
    new_credential_list_sid = twilio_control.create_credential_list('testlist')
    credential_sid = twilio_control.create_credential_resource(new_credential_list_sid, username, password)
    registration_sid = twilio_control.register_sip(sip_domain, credential_list_sid)
    # call = twilio_control.create_hello_call(to=f"sip:{username}@{sip_domain}", from_who="+15673027055")
    call = twilio_control.create_hello_call(to="+14154834991", from_who=available_numbers[0])
    print(call)


if __name__ == '__main__':
    main()
