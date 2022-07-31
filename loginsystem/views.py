import re
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from loginsystem.token import generate_token


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

        x = re.search("\w+(gitam).in", email)
        x = bool(x)
        if x != True:
            messages.error(request, 'Gitam email only')

        if User.objects.filter(email=email):
            messages.error(request, 'Email already registered!')
            return redirect('home')

        if len(username) > 10:
            messages.error(request, 'username must be under 10 character')

        if pass1 != pass2:
            messages.error(request, 'Passwords does not match')

        if not username.isalnum():
            messages.error(request, "Username must be alpha-Numeric")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False

        myuser.save()

        messages.success(request, "Your account has been successfully created.")

        # emailing

        subject = "Welcome To david apps"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to David apps we serve you the best\nWe have sent a confirmation email confirm your email address to activate your account.\nThanks\nDavid."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)

        # Email address confirmation

        current_site = get_current_site(request)
        email_subject = "Confirm your email @ David Apps"
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )
        email.fail_silently = True
        email.send()

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
            return render(request, "loginsystem/index.html", {'fname': fname})

        else:
            messages.error(request, "Invalid Password or username")
            return redirect('home')

    return render(request, "loginsystem/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Your are successfully logged out")
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')

    else:
        return render(request, 'activation_failed.html')
