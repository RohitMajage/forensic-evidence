from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings

from .forms import *
from .models import *
from .utils import *

import os
import numpy as np
import tempfile

# Lazy-loaded globals (only initialized when first used, not at import time)
_voice_encoder = None

def get_voice_encoder():
    global _voice_encoder
    if _voice_encoder is None:
        try:
            from resemblyzer import VoiceEncoder
            _voice_encoder = VoiceEncoder()
        except Exception as e:
            print(f"[VoiceEncoder load error] {e}")
    return _voice_encoder



def base(request):
    return render(request, 'base.html')


def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)


def debug_view(request):
    """Temporary debug endpoint to check server health on Render."""
    import sys, django
    from django.conf import settings as s
    info = {
        'python': sys.version,
        'django': django.__version__,
        'debug': s.DEBUG,
        'db_engine': s.DATABASES['default'].get('ENGINE', '?'),
        'email_backend': s.EMAIL_BACKEND,
        'allowed_hosts': s.ALLOWED_HOSTS,
    }
    # Test DB connection
    try:
        from accounts.models import CustomUser
        count = CustomUser.objects.count()
        info['db_users'] = count
        info['db_ok'] = True
    except Exception as e:
        info['db_error'] = str(e)
        info['db_ok'] = False

    # Test imports
    for mod in ['whitenoise', 'gunicorn', 'dj_database_url', 'resemblyzer', 'face_recognition']:
        try:
            __import__(mod)
            info[f'import_{mod}'] = 'OK'
        except Exception as e:
            info[f'import_{mod}'] = f'FAIL: {e}'

    import json
    from django.http import JsonResponse
    return JsonResponse(info)


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Remove any leftover unverified accounts with same username/email
        if username:
            CustomUser.objects.filter(username=username, is_active=False).delete()
        if email:
            CustomUser.objects.filter(email=email, is_active=False).delete()

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                otp = generate_otp()
                user.otp_code = otp
                user.is_active = True   # Active immediately so user is never locked out
                user.is_verified = False
                user.save()

                # Log the user in right away
                login(request, user)

                # Send OTP email synchronously (not in daemon thread) so Gunicorn doesn't kill it
                email_sent = False
                try:
                    send_mail(
                        'Your ForensicEvidence Email OTP',
                        f'Hello {user.username},\n\nYour OTP code is: {otp}\n\nPlease enter this code to verify your email address.',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    email_sent = True
                except Exception as e:
                    print(f"[OTP Email Error] {e}")

                if email_sent:
                    messages.success(request, f"Welcome {user.username}! An OTP has been sent to {user.email}.")
                else:
                    messages.warning(request, f"Welcome {user.username}! Email delivery issue encountered. Your verification OTP code is: {otp}")

                return redirect('verify_otp')

            except Exception as e:
                print(f"[Register Error] {e}")
                messages.error(request, f"Registration failed: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_otp_view(request):
    # User is already logged in after registration; get from request.user or session
    if request.user.is_authenticated:
        user = request.user
    else:
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('register')
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return redirect('register')

    # Already verified — skip OTP page
    if user.is_verified:
        return redirect('base')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if user.otp_code and user.otp_code == entered_otp:
            user.is_verified = True
            user.otp_code = None
            user.save()
            messages.success(request, "Email verified successfully!")
            return redirect('base')
        else:
            return render(request, 'accounts/verify_otp.html', {'error': 'Invalid OTP. Please try again.'})

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
    contacts_list = Contact.objects.all().order_by('-id')
    paginator = Paginator(contacts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'contact/contactView.html', {'page_obj': page_obj})


@login_required
def about(request):
    return render(request, 'about/about.html')


@login_required
def case_create(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.created_by = request.user
            team, _ = Team.objects.get_or_create(name="Default Forensic Team")
            team.members.add(request.user)
            case.team = team
            case.save()
            messages.success(request, f"Case '{case.case_name}' created successfully!")
            return redirect('evidence_create')
    else:
        form = CaseForm()
    return render(request, 'evidence/case_form.html', {'form': form})


from django.db.models import Q

@login_required
def evidence_list(request):
    query = request.GET.get('q', '').strip()
    evidence_type = request.GET.get('type', '').strip()

    if request.user.is_superuser:
        evidences = Evidence.objects.all()
    else:
        evidences = Evidence.objects.filter(
            Q(viewers=request.user) | Q(uploaded_by=request.user)
        ).distinct()

    if query:
        evidences = evidences.filter(
            Q(case__case_number__icontains=query) |
            Q(case__case_name__icontains=query) |
            Q(description__icontains=query)
        )
    if evidence_type:
        evidences = evidences.filter(type=evidence_type)

    evidences = evidences.order_by('-uploaded_at')

    return render(request, 'evidence/evidence_list.html', {
        'evidences': evidences,
        'query': query,
        'selected_type': evidence_type,
    })


@login_required
def evidence_delete(request, pk):
    evidence = get_object_or_404(Evidence, pk=pk)
    if request.user == evidence.uploaded_by or request.user.is_superuser:
        evidence.delete()
        messages.success(request, "Evidence deleted successfully.")
    else:
        messages.error(request, "You do not have permission to delete this evidence.")
    return redirect('evidence_list')


@login_required
def evidence_create(request):
    # Ensure at least one default case exists so the dropdown is never empty
    if not Case.objects.exists():
        team, _ = Team.objects.get_or_create(name="Default Forensic Team")
        team.members.add(request.user)
        Case.objects.create(
            case_name="General Forensic Case",
            case_number="CASE-001",
            team=team,
            created_by=request.user
        )

    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.uploaded_by = request.user
            evidence.save()
            form.save_m2m()

            # Always add uploader as a viewer of their own evidence
            evidence.viewers.add(request.user)

            viewers = form.cleaned_data.get('viewers')
            if viewers:
                for viewer in viewers:
                    if viewer.email and viewer != request.user:
                        try:
                            send_mail(
                                subject='New Evidence Uploaded',
                                message=f"New evidence has been uploaded to case {evidence.case.case_number}.",
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[viewer.email],
                                fail_silently=True,
                            )
                        except Exception as e:
                            print(f"[Evidence Mail Error] {e}")

            messages.success(request, "Evidence uploaded successfully!")
            return redirect('evidence_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = EvidenceForm(request=request)
    return render(request, 'evidence/evidence_form.html', {'form': form})


def convert_to_wav(source_path, target_path):
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(source_path)
        audio.export(target_path, format="wav")
        return True
    except Exception as e:
        print("[Conversion Error]", e)
        return False


def compare_audio(file1, file2):
    try:
        from resemblyzer import preprocess_wav
        enc = get_voice_encoder()
        if enc is None:
            return False
        wav1 = preprocess_wav(file1)
        wav2 = preprocess_wav(file2)
        embed1 = enc.embed_utterance(wav1)
        embed2 = enc.embed_utterance(wav2)
        similarity = np.dot(embed1, embed2) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))
        return similarity > 0.75
    except Exception as e:
        print("[Audio Embed Compare Error]", e)
        return False


@login_required
def match_input(request):
    match_result = None
    matched_evidence = None
    match_message = None

    if request.method == 'POST':
        form = MatchInputForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = request.FILES.get('uploaded_face')
            uploaded_voice = request.FILES.get('uploaded_voice')

            if uploaded_image:
                try:
                    import face_recognition
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
                except Exception as e:
                    print(f"[face_recognition import error] {e}")
                    match_message = "Face recognition is not available."

            if not matched_evidence and uploaded_voice:
                temp_input_path = os.path.join(tempfile.gettempdir(), uploaded_voice.name)
                temp_wav_path = temp_input_path.replace(".mp3", ".wav").replace(".m4a", ".wav")

                with open(temp_input_path, 'wb+') as dest:
                    for chunk in uploaded_voice.chunks():
                        dest.write(chunk)

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

                for path in [temp_input_path, temp_wav_path]:
                    if os.path.exists(path):
                        os.remove(path)

            match_result = matched_evidence

    else:
        form = MatchInputForm()

    return render(request, 'evidence/match_input.html', {
        'form': form,
        'match_result': match_result,
        'match_message': match_message,
    })
