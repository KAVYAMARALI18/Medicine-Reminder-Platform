import logging
from django.conf import settings

# Attempt to load firebase_admin if credentials exist
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    import os
    
    cred_path = os.path.join(settings.BASE_DIR, 'serviceAccountKey.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        FIREBASE_ENABLED = True
    else:
        FIREBASE_ENABLED = False
except ImportError:
    FIREBASE_ENABLED = False

logger = logging.getLogger(__name__)

def send_push_notification(user, title, body, data=None):
    """
    Sends a push notification to all active devices of the given user.
    """
    if data is None:
        data = {}
        
    devices = user.fcm_devices.filter(active=True)
    if not devices.exists():
        logger.warning(f"No active FCM devices found for user {user.username}")
        return False
        
    tokens = list(devices.values_list('registration_id', flat=True))
    
    if FIREBASE_ENABLED:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data,
            tokens=tokens,
        )
        try:
            response = messaging.send_multicast(message)
            logger.info(f"{response.success_count} messages were sent successfully.")
            return True
        except Exception as e:
            logger.error(f"Error sending FCM: {e}")
            return False
    else:
        # Mocked sender for development when no credentials exist
        logger.info(f"MOCKED FCM SEND to {user.username} ({len(tokens)} devices):")
        logger.info(f"Title: {title}")
        logger.info(f"Body: {body}")
        logger.info(f"Data: {data}")
        return True
