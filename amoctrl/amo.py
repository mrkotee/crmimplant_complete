import requests
import json


class AmoControl:

    def __init__(self, url, amo_id, amo_secret, amo_access_token):
        self.main_url = url
        self._id = amo_id
        self.secret = amo_secret
        self.access_token = amo_access_token

    def _check_response_status_code(self, response):
        errors = {
            301: 'Moved permanently',
            400: 'Bad request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found',
            500: 'Internal server error',
            502: 'Bad gateway',
            503: 'Service unavailable'
        }

        if response.status_code == 200 or response.status_code == 204:
            try:
                return response.json()['_embedded']['items']
            except json.decoder.JSONDecodeError:
                return list()
        else:
            print(errors[response.status_code])
            return False

    def _send_data(self, url, data):
        headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/hal+json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        return self._check_response_status_code(response)

    def _get_data(self, url, data=None):
        headers = {'Authorization': f'Bearer {self.access_token}'}

        if data:
            response = requests.get(url, headers=headers, data=data)
        else:
            response = requests.get(url, headers=headers)

        return self._check_response_status_code(response)

    def refresh_tokens(self, client_id, client_secret, refresh_token, redirect_uri):
        url = self.main_url + '/oauth2/access_token'
        data = {'grant_type': 'refresh_token',
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'redirect_uri': redirect_uri}
        response = requests.post(url, data=data)
        return response.json()

    def create_custom_field(self, fields_list):
        url = self.main_url + '/api/v2/fields'
        data = {'add': fields_list}
        return self._send_data(url, data)

    def get_custom_fields(self):
        headers = {'Authorization': f'Bearer {self.access_token}'}
        url = self.main_url + '/api/v2/account' + "?with=custom_fields"
        response = requests.get(url, headers=headers)
        return response.json()['_embedded']['custom_fields']

    def get_contacts_fields(self):
        custom_fields = self.get_custom_fields()
        return custom_fields['contacts'].values()

    def add_contacts(self, contacts_list):
        url = self.main_url + '/api/v2/contacts'
        data = {'add': contacts_list}
        return self._send_data(url, data)

    def get_contacts(self, contact_id=None):
        url = self.main_url + '/api/v2/contacts'
        if contact_id:
            url += f"?id={contact_id}"
            return self._get_data(url)[0]
        else:
            return self._get_data(url)

    def update_contacts(self, contacts_list):
        url = self.main_url + '/api/v2/contacts'
        data = {'update': contacts_list}
        return self._send_data(url, data)

    def add_leads(self, leads_list):
        url = self.main_url + '/api/v2/leads'
        data = {'add': leads_list}
        return self._send_data(url, data)

    def get_leads(self):
        url = self.main_url + '/api/v2/leads'

        return self._get_data(url)

    def check_leads_stages(self, leads_in_base: dict):
        """

        :param leads_in_base: {lead_id: lead_status_id}
        :return: list with changed leads
        """
        actual_leads = self.get_leads()
        lead_with_new_statuses = []
        for lead in actual_leads:
            if lead['status_id'] != leads_in_base[lead['id']]:
                lead_with_new_statuses.append(lead)
        return lead_with_new_statuses

    def add_task_from_leads(self, leads_list):
        """
        create task with client name when lead change stage
        :param leads_in_base: {lead_id: lead_status_id}
        :return:
        """
        task_to_add = []
        url = self.main_url + '/api/v2/tasks'
        for lead in leads_list:
            contact = self.get_contacts(lead['main_contact']['id'])
            task_to_add.append({
                'element_id': f'{lead["id"]}',
                'element_type': 2,
                'text': f'{contact["name"]} has change stage',
                'task_type': 3,
            })
        return self._send_data(url, {'add': task_to_add})

    def get_pipelines(self):
        url = self.main_url + '/api/v2/pipelines'

        return self._get_data(url)

    def add_notes(self, notes_list):
        url = self.main_url + '/api/v2/notes'
        data = {'add': notes_list}
        return self._send_data(url, data)

    def get_notes(self):
        url = self.main_url + '/api/v2/notes'
        url += "?type=contact"

        return self._get_data(url)

