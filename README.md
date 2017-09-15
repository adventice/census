# Usage

## Setup env

    $ virtualenv -p python3 env

## Download & unzip boundaries and observations

    $ python cli.py download
    $ python cli.py unzip

## Transform observations XML to CSV

```bash
    $ python cli.py csv \
      filename=data/2016/aggregate_dissemination_areas/Generic_98-401-X2016030.xml \
      > data/2016/aggregate_dissemination_areas/lada.csv
    $ head -10 data/2016/aggregate_dissemination_areas/lada.csv
    geo_id dim0 dim1 value
    01     1    1    35151728
    01     2    1    33476688
    01     3    1    5.0
    01     4    1    15412443
    01     5    1    14072079
    01     6    1    3.9
    01     7    1    8965588.85
    [...]    
```

Aggregated dissemination areas took around 20mins to transform on a 2.5Ghz CPU.

## Load into postgres

```
    $ psql geo < sql/create_table.sql

    $ psql geo -c "\copy census_observations \
    FROM data/2016/aggregate_dissemination_areas/lada.csv \
    CSV DELIMITER E'\t' HEADER"

    $ psql geo -c "CREATE EXTENSION postgis"

    $ ogr2ogr -f "PostgreSQL" PG:"dbname=geo" \
    -overwrite \
    -nlt MULTIPOLYGONE \
    -nln census_lada \
    -t_srs EPSG:4326 \
    -progress \
    data/2016/aggregate_dissemination_areas/lada000b16a_e.shp
```

## Transform observations from row to column (optional)

Usuful if you want observations grouped per geo_id.

## Dump descriptions (optional)

```bash
    $ python cli.py description \
      filename=data/2016/aggregate_dissemination_areas/Structure_98-401-X2016030.xml
    1    Population, 2016    Population, 2016
    2    Population, 2011    Population, 2011
    3    Population percentage change, 2011 to 2016      Variation en pourcentage de la population, 2011 à 2016
    4    Total private dwellings     Total des logements privés
    [...]
```

# Example


## Dwelling income

```sql
SELECT s.ogc_fid, s.wkb_geometry, o.value as dwelling_income 
FROM census_lada s, census_observations o 
WHERE s.adauid = o.geo_id 
AND o.dim0 = 727
AND o.dim1 = 1;
```

## Get dwelling income by latitude, longitude

# URLs

## Observations (2016)

http://www12.statcan.gc.ca/census-recensement/2016/dp-pd/prof/details/download-telecharger/comp/page_dl-tc.cfm

## Observations (Previous)

http://www12.statcan.gc.ca/census-recensement/pc-eng.cfm

## Observations (All)

http://www12.statcan.gc.ca/datasets/index-eng.cfm

## Boundaries

http://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-eng.cfm
