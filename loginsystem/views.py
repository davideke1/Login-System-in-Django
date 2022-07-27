from django.contrib.auth import authenticate, login, logout
from system import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages


# Create your views here.
def home(request):
    return render(request, "loginsystem/index.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        email = request.POST['email']
        pass1 = request.POST['password']
        pass2 = request.POST['confirmpassword']

        if User.objects.filter(username=username):
            messages.error(request, 'Username already exist!')
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request, 'Email already registered!')
            return redirect('home')

        if len(username) >10:
            messages.error(request, 'username must be under 10 character')

        if pass1 != pass2:
            messages.error(request, 'Passwords does not match')

        if not username.isalnum():
            messages.error(request, "Username must be alpha-Numeric")
            return redirect('home')

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been successfully created.")

        #emailing
        subject = "Welcome To david apps"
        message = "Hello " +myuser.first_name + "!! \n" + "Welcome to David apps we serve you the best\nWe have sent a confirmation email confirm your email address to activate your account.\nThanks\n David."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message,from_email, to_list, fail_silently=True)

        return redirect('signin')
    return render(request, "loginsystem/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['password']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "loginsystem/index.html", {'fname':fname})

        else:
            messages.error(request, "Invalid Password or username")
            return redirect('home')

    return render(request, "loginsystem/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Your are successfully logged out")
    return redirect('home')