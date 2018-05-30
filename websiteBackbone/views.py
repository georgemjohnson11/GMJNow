from django.shortcuts import render
from django.http import HttpResponseRedirect
from .contactform import ContactForm
from django.core.mail import send_mail

# Create your views here
def index(request):
    return render(request, 'websiteBackbone/home.html')


def submission(request):
    return render(request, 'websiteBackbone/submission.html',
                  {'content': ['An email has been sent!',
                               'If you would like to follow up please contact me, please email me']})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contactSubject = form.cleaned_data['contactSubject']
            contactMessage = form.cleaned_data['contactMessage']
            contactEmail = form.cleaned_data['contactSenderEmail']
            recipients = ['georgemjohnson11@gmail.com']
            cc_myself = form.cleaned_data['cc_myself']
            if cc_myself:
                recipients.append(contactEmail)
            #send_mail(contactSubject, contactMessage, contactEmail, recipients)
            return HttpResponseRedirect('/submission/')
    else:
        form = ContactForm()
    return render(request, 'websiteBackbone/contact.html', {'form': form})