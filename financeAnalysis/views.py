from django.shortcuts import render


def financeHome(request):
    return render(request, 'financeHome.html')
