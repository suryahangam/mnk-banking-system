import ssl
import threading
from smtplib import SMTP

from django.core.mail import send_mail
from django.conf import settings


class EmailNotificationServiceThread(threading.Thread):
    '''
    A thread that sends email notifications.

    This class allows for sending emails in a separate thread to avoid blocking 
    the main application flow. It uses the SMTP protocol with TLS encryption 
    for secure email transmission.

    Attributes:
        subject: The subject of the email.
        message: The body of the email.
        recipient_list: A list of email addresses to which the email will be sent.
    '''

    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        '''
        Executes the thread to send the email.

        This method is called when the thread is started. It establishes a connection
        to the SMTP server and sends the email using the provided subject, message, 
        and recipient list. 

        Note: SSL certificate verification is skipped for testing purposes.
        '''
        # Skips verification (only for testing!)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Send mail using the custom SSL context
        with SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
            smtp.starttls(context=context)  # Start TLS with our custom context
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            send_mail(
                self.subject,
                self.message,
                settings.EMAIL_HOST_USER,
                self.recipient_list,
                fail_silently=False,
            )
