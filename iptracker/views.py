from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect 
from django.template.response import TemplateResponse
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from iptracker.models import *
from iptracker.forms import *
from django.template import RequestContext
from django.core.validators import validate_ipv46_address, validate_ipv4_address, validate_ipv6_address
from django.core.exceptions import ValidationError
from netaddr import *
import datetime
from itertools import chain

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
  all_domains = Domain.objects.all().order_by('name')
  return render_to_response('list-domains.html', {'all_domains': all_domains})

@login_required()
def list_iprange(request):
  all_ranges = Range.objects.all().order_by('name')
  return render_to_response('list-iprange.html', {'all_ranges': all_ranges})

@login_required()
def list_iprange_entries(request, range_id=1):
  entries = Record.objects.select_related().filter(ip__range_id=range_id).order_by('name')
  ips = Ip.objects.select_related().filter(range_id=range_id).order_by('ip')
  return render_to_response('list-iprange-entries.html', {'entries': entries,'ips': ips})

@login_required()
def list_entries(request):
  entries = Record.objects.all().order_by('name').select_related()
  return render_to_response('list-entries.html', {'entries': entries}, context_instance=RequestContext(request))

@login_required()
def list_domains_entries(request, domain_id=1):
  entries = Record.objects.filter(domain_id=domain_id).select_related().order_by('name')
  return render_to_response('list-domains-entries.html', {'entries': entries})

@login_required()
def list_ips(request):
  all_ips = Ip.objects.all()
  return render_to_response('list-ips.html', {'all_ips': all_ips})

@login_required()
def edit_record(request, record_id=1):
  org_record = Record.objects.get(id=record_id)
  org_ip = Ip.objects.get(record_id=record_id)
  if request.method == 'POST':
    form = EditRecordForm(request.POST)
    if form.is_valid():
      domain = Domain.objects.get(id=form.cleaned_data['domain'])
      records = Record.objects.all()
      if form.cleaned_data['name'] != org_record.name:
        for record in records:
          if form.cleaned_data['name'] == record.name:
            if record.domain_id == domain:
              return HttpResponseRedirect('/add/error/name')
      content = form.cleaned_data['content']
      ranges = Range.objects.all()
      rangeRecord = 0
      for range in ranges:
        r1 = IPRange(range.start, range.end)
        addrs = list(r1)
        if IPAddress(content) in addrs:
          rangeRecord = range
          break
      ip_changed = False
      if content != org_record.content:
        ip_changed = True
        ips = Ip.objects.all()
        for ip in ips:
          if ip.ip == content:
            return HttpResponseRedirect('/add/error/ip/exists')
      mac_changed = False
      if form.cleaned_data['mac'] != org_ip.mac:
        mac_changed = True
        macs = Ip.objects.all()
        for mac in macs:
          if mac.mac == form.cleaned_data['mac']:
            return HttpResponseRedirect('/add/error/mac/exists')
      record = Record(
        id=record_id,
        name=form.cleaned_data['name'],
        type=form.cleaned_data['type'],
        content=form.cleaned_data['content'],
        ttl=form.cleaned_data['ttl'],
        domain_id = org_record.domain_id,
	pri = org_record.pri,
        comment=form.cleaned_data['comment']
      )
      record.save()
      if ip_changed or mac_changed:
        ip = Ip.objects.get(record_id=record)
        ip.delete()
        ip = Ip(ip=content,record_id=record,range_id=rangeRecord,mac=form.cleaned_data['mac'])
        ip.save()
      return HttpResponseRedirect('/edit/record/saved')
  else:
    form = EditRecordForm(initial={
      'name': org_record.name,
      'type': org_record.type,
      'content': org_record.content,
      'pri': org_record.pri,
      'ttl': org_record.ttl,
      'comment': org_record.comment,
      'mac': org_ip.mac
      })
    
  record = Record.objects.get(id=record_id)
  return render_to_response('edit-record.html', {'record': record, 'id': record_id, 'form': form}, RequestContext(request))

@login_required()
def edit_domain(request, domain_id=1):
  org_domain = Domain.objects.get(id=domain_id)
  if request.method == 'POST':
    form = DomainForm(request.POST)
    domains = Domain.objects.all()
    if form.is_valid():
      if form.cleaned_data['name'] != org_domain.name:
        for domain in domains:
          if domain.name == form.cleaned_data['name']:
            return HttpResponseRedirect('/edit/error/name')
      domain = Domain(
        id=domain_id,
        name=form.cleaned_data['name'],
        type=form.cleaned_data['type'],
        comment=form.cleaned_data['comment']
      )
      domain.save()
      return HttpResponseRedirect('/edit/record/saved')
  else:
    form = DomainForm(initial={
      'name': org_domain.name,
      'type': org_domain.type,
      'comment': org_domain.comment
    })
  domain = Domain.objects.get(id=domain_id)
  return render_to_response('edit-domain.html', {'domain': domain, 'id': domain_id, 'form': form}, RequestContext(request))

@login_required()
def edit_ip(request, ip_id=1):
  org_ip = Ip.objects.get(id=ip_id)
  if org_ip.record_id:
    return HttpResponseRedirect('/edit/record/'+str(org_ip.record_id.id))
  if request.method == 'POST':
    form = EditIpForm(request.POST)
    if form.is_valid():
      ranges = Range.objects.all()
      rangeRecord = 0
      ip = form.cleaned_data['ip']
      for range in ranges:
        r1 = IPRange(range.start, range.end)
        addrs = list(r1)
        if IPAddress(ip) in addrs:
          rangeRecord = range
          break
      ip_changed = False
      if ip != org_ip:
        ip_changed = True
        ips = Ip.objects.all()
        for i in ips:
          if i == ip:
            return HttpResponseRedirect('/add/error/ip/exists')
      mac_changed = False
      if form.cleaned_data['mac'] != org_ip.mac:
        mac_changed = True
        macs = Ip.objects.all()
        for mac in macs:
          if mac.mac == form.cleaned_data['mac']:
            return HttpResponseRedirect('/add/error/mac/exists')
      ip = Ip(
        id=org_ip.id,
        ip=form.cleaned_data['ip'],
        range_id=rangeRecord,
        mac=form.cleaned_data['mac'],
        comment=form.cleaned_data['comment']
      )
      ip.save()
      return HttpResponseRedirect('/edit/record/saved')
  else:
    form = EditIpForm(initial={
      'ip': org_ip.ip,
      'mac': org_ip.mac,
      'comment': org_ip.comment
    })
  return render_to_response('edit-ip.html', {'form': form},RequestContext(request))

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
        type=form.cleaned_data['type'],
        comment=form.cleaned_data['comment']
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
        end=form.cleaned_data['end'],
        comment=form.cleaned_data['comment']
      )
      range.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form = RangeForm()

  return render_to_response('add-iprange.html', {'form': form}, RequestContext(request))

@login_required()
def add_entry(request):
  if request.method == 'POST':
    form = RecordForm(request.POST)
    if form.is_valid():
      domain = Domain.objects.get(id=form.cleaned_data['domain'])
      content=form.cleaned_data['content']
      ranges = Range.objects.all()
      rangeRecord = 0
      for range in ranges:
        r1 = IPRange(range.start, range.end)
        addrs = list(r1)
        if IPAddress(content) in addrs:
          rangeRecord = range
          break
      record = Record(
        name=form.cleaned_data['name'],
        type=form.cleaned_data['type'],
	content=content,
        ttl=form.cleaned_data['ttl'],
        domain_id=domain,
        pri=form.cleaned_data['pri'],
        comment=form.cleaned_data['comment'],
      )
      record.save()
      ip = Ip(ip=content,record_id=record,range_id=rangeRecord,mac=form.cleaned_data['mac'])
      ip.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form =RecordForm(initial={'ttl': 3600,'pri': 10})

  return render_to_response('add-entry.html', {'form': form}, RequestContext(request))

@login_required()
def add_ip(request):
  if request.method == 'POST':
    form = IpForm(request.POST)
    if form.is_valid():
      ranges = Range.objects.all()
      rangeRecord = 0
      for range in ranges:
        r1 = IPRange(range.start, range.end)
        addrs = list(r1)
        if IPAddress(form.cleaned_data['ip']) in addrs:
          rangeRecord = range
          break
      ip = Ip(
        ip=form.cleaned_data['ip'],
        mac=form.cleaned_data['mac'],
        range_id=rangeRecord,
        comment=form.cleaned_data['comment'] 
      )
      ip.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form = IpForm()
  return render_to_response('add-ip.html', {'form': form}, RequestContext(request))

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
def add_error_mac_exists(request):
  return render_to_response('add-error-mac-exists.html')

@login_required()
def edit_error_name(request):
  return render_to_response('edit-error-name.html')

@login_required()
def delete(request):
  return render_to_response('del.html')

@login_required()
def del_record(request, record_id=1):
  entry = Record.objects.get(id=record_id)
  return render_to_response('del-record.html', {'entry': entry})

@login_required()
def del_domain(request, domain_id=1):
  domain = Domain.objects.get(id=domain_id)
  return render_to_response('del-domain.html', {'domain': domain})

@login_required()
def del_ip(request, ip_id=1):
  ip = Ip.objects.get(id=ip_id)
  if ip.record_id:
    entry = Record.objects.get(id=ip.record_id.id)
    return render_to_response('del-record.html', {'entry': entry})
  return render_to_response('del-ip.html', {'ip': ip})

@login_required()
def del_del_record(request, record_id=1):
  ip = Ip.objects.get(record_id=record_id)
  ip.delete()
  entry = Record.objects.get(id=record_id)
  entry.delete()
  return render_to_response('del-deleted.html')

@login_required()
def del_del_domain(request, domain_id=1):
  domain = Domain.objects.get(id=domain_id)
  entries = Record.objects.select_related().filter(domain_id=domain_id)
  for entry in entries:
    entry.delete()
  domain.delete()
  return render_to_response('del-deleted.html')

@login_required()
def del_del_ip(request, ip_id):
  ip = Ip.objects.get(id=ip_id)
  ip.delete()
  return render_to_response('del-deleted.html')
