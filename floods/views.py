from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .forms import ReliefForm

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


def apply_relief(request):

    if request.method == 'POST':
        form = ReliefForm(request.POST)

        if form.is_valid():
            relief = form.save(commit=False)
            relief.user = request.user
            relief.save()
            return redirect('home')

    else:
        form = ReliefForm()

    return render(request, "apply.html", {'form': form})
