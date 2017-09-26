CREATE TABLE census_observations (
  level varchar(1),
  geo_id varchar(12), 
  dim smallint,
  value_total real,
  value_male real,
  value_female real
);
CREATE INDEX census_observations_geo_dim ON census_observations (geo_id, dim);
CREATE INDEX census_observations_value_total_dim ON census_observations (value_total, dim);