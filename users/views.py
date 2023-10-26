from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import render
from .models import SignUpModel,UserModel,LoginModel
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

# Create your views here.

def opening(request):
    return render(request, 'opening.html')   

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try to retrieve the user from the database
        try:
            user = SignUpModel.objects.get(username=username)
        except SignUpModel.DoesNotExist:
            user = None

        # Check if the user exists and the password is correct
        if user and user.check_password(password):
            # If so, log in the user
            request.session['user_id'] = user.id  # You can use Django's session framework to keep the user logged in
            return redirect('admin_dashboard')  # Replace with your actual dashboard URL name
        else:
            # Handle invalid login here (e.g., display an error message)
            error_message_usernname_or_password_mismatch = "Username or password is wrong. Please try again."
            return render(request, 'signin.html', {'error_message_usernname_or_password_mismatch': error_message_usernname_or_password_mismatch})


    return render(request, 'signin.html')

def signup(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass')
        pass2 = request.POST.get('con_pass')

        if SignUpModel.objects.filter(username=uname).exists():
            error_message_duplicate_username = "Username already exists. Please choose another username."
            return render(request, 'signup.html', {'error_message_duplicate_username': error_message_duplicate_username, 'email': email})

        elif pass1 != pass2:
            error_message_password_mismatch = "Passwords do not match. Please try again."
            return render(request, 'signup.html', {'error_message_password_mismatch': error_message_password_mismatch, 'username': uname, 'email': email})

        else:
            # Assuming the email format is also validated
            pass1 = make_password(pass1)
            new_user = SignUpModel(username=uname, email=email, password=pass1)
            new_user.save()
            return redirect('signin')  # Redirect to a success page

    return render(request, 'signup.html')

def success(request):
    return render(request, 'success.html')

def failed(request):
    return render(request, 'failed.html')