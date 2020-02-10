from django.contrib import admin
from django.urls import path, re_path, include
from . import views
#from . views import FileCreateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='vinwash-home'),
    path('vindecoder/', views.vin_decoder, name='vindecoder'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
