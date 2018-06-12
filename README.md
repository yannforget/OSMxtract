# OSMxtract

## Description

**OSMxtract** is a simple Python package that uses the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) to fetch [OpenStreetMap](https://www.openstreetmap.org) features and export them in a GeoJSON file.

## Installation

Using `pip`:

```sh
pip install osmxtract
```

## Command-line interface

### Usage

**OSMxtract** can guess the extent of your query based on three different options:

* `--fromfile`: use the bounds from the input vector or raster file ;
* `--latlon` and `--buffer`: use the bounds of a buffer around a given point ;
* `--address` and `--buffer`: use the bounds of a buffer around a geocoded address.

```
Usage: osmxtract [OPTIONS] OUTPUT

  Extract GeoJSON features from OSM with the Overpass API.

Options:
  --fromfile PATH                 Bounding box from input file.
  --latlon FLOAT...               Space-separated lat/lon coordinates.
  --address TEXT                  Address to geocode.
  --buffer INTEGER                Buffer size in meters around lat/lon or
                                  address.
  --tag TEXT                      OSM tag of interest (ex: "highway").
  --values TEXT                   Comma-separated list of possible values (ex:
                                  "tertiary,primary").
  --case-insensitive              Make the first character of each value case
                                  insensitive.
  --geom [point|linestring|polygon|multipolygon]
                                  Output geometry type.
  --help                          Show this message and exit.
```

### Examples

```bash
# buildings around the "Université Libre de Bruxelles" as polygons
# save features in the file `buildings.geojson`. since no values
# are provided, all non-null values are accepted for the tag
# "highway" are accepted.
osmxtract --address "Université Libre de Bruxelles" --buffer 5000 \
          --tag building --geom polygon buildings.geojson

# primary, secondary and tertiary roads based on the extent
# of an existing raster. save the result as linestrings in the
# `major_roads.geojson` file. we use the `--case-insensitive`
# flag to get roads tagged as "primary" as well as "Primary".
osmxtract --fromfile map.tif --tag highway \
          --values "primary,secondary,tertiary" \
          --case-insensitive --geom linestring \
          major_roads.geojson

# cafes and bars near "Atomium, Brussels" 
osmxtract --address "atomium, brussels" --buffer 1000 \
          --tag amenity --values "cafe,bar" --geom point \
          cafes_and_bars.geojson
```

## API



``` python
import json
from osmxtract import overpass, location
import geopandas as gpd

# Get bounding box coordinates from a 2km buffer
# around the Atomium in Brussels
lat, lon = location.geocode('Atomium, Brussels')
bounds = location.from_buffer(lat, lon, buffer_size=2000)

# Build an overpass QL query and get the JSON response
query = overpass.ql_query(bounds, tag='amenity', values=['cafe', 'bar'])
response = overpass.request(query)

# Process response manually...
for elem in response['elements']:
    print(elem['tags'].get('name'))

# Output:
# Au Bon Coin
# Aux 4 Coins du Monde
# Excelsior
# Welcome II
# Heymbos
# Games Café
# Stadium
# Le Beau Rivage
# The Corner
# None
# Expo
# Koning
# Centrum
# St. Amands
# Bij Manu

# ...or parse them as GeoJSON
feature_collection = overpass.as_geojson(response, 'point')

# Write as GeoJSON
with open('cafes_and_bars.geojson', 'w') as f:
    json.dump(feature_collection, f)

# To GeoPandas GeoDataFrame:
geodataframe = gpd.GeoDataFrame.from_features(feature_collection)
```