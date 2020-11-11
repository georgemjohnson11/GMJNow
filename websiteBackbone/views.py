from django.conf import settings
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import HttpResponse, BadHeaderError, HttpResponseRedirect
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from websiteBackbone.forms import CustomUserCreationForm, ContactForm


def update_profile(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST, instance=request.user)
        if user_form.is_valid() and request.user.is_authenticated:
            user_form.save()
            messages.success(request, ('Your profile was successfully updated!'))
            return render(request, 'registration/user_profile.html')
        else:
            messages.error(request, ('Please login or correct the error below.'))
    else:
        user_form = CustomUserCreationForm(instance=request.user)
    return render(request, 'registration/password_change_form.html',
                  {'user_form': user_form} )


def register(request):
     if request.method == "GET":
         return render(
             request, "registration/register.html",
             {"form": CustomUserCreationForm}
         )
     elif request.method == "POST":
         form = CustomUserCreationForm(request.POST)
         if form.is_valid():
             user = form.save()
             login(request, user)
             return redirect(reverse('index'))
         messages.error(request, ('Please correct the error below.'))
         return render(
             request, "registration/register.html",
             {"form": CustomUserCreationForm}
         )

def about(request):
    return render(request, './websiteBackbone/about.html')

def index(request):
    return render(request, './websiteBackbone/home.html')

def privacypolicy(request):
    return render(request, './websiteBackbone/privacypolicy.html')

def termsconditions(request):
    return render(request, './websiteBackbone/termsconditions.html')

def submission(request):
    return render(request, './websiteBackbone/submission.html',
                  {'content': ['An email has been sent!',
                               'A representative will follow up within 3-5 business days.']})


def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            contactSubject = form.cleaned_data['contactSubject']
            contactMessage = form.cleaned_data['contactMessage']
            contactEmail = form.cleaned_data['contactSenderEmail']
            recipients = ['resources@gmjnow.com']
            cc_myself = form.cleaned_data['cc_myself']
            if cc_myself:
                recipients.append(contactEmail)
            try:
                email = EmailMessage(contactSubject, contactMessage, settings.DEFAULT_FROM_EMAIL, recipients)
                email.send()
            except KeyError:
                return HttpResponse('Please fill in all fields')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return HttpResponseRedirect('/submission/')
    return render(request, "websiteBackbone/contact.html", {'form': form})
