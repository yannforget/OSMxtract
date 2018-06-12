"""Build & send overpass QL queries and parse the response
as GeoJSON.
"""

import requests
import geojson

from .errors import (
    OverpassBadRequest,
    OverpassMoved,
    OverpassTooManyRequests,
    OverpassGatewayTimeout
)


def _make_case_insensitive(value):
    """Replace the first character of a string by an uppercase-lowercase
    regex.

    Parameters
    ----------
    value : str
        Value (ex: "Residential").

    Returns
    -------
    value : str
        Output value (ex: "[rR]esidential").
    """
    return f'[{ value[0].lower() }{ value[0].upper() }]{ value[1:] }'


def _bbox(lat_min, lon_min, lat_max, lon_max):
    """Format bounding box as a string as expected by the Overpass API."""
    return f'({lat_min},{lon_min},{lat_max},{lon_max})'


def ql_query(bounds, tag, values=None, case_insensitive=False, timeout=25):
    """Build an Overpass QL query.

    Parameters
    ----------
    bounds : tuple
        Bounding box (lat_min, lon_min, lat_max, lon_max).
    tag : str
        OSM tag to query (ex: "highway").
    values : list of str
        List of possible values for the provided OSM tag.
    case_insensitive : bool, optional
        Make the first character of each value case insensitive.
        Defaults to `False`.
    timeout : int, optional
        Overpass timeout. Defaults to 25.

    Returns
    -------
    query : str
        Formatted Overpass QL query.
    """
    bbox = _bbox(*bounds)
    if values:
        if case_insensitive:
            values = [_make_case_insensitive(v) for v in values]
        if len(values) > 1 or case_insensitive:
            query = f'["{ tag }"~"{ "|".join(values) }"]'
        else:
            query = f'["{ tag }"="{ values[0] }"]'
    else:
        query = f'["{ tag }"]'
    return f'[out:json][timeout:{ timeout }]; nwr{ query }{ bbox }; out geom qt;'


def request(query, endpoint='http://overpass-api.de/api/interpreter'):
    """Send a request to the Overpass API.

    Parameters
    ----------
    query : str
        Overpass QL query.
    endpoint : str, optional
        API endpoint, defaults to `http://overpass-api.de/api/interpreter`.

    Returns
    -------
    response : dict
        JSON response as a dictionnary.
    """
    response = requests.get(endpoint, params={'data': query})
    if response.status_code == 302:
        raise OverpassMoved
    elif response.status_code == 400:
        raise OverpassBadRequest
    elif response.status_code == 429:
        raise OverpassTooManyRequests
    elif response.status_code == 504:
        raise OverpassGatewayTimeout
    return response.json()


def _as_points(elements):
    """Parse an iterable of elements to retrieve a FeatureCollection of points.

    Parameters
    ----------
    elements : list of dict
        JSON response elements.

    Returns
    -------
    feature_collection : dict
        Output GeoJSON FeatureCollection.
    """
    features = []
    elements = [e for e in elements if e.get('type') == 'node']
    for elem in elements:
        coords = [elem['lon'], elem['lat']]
        geom = geojson.Point(coordinates=coords)
        features.append(geojson.Feature(elem['id'], geom, elem['tags']))
    return geojson.FeatureCollection(features)


def _as_linestrings(elements):
    """Parse an iterable of elements to retrieve a FeatureCollection of linestrings.

    Parameters
    ----------
    elements : list of dict
        JSON response elements.

    Returns
    -------
    feature_collection : dict
        Output GeoJSON FeatureCollection.
    """
    features = []
    elements = [e for e in elements if e.get('type') == 'way']
    for elem in elements:
        coords = [[node['lon'], node['lat']] for node in elem['geometry']]
        geom = geojson.LineString(coordinates=coords)
        features.append(geojson.Feature(elem['id'], geom, elem['tags']))
    return geojson.FeatureCollection(features)


def _as_polygons(elements):
    """Parse an iterable of elements to retrieve a FeatureCollection of polygons.

    Parameters
    ----------
    elements : list of dict
        JSON response elements.

    Returns
    -------
    feature_collection : dict
        Output GeoJSON FeatureCollection.    
    """
    features = []
    elements = [e for e in elements if e.get('type') == 'way']
    for elem in elements:
        coords = [[node['lon'], node['lat']] for node in elem['geometry']]
        geom = geojson.Polygon(coordinates=[coords])
        features.append(geojson.Feature(elem['id'], geom, elem['tags']))
    return geojson.FeatureCollection(features)


def _as_multipolygons(elements):
    """Parse an iterable of elements to retrieve a FeatureCollection of multipolygons.

    Parameters
    ----------
    elements : list of dict
        JSON response elements.

    Returns
    -------
    feature_collection : dict
        Output GeoJSON FeatureCollection.
    """
    features = []
    elements = [e for e in elements if
                e.get('type') == 'relation' and
                e['tags']['type'] == 'multipolygon']
    for elem in elements:
        coords = []
        for member in elem['members']:
            member_coords = []
            for node in member['geometry']:
                member_coords.append([node['lon'], node['lat']])
            coords.append(member_coords)
        geom = geojson.MultiPolygon(coordinates=[coords])
        features.append(geojson.Feature(elem['id'], geom, elem['tags']))
    return geojson.FeatureCollection(features)


def as_geojson(response, geometry):
    """Parse an iterable of elements to retrieve a GeoJSON FeatureCollection
    of the given geometry types. Non-relevant input elements are ignored.

    Parameters
    ----------
    response : json dict
        Overpass JSON response.
    geometry : str
        GeoJSON geometry type: point, linestring, polygon or multipolygon.
    
    Returns
    -------
    feature_collection : dict
        GeoJSON FeatureCollection.
    """
    geometry = geometry.lower()
    if geometry == 'point':
        return _as_points(response['elements'])
    elif geometry == 'linestring':
        return _as_linestrings(response['elements'])
    elif geometry == 'polygon':
        return _as_polygons(response['elements'])
    elif geometry == 'multipolygons':
        return _as_multipolygons(response['elements'])
    else:
        raise ValueError('Bad geometry type.')
