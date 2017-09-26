# Usage

## Requirements

- unzip v6.0.
- PostgreSQL / PostGIS
- Python3

## Setup env

    $ virtualenv -p python3 env

## Download & unzip boundaries and observations

    $ python cli.py download
    $ python cli.py unzip

## Prepare observations

```bash
    $ python cli.py prepare \
      filename=data/2016/dissemination_areas/98-401-X2016024_English_TAB_data.csv \
      > data/2016/dissemination_areas/census_observations.csv   
```

Dissemination areas took around 5mins to prepare on a 2.5Ghz CPU.

## Load into postgres

```
    $ psql geo < sql/create_table.sql

    $ psql geo -c "\copy census_observations \
    FROM data/2016/dissemination_areas/census_observations.csv \
    CSV DELIMITER E'\t' NULL as 'null'"

    $ psql geo -c "CREATE EXTENSION postgis"

    $ ogr2ogr -f "PostgreSQL" PG:"dbname=geo" \
    -overwrite \
    -nlt MULTIPOLYGON \
    -nln census_lda \
    -t_srs EPSG:4326 \
    -progress \
    data/2016/dissemination_areas/lda_000b16a_e.shp
```

# Example

## Top individual income by DA

```sql
SELECT o.geo_id, o.value_total, g.prname FROM census_observations o, census_lda g 
  WHERE g.dauid = o.geo_id 
  AND dim=727 
  AND value_total is not null 
  ORDER BY value_total 
  DESC LIMIT 10;
 ```

Result:

```
    geo_id  | value_total | prname  
  ----------+-------------+---------
   35202898 |      598016 | Ontario
   48060591 |      519168 | Alberta
   35204279 |      490496 | Ontario
   48060566 |      474112 | Alberta
   35202777 |      468992 | Ontario
   35204262 |      431104 | Ontario
   35202897 |      431104 | Ontario
   35202351 |      423936 | Ontario
   35240203 |      422912 | Ontario
   35202349 |      410624 | Ontario  
```

## Get individual income by lat lon

```sql
SELECT o.value_total FROM census_observations o, census_lda g
    WHERE ST_Intersects(wkb_geometry, ST_PointFromText('Point(-79.4105825 43.6960938)', 4326))
    AND o.geo_id = g.dauid AND o.dim = 727;
```

Result:

```
 value_total 
-------------
      598016
```

# URLs

## Observations (2016)

http://www12.statcan.gc.ca/census-recensement/2016/dp-pd/prof/details/download-telecharger/comp/page_dl-tc.cfm

## Observations (Previous)

http://www12.statcan.gc.ca/census-recensement/pc-eng.cfm

## Observations (All)

http://www12.statcan.gc.ca/datasets/index-eng.cfm

## Boundaries

http://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-eng.cfm

# Census Observations Fields

     index description
     0     "CENSUS_YEAR"
     1     "GEO_CODE (POR)"
     2     "GEO_LEVEL"
     3     "GEO_NAME"
     4     "GNR"
     5     "DATA_QUALITY_FLAG"
     6     "CSD_TYPE_NAME"
     7     "ALT_GEO_CODE"
     8     "DIM: Profile of Dissemination Areas (832)"
     9     "Member ID: Profile of Dissemination Areas (832)"
     10    "Notes: Profile of Dissemination Areas (832)" 
     11    "Dim: Sex (3): Member ID: [1]: Total - Sex"
     12    "Dim: Sex (3): Member ID: [2]: Male"
     13    "Dim: Sex (3): Member ID: [3]: Female"
