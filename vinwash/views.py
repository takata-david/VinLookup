from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . models import vinfile, business
from . forms import VinForm
import pandas as pd
from . models import washed_vins, original_vins, business, start_api, undertaking, honda_mapped_address
from araa import settings
from azure.storage.blob import BlockBlobService
from azure.storage.blob.baseblobservice import BaseBlobService
from azure.storage.blob import BlobPermissions
from datetime import datetime, timedelta
import urllib.request
import numpy as np
from io import StringIO, BytesIO
from requests.utils import requote_uri
import os
import requests
import json


def home(request):
    return render(request, 'vinwash/index.html')

def lookup_vinwash(a, make1, make2, make3, side):

    d = original_vins.objects.all().values('img', 'date', 'stock_number', 'location', 'business_id',
                                           'file_id', 'wiki_id', 'vin').filter(vin=a)
    d = pd.DataFrame(d)
    listt = d.values.tolist()
    if len(listt) > 0:
        listt = listt[0]
        biz = business.objects.all().values('bname', 'state', 'street', 'city').filter(id=listt[4])
        biz = pd.DataFrame(biz)
        listt1 = biz.values.tolist()
        listt1 = listt1[0]
        filid = listt[5]
        filname = vinfile.objects.values('filename').filter(id=filid)
        path = settings.MEDIA_ROOT + '\\electronic\\' + filname[0]['filename']
        context = {
            'vals': listt,
            'path': path,
            'biz' : listt1,
            'filename': filname[0]['filename']
        }
    else:
        context = {
            'vals': '',
            'path': '',
            'biz': '',
            'filename': ''
        }
    return context


def lookup_washedvins(a, make1, make2, make3, username, side):

    if side == "default":
        if username == 'takata' or username == 'prafull':
            dd1 = washed_vins.objects.all().values('vehicleid', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha').filter(vin=a)
        else:
            dd1 = washed_vins.objects.all().values('vehicleid', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha').filter(vin=a).filter(make__in=[make1, make2, make3])
    else:
        if username == 'takata' or username == 'prafull':
            dd1 = washed_vins.objects.all().values('vehicleid', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha').filter(airbaglocation=side).filter(vin=a)
        else:
            dd1 = washed_vins.objects.all().values('vehicleid', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha').filter(airbaglocation=side).filter(vin=a).filter(make__in=[make1, make2, make3])

    if dd1.count() > 0:
        d = pd.DataFrame(dd1)
        listt = d.values.tolist()
        listt = listt[0]
        context = {
            'wv_vals': listt
        }
    else:
        context = {
            'na_washedvins': 'Vin Not Found in washed vins table'
        }
    return context


def lookup_star(a, make1, make2, make3, username, side):
    if side == "default":
        if username == 'takata' or username == 'prafull':
            dd1 = start_api.objects.all().values('starid', 'barcode', 'pranum', 'notifierfname', 'abn', 'cname',
                                           'email', 'bphone', 'status', 'cond', 'warehouse', 'comp', 'cour',
                                           'fname', 'lname', 'tradingname', 'street', 'city', 'state', 'post',
                                           'cemail', 'bsb', 'accnum', 'phone', 'notdate', 'sub_date', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha', 'cond_alias').filter(vin=a)
        else:
            dd1 = start_api.objects.all().values('starid', 'barcode', 'pranum', 'notifierfname', 'abn', 'cname',
                                           'email', 'bphone', 'status', 'cond', 'warehouse', 'comp', 'cour',
                                           'fname', 'lname', 'tradingname', 'street', 'city', 'state', 'post',
                                           'cemail', 'bsb', 'accnum', 'phone', 'notdate', 'sub_date', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha', 'cond_alias').filter(vin=a).filter(make__in=[make1, make2, make3])
    else:
        if username == 'takata' or username == 'prafull':
            dd1 = start_api.objects.all().values('starid', 'barcode', 'pranum', 'notifierfname', 'abn', 'cname',
                                           'email', 'bphone', 'status', 'cond', 'warehouse', 'comp', 'cour',
                                           'fname', 'lname', 'tradingname', 'street', 'city', 'state', 'post',
                                           'cemail', 'bsb', 'accnum', 'phone', 'notdate', 'sub_date', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha', 'cond_alias').filter(airbaglocation=side).filter(vin=a)
        else:
            dd1 = start_api.objects.all().values('starid', 'barcode', 'pranum', 'notifierfname', 'abn', 'cname',
                                           'email', 'bphone', 'status', 'cond', 'warehouse', 'comp', 'cour',
                                           'fname', 'lname', 'tradingname', 'street', 'city', 'state', 'post',
                                           'cemail', 'bsb', 'accnum', 'phone', 'notdate', 'sub_date', 'make', 'model', 'series', 'year', 'airbaglocation', 'isalpha', 'cond_alias').filter(airbaglocation=side).filter(vin=a).filter(make__in=[make1, make2, make3])


    if dd1.count() > 0:
        d = pd.DataFrame(dd1)
        listt = d.values.tolist()
        listt = listt[0]
        print(listt)
        cod_url = 'http://takatadev.com/home/print/'+listt[0]
        print(listt[5])
        cod = listt[32]
        print(cod)
        folder = listt[5].upper()
        if cod == 'CoD' and (listt[5] == 'JJ Auto Parts Pty Ltd' or folder == 'ACM PARTS - HEAD OFFICE'):
            side = listt[30]
            STORAGEACCOUNTNAME = 'djangodevdiag'
            STORAGEACCOUNTKEY = "Y5k5ahE0d1gVlZ8HkeUkG/l3wUd1/f4dApWmS8ua+fi7fxLBI/eqkbMQVPlu1m9uAFXTNQufgja+fSWrVuYTzQ=="
            blob_service = BlockBlobService(account_name=STORAGEACCOUNTNAME, account_key=STORAGEACCOUNTKEY)
            CONTAINERNAME = 'vinwash'

            pf = folder+"/"
            generator = blob_service.list_blobs(CONTAINERNAME, prefix=pf , delimiter="")
            p = 0
            q = 0
            for blob in generator:
                csv_name = blob.name
                #print(csv_name)
                newstr = csv_name[-3:]
                if newstr == 'csv':
                    blobstring1 = blob_service.get_blob_to_text(CONTAINERNAME, csv_name).content
                    b1 = blobstring1
                    df = pd.read_csv(StringIO(b1), encoding='utf-8')
                    i=1
                    for h in df.iterrows():
                        bs = h[1]['VIN']
                        i = i + 1
                        if bs == a and p ==0:
                            filename = csv_name
                            p = i
                        if bs == a and p > 0:
                            filename = csv_name
                            q = i

            fl = filename.split("/")
            print(fl)
            fl1 = fl[1]
            uri = "https://" + STORAGEACCOUNTNAME + ".blob.core.windows.net/" + CONTAINERNAME + "/" + pf + fl1
            query_string = "?st=2020-02-19T01%3A51%3A32Z&se=2021-02-20T01%3A51%3A00Z&sp=rl&sv=2018-03-28&sr=c&sig=loHB8Qxmbu%2BOPjMjVD2tA6CqzfTTeDt6jrjSsUkV%2BNo%3D"
            url_vinfile = uri + query_string
            url_vinfile = requote_uri(url_vinfile)

            # Field Courier Statement.pdf
            uri_fcs = "https://" + STORAGEACCOUNTNAME + ".blob.core.windows.net/" + CONTAINERNAME + "/" + pf + "Field Courier Statement.pdf"
            url_fcs = uri_fcs + query_string
            url_fcs = requote_uri(url_fcs)

            # Owner Statement.pdf : stat dec
            uri_stat = "https://" + STORAGEACCOUNTNAME + ".blob.core.windows.net/" + CONTAINERNAME + "/" + pf + "Owner Statement.pdf"
            url_stat = uri_stat + query_string
            url_stat = requote_uri(url_stat)
            context = {
                'st_vals': listt,
                'st_vals_url_vinfile': url_vinfile,
                'st_vals_url_fcs': url_fcs,
                'st_vals_url_stat': url_stat,
                'st_line1': p,
                'st_line2': q,
                'cod_url': cod_url
            }

        else:
            p = 0
            context = {
                'st_vals': listt
            }
    else:
        context = {
            'na_star': 'Vin Not Found in Star'
        }
    return context


def lookup_taut(a, make1, make2, make3, username, side):
    if side == "default":
        if username == 'takata' or username == 'prafull':
            dd1 = undertaking.objects.all().values('condition', 'dateOfSale', 'dateSigned', 'email', 'licenseDetail',
                                             'notificationDate', 'status', 'sellerPhone', 'companyName','praNum', 'firstName',
                                             'lastName', 'companyName', 'businessPhone', 'email', 'recyclerABN', 'street',
                                             'city', 'postCode', 'stateCode', 'make', 'model', 'series', 'year', 'airbagLocation', 'isAlpha').filter(vin=a)
        else:
            dd1 = undertaking.objects.all().values('condition', 'dateOfSale', 'dateSigned', 'email', 'licenseDetail',
                                             'notificationDate', 'status', 'sellerPhone', 'companyName','praNum', 'firstName',
                                             'lastName', 'companyName', 'businessPhone', 'email', 'recyclerABN', 'street',
                                             'city', 'postCode', 'stateCode', 'make', 'model', 'series', 'year', 'airbagLocation', 'isAlpha')\
                .filter(vin=a).filter(make__in=[make1, make2, make3])
    else:
        if username == 'takata' or username == 'prafull':
            dd1 = undertaking.objects.all().values('condition', 'dateOfSale', 'dateSigned', 'email', 'licenseDetail',
                                             'notificationDate', 'status', 'sellerPhone', 'companyName','praNum', 'firstName',
                                             'lastName', 'companyName', 'businessPhone', 'email', 'recyclerABN', 'street',
                                             'city', 'postCode', 'stateCode', 'make', 'model', 'series', 'year', 'airbagLocation', 'isAlpha')\
                .filter(airbagLocation=side).filter(vin=a)
        else:
            dd1 = undertaking.objects.all().values('condition', 'dateOfSale', 'dateSigned', 'email', 'licenseDetail',
                                             'notificationDate', 'status', 'sellerPhone', 'companyName','praNum', 'firstName',
                                             'lastName', 'companyName', 'businessPhone', 'email', 'recyclerABN', 'street',
                                             'city', 'postCode', 'stateCode', 'make', 'model', 'series', 'year', 'airbagLocation', 'isAlpha')\
                .filter(airbagLocation=side).filter(vin=a).filter(make__in=[make1, make2, make3])



    if dd1.count() > 0:
        d = pd.DataFrame(dd1)
        listt = d.values.tolist()
        listt = listt[0]
        context = {
            'ut_vals': listt
        }
    else:
        context = {
            'na_taut': 'Vin Not Found in taut db'
        }
    return context


def lookup_zoho(a):
    context = {
        'zh_vals': ''
    }
    return context


def lookup_hondafile(a, make1, make2, make3, username, side):
    d = original_vins.objects.all().values('img', 'date', 'stock_number', 'location', 'business_id',
                                           'file_id', 'wiki_id').filter(vin=a)
    d = pd.DataFrame(d)
    listt = d.values.tolist()
    if len(listt) > 0:
        listt = listt[0]
        biz = business.objects.all().values('bname', 'state').filter(id=listt[4])
        biz = pd.DataFrame(biz)
        listt1 = biz.values.tolist()
        listt1 = listt1[0]
        bizz = listt1[0]
        hbiz = honda_mapped_address.objects.all().values('Honda_Name', 'HONDA_Address').filter(ZOHO_Business_name=bizz) | honda_mapped_address.objects.all().values('Honda_Name', 'HONDA_Address').filter(ZOHO_Trading_Name = bizz)
        hbiz = pd.DataFrame(hbiz)
        listt2 = hbiz.values.tolist()
        if len(listt2) > 0:
            listt2 = listt2[0]
            context = {
                'hff_vals': listt2
            }
        else:
            context = {
                'hff_vals': ''
            }
    else:
        context = {
            'na_hondaf': ' '
        }
    return context


def lookup_dp(a, make1, make2, make3, username, side):
    dd1 = undertaking.objects.all().values('airbagLocation').filter(vin=a)
    dd1 = pd.DataFrame(dd1)
    taut = dd1.values.tolist()
    taut = [item for sublist in taut for item in sublist]
    dd2 = start_api.objects.all().values('airbaglocation').filter(vin=a)
    dd2 = pd.DataFrame(dd2)
    star = dd2.values.tolist()
    star = [item for sublist in star for item in sublist]
    dd3 = washed_vins.objects.all().values('airbaglocation').filter(vin=a)
    dd3 = pd.DataFrame(dd3)
    washed_vin = dd3.values.tolist()
    washed_vin = [item for sublist in washed_vin for item in sublist]
    driver = 0
    passenger = 0
    wd, wp, sd, sp, td, tp = 0,0,0,0,0,0

    wv_len = len(washed_vin)
    if wv_len == 2:
        if washed_vin[0] == 'Driver' or washed_vin[1] == 'Driver':
            wd = 1
            driver = 1
        if washed_vin[0] == 'Passenger' or washed_vin[1] == 'Passenger':
            wp = 1
            passenger = 1
    elif wv_len == 1:
        if washed_vin[0] == 'Driver':
            wd = 1
            driver = 1
        if washed_vin[0] == 'Passenger':
            wp = 1
            passenger = 1
    else:
        pass

    st_len = len(star)
    if st_len == 2:
        if star[0] == 'Driver' or star[1] == 'Driver':
            sd = 1
            driver = 1
        if star[0] == 'Passenger' or star[1] == 'Passenger':
            sp = 1
            passenger = 1
    elif st_len == 1:
        if star[0] == 'Driver':
            sd = 1
            driver = 1
        if star[0] == 'Passenger':
            sp = 1
            passenger = 1
    else:
        pass

    tt_len = len(taut)
    if tt_len == 2:
        if taut[0] == 'Driver' or taut[1] == 'Driver':
            td = 1
            driver = 1
        if taut[0] == 'Passenger' or taut[1] == 'Passenger':
            tp = 1
            passenger = 1
    elif tt_len == 1:
        if taut[0] == 'Driver':
            td = 1
            driver = 1
        if taut[0] == 'Passenger':
            tp = 1
            passenger = 1
    else:
        pass

    if wd ==1 or wp == 1:
        m1 = 'in Vinwash System'
    else:
        m1 = ''

    if sd ==1 or sp == 1:
        m2 = 'in STAR System'
    else:
        m2 = ''

    if td ==1 or tp == 1:
        m3 = 'in TAUT System'
    else:
        m3 = ''
    if driver == 0 and passenger ==0:
        m4 = 'not available'
    else:
        m4 = ''

    context = {
        'wv_dp': washed_vin,
        'st_dp': star,
        'tt_dp': taut,
        'dr_cn': driver,
        'ps_cn': passenger,
        'm1': m1,
        'm2': m2,
        'm3': m3,
        'm4': m4
    }
    return context


def lookup_oemfiles(a):
    print('hello')
    link = "https://takatalive.com/api/takata/" + a
    f = requests.get(link)
    data = f.json()
    print(f.json)
    j = json.loads(data)
    val = j['HasMatch']
    print(j['HasMatch'])
    i = 0
    if val == "YES":
        details = []
        flag = ''
        result = j['Result']
        print(result)
        for k in result:
            print(k['VIN'])
            if i == 0:

                #details = [ str(k['VehicleAirbagID']), str(k['VehicleID']), str(k['VIN']), str(k['PRANum']), str(k['Make']), str(k['Model']), str(k['Series']), str(k['Year']), str(k['AirbagLocation']), str(k['IsAlpha']), str(k['IsSubmitted'])]

                details.append(str(k['VehicleAirbagID']))
                details.append(str(k['VehicleID']))
                details.append(str(k['VIN']))
                details.append(str(k['PRANum']))
                details.append(str(k['Make']))
                details.append(str(k['Model']))
                details.append(str(k['Series']))
                details.append(str(k['Year']))
                details.append(str(k['AirbagLocation']))
                details.append(str(k['IsAlpha']))
                details.append(str(k['IsSubmitted']))

                '''
                details[0] = str(k['VehicleAirbagID'])
                details[1] = str(k['VehicleID'])
                details[2] = str(k['VIN'])
                details[3] = str(k['PRANum'])
                details[4] = str(k['Make'])
                details[5] = str(k['Model'])
                details[6] = str(k['Series'])
                details[7] = str(k['Year'])
                details[8] = str(k['AirbagLocation'])
                details[9] = str(k['IsAlpha'])
                details[10] = str(k['IsSubmitted'])
                '''
            if i == 1:
                details.append(str(k['VehicleAirbagID']))
                details.append(str(k['VehicleID']))
                details.append(str(k['VIN']))
                details.append(str(k['PRANum']))
                details.append(str(k['Make']))
                details.append(str(k['Model']))
                details.append(str(k['Series']))
                details.append(str(k['Year']))
                details.append(str(k['AirbagLocation']))
                details.append(str(k['IsAlpha']))
                details.append(str(k['IsSubmitted']))
                '''
                details[11] = str(k['VehicleAirbagID'])
                details[12] = str(k['VehicleID'])
                details[13] = str(k['VIN'])
                details[14] = str(k['PRANum'])
                details[15] = str(k['Make'])
                details[16] = str(k['Model'])
                details[17] = str(k['Series'])
                details[18] = str(k['Year'])
                details[19] = str(k['AirbagLocation'])
                details[20] = str(k['IsAlpha'])
                details[21] = str(k['IsSubmitted'])
                '''
                flag = 'yes'
            i = i + 1
        context = {
            'details_oem': details,
            'affected_oem': 'yes',
            'flag': flag
        }
    else:
        details = []
        context = {
            'details_oem': details,
            'na_affected_oem': 'yes'
        }
    return context


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
        sample = 'MRHES16505P023315'
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
        sample = '1C3H9E3G66Y112346'
    elif username == 'subaru':
        make1 = 'Subaru'
        make2 = ''
        make3 = ''
        sample = 'JF1GH7KS5BG059258'
    elif username == 'takata':
        make1 = 'Honda'
        make2 = ''
        make3 = ''
        sample = 'MRHES16505P023315'
    else:
        make1 = 'Honda'
        make2 = ''
        make3 = ''
        sample = 'MRHES16505P023315'

    if request.method == 'POST':
        form = VinForm(request.POST)
        if form.is_valid():
            a = request.POST.get('your_vin')
            loc = request.POST.get('airbaglocation')
            if loc == None:
                side = 'default'
            else:
                side = loc
            # -- START CODE -- this code is finalized for checking if vin is in database or not ..
            dd1 = washed_vins.objects.all().values('vehicleid').filter(vin=a).count()
            dd2 = start_api.objects.all().values('starid').filter(vin=a).count()
            dd3 = undertaking.objects.all().values('vin').filter(vin=a).count()
            dd4 = original_vins.objects.all().values('vin').filter(vin=a).count()
            # -- END CODE -- this code is finalized for checking if vin is in database or not ..

            if dd1 > 0 or dd2 > 0 or dd3 > 0 or dd4 > 0:
                m1 = 'Vin does exist in our database'
                context0 = {'form': form}
                context1 = lookup_vinwash(a, make1, make2, make3, side)
                context2 = lookup_washedvins(a, make1, make2, make3, username, side)
                context3 = lookup_star(a, make1, make2, make3, username, side)
                context4 = lookup_taut(a, make1, make2, make3, username, side)
                context5 = lookup_zoho(a)
                context6 = {'vin': a}
                context7 = lookup_hondafile(a, make1, make2, make3, username, side)
                context8 = lookup_dp(a, make1, make2, make3, username, side)
                #context9 = lookup_oemfiles(a)
                #print(context9)
                context = {**context0, **context1, **context2, **context3, **context4, **context5, **context6, **context7, **context8}
            else:
                m2 = 'Vin does not exist in our database.. wrecker files / star/ undertaking'
                context0 = {'form': form}
                context1 = {
                    'notfound': m2,
                    'na_washedvins': 'yes',
                    'na_star': 'yes',
                    'na_taut': 'yes'
                }
                context2 = lookup_oemfiles(a)
                context = {**context0, **context1, **context2}
    else:
        a = sample
        side = 'default'
        form = VinForm()
        context0 = {'form': form}
        context1 = lookup_vinwash(a, make1, make2, make3, side)
        context2 = lookup_washedvins(a, make1, make2, make3, username, side)
        context3 = lookup_star(a, make1, make2, make3, username, side)
        context4 = lookup_taut(a, make1, make2, make3, username, side)
        context5 = lookup_zoho(a)
        context6 = {'vin': a}
        context7 = lookup_hondafile(a, make1, make2, make3, username, side)
        context8 = lookup_dp(a, make1, make2, make3, username, side)
        context9 = lookup_oemfiles(a)
        print(context9)
        context = {**context0, **context1, **context2, **context3, **context4, **context5, **context6, **context7, **context8, **context9}

    print('# END CODE vin lookup')
    return render(request, 'vinwash/vinlookup.html', context)


def file_upload(request):
    STORAGEACCOUNTNAME = 'djangodevdiag'
    STORAGEACCOUNTKEY = "Y5k5ahE0d1gVlZ8HkeUkG/l3wUd1/f4dApWmS8ua+fi7fxLBI/eqkbMQVPlu1m9uAFXTNQufgja+fSWrVuYTzQ=="
    CONTAINERNAME = 'vinwash'
    BLOBNAME = 'test.csv'
    blob_service = BlockBlobService(account_name=STORAGEACCOUNTNAME, account_key=STORAGEACCOUNTKEY)
    blobstring = blob_service.get_blob_to_text(CONTAINERNAME, BLOBNAME).content
    df = pd.read_csv(StringIO(blobstring))

    context = {
        'prafull': ''
    }
    return render(request, 'vinwash/vinlookup.html', context)