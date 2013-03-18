from django import forms
from iptracker.models import *
from django.core.validators import validate_ipv46_address, validate_ipv4_address, validate_ipv6_address
from django.core.exceptions import ValidationError
from netaddr import *
import re

class RecordForm(forms.Form):
  def __init__(self, *args, **kwargs):
    super(RecordForm, self).__init__(*args, **kwargs)
    self.fields['domain'].choices = [(choice.id,choice.name) for choice in Domain.objects.all() ]
  name = forms.CharField(max_length=255)
  domain = forms.TypedChoiceField()
  type = forms.TypedChoiceField(choices=Record.type_choices)
  content = forms.CharField()
  ttl = forms.IntegerField()
  pri = forms.IntegerField()
  comment = forms.CharField(required=False )
  mac = forms.CharField(max_length=17,min_length=17,required=False)
  def clean(self):
    cleaned_data = super(RecordForm, self).clean()
    name = cleaned_data.get('name')
    domain = Domain.objects.get(id=cleaned_data.get('domain'))
    type = cleaned_data.get('type')
    content = cleaned_data.get('content')
    mac = cleaned_data.get('mac')
    #fix a bug where validate_ipv6_address cannot process NoneType
    #So instead of passing None we pass 1 witch is invalid as well
    if content == None:
      content = '1'
    records = Record.objects.all()
    for record in records:
      if name == record.name and domain == record.domain_id:
        self.errors['name'] = self.error_class(['Domain name already exists'])
        del cleaned_data['name']
    ip_valid = True
    if type == 'A':
      try: 
        validate_ipv4_address(content)
      except ValidationError:
        self.errors['content'] = self.error_class(['Not an IPv4 address'])
        ip_valid = False
      except AddrFormatError:
        self.errors['content'] = self.error_class(['Not an IPv4 address'])
        ip_valid = False
    if type == 'AAAA' and ip_valid:
      try: 
        validate_ipv6_address(content)
      except ValidationError:
        self.errors['content'] = self.error_class(['Not an IPv6 address'])
        ip_valid = False
    ranges = Range.objects.all()
    found = False
    if ip_valid:
      for range in ranges:
        r = IPRange(range.start, range.end)
        addrs = list(r)
        if IPAddress(content) in addrs:
          found = True
          break
    if not found and ip_valid:
      self.errors['content'] = self.error_class(['IP is not within a known range'])
      ip_valid = False
    if not re.match("[0-9a-f]{2}([.-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()): 
      self.errors['mac'] = self.error_class(['Not a MAC address'])
      del cleaned_data['mac']
    m = re.sub("[.:-]", "", mac)
    m = m.lower()
    mac = "%s-%s-%s-%s-%s-%s" % (m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:])
    cleaned_data['mac'] = mac
    ips = Ip.objects.all()
    for ip in ips:
      if content == ip.ip and ip_valid:
        self.errors['content'] = self.error_class(['IP already exists'])
        ip_valid = False
      if mac == ip.mac:
        self.errors['mac'] = self.error_class(['MAC already exists'])  
    return cleaned_data

class EditRecordForm(forms.Form):
  def __init__(self, *args, **kwargs):
    super(EditRecordForm, self).__init__(*args, **kwargs)
    self.fields['domain'].choices = [(choice.id,choice.name) for choice in Domain.objects.all() ]
  name = forms.CharField(max_length=255)
  domain = forms.TypedChoiceField()
  type = forms.TypedChoiceField(choices=Record.type_choices)
  content = forms.CharField()
  ttl = forms.IntegerField()
  pri = forms.IntegerField()
  comment = forms.CharField(required=False )
  mac = forms.CharField(max_length=17,min_length=17,required=False)
  def clean(self):
    cleaned_data = super(EditRecordForm, self).clean()
    name = cleaned_data.get('name')
    domain = Domain.objects.get(id=cleaned_data.get('domain'))
    type = cleaned_data.get('type')
    content = cleaned_data.get('content')
    mac = cleaned_data.get('mac')
    #fix a bug where validate_ipv6_address cannot process NoneType
    #So instead of passing None we pass 1 witch is invalid as well
    if content == None:
      content = '1'
    ip_valid = True
    if type == 'A':
      try: 
        validate_ipv4_address(content)
      except ValidationError:
        self.errors['content'] = self.error_class(['Not an IPv4 address'])
        ip_valid = False
      except AddrFormatError:
        self.errors['content'] = self.error_class(['Not an IPv4 address'])
        ip_valid = False
    if type == 'AAAA' and ip_valid:
      try: 
        validate_ipv6_address(content)
      except ValidationError:
        self.errors['content'] = self.error_class(['Not an IPv6 address'])
        ip_valid = False
    ranges = Range.objects.all()
    found = False
    if ip_valid:
      for range in ranges:
        r = IPRange(range.start, range.end)
        addrs = list(r)
        if IPAddress(content) in addrs:
          found = True
          break
    if not re.match("[0-9a-f]{2}([\.\-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
      self.errors['mac'] = self.error_class(['Not a MAC address'])
      del cleaned_data['mac']
    m = re.sub("[.:-]", "", mac)
    m = m.lower()
    mac = "%s-%s-%s-%s-%s-%s" % (m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:])
    cleaned_data['mac'] = mac
    if not found and ip_valid:
      self.errors['content'] = self.error_class(['IP is not within a known range'])
      ip_valid = False
    return cleaned_data

class DomainForm(forms.Form):
  name = forms.CharField(max_length=255)
  type = forms.TypedChoiceField(choices=Domain.type_choices)
  comment = forms.CharField(required=False)

class RangeForm(forms.Form):
  name = forms.CharField(max_length=255)
  start = forms.CharField()
  end = forms.CharField()
  comment = forms.CharField(required=False)

class IpForm(forms.Form):
  ip = forms.CharField()
  mac = forms.CharField(max_length=17,min_length=17,required=False)
  comment = forms.CharField()
  def clean(self):
    cleaned_data = super(IpForm, self).clean()
    ip = cleaned_data.get('ip')
    mac = cleaned_data.get('mac')
    ips = Ip.objects.all()
    #fix a bug where validate_ipv6_address cannot process NoneType
    #So instead of passing None we pass 1 witch is invalid as well
    if ip == None:
      ip = '1'
    ip_valid = True
    try:
      validate_ipv46_address(ip)
    except ValidationError:
      self.errors['ip'] = self.error_class(['Not an IP address'])
      del cleaned_data['ip']
      ip_valid = False
    except AddrFormatError:
      self.errors['ip'] = self.error_class(['Not an IP address'])
      del cleaned_data['ip']
      ip_valid = False
    ranges = Range.objects.all()
    found = False
    if ip_valid:
      for range in ranges:
        r = IPRange(range.start, range.end)
        addrs = list(r)
        if IPAddress(ip) in addrs:
          found = True
          break
    if not found and ip_valid:
      self.errors['ip'] = self.error_class(['IP is not within a known range'])
      del cleaned_data['ip']
      ip_valid = False
    if not re.match("[0-9a-f]{2}([\.\-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
      self.errors['mac'] = self.error_class(['Not a MAC address'])
      del cleaned_data['mac']
    m = re.sub("[.:-]", "", mac)
    m = m.lower()
    mac = "%s-%s-%s-%s-%s-%s" % (m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:])
    cleaned_data['mac'] = mac
    for i in ips:
      if i.ip == ip and ip_valid:
        self.errors['ip'] = self.error_class(['IP already exists'])
        del cleaned_data['ip']
        ip_valid = False
      if mac == i.mac:
        self.errors['mac'] = self.error_class(['MAC already exists'])
        del cleaned_data['mac']  
    return cleaned_data
