from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from jobb.utils import db, users_collection
from django.contrib.auth.hashers import check_password

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
	        username = request.POST.get('username')
	        email = request.POST.get('email')
	        password = request.POST.get('password')  # Store hashed passwords in production!
	        
	        user_data = {
	            'username': username,
	            'email': email,
	            'password': password,
	        }
	        result = users_collection.insert_one(user_data)

        return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

from django.contrib.auth.forms import AuthenticationForm

def user_login(request):
	if request.method == 'POST':
		form = AuthenticationForm()
		username = request.POST.get('username')
		email = request.POST.get('email')
		password = request.POST.get('password')
		user_data = users_collection.find_one({'username': username, 'password': password})
		if user_data:
			request.session['user_id'] = str(user_data['_id'])  # Store user ID in session
			request.session['username'] = user_data['username']  # Store username in session
			if user_data['isAdmin']:
				request.session['isAdmin'] = True
			return redirect('home')
		else:
			messages.error(request, 'Invalid username or password.')
	else:
		form = AuthenticationForm()
	return render(request, 'login.html', {'form': form})


def logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')
