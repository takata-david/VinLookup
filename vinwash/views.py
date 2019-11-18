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
from . forms import vinfileForm
import pandas as pd
import json as js
import requests
from . models import washed_vins, original_vins, vin_conflicts, wiki_vincodes, business, original_extension, start_api, \
    undertaking
from araa import settings
import io
import datetime
from django.db.models import Count
import zcrmsdk as zoho
from django import template

# Create your views here.


def home(request):
    context = {
        'title': 'Wassup homie',
    }
    return render(request, 'vinwash/home.html', context)



def original_vins_data():
    resultdf = pd.DataFrame()
    table_frame = pd.DataFrame(business.objects.values_list('id', 'state'))
    table_frame.columns = ['id', 'state']
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    states = ['NT', 'VIC', 'QLD', 'NSW', 'SA', 'WA', 'TAS', 'ACT']
    for i in months:
        nt = 0
        vic = 0
        qld = 0
        nsw = 0
        sa = 0
        wa = 0
        tas = 0
        act = 0
        # a = original_vins.objects.values('business_id', 'date').filter(date__month__gte=i)
        a = original_vins.objects.values('business_id', 'date') \
            .filter(date__month=i) \
            .annotate(dcount=Count('business_id')).filter(date__year='2019')

        b = pd.DataFrame(a)
        for h in b.iterrows():
            bs = h[1]['business_id']
            dc = h[1]['dcount']
            dt = h[1]['date']
            state = table_frame[table_frame['id'] == bs]['state']

            resultdf = resultdf.append({'month': i, 'state': state.values[0], 'business_id': bs, 'dcount': dc},
                                       ignore_index=True)
    print("current error here")
    print(resultdf.shape)
    if resultdf.shape[0] > 0:
        zzz = resultdf[(resultdf["state"] == 'NSW') & (resultdf["month"] == '01')].sum()["dcount"]
        data = []
        for s in states:
            for m in months:
                z = resultdf[(resultdf["state"] == s) & (resultdf["month"] == m)].sum()["dcount"]
                data.append(int(z))

        ntl = data[0:12]
        vicl = data[12:24]
        qldl = data[24:36]
        nswl = data[36:48]
        sal = data[48:60]
        wal = data[60:72]
        tasl = data[72:84]
        actl = data[84:96]
        return ntl, vicl, qldl, nswl, sal, wal, tasl, actl
    else:
        return '0', '0', '0', '0', '0', '0', '0', '0'


def groups(oem):
    val = ''
    if oem == 'Honda':
        val = ['Honda']
    if oem == 'Nissan':
        val = ['Nissan']
    if oem == 'Toyota' or oem == 'Lexus':
        val = ['Toyota', 'Lexus']
    if oem == 'Mitsubishi':
        val = ['Mitsubishi']
    if oem == 'Holden' or oem == 'SAAB' or oem == 'Opel':
        val = ['Holden', 'SAAB', 'Opel']
    if oem == 'BMW':
        val = ['BMW']
    if oem == 'Ford':
        val = ['Ford']
    if oem == 'Mazda':
        val = ['Mazda']
    if oem == 'Chrysler' or oem == 'Jeep':
        val = ['Chrysler', 'Jeep']
    if oem == 'Subaru':
        val = ['Subaru']

    return val


def months1():
    months = [['10', '2018'], ['11', '2018'], ['12', '2018'], ['01', '2019'], ['02', '2019'], ['03', '2019'], ['04', '2019'],
              ['05', '2019'], ['06', '2019'], ['07', '2019'], ['08', '2019'], ['09', '2019']]
    return months


def washed_vins_bybusiness(oem):   # for current month
    now = datetime.datetime.now()
    current_month = now.strftime('%m')
    current_day = now.strftime('%d')
    if int(current_day) > 25:
        c_m = current_month
    elif (int(current_day) > 0) & (int(current_day) < 25) & (int(current_month) > 1):
        c_m = int(current_month)-1
    else:
        c_m = current_month

    if len(str(c_m)) == 1:
        c_m = '0'+str(c_m)

    tf1 = pd.DataFrame(business.objects.values_list('id', 'state', 'bname'))
    tf1.columns = ['business_id', 'state', 'bname']
    #print(tf1)


    tf2 = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    if tf2.shape[0]>0:
        tf2.columns = ['file_id', 'business_id', 'date']
        #print(tf2)
        df1 = pd.merge(tf2, tf1, on='business_id', how='outer')
        df1 = df1[~df1['file_id'].isna()]
        df1['file_id'] = df1.apply(lambda row: int(row.file_id), axis=1)
        #print(df1)


        a = washed_vins.objects.values('vin', 'file_id', 'isalpha').filter(make=oem)
        b = pd.DataFrame(a)
        #print(b)
        df2 = pd.merge(df1, b, on='file_id', how='outer')
        df2 = df2[~df2['vin'].isna()]
        df2['month'] = df2.apply(lambda row: row.date.strftime('%m'), axis=1)
        df2['year'] = df2.apply(lambda row: row.date.strftime('%Y'), axis=1)
        #print(df2)
        df2 = df2[df2['month'] == str(c_m)]
        df2 = df2[~df2['vin'].isna()]
        #print(df2)
        dfarb = df2
        dfvin = df2.drop_duplicates(subset='vin', keep='first')
        dfalp = df2[df2['isalpha'] == 'True']
        #print(b)
        return df2
    else:
        b = pd.DataFrame()
        return b


def washed_vins_bybusiness_notsold(oem):   # for current month
    now = datetime.datetime.now()
    current_month = now.strftime('%m')
    current_day = now.strftime('%d')
    if int(current_day) > 25:
        c_m = current_month
    elif (int(current_day) > 0) & (int(current_day) < 25) & (int(current_month) > 1):
        c_m = int(current_month)-1
    else:
        c_m = current_month

    if len(str(c_m)) == 1:
        c_m = '0'+str(c_m)

    tf1 = pd.DataFrame(business.objects.values_list('id', 'state', 'bname'))
    tf1.columns = ['business_id', 'state', 'bname']
    #print(tf1)


    tf2 = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    if tf2.shape[0]>0:
        tf2.columns = ['file_id', 'business_id', 'date']
        #print(tf2)
        df1 = pd.merge(tf2, tf1, on='business_id', how='outer')
        df1 = df1[~df1['file_id'].isna()]
        df1['file_id'] = df1.apply(lambda row: int(row.file_id), axis=1)
        #print(df1)


        a = washed_vins.objects.values('vin', 'file_id', 'isalpha').filter(make=oem).exclude(location='sold')
        b = pd.DataFrame(a)
        #print(b)
        df2 = pd.merge(df1, b, on='file_id', how='outer')
        df2 = df2[~df2['vin'].isna()]
        df2['month'] = df2.apply(lambda row: row.date.strftime('%m'), axis=1)
        df2['year'] = df2.apply(lambda row: row.date.strftime('%Y'), axis=1)
        #print(df2)
        df2 = df2[df2['month'] == str(c_m)]
        df2 = df2[~df2['vin'].isna()]
        #print(df2)
        dfarb = df2
        dfvin = df2.drop_duplicates(subset='vin', keep='first')
        dfalp = df2[df2['isalpha'] == 'True']
        #print(b)
        return df2
    else:
        b = pd.DataFrame()
        return b


def washed_vins_data_bystate_byoem(oem):
    now = datetime.datetime.now()
    current_month = now.strftime('%m')
    current_day = now.strftime('%d')
    #print(current_day)
    #print(current_month)
    if int(current_day) > 25:
        c_m = current_month
    elif (int(current_day) > 0) & (int(current_day) < 25) & (int(current_month) > 1):
        c_m = int(current_month)-1
    else:
        c_m = current_month

    if len(str(c_m)) == 1:
        c_m = '0'+str(c_m)
    #print(c_m)
    tf1 = pd.DataFrame(business.objects.values_list('id', 'state'))
    tf1.columns = ['business_id', 'state']

    tf2 = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    if tf2.shape[0]>0:
        tf2.columns = ['file_id', 'business_id', 'date']
        #print(tf2)
        df1 = pd.merge(tf2, tf1, on='business_id', how='outer')
        df1 = df1[~df1['file_id'].isna()]
        df1['file_id'] = df1.apply(lambda row: int(row.file_id), axis=1)

        a = washed_vins.objects.values('vin', 'file_id', 'isalpha').filter(make=oem)
        b = pd.DataFrame(a)
        #print(b)
        df2 = pd.merge(df1, b, on='file_id', how='outer')

        df2 = df2[~df2['vin'].isna()]
        #print(df2)
        df2['month'] = df2.apply(lambda row: row.date.strftime('%m'), axis=1)
        df2['year'] = df2.apply(lambda row: row.date.strftime('%Y'), axis=1)

        df2 = df2[df2['month'] == str(c_m)]

        dfarb = df2
        dfvin = df2.drop_duplicates(subset='vin', keep='first')
        dfalp = df2[df2['isalpha'] == 'True']

        #print(df2)

        states = ['NT', 'VIC', 'QLD', 'NSW', 'SA', 'WA', 'TAS', 'ACT', 'NQLD']
        #data = []
        bgs = []
        vns = []
        alp = []
        for s in states:
            bgs1 = dfarb[dfarb['state'] == s]
            vns1 = dfvin[dfvin['state'] == s]
            alp1 = dfalp[dfalp['state'] == s]
            #z = df2[df2['state'] == s]
            bgs.append(bgs1.shape[0])
            vns.append(vns1.shape[0])
            alp.append(alp1.shape[0])

        #print(states)
        #print(bgs, vns, alp)
        return states, bgs, vns, alp
    else:
        return [], [], [], []


def washed_vins_data_bystate_byoem_notsold(oem):
    now = datetime.datetime.now()
    current_month = now.strftime('%m')
    current_day = now.strftime('%d')
    #print(current_day)
    #print(current_month)
    if int(current_day) > 25:
        c_m = current_month
    elif (int(current_day) > 0) & (int(current_day) < 25) & (int(current_month) > 1):
        c_m = int(current_month)-1
    else:
        c_m = current_month

    if len(str(c_m)) == 1:
        c_m = '0'+str(c_m)
    #print(c_m)
    tf1 = pd.DataFrame(business.objects.values_list('id', 'state'))
    tf1.columns = ['business_id', 'state']

    tf2 = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    if tf2.shape[0]>0:
        tf2.columns = ['file_id', 'business_id', 'date']
        #print(tf2)
        df1 = pd.merge(tf2, tf1, on='business_id', how='outer')
        df1 = df1[~df1['file_id'].isna()]
        df1['file_id'] = df1.apply(lambda row: int(row.file_id), axis=1)

        a = washed_vins.objects.values('vin', 'file_id', 'isalpha').filter(make=oem).exclude(location='sold')
        b = pd.DataFrame(a)
        #print(b)
        df2 = pd.merge(df1, b, on='file_id', how='outer')

        df2 = df2[~df2['vin'].isna()]
        #print(df2)
        df2['month'] = df2.apply(lambda row: row.date.strftime('%m'), axis=1)
        df2['year'] = df2.apply(lambda row: row.date.strftime('%Y'), axis=1)

        df2 = df2[df2['month'] == str(c_m)]

        dfarb = df2
        dfvin = df2.drop_duplicates(subset='vin', keep='first')
        dfalp = df2[df2['isalpha'] == 'True']

        #print(df2)

        states = ['NT', 'VIC', 'QLD', 'NSW', 'SA', 'WA', 'TAS', 'ACT', 'NQLD']
        #data = []
        bgs = []
        vns = []
        alp = []
        for s in states:
            bgs1 = dfarb[dfarb['state'] == s]
            vns1 = dfvin[dfvin['state'] == s]
            alp1 = dfalp[dfalp['state'] == s]
            #z = df2[df2['state'] == s]
            bgs.append(bgs1.shape[0])
            vns.append(vns1.shape[0])
            alp.append(alp1.shape[0])

        #print(states)
        #print(bgs, vns, alp)
        return states, bgs, vns, alp
    else:
        return [], [], [], []


def washed_vins_data_bymonth():
    table_frame = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    #print(len(table_frame))
    if len(table_frame)>0:
        table_frame.columns = ['file_id', 'business_id', 'date']
        a = table_frame.shape
        #print("shape of empty table")
        #print(a)
        table_frame['month'] = table_frame.apply(lambda row: row.date.strftime('%m'), axis=1)
        table_frame['year'] = table_frame.apply(lambda row: row.date.strftime('%Y'), axis=1)

        months = months1()
        states = ['NT', 'VIC', 'QLD', 'NSW', 'SA', 'WA', 'TAS', 'ACT']
        a = washed_vins.objects.values('vin', 'file_id', 'isalpha')
        b = pd.DataFrame(a)
        #print(b)
        df1 = pd.merge(table_frame, b, on='file_id', how='outer')
        #print(df1)
        df1 = df1[~df1['vin'].isna()]
        #print(df1)
        #df1 = df1[df1['year'] == '2019']
        dfx = df1
        dfx = dfx.drop_duplicates(subset='vin', keep='first')
        dfy = df1[df1['isalpha'] == 'True']
        airbags1 = []
        vins1 = []
        alpha1 = []
        period_size = len(months)
        #print(period_size)
        for m in months:
            df2 = df1[(df1['month'] == m[0]) & (df1['year'] == m[1])]
            df3 = dfx[(dfx['month'] == m[0]) & (dfx['year'] == m[1])]
            df4 = dfy[(dfy['month'] == m[0]) & (dfy['year'] == m[1])]
            airbags = int(df2.shape[0])
            vins = int(df3.shape[0])
            alpha = int(df4.shape[0])
            airbags1.append(int(airbags))
            vins1.append(int(vins))
            alpha1.append(int(alpha))
        return airbags1, alpha1, vins1, period_size
    else:
        return '0', '0', '0', '0'


def washed_vins_data_bymonth_notsold():
    table_frame = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    #print(len(table_frame))
    if len(table_frame)>0:
        table_frame.columns = ['file_id', 'business_id', 'date']
        a = table_frame.shape
        #print("shape of empty table")
        #print(a)
        table_frame['month'] = table_frame.apply(lambda row: row.date.strftime('%m'), axis=1)
        table_frame['year'] = table_frame.apply(lambda row: row.date.strftime('%Y'), axis=1)

        months = months1()
        states = ['NT', 'VIC', 'QLD', 'NSW', 'SA', 'WA', 'TAS', 'ACT']
        a = washed_vins.objects.values('vin', 'file_id', 'isalpha').exclude(location='sold')
        b = pd.DataFrame(a)
        #print(b)
        df1 = pd.merge(table_frame, b, on='file_id', how='outer')
        #print(df1)
        df1 = df1[~df1['vin'].isna()]
        #print(df1)
        #df1 = df1[df1['year'] == '2019']
        dfx = df1
        dfx = dfx.drop_duplicates(subset='vin', keep='first')
        dfy = df1[df1['isalpha'] == 'True']
        airbags1 = []
        vins1 = []
        alpha1 = []
        period_size = len(months)
        #print(period_size)
        for m in months:
            df2 = df1[(df1['month'] == m[0]) & (df1['year'] == m[1])]
            df3 = dfx[(dfx['month'] == m[0]) & (dfx['year'] == m[1])]
            df4 = dfy[(dfy['month'] == m[0]) & (dfy['year'] == m[1])]
            airbags = int(df2.shape[0])
            vins = int(df3.shape[0])
            alpha = int(df4.shape[0])
            airbags1.append(int(airbags))
            vins1.append(int(vins))
            alpha1.append(int(alpha))
        return airbags1, alpha1, vins1, period_size
    else:
        return '0', '0', '0', '0'




def original_vins_data_bymonth():
    df1 = pd.DataFrame()
    table_frame = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    months = months1()
    period_size = len(months)
    if table_frame.shape[0]>0:
        table_frame.columns = ['file_id', 'business_id', 'date']
        table_frame['month'] = table_frame.apply(lambda row: row.date.strftime('%m'), axis=1)
        table_frame['year'] = table_frame.apply(lambda row: row.date.strftime('%Y'), axis=1)
        #print(table_frame)
        #print(period_size)
        a = original_vins.objects.values('vin', 'file_id')
        b = pd.DataFrame(a)
        #print(b)
        #data2 = pd.DataFrame()
        df1 = pd.merge(table_frame, b, on='file_id', how='outer')
        df1 = df1[~df1['vin'].isna()]
        #print(df1)
        #df1 = df1[df1['year'] == '2019']
        dfx = df1
        vins1 = []
        for m in months:
            df3 = dfx[(dfx['month'] == m[0]) & (dfx['year'] == m[1])]
            vins = int(df3.shape[0])
            vins1.append(int(vins))
            #print('1')
            #print(vins1)
            #print('2')
            #print(period_size)
        return vins1, period_size
    else:
        return [0], 0


def original_vins_data_bymonth_notsold():
    df1 = pd.DataFrame()
    table_frame = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    months = months1()
    period_size = len(months)
    if table_frame.shape[0]>0:
        table_frame.columns = ['file_id', 'business_id', 'date']
        table_frame['month'] = table_frame.apply(lambda row: row.date.strftime('%m'), axis=1)
        table_frame['year'] = table_frame.apply(lambda row: row.date.strftime('%Y'), axis=1)
        #print(table_frame)
        #print(period_size)
        a = original_vins.objects.values('vin', 'file_id').exclude(location='sold')
        b = pd.DataFrame(a)
        #print(b)
        #data2 = pd.DataFrame()
        df1 = pd.merge(table_frame, b, on='file_id', how='outer')
        df1 = df1[~df1['vin'].isna()]
        #print(df1)
        #df1 = df1[df1['year'] == '2019']
        dfx = df1
        vins1 = []
        for m in months:
            df3 = dfx[(dfx['month'] == m[0]) & (dfx['year'] == m[1])]
            vins = int(df3.shape[0])
            vins1.append(int(vins))
            #print('1')
            #print(vins1)
            #print('2')
            #print(period_size)
        return vins1, period_size
    else:
        return [0], 0


'''
def months1():
    months = [['04', '2019']]
    return months
'''


def washed_vins_data_bymonth_byoem(oem):
    months = months1()
    table_frame = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    if table_frame.shape[0] > 0:
        table_frame.columns = ['file_id', 'business_id', 'date']
        table_frame['month'] = table_frame.apply(lambda row: row.date.strftime('%m'), axis=1)
        table_frame['year'] = table_frame.apply(lambda row: row.date.strftime('%Y'), axis=1)
        a = washed_vins.objects.values('vin', 'file_id', 'isalpha').filter(make=oem)
        b = pd.DataFrame(a)
        #print('washed vins')
        #print('oem airbag count affected')
        #print(b.shape)
        df1 = pd.merge(table_frame, b, on='file_id', how='outer')
        df1 = df1[~df1['vin'].isna()]
        #print(df1)
        #df1 = df1[df1['year'] == '2019']


        dfx = df1
        dfx = dfx.drop_duplicates(subset='vin', keep='first')
        #print('unique vins')
        #print(dfx.shape)
        #print(dfx)
        dfy = df1[df1['isalpha'] == 'True']
        airbags1 = []
        vins1 = []
        alpha1 = []
        period_size = len(months)
        #print(period_size)
        for m in months:
            df2 = df1[(df1['month'] == m[0]) & (df1['year'] == m[1])]
            df3 = dfx[(dfx['month'] == m[0]) & (dfx['year'] == m[1])]
            df4 = dfy[(dfy['month'] == m[0]) & (dfy['year'] == m[1])]
            airbags = int(df2.shape[0])
            vins = int(df3.shape[0])
            alpha = int(df4.shape[0])
            airbags1.append(int(airbags))
            vins1.append(int(vins))
            alpha1.append(int(alpha))
        return airbags1, alpha1, vins1, period_size
    else:
        return [], [], [], []


def washed_vins_data_bymonth_byoem_notsold(oem):
    months = months1()
    table_frame = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    if table_frame.shape[0] > 0:
        table_frame.columns = ['file_id', 'business_id', 'date']
        table_frame['month'] = table_frame.apply(lambda row: row.date.strftime('%m'), axis=1)
        table_frame['year'] = table_frame.apply(lambda row: row.date.strftime('%Y'), axis=1)
        a = washed_vins.objects.values('vin', 'file_id', 'isalpha').filter(make=oem).exclude(location='sold')
        b = pd.DataFrame(a)
        #print('washed vins')
        #print('oem airbag count affected')
        #print(b.shape)
        df1 = pd.merge(table_frame, b, on='file_id', how='outer')
        df1 = df1[~df1['vin'].isna()]
        #print(df1)
        #df1 = df1[df1['year'] == '2019']


        dfx = df1
        dfx = dfx.drop_duplicates(subset='vin', keep='first')
        #print('unique vins')
        #print(dfx.shape)
        #print(dfx)
        dfy = df1[df1['isalpha'] == 'True']
        airbags1 = []
        vins1 = []
        alpha1 = []
        period_size = len(months)
        #print(period_size)
        for m in months:
            df2 = df1[(df1['month'] == m[0]) & (df1['year'] == m[1])]
            df3 = dfx[(dfx['month'] == m[0]) & (dfx['year'] == m[1])]
            df4 = dfy[(dfy['month'] == m[0]) & (dfy['year'] == m[1])]
            airbags = int(df2.shape[0])
            vins = int(df3.shape[0])
            alpha = int(df4.shape[0])
            airbags1.append(int(airbags))
            vins1.append(int(vins))
            alpha1.append(int(alpha))
        return airbags1, alpha1, vins1, period_size
    else:
        return [], [], [], []



@login_required
def oem_report(request, oem):
    months = months1()
    x = groups(oem)

    var = months
    airbags1, alpha1, vins1, period_size1 = washed_vins_data_bymonth() # for all oem
    o_vins_bymonth, period_size2 = original_vins_data_bymonth()

    var.append(["Total", ""])
    if len(vins1)>1:
        vins1.append(sum(vins1))
        alpha1.append(sum(alpha1))
        airbags1.append(sum(airbags1))
        o_vins_bymonth.append(sum(o_vins_bymonth))
    else:
        pass

    zipped_list = zip(var, vins1, alpha1, airbags1, o_vins_bymonth)
    context = {
        'zip': zipped_list,
        'oem': x
    }

    # ------------------------------------------------------------- not sold --------------------------
    airbags11, alpha11, vins11, period_size11 = washed_vins_data_bymonth_notsold()  # for all oem

    o_vins_bymonth2, period_size22 = original_vins_data_bymonth_notsold()

    var.append(["Total", ""])
    if len(vins1) > 1:
        vins11.append(sum(vins11))
        alpha11.append(sum(alpha11))
        airbags11.append(sum(airbags11))
        o_vins_bymonth2.append(sum(o_vins_bymonth2))
        #print(vins11, alpha11, airbags11, o_vins_bymonth2)
    else:
        pass

    zipped_list_notsold = zip(var, vins11, alpha11, airbags11, o_vins_bymonth2)
    context.update({'zip_notsold': zipped_list_notsold})
    # ------------------------------------------------------------- not sold --------------------------




    #context.update({'by_biz1': zipped_list_biz})

    # this is for particular oem

    keyss_notsold = ['oem1_notsold', 'oem2_notsold', 'oem3_notsold']
    keyss = ['oem1', 'oem2', 'oem3']
    keyss1 = ['oem11', 'oem22', 'oem33']
    keyss1_notsold = ['oem11_notsold', 'oem22_notsold', 'oem33_notsold']
    keyss11 = ['oem111', 'oem222', 'oem333']
    keyss11_notsold = ['oem111_notsold', 'oem222_notsold', 'oem333_notsold']
    names = ['name1', 'name2', 'name3']
    i = 0
    for o in x:
        #print(o)
        # ---------------------------------------------- by month by oem :: not sold ---------------------------------
        airbags1o_notsold, alpha1o_notsold, vins1o_notsold, period_size1o_notsold \
            = washed_vins_data_bymonth_byoem_notsold(o)  # for pecific oem
        vins1o_notsold.append(sum(vins1o_notsold))
        alpha1o_notsold.append(sum(alpha1o_notsold))
        airbags1o_notsold.append(sum(airbags1o_notsold))

        zipped_list1_notsold = zip(var, vins1o_notsold, alpha1o_notsold, airbags1o_notsold)
        context.update({keyss_notsold[i]: zipped_list1_notsold})
        # ---------------------------------------------- by month by oem :: not sold ---------------------------------




        airbags1o, alpha1o, vins1o, period_size1o = washed_vins_data_bymonth_byoem(o) # for pecific oem
        #print(vins1o)
        vins1o.append(sum(vins1o))
        alpha1o.append(sum(alpha1o))
        airbags1o.append(sum(airbags1o))
        #wordFreqDic.update( {'before' : 23} )
        zipped_list1 = zip(var, vins1o, alpha1o, airbags1o)
        context.update({keyss[i]: zipped_list1})
        context.update({names[i]: o})
        # ------------------------------------------ by state by oem not SOLD ------------------------------
        states_notsold, bgs_notsold, vns_notsold, alp_notsold = washed_vins_data_bystate_byoem_notsold(o)
        ss_notsold = states_notsold + ['Total']
        bgs_notsold.append(sum(bgs_notsold))
        vns_notsold.append(sum(vns_notsold))
        alp_notsold.append(sum(alp_notsold))
        # print(ss)
        # print(alp)
        # print(vns)
        # print(bgs)
        zipped_list2_notsold = zip(ss_notsold, bgs_notsold, vns_notsold, alp_notsold)
        context.update({keyss1_notsold[i]: zipped_list2_notsold})
        # ------------------------------------------ by state by oem not SOLD ------------------------------
        states, bgs, vns, alp = washed_vins_data_bystate_byoem(o)
        ss = states + ['Total']
        bgs.append(sum(bgs))
        vns.append(sum(vns))
        alp.append(sum(alp))
        #print(ss)
        #print(alp)
        #print(vns)
        #print(bgs)
        zipped_list2 = zip(ss, bgs, vns, alp)
        context.update({keyss1[i]: zipped_list2})
        # --------------------------------------- last section of report
        dfb = washed_vins_bybusiness(o)  # data frame business wise
        dfb_notsold = washed_vins_bybusiness_notsold(o)  # data frame business wise
        if dfb.shape[0]>0:
            biz_df = dfb.drop_duplicates(subset='business_id', keep='first')
            bizid = biz_df['business_id'].tolist()
            biznm = biz_df['bname'].tolist()
            #print(biznm)
            #print(bizid)
            #print(biz_df)
            dfarb = []
            dfvin = []
            dfalp = []

            for bi in bizid:
                bhalu = dfb[dfb['business_id'] == bi]
                pass
                d = bhalu
                e = bhalu.drop_duplicates(subset='vin', keep='first')
                f = bhalu[bhalu['isalpha'] == 'True']

                dfarb.append(int(d.shape[0]))
                dfvin.append(int(e.shape[0]))
                dfalp.append(int(f.shape[0]))

            biznm = biznm + ['Total']
            dfarb.append(sum(dfarb))
            dfvin.append(sum(dfvin))
            dfalp.append(sum(dfalp))
            zipped_list_biz = zip(biznm, dfarb, dfvin, dfalp)
            context.update({keyss11[i]: zipped_list_biz})
            # --------------------------------------- last section of report
            # ---------------------------------- NOT SOLD business wise ----------------------------------------
            if dfb_notsold.shape[0] > 0:
                biz_df_notsold = dfb_notsold.drop_duplicates(subset='business_id', keep='first')
                bizid_notsold = biz_df_notsold['business_id'].tolist()
                biznm_notsold = biz_df_notsold['bname'].tolist()
                # print(biznm)
                # print(bizid)
                # print(biz_df)
                dfarb_notsold = []
                dfvin_notsold = []
                dfalp_notsold = []

                for bi_notsold in bizid_notsold:
                    bhalu_notsold = dfb_notsold[dfb_notsold['business_id'] == bi_notsold]
                    pass
                    d_notsold = bhalu_notsold
                    e_notsold = bhalu_notsold.drop_duplicates(subset='vin', keep='first')
                    f_notsold = bhalu_notsold[bhalu_notsold['isalpha'] == 'True']

                    dfarb_notsold.append(int(d_notsold.shape[0]))
                    dfvin_notsold.append(int(e_notsold.shape[0]))
                    dfalp_notsold.append(int(f_notsold.shape[0]))

                biznm_notsold = biznm_notsold + ['Total']
                dfarb_notsold.append(sum(dfarb_notsold))
                dfvin_notsold.append(sum(dfvin_notsold))
                dfalp_notsold.append(sum(dfalp_notsold))
                zipped_list_biz_notsold = zip(biznm_notsold, dfarb_notsold, dfvin_notsold, dfalp_notsold)
                context.update({keyss11_notsold[i]: zipped_list_biz_notsold})
            # ---------------------------------- NOT SOLD business wise ----------------------------------------

            i = i + 1

    #print(context)
    return render(request, 'vinwash/oem.html', context)


@login_required
def file_count(request):
    tf1 = pd.DataFrame(business.objects.values_list('id', 'state', 'bname'))
    tf1.columns = ['business_id', 'state', 'bname']
    # print(tf1)

    tf2 = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date', 'filename'))
    tf2.columns = ['file_id', 'business_id', 'date', 'filename']

    df1 = pd.merge(tf2, tf1, on='business_id', how='outer')
    df1 = df1[~df1['file_id'].isna()]
    df1['month'] = df1.apply(lambda row: row.date.strftime('%m'), axis=1)
    df1['year'] = df1.apply(lambda row: row.date.strftime('%Y'), axis=1)
    #print(df1)
    month_file_count = []
    months = months1()
    for m in months:
        df3 = df1[(df1['month'] == m[0]) & (df1['year'] == m[1])]
        dfx = df3.drop_duplicates(subset='bname', keep='first')
        #print(dfx)
        month_files2 = df3.shape[0]
        month_files1 = dfx.shape[0]
        #print(m, month_files1)
        print(m, month_files2)
        #month_file_count.append(month_files)
    #print(tf2)
    '''
    now = datetime.datetime.now()
    current_month = now.strftime('%m')
    current_day = now.strftime('%d')
    if int(current_day) > 25:
        c_m = current_month
    elif (int(current_day) > 0) & (int(current_day) < 25) & (int(current_month) > 1):
        c_m = int(current_month) - 1
    else:
        c_m = current_month

    if len(str(c_m)) == 1:
        c_m = '0' + str(c_m)

    tf1 = pd.DataFrame(business.objects.values_list('id', 'state', 'bname'))
    tf1.columns = ['business_id', 'state', 'bname']
    # print(tf1)

    tf2 = pd.DataFrame(vinfile.objects.values_list('id', 'business_id', 'date'))
    tf2.columns = ['file_id', 'business_id', 'date']
    # print(tf2)
    df1 = pd.merge(tf2, tf1, on='business_id', how='outer')
    df1 = df1[~df1['file_id'].isna()]
    df1['file_id'] = df1.apply(lambda row: int(row.file_id), axis=1)
    # print(df1)

    a = washed_vins.objects.values('vin', 'file_id', 'isalpha').filter(make=oem)
    b = pd.DataFrame(a)
    # print(b)
    df2 = pd.merge(df1, b, on='file_id', how='outer')

    df2['month'] = df2.apply(lambda row: row.date.strftime('%m'), axis=1)
    df2['year'] = df2.apply(lambda row: row.date.strftime('%Y'), axis=1)

    df2 = df2[df2['month'] == str(c_m)]
    df2 = df2[~df2['vin'].isna()]
    '''
    return render(request, 'vinwash/file_count.html')




@login_required
def dashboard(request):
    airbags1, alpha1, vins1, period_size = washed_vins_data_bymonth()
    a = len(airbags1)
    print('printing this')
    print(a)
    print('printing this')
    ntl, vicl, qldl, nswl, sal, wal, tasl, actl = original_vins_data()
    context = {
        'nt': ntl,
        'vic': vicl,
        'qld': qldl,
        'nsw': nswl,
        'sa': sal,
        'wa': wal,
        'tas': tasl,
        'act': actl,
        'w_vins': vins1,
        'w_airbags': airbags1,
        'w_alpha': alpha1
    }
    return render(request, 'vinwash/dashboard.html', context)


@login_required
def process(request):
    return render(request, 'vinwash/process.html')


'''
class FileCreateView(LoginRequiredMixin, CreateView):
    model = vinfile
    fields = ['filename', 'date', 'user', 'notes']
    #jimmy = business.objects.get(id=1)
    def form_valid(self, form):
        form.instance.business = business.objects.get(id=1)
        return super().form_valid(form)


class FileDetailView(DetailView):
    model = vinfile


def upload(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        print(uploaded_file.name)
        print(uploaded_file.size)
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, request.FILES['document'])
        url = fs.url(name)
        context = {
            'url': url
        }
        print(url)
    else:
        context = {
            'url': 'nothing to upload'
        }
    return render(request, 'vinwash/upload_useless.html', context)
'''


def file_list(request):
    return render(request, 'vinwash/file_list.html')


def original_vinsdb(df, fileid):

    '''
    list1 = original_vins.objects.values_list('vin', flat=True)
    vin_list = list(list1)
    print(vin_list)
    dup_vins = df[df['vin'].isin(vin_list)] # duplicate b/w 2 files
    print(dup_vins['vin'])
    dup_data = original_vins.objects.filter(vin__in=list(dup_vins['vin'])).values_list('vin', 'file_id')
    #dup_data = original_vins.objects.filter(vin__in=list(dup_vins))
    print(dup_data)
    for (vin, filid) in dup_data:
        instance = vin_conflicts(vin=vin, originalvins_business=filid, conflict_location='a', conflict_stocknumber='b',
                                 conflict_filename=fileid, cnflict_business_id=1)
        instance.save()

    df = df[~df['vin'].isin(vin_list)]

    for j in df.iterrows():
        vn = j[1]['vin']
        lc = j[1]['location']
        st = j[1]['stock']
        instance = original_vins(vin=vn, location=lc, stock_number=st, date='2019-07-24', file_id=fileid,
                                     business_id=1)
        instance.save()

    return df
    '''
    #return vin_list

'''
def validate_vins(df):
    df = df[df['vin'].apply(lambda x: len(x) == 17)]
    #df['vin'] = df['vin'].str.replace(['.', ',', ';', ':', '+', '-', '_', '=', '/'], '')
    df['vin'] = df['vin'].str.replace('i', '1')
    df['vin'] = df['vin'].str.replace('o', '0')
    return df
'''

def processcsv(df, fileid):

    #df1 = validate_vins(df)  #validate original vins
    df1 = original_vinsdb(df, fileid)  # save original vins to database

    dfToList = df1['vin'].tolist()
    url = "https://takatalive.com/api/takata/bulk"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=js.dumps(dfToList), headers=headers)
    p = r.json()
    j = js.loads(p)
    result = j['Result']

    resultdf = pd.DataFrame(columns=['VehicleAirbagID', 'VehicleID', 'VIN', 'PRANum', 'Make', 'Model', 'Series', 'Year',
                                     'AirbagLocation', 'IsAlpha', 'IsSubmitted'])
    if result != None:
        for k in result:
            VehicleAirbagID = str(k['VehicleAirbagID'])
            VehicleID = str(k['VehicleID'])
            VIN = str(k['VIN'])
            PRANum = str(k['PRANum'])
            Make = str(k['Make'])
            Model = str(k['Model'])
            Series = str(k['Series'])
            Year = str(k['Year'])
            AirbagLocation = str(k['AirbagLocation'])
            IsAlpha = str(k['IsAlpha'])
            IsSubmitted = str(k['IsSubmitted'])

            resultdf = resultdf.append({'VehicleAirbagID': VehicleAirbagID,
                                        'VehicleID': VehicleID,
                                        'VIN': VIN,
                                        'PRANum': PRANum,
                                        'Make': Make,
                                        'Model': Model,
                                        'Series': Series,
                                        'Year': Year,
                                        'AirbagLocation': AirbagLocation,
                                        'IsAlpha': IsAlpha,
                                        'IsSubmitted': IsSubmitted
                                        }, ignore_index=True)

            instance = washed_vins(vehicleairbagid=VehicleAirbagID, vehicleid=VehicleID, vin=VIN, pranum=PRANum,
                                   make=Make, model=Model, series=Series, year=Year, airbaglocation=AirbagLocation,
                                   isalpha=IsAlpha, issubmitted=IsSubmitted, bagcollectiondate='2019-07-24',
                                   business_id=1)
            instance.save()
    return resultdf

    #return df1

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = vinfileForm(request.POST, request.FILES)
        if form.is_valid():
            bid = request.POST.get('business')
            udt = request.POST.get('date')
            udt = datetime.datetime.strptime(udt, "%d/%m/%Y").strftime("%Y-%m-%d")
            print('business id after this')
            print(bid)
            uploaded_file = request.FILES['filename']

            of = pd.read_csv(uploaded_file, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                             encoding='latin1', sep=',')
            of.columns = ['vin', 'location', 'stock', 'image', 'model', 'year', 'inventoried', 'odoreading', 'engine',
                          'gearboxtype', 'gears', 'doors', 'site', 'registration', 'cod', 'enginenumber',
                          'purchasedate',
                          'fueltype', 'bodystyle', 'classification']
            forminstance = form.save()
            recordid = forminstance.pk

            df = of
            df['vin'] = df['vin'].str.replace('.', '')
            df['vin'] = df['vin'].str.replace(',', '')
            df['vin'] = df['vin'].str.replace(';', '')
            df['vin'] = df['vin'].str.replace('\'', '')
            df['vin'] = df['vin'].str.replace(':', '')
            df['vin'] = df['vin'].str.replace('+', '')
            df['vin'] = df['vin'].str.replace('=', '')
            df['vin'] = df['vin'].str.replace('@', '')
            df['vin'] = df['vin'].str.replace('#', '')
            df['vin'] = df['vin'].str.replace('$', '')
            df['vin'] = df['vin'].str.replace('%', '')
            df['vin'] = df['vin'].str.replace('^', '')
            df['vin'] = df['vin'].str.replace('&', '')
            df['vin'] = df['vin'].str.replace('*', '')

            df = df[df['vin'].apply(lambda x: len(str(x)) == 17)]
            df['vin'] = df['vin'].str.replace('i', '1')
            df['vin'] = df['vin'].str.replace('o', '0')
            df = df.drop_duplicates(subset='vin', keep='first')

            list1 = original_vins.objects.values_list('vin', flat=True)
            vin_list = list(list1)
            dup_vins = df[df['vin'].isin(vin_list)]  # duplicate b/w 2 files
            dup_data = original_vins.objects.filter(vin__in=list(dup_vins['vin'])).values_list('vin', 'file_id')

            if len(list(dup_vins['vin'])) > 0:
                for (vin, filid) in dup_data:
                    e1 = vinfile.objects.get(id=filid)
                    c1 = e1.business_id

                    e2 = vinfile.objects.get(id=recordid)
                    c2 = e2.business_id

                    if c1 == c2:
                        pass
                    else:
                        instance = vin_conflicts(vin=vin, previous_occurence_fileid=filid,
                                                 current_occurence_fileid=recordid,
                                                 conflict_location='', conflict_stocknumber='')
                        instance.save()

            df = df[~df['vin'].isin(vin_list)]  # unique vins
            if df.shape[0] > 0:
                table_frame = pd.DataFrame(wiki_vincodes.objects.values_list('id', 'code', 'make'))
                table_frame.columns = ['id', 'code', 'make']
                prefix_list = list(table_frame['code'])
                for h in df.iterrows():
                    vn = h[1]['vin']
                    lc = h[1]['location']
                    st = h[1]['stock']
                    img = h[1]['image']
                    ext = 'JPG'
                    if pd.isnull(img):
                        loc = ''
                    else:
                        loc = img + '.' + ext
                    pre3 = vn[0:3]
                    pre2 = vn[0:2]
                    if pre2 in prefix_list:
                        m_oem = int(table_frame[table_frame['code'] == pre2]['id'])
                    elif pre3 in prefix_list:
                        m_oem = int(table_frame[table_frame['code'] == pre3]['id'])
                    else:
                        m_oem = ''

                    instance = original_vins(vin=vn, location=lc, stock_number=st, date=udt, file_id=recordid,
                                             business_id=bid, wiki_id=m_oem, img=loc)
                    instance.save()

                    sdsf = ['model', 'year', 'inventoried', 'odoreading', 'engine',
                            'gearboxtype', 'gears', 'doors', 'site', 'registration', 'cod', 'enginenumber',
                            'purchasedate',
                            'fueltype', 'bodystyle', 'classification']

                    instance1 = original_extension(vin=vn, model=h[1]['model'], year=h[1]['year'],
                                                   inventoried=h[1]['inventoried'],
                                                   odoreading=h[1]['odoreading'], engine=h[1]['engine'],
                                                   gearboxtype=h[1]['gearboxtype'],
                                                   gears=h[1]['gears'], doors=h[1]['doors'], sute=h[1]['site'],
                                                   registration=h[1]['registration'],
                                                   cod=h[1]['cod'], enginenumber=h[1]['enginenumber'],
                                                   purchasedate=h[1]['purchasedate'],
                                                   fueltype=h[1]['fueltype'], bodystyle=h[1]['bodystyle'],
                                                   classification=h[1]['classification'])
                    instance1.save()

                df1 = df
                dfToList = df1['vin'].tolist()
                url = "https://takatalive.com/api/takata/bulk"
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                r = requests.post(url, data=js.dumps(dfToList), headers=headers)
                p = r.json()
                j = js.loads(p)
                result = j['Result']

                resultdf = pd.DataFrame(
                    columns=['VehicleAirbagID', 'VehicleID', 'VIN', 'PRANum', 'Make', 'Model', 'Series', 'Year',
                             'AirbagLocation', 'IsAlpha', 'IsSubmitted'])

                if result != None:
                    for k in result:
                        VehicleAirbagID = str(k['VehicleAirbagID'])
                        VehicleID = str(k['VehicleID'])
                        VIN = str(k['VIN'])
                        PRANum = str(k['PRANum'])
                        Make = str(k['Make'])
                        Model = str(k['Model'])
                        Series = str(k['Series'])
                        Year = str(k['Year'])
                        AirbagLocation = str(k['AirbagLocation'])
                        IsAlpha = str(k['IsAlpha'])
                        IsSubmitted = str(k['IsSubmitted'])

                        stk_frame = df[df['vin'] == VIN]

                        if len(stk_frame['stock'].values) > 0:
                            stk = stk_frame['stock'].values[0]
                            lac = stk_frame['location'].values[0]
                        else:
                            stk = ''
                            lac = ''

                        resultdf = resultdf.append({'VehicleAirbagID': VehicleAirbagID,
                                                    'VehicleID': VehicleID,
                                                    'VIN': VIN,
                                                    'PRANum': PRANum,
                                                    'Make': Make,
                                                    'Model': Model,
                                                    'Series': Series,
                                                    'Year': Year,
                                                    'AirbagLocation': AirbagLocation,
                                                    'IsAlpha': IsAlpha,
                                                    'IsSubmitted': IsSubmitted
                                                    }, ignore_index=True)

                        instance1 = washed_vins(vehicleid=VehicleID, vin=VIN, pranum=PRANum,
                                                make=Make, model=Model, series=Series, year=Year,
                                                airbaglocation=AirbagLocation,
                                                isalpha=IsAlpha, issubmitted=IsSubmitted,
                                                bagcollectiondate="2015-11-22",
                                                file_id=recordid, stock_number=stk, location=lac)
                        instance1.save()





            print(recordid)

    else:
        form = vinfileForm()
    context = {
        'form': form
    }
    return render(request, 'vinwash/upload_file.html', context)


def undertaking_detailed_upload(request):
    pass


def undertaking_upload(request):
    url = "http://takataundertakings.com/getdetailedlist"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.get(url, headers=headers)
    p = r.json()
    j = js.loads(p)
    mm = 0
    for i in j:
         UndertakingSubmissionID = i['UndertakingSubmissionID']
         VIN = i['VIN']
         BarCode = i['BarCode']
         AirbagLocation = i['AirbagLocation']
         Make = i['Make']
         Model = i['Model']
         Series = i['Series']
         Year = i['Year']
         PRANum = i['PRANum']
         IsAlpha = i['IsAlpha']
         NotificationDate = i['NotificationDate']
         NotifFirstName = i['NotifFirstName']
         NotifLastName = i['NotifLastName']
         FirstName = i['FirstName']
         LastName = i['LastName']
         CompanyID = i['CompanyID']
         RecyclerABN = i['RecyclerABN']
         CompanyName = i['CompanyName']
         TradingName = i['TradingName']
         Street = i['Street']
         City = i['City']
         StateCode = i['StateCode']
         PostCode = i['PostCode']
         Email = i['Email']
         BusinessPhone = i['BusinessPhone']
         Fax = i['Fax']
         Website = i['Website']
         Title = i['Title']
         Phone = i['Phone']
         ContactEmail = i['ContactEmail']
         AccountName = i['AccountName']
         BSB = i['BSB']
         AccountNumber = i['AccountNumber']
         Status = i['Status']
         Condition = i['Condition']
         LicenseDetail = i['LicenseDetail']
         SellerCompanyName = i['SellerCompanyName']
         SellerEmail = i['SellerEmail']
         SellerPhone = i['SellerPhone']
         SellerFName = i['SellerFName']
         SellerLName = i['SellerLName']
         SellerFullName = i['SellerFullName']
         OwnerCompanyName = i['OwnerCompanyName']
         OwnerEmail = i['OwnerEmail']
         OwnerPhone = i['OwnerPhone']
         OwnerFName = i['OwnerFName']
         OwnerLName = i['OwnerLName']
         OwnerFullName = i['OwnerFullName']
         UploadedImageCount = i['UploadedImageCount']
         DateOfSale = i['DateOfSale']
         WriteOffTypeID = i['WriteOffTypeID']
         WrittenOffType = i['WrittenOffType']
         DateSigned = i['DateSigned']

         instance = undertaking(accountName=AccountName, accountNumber=AccountNumber, airbagLocation=AirbagLocation,
                                barcode=BarCode, bsb=BSB, businessPhone=BusinessPhone, city=City, companyID=CompanyID,
                                companyName=CompanyName, condition=Condition, contactEmail=ContactEmail,
                                dateOfSale=DateOfSale, dateSigned=DateSigned, email=Email, fax=Fax, firstName=FirstName,
                                isAlpha=IsAlpha, lastName=LastName, licenseDetail=LicenseDetail, make=Make, model=Model,
                                notifFirstName=NotifFirstName, notifLastName=NotifLastName,
                                notificationDate=NotificationDate, ownerCompanyName=OwnerCompanyName,
                                ownerEmail=OwnerEmail, ownerFName=OwnerFName, ownerFullName=OwnerFullName,
                                ownerLName=OwnerLName, ownerPhone=OwnerPhone, phone=Phone, postCode=PostCode,
                                praNum=PRANum, recyclerABN=RecyclerABN, sellerCompanyName=SellerCompanyName,
                                sellerEmail=SellerEmail, sellerFName=SellerFName, sellerFullName=SellerFullName,
                                sellerLName=SellerLName, sellerPhone=SellerPhone, series=Series, stateCode=StateCode,
                                status=Status, street=Street, title=Title, tradingName=TradingName,
                                uid=UndertakingSubmissionID, uploadedImageCount=UploadedImageCount, vin=VIN,
                                website=Website, writeOffTypeID=WriteOffTypeID, writtenOffType=WrittenOffType, year=Year
                                )
         instance.save()

         print(i['VIN'])
         mm = mm + 1
         #if mm == 10:
            #break
    return render(request, 'vinwash/upload_file.html')



def add_star_id(request):
    table_frame = pd.DataFrame(start_api.objects.values_list('vin','starid','airbaglocation'))
    table_frame.columns = ['vin', 'starid', 'loc']
    #print(table_frame)

    mm = 0
    for j in table_frame.iterrows():
        vin = j[1]['vin']
        print(mm,vin)
        starid = j[1]['starid']
        loc = j[1]['loc']
        washed_vins.objects.filter(vin=vin).filter(airbaglocation=loc).update(starid=starid)
        #if mm==10:
            #break
        mm = mm +1
    return render(request, 'vinwash/upload_file.html')


def add_taut_id(request):
    table_frame = pd.DataFrame(undertaking.objects.values_list('vin', 'uid', 'airbagLocation'))
    table_frame.columns = ['vin', 'uid', 'loc']
    #print(table_frame)

    mm = 0
    for j in table_frame.iterrows():
        vin = j[1]['vin']
        print("'"+vin+"',")
        uid = j[1]['uid']
        loc = j[1]['loc']
        washed_vins.objects.filter(vin=vin).filter(airbaglocation=loc).update(uid=uid)
        #if mm==30:
            #break
        mm = mm +1
    return render(request, 'vinwash/upload_file.html')


# upload star id to vinwash table
def star_upload(request):
    url = "http://takatalive.com/getdetailedlist"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.get(url, headers=headers)
    p = r.json()
    j = js.loads(p)
    mm = 0
    for i in j:
        starid = i['StarSubmissionID']
        vin = i['VIN']
        bcode = i['BarCode']
        driver = i['Driver']
        passenger = i['Passenger']
        loc = i['AirbagLocation']
        make = i['Make']
        model = i['Model']
        series = i['Series']
        year = i['Year']
        pranum = i['PRANum']
        isalpha = i['IsAlpha']
        notdate = i['NotificationDate']
        notfname = i['NotifFirstName']
        notlname = i['NotifLastName']
        fname = i['FirstName']
        lname = i['LastName']
        cid = i['CompanyID']
        rabn = i['RecyclerABN']
        cname = i['CompanyName']
        tname = i['TradingName']
        strt = i['Street']
        city = i['City']
        scode = i['StateCode']
        pcode = i['PostCode']
        email = i['Email']
        bphone = i['BusinessPhone']
        fax = i['Fax']
        web = i['Website']
        title = i['Title']
        phone = i['Phone']
        cemail = i['ContactEmail']
        aname = i['AccountName']
        bsb = i['BSB']
        anumber = i['AccountNumber']
        status = i['Status']
        cond = i['Condition']
        comp = i['Compensation']
        ware = i['Warehouse']
        courier = i['Courier']
        invoice = i['RecyclerInvoiceStatus']
        pstatus = i['OEMPaymentStatus']
        imgcount = i['UploadedImageCount']
        starstatus = i['StarStatus']
        condalias = i['ConditionAlias']
        datestring = i['SubmittedDateString']
        compcur = i['CompensationInCurrency']
        repcode = i['FieldRepCode']
        print((mm + 1), i['VIN'])
        mm = mm + 1
        instance = start_api(starid=starid, vin=vin, barcode=bcode, driver=driver, passenger=passenger,airbaglocation=loc,
                             make=make, model=model, series=series, year=year, pranum=pranum, isalpha=isalpha, notdate=notdate,
                             notifierfname=notfname, notifierlname=notlname, fname=fname, lname=lname, cid=cid,
                             abn=rabn, cname=cname, tradingname=tname, street=strt, city=city, state=scode, post=pcode,
                             email=email, bphone=bphone, fax=fax, website=web, title=title, phone=phone, cemail=cemail,
                             aname=aname, bsb=bsb, accnum=anumber, status=status,cond=cond, comp=comp, warehouse=ware,
                             cour=courier, recycler_inv_stat=invoice, oem_pmt_stat=pstatus, up_imgcnt=imgcount, str_stat=starstatus,
                             cond_alias=condalias, sub_date=datestring, comp_curn=compcur, field_repcode=repcode)
        instance.save()
        #if mm == 10:
            #break
    return render(request, 'vinwash/upload_file.html')



@login_required
def star_detailed_upload(request):
    meta = settings.MEDIA_ROOT + '\\' + 'star.csv'
    file1 = pd.read_csv(meta, encoding='latin1', sep=',')
    #print(file1)
    for j in file1.iterrows():
        si = j[1]['Star#']
        print(si)
        vn = j[1]['VIN']
        bc = j[1]['Bar Code']
        lc = j[1]['Loc']
        mk = j[1]['Make']
        md = j[1]['Model']
        sr = j[1]['Series']
        yr = j[1]['Year']
        pr = j[1]['PRA #']
        al = j[1]['Alpha']
        dt = j[1]['Date']
        sv = j[1]['STAR Vendor Number']
        st = j[1]['Status']
        cr = j[1]['Courier']
        wr = j[1]['Warehouse']
        ri = j[1]['Recycler Inv']
        nfn = j[1]['Notifier First Name']
        nln = j[1]['Notifier Last Name']
        ttl = j[1]['Title']
        tdn = j[1]['Trading Name']
        typ = j[1]['Type']
        wbs = j[1]['Website']
        dlr = j[1]['$']
        mbl = j[1]['Mobile Phone Number']
        eml = j[1]['Email']
        #print(si)
        #udt = datetime.datetime.strptime(dt, "%d/%m/%Y %I:%M:%S").strftime("%Y-%m-%d")
        udt = datetime.datetime.strptime(dt, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d")
        #print(udt)
        washed_vins.objects.filter(vin=vn).update(starid=si, barcode=bc, bagcollectiondate=udt,
                                                            star_vendor_no=sv, location_status=st, bagcollectedby=cr,
                                                            warehouse=wr, recycler_inv=ri, notifierfname=nfn,
                                                            notifierlname=nln, title=ttl, tradingname=tdn,
                                                            typeatstar=typ, website=wbs, dollaratstar=dlr,
                                                            mobileatstar=mbl, emailatstar=eml)

        objects = washed_vins.objects.filter(vin=vn)
        for a in objects:
            fileid = a.file_id
            ob1 = vinfile.objects.filter(id=fileid)
            for bbb in ob1:
                bid = bbb.business_id
                #print(bid)
                bnm = j[1]['Recycler']
                abn = j[1]['ABN']
                str = j[1]['Street']
                cty = j[1]['City']
                stt = j[1]['State/Territory']
                pcd = j[1]['Post Code']
                bem = j[1]['Business Email']
                bph = j[1]['Business Phone']
                fax = j[1]['Fax']
                fnm = j[1]['First Name']
                lnm = j[1]['Last Name']
                anm = j[1]['Account Name']
                bsb = j[1]['BSB']
                ano = j[1]['Account Number']

                business.objects.filter(id=bid).update(bname=bnm, abn=abn, street=str, city=cty, state=stt, zip=pcd, email=bem,
                                                       phone=bph, fax=fax, fname=fnm, lname=lnm, account_name=anm, bsb=bsb,
                                                       account_number=ano)
    return render(request, 'vinwash/upload_file.html')

#def upload_automated(request):
def upload_bulk(request):
    meta = settings.MEDIA_ROOT + '\\' + 'filenames.csv'
    file1 = pd.read_csv(meta, usecols=[0, 1, 2, 3, 4, 5],  encoding='latin1',  sep=',')
    file1.columns = ['business', 'filename', 'date', 'coord', 'bid', 'filetype']
    metaframe = pd.DataFrame(data=file1)
    #print(metaframe)
    for j in metaframe.iterrows():
        bs = j[1]['business']
        fl = j[1]['filename']
        ftyp = j[1]['filetype']
        #print(bs)
        print(fl)
        #print(ftyp)
        filepath = settings.MEDIA_ROOT+'\\electronic\\' + str(fl)
        dt = j[1]['date']
        print(dt)

        dt = datetime.datetime.strptime(str(dt), "%d/%m/%Y").strftime("%Y-%m-%d")
        #print(dt)
        cr = str(j[1]['coord'])
        bd = j[1]['bid']
        #print(fl)
        # from here business files will be read.
        instance = vinfile(filename=fl, date=dt, user=cr, notes=' ', business_id=bd, filetype=ftyp)
        instance.save()
        fid = instance.id

        of = pd.read_csv(filepath, usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                            encoding='latin1', sep=',')
        of.columns = ['vin', 'location', 'stock', 'image', 'model', 'year', 'inventoried', 'odoreading', 'engine',
                      'gearboxtype', 'gears', 'doors', 'site', 'registration', 'cod', 'enginenumber', 'purchasedate',
                      'fueltype', 'bodystyle', 'classification']

        df = of
        '''
        df['vin'] = df['vin'].str.replace('.', '')
        df['vin'] = df['vin'].str.replace(',', '')
        df['vin'] = df['vin'].str.replace(';', '')
        df['vin'] = df['vin'].str.replace('\'', '')
        df['vin'] = df['vin'].str.replace(':', '')
        df['vin'] = df['vin'].str.replace('+', '')
        df['vin'] = df['vin'].str.replace('=', '')
        df['vin'] = df['vin'].str.replace('@', '')
        df['vin'] = df['vin'].str.replace('#', '')
        df['vin'] = df['vin'].str.replace('$', '')
        df['vin'] = df['vin'].str.replace('%', '')
        df['vin'] = df['vin'].str.replace('^', '')
        df['vin'] = df['vin'].str.replace('&', '')
        df['vin'] = df['vin'].str.replace('*', '')
        df['vin'] = df['vin'].str.replace('i', '1')
        df['vin'] = df['vin'].str.replace('o', '0')
        
        df['vin'].replace('.', '', inplace=True)
        df['vin'].replace(',', '', inplace=True)
        df['vin'].replace(';', '', inplace=True)
        df['vin'].replace('\'', '', inplace=True)
        df['vin'].replace(':', '', inplace=True)
        df['vin'].replace('+', '', inplace=True)
        df['vin'].replace('=', '', inplace=True)
        df['vin'].replace('@', '', inplace=True)
        df['vin'].replace('#', '', inplace=True)
        df['vin'].replace('$', '', inplace=True)
        df['vin'].replace('%', '', inplace=True)
        df['vin'].replace('^', '', inplace=True)
        df['vin'].replace('&', '', inplace=True)
        df['vin'].replace('*', '', inplace=True)
        df['vin'].replace('i', '1', inplace=True)
        df['vin'].replace('I', '1', inplace=True)
        df['vin'].replace('o', '0', inplace=True)
        df['vin'].replace('O', '0', inplace=True)
        '''



        #s = df.iloc[:, ('vin')].str.replace()

        df['vin'] = df['vin'].apply(lambda x: str(x).replace('O', '0'))
        df['vin'] = df['vin'].apply(lambda x: x.replace('o', '0'))
        df['vin'] = df['vin'].apply(lambda x: x.replace('i', '1'))
        df['vin'] = df['vin'].apply(lambda x: x.replace('I', '1'))

        df['vin'] = df['vin'].apply(lambda x: x.replace('.', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace(',', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace(';', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('\'', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace(':', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('+', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('=', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('@', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('#', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('$', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('%', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('^', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('&', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('*', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('/', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('\\', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('_', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('-', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('!', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('(', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace(')', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('|', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('~', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('?', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('<', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('>', ''))
        df['vin'] = df['vin'].apply(lambda x: x.replace('`', ''))
        #df['vin'] = df['vin'].apply(lambda x: x.replace(" ", ""))
        df['vin'] = df['vin'].str.strip()



        df = df[df['vin'].apply(lambda x: len(str(x)) == 17)]
        #print(df)

        df = df.drop_duplicates(subset='vin', keep='first')
        print(df)
        list1 = original_vins.objects.values_list('vin', flat=True)
        vin_list = list(list1)
        dup_vins = df[df['vin'].isin(vin_list)]  # duplicate b/w 2 files
        print(list(dup_vins['vin']))
        shinobi = list(dup_vins['vin'])

        dup_data = original_vins.objects.filter(vin__in=str(shinobi)[1:-1]).values_list('vin', 'file_id')
        #dup_data = original_vins.objects.raw('select vin, file_id from original_vins where vin in (shinobi)')
        print(dup_data)
        recordid = fid
        if len(list(dup_vins['vin'])) > 0:
            for (vin, filid) in dup_data:
                e1 = vinfile.objects.get(id=filid)
                c1 = e1.business_id

                e2 = vinfile.objects.get(id=recordid)
                c2 = e2.business_id

                if c1 == c2:
                    pass
                else:
                    instance = vin_conflicts(vin=vin, previous_occurence_fileid=filid, current_occurence_fileid=recordid,
                                             conflict_location='', conflict_stocknumber='')
                    instance.save()

        df = df[~df['vin'].isin(vin_list)] #unique vins
        if df.shape[0] > 0:
            table_frame = pd.DataFrame(wiki_vincodes.objects.values_list('id', 'code', 'make'))
            table_frame.columns = ['id', 'code', 'make']
            prefix_list = list(table_frame['code'])
            for h in df.iterrows():
                vn = h[1]['vin']
                lc = h[1]['location']
                st = h[1]['stock']
                img = h[1]['image']
                ext = 'JPG'
                if pd.isnull(img):
                    loc = ''
                else:
                    loc = img
                pre3 = vn[0:3]
                pre2 = vn[0:2]
                if pre2 in prefix_list:
                    m_oem = int(table_frame[table_frame['code'] == pre2]['id'])
                elif pre3 in prefix_list:
                    m_oem = int(table_frame[table_frame['code'] == pre3]['id'])
                else:
                    m_oem = ''

                instance = original_vins(vin=vn, location=lc, stock_number=st, date=dt, file_id=recordid,
                                         business_id=bd, wiki_id=m_oem, img=loc)
                instance.save()
                sdsf =  ['model', 'year', 'inventoried', 'odoreading', 'engine',
                 'gearboxtype', 'gears', 'doors', 'site', 'registration', 'cod', 'enginenumber', 'purchasedate',
                 'fueltype', 'bodystyle', 'classification']

                instance1 = original_extension(vin=vn, model=h[1]['model'], year=h[1]['year'], inventoried=h[1]['inventoried'],
                                              odoreading=h[1]['odoreading'], engine=h[1]['engine'], gearboxtype=h[1]['gearboxtype'],
                                              gears=h[1]['gears'], doors=h[1]['doors'], sute=h[1]['site'], registration=h[1]['registration'],
                                              cod=h[1]['cod'], enginenumber=h[1]['enginenumber'], purchasedate=h[1]['purchasedate'],
                                              fueltype=h[1]['fueltype'], bodystyle=h[1]['bodystyle'], classification=h[1]['classification'])
                instance1.save()

            #print("original vins inserted")
            df1 = df
            dfToList = df1['vin'].tolist()
            #print("list created")
            #print(dfToList)
            url = "https://takatalive.com/api/takata/bulk"
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            #print("data sent to star")
            r = requests.post(url, data=js.dumps(dfToList), headers=headers)
            p = r.json()
            #print("response recieved")
            j = js.loads(p)
            #print(j)
            result = j['Result']
            #print(result)
            #print("results generated")
            resultdf = pd.DataFrame(
                columns=['VehicleAirbagID', 'VehicleID', 'VIN', 'PRANum', 'Make', 'Model', 'Series', 'Year',
                         'AirbagLocation', 'IsAlpha', 'IsSubmitted'])
            if result != None:
                for k in result:
                    VehicleAirbagID = str(k['VehicleAirbagID'])
                    VehicleID = str(k['VehicleID'])
                    VIN = str(k['VIN'])
                    PRANum = str(k['PRANum'])
                    Make = str(k['Make'])
                    Model = str(k['Model'])
                    Series = str(k['Series'])
                    Year = str(k['Year'])
                    AirbagLocation = str(k['AirbagLocation'])
                    IsAlpha = str(k['IsAlpha'])
                    IsSubmitted = str(k['IsSubmitted'])

                    stk_frame = df[df['vin'] == VIN]

                    if len(stk_frame['stock'].values) > 0:
                        stk = stk_frame['stock'].values[0]
                        lac = stk_frame['location'].values[0]
                    else:
                        stk = ''
                        lac = ''

                    resultdf = resultdf.append({'VehicleAirbagID': VehicleAirbagID,
                                                'VehicleID': VehicleID,
                                                'VIN': VIN,
                                                'PRANum': PRANum,
                                                'Make': Make,
                                                'Model': Model,
                                                'Series': Series,
                                                'Year': Year,
                                                'AirbagLocation': AirbagLocation,
                                                'IsAlpha': IsAlpha,
                                                'IsSubmitted': IsSubmitted
                                                }, ignore_index=True)

                    instance1 = washed_vins(vehicleid=VehicleID, vin=VIN, pranum=PRANum,
                                            make=Make, model=Model, series=Series, year=Year,
                                            airbaglocation=AirbagLocation,
                                            isalpha=IsAlpha, issubmitted=IsSubmitted, bagcollectiondate="2015-11-22",
                                            file_id=recordid, stock_number=stk, location=lac)
                    instance1.save()

    context = {
        'abc': 'prafull'
    }
    return render(request, 'vinwash/upload_file.html', context)


@login_required
def vins_located(request):
    a = original_vins.objects.values('wiki_id').annotate(dcount=Count('wiki_id'))
    b = pd.DataFrame(a)
    if b.shape[0]>0:
        b.columns = ['count', 'wiki_id']
    tf = pd.DataFrame(wiki_vincodes.objects.values('id', 'code', 'make'))
    tf.columns = ['code', 'id', 'make']
    print(tf)
    resultdf = pd.DataFrame()

    for j in b.iterrows():
        ct = j[1]['count']
        wid = j[1]['wiki_id']
        if len(wid) > 0:
            rs = tf[tf['id'] == int(wid)]
            print(rs)
            resultdf = resultdf.append({'make': rs['make'].values[0], 'code': rs['code'].values[0],
                                        'count': ct}, ignore_index=True)

    listt = resultdf.values.tolist()

    context = {
        'res': listt
    }
    return render(request, 'vinwash/report-1.html', context)


@login_required
def vins_make_consl(request):
    a = washed_vins.objects.values_list('make').annotate(dcount=Count('make')) # affected airbags
    a = pd.DataFrame(a)
    sh1 = a.shape[0]
    if sh1>0:
        a.columns = ['make', 'count']
        makes = list(a['make'])

    q = washed_vins.objects.all().values('make').annotate(count=Count('vin', distinct=True)).order_by() # affected vins
    q = pd.DataFrame(q)
    if q.shape[0]>0:
        q.columns = ['count', 'make']

    #d = washed_vins.objects.all().values('make').annotate(count=Count('vin', distinct=True)).filter(isalpha=True) #alpha
    d = washed_vins.objects.all().values('make').annotate(count=Count('vin')).filter(isalpha=True)  # alpha
    d = pd.DataFrame(d)
    print(d.shape)
    sh = d.shape[0]
    if sh>0:
        d.columns = ['count', 'make']

    resultdf = pd.DataFrame()
    for j in a.iterrows():
        make = j[1]['make']
        airbags = j[1]['count']

        rs = q[q['make'] == make]
        affected_vins = rs['count'].values[0]

        if sh>0:
            rs1 = d[d['make'] == make]
            if len(rs1['count']) > 0:
                alpha = rs1['count'].values[0]
            else:
                alpha = 0
        else:
            alpha = 0

        resultdf = resultdf.append({'make': make, 'airbags': airbags,
                                    'vins': affected_vins, 'alpha': alpha}, ignore_index=True)
        print(make, airbags, affected_vins, alpha)

    listt = resultdf.values.tolist()
    #print(a)
    #print(q)

    #print(list(a['make']))
    #print(a)

    context = {
        'table': listt
    }
    return render(request, 'vinwash/report-2.html', context)


def zoho_sync(request):
    print("we are here")
    url = 'https://crm.zoho.com/crm/v2/functions/prafull/actions/execute?auth_type=apikey&zapikey=1003.b8dcef9cb0743151af0b218cc1254715.7153890a3ea6d11cc7e7e0aed6ae5df3'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    #r = requests.post(url, data=js.dumps(dfToList), headers=headers)
    r = requests.get(url=url)
    print(r)

    p = r.json()
    a = p['code']
    b = p['details']
    c = b['userMessage']
    rec = len(c)
    id = []
    bname = []
    for r in range(0,rec):
        if r%2 == 0:
            id.append(c[r])
        else:
            bname.append(c[r])
    for i in range(len(id)):
        print(id[i], bname[i])

    return render(request, 'vinwash/upload_file.html')

def vin_lookup(request, vin):
    a = vin
    dd = original_vins.objects.all().values('img', 'date', 'stock_number', 'location', 'business_id',
                                           'file_id', 'wiki_id').filter(vin=a).count()
    if dd > 0:
        d = original_vins.objects.all().values('img', 'date', 'stock_number', 'location', 'business_id',
                                                    'file_id', 'wiki_id').filter(vin=a)


        #print(dd)

        d = pd.DataFrame(d)
        #print(d['img'].values[0])
        listt = d.values.tolist()
        listt = listt[0]
        #print(listt)
        biz = business.objects.all().values('bname', 'state').filter(id=listt[0])
        biz = pd.DataFrame(biz)
        listt1 = biz.values.tolist()
        listt1 = listt1[0]

        if listt[3] != None:
            path = settings.MEDIA_ROOT + '\\manual\\' + str(listt[0]) + listt[3]
            context = {
                'vals': listt,
                'path': path,
                'folder': 'manual',
                'biz': listt1
            }
        else:
            filid = listt[2]
            print(filid)
            filname = vinfile.objects.values('filename').filter(id=filid)
            print(filname[0]['filename'])

            print('vin has electronic file as source')
            path = settings.MEDIA_ROOT + '\\electronic\\' + filname[0]['filename']
            print(path)
            context = {
                'elec': filname[0]['filename'],
                'vals1': listt,
                'path': path,
                'folder': 'manual',
                'biz': listt1
            }
    else:
        context = {
            'notfound': 'Vin Not Found in business files'
        }
    return render(request, 'vinwash/vinlookup.html', context)

@login_required
def consolidated_data(request):

    OEM = ['BMW', 'Honda', 'Toyota', 'Lexus', 'Chrysler', 'Jeep', 'SAAB', 'Holden', 'Opel', 'Nissan', 'Mazda', 'Ford', 'Mitsubishi', 'Subaru', 'Mercedes-Benz']

    resultdf = pd.DataFrame()
    for o in OEM:
        ol = '%%' + o + '%%'
        locatedQuery = original_vins.objects.raw(
            'select COUNT(a.wiki_id) as id from vinwash_original_vins a inner join vinwash_wiki_vincodes b on a.wiki_id = b.id where b.make like %s',
            [ol])[0]
        locatedVINs = locatedQuery.id

        affectedQueryData = \
        washed_vins.objects.raw('select COUNT(distinct vin) as id from vinwash_washed_vins where make = %s', [o])[0]
        affectedVINs = affectedQueryData.id

        totalAirbagsQuery = \
        washed_vins.objects.raw('select COUNT(vin) as id from vinwash_washed_vins where make = %s', [o])[0]
        totalAirbags = totalAirbagsQuery.id

        alphaQuery = washed_vins.objects.raw(
            'select COUNT(isalpha) as id from vinwash_washed_vins where make = %s and isalpha = \'True\'', [o])[0]
        alpha = alphaQuery.id

        resultdf = resultdf.append(
            {'OEM': o, 'locatedVINs': locatedVINs, 'affectedVINs': affectedVINs, 'totalAirbags': totalAirbags,
             'alpha': alpha}, ignore_index=True)

    totalL = resultdf['locatedVINs'].sum()
    totalA = resultdf['affectedVINs'].sum()
    totalT = resultdf['totalAirbags'].sum()
    totalAl = resultdf['alpha'].sum()

    resultdf = resultdf.append({'OEM': 'VINs TOTAL', 'locatedVINs': totalL, 'affectedVINs': totalA, 'totalAirbags': totalT,
             'alpha': totalAl}, ignore_index=True)

    resultList = resultdf.values.tolist()

    context = {
        'result': resultList
    }
    return render(request, 'vinwash/consolidated.html', context)


def xgboost_results(request):
    return render(request, 'vinwash/home.html')


def report_menu(request):
    return render(request, 'vinwash/reports.html')