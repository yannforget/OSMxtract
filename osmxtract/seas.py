"""Use water polygons from openstreetmapdata.org."""

import os
import shutil

import requests
import fiona
from tqdm import tqdm
from appdirs import user_data_dir


URL = 'http://data.openstreetmapdata.com/water-polygons-split-4326.zip'


def download():
    """Download water-polygons shapefile."""
    dst_dir = user_data_dir(appname='osmxtract')
    os.makedirs(dst_dir, exist_ok=True)
    filename = URL.split('/')[-1]
    dst_file = os.path.join(dst_dir, filename)
    r = requests.head(URL)
    content_length = int(r.headers['Content-Length'])
    progress = tqdm(total=content_length, unit='B', unit_scale=True)
    chunk_size = 1024 ** 2
    with requests.get(URL, stream=True) as r:
        with open(dst_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress.update(chunk_size)


def is_downloaded():
    """Check if seas shapefile is downloaded."""
    data_dir = user_data_dir(appname='osmxtract')
    expected_path = os.path.join(
        data_dir, 'water-polygons-split-4326.zip'
    )
    return os.path.isfile(expected_path)


def clean():
    """Clean downloaded data."""
    data_dir = user_data_dir(appname='osmxtract')
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)


def get_water_polygons(bounds):
    """Get water polygons according to the provided bounds.

    Parameters
    ----------
    bounds : tuple
        Bounds decimal lat/lon coordinates (xmin, ymin, xmax, ymax).

    Returns
    -------
    feature : iterable
        Output features as an iterable of GeoJSON-like dicts.
    """
    data_dir = user_data_dir(appname='osmxtract')
    if not is_downloaded():
        download()
    zip_path = os.path.join(data_dir, 'water-polygons-split-4326.zip')
    shp_path = '/water-polygons-split-4326/water_polygons.shp'
    with fiona.open(shp_path, vfs=f'zip://{zip_path}') as src:
        features = [feature for _, feature in src.items(bbox=bounds)]
    return features
