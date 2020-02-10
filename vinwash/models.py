from django.db import models
from django.utils import timezone
from django.urls import reverse

class business(models.Model):
    zohoid = models.CharField(max_length=50)
    bname = models.TextField(null=True)
    fname = models.CharField(max_length=50, null=True)
    lname = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=15, null=True)
    fax = models.CharField(max_length=15, null=True)
    mobile = models.CharField(max_length=15, null=True)
    leadstatus = models.CharField(max_length=35, null=True)
    street = models.TextField(null=True)
    city = models.TextField(null=True)
    zip = models.IntegerField(null=True)
    state = models.CharField(max_length=25, null=True)
    coord = models.TextField(null=True)
    abn = models.CharField(max_length=20, null=True)
    account_name =  models.TextField(null=True)
    bsb = models.CharField(max_length=15, null=True)
    account_number = models.CharField(max_length=15, null=True)
    notes = models.TextField(null=True)
    courier = models.TextField(null=True)

    def __str__(self):
        return '{} at {}'.format(self.bname, self.street)

    def get_absolute_url(self):
        return  reverse('business-detail', kwargs={'pk': self.pk})


class vinfile(models.Model):
    #filename = models.CharField(max_length=200)
    filename = models.FileField(upload_to='electronic/')
    date = models.DateField(null=True)
    user = models.CharField(max_length=100, null=True)
    notes = models.TextField(null=True)
    business = models.ForeignKey(business, on_delete=models.PROTECT)
    #business = models.TextField(null=True)
    filetype = models.CharField(max_length=25, null=True)
    #business = models.CharField(max_length=250)

    #def get_absolute_url(self):
        #return reverse('vinwash-detail', kwargs={'pk': self.pk})




class business_attachments(models.Model):
    attachment_name = models.TextField(null=True)
    business = models.ForeignKey(
        business, on_delete=models.PROTECT
    )

    def __str__(self):
        return ' attachment {} for {}'.format(self.attachment_name, self.business)


class connectstar(models.Model):
    starid = models.CharField(max_length=25, null=True)
    vin = models.CharField(max_length=25, null=True)


class start_api(models.Model):
    starid = models.CharField(max_length=100, null=True)
    vin = models.CharField(max_length=50, null=True)
    barcode = models.TextField(null=True)
    driver = models.TextField(null=True)
    passenger = models.TextField(null=True)
    airbaglocation = models.CharField(max_length=50, null=True)
    make = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True)
    series = models.CharField(max_length=50, null=True)
    year = models.CharField(max_length=50, null=True)
    pranum = models.TextField(max_length=50, null=True)
    isalpha = models.CharField(max_length=50, null=True)
    notdate = models.TextField(null=True)
    notifierfname = models.TextField(null=True)
    notifierlname = models.TextField(null=True)
    fname = models.TextField(null=True)
    lname = models.TextField(null=True)
    cid = models.TextField(null=True)
    abn = models.TextField(null=True)
    cname = models.TextField(null=True)
    tradingname = models.TextField(null=True)
    street = models.TextField(null=True)
    city = models.TextField(null=True)
    state = models.TextField(null=True)
    post = models.TextField(null=True)
    email = models.TextField(null=True)
    bphone = models.TextField(null=True)
    fax = models.TextField(null=True)
    website = models.TextField(null=True)
    title = models.TextField(null=True)
    phone = models.TextField(null=True)
    cemail = models.TextField(null=True)
    aname = models.TextField(null=True)
    bsb = models.TextField(null=True)
    accnum = models.TextField(null=True)
    status = models.TextField(null=True)
    cond = models.TextField(null=True)
    comp = models.TextField(null=True)
    warehouse = models.TextField(null=True)
    cour = models.TextField(null=True)
    recycler_inv_stat = models.TextField(null=True)
    oem_pmt_stat = models.TextField(null=True)
    up_imgcnt = models.TextField(null=True)
    str_stat = models.TextField(null=True)
    cond_alias = models.TextField(null=True)
    sub_date = models.TextField(null=True)
    comp_curn = models.TextField(null=True)
    field_repcode = models.TextField(null=True)


class washed_vins(models.Model):
    vehicleid  = models.CharField(max_length=50, null=True)
    vin = models.CharField(max_length=50, null=True)
    pranum = models.CharField(max_length=50, null=True)
    make = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True)
    series = models.CharField(max_length=50, null=True)
    year = models.CharField(max_length=50, null=True)
    airbaglocation = models.CharField(max_length=50, null=True)
    isalpha = models.CharField(max_length=50, null=True)
    issubmitted = models.CharField(max_length=50, null=True)
    location = models.TextField(null=True)
    stock_number = models.TextField(null=True)
    file = models.ForeignKey(
        vinfile, on_delete=models.CASCADE, null=True
    )
    starid = models.CharField(max_length=100, null=True)
    uid = models.TextField(null=True)







class vin_attachments(models.Model):
    attachment_name = models.TextField(null=True)
    vin = models.ForeignKey(washed_vins, on_delete=models.CASCADE)

    def __str__(self):
        return '{} for {}'.format(self.attachment_name, self.vin)


class weeks(models.Model):
    wstart = models.CharField(max_length=4, null=True)
    wend = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=15, null=True)
    year = models.IntegerField(null=True)
    weekno = models.IntegerField(null=True)


class undertaking(models.Model):
    uid = models.TextField(null=True)
    vin = models.CharField(max_length=50, null=True)
    barcode = models.TextField(null=True)
    airbagLocation = models.TextField(null=True)
    make = models.TextField(null=True)
    model = models.TextField(null=True)
    series = models.TextField(null=True)
    year = models.TextField(null=True)
    praNum = models.TextField(null=True)
    isAlpha = models.TextField(null=True)
    notificationDate = models.TextField(null=True)
    notifFirstName = models.TextField(null=True)
    notifLastName = models.TextField(null=True)
    firstName = models.TextField(null=True)
    lastName = models.TextField(null=True)
    companyID = models.TextField(null=True)
    recyclerABN = models.TextField(null=True)
    companyName = models.TextField(null=True)
    tradingName = models.TextField(null=True)
    street = models.TextField(null=True)
    city = models.TextField(null=True)
    stateCode = models.TextField(null=True)
    postCode = models.TextField(null=True)
    email = models.TextField(null=True)
    businessPhone = models.TextField(null=True)
    fax = models.TextField(null=True)
    website = models.TextField(null=True)
    title = models.TextField(null=True)
    phone = models.TextField(null=True)
    contactEmail = models.TextField(null=True)
    accountName = models.TextField(null=True)
    bsb = models.TextField(null=True)
    accountNumber = models.TextField(null=True)
    status = models.TextField(null=True)
    condition = models.TextField(null=True)
    licenseDetail = models.TextField(null=True)
    sellerCompanyName = models.TextField(null=True)
    sellerEmail = models.TextField(null=True)
    sellerPhone = models.TextField(null=True)
    sellerFName = models.TextField(null=True)
    sellerLName = models.TextField(null=True)
    sellerFullName = models.TextField(null=True)
    ownerCompanyName = models.TextField(null=True)
    ownerEmail = models.TextField(null=True)
    ownerPhone = models.TextField(null=True)
    ownerFName = models.TextField(null=True)
    ownerLName = models.TextField(null=True)
    ownerFullName = models.TextField(null=True)
    uploadedImageCount = models.TextField(null=True)
    dateOfSale = models.TextField(null=True)
    writeOffTypeID = models.TextField(null=True)
    writtenOffType = models.TextField(null=True)
    dateSigned = models.TextField(null=True)


class original_vins(models.Model):
    vin = models.CharField(max_length=17, null=True)
    stock_number = models.TextField(null=True)
    location = models.TextField(null=True)
    date = models.DateField(null=True)

    file = models.ForeignKey(
        vinfile, on_delete=models.PROTECT
    )

    business = models.ForeignKey(
        business, on_delete=models.PROTECT
    )
    wiki_id = models.CharField(max_length=10, null=True)
    img = models.TextField(null=True)
    uid = models.ForeignKey(undertaking, on_delete=models.PROTECT, null=True)


class makes(models.Model):
    manufacturer = models.TextField(null=True)


class wiki_vincodes(models.Model):
    code = models.CharField(max_length=10, null=True)
    make = models.TextField(null=True)


class unidentified_vins_17character(models.Model):
    vin = models.ForeignKey(
        original_vins, on_delete=models.PROTECT
    )

    business = models.ForeignKey(
        business, on_delete=models.PROTECT
    )


class vin_conflicts(models.Model):
    vin = models.CharField(max_length=17, null=True)
    previous_occurence_fileid = models.IntegerField(null=True)
    current_occurence_fileid = models.IntegerField(null=True)
    conflict_location = models.TextField(null=True)
    conflict_stocknumber = models.TextField(null=True)


class staff(models.Model):
    fname = models.CharField(max_length=50, null=True)
    lname = models.CharField(max_length=50, null=True)


class original_extension(models.Model):
    vin = models.TextField(null=True)
    model = models.TextField(null=True)
    year = models.TextField(null=True)
    inventoried = models.TextField(null=True)
    odoreading = models.TextField(null=True)
    engine = models.TextField(null=True)
    gearboxtype = models.TextField(null=True)
    gears = models.TextField(null=True)
    doors = models.TextField(null=True)
    sute = models.TextField(null=True)
    registration = models.TextField(null=True)
    cod = models.TextField(null=True)
    enginenumber = models.TextField(null=True)
    purchasedate = models.TextField(null=True)
    fueltype = models.TextField(null=True)
    bodystyle = models.TextField(null=True)
    classification = models.TextField(null=True)


class results(models.Model):
    threshold = models.TextField(null=True)
    col1 = models.TextField(null=True)
    col2 = models.TextField(null=True)
    accuracy = models.TextField(null=True)
    method = models.TextField(null=True)
    lossfunction = models.TextField(null=True)
    dataset = models.TextField(null=True)


class makemodel(models.Model):
    oem = models.TextField(null=True)
    model = models.TextField(null=True)
    note = models.TextField(null=True)
    year = models.TextField(null=True)
    airbag = models.TextField(null=True)
    status = models.TextField(null=True)


class mapping(models.Model):
    starbn = models.TextField(null=True)
    startn = models.TextField(null=True)
    zohobn = models.TextField(null=True)
    zohotn = models.TextField(null=True)
    tautbn = models.TextField(null=True)
    tauttn = models.TextField(null=True)
    hondabn = models.TextField(null=True)
    hondatn = models.TextField(null=True)


class zoho_sync_day1(models.Model):
    bname = models.TextField(null=True)
    bid = models.TextField(null=True)

class zoho_sync_day2(models.Model):
    bname = models.TextField(null=True)

class zoho_sync_day3(models.Model):
    bname = models.TextField(null=True)


class zoho_sync_log(models.Model):
    day = models.TextField(null=True)
    date = models.TextField(null=True)


class zoho_calls(models.Model):
    call_duration = models.TextField(null=True)
    description = models.TextField(null=True)
    call_status = models.TextField(null=True)
    call_start_time = models.TextField(null=True)
    billable = models.TextField(null=True)
    subject = models.TextField(null=True)
    call_type = models.TextField(null=True)
    call_result = models.TextField(null=True)
    what_id_name = models.TextField(null=True)
    what_id_id = models.TextField(null=True)
    call_duration_in_seconds = models.TextField(null=True)
    tag = models.TextField(null=True)

class honda_file(models.Model):
    honda_name = models.TextField(null=True)
    honda_address = models.TextField(null=True)
    zoho_business_name = models.TextField(null=True)
    zoho_trading_name = models.TextField(null=True)
    zoho_street = models.TextField(null=True)
    zoho_city = models.TextField(null=True)
    zoho_zipcode = models.TextField(null=True)
    zoho_state = models.TextField(null=True)
    account_lead = models.TextField(null=True)
    remark = models.TextField(null=True)