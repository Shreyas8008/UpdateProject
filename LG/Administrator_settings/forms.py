from django import forms
from django.contrib.auth.models import User  # default User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']  # ONLY include fields that actually exist
        widgets = {
            'password': forms.PasswordInput(),  # makes password field hidden
        }


from django import forms
from Administrator_settings.models import UserRights

class UserRightsForm(forms.ModelForm):
    class Meta:
        model = UserRights
        fields = ['user', 'form_name', 'can_view', 'can_add', 'can_edit', 'can_delete', 'all_access']
        widgets = {
            'form_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Form Name'}),
        }
