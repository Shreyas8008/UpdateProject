from django.db import models


# Create your models here.
class RawInwardMaterial(models.Model):
    invoice_no = models.CharField(max_length=50)
    invoice_date = models.DateField()
    vendor_code = models.CharField(max_length=100)
    vendor_name = models.CharField(max_length=255)
    grn_no = models.CharField(max_length=50)
    grn_date = models.DateField()
    store = models.CharField(max_length=100)
    po_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.invoice_no


# models.py
class RawInwardMaterialSub(models.Model):
    inward_material = models.ForeignKey('RawInwardMaterial', on_delete=models.CASCADE, null=True, blank=True)  # Make it nullable
    
    item_code = models.CharField(max_length=100)
    item_name = models.CharField(max_length=255)

  
    uom = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    no_of_bags = models.IntegerField()
    mfg_date = models.DateField()
    exp_date = models.DateField()
    lot_no = models.CharField(max_length=100)
    repacking_batch_no= models.CharField(max_length=100)

    def __str__(self):
        return f"{self.item_name} -  {self.quantity} units"



