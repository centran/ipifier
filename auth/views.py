from django.shortcuts import render_to_response
from django.contrib.auth import authenticate 
from django.http import HttpResponse
from django.template.response import TemplateResponse

def logout(request):
  return TemplateResponse(request, 'registration/logout.html')
