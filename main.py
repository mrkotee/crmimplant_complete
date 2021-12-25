from datetime import datetime as dt
from config import amo_id, amo_secret, amo_access_token, amo_refresh_token, url, basepath
from config import amo_access_token_expire, redirect_uri
from config import twilio_sid, twilio_secret, credential_list_sid, username, password, sip_domain, twilio_number
from twilioctrl.twilio_ctrl import TwilioControl
from amoctrl.amo import AmoControl
from amoctrl.base.models import create_db, create_session, AmoStatuses
from amoctrl.base.basemanage import AmoStatusesManage
from amoctrl.send_mail import send_mail
from amoctrl.main import check_access_token


def call_and_create_note(ac, twilio_control, twilio_number, contact):
    phone_number = [field['values'][0]['value']
                    for field in contact['custom_fields'] if field['name'] == "Phone"][0]
    if twilio_control.create_hello_call(phone_number, twilio_number):
        note_text = f"create a call. {dt.now()}"
        ac.add_notes(
            [{
                'element_id': contact['leads']['id'][0],
                'element_type': 2,
                'note_type': 11,
                'text': note_text
            }]
        )


def add_notes_to_inbound_calls(ac, twilio_control):

    contacts = ac.get_contacts()

    for call in twilio_control.get_call_list():
        if call.direction == 'inbound-api':
            for contact in contacts:
                phone_number = [field['values'][0]['value']
                                for field in contact['custom_fields'] if field['name'] == "Phone"][0]
                if call.from_ == phone_number:
                    note_text = f"receive a call. {call.date_created}"
                    ac.add_notes(
                        [{
                            'element_id': contact['leads']['id'][0],
                            'element_type': 2,
                            'note_type': 10,
                            'text': note_text
                        }]
                    )


def main():
    check_access_token(amo_access_token_expire,
                        amo_refresh_token,
                        amo_access_token,
                        amo_id,
                        amo_secret,
                        url,
                        redirect_uri,)
    ac = AmoControl(url, amo_id, amo_secret, amo_access_token)
    session = create_session(basepath)
    a_base_manage = AmoStatusesManage(session)
    twilio_control = TwilioControl(twilio_sid, twilio_secret)

    contacts = ac.get_contacts()

    call_and_create_note(ac, twilio_control, twilio_number, contacts[0])

    add_notes_to_inbound_calls(ac, twilio_control)


if __name__ == '__main__':
    main()
