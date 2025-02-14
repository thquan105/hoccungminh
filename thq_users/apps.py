from django.apps import AppConfig


class ThqUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'thq_users'

    def ready(self):
        import thq_users.signals