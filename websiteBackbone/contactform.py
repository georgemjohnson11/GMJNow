from django import forms
from websiteBackbone.models import Profile, User


class ContactForm(forms.Form):
    contactName = forms.CharField(label='contactName', max_length=100)
    contactSubject = forms.CharField(label='contactSubject', widget=forms.Textarea)
    contactSenderEmail = forms.EmailField(label='contactSenderEmail')
    cc_myself = forms.BooleanField(label='cc_myself', required=False)
    contactMessage = forms.CharField(label='contactMessage', widget=forms.Textarea, max_length=400)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date')
