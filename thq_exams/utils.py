from django.utils.timezone import now

def check_and_reset_luot_tao(profile):
    if profile.last_reset < now().date():
        profile.created_questions_today = 0
        profile.last_reset = now().date()
        profile.save()