from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .models import FloodAlert


def home(request):
    return render(request, 'home.html')


def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')

    return render(request, 'register.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('home')


def alerts(requests):
    alerts = FloodAlert.objects.all().order_by('-created_at')
    return render( request, "alerts.html", {"alerts":alerts})
