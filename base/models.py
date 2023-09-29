from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from pydub import AudioSegment
from django.utils import timezone

class AudioFile(models.Model):
    Cat_choices = (
        ('Indian', 'Indian'),
        ('Philippino', 'Philippino'),
        )
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200,blank=True,null=True)
    audio_file = models.FileField(upload_to='', max_length=1024)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="uploaded_by")
    category = models.CharField(max_length=200, null=True,blank=True, choices=Cat_choices)
    audio_duration = models.DurationField(null=True, blank=True)
    to_be_reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="reviewer")
    def __str__(self) -> str:
        return f"Audio #{self.id}"

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         print(self.audio_file.path)
    #         if not self.audio_duration and self.audio_file:
    #             try:
    #                 audio = AudioSegment.from_file(self.audio_file.path)
    #                 duration_ms = len(audio)
    #                 seconds_duration = duration_ms / 1000.0  # Convert to seconds

    #                 if audio:
    #                     # Convert seconds_duration to a timedelta object
    #                     audio_duration = timezone.timedelta(seconds=seconds_duration)
    #                     self.audio_duration = audio_duration
    #                     print(audio_duration.total_seconds())  # Print the total duration in seconds
    #             except Exception as e:
    #                 print(f"Error while calculating audio duration: {e}")
    #     super().save(*args, **kwargs)
        
class TranscriptionEditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    edit_date = models.DateField(auto_now_add=True)
    num_edits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.edit_date}"

class Transcription(models.Model):
    STATUSES = (
        ('GOOD', 'GOOD'),
        ('BAD', 'BAD'),
        ('unverified','unverified'),
        )
    REVIEW_STATUSES = (
        ('GOOD', 'GOOD'),
        ('BAD', 'BAD'),
        ('unreviewed','unreviewed'),
        )
    status = models.CharField(max_length=200, null=True, choices=STATUSES, default='',blank=True)
    audio_file = models.OneToOneField(AudioFile, on_delete=models.CASCADE, null=True, blank=True)
    old_text = models.TextField(default='', blank=True, null=True)
    text = models.TextField()
    transcription_date = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(null=True, blank=True, default=False)
    review_status = models.CharField(max_length=200, null=True, choices=REVIEW_STATUSES, default='',blank=True)
    reviewed = models.BooleanField(null=True, blank=True, default=False)
    edit_log = models.ForeignKey(TranscriptionEditLog, on_delete=models.SET_NULL, null=True, blank=True)
    # reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)



