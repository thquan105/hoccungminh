from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    displayname = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    daily_question_limit = models.IntegerField(default=2)
    created_questions_today = models.IntegerField(default=0)
    last_reset = models.DateField(default=now)
    
    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.user.is_staff or self.user.is_superuser:
            self.is_premium = True
        super().save(*args, **kwargs)
    
    @property
    def name(self):
        if self.displayname:
            return self.displayname
        return self.user.username 
 
    @property
    def avatar(self):
        if self.image:
            return self.image.url
        return f'{settings.STATIC_URL}images/avatar.svg'