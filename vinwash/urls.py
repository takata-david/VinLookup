from django.contrib import admin
from django.urls import path, re_path, include
from . import views
#from . views import FileCreateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='vinwash-home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('files/', views.file_list, name='file_list'),
    path('files/upload/', views.upload_file, name='upload_file'),
    path('files/bulk/', views.upload_bulk, name='upload_bulk'),
    path('report/1/', views.vins_located, name='vins-located'),
    path('report/2/', views.vins_make_consl, name='vins-make-consl'),
    path('xgboost/results/', views.xgboost_results, name='xgboost-results'),
    #path('report/3/', views.vins_located_monthly, name='vins-located-monthly'),

    path('report/consolidated/', views.consolidated_data, name='vins-consolidated'),

    path('reports/', views.report_menu, name='report-menu'),

    path('report/<slug:oem>/', views.oem_report, name='oem-report'),
    path('report1/filecount/', views.file_count, name='file-count'),
    path('vinlookup/<slug:vin>/', views.vin_lookup, name='vin-lookup'),




    path('upload/star/', views.star_upload, name='star-upload'),
    path('upload/undertaking/', views.undertaking_upload, name='undertaking-upload'),

    path('upload/staridlink/', views.add_star_id, name='add_star_id'),
    path('upload/tautidlink/', views.add_taut_id, name='add_taut_id'),

    #path('upload/bose/', views.star_id_upload, name='vin-id-upload'),
    path('zoho/', views.zoho_sync, name='zoho-sync'),
    path('upload/undertaking/', views.undertaking_detailed_upload, name='undertaking-detailed-upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
