from django import forms
from .models import *
# forms.py
from django.forms.widgets import ClearableFileInput

class MultipleFileInput(ClearableFileInput):
    template_name = 'base/widgets/multiple_file_input.html'  # Path to your custom template

class AudioFileForm(forms.ModelForm):
    class Meta:
        model = AudioFile
        fields = ('title', 'audio_file')

class TranscriptionForm(forms.Form):
    transcription = forms.CharField(widget=forms.Textarea)


class UploadAudioForm(forms.Form):
    audio_files = forms.FileField(label='Upload Audio', widget=MultipleFileInput)
    transcription = forms.CharField(label='Transcription', widget=forms.Textarea, required=False)
    def __init__(self, *args, **kwargs):
        super(UploadAudioForm, self).__init__(*args, **kwargs)

        transcribers = User.objects.filter(groups__name='transcribers')
        transcriber_choices = [(user.id, user.username) for user in transcribers]
        reviewers = User.objects.filter(groups__name='reviewers')
        reviewers_choices = [(user.id, user.username) for user in reviewers]
    
        # Add the transcriber field with choices directly to the form
        self.fields['transcriber'] = forms.ChoiceField(choices=transcriber_choices, required=False)       
        self.fields['reviewer'] = forms.ChoiceField(choices=reviewers_choices, required=False)