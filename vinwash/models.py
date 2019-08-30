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

    barcode = models.TextField(null=True)
    star_vendor_no = models.TextField(null=True)

    location_status = models.TextField(null=True)
    no_collected = models.TextField(null=True)
    in_possession = models.TextField(null=True)
    warehouse = models.TextField(null=True)
    recycler_inv = models.TextField(null=True)
    bagcollectiondate = models.DateField(null=True)
    bagcollectedby = models.TextField(null=True)
    starid = models.CharField(max_length=100, null=True)
    file = models.ForeignKey(
        vinfile, on_delete=models.CASCADE, null=True
    )
    notifierfname = models.TextField(null=True)
    notifierlname = models.TextField(null=True)
    tradingname = models.TextField(null=True)
    website = models.TextField(null=True)
    title = models.TextField(null=True)
    emailatstar = models.TextField(null=True)
    mobileatstar = models.TextField(null=True)
    typeatstar = models.TextField(null=True)
    dollaratstar = models.TextField(null=True)
    '''
    business = models.ForeignKey(
        business, on_delete=models.PROTECT
    )
    
    def __str__(self):
        return '{} is an affected vin '.format(self.vin)
    '''

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
    #wiki_prefix = models.CharField(max_length=10, null=True)
    #wiki_oem = models.TextField(null=True)

    '''
    def __str__(self):
        return 'vins for {} '.format(self.business)
    '''

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


