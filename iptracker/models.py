from django.db import models

class Record(models.Model):
  name = models.CharField(max_length=255)
  domain_id = models.ForeignKey('Domain')
  A = 'A'
  AAAA = 'AAAA'
  CNAME = 'CNAME'
  HINFO = 'HINFO'
  MX = 'MX'
  NAPTR = 'NAPTR'
  NS = 'NS'
  PTR = 'PTR'
  SOA = 'SOA'
  SPF = 'SPF'
  SRV = 'SRV'
  SSHFP = 'SSHFP'
  TXT = 'TXT'
  URL = 'URL'
  MBOXFW = 'MBOXFW'
  type_choices = (
    (A, 'A'),
    (AAAA, 'AAAA'),
    (CNAME, 'CNAME'),
    (HINFO, 'HINFO'),
    (MX, 'MX'),
    (NAPTR, 'NAPTR'),
    (NS, 'NS'),
    (PTR, 'PTR'),
    (SOA, 'SOA'),
    (SPF, 'SPF'),
    (SRV, 'SRV'),
    (SSHFP, 'SSHFP'),
    (TXT, 'TXT'),
    (URL, 'URL'),
    (MBOXFW, 'MBOXFW'),
  )
  type = models.CharField(max_length=6, choices=type_choices, default=A)
  content = models.CharField(max_length=64000)
  ttl = models.IntegerField()
  pri = models.IntegerField()
  changedate = models.IntegerField()

  def __unicode__(self):
    return self.name

class Ip(models.Model):
  ip = models.GenericIPAddressField()
  record_id = models.ForeignKey('Record')

  def __unicode__(self):
    return self.ip

class Mac(models.Model):
  mac = models.CharField(max_length=17)
  record_id = models.ForeignKey('Record')

  def __unicode__(self):
    return self.mac

class Domain(models.Model):
  name = models.CharField(max_length=250)
  master = models.CharField(max_length=128)
  last_check = models.IntegerField(blank=True, null=True)
  native = 'native'
  master = 'master'
  type_choices = ( (native, 'native'), (master, 'master') )
  type = models.CharField(max_length=6, choices=type_choices, default=native)
  notified_serial = models.IntegerField(blank=True, null=True)

  def __unicode__(self):
    return self.name
