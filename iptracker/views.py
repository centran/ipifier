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
import datetime
from itertools import chain
from django.db.models import Q
import sync_named

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
  entries = Record.objects.all()
  ips = Ip.objects.all()
  range = Range.objects.get(id=range_id)
  r = IPNetwork(range.cidr)
  addrs = list(r)
  ip_list = []
  for ip in ips:
    if IPAddress(ip.ip) in addrs:
      ip_list.append(ip)
  entry_list = []
  for entry in entries:
    if entry.type == 'A' or entry.type == 'AAAA':
      if IPAddress(entry.content) in addrs:
        entry_list.append(entry)
  return render_to_response('list-iprange-entries.html', {'entries': entry_list,'ips': ip_list})

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
def edit_record(request, record_id=0):
  org_record = Record.objects.get(id=record_id)
  try:
    org_ip = Ip.objects.get(record_id=record_id)
  except Ip.DoesNotExist:
    org_ip = 0
  if request.method == 'POST':
    form = EditRecordForm(request.POST)
    if form.is_valid():
      domain = Domain.objects.get(id=form.cleaned_data['domain'])
      comment = form.cleaned_data['comment']
      type = form.cleaned_data['type']
      content = form.cleaned_data['content']
      ranges = Range.objects.all()
      rangeRecord = 0
      ip_changed = False
      if content != org_record.content and (type == 'A' or type == 'AAAA'):
        ip_changed = True
      mac_changed = False
      if org_ip != 0 and form.cleaned_data['mac'] != org_ip.mac:
        mac_changed = True
      record = Record(
        id=record_id,
        name=form.cleaned_data['name'],
        type=form.cleaned_data['type'],
        content=form.cleaned_data['content'],
        ttl=form.cleaned_data['ttl'],
        domain_id = domain,
        pri = org_record.pri,
        comment=form.cleaned_data['comment']
      )
      record.save()
      if comment is None or comment == '':
        comment = form.cleaned_data['name']
      if ip_changed or mac_changed:
        ip = Ip.objects.get(record_id=record)
        ip.delete()
        ip = Ip(ip=content,record_id=record,range_id=rangeRecord,mac=form.cleaned_data['mac'],comment=comment)
        ip.save()
      return HttpResponseRedirect('/edit/record/saved')
  else:
    if org_ip == 0:
      form = EditRecordForm(initial={
      'name': org_record.name,
      'type': org_record.type,
      'content': org_record.content,
      'pri': org_record.pri,
      'ttl': org_record.ttl,
      'comment': org_record.comment,
      })
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
def edit_domain(request, domain_id=0):
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
def edit_ip(request, ip_id=0):
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
        r1 = IPNetwork(range.cidr)
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
def edit_iprange(request, range_id=1):
  org_range = Range.objects.get(id=range_id)
  if request.method == 'POST':
    form = EditRangeForm(request.POST)
    if form.is_valid():
      name = form.cleaned_data['name']
      names = Range.objects.all()
      for n in names:
        if name != org_range.name and n == name:
          return HttpResponseRedirect('/edit/error/name')
      range = Range(
        id = org_range.id,
        name = form.cleaned_data['name'],
        cidr = org_range.cidr,
        comment = form.cleaned_data['comment']
      )
      range.save()
      return HttpResponseRedirect('/edit/record/saved')
  else:
    form = EditRangeForm(initial={
      'name': org_range.name,
      'cidr': org_range.cidr,
      'comment': org_range.comment
    })
  return render_to_response('edit-iprange.html', {'form': form}, RequestContext(request))

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
  if request.method == 'POST':
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
      range = Range(
        name=form.cleaned_data['name'],
        cidr=form.cleaned_data['cidr'],
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
      mac=form.cleaned_data['mac']
      comment = form.cleaned_data['comment']
      name = form.cleaned_data['name']
      type = form.cleaned_data['type']
      ips = Ip.objects.all()
      warning = ''
      warn = False
      for ip in ips:
        if content == ip.ip:
          warn = True
          warning = warning + 'IP already exists. '
        if mac == ip.mac and mac:
          warn = True
          warning = warning + 'MAC already exists. '
        if warn:
          break
      if warn:
        request.session['_old_post'] = form.cleaned_data
        request.session['warning'] = warning
        return HttpResponseRedirect('/add/entry/warn')
      if name[-1] == '.':
        name = name[0:-1]
      record = Record(
        name=name,
        type=type,
        content=content,
        ttl=form.cleaned_data['ttl'],
        domain_id=domain,
        pri=form.cleaned_data['pri'],
        comment=comment,
      )
      record.save()
      if type == 'A' or type == 'AAAA':
        if comment is None or comment == '':
          comment = form.cleaned_data['name']
        ip = Ip(ip=content,record_id=record,mac=form.cleaned_data['mac'],comment=comment)
        ip.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form = RecordForm(initial={'ttl': 3600,'pri': 10})

  return render_to_response('add-entry.html', {'form': form}, RequestContext(request))

@login_required()
def add_entry_warn(request):
  if request.method == 'POST':
    form = RecordForm(request.POST)
    if form.is_valid():
      domain = Domain.objects.get(id=form.cleaned_data['domain'])
      content=form.cleaned_data['content']
      comment=form.cleaned_data['comment']
      type = form.cleaned_data['type']
      name = form.cleaned_data['name']
      if name[-1] == '.':
        name = name[0:-1]
      record = Record(
        name=name,
        type=type,
        content=content,
        ttl=form.cleaned_data['ttl'],
        domain_id=domain,
        pri=form.cleaned_data['pri'],
        comment=form.cleaned_data['comment'],
      )
      record.save()
      if type == 'A' or type == 'AAAA':
        if comment is None or comment == '':
          comment = form.cleaned_data['name']
        ip = Ip(ip=content,record_id=record,mac=form.cleaned_data['mac'],comment=comment)
        ip.save()
      return HttpResponseRedirect('/add/saved')
  else:
    old_post = request.session.get('_old_post')
    form = RecordForm(initial={
      'name': old_post['name'],
      'type': old_post['type'],
      'content': old_post['content'],
      'ttl': old_post['ttl'],
      'domain_id': old_post['domain'],
      'pri': old_post['pri'],
      'comment': old_post['comment']
    })
  return render_to_response('add-entry-warn.html', {'form': form}, RequestContext(request))

@login_required()
def add_entry_ip(request, ip):
  if request.method == 'POST':
    form = RecordForm(request.POST)
    if form.is_valid():
      domain = Domain.objects.get(id=form.cleaned_data['domain'])
      content=form.cleaned_data['content']
      comment=form.cleaned_data['comment']
      record = Record(
        name=form.cleaned_data['name'],
        type=form.cleaned_data['type'],
        content=content,
        ttl=form.cleaned_data['ttl'],
        domain_id=domain,
        pri=form.cleaned_data['pri'],
        comment=form.cleaned_data['comment'],
      )
      record.save
      if name[-1] == '.':e()
      if type == 'A' or type == 'AAAA':
        if comment is None or comment == '':
          comment = form.cleaned_data['name']
        ip = Ip(ip=content,record_id=record,mac=form.cleaned_data['mac'],comment=comment)
        ip.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form = RecordForm(initial={'content': ip, 'ttl': 3600,'pri': 10})

  return render_to_response('add-entry.html', {'form': form}, RequestContext(request))

@login_required()
def add_ip(request):
  if request.method == 'POST':
    form = IpForm(request.POST)
    if form.is_valid():
      addr = form.cleaned_data['ip']
      if len(addr) > 3 and (addr[-2] == '/' or addr[-3] == '/'):
        ip_list = list(IPNetwork(addr))
        for i in ip_list:
          if i == addr:
            ip = Ip(ip=i,mac=form.cleaned_data['mac'],comment=form.cleaned_data['comment'])
          else:
            ip = Ip(ip=i,mac='',comment=form.cleaned_data['comment'])
          ip.save()
      else:
        ip = Ip(
          ip=form.cleaned_data['ip'],
          mac=form.cleaned_data['mac'],
          comment=form.cleaned_data['comment'] 
        )
        ip.save()
      return HttpResponseRedirect('/add/saved')
  else:
    form = IpForm()
  return render_to_response('add-ip.html', {'form': form}, RequestContext(request))

@login_required()
def add_ip_ip(request, ip):
  if request.method == 'POST':
    form = IpForm(request.POST)
    if form.is_valid():
      addr = form.cleaned_data['ip']
      if len(addr) > 3 and (addr[-2] == '/' or addr[-3] == '/'):
        ip_list = list(IPNetwork(addr))
        for i in ip_list:
          if i == addr:
            ip = Ip(ip=i,mac=form.cleaned_data['mac'],comment=form.cleaned_data['comment'])
          else:
            ip = Ip(ip=i,mac='',comment=form.cleaned_data['comment'])
          ip.save()
      else:
        ip = Ip(
          ip=form.cleaned_data['ip'],
          mac=form.cleaned_data['mac'],
          comment=form.cleaned_data['comment'] 
        )
        ip.save()
    return HttpResponseRedirect('/add/saved')
  else:
    form = IpForm(initial={'ip': ip})
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
def del_domain(request, domain_id=0):
  domain = Domain.objects.get(id=domain_id)
  return render_to_response('del-domain.html', {'domain': domain})

@login_required()
def del_ip(request, ip_id=0):
  ip = Ip.objects.get(id=ip_id)
  if ip.record_id:
    entry = Record.objects.get(id=ip.record_id.id)
    return render_to_response('del-record.html', {'entry': entry})
  return render_to_response('del-ip.html', {'ip': ip})

@login_required()
def del_iprange(request, range_id=0):
  range = Range.objects.get(id=range_id)
  return render_to_response('del-iprange.html', {'range': range})

@login_required()
def del_del_record(request, record_id=1):
  entry = Record.objects.get(id=record_id)  
  if entry.type == 'A' or entry.type == 'AAAA':
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

@login_required()
def del_del_iprange(request, range_id=0):
  range = Range.objects.get(id=range_id)
  range.delete()
  return render_to_response('del-deleted.html')

@login_required()
def search_global(request):
  if request.method == 'POST':
    form = SearchForm(request.POST)
    if form.is_valid():
      term = form.cleaned_data['term']
      entries = Record.objects.all().filter( Q(name__icontains=term) | Q(content__icontains=term) | Q(comment__icontains=term) )
      domains = Domain.objects.all().filter( Q(name__icontains=term) | Q(comment__icontains=term) )
      ranges = Range.objects.all().filter( Q(name__icontains=term) | Q(comment__icontains=term) | Q(cidr__icontains=term) )
      ips = Ip.objects.all().filter( Q(ip__icontains=term) | Q(mac__icontains=term) | Q(comment__icontains=term) )
      return render_to_response('search-global.html', {
        'form': form, 
        'entries': entries,
        'all_domains': domains,
        'all_ranges': ranges,
        'all_ips': ips
      }, RequestContext(request))
  else:
    form = SearchForm()
  return render_to_response('search-global.html', {'form': form}, RequestContext(request))

@login_required()
def search_ip(request):
  if request.method == 'POST':
    form = IpSearchForm(request.POST)
    if form.is_valid():
      term = form.cleaned_data['term']      
      term = IPAddress(term)
      ips = Ip.objects.all()
      i = 0
      ip_list = []
      while i < 5:
        found = False
        for ip in ips:
          if term == IPAddress(ip.ip):
            found = True
            break
        if found:
          term = term + 1
        else:
          ip_list.append(str(term))
          term = term + 1
          i = i + 1
      return render_to_response('search-ip.html', {
        'form': form,
        'ip_list': ip_list
      }, RequestContext(request))
  else:
    form = IpSearchForm()
  return render_to_response('search-ip.html', {'form': form}, RequestContext(request))

@login_required()
def search_iprange(request):
  ranges = Range.objects.all()
  return render_to_response('search-iprange.html', {'ranges': ranges}, RequestContext(request))

@login_required()
def search_iprange_range(request, range=0):
  ip_list = []
  ips = Ip.objects.all()
  range = Range.objects.get(id=range)
  r = IPRange(IPNetwork(range.cidr).network,IPNetwork(range.cidr).broadcast)
  for ip in r:
    ip_list.append(str(ip))
    for i in ips:
      if IPAddress(i.ip) == ip:
        ip_list.pop()
        break
  return render_to_response('search-iprange-range.html', {'ip_list': ip_list[0:5]})

@login_required()
def sync(request):
  sync_named.write_named()
  rsync_output = sync_named.rsync_named()
  restart_output = sync_named.restart_named()
  return render_to_response('synced.html',{'rsync_output':rsync_output,'restart_output':restart_output})