from osmxtract.overpass import ql_query


_BOUNDS = (44.84, 3.94, 44.96, 4.09)
_TAG = 'highway'
_VALUES_UNIQUE = ['residential']
_VALUES_MULTIPLE = ['primary', 'secondary', 'tertiary']
_TIMEOUT = 25

# overpass ql query with only one value

_EXPECTED_1 = (
    '[out:json][timeout:25]; '
    'nwr["highway"="residential"](44.84,3.94,44.96,4.09); '
    'out geom qt;'
)

def test_ql_query_unique():
    query = ql_query(_BOUNDS, _TAG, _VALUES_UNIQUE, case_insensitive=False)
    assert query == _EXPECTED_1

# overpass ql query with multiple values

_EXPECTED_2 = (
    '[out:json][timeout:25]; '
    'nwr["highway"~"primary|secondary|tertiary"]'
    '(44.84,3.94,44.96,4.09); '
    'out geom qt;'
)

def test_ql_query_multiple():
    query = ql_query(_BOUNDS, _TAG, _VALUES_MULTIPLE, case_insensitive=False)
    assert query == _EXPECTED_2

# overpass ql query with multiple case-insensitive values

_EXPECTED_3 = (
    '[out:json][timeout:25]; '
    'nwr["highway"~"[pP]rimary|[sS]econdary|[tT]ertiary"]'
    '(44.84,3.94,44.96,4.09); '
    'out geom qt;'
)

def test_ql_query_multiple_nocase():
    query = ql_query(_BOUNDS, _TAG, _VALUES_MULTIPLE, case_insensitive=True)
    assert query == _EXPECTED_3

# overpass ql query without any value

_EXPECTED_4 = (
    '[out:json][timeout:25]; '
    'nwr["highway"](44.84,3.94,44.96,4.09); '
    'out geom qt;'
)

def test_ql_query_novalue():
    query = ql_query(_BOUNDS, _TAG, case_insensitive=False)
    assert query == _EXPECTED_4
