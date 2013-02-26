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
def list_iprange(request):
  all_ranges = Range.objects.all()
  paginator = Paginator(all_ranges, 10)

  page = request.GET.get('page')
  try:
    c = paginator.page(page)
  except PageNotAnInteger:
    c = paginator.page(1)
  except EmptyPage:
    c = paginator.page(paginator.num_pages)
  return render_to_response('list-iprange.html', {'all_ranges': c})

@login_required()
def list_entries(request):
  entries = Record.objects.all()
  paginator = Paginator(entries, 20)

  page = request.GET.get('page')
  try:
    c = paginator.page(page)
  except PageNotAnInteger:
    c = paginator.page(1)
  except Emptypage:
    c = paginator.page(paginator.num_pages)
  return render_to_response('list-entries.html', {'entries': c})

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

@login_required()
def add(request):
  return render_to_response('add.html')

@login_required()
def add_domain(request):
  if request.method =='POST':
    form = DomainForm(request.POST)
    if form.is_valid():
      domain = Domain( 
        name=form.cleaned_data['name'],
        type=form.cleaned_data['type']
      )
      domain.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form = DomainForm(initial={'type': 'master'})
  
  return render_to_response('add-domain.html', {'form': form}, RequestContext(request))

@login_required()
def add_iprange(request):
  if request.method == 'POST':
    form = RangeForm(request.POST)
    if form.is_valid():
      range = Range(
        name=form.cleaned_data['name'],
        start=form.cleaned_data['start'],
        end=form.cleaned_data['end']
      )
      range.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form = RangeForm()

  return render_to_response('add-iprange.html', {'form': form}, RequestContext(request))

@login_required()
def list_iprange_entries(request, range_id=1):
  entries = Record.objects.select_related().filter(ip__range_id=range_id)
  paginator = Paginator(entries, 20)

  page = request.GET.get('page')
  try:
    c = paginator.page(page)
  except PageNotAnInteger:
    c = paginator.page(1)
  except EmptyPage:
    c = paginator.page(paginator.num_pages) 
  return render_to_response('list-iprange-entries.html', {'entries': c})

@login_required()
def add_entry(request):
  return render_to_response('add-entry.html')

@login_required()
def add_saved(request):
  return render_to_response('add-saved.html')
