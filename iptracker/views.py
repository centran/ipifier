from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect 
from django.template.response import TemplateResponse
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from iptracker.models import *
from iptracker.forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext

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

@login_required()
def list_domains_entries(request, domain_id=1):
  entries = Record.objects.filter(domain_id=domain_id).select_related()
  paginator = Paginator(entries, 20)

  page = request.GET.get('page')
  try:
    c = paginator.page(page)
  except PageNotAnInteger:
    c = paginator.page(1)
  except EmptyPage:
    c = paginator.page(paginator.num_pages) 
  return render_to_response('list-domains-entries.html', {'entries': c})

@login_required()
def edit_record(request, record_id=1):
  org_record = Record.objects.get(id=record_id)
  if request.method == 'POST':
    form = RecordForm(request.POST)
    if form.is_valid():
      record = Record(
        id=record_id,
        name=form.cleaned_data['name'],
        type=form.cleaned_data['type'],
        content=form.cleaned_data['content'],
        ttl=form.cleaned_data['ttl'],
        domain_id = org_record.domain_id,
	pri = org_record.pri,
        changedate = org_record.changedate
      )
      record.save()
      return HttpResponseRedirect('/edit/record/saved')
  else:
    form = RecordForm(initial={
      'name': org_record.name,
      'type': org_record.type,
      'content': org_record.content,
      'ttl': org_record.ttl
      })
    
  record = Record.objects.get(id=record_id)
  return render_to_response('edit-record.html', {'record': record, 'id': record_id, 'form': form}, RequestContext(request))

@login_required()
def edit_record_saved(request):
  return render_to_response('edit-record-saved.html')

@login_required()
def edit(request):
  return render_to_response('edit.html')
