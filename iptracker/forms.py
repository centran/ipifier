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
    if type == 'A' or type == 'AAAA':    
      ip_valid = True
    else:
      ip_valid = False
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
        if IPAddress(content) >= IPNetwork(range.cidr).network and IPAddress(content) <= IPNetwork(range.cidr).broadcast:
          found = True
          break
    if not found and ip_valid:
      self.errors['content'] = self.error_class(['IP is not within a known range'])
      ip_valid = False
    if mac:
      if not re.match("[0-9a-f]{2}([.-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()): 
        self.errors['mac'] = self.error_class(['Not a MAC address'])
        del cleaned_data['mac']
      m = re.sub("[.:-]", "", mac)
      m = m.lower()
      mac = "%s-%s-%s-%s-%s-%s" % (m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:])
      cleaned_data['mac'] = mac
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
    if type == 'A' or type == 'AAAA':
      ip_valid = True
    else:
      ip_valid = False
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
        if IPAddress(content) >= IPNetwork(range.cidr).network and IPAddress(content) <= IPNetwork(range.cidr).broadcast:
          found = True
          break
    if mac:
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
  cidr = forms.CharField()
  comment = forms.CharField(required=False)
  def clean(self):
    cleaned_data = super(RangeForm, self).clean()
    name = cleaned_data.get('name')
    cidr = cleaned_data.get('cidr')
    names = Range.objects.all()
    for n in names:
      if n.name.lower() == name.lower():
        self.errors['name'] = self.error_class(['Range name already exists'])
        del cleaned_data['name']
      if n.cidr == cidr:
        self.errors['cidr'] = self.error_class(['CIDR already exists'])
        del cleaned_data['cidr']
    if cidr == None:
      cidr = '1'
    try:
      network = IPNetwork(cidr)
    except AddrFormatError:
      self.errors['cidr'] = self.error_class(['Not a valid cidr notation'])
      del cleaned_data['cidr']
    return cleaned_data

class EditRangeForm(forms.Form):
  name = forms.CharField(max_length=255)
  cidr = forms.CharField(widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'}))
  comment = forms.CharField(required=False)
  def clean(self):
    cleaned_data = super(EditRangeForm, self).clean()
    return cleaned_data

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
    if len(ip)>3 and (ip[-2] == '/' or ip[-3] == '/' or ip[-4] == '/'):
      try:
        network = IPNetwork(ip)
      except AddrFormatError:
        self.errors['ip'] = self.error_class(['Not a valid cidr notation'])
        ip_valid = False
        del cleaned_data['ip']
    else:
      try:
        validate_ipv46_address(ip)
      except ValidationError:
        self.errors['ip'] = self.error_class(['Not an IP address'])
        ip_valid = False
      except AddrFormatError:
        self.errors['ip'] = self.error_class(['Not an IP address'])
        ip_valid = False
    ranges = Range.objects.all()
    found = False
    if ip_valid:
      for range in ranges:
        r = IPNetwork(range.cidr)
        addrs = list(r)
        if len(ip)>3 and (ip[-2] == '/' or ip[-3] == '/' or ip[-4] == '/'):
          for i in IPNetwork(ip):
            if i in addrs:
              found = True
              break
        else:
          if IPAddress(ip) >= IPNetwork(range.cidr).network and IPAddress(ip) <= IPNetwork(range.cidr).broadcast:
            found = True
          break
    if not found and ip_valid:
      self.errors['ip'] = self.error_class(['IP is not within a known range'])
      del cleaned_data['ip']
      ip_valid = False
    if mac:
      if not re.match("[0-9a-f]{2}([\.\-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
        self.errors['mac'] = self.error_class(['Not a MAC address'])
        del cleaned_data['mac']
      m = re.sub("[.:-]", "", mac)
      m = m.lower()
      mac = "%s-%s-%s-%s-%s-%s" % (m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:])
      cleaned_data['mac'] = mac
    if len(ip) > 3 and (ip[-2] == '/' or ip[-3] == '/'):
      for i in ips:
        for j in list(IPNetwork(ip)):
          if IPAddress(i.ip) == j and ip_valid:
            self.errors['ip'] = self.error_class(['IP already exists'])
            del cleaned_data['ip']
            ip_valid = False
        if mac == i.mac and mac:
          self.errors['mac'] = self.error_class(['MAC already exists'])
          del cleaned_data['mac']  
    else:
      for i in ips:
        if i.ip == ip and ip_valid:
          self.errors['ip'] = self.error_class(['IP already exists'])
          del cleaned_data['ip']
          ip_valid = False
        if mac == i.mac and mac:
          self.errors['mac'] = self.error_class(['MAC already exists'])
          del cleaned_data['mac']  
    return cleaned_data

class EditIpForm(forms.Form):
  ip = forms.CharField()
  mac = forms.CharField(max_length=17,min_length=17,required=False)
  comment = forms.CharField()
  def clean(self):
    cleaned_data = super(EditIpForm, self).clean()
    ip = cleaned_data.get('ip')
    mac = cleaned_data.get('mac')
    ips = Ip.objects.all()
    #fix a bug where validate_ipv6_address cannot process NoneType
    #So instead of passing None we pass 1 witch is invalid as well
    if ip == None:
      ip = '1'
    if mac == None:
      mac = 'a'
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
        r = IPNetwork(range.cidr)
        addrs = list(r)
        if IPAddress(ip) in addrs:
          found = True
          break
    if not found and ip_valid:
      self.errors['ip'] = self.error_class(['IP is not within a known range'])
      del cleaned_data['ip']
      ip_valid = False
    if mac:
      if not re.match("[0-9a-f]{2}([\.\-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
        self.errors['mac'] = self.error_class(['Not a MAC address'])
      m = re.sub("[.:-]", "", mac)
      m = m.lower()
      mac = "%s-%s-%s-%s-%s-%s" % (m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:])
      cleaned_data['mac'] = mac
    return cleaned_data

class SearchForm(forms.Form):
  term = forms.CharField()

class IpSearchForm(forms.Form):
  term = forms.CharField()
  def clean(self):
    cleaned_data = super(IpSearchForm, self).clean()
    term = cleaned_data.get('term')
    ip_valid = True
    if term == None:
      term = '1'
    try:
      validate_ipv46_address(term)
    except ValidationError:
      self.errors['term'] = self.error_class(['Not an IP address'])
      del cleaned_data['term']
      ip_valid = False
    except AddrFormatError:
      self.errors['term'] = self.error_class(['Not an IP address'])
      del cleaned_data['term']
      ip_valid = False
    ranges = Range.objects.all()
    found = False
    if ip_valid:
      for range in ranges:
        r = IPNetwork(range.cidr)
        addrs = list(r)
        if IPAddress(term) in addrs:
          found = True
          break
    if not found and ip_valid:
      self.errors['term'] = self.error_class(['IP is not within a known range'])
      del cleaned_data['term']
      ip_valid = False
    return cleaned_data
