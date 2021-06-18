from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def home(request):
    return render(request, 'home.html')

def login_attempt(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username).first()
        if user_obj is None:
            messages.warning(request, 'User not found. Please register.')
            return redirect('/login')
        
        profile_obj = Profile.objects.filter(user = user_obj).first()
        if not profile_obj.is_verified:
            messages.warning(request, 'Profile is not verified check your mail.')
            return redirect('/login')

        user = authenticate(username = username , password = password)
        if user is None:
            messages.warning(request, 'Wrong password.')
            return redirect('/accounts/login')
        
        context ={ user: user}
        login(request , user)
        return redirect('/', context)

    return render(request, 'login.html')

def register(request):

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
                
            if User.objects.filter(username = username).first():
                messages.warning(request, 'This username is already taken, please try another one.')
                return redirect('/register')

            if User.objects.filter(email = email).first():
                messages.warning(request, 'This email is already taken, please register from another email.')
                return redirect('/register')

            
            user_obj = User.objects.create(username = username, email = email )
            user_obj.set_password(password)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user = user_obj, auth_token= auth_token)
            profile_obj.save() 
            send_email_verifaction(email, auth_token)
            return redirect('/token')
        
        except Exception as e:
            print(e)
            
    return render(request, 'register.html')

def token_send(request):
    return render(request, 'token_send.html')

def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified')
                return redirect('/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified')
            return redirect('/login')
        else:
            return redirect('/error')

    except Exception as e:
        print(e)

def error_page(request):
    return render(request, 'error.html')

def change_pass(request, auth_token):
    context={}
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
        context = {'user_id': profile_obj.user.id}
        print(profile_obj)
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            user_id = request.POST.get('user_id')

            if user_id is None:
                messages.warning(request, 'No user ID found.')
                return redirect(f'/change_pass/{auth_token}/')

            if new_password != confirm_password:
                messages.warning(request, "Both should be equal.")
                return redirect(f'/change_pass/{auth_token}')
            
            user_obj = User.objects.get(id = user_id)
            user_obj.set_password(new_password)
            user_obj.save()
            return redirect('login')

    except Exception as e:
        print(e)
    return render(request, 'change_pass.html', context=context)

def forget_pass(request):
    try:
        if request.method == "POST":
            username = request.POST.get('username')
        
            user_obj = User.objects.filter(username = username).first()
            if user_obj is None:
                messages.warning(request, 'User not found. Please register.')
                return redirect('/login')

            auth_token = str(uuid.uuid4())
            send_email_reset_pass(user_obj.email, auth_token)
            profile_obj = Profile.objects.get(user = user_obj)
            profile_obj.auth_token = auth_token
            profile_obj.save()
            messages.success(request, 'An email is send to you. Please check your email')
            return redirect('/forget_pass')

    except Exception as e:
            print(e)

    return render(request, 'forget_pass.html')

def send_email_reset_pass(email, token):
    subject = "Reset password"
    message = f"Hi click on the link to change your password http://127.0.0.1:8000/change_pass/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    
def send_email_verifaction(email, token):
    subject = "Email Verification"
    message = f"Hi click on the link to verify your account http://127.0.0.1:8000/verify/{token}"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    