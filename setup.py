from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='osmxtract',
    version='0.0.1',
    description='Extract vector and raster data from OSM.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yannforget/osmxtract',
    author='Yann Forget',
    author_email='yannforget@mailbox.org',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['earth observation', 'gis', 'openstreetmap'],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'requests',
        'click',
        'pyproj',
        'geojson',
        'shapely',
        'fiona',
        'rasterio',
        'geopy',
        'tqdm',
        'appdirs'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points="""
        [console_scripts]
        osmxtract=osmxtract.cli:cli
    """,
)
