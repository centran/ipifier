from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required

@login_required()
def default(request):
  return HttpResponse('Hello default page')
