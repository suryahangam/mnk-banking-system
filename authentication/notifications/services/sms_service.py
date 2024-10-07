from django.conf import settings

import clicksend_client
from clicksend_client import SmsMessage
from clicksend_client.rest import ApiException


class SMSNotificationService:
    '''
    A service for sending SMS notifications using ClickSend API.

    This class allows sending SMS messages to a specified phone number.
    It initializes with the message content and recipient's phone number,
    and uses ClickSend's SMS API for sending messages.

    Attributes:
        message: The content of the SMS message to be sent.
        recipient_phone_number: The phone number of the recipient.
        configuration: ClickSend API configuration containing authentication details.


    documentation: https://developers.clicksend.com/docs/messaging/sms/#operation/send-sms
    '''

    def __init__(self, message, recipient_phone_number):
        # Initializes the SMSNotificationService with the message and recipient details.
        # message: The SMS message to send.
        # recipient_phone_number: The phone number of the recipient.

        self.message = message
        self.recipient_phone_number = recipient_phone_number

        self.configuration = clicksend_client.Configuration()
        self.configuration.username = settings.CLICKSEND_USERNAME
        self.configuration.password = settings.CLICKSEND_API_KEY

    def send(self):
        '''
        Sends the SMS message to the recipient.

        This method creates an SMS message object and sends it using the ClickSend API.
        It handles any exceptions that may occur during the sending process.

        If the message is sent successfully, a success message is printed.
        If there is an error, the exception is caught and an error message is printed.
        '''
        api_instance = clicksend_client.SMSApi(
            clicksend_client.ApiClient(self.configuration))

        sms_message = SmsMessage(source="Banking System", # TODO: better source name?
                                 body=self.message,
                                 to=self.recipient_phone_number)

        sms_messages = clicksend_client.SmsMessageCollection(messages=[
                                                             sms_message])

        try:
            api_response = api_instance.sms_send_post(sms_messages)
            print(f"2FA SMS sent successfully. Response: {api_response}")
        except ApiException as e:
            # TODO: log the exception
            print("Exception when calling SMSApi->sms_send_post: %s\n" % e)
