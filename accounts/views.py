from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings

from .forms import *
from .models import *
from .utils import *


# base_dir = settings.BASE_DIR
# models_folder = os.path.join(base_dir, "model", "")
# model_name = "" 
# model_path = os.path.join(models_folder, model_name)
# model = tf.keras.models.load_model(model_path)


def base(request):
    return render(request, 'base.html')



# def register_view(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('login')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'accounts/register.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        if username:
            CustomUser.objects.filter(username=username, is_active=False).delete()
        if email:
            CustomUser.objects.filter(email=email, is_active=False).delete()

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            otp = generate_otp()
            user.otp_code = otp
            user.is_active = False  # Deactivate until verified
            user.save()

            # Send OTP via email safely
            try:
                send_mail(
                    'Verify your email with OTP',
                    f'Your OTP code is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"[Email Error] {e}")

            request.session['user_id'] = user.id
            messages.info(request, f"An OTP code has been sent to {user.email}. Please enter it to verify.")
            return redirect('verify_otp')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})





from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import CustomUser

def verify_otp_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if user.otp_code == entered_otp:
            user.is_active = True
            user.is_verified = True
            user.otp_code = None
            user.save()
            login(request, user)
            return redirect('base')
        else:
            return render(request, 'accounts/verify_otp.html', {'error': 'Invalid OTP'})
    
    return render(request, 'accounts/verify_otp.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('base')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# profile
@login_required
def view_profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')  
    else:
        form = CustomUserProfileForm(instance=user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# contact
@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})


@login_required
def contact_view(request):
    contacts_list = Contact.objects.all()
    paginator = Paginator(contacts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'contact/contactView.html', {'page_obj': page_obj})

# about
@login_required
def about(request):
    return render(request, 'about/about.html')

# recoz
from .models import Evidence, Case
from .forms import EvidenceForm

@login_required
def evidence_list(request):
    if request.user.is_superuser:
        evidences = Evidence.objects.all()
    else:
        evidences = Evidence.objects.filter(viewers=request.user)
    return render(request, 'evidence/evidence_list.html', {'evidences': evidences})

@login_required
def evidence_create(request):
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.uploaded_by = request.user
            evidence.save()
            form.save_m2m()

            # Notify viewers
            for viewer in form.cleaned_data['viewers']:
                send_mail(
                    subject='New Evidence Uploaded',
                    message=f"New evidence has been uploaded to case {evidence.case.case_number}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[viewer.email],
                    fail_silently=True,
                )
            messages.success(request, "Evidence uploaded and viewers notified.")
            return redirect('evidence_list')
    else:
        form = EvidenceForm(request=request)
    return render(request, 'evidence/evidence_form.html', {'form': form})



from django.shortcuts import render
from .forms import MatchInputForm
from .models import Person, MatchResult
import cv2
import face_recognition
import os
from pydub import AudioSegment
from scipy.io import wavfile
import numpy as np

from scipy.io import wavfile
import numpy as np
import face_recognition
import os
from django.conf import settings

import os
import numpy as np
from scipy.io import wavfile
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Evidence, MatchResult  # or whatever model stores match history
from .forms import MatchInputForm
import face_recognition


import os
import numpy as np
from scipy.io import wavfile
import face_recognition
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import MatchInputForm
from .models import Evidence

# def compare_audio(file1, file2):
#     try:
#         sr1, data1 = wavfile.read(file1)
#         sr2, data2 = wavfile.read(file2)
#         # Compare the first 10000 samples
#         return np.corrcoef(data1[:10000], data2[:10000])[0, 1] > 0.9
#     except Exception as e:
#         print("[Audio Compare Error]", e)
#         return False

# @login_required
# def match_input(request):
#     match_result = None
#     matched_evidence = None
#     uploaded_voice_path = None

#     if request.method == 'POST':
#         form = MatchInputForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Handle uploaded files
#             uploaded_image = request.FILES.get('uploaded_face')
#             uploaded_voice = request.FILES.get('uploaded_voice')

#             # --- IMAGE MATCHING ---
#             if uploaded_image:
#                 uploaded_image_data = face_recognition.load_image_file(uploaded_image)
#                 uploaded_encoding = face_recognition.face_encodings(uploaded_image_data)
#                 if uploaded_encoding:
#                     uploaded_encoding = uploaded_encoding[0]
#                     for evidence in Evidence.objects.filter(type='image'):
#                         try:
#                             known_img = face_recognition.load_image_file(evidence.file.path)
#                             known_encoding = face_recognition.face_encodings(known_img)
#                             if known_encoding and face_recognition.compare_faces([known_encoding[0]], uploaded_encoding)[0]:
#                                 matched_evidence = evidence
#                                 break
#                         except Exception as e:
#                             print(f"[Image Match Error] {e}")

#             # --- AUDIO MATCHING ---
#             if not matched_evidence and uploaded_voice:
#                 uploaded_voice_path = f'/tmp/{uploaded_voice.name}'
#                 with open(uploaded_voice_path, 'wb+') as dest:
#                     for chunk in uploaded_voice.chunks():
#                         dest.write(chunk)

#                 for evidence in Evidence.objects.filter(type='audio'):
#                     try:
#                         if compare_audio(evidence.file.path, uploaded_voice_path):
#                             matched_evidence = evidence
#                             break
#                     except Exception as e:
#                         print(f"[Audio Match Error] {e}")

#             # Clean up temp voice file if created
#             if uploaded_voice_path and os.path.exists(uploaded_voice_path):
#                 os.remove(uploaded_voice_path)

#             match_result = matched_evidence

#     else:
#         form = MatchInputForm()

#     return render(request, 'evidence/match_input.html', {
#         'form': form,
#         'match_result': match_result
#     })

import os
import numpy as np
import tempfile
from pydub import AudioSegment
from scipy.io import wavfile
import face_recognition
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import MatchInputForm
from .models import Evidence

def convert_to_wav(source_path, target_path):
    try:
        audio = AudioSegment.from_file(source_path)
        audio.export(target_path, format="wav")
        return True
    except Exception as e:
        print("[Conversion Error]", e)
        return False

# def compare_audio(file1, file2):
#     try:
#         sr1, data1 = wavfile.read(file1)
#         sr2, data2 = wavfile.read(file2)

#         # Make mono
#         if data1.ndim > 1:
#             data1 = data1[:, 0]
#         if data2.ndim > 1:
#             data2 = data2[:, 0]

#         # Normalize length
#         min_len = min(len(data1), len(data2))
#         data1, data2 = data1[:min_len], data2[:min_len]

#         # Normalize amplitude
#         data1 = data1 / np.max(np.abs(data1))
#         data2 = data2 / np.max(np.abs(data2))

#         correlation = np.corrcoef(data1, data2)[0, 1]
#         return correlation > 0.85
#     except Exception as e:
#         print("[Audio Compare Error]", e)
#         return False

from resemblyzer import VoiceEncoder, preprocess_wav

encoder = VoiceEncoder()

def compare_audio(file1, file2):
    try:
        wav1 = preprocess_wav(file1)
        wav2 = preprocess_wav(file2)
        embed1 = encoder.embed_utterance(wav1)
        embed2 = encoder.embed_utterance(wav2)
        similarity = np.dot(embed1, embed2) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))
        return similarity > 0.75  # Adjustable threshold
    except Exception as e:
        print("[Audio Embed Compare Error]", e)
        return False


@login_required
def match_input(request):
    match_result = None
    matched_evidence = None
    temp_audio_path = None
    match_message = None  # <-- Add this

    if request.method == 'POST':
        form = MatchInputForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = request.FILES.get('uploaded_face')
            uploaded_voice = request.FILES.get('uploaded_voice')

            # --- IMAGE MATCHING ---
            if uploaded_image:
                uploaded_image_data = face_recognition.load_image_file(uploaded_image)
                uploaded_encoding = face_recognition.face_encodings(uploaded_image_data)
                if uploaded_encoding:
                    uploaded_encoding = uploaded_encoding[0]
                    for evidence in Evidence.objects.filter(type='image'):
                        try:
                            known_img = face_recognition.load_image_file(evidence.file.path)
                            known_encoding = face_recognition.face_encodings(known_img)
                            if known_encoding and face_recognition.compare_faces([known_encoding[0]], uploaded_encoding)[0]:
                                matched_evidence = evidence
                                match_message = f"Image matched with evidence ID {evidence.id}."
                                break
                        except Exception as e:
                            print(f"[Image Match Error] {e}")
                if not matched_evidence:
                    match_message = "Image did not match any stored evidence."

            # --- AUDIO MATCHING ---
            if not matched_evidence and uploaded_voice:
                temp_input_path = os.path.join(tempfile.gettempdir(), uploaded_voice.name)
                temp_wav_path = temp_input_path.replace(".mp3", ".wav").replace(".m4a", ".wav")

                # Save the uploaded file
                with open(temp_input_path, 'wb+') as dest:
                    for chunk in uploaded_voice.chunks():
                        dest.write(chunk)

                # Convert to wav
                if convert_to_wav(temp_input_path, temp_wav_path):
                    for evidence in Evidence.objects.filter(type='audio'):
                        try:
                            if compare_audio(evidence.file.path, temp_wav_path):
                                matched_evidence = evidence
                                match_message = f"Audio matched with evidence ID {evidence.id}."
                                break
                        except Exception as e:
                            print(f"[Audio Match Error] {e}")
                    if not matched_evidence:
                        match_message = "Audio did not match any stored evidence."
                else:
                    match_message = "Audio conversion failed."

                # Clean up temp files
                for path in [temp_input_path, temp_wav_path]:
                    if os.path.exists(path):
                        os.remove(path)

            match_result = matched_evidence

    else:
        form = MatchInputForm()

    return render(request, 'evidence/match_input.html', {
        'form': form,
        'match_result': match_result,
        'match_message': match_message,  # <-- Pass message to template
    })
