import json
from datetime import datetime as dt
import random


def check_access_token(amo_access_token_expire,
                        amo_refresh_token,
                        amo_access_token,
                        amo_id,
                        amo_secret,
                        url,
                        redirect_uri,):
    from datetime import datetime as dt
    try:
        from amo import AmoControl
    except ModuleNotFoundError:
        from .amo import AmoControl
    if dt.now().timestamp() > amo_access_token_expire:
        ac = AmoControl(url, amo_id, amo_secret, amo_access_token)
        token_dict = ac.refresh_tokens(amo_id, amo_secret, amo_refresh_token, redirect_uri)
        token_dict['expires_in'] = dt.now().timestamp() + token_dict['expires_in']
        json.dump(token_dict, open('keys.json', 'w'))
        amo_access_token = token_dict['access_token']


def add_ten_contacts(ac):
    import names

    contacts = []
    for _ in range(10):
        contacts.append({'name': names.get_full_name()})

    ac.add_contacts(contacts)


def add_ten_leads(ac):
    contacts = ac.get_contacts()
    leads = []
    for contact in contacts[:10]:
        leads.append({'name': 'Pencils purchase', 'contacts_id': contact['id']})
    ac.add_leads(leads)


def create_email_custom_field(ac):
    custom_field_list = [
        {
            'name': 'email',
            'field_type': 1,
            'element_type': 1,
            'origin': amo_id,
        }
    ]
    return ac.create_custom_field(custom_field_list)


def add_emails_to_contacts(ac):
    import random
    from datetime import datetime as dt
    contacts = ac.get_contacts()
    email_field_id = [field['id'] for field in ac.get_contacts_fields() if field['name'] == "Email"][0]
    list_to_update = [{
        'id': contact['id'],
        'updated_at': dt.now().timestamp(),
        'custom_fields': [{'id': email_field_id,
                          'values': [
                              {'value': f"{contact['last_name']}{random.randint(10, 1000)}@gmail.com",
                               'enum': 'WORK'}]}]
    } for contact in contacts]
    ac.update_contacts(list_to_update)


def add_task_from_changed_leads(ac, a_base_manage):

    leads_in_base = a_base_manage.get_leads_dict()

    changed_leads = ac.check_leads_stages(leads_in_base)
    if changed_leads:
        if ac.add_task_from_leads(changed_leads):
            a_base_manage.update_changed_leads(changed_leads)


def send_mail_if_next_stage(ac, a_base_manage):

    leads_in_base = a_base_manage.get_all_leads()
    changed_leads = ac.check_leads_stages(a_base_manage.get_leads_dict())

    notes_to_add = []
    for lead in changed_leads:
        lead_in_base = None
        for b_lead in leads_in_base:
            if b_lead.amo_id == lead['id']:
                lead_in_base = b_lead
                leads_in_base.remove(b_lead)
                break
        prev_sort_inx = a_base_manage.get_status_sort_inx(lead_in_base.status_id)
        new_sort_inx = a_base_manage.get_status_sort_inx(lead['status_id'])
        if new_sort_inx > prev_sort_inx:
            contact = ac.get_contacts(lead['main_contact']['id'])
            meet_date = dt.now().replace(day=random.randint(1, 28))
            meet_address = "somewhere in Moscow"
            meet_duration = f"{random.randint(1, 3)} hours"
            meet_info_text = f"Meeting information: \n" \
                             f"Date: {meet_date.date()}\n" \
                             f"Time: {meet_date.time()}\n" \
                             f"Duration: {meet_duration}\n" \
                             f"Address: {meet_address}"
            msg = f"Hello, {contact['first_name']}! " + meet_info_text
            send_mail  # set mail server
            print(msg)
            notes_to_add.append(
                {
                    'element_id': contact['id'],
                    'element_type': 1,
                    'note_type': 4,
                    'text': meet_info_text
                }
            )
    if notes_to_add:
        ac.add_notes(notes_to_add)


def main():
    # check_access_token(amo_access_token_expire,
    #                    amo_refresh_token,
    #                    amo_access_token,
    #                    amo_id,
    #                    amo_secret,
    #                    url,
    #                    redirect_uri,)

    ac = AmoControl(url, amo_id, amo_secret, amo_access_token)
    create_db(basepath)
    session = create_session(basepath)
    a_base_manage = AmoStatusesManage(session)

    pipelines = ac.get_pipelines()

    a_base_manage.add_new_pipeline_statuses(pipelines)

    contacts = ac.get_contacts()
    if len(contacts) < 10:
        add_ten_contacts(ac)
        add_emails_to_contacts(ac)

    leads = ac.get_leads()
    if len(leads) < 10:
        add_ten_leads(ac)

    a_base_manage.add_new_leads(leads)

    send_mail_if_next_stage(ac, a_base_manage)

    add_task_from_changed_leads(ac, a_base_manage)

    notes = ac.get_notes()

    # print(notes)
    print(contacts[0])
    print(leads[0])


if __name__ == '__main__':
    from config import amo_id, amo_secret, amo_access_token, amo_refresh_token, url, basepath
    from config import amo_access_token_expire, redirect_uri
    from amo import AmoControl
    from base.models import create_db, create_session, AmoStatuses
    from base.basemanage import AmoStatusesManage
    from send_mail import send_mail
    main()
