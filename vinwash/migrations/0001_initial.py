# Generated by Django 2.1.15 on 2020-02-03 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='business',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zohoid', models.CharField(max_length=50)),
                ('bname', models.TextField(null=True)),
                ('fname', models.CharField(max_length=50, null=True)),
                ('lname', models.CharField(max_length=50, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('phone', models.CharField(max_length=15, null=True)),
                ('fax', models.CharField(max_length=15, null=True)),
                ('mobile', models.CharField(max_length=15, null=True)),
                ('leadstatus', models.CharField(max_length=35, null=True)),
                ('street', models.TextField(null=True)),
                ('city', models.TextField(null=True)),
                ('zip', models.IntegerField(null=True)),
                ('state', models.CharField(max_length=25, null=True)),
                ('coord', models.TextField(null=True)),
                ('abn', models.CharField(max_length=20, null=True)),
                ('account_name', models.TextField(null=True)),
                ('bsb', models.CharField(max_length=15, null=True)),
                ('account_number', models.CharField(max_length=15, null=True)),
                ('notes', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='business_attachments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_name', models.TextField(null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vinwash.business')),
            ],
        ),
        migrations.CreateModel(
            name='connectstar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starid', models.CharField(max_length=25, null=True)),
                ('vin', models.CharField(max_length=25, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='makemodel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oem', models.TextField(null=True)),
                ('model', models.TextField(null=True)),
                ('note', models.TextField(null=True)),
                ('year', models.TextField(null=True)),
                ('airbag', models.TextField(null=True)),
                ('status', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='makes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manufacturer', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='mapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starbn', models.TextField(null=True)),
                ('startn', models.TextField(null=True)),
                ('zohobn', models.TextField(null=True)),
                ('zohotn', models.TextField(null=True)),
                ('tautbn', models.TextField(null=True)),
                ('tauttn', models.TextField(null=True)),
                ('hondabn', models.TextField(null=True)),
                ('hondatn', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='original_extension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vin', models.TextField(null=True)),
                ('model', models.TextField(null=True)),
                ('year', models.TextField(null=True)),
                ('inventoried', models.TextField(null=True)),
                ('odoreading', models.TextField(null=True)),
                ('engine', models.TextField(null=True)),
                ('gearboxtype', models.TextField(null=True)),
                ('gears', models.TextField(null=True)),
                ('doors', models.TextField(null=True)),
                ('sute', models.TextField(null=True)),
                ('registration', models.TextField(null=True)),
                ('cod', models.TextField(null=True)),
                ('enginenumber', models.TextField(null=True)),
                ('purchasedate', models.TextField(null=True)),
                ('fueltype', models.TextField(null=True)),
                ('bodystyle', models.TextField(null=True)),
                ('classification', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='original_vins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vin', models.CharField(max_length=17, null=True)),
                ('stock_number', models.TextField(null=True)),
                ('location', models.TextField(null=True)),
                ('date', models.DateField(null=True)),
                ('wiki_id', models.CharField(max_length=10, null=True)),
                ('img', models.TextField(null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vinwash.business')),
            ],
        ),
        migrations.CreateModel(
            name='results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('threshold', models.TextField(null=True)),
                ('col1', models.TextField(null=True)),
                ('col2', models.TextField(null=True)),
                ('accuracy', models.TextField(null=True)),
                ('method', models.TextField(null=True)),
                ('lossfunction', models.TextField(null=True)),
                ('dataset', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.CharField(max_length=50, null=True)),
                ('lname', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='start_api',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starid', models.CharField(max_length=100, null=True)),
                ('vin', models.CharField(max_length=50, null=True)),
                ('barcode', models.TextField(null=True)),
                ('driver', models.TextField(null=True)),
                ('passenger', models.TextField(null=True)),
                ('airbaglocation', models.CharField(max_length=50, null=True)),
                ('make', models.CharField(max_length=50, null=True)),
                ('model', models.CharField(max_length=50, null=True)),
                ('series', models.CharField(max_length=50, null=True)),
                ('year', models.CharField(max_length=50, null=True)),
                ('pranum', models.TextField(max_length=50, null=True)),
                ('isalpha', models.CharField(max_length=50, null=True)),
                ('notdate', models.TextField(null=True)),
                ('notifierfname', models.TextField(null=True)),
                ('notifierlname', models.TextField(null=True)),
                ('fname', models.TextField(null=True)),
                ('lname', models.TextField(null=True)),
                ('cid', models.TextField(null=True)),
                ('abn', models.TextField(null=True)),
                ('cname', models.TextField(null=True)),
                ('tradingname', models.TextField(null=True)),
                ('street', models.TextField(null=True)),
                ('city', models.TextField(null=True)),
                ('state', models.TextField(null=True)),
                ('post', models.TextField(null=True)),
                ('email', models.TextField(null=True)),
                ('bphone', models.TextField(null=True)),
                ('fax', models.TextField(null=True)),
                ('website', models.TextField(null=True)),
                ('title', models.TextField(null=True)),
                ('phone', models.TextField(null=True)),
                ('cemail', models.TextField(null=True)),
                ('aname', models.TextField(null=True)),
                ('bsb', models.TextField(null=True)),
                ('accnum', models.TextField(null=True)),
                ('status', models.TextField(null=True)),
                ('cond', models.TextField(null=True)),
                ('comp', models.TextField(null=True)),
                ('warehouse', models.TextField(null=True)),
                ('cour', models.TextField(null=True)),
                ('recycler_inv_stat', models.TextField(null=True)),
                ('oem_pmt_stat', models.TextField(null=True)),
                ('up_imgcnt', models.TextField(null=True)),
                ('str_stat', models.TextField(null=True)),
                ('cond_alias', models.TextField(null=True)),
                ('sub_date', models.TextField(null=True)),
                ('comp_curn', models.TextField(null=True)),
                ('field_repcode', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='undertaking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.TextField(null=True)),
                ('vin', models.CharField(max_length=50, null=True)),
                ('barcode', models.TextField(null=True)),
                ('airbagLocation', models.TextField(null=True)),
                ('make', models.TextField(null=True)),
                ('model', models.TextField(null=True)),
                ('series', models.TextField(null=True)),
                ('year', models.TextField(null=True)),
                ('praNum', models.TextField(null=True)),
                ('isAlpha', models.TextField(null=True)),
                ('notificationDate', models.TextField(null=True)),
                ('notifFirstName', models.TextField(null=True)),
                ('notifLastName', models.TextField(null=True)),
                ('firstName', models.TextField(null=True)),
                ('lastName', models.TextField(null=True)),
                ('companyID', models.TextField(null=True)),
                ('recyclerABN', models.TextField(null=True)),
                ('companyName', models.TextField(null=True)),
                ('tradingName', models.TextField(null=True)),
                ('street', models.TextField(null=True)),
                ('city', models.TextField(null=True)),
                ('stateCode', models.TextField(null=True)),
                ('postCode', models.TextField(null=True)),
                ('email', models.TextField(null=True)),
                ('businessPhone', models.TextField(null=True)),
                ('fax', models.TextField(null=True)),
                ('website', models.TextField(null=True)),
                ('title', models.TextField(null=True)),
                ('phone', models.TextField(null=True)),
                ('contactEmail', models.TextField(null=True)),
                ('accountName', models.TextField(null=True)),
                ('bsb', models.TextField(null=True)),
                ('accountNumber', models.TextField(null=True)),
                ('status', models.TextField(null=True)),
                ('condition', models.TextField(null=True)),
                ('licenseDetail', models.TextField(null=True)),
                ('sellerCompanyName', models.TextField(null=True)),
                ('sellerEmail', models.TextField(null=True)),
                ('sellerPhone', models.TextField(null=True)),
                ('sellerFName', models.TextField(null=True)),
                ('sellerLName', models.TextField(null=True)),
                ('sellerFullName', models.TextField(null=True)),
                ('ownerCompanyName', models.TextField(null=True)),
                ('ownerEmail', models.TextField(null=True)),
                ('ownerPhone', models.TextField(null=True)),
                ('ownerFName', models.TextField(null=True)),
                ('ownerLName', models.TextField(null=True)),
                ('ownerFullName', models.TextField(null=True)),
                ('uploadedImageCount', models.TextField(null=True)),
                ('dateOfSale', models.TextField(null=True)),
                ('writeOffTypeID', models.TextField(null=True)),
                ('writtenOffType', models.TextField(null=True)),
                ('dateSigned', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='unidentified_vins_17character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vinwash.business')),
                ('vin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vinwash.original_vins')),
            ],
        ),
        migrations.CreateModel(
            name='vin_attachments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_name', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='vin_conflicts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vin', models.CharField(max_length=17, null=True)),
                ('previous_occurence_fileid', models.IntegerField(null=True)),
                ('current_occurence_fileid', models.IntegerField(null=True)),
                ('conflict_location', models.TextField(null=True)),
                ('conflict_stocknumber', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='vinfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.FileField(upload_to='electronic/')),
                ('date', models.DateField(null=True)),
                ('user', models.CharField(max_length=100, null=True)),
                ('notes', models.TextField(null=True)),
                ('filetype', models.CharField(max_length=25, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vinwash.business')),
            ],
        ),
        migrations.CreateModel(
            name='washed_vins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicleid', models.CharField(max_length=50, null=True)),
                ('vin', models.CharField(max_length=50, null=True)),
                ('pranum', models.CharField(max_length=50, null=True)),
                ('make', models.CharField(max_length=50, null=True)),
                ('model', models.CharField(max_length=50, null=True)),
                ('series', models.CharField(max_length=50, null=True)),
                ('year', models.CharField(max_length=50, null=True)),
                ('airbaglocation', models.CharField(max_length=50, null=True)),
                ('isalpha', models.CharField(max_length=50, null=True)),
                ('issubmitted', models.CharField(max_length=50, null=True)),
                ('location', models.TextField(null=True)),
                ('stock_number', models.TextField(null=True)),
                ('starid', models.CharField(max_length=100, null=True)),
                ('uid', models.TextField(null=True)),
                ('file', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='vinwash.vinfile')),
            ],
        ),
        migrations.CreateModel(
            name='weeks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wstart', models.CharField(max_length=4, null=True)),
                ('wend', models.CharField(max_length=4, null=True)),
                ('month', models.CharField(max_length=15, null=True)),
                ('year', models.IntegerField(null=True)),
                ('weekno', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='wiki_vincodes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, null=True)),
                ('make', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='zoho_calls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_duration', models.TextField(null=True)),
                ('description', models.TextField(null=True)),
                ('call_status', models.TextField(null=True)),
                ('call_start_time', models.TextField(null=True)),
                ('billable', models.TextField(null=True)),
                ('subject', models.TextField(null=True)),
                ('call_type', models.TextField(null=True)),
                ('call_result', models.TextField(null=True)),
                ('what_id_name', models.TextField(null=True)),
                ('what_id_id', models.TextField(null=True)),
                ('call_duration_in_seconds', models.TextField(null=True)),
                ('tag', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='zoho_sync_day1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bname', models.TextField(null=True)),
                ('bid', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='zoho_sync_day2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bname', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='zoho_sync_day3',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bname', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='zoho_sync_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.TextField(null=True)),
                ('date', models.TextField(null=True)),
            ],
        ),
        migrations.AddField(
            model_name='vin_attachments',
            name='vin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vinwash.washed_vins'),
        ),
        migrations.AddField(
            model_name='original_vins',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vinwash.vinfile'),
        ),
        migrations.AddField(
            model_name='original_vins',
            name='uid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='vinwash.undertaking'),
        ),
    ]
