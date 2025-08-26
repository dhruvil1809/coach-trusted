from core.users.tests.factories import ProfileFactory
from notifications.tests.factories import NotificationFactory


def run():
    profile = ProfileFactory()
    user = profile.user
    NotificationFactory.create_batch(100, to=user)
