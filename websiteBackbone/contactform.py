from django import forms


class ContactForm(forms.Form):
    contactName = forms.CharField(label='contactName', max_length=100)
    contactSubject = forms.CharField(label='contactSubject', widget=forms.Textarea)
    contactSenderEmail = forms.EmailField(label='contactSenderEmail')
    cc_myself = forms.BooleanField(label='cc_myself', required=False)
    contactMessage = forms.CharField(label='contactMessage', widget=forms.Textarea, max_length=400)
