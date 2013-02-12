from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from iptracker.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required()
def default(request):
  return render_to_response('home.html')

@login_required()
def search(request):
  return render_to_response('search.html')

@login_required()
def list(request):
  return render_to_response('list.html')

@login_required()
def list_domains(request):
  all_domains = Domain.objects.all()
  paginator = Paginator(all_domains, 10)

  page = request.GET.get('page')
  try:
    c = paginator.page(page)
  except PageNotAnInteger:
    c = paginator.page(1)
  except EmptyPage:
    c = paginator.page(paginator.num_pages)
  return render_to_response('list-domains.html', {'all_domains': c})

def list_domains_entries(request):
  return render_to_response('list-domains-entries.html')
