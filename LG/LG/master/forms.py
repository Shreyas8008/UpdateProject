
from django import forms
from .models import VendorDetail,category,CustomerDetail,company,ItemDetail
class VendorDetailForm(forms.ModelForm):
    class Meta:
        model = VendorDetail
        fields = '__all__'



class categoryForm(forms.ModelForm):

    class Meta:
        model = category
        fields = ['name', 'description', 'remarks']

 
class CustomerDetailForm(forms.ModelForm):
    class Meta:
        model = CustomerDetail
        fields = '__all__'
    

class companyForm(forms.ModelForm):
    class Meta:
        model = company
        fields = ['name', 'lst_no', 'pan_no', 'cst_no', 'company_address']



class ItemDetailForm(forms.ModelForm):
    class Meta:
        model = ItemDetail
        fields = ['item_code', 'item_name', 'category', 'rol', 'rate', 
                  'remarks', 'grade', 'hsncode', 'molqty', 'packingqty']
        widgets = {
            'category': forms.Select(attrs={'id': 'category-dropdown'}),  # Dropdown for Category
        }

        

