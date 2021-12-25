from twilio.rest import Client


class TwilioControl:

    def __init__(self, twilio_sid, twilio_secret):
        self.client = Client(twilio_sid, twilio_secret)

    def get_available_numbers(self, country_code):
        available_numbers = self.client.available_phone_numbers(country_code).fetch()

        return [phone.phone_number for phone in available_numbers.local.list()]

    def create_incoming_number(self, phone_number):
        incoming_number = self.client.incoming_phone_numbers.create(phone_number=phone_number)
        return incoming_number.sid

    def create_sip_domain(self, domain_name):
        """

        :param domain_name: "example.sip.twilioctrl.com"
        :return:
        """
        sip_domain = self.client.sip.domains.create(domain_name=domain_name)
        return sip_domain.sid

    def create_credential_list(self, name):
        credential_list = self.client.sip.credential_lists.create(
            friendly_name=name
        )
        return credential_list.sid

    def create_credential_resource(self, credential_list_sid, username, pswrd):
        credential = self.client.sip.credential_lists(credential_list_sid).\
            credentials.create(username, pswrd)
        return credential.sid

    def create_hello_call(self, to, from_who):
        call = self.client.calls.create(to, from_=from_who, twiml='<Response><Say>Hello srmimplant!</Say></Response>')
        return call.sid

    def register_sip(self, domain_sid, credential_list_sid):
        auth_registrations_credential_list_mapping = self.client.sip \
            .domains(domain_sid) \
            .auth \
            .registrations \
            .credential_list_mappings \
            .create(credential_list_sid=credential_list_sid)
        return auth_registrations_credential_list_mapping.sid

    def get_call_list(self):
        calls = self.client.calls.list()
        return calls

