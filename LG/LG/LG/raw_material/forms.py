from django import forms
from .models import RawInwardMaterial,RawInwardMaterialSub
from master.models import ItemDetail
class RawInwardMaterialForm(forms.ModelForm):
    class Meta:
        model = RawInwardMaterial
        fields = '__all__'
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'grn_date': forms.DateInput(attrs={'type': 'date'}),
            'po_date': forms.DateInput(attrs={'type': 'date'}),
        }


class RawInwardMaterialSubForm(forms.ModelForm):
    item_code = forms.ModelChoiceField(
        queryset=ItemDetail.objects.all(),
        empty_label="Select Item Code",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Assuming `item_name` is a representation of the selected `item_code`, you can choose not to display it directly.
    # If you still want to keep it for some reason, you can add a custom method or widget
    # to show item_name based on the item_code.
    item_name = forms.ModelChoiceField(
        queryset=ItemDetail.objects.all(),
        empty_label="Select Item Name",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = RawInwardMaterialSub
        fields =  '__all__'
        widgets = {
            'exp_date': forms.DateInput(attrs={'type': 'date'}),
            'mfg_date': forms.DateInput(attrs={'type': 'date'}),
            
        }

        
      


