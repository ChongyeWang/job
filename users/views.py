from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from jobb.utils import db, users_collection
from django.contrib.auth.hashers import check_password
from jobb.hash_utils import hash_password
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')  # Store hashed passwords in production!
            password2 = request.POST.get('password2')
            if not all([username, email, password1, password2]):
                return HttpResponseBadRequest("All fields are required.")
            if password1 != password2:
                return HttpResponseBadRequest("Passwords do not match.")
            # Adding Salt and MD5 Encryption  
            hashed_password, salt = hash_password(password1)

            # Check if user already exists in MongoDB
            if users_collection.find_one({'username': username}):
                messages.error(request, 'Username already taken.')
                return redirect('register')

# Store in MongoDB
            users_collection.insert_one({
                "username": username,
                "email": email,
                "password": hashed_password,
                "salt": salt,
                "isAdmin": False  
            })
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

from django.contrib.auth.forms import AuthenticationForm

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm()
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_data = users_collection.find_one({'username': username})
        if user_data:
            stored_salt = user_data.get('salt')
            stored_hash = user_data.get('password')
            input_hash, _ = hash_password(password, stored_salt)

            if input_hash == stored_hash:
                request.session['user_id'] = str(user_data['_id'])
                request.session['username'] = user_data['username']
                if user_data.get('isAdmin'):
                    request.session['isAdmin'] = True
                return redirect('home')

        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})



def logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
