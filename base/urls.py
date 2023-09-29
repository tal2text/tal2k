# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('transcribe/', views.transcriber, name='audio_list'),
    path('login/', views.login_view, name='login'),
    path('review/', views.reviewer, name='review'),
    path('', views.dashboard, name='dashboard'),

    path('transcribeme/<int:audio_id>/', views.transcribe_audio, name='transcribe'),
    path('transcriber/<int:transcriber_id>/', views.transcriber_details, name='transcriber_details'),

    path('get_transcriber_data/', views.get_transcriber_data, name='get_transcriber_data'),
    path('get_reviewer_data/', views.get_reviewer_data, name='get_reviewer_data'),


    
    path('upload_transcription/', views.upload_transcription, name='upload_transcription'),
    path('upload_multiple_audio/', views.upload_multiple_audio, name='upload_multiple_audio'),
    path('update_transcription/<int:audio_id>/', views.update_transcription, name='update_transcription'),
    path('update_transcription_review/<int:audio_id>/', views.update_transcription_review, name='update_transcription_review'),
    path('upload-audios/', views.upload_audios, name='upload_audios'),
    path('upload-folder/', views.upload_audio_folder, name='upload_audio_folder'),

    # path('update_status/<int:audio_id>/', views.update_transcript_status, name='update_transcript_status'),
    path('export_transcriptions/', views.export_transcriptions, name='export_transcriptions'),
    
    # path('test1/', views.test1),
    # path('test2/', views.test2),
    # path('test3/', views.test3),
    # path('test4/', views.test4),
    # path('test5/', views.test5, name='gladia_call_api'),
    # path('test6/', views.test6, name='duration'),

    path('testing/', views.testing, name='testing'),

]