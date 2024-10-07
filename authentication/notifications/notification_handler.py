from .services.email_service import EmailNotificationServiceThread
from .services.sms_service import SMSNotificationService


class NotificationHandler:
    '''
    Handles sending notifications to users via email or SMS.

    This class allows the sending of notifications to a specified user 
    through their preferred communication method. The user can receive 
    notifications via email or SMS based on the provided parameters.

    Attributes:
        user: The user to whom the notification will be sent.
        message: The content of the notification message.
        subject: The subject of the notification (for email).
        notification_type: The type of notification ('email' or 'sms').
    '''

    def __init__(self, user, message, subject=None, notification_type='email'):
        self.user = user
        self.message = message
        self.subject = subject
        self.notification_type = notification_type

    def send(self):
        '''
        Sends the notification based on the specified notification type.

        Depending on the notification_type, this method will either 
        send an email using the EmailNotificationServiceThread or an 
        SMS using the SMSNotificationService. 

        Raises:
            ValueError: If an invalid notification type is provided.
        '''
        if self.notification_type == 'email':
            # Email notification service runs in a separate thread
            # to avoid blocking the main application.
            email_service = EmailNotificationServiceThread(
                subject=self.subject,
                message=self.message,
                recipient_list=[self.user.email]
            )
            email_service.start()

        elif self.notification_type == 'sms':
            # Uses third-party SMS service to send SMS notifications
            if self.user.mobile_number:
                sms_service = SMSNotificationService(
                    message=self.message,
                    recipient_phone_number=self.user.mobile_number
                )
                sms_service.send()

        else:
            raise ValueError(
                "Invalid notification type. Choose 'email' or 'sms'.")
