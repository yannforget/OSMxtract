"""Command-line interface."""

import json

import click

from .overpass import ql_query, request, as_geojson
from .location import geocode, from_buffer, from_file


@click.command()
@click.option(
    '--fromfile', type=click.Path(), default=None,
    help='Bounding box from input file.')
@click.option(
    '--latlon', nargs=2, type=click.FLOAT, default=None,
    help='Space-separated lat/lon coordinates.')
@click.option(
    '--address', type=click.STRING, default=None,
    help='Address to geocode.')
@click.option(
    '--buffer', type=click.INT, default=None,
    help='Buffer size in meters around lat/lon or address.')
@click.option(
    '--tag', type=click.STRING, default=None,
    help='OSM tag of interest (ex: "highway").')
@click.option(
    '--values', type=click.STRING, default=None,
    help='Comma-separated list of possible values (ex: "tertiary,primary").')
@click.option(
    '--case-insensitive', is_flag=True, default=False,
    help='Make the first character of each value case insensitive.')
@click.option(
    '--geom', help='Output geometry type.',
    type=click.Choice(['point', 'linestring', 'polygon', 'multipolygon']))
@click.argument('output', type=click.Path())
def cli(fromfile, latlon, address, buffer, tag,
        values, case_insensitive, geom, output):
    """Extract GeoJSON features from OSM with the Overpass API."""
    if fromfile:
        bounds = from_file(fromfile)
    elif latlon:
        bounds = from_buffer(*latlon, buffer)
    elif address:
        lat, lon = geocode(address)
        bounds = from_buffer(lat, lon, buffer)
    else:
        raise click.BadOptionUsage('A location must be provided.')

    if values:
        values = values.split(',')
    query = ql_query(bounds, tag, values, case_insensitive)
    response = request(query)

    if not geom:
        raise click.BadOptionUsage('An output geometry type must be provided.')
    feature_collection = as_geojson(response, geom)

    with open(output, 'w') as f:
        json.dump(feature_collection, f)
