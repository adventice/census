import os
from sys import argv
from lxml import etree
from subprocess import call

BOUNDARIES = {
  'forward_sortation_areas': 'lfsa000b16a_e.zip',
  'dissemination_areas': 'lda_000b16a_e.zip'
}

OBSERVATIONS = {
  'dissemination_areas': '024',
}

data = os.path.join('data', '2016')
archives = os.path.join(data, 'archives')

def download():
  if not os.path.exists(archives):
    os.makedirs(archives)

  geo_url = 'http://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/files-fichiers/2016/'
  for filename in BOUNDARIES.values():
    url = os.path.join(geo_url, filename)
    call(['wget', '--directory-prefix', archives, '--no-clobber', url])

  observations_url = 'http://www12.statcan.gc.ca/census-recensement/2016/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&TYPE=TAB&GEONO={geo_no}'
  for name, geo_no in OBSERVATIONS.items():
    url = observations_url.format(geo_no=geo_no)
    filename = os.path.join(archives, '%s.zip' % name)
    call(['wget', '--no-clobber', url, '-O', filename])

def unzip():
  for name, filename in BOUNDARIES.items():
    zipfile = os.path.join(archives, filename)
    dest = os.path.join(data, name)
    call(['unzip', '-n', zipfile, '-d', dest])

  for name in OBSERVATIONS.keys():
    zipfile = os.path.join(archives, '%s.zip' % name )
    dest = os.path.join(data, name)
    call(['unzip', '-n', zipfile, '-d', dest])

def prepare(filename):
  first = True
  for row in open(filename):
    if first:
      first = False
      continue
    row = row.strip('\r\n')
    # see "Census Observations Fields" in README.md
    indexes = [2,1,9,11,12,13]
    fields = row.split('\t')
    fields = [fields[i] if fields[i] not in ['x', '..', '...','F'] else 'null' for i in indexes]
    result = [field.strip('"') for field in fields]
    print ('\t'.join(result))

if __name__=='__main__':
  argv.pop(0)
  cmd = argv.pop(0)
  config = dict([item.split('=') for item in argv])

  if cmd == 'download':
    download()
  elif cmd == 'unzip':
    unzip()
  elif cmd == 'prepare':
    prepare(**config)
  elif cmd == 'descriptions':
    dump_descriptions(**config)
  else:
    raise Exception('command not found')

