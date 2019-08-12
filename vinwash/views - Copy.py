from django.shortcuts import render,  redirect
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
from . models import washed_vins, original_vins, vin_conflicts, wiki_vincodes
import io


# Create your views here.


def home(request):
    context = {
        'title': 'Wassup homie',
    }
    return render(request, 'vinwash/home.html', context)

@login_required
def dashboard(request):
    return render(request, 'vinwash/dashboard.html')


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



def upload_file(request):
    if request.method == 'POST':
        form = vinfileForm(request.POST, request.FILES)
        if form.is_valid():
            bid = request.POST.get('business')
            udt = request.POST.get('date')
            print('business id after this')
            print(bid)

            uploaded_file = request.FILES['filename']
            file1 = pd.read_csv(uploaded_file, usecols=[0, 1, 2], encoding='latin1', sep=',')

            df = pd.DataFrame(data=file1)
            df.columns = ['vin', 'location', 'stock']
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

            print(df)

            df = df[df['vin'].apply(lambda x: len(str(x)) == 17)]
            df['vin'] = df['vin'].str.replace('i', '1')
            df['vin'] = df['vin'].str.replace('o', '0')
            df = df.drop_duplicates(subset='vin', keep='first')

            list1 = original_vins.objects.values_list('vin', flat=True)
            vin_list = list(list1)
            #print(vin_list)
            dup_vins = df[df['vin'].isin(vin_list)]  # duplicate b/w 2 files
            #print(dup_vins['vin'])
            dup_data = original_vins.objects.filter(vin__in=list(dup_vins['vin'])).values_list('vin', 'file_id')
            # dup_data = original_vins.objects.filter(vin__in=list(dup_vins))
            #print(dup_data)

            df = df[~df['vin'].isin(vin_list)]

            if df.shape[0] > 0:
                forminstance = form.save()
                recordid = forminstance.pk
                for (vin, filid) in dup_data:
                    instance = vin_conflicts(vin=vin, previous_occurence_fileid=filid, current_occurence_fileid=recordid,
                                             conflict_location='', conflict_stocknumber='')
                    instance.save()


                print(wiki_vincodes.objects.values_list('id','code','make'))
                table_frame = pd.DataFrame(wiki_vincodes.objects.values_list('id', 'code', 'make'))
                table_frame.columns = ['id', 'code', 'make']
                print('table frame below this')
                print(table_frame)
                #codes = wiki_vincodes.objects.all()
                prefix_list= list(table_frame['code'])
                print(prefix_list)
                for j in df.iterrows():
                    vn = j[1]['vin']
                    lc = j[1]['location']
                    st = j[1]['stock']

                    pre3 = vn[0:3]
                    pre2 = vn[0:2]
                    if pre2 in prefix_list:
                        m_pre = pre2
                        m_oem = list(table_frame[table_frame['code'] == pre2]['id'])
                        print(m_oem[0])
                    elif pre3 in prefix_list:
                        m_pre = pre3
                        m_oem = list(table_frame[table_frame['code'] == pre3]['id'])
                        print(m_oem[0])
                    else:
                        m_pre = ''
                        m_oem = ''
                    instance = original_vins(vin=vn, location=lc, stock_number=st, date=udt, file_id=recordid,
                                             business_id=bid, wiki_id=m_oem)
                    instance.save()

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
                                               file_id=recordid)
                        instance1.save()
                messages.add_message(request, messages.INFO, "Process executed successfully")
            else:
                messages.add_message(request, messages.INFO, "All vins in this file already exist in DB!!")

            return redirect('dashboard')
    else:
        form = vinfileForm()
    context = {
        'form': form
    }
    return render(request, 'vinwash/upload_file.html', context)
