import os
import datetime
import iscpy
from iptracker.models import *
from django.db.models import Q
import subprocess
import paramiko

def write_named():
  named = {}
  f = open('/tmp/named.ipifier.conf', 'w')
  domains = Domain.objects.all()
  for domain in domains:
    named['zone "'+domain.name+'" IN'] = {
      'type': domain.type,
      'file': '"named.'+domain.name+'"',
      'allow-update': { 'none': '' }
    }

  ipprefix = get_prefix()
  for prefix in ipprefix:
    named['zone "0.0.0.'+prefix+'" IN'] = {
      'type': 'master',
      'file': '"named.0.0.0.'+prefix+'"',
      'allow-update': { 'none': '' }
    }
  f.write(iscpy.MakeISC(named))
  f.close()
  if not os.path.exists('/tmp/pri'):
    os.makedirs('/tmp/pri')

  for prefix in ipprefix:
    try:
      f = open('/tmp/pri/named.0.0.0.'+prefix, 'r')
      i = 1
      n = '00'
      lines = f.readlines()
      for line in lines:
        if i == 3:
          n = line[-2:]
          break
        i = i + 1
      num = int(n)
      num = num+1
      if num < 10:
        n = '0' + str(num)
      else:
        n = str(num)
      if num == 100:
        n = '00'
    except IOError:
      n = '00'
    f = open('/tmp/pri/named.0.0.0.'+prefix, 'w')
    f.write('')
    f.close
    f = open('/tmp/pri/named.0.0.0.'+prefix, 'a')
    f.write('$TTL 1D\n@\tIN\tSOA\tbigwells.net root.bigwells.net. (\n')
    now = datetime.datetime.now()
    f.write('\t\t\t'+str(now.year)+str(now.month)+str(now.day)+n+'\n')
    f.write('\t\t\t8H\n\t\t\t2H\n\t\t\t4W\n\t\t\t1D )\n')
    f.write('\t\tNS\tns1.he.net.\n')
    f.write('\t\tNS\tns2.he.net.\n')
    records = Record.objects.all().filter( type='A' ).filter( content__startswith=prefix )
    for record in records:
      r = record.content.split('.')
      f.write(r[3]+'.'+r[2]+'.'+r[1]+'.'+r[0]+'.in-addr.arpa.\t\tPTR\t'+record.name)
      domainname = Domain.objects.get(id=record.domain_id.id)
      f.write('.'+domainname.name+'.\n')
  for domain in domains:
    try:
      f = open('/tmp/pri/named.'+domain.name, 'r')
      i = 1
      n = '00'
      lines = f.readlines()
      for line in lines:
        if i == 3:
          n = line[-2:]
          break
        i = i + 1
      num = int(n)
      num = num+1
      if num < 10:
        n = '0' + str(num)
      else:
        n = str(num)
      if num == 100:
        n = '00'
    except IOError:
      n = '00'
    f = open('/tmp/pri/named.'+domain.name, 'w')
    f.write('')
    f.close()
    f = open('/tmp/pri/named.'+domain.name, 'a')
    f.write('$TTL 1D\n@\tIN\tSOA\t'+domain.name+'. root.'+domain.name+'. (\n')
    now = datetime.datetime.now()
    f.write('\t\t\t'+str(now.year)+str(now.month)+str(now.day)+n+'\n')
    f.write('\t\t\t8H\n\t\t\t2H\n\t\t\t4W\n\t\t\t1D )\n')
    nameservers = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='NS') )
    for ns in nameservers:
      f.write('\t\tNS\t'+ns.content+'.\n')
    mailexchanges = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='MX') )
    for mx in mailexchanges:
      f.write('\t\tMX\t'+str(mx.pri)+' '+mx.content+'.\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='A') )
    for record in records:
      f.write(record.name)
      if record.name[-3:] == 'com' or record.name[-3:] == 'org' or record.name[-3:] == 'net':
        f.write('.')
      f.write('\tA\t'+record.content+'\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='AAAA') )
    for record in records:
      f.write(record.name)
      if record.name[-3:] == 'com' or record.name[-3:] == 'org' or record.name[-3:] == 'net':
        f.write('.')
      f.write('\tAAAA\t'+record.content+'\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='SRV') )
    for record in records:
      f.write(record.name+'\tSRV'+'\t0 '+record.content)
      if not record.content[-1] == '.':
        f.write('.')
      f.write('\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='TXT') )
    for record in records:
      f.write(record.name+'\tIN TXT\t'+'"'+record.content+'"\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='CNAME') )
    for record in records:
      f.write(record.name+'\tCNAME\t'+''+record.content)
      if record.content[-3:] == 'com' or record.content[-3:] == 'org' or record.content[-3:] == 'net':
        f.write('.')
      f.write('\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='HINFO') )
    for record in records:
      f.write(record.name+'\tIN HINFO\t'+'"'+record.content+'"\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='NAPTR') )
    for record in records:
      f.write(record.name+'\tIN NAPTR\t'+'"'+record.content+'"\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='PTR') )
    for record in records:
      f.write(record.name+'\tIN PTR\t'+'"'+record.content+'"\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='SPF') )
    for record in records:
      f.write(record.name)
      if record.name[-3:] == 'com' or record.name[-3:] == 'org' or record.name[-3:] == 'net':
        f.write('.')
      f.write('\tIN SPF\t'+record.content+'\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='SSHFP') )
    for record in records:
      f.write(record.name+'\tIN SSHFP\t'+'"'+record.content+'"\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='URL') )
    for record in records:
      f.write(record.name+'\tURL\t'+'"'+record.content+'"\n')
    records = Record.objects.all().filter( Q(domain_id=domain.id) & Q(type='MBOXFW') )
    for record in records:
      f.write(record.name+'\tMBOXFW\t'+'"'+record.content+'"\n')
    f.close()
    
def rsync_named():
  outputs = []
  p = subprocess.Popen('rsync -avH /tmp/named.ipifier.conf root@dnstest.ch1:/etc/',
    stdout=subprocess.PIPE,shell=True
  )
  output, err = p.communicate()
  outputs.append(output)
  p = subprocess.Popen('rsync -avH /tmp/pri/* root@dnstest.ch1:/var/named/',
    stdout=subprocess.PIPE, shell=True
  )
  output, err = p.communicate()
  outputs.append(output)
  return outputs

def restart_named():
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  ssh.connect('10.26.96.116', username='root', password='shin3y3zen')
  stdin, stdout, stderr = ssh.exec_command('service named restart')
  return stdout.readlines()

def get_prefix():
  records = Record.objects.all().filter( Q(type='A') )
  prefixs = []
  for record in records:
    ip = record.content
    ipsplit = ip.split('.')
    prefix = ipsplit[0]
    if not prefix in prefixs:
      prefixs.append(prefix)
  return prefixs