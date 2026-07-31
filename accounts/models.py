from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)

from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name
from django.conf import settings
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name

class Case(models.Model):
    case_name = models.CharField(max_length=255)
    case_number = models.CharField(max_length=100, unique=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.case_number} - {self.case_name}"

class Evidence(models.Model):
    EVIDENCE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('digital', 'Digital Evidence'),
        ('audio', 'Audio'),  # ✅ Added 'audio' option
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='evidence/')
    type = models.CharField(max_length=10, choices=EVIDENCE_TYPES)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='evidence_viewers')

    def __str__(self):
        return f"{self.type} for {self.case.case_number}"


from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=100)
    face_image = models.ImageField(upload_to='faces/')
    voice_sample = models.FileField(upload_to='voices/', blank=True, null=True)

class MatchResult(models.Model):
    matched_person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
    uploaded_face = models.ImageField(upload_to='matches/faces/', blank=True, null=True)
    uploaded_voice = models.FileField(upload_to='matches/voices/', blank=True, null=True)
    matched_at = models.DateTimeField(auto_now_add=True)
