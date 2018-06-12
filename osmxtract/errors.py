class OverpassBadRequest(Exception):
    """Error 400: Syntax error."""
    pass

class OverpassMoved(Exception):
    """Error 302: Moved."""
    pass

class OverpassTooManyRequests(Exception):
    """Error 429: Too many requests."""
    pass

class OverpassGatewayTimeout(Exception):
    """Error 504: Too much load."""
    pass