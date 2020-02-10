from django.shortcuts import render,  redirect
from django.db.models import Q
from django.db import models
from django.views import generic
from django.contrib.auth.decorators import login_required
import re
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from . models import vinfile, business
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from . forms import vinfileForm, VinForm
import pandas as pd
import json as js
import requests
from . models import washed_vins, original_vins, vin_conflicts, wiki_vincodes, business, original_extension, start_api, \
    undertaking, zoho_sync_day1
from araa import settings
import io
import datetime
from django.db.models import Count
from zcrmsdk import ZCRMRestClient, ZohoOAuth, ZCRMRecord, ZCRMModule
import zcrmsdk as zoho
from django import template
import json


# Create your views here.


def home(request):
    return render(request, 'vinwash/index.html')


def lookup_vinwash(a, make1, make2, make3):

    d = original_vins.objects.all().values('img', 'date', 'stock_number', 'location', 'business_id',
                                           'file_id', 'wiki_id').filter(vin=a)
    d = pd.DataFrame(d)
    listt = d.values.tolist()
    #print(listt)
    if len(listt) > 0:
        #print(listt)
        #print(len(listt))
        listt = listt[0]
        #print(listt)
        #print(len(listt))
        #print(listt[4])
        biz = business.objects.all().values('bname', 'state').filter(id=listt[4])
        biz = pd.DataFrame(biz)
        listt1 = biz.values.tolist()
        listt1 = listt1[0]
        #print("prafull")
        #print(listt[3])
        if listt[3] != '':
            path = settings.MEDIA_ROOT + '\\manual\\' + str(listt[0]) + listt[3]
            #print(path)
            context = {
                'vals': listt,
                'path': path,
                'folder': 'manual',
                'biz': listt1
            }
        else:
            filid = listt[2]
            #print(filid)
            filname = vinfile.objects.values('filename').filter(id=filid)
            #print(filname[0]['filename'])

            #print('vin has electronic file as source')
            path = settings.MEDIA_ROOT + '\\electronic\\' + filname[0]['filename']
            #print(path)
            context = {
                'elec': filname[0]['filename'],
                'vals1': listt,
                'path': path,
                'folder': 'manual',
                'biz': listt1
            }
    else:
        context = {
            'elec': '',
            'vals1': '',
            'path': '',
            'folder': '',
            'biz': ''
        }
    #print('------')
    #print(context)
    #print('------')
    return context


def lookup_washedvins(a, make1, make2, make3, username):

    # dd1 = washed_vins.objects.all().values('vehicleid').filter(vin=a).filter(make__in=[make1, make2, make3]).count()
    if username != 'takata':
        dd = washed_vins.objects.all().values('vehicleid').filter(vin=a).filter(make__in=[make1, make2, make3]).count()
    else:
        dd = washed_vins.objects.all().values('vehicleid').filter(vin=a).count()
    if dd > 0:
        d = washed_vins.objects.all().values('vehicleid', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha').filter(vin=a)
        # print(dd)
        d = pd.DataFrame(d)
        # print(d['img'].values[0])
        listt = d.values.tolist()
        #print(listt)
        listt = listt[0]  # list of values
        #print(listt)

        context = {
            'wv_vals': listt
        }

    else:
        context = {
            'na_washedvins': 'Vin Not Found in washed vins table'
        }
    return context


def lookup_star(a, make1, make2, make3, username):

    if username == 'takata':
        dd = start_api.objects.all().values('vin').filter(vin=a).count()
    else:
        dd = start_api.objects.all().values('vin').filter(vin=a).filter(make__in=[make1, make2, make3]).count()

    #dd = start_api.objects.all().values('starid').filter(vin=a).filter(make__in=[make1, make2, make3]).count()
    if dd > 0:
        d = start_api.objects.all().values('starid', 'barcode', 'pranum', 'notifierfname', 'abn', 'cname',
                                           'email', 'bphone', 'status', 'cond', 'warehouse').filter(vin=a)
        # print(dd)
        d = pd.DataFrame(d)
        listt = d.values.tolist()
        print(listt)
        listt = listt[0]  # list of values
        print(listt)

        context = {
            'st_vals': listt
        }

    else:
        #print("bulls eye")
        context = {
            'na_star': 'Vin Not Found in star db'
        }
    return context


def lookup_taut(a, make1, make2, make3, username):

    if username != 'takata':
        dd = undertaking.objects.all().values('vin').filter(vin=a).filter(make__in=[make1, make2, make3]).count()
    else:
        dd = undertaking.objects.all().values('vin').filter(vin=a).count()

    #dd = undertaking.objects.all().values('vin').filter(vin=a).filter(make__in=[make1, make2, make3]).count()
    if dd > 0:
        d = undertaking.objects.all().values('condition', 'dateOfSale', 'dateSigned', 'email', 'licenseDetail',
                                             'notificationDate', 'status', 'sellerPhone', 'companyName').filter(vin=a)
        # print(dd)
        d = pd.DataFrame(d)
        # print(d['img'].values[0])
        listt = d.values.tolist()
        #print(listt)
        listt = listt[0]  # list of values
        #print(listt)

        context = {
            'ut_vals': listt
        }

    else:
        #print("bulls eye")
        context = {
            'na_taut': 'Vin Not Found in taut db'
        }
    return context


def lookup_zoho(a):
    ''''
    bn = start_api.objects.all().values('cname').filter(vin=a)
    print(bn)
    if len(bn)> 0:
        print("name in star")
        star_bname = bn[0]['cname']
        print(star_bname)
        zid = zoho_sync_day1.objects.all().values('bid').filter(bname=star_bname)
        zbid = zid[0]['bid']
        print(zbid)
        data = calls_for_business(zbid)
        print(data)
        context = {
            'zh_vals': data
        }
    else:
        context = {
            'zh_vals': ''
        }
    '''
    context = {
        'zh_vals': ''
    }
    return context


def lookup_hondafile(a, make1, make2, make3):
    d = original_vins.objects.all().values('img', 'date', 'stock_number', 'location', 'business_id',
                                           'file_id', 'wiki_id').filter(vin=a)
    d = pd.DataFrame(d)
    listt = d.values.tolist()
    #print('tangainamabobo pekpek')
    if len(listt) > 0:
        listt = listt[0]
        #print(listt)
        #print(len(listt))
        #print(listt[4])
        biz = business.objects.all().values('bname', 'state').filter(id=listt[4])
        biz = pd.DataFrame(biz)
        listt1 = biz.values.tolist()
        listt1 = listt1[0]
        bizz = listt1[0]
        print(bizz)

        hf = business.objects.all().values('bname', 'state').filter(id=listt[4])
        biz = pd.DataFrame(biz)




@login_required
def vin_decoder(request):
    print('# START CODE vin lookup #')
    username = request.user.username
    print(username)
    if username == 'nissan':
        make1 = 'Nissan'
        make2 = ''
        make3 = ''
        sample = 'MNTBBAC11A0012771'
    elif username == 'honda':
        make1 = 'Honda'
        make2 = ''
        make3 = ''
        sample = 'MRHCM56405P031460'
    elif username == 'toyota':
        make1 = 'Toyota'
        make2 = 'Lexus'
        make3 = ''
        sample = 'JTDBR22E703088305'
    elif username == 'mitsubishi':
        make1 = 'Mitsubishi'
        make2 = ''
        make3 = ''
        sample = 'JMFLYV97W8J000369'
    elif username == 'holden':
        make1 = 'Holden'
        make2 = 'SAAB'
        make3 = 'Opel'
        sample = '6G1PE6E89CL656195'
    elif username == 'bmw':
        make1 = 'BMW'
        make2 = ''
        make3 = ''
        sample = 'WBAAU52030KN42441'
    elif username == 'ford':
        make1 = 'Ford'
        make2 = ''
        make3 = ''
        sample = 'MNAUSFE909W842107'
    elif username == 'mazda':
        make1 = 'Mazda'
        make2 = ''
        make3 = ''
        sample = 'JM0ER103190116446'
    elif username == 'chrysler':
        make1 = 'Chrysler'
        make2 = 'Jeep'
        make3 = ''
        sample = ''
    elif username == 'subaru':
        make1 = 'Subaru'
        make2 = ''
        make3 = ''
        sample = 'JF1GH7KS5BG059258'
    elif username == 'takata':
        make1 = 'Subaru'
        make2 = ''
        make3 = ''
        sample = 'JF1GH7KS5BG059258'
    else:
        make1 = 'Subaru'
        make2 = ''
        make3 = ''
        sample = 'JF1GH7KS5BG059258'

    if request.method == 'POST':
        form = VinForm(request.POST)
        if form.is_valid():
            a = request.POST.get('your_vin')
            # -- START CODE -- this code is finalized for checking if vin is in database or not ..
            dd1 = washed_vins.objects.all().values('vehicleid').filter(vin=a).count()
            dd2 = start_api.objects.all().values('starid').filter(vin=a).count()
            dd3 = undertaking.objects.all().values('vin').filter(vin=a).count()
            dd4 = original_vins.objects.all().values('vin').filter(vin=a).count()
            # -- END CODE -- this code is finalized for checking if vin is in database or not ..
            #print(a)
            if dd1 > 0 or dd2 > 0 or dd3 > 0 or dd4 > 0:
                m1 = 'Vin does exist in our database'
                context0 = {'form': form}
                context1 = lookup_vinwash(a, make1, make2, make3)
                context2 = lookup_washedvins(a, make1, make2, make3, username)
                context3 = lookup_star(a, make1, make2, make3, username)
                context4 = lookup_taut(a, make1, make2, make3, username)
                context5 = lookup_zoho(a)
                context6 = {'vin': a}
                context7 = lookup_hondafile(a, make1, make2, make3)

                context = {**context0, **context1, **context2, **context3, **context4, **context5, **context6}
                #print(context)
            else:
                context0 = {'form': form}
                m2 = 'Vin does not exist in our database.. wrecker files / star/ undertaking'
                #print(m2)
                context1 = {
                    'notfound': m2
                }
                context = {**context0, **context1}
    else:
        a = sample
        form = VinForm()
        context0 = {'form': form}
        context1 = lookup_vinwash(a, make1, make2, make3)
        context2 = lookup_washedvins(a, make1, make2, make3, username)
        context3 = lookup_star(a, make1, make2, make3, username)
        context4 = lookup_taut(a, make1, make2, make3, username)
        context5 = lookup_zoho(a)
        context6 = {'vin': a}
        context = {**context0, **context1, **context2, **context3, **context4, **context5, **context6}

    print('# END CODE vin lookup')
    return render(request, 'vinwash/vinlookup.html', context)