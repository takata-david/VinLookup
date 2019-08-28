from django.contrib import admin
from django.urls import path, re_path, include
from . import views
#from . views import FileCreateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='vinwash-home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #('process/', views.process, name='process'),
    #path('upload/', views.upload, name='upload'),
    path('files/', views.file_list, name='file_list'),
    path('files/upload/', views.upload_file, name='upload_file'),
    path('files/bulk/', views.upload_bulk, name='upload_bulk'),
    path('report/1/', views.vins_located, name='vins-located'),
    path('report/2/', views.vins_make_consl, name='vins-make-consl'),
    path('report/<slug:oem>/', views.oem_report, name='oem-report'),
    path('report1/filecount/', views.file_count, name='file-count'),
    path('vinlookup/<slug:vin>/', views.vin_lookup, name='vin-lookup'),
    path('upload/star/', views.star_detailed_upload, name='vin-detailed-upload'),
    path('zoho/', views.zoho_sync, name='zoho-sync'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
