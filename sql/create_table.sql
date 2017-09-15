CREATE TABLE census_observations (
  geo_id text, 
  dim0 smallint,
  dim1 smallint,
  value real
);
CREATE INDEX census_observations_geo ON census_observations (geo_id);
CREATE INDEX census_observations_dim0 ON census_observations (dim0);
