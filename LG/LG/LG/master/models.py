from django.db import models

class VendorDetail(models.Model):
    vendor_code = models.CharField(max_length=50, unique=True)
    vendor_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    tel_no = models.CharField(max_length=15)
    email = models.EmailField()
    lst_no = models.CharField(max_length=50, blank=True, null=True)
    gst_no = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return self.vendor_name

class category(models.Model):   
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class CustomerDetail(models.Model):
    customer_code = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    # opening_balance = models.DecimalField(max_digits=15, null=True)
 
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
 
    # Added customer_type as a regular text field
    customer_type = models.CharField(max_length=50, blank=True, null=True)
 
    tel_no = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gst_no = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return self.customer_name

  

class company(models.Model):
    name = models.CharField(max_length=255, verbose_name="company Name")
    lst_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="LST No")
    pan_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="PAN No")
    cst_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="CST No")
    company_address = models.TextField(verbose_name="company Address")

    def __str__(self):
        return self.name

    


class ItemDetail(models.Model):
    item_code = models.CharField(max_length=50, null=True, blank=True)
    item_name = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(category, on_delete=models.CASCADE,default=1) 
    rol = models.IntegerField(null=True, blank=True)
   
    rate = models.FloatField(null=True, blank=True)

    remarks = models.TextField(null=True, blank=True)
   
    grade = models.CharField(max_length=100, null=True, blank=True)
   
    hsncode = models.CharField(max_length=50, null=True, blank=True)
 
   
    molqty = models.FloatField(null=True, blank=True)
    packingqty = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.item_name
