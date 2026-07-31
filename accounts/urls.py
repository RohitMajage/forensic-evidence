from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from  .views import *

urlpatterns = [
    path('', base, name='base'),
    path('debug/', debug_view, name='debug'),
    path('register/', register_view, name='register'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # profile
    path('profile/', view_profile, name='view_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),

    # contact
    path('contact/', contact, name='contact'),
    path('contactView/', contact_view, name='contactView'),

    # about
    path('about/', about, name='about'),
    
    path('case_create/', case_create, name='case_create'),
    path('evidence_create/', evidence_create, name='evidence_create'),
    path('evidence_list/', evidence_list, name='evidence_list'),
    path('verify/', match_input, name='verify_input'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)