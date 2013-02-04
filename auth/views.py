from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login

def login_user(request):
  state = "Please login..."
  username = ''
  password = ''
  if request.POST:
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(username=username, password=password)
    if user is not None:
      if user.us_active:
        login(request,user)
        state = "Login successfull"
      else:
        state = "Your account is not active"
    else:
      state = "Username or password is incorrect"
    
  return render_to_response('auth.html',{'state':state, 'username': username})
