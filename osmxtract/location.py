"""Generate bounding boxes from addresses, lat/lon or input files."""

import math

import pyproj
import fiona
import rasterio
from geopy.geocoders import Nominatim
from shapely.geometry import Point


def _find_utm_crs(lat, lon):
    """Find the UTM CRS based on lat/lon coordinates.

    Parameters
    ----------
    lat : float
        Decimal latitude.
    lon : float
        Decimal longitude.

    Returns
    -------
    crs : dict
        Corresponding UTM CRS.
    """
    utm_zone = (math.floor((lon + 180) // 6) % 60) + 1
    if lat >= 0:
        pole = 600
    else:
        pole = 700
    epsg = 32000 + pole + utm_zone
    return {'init': f'epsg:{epsg}'}


def geocode(address):
    """Retrieve lat/lon coordinates of an address with Nominatim.

    Parameters
    ----------
    address : str
        Address to geocode (ex: "Brussels, Belgium").

    Returns
    -------
    lat : float
        Decimal latitude.
    lon : float
        Decimal longitude.
    """
    geolocator = Nominatim()
    location = geolocator.geocode(address)
    return location.latitude, location.longitude


def _spatial_buffer(lat, lon, size, intermediate_crs):
    """Generate a spatial buffer around a given point.

    Parameters
    ----------
    lat : float
        Decimal latitude.
    lon : float
        Decimal longitude.
    size : int
        Buffer size in meters.
    intermediate_crs : dict
        Intermediate CRS to calculate spatial buffer in meters.

    Returns
    -------
    buffer : shapely polygon
        Output buffer geometry.
    """
    proj = pyproj.Proj(**intermediate_crs)
    x, y = proj(lon, lat)
    return Point(x, y).buffer(size)


def _reproject_bounds(bounds, src_crs):
    """Reproject bounding box coordinates to WGS84.

    Parameters
    ----------
    bounds : tuple
        Input bounds coordinates (lat_min, lon_min, lat_max, lon_max).
    src_crs : dict
        CRS of the input bounds coordinates.

    Returns
    -------
    bounds : tuple
        Reprojected bounds coordinates (lat_min, lon_min, lat_max, lon_max).
    """
    proj = pyproj.Proj(**src_crs)
    lat_min, lon_min, lat_max, lon_max = bounds
    lon_min, lat_max = proj(lon_min, lat_max, inverse=True)
    lon_max, lat_min = proj(lon_max, lat_min, inverse=True)
    return lat_min, lon_min, lat_max, lon_max


def _reorder_bounds(bounds):
    """Reorder bounds from shapely/fiona/rasterio order to the one
    expected by Overpass, e.g: `(x_min, y_min, x_max, y_max)` to
    `(lat_min, lon_min, lat_max, lon_max)`.
    """
    lon_min, lat_min, lon_max, lat_max = bounds
    return lat_min, lon_min, lat_max, lon_max


def from_buffer(lat, lon, buffer_size):
    """Get bounding box from a buffer.

    Parameters
    ----------
    lat : float
        Decimal latitude.
    lon : float
        Decimal longitude.
    buffer_size : int
        Buffer size in meters.

    Returns
    -------
    bounds : tuple
        Output bounding box (lat_min, lon_min, lat_max, lon_max).
    """
    intermediate_crs = _find_utm_crs(lat, lon)
    buffer = _spatial_buffer(lat, lon, buffer_size, intermediate_crs)
    bounds = _reorder_bounds(buffer.bounds)
    bounds = _reproject_bounds(bounds, intermediate_crs)
    return bounds


def from_file(filename):
    """Get bounding box from an input file.

    Parameters
    ----------
    filename : str
        Path to input vector or raster file.

    Returns
    -------
    bounds : tuple
        Output bounds (lat_min, lon_min, lat_max, lon_max).
    """
    try:
        with fiona.open(filename) as src:
            bounds, crs = src.bounds, src.crs
    except:
        try:
            with rasterio.open(filename) as src:
                bounds, crs = src.bounds, src.crs
        except:
            raise IOError('Unable to read metadata from input file.')

    # default CRS if not assigned
    if not crs:
        crs = {'init': 'epsg:4326'}

    # reorder from fiona and rasterio
    lon_min, lat_min, lon_max, lat_max = bounds
    bounds = lat_min, lon_min, lat_max, lon_max

    if crs['init'].lower() != 'epsg:4326':
        bounds = _reproject_bounds(bounds, crs)

    return bounds
