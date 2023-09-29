from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from django.template.loader import render_to_string
from datetime import date
from .models import *
from .forms import *
import os, tempfile, zipfile, json, requests
from django.contrib.auth import authenticate, login
from django.contrib import messages
from online_users.models import OnlineUserActivity
from pydub import AudioSegment

from django.db.models import Sum, ExpressionWrapper, F, fields
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.shortcuts import render, get_object_or_404

from datetime import timedelta

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
            if user.groups.filter(name='transcribers').exists():
                # Redirect transcribers to a specific page
                return redirect('audio_list')
            elif user.groups.filter(name='reviewers').exists():
                return redirect('review')

            return redirect('dashboard') 
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'base/login.html')

def reviewer(request):
    # audio_files = AudioFile.objects.all()
    # total_count = audio_files.count()
    # half_count = total_count // 2  # Calculate the midpoint

    # # Divide the queryset into two parts
    # part1 = audio_files[:half_count]
    # part2 = audio_files[half_count:]

    # # Set 'to_be_reviewed_by' for each part
    # for audio in part1:
    #     audio.to_be_reviewed_by = User.objects.get(username='lea')
    #     audio.save()

    # for audio in part2:
    #     audio.to_be_reviewed_by = User.objects.get(username='stephanie')
    #     audio.save()
    selected_status = request.GET.get('status', '')
    audio_files = AudioFile.objects.all().filter(to_be_reviewed_by=request.user).order_by("-id")

    done_duration_timedelta = timezone.timedelta(seconds=0)
    left_duration_timedelta = timezone.timedelta(seconds=0)
    total_duration_timedelta = timezone.timedelta(seconds=0)
    
    for audio_file in audio_files:
        audio_duration = audio_file.audio_duration

        if audio_duration is not None:
            if audio_file.transcription.review_status in ['GOOD', 'BAD']:
                done_duration_timedelta += audio_duration

            if audio_file.transcription.review_status in ['unreviewed', '']:
                left_duration_timedelta += audio_duration

            total_duration_timedelta += audio_duration

    done_duration_formatted = format_duration(done_duration_timedelta)
    left_duration_formatted = format_duration(left_duration_timedelta)
    total_duration_formatted = format_duration(total_duration_timedelta)

    if not selected_status:
        audio_files = AudioFile.objects.all().filter(to_be_reviewed_by=request.user).order_by("-id")
    else:
        if selected_status != "unverified"  :
            audio_files = audio_files.filter(transcription__status=selected_status).order_by("-id")
        elif selected_status == "unverified":
            audio_files = audio_files.filter(Q(transcription__status = "") | Q(transcription__status="unverified")).order_by("-id")
        
    page_number = request.GET.get('page')
    paginator = Paginator(audio_files, 30)  # Show 60 audio files per page
    audio_files = paginator.get_page(page_number)
    edit_log  = TranscriptionEditLog.objects.all().first()
    context = {
        'audio_files': audio_files,
        'selected_status':selected_status,
        'editlog':edit_log,
        'done_duration_formatted': done_duration_formatted,
        'left_duration_formatted': left_duration_formatted,
        'total_duration_formatted': total_duration_formatted,
        'name':'review'
        
    }
    return render(request, 'base/audio_list_reviewers.html', context)


def format_duration(duration):
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    formatted_duration = ""
    
    if hours > 0:
        formatted_duration += f"{hours}h "
    
    if minutes > 0:
        formatted_duration += f"{minutes}m "
    
    formatted_duration += f"{seconds}s"
    
    return formatted_duration


import os

from django.core.files import File
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def test1(request):
    directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transcriber1')
    print(directory_path)
    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # Get a list of all files in the directory
        files = os.listdir(directory_path)

        for file_name in files:
            # Create a new instance of the AudioFile model
            audio = AudioFile()
            audio.assigned_to = User.objects.get(id=4)  # Replace with the appropriate user
            audio.title = file_name  # Set the title to the file name
            audio.audio_duration = None  # Set the audio duration as needed

            # Open and save the audio file
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'rb') as file:
                audio.audio_file.save(file_name, File(file), save=False)

            audio.save()
        return JsonResponse({'message': 'Audio files imported successfully'})
    else:
        return JsonResponse({'message': 'Directory "transcriber1" not found'}, status=404)

def test2(request):
    directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transcriber2')
    print(directory_path)
    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # Get a list of all files in the directory
        files = os.listdir(directory_path)

        for file_name in files:
            # Create a new instance of the AudioFile model
            audio = AudioFile()
            audio.assigned_to = User.objects.get(id=5)  # Replace with the appropriate user
            audio.title = file_name  # Set the title to the file name
            audio.audio_duration = None  # Set the audio duration as needed

            # Open and save the audio file
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'rb') as file:
                audio.audio_file.save(file_name, File(file), save=False)

            audio.save()
        return JsonResponse({'message': 'Audio files imported successfully'})
    else:
        return JsonResponse({'message': 'Directory "transcriber1" not found'}, status=404)

def test3(request):
    directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transcriber3')
    print(directory_path)
    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # Get a list of all files in the directory
        files = os.listdir(directory_path)

        for file_name in files:
            # Create a new instance of the AudioFile model
            audio = AudioFile()
            audio.assigned_to = User.objects.get(id=6)  # Replace with the appropriate user
            audio.title = file_name  # Set the title to the file name
            audio.audio_duration = None  # Set the audio duration as needed

            # Open and save the audio file
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'rb') as file:
                audio.audio_file.save(file_name, File(file), save=False)

            audio.save()
        return JsonResponse({'message': 'Audio files imported successfully'})
    else:
        return JsonResponse({'message': 'Directory "transcriber1" not found'}, status=404)

def test4(request):
    directory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transcriber4')
    print(directory_path)
    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # Get a list of all files in the directory
        files = os.listdir(directory_path)

        for file_name in files:
            # Create a new instance of the AudioFile model
            audio = AudioFile()
            audio.assigned_to = User.objects.get(id=7)  # Replace with the appropriate user
            audio.title = file_name  # Set the title to the file name
            audio.audio_duration = None  # Set the audio duration as needed

            # Open and save the audio file
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'rb') as file:
                audio.audio_file.save(file_name, File(file), save=False)

            audio.save()
        return JsonResponse({'message': 'Audio files imported successfully'})
    else:
        return JsonResponse({'message': 'Directory "transcriber1" not found'}, status=404)
from django.core.exceptions import ObjectDoesNotExist

def test5(request):
    try:
        # audios = AudioFile.objects.all()[:25]
        audios = AudioFile.objects.filter(transcription__isnull=True)[:10]

        for audio in audios:
            try:
                transcription = audio.transcription  # Try to access the associated Transcription object
            except ObjectDoesNotExist:
                # Handle the case where the Transcription object doesn't exist
                transcription = None 
            if transcription is None:
                audio_url = audio.audio_file.url
                result_text = transcribe_audio(audio_url)
                # Create or update a Transcription object associated with the AudioFile
                transcription, created = Transcription.objects.get_or_create(audio_file=audio)
                transcription.text = result_text
                transcription.save() 
        return JsonResponse({'message': 'Done'})
    except:
        return JsonResponse({'message': 'Try again'})

def test6(request):
    audios = AudioFile.objects.all()
    for audio in audios:
        if audio.audio_file and not audio.audio_duration:
            try:
                audio_segment = AudioSegment.from_file(audio.audio_file.path)
                duration_ms = len(audio_segment)
                seconds_duration = duration_ms / 1000.0  # Convert to seconds

                if audio_segment:
                    # Convert seconds_duration to a timedelta object
                    audio_duration = timezone.timedelta(seconds=seconds_duration)
                    audio.audio_duration = audio_duration
                    audio.save()  # Save the instance with the calculated duration
            except Exception as e:
                return JsonResponse({'message': f'Error while calculating audio duration: {e}'})

def dashboard(request):
    num_audios_tobetranscribed = AudioFile.objects.all().filter(transcription__status__in=['unverified', '']).count()
    num_audios_tobereviewed = AudioFile.objects.all().filter(transcription__reviewed__in=['False', ''], transcription__status__in=['GOOD', 'BAD']).count()
    all_audios = AudioFile.objects.all().count()
    num_good_transcription = AudioFile.objects.all().filter(transcription__status='GOOD').count()
    num_bad_transcription = AudioFile.objects.all().filter(transcription__status='BAD').count()
    print(num_bad_transcription)
    num_unverified_transcription = AudioFile.objects.all().filter(transcription__status__in=['unverified', '']).count()


    transcribers = User.objects.filter(groups__name='transcribers')
    reviewers = User.objects.filter(groups__name='reviewers')

    num_transcribers = User.objects.filter(groups__name='transcribers').count()
    num_reviewers = User.objects.filter(groups__name='reviewers').count()

    transcriber_counts = []
    for transcriber in transcribers:
        audio_files = transcriber.audiofile_set.all()
        done_duration_timedelta = timezone.timedelta(seconds=0)
        left_duration_timedelta = timezone.timedelta(seconds=0)
        total_duration_timedelta = timezone.timedelta(seconds=0)

        for audio_file in audio_files:
            audio_duration = audio_file.audio_duration

            if audio_duration is not None:
                if audio_file.transcription.status in ['GOOD', 'BAD']:
                    done_duration_timedelta += audio_duration

                if audio_file.transcription.status in ['unverified', '']:
                    left_duration_timedelta += audio_duration

                total_duration_timedelta += audio_duration

        done_duration_formatted = format_duration(done_duration_timedelta)
        left_duration_formatted = format_duration(left_duration_timedelta)
        total_duration_formatted = format_duration(total_duration_timedelta)

        is_online = OnlineUserActivity.objects.filter(user=transcriber, last_activity__gte=timezone.now() - timezone.timedelta(minutes=15)).exists()

        transcriber_data = {
            'transcriber': transcriber,
            'audio_files_done': audio_files.filter(transcription__status__in=['GOOD', 'BAD']).count(),
            'audio_files_left': audio_files.filter(transcription__status__in=['unverified', '']).count(),
            'audio_files_total': audio_files.count(),
            'done_duration_timedelta': done_duration_formatted,
            'left_duration_timedelta': left_duration_formatted,
            'total_duration_timedelta': total_duration_formatted,
            'is_online': is_online,  
        }

        transcriber_counts.append(transcriber_data)

    selected_status = request.GET.get('status', '')
    audio_files = AudioFile.objects.all().filter(uploaded_by=request.user).order_by("-id")
    if not selected_status:
        audio_files = AudioFile.objects.all().filter(uploaded_by=request.user).order_by("-id")
    else:
        if selected_status != "unverified"  :
            audio_files = audio_files.filter(transcription__status=selected_status).order_by("-id")
        elif selected_status == "unverified":
            audio_files = audio_files.filter(Q(transcription__status = "") | Q(transcription__status="unverified")).order_by("-id")
        
    page_number = request.GET.get('page')
    paginator = Paginator(audio_files, 60)  # Show 10 audio files per page
    audio_files = paginator.get_page(page_number)
    edit_log  = TranscriptionEditLog.objects.all().first()

    user_activity_objects = OnlineUserActivity.get_user_activities()
    number_of_active_users = user_activity_objects.count()
    context = {
        'audio_files': audio_files,
        'selected_status':selected_status,
        'editlog':edit_log,
        'transcribers':transcribers,
        'reviewers':reviewers,
        'transcriber_counts':transcriber_counts,
        'num_audios_tobetranscribed':num_audios_tobetranscribed,
        'num_audios_tobereviewed': num_audios_tobereviewed,
        'num_transcribers': num_transcribers,
        'num_reviewers': num_reviewers,
        'number_of_active_users':number_of_active_users,
        'all_audios': all_audios,
        'num_good_transcription':num_good_transcription,
        'num_bad_transcription':num_bad_transcription,
        'num_unverified_transcription': num_unverified_transcription,
        'name':'dashboard'
        
            
        }
    return render(request, 'base/dashboard.html', context)

def transcriber_details(request, transcriber_id):
    # Retrieve the Transcriber object with the given ID or return a 404 if not found
    transcriber = get_object_or_404(User, id=transcriber_id)
    is_online = OnlineUserActivity.objects.filter(user=transcriber, last_activity__gte=timezone.now() - timezone.timedelta(minutes=15)).exists()

    transription_audio_files = AudioFile.objects.filter(assigned_to=transcriber).order_by('-id')
    review_audio_files = AudioFile.objects.filter(to_be_reviewed_by=transcriber).order_by('-id')

    review_done_duration_timedelta = timezone.timedelta(seconds=0)
    review_left_duration_timedelta = timezone.timedelta(seconds=0)
    review_total_duration_timedelta = timezone.timedelta(seconds=0)

    for audio_file in review_audio_files:
        audio_duration = audio_file.audio_duration

        if audio_duration is not None:
            if audio_file.transcription.review_status in ['GOOD', 'BAD']:
                review_done_duration_timedelta += audio_duration

            if audio_file.transcription.review_status in ['unreviewed', '']:
                review_left_duration_timedelta += audio_duration

            review_total_duration_timedelta += audio_duration

    review_done_duration_formatted = format_duration(review_done_duration_timedelta)
    review_left_duration_formatted = format_duration(review_left_duration_timedelta)
    review_total_duration_formatted = format_duration(review_total_duration_timedelta)


    done_duration_timedelta = timezone.timedelta(seconds=0)
    left_duration_timedelta = timezone.timedelta(seconds=0)
    total_duration_timedelta = timezone.timedelta(seconds=0)
    
    for audio_file in transription_audio_files:
        audio_duration = audio_file.audio_duration

        if audio_duration is not None:
            if audio_file.transcription.status in ['GOOD', 'BAD']:
                done_duration_timedelta += audio_duration

            if audio_file.transcription.status in ['unverified', '']:
                left_duration_timedelta += audio_duration

            total_duration_timedelta += audio_duration

    done_duration_formatted = format_duration(done_duration_timedelta)
    left_duration_formatted = format_duration(left_duration_timedelta)
    total_duration_formatted = format_duration(total_duration_timedelta)

    all_audios = transription_audio_files.count()
    num_of_good = transription_audio_files.filter(transcription__review_status= "GOOD").count()
    num_of_bad = transription_audio_files.filter(transcription__review_status= "BAD").count()
    percentage = num_of_good/ all_audios
    
    page_number = request.GET.get('page')
    paginator = Paginator(transription_audio_files, 10)  # Show 10 audio files per page
    transription_audio_files = paginator.get_page(page_number)
    context ={
        'transcriber': transcriber,
        'transription_audio_files': transription_audio_files,
        
        'done_duration_formatted': done_duration_formatted,
        'left_duration_formatted': left_duration_formatted,
        'total_duration_formatted': total_duration_formatted,
        
        'review_done_duration_formatted':review_done_duration_formatted,
        'review_left_duration_formatted':review_left_duration_formatted,
        'review_total_duration_formatted':review_total_duration_formatted,
        
        'is_online': is_online,
        'num_of_good': num_of_good,
        'num_of_bad': num_of_bad,
        'percentage': percentage,
                'name':'detail',

    }
    return render(request, 'base/transcriber_details.html', context)

def get_reviewer_data(request):

    audio_files = AudioFile.objects.all().filter(to_be_reviewed_by=request.user).order_by("-id")
    print("whhahaht")
    done_duration_timedelta = timezone.timedelta(seconds=0)
    left_duration_timedelta = timezone.timedelta(seconds=0)
    total_duration_timedelta = timezone.timedelta(seconds=0)
    
    for audio_file in audio_files:
        audio_duration = audio_file.audio_duration

        if audio_duration is not None:
            if audio_file.transcription.review_status in ['GOOD', 'BAD']:
                done_duration_timedelta += audio_duration

            if audio_file.transcription.review_status in ['unreviewed', '']:
                left_duration_timedelta += audio_duration

            total_duration_timedelta += audio_duration


    data = {
        'done_duration_formatted': format_duration(done_duration_timedelta),
        'left_duration_formatted': format_duration(left_duration_timedelta),
        'total_duration_formatted': format_duration(total_duration_timedelta),
    }
    
    print(data)
    return JsonResponse(data)


def get_transcriber_data(request):

    audio_files = AudioFile.objects.all().filter(assigned_to=request.user).order_by("-id")
    print("whhahaht")
    done_duration_timedelta = timezone.timedelta(seconds=0)
    left_duration_timedelta = timezone.timedelta(seconds=0)
    total_duration_timedelta = timezone.timedelta(seconds=0)
    
    for audio_file in audio_files:
        audio_duration = audio_file.audio_duration

        if audio_duration is not None:
            if audio_file.transcription.status in ['GOOD', 'BAD']:
                done_duration_timedelta += audio_duration

            if audio_file.transcription.status in ['unverified', '']:
                left_duration_timedelta += audio_duration

            total_duration_timedelta += audio_duration


    data = {
        'done_duration_formatted': format_duration(done_duration_timedelta),
        'left_duration_formatted': format_duration(left_duration_timedelta),
        'total_duration_formatted': format_duration(total_duration_timedelta),
    }
    
    print(data)
    return JsonResponse(data)

def transcriber(request):
    selected_status = request.GET.get('status', '')
    audio_files = AudioFile.objects.all().filter(assigned_to=request.user).order_by("-id")

    done_duration_timedelta = timezone.timedelta(seconds=0)
    left_duration_timedelta = timezone.timedelta(seconds=0)
    total_duration_timedelta = timezone.timedelta(seconds=0)
    
    for audio_file in audio_files:
        audio_duration = audio_file.audio_duration

        if audio_duration is not None:
            if audio_file.transcription.status in ['GOOD', 'BAD']:
                done_duration_timedelta += audio_duration

            if audio_file.transcription.status in ['unverified', '']:
                left_duration_timedelta += audio_duration

            total_duration_timedelta += audio_duration

    done_duration_formatted = format_duration(done_duration_timedelta)
    left_duration_formatted = format_duration(left_duration_timedelta)
    total_duration_formatted = format_duration(total_duration_timedelta)

    if not selected_status:
        audio_files = AudioFile.objects.all().filter(assigned_to=request.user).order_by("-id")
    else:
        if selected_status != "unverified"  :
            audio_files = audio_files.filter(transcription__status=selected_status).order_by("-id")
        elif selected_status == "unverified":
            audio_files = audio_files.filter(Q(transcription__status = "") | Q(transcription__status="unverified")).order_by("-id")
        
    page_number = request.GET.get('page')
    paginator = Paginator(audio_files, 10)  # Show 10 audio files per page
    audio_files = paginator.get_page(page_number)
    edit_log  = TranscriptionEditLog.objects.all().first()
    context = {
        'audio_files': audio_files,
        'selected_status':selected_status,
        'editlog':edit_log,
        'done_duration_formatted': done_duration_formatted,
        'left_duration_formatted': left_duration_formatted,
        'total_duration_formatted': total_duration_formatted,
        'name':'transcribe'
    }
    return render(request, 'base/audio_list_transcribers.html', context)



def audio_list(request):
    # if request.user.groups.filter(name='transcribers').exists():
    selected_status = request.GET.get('status', '')
    audio_files = AudioFile.objects.all().filter(assigned_to=request.user).order_by("-id")
    if not selected_status:
        audio_files = AudioFile.objects.all().filter(assigned_to=request.user).order_by("-id")
    else:
        if selected_status != "unverified"  :
            audio_files = audio_files.filter(transcription__status=selected_status).order_by("-id")
        elif selected_status == "unverified":
            audio_files = audio_files.filter(Q(transcription__status = "") | Q(transcription__status="unverified")).order_by("-id")
        
    page_number = request.GET.get('page')
    paginator = Paginator(audio_files, 10)  # Show 10 audio files per page
    audio_files = paginator.get_page(page_number)
    edit_log  = TranscriptionEditLog.objects.all().first()
    return render(request, 'base/audio_list_transcribers.html', {'audio_files': audio_files,'selected_status':selected_status,'editlog':edit_log})

def upload_audios(request):
    transcribers = User.objects.filter(groups__name='transcribers')
    reviewers = User.objects.filter(groups__name='reviewers')
    if request.method == 'POST':
        form = UploadAudioForm(request.POST, request.FILES)
        if form.is_valid():
            audio = form.save(commit=False)
            audio.user = request.user
            audio.save()
            return redirect('audio_list')
    else:
        form = UploadAudioForm()
    return render(request, 'base/upload_audio.html', {'form': form,'transcribers':transcribers,'reviewers':reviewers,'type':"files"})

def upload_audio_folder(request):
    transcribers = User.objects.filter(groups__name='transcribers')
    reviewers = User.objects.filter(groups__name='reviewers')
    if request.method == 'POST':
        form = UploadAudioForm(request.POST, request.FILES)
        if form.is_valid():
            audio = form.save(commit=False)
            audio.user = request.user
            audio.save()
            return redirect('audio_list')
    else:
        form = UploadAudioForm()
    return render(request, 'base/upload_audio.html', {'form': form,'transcribers':transcribers,'reviewers':reviewers,'type':"folder"})


# def test(request):
#     start_id = 12216
#     end_id = 13016

#     # Query the database to get audio files within the specified range of IDs
#     audio_files = AudioFile.objects.filter(id__range=(start_id, end_id))

#     total_duration_seconds = 0.0

#     for audio in audio_files:
#         if audio.audio_file:
#             # Calculate the duration of each audio file and add it to the total
#             audio_segment = AudioSegment.from_file(audio.audio_file.path)
#             total_duration_seconds += audio_segment.duration_seconds

#     # Convert the total duration to a more human-readable format (e.g., hours, minutes, seconds)
#     total_duration = str(int(total_duration_seconds // 3600)).zfill(2) + ":" + str(int((total_duration_seconds // 60) % 60)).zfill(2) + ":" + str(int(total_duration_seconds % 60)).zfill(2)

#     print(f"Total duration of audio files between IDs {start_id} and {end_id}: {total_duration}")

#     return render(request, 'base/upload_audio.html')

def update_transcription(request, audio_id):
    if request.method == 'POST':
        new_transcription = request.POST.get('newTranscription')
        # Update the transcription for the specified audio_id
        try:
            audio = AudioFile.objects.get(id=audio_id)
            user = User.objects.get(id=2)
            if audio.transcription.edit_log is None:
            # Create a new edit log entry if it doesn't exist
                edit_log, created = TranscriptionEditLog.objects.get_or_create(user=user, edit_date=date.today())
                audio.transcription.edit_log = edit_log
                audio.transcription.save()
            else:
                edit_log = audio.transcription.edit_log
            
            if audio.transcription.text == new_transcription:
                if audio.transcription.status == "BAD":
                    audio.transcription.edited = True
                    audio.transcription.status = "BAD"
                elif audio.transcription.status == 'unverified':
                    audio.transcription.edited = None
                    audio.transcription.status = "unverified"
                else:
                    audio.transcription.edited = False
                    audio.transcription.status = "GOOD"
                    edit_log.num_edits += 1
                    edit_log.save()

            else:
                audio.transcription.edited = True
                audio.transcription.status = "BAD"
                edit_log.num_edits += 1
                edit_log.save()
            audio.transcription.text = new_transcription
            audio.transcription.save()
            
            # edit_log.num_edits += 1
            # edit_log.save()
            return JsonResponse({'success': True})
        except AudioFile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Audio not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def update_transcription_review(request, audio_id):
    if request.method == 'POST':
        new_transcription = request.POST.get('newTranscription')
        # Update the transcription for the specified audio_id
        try:
            audio = AudioFile.objects.get(id=audio_id)

            if audio.transcription.text == new_transcription:
                audio.transcription.reviewed = True
                audio.transcription.review_status = 'GOOD'


            else:
                audio.transcription.reviewed = True
                audio.transcription.review_status = 'BAD'

            audio.transcription.text = new_transcription
            audio.transcription.save()
            
            return JsonResponse({'success': True})
        except AudioFile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Audio not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


    
# def transcribe_audio(request, audio_id):
#     audio = AudioFile.objects.get(id=audio_id)

#     form = TranscriptionForm(request.POST or None)
#     if form.is_valid():
#         transcription_text = form.cleaned_data['transcription']
#         # Save the transcription, you can use the 'audio' object to link it
#         Transcription.objects.create(audio_file=audio, text=transcription_text)

#     context = {'audio': audio, 'form': form}
#     return render(request, 'base/transcribe_audio.html', context)


@login_required  # Ensure the user is authenticated
def upload_transcription(request):
    if request.method == 'POST':
        form = UploadAudioForm(request.POST, request.FILES)
        if form.is_valid():
            audio = AudioFile.objects.create(user=request.user, audio_file=form.cleaned_data['audio_file'])
            transcription_text = form.cleaned_data['transcription']
            Transcription.objects.create(audio_file=audio, text=transcription_text)
            return redirect('audio_list')  # Redirect to audio list page after successful upload and transcription
    else:
        form = UploadAudioForm()
    return render(request, 'base/upload_transcription.html', {'form': form})


def upload_multiple_audio(request):
    if request.method == 'POST':
        form = UploadAudioForm(request.POST, request.FILES)
        if form.is_valid():
            transcriber_id = form.cleaned_data['transcriber']
            reviewer_id = form.cleaned_data['reviewer']
            audio_files = request.FILES.getlist('audio_files')
            assigned_who = User.objects.get(id=transcriber_id)
            reviewer_who = User.objects.get(id=reviewer_id)
            result_text = [] 
            for audio_file in audio_files:
                if isinstance(audio_file, InMemoryUploadedFile):
                    audio = AudioFile.objects.create(audio_file=audio_file, assigned_to=assigned_who, uploaded_by=request.user, to_be_reviewed_by=reviewer_who )
                    if audio.audio_file:
                        try:
                            audio_segment = AudioSegment.from_file(audio.audio_file.path)
                            duration_ms = len(audio_segment)
                            seconds_duration = duration_ms / 1000.0  # Convert to seconds

                            if audio_segment:
                                # Convert seconds_duration to a timedelta object
                                audio_duration = timezone.timedelta(seconds=seconds_duration)
                                audio.audio_duration = audio_duration
                                audio.save()  # Save the instance with the calculated duration
                        except Exception as e:
                            print(f"Error while calculating audio duration: {e}")
                    audio_url = audio.audio_file.url
                    result_text = transcribe_audio(audio_url)
                    # Create or update a Transcription object associated with the AudioFile
                    transcription, created = Transcription.objects.get_or_create(audio_file=audio)
                    transcription.text = result_text
                    transcription.save()  # Save the transcription with the transcribed text
            
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            print(form.errors)
    else:
        form = UploadAudioForm()
    return render(request, 'base/audio_list_reviewers.html', {'audio_files': AudioFile.objects.all(), 'form': form})


def transcribe_audio(audio_url):
    headers = {
        'x-gladia-key': 'dc0b43d7-49a5-4a4d-af4b-427aa8c512c5',
    }
    # print("https://app.tal2text.com"+audio_url)
    files = {
        'audio_url': (None,"https://app.tal2text.com" + audio_url),
        'language_behaviour': (None, 'automatic single language'),
        'toggle_chapterization': (None, 'false'),
        'toggle_diarization': (None, 'true'),
        'toggle_direct_translate': (None, 'false'),
        'toggle_noise_reduction': (None, 'false'),
        'toggle_summarization': (None, 'false'),
        'toggle_text_emotion_recognition': (None, 'false'),
    }

    response = requests.post('https://api.gladia.io/audio/text/audio-transcription/', headers=headers, files=files)
    response_json = response.json()
    print("Response Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("Response Content:")
    print(response.text)    # Extract and concatenate words
    concatenated_words = []
    result_text = ""  # Initialize result_text as an empty string

    if 'prediction' in response_json:
        for prediction in response_json['prediction']:
            if 'transcription' in prediction:
                result_text += prediction['transcription']
    
    return result_text


def testing(request):
    # Retrieve audio URLs and related AudioFile objects from the database
    audio_files = AudioFile.objects.all()[:5]

    transcriptions = {}
    
    for audio_file in audio_files:
        audio_url = audio_file.audio_file.url
        result_text = transcribe_audio(audio_url)
        transcriptions[audio_url] = result_text
    
    # You now have a dictionary where keys are audio URLs and values are transcriptions
    # You can associate these transcriptions with the corresponding AudioFile objects
    
    for audio_url, result_text in transcriptions.items():
        audiof = AudioFile.objects.filter(audio_file__icontains=audio_url).first()
        if audiof:
            # Create or update a Transcription object associated with the AudioFile
            transcription, created = Transcription.objects.get_or_create(audio_file=audiof)
            transcription.text = result_text
            transcription.save()

    return render(request, 'base/test.html')


import os
import tempfile
import zipfile
from django.http import HttpResponse
from django.conf import settings

def export_transcriptions(request):
    # Specify the absolute path to your desired directory
    custom_dir = os.path.join(settings.BASE_DIR, 'static/')
    print(custom_dir)
    # Create a temporary directory inside the specified directory
    temp_dir = tempfile.mkdtemp(dir=custom_dir)

    # Get all transcriptions with non-empty text
    transcriptions = Transcription.objects.all().exclude(text='')

    # Create a text file for each transcription
    for transcription in transcriptions:
        file_name = f"{transcription.audio_file.audio_file.name}.txt"
        file_path = os.path.join(temp_dir, file_name)
        
        with open(file_path, 'w') as file:
            # file.write(f"Audio File Name: {transcription.audio_file.audio_file.name}\n")
            file.write(f"{transcription.text}\n")

    # Create a ZIP file containing all the text files
    zip_file_path = os.path.join(temp_dir, 'transcriptions.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), temp_dir))

    # Serve the ZIP file for download
    with open(zip_file_path, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=transcriptions.zip'

    # # Clean up the temporary directory
    # os.remove(zip_file_path)
    # os.rmdir(temp_dir)

    return response
