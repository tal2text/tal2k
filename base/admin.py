from django.contrib import admin
from .models import *

class TranscriptionInline(admin.TabularInline):
    model = Transcription
    extra = 0  # Set the number of empty forms to display

class AudioFileAdmin(admin.ModelAdmin):
    # list_display = ('title', 'assigned_to', 'uploaded_at')
    inlines = [TranscriptionInline]
    search_fields = ('id', )

class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ('audio_file', 'text', 'status',)
    list_filter = ('status','edited')  # Add 'status' filter
    ordering = ('audio_file__id',)
    search_fields = ('text','audio_file__id' )

admin.site.register(AudioFile, AudioFileAdmin)
admin.site.register(Transcription, TranscriptionAdmin)
admin.site.register(TranscriptionEditLog)