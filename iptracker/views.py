from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required

@login_required()
def default(request):
  return render_to_response('home.html')

@login_required()
def search(request):
  return render_to_response('home.html')

@login_required()
def list(request):
  return render_to_response('home.html')
