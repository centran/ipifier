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
  comment = models.CharField(max_length=255, blank=True)

  def __unicode__(self):
    return self.name

class Ip(models.Model):
  ip = models.GenericIPAddressField()
  record_id = models.ForeignKey('Record',null=True,blank=True)
  range_id = models.ForeignKey('Range')
  comment = models.CharField(max_length=255,blank=True)

  def __unicode__(self):
    return self.ip

class Mac(models.Model):
  mac = models.CharField(max_length=17,unique=True)
  ip_id = models.ForeignKey('Ip')

  def __unicode__(self):
    return self.mac

class Domain(models.Model):
  name = models.CharField(max_length=255, unique=True)
  slave = 'slave'
  master = 'master'
  forward = 'forward'
  type_choices = ( (master, 'master'), (slave, 'slave'), (forward, 'forward') )
  type = models.CharField(max_length=7, choices=type_choices, default=master)
  comment = models.CharField(max_length=255, blank=True)

  def __unicode__(self):
    return self.name

class Range(models.Model):
  name = models.CharField(max_length=255, unique=True)
  start = models.GenericIPAddressField()
  end = models.GenericIPAddressField()
  comment = models.CharField(max_length=255, blank=True)

  def __unicode__(self):
    return self.name
