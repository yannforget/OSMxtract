from osmxtract.location import (
    _find_utm_crs,
    geocode,
    _spatial_buffer,
    _reproject_bounds,
)

_ADDRESS = 'Université Libre de Bruxelles'
_LAT = 50.81
_LON = 4.38
_CRS = {'init': 'epsg:32631'}
_UTM_BOUNDS = (587227.11, 5619604.09, 607227.11, 5639604.09)
_WGS84_BOUNDS = (3.94, 44.84, 4.09, 44.96)
_BUFFER_SIZE = 10000


def test_find_utm_crs():
    assert _find_utm_crs(_LAT, _LON) == _CRS


def test_geocode():
    lat, lon = geocode(_ADDRESS)
    lat = round(lat, 2)
    lon = round(lon, 2)
    assert (lat, lon) == (_LAT, _LON)


def test_bounds_from_buffer():
    buffer = _spatial_buffer(_LAT, _LON, 10000, _CRS)
    bounds = tuple([round(b, 2) for b in buffer.bounds])
    assert bounds == _UTM_BOUNDS


def test_reproject_bounds():
    bounds = _reproject_bounds(_UTM_BOUNDS, _CRS)
    bounds = tuple([round(b, 2) for b in bounds])
    assert bounds == _WGS84_BOUNDS
