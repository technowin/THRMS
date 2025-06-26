from django import forms

from Account.models import CustomUser



class RegistrationForm(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields =['email','name','password']
    
    password = forms.CharField(widget=forms.PasswordInput)