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
from django.core.validators import validate_ipv46_address, validate_ipv4_address, validate_ipv6_address
from django.core.exceptions import ValidationError
from netaddr import *

@login_required()
def default(request):
  return render_to_response('home.html')

@login_required()
def search(request):
  return render_to_response('search.html')

@login_required()
def list_default(request):
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
      domains = Domain.objects.all()
      for d in domains:
        if d.name == form.cleaned_data['name']:
          return HttpResponseRedirect('/add/error/name')
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
      ranges = Range.objects.all()
      for range in ranges:
        if range.name == form.cleaned_data['name']:
          return HttpResponseRedirect('/add/error/name')
      try:
        validate_ipv46_address(form.cleaned_data['start'])
      except ValidationError:
        return HttpResponseRedirect('/add/error/ip')
      try:
        validate_ipv46_address(form.cleaned_data['end'])
      except ValidationError:
        return HttpResponseRedirect('/add/error/ip')
      ranges = Range.objects.all()
      found = False
      for range in ranges:
        r1 = IPRange(range.start, range.end)
        addrs = list(r1)
        if IPAddress(form.cleaned_data['start']) in addrs:
          found = True
        if IPAddress(form.cleaned_data['end']) in addrs:
          found = True
      if found:
        return HttpResponseRedirect('/add/error/range/ip')
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
  if request.method == 'POST':
    form = AddRecordForm(request.POST)
    if form.is_valid():
      domain = Domain.objects.get(id=form.cleaned_data['domain'])
      records = Record.objects.all()
      for record in records:
        if form.cleaned_data['name'] == record.name:
          if record.domain_id == domain:
            return HttpResponseRedirect('/add/error/name')  
      content = form.cleaned_data['content']
      if form.cleaned_data['type'] == 'A':
        try:
          validate_ipv4_address(content)
        except ValidationError:
          return HttpResponseRedirect('/add/error/ip')
      if form.cleaned_data['type'] == 'AAAA':
        try:
          validate_ipv6_address(content)
        except ValidationError:
          return HttpResponseRedirect('/add/error/ip')
      ranges = Range.objects.all()
      found = False
      for range in ranges:
        r1 = IPRange(range.start, range.end)
        addrs = list(r1)
        if IPAddress(content) in addrs:
          found = True
      if not found:
        return HttpResponseRedirect('/add/error/range')
      ips = Ip.objects.all()
      for ip in ips:
        if ip.ip == content:
          return HttpResponseRedirect('add/error/ip') 
      record = Record(
        name=form.cleaned_data['name'],
        type=form.cleaned_data['type'],
	content=form.cleaned_data['content'],
        ttl=form.cleaned_data['ttl'],
        domain_id = domain,
        pri = 1,
        changedate = 1
      )
      record.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form = AddRecordForm()

  return render_to_response('add-entry.html', {'form': form}, RequestContext(request))

@login_required()
def add_saved(request):
  return render_to_response('add-saved.html')

@login_required()
def add_error_ip(request):
  return render_to_response('add-error-ip.html')

@login_required()
def add_error_range(request):
  return render_to_response('add-error-range.html')

@login_required()
def add_error_range_ip(request):
  return render_to_response('add-error-range-ip.html')

@login_required()
def add_error_name(request):
  return render_to_response('add-error-name.html')

@login_required()
def add_error_ip_exists(request):
  return render_to_response('add-error-ip-exists.html')

@login_required()
def delete(request):
  return render_to_response('del.html')

@login_required()
def del_record(request, record_id=1):
  entry = Record.objects.get(id=record_id)
  return render_to_response('del-record.html', {'entry': entry})

@login_required()
def del_del_record(request, record_id=1):
  entry = Record.objects.get(id=record_id)
  entry.delete()
  return render_to_response('del-deleted.html')
