import os
from sys import argv
from lxml import etree
from subprocess import call

BOUNDARIES = {
  'aggregate_dissemination_areas': 'lada000b16a_e.zip',
  'forward_sortation_areas': 'lfsa000b16a_e.zip',
  'tracts': 'lct_000b16a_e.zip',
  'dissemination_areas': 'lda_000b16a_e.zip'
}

OBSERVATIONS = {
  'forward_sortation_areas': '026',
  'aggregate_dissemination_areas': '030',
  'tracts': '023',
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

  observations_url = 'http://www12.statcan.gc.ca/census-recensement/2016/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&TYPE=XML&GEONO={geo_no}'
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
    call(['7za', 'x', zipfile, '-y', '-o%s' % dest])

def iter_observation(filename):
  dom = etree.iterparse(filename, events=('start', 'end'))
  z = 0
  for action, elem in dom:
    tag = elem.tag.split('}')[1]
    if action == 'start' and tag == 'Series':
      if elem.find('./{*}Obs/{*}ObsValue') is None:  
        continue
      dough = {
        'geo_id': elem.find('./{*}SeriesKey/{*}Value[@concept="GEO"]').get('value'),
        'dim0': elem.find('./{*}SeriesKey/{*}Value[@concept="DIM0"]').get('value'),
        'dim1': elem.find('./{*}SeriesKey/{*}Value[@concept="DIM1"]').get('value'),
        'value': elem.find('./{*}Obs/{*}ObsValue').get('value'),
      }
      yield dough
    elem.clear()

def to_csv(filename):
  print ('\t'.join(['geo_id', 'dim0', 'dim1', 'value']))
  for dough in iter_observation(filename):
      print ('\t'.join(dough.values()))

def dump_descriptions(filename):
  dom = etree.iterparse(filename, events=('start', 'end'))
  for action, elem in dom:
    if '}' not in elem.tag:
      continue
    tag = elem.tag.split('}')[1]       
    if action == 'start' and tag == 'Code':
      if elem.find('./{*}Description') is None:
        continue
      if len(elem.findall('.//{*}Description')) != 2:
        continue
      desc_en, desc_fr = elem.findall('.//{*}Description')
      print (elem.get('value'), '\t',desc_en.text,'\t', desc_fr.text)
    elem.clear()

def to_grouped(filename):
  geos = {}
  p = 0 
  fields = ['geo_id']
  first = True
  for line in open(filename).readlines():
    if first:
      first = False
      continue
    geo_id, dim0, dim1, value = line[:-1].split('\t')
    key = 'dim_%s_%s' % (dim0, dim1)
    if key not in fields: 
      fields.append(key)
    geo = geos.get(geo_id, dict(geo_id=geo_id))
    geo[key] = value
    geos[geo_id] = geo

  header = None
  for geo_id, obs in geos.items():
      if not header:
        print ('\t'.join(fields))
        header = True
      
      row = [obs[k] if k in obs else '' for k in fields]
      print ('\t'.join(row))

if __name__=='__main__':
  argv.pop(0)
  cmd = argv.pop(0)
  config = dict([item.split('=') for item in argv])

  if cmd == 'download':
    download()
  elif cmd == 'unzip':
    unzip()
  elif cmd == 'csv':
    to_csv(**config)
  elif cmd == 'grouped':
    to_grouped(**config)
  elif cmd == 'descriptions':
    dump_descriptions(**config)
  else:
    raise Exception('command not found')
