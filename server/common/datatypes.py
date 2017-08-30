from urllib.parse import urlparse

def avatar_url(value, *args):
    # This should include more robust handling of errors
    url = urlparse(value)

    if not (url.scheme == "http" or url.scheme == "https"):
        raise TypeError("Invalid Scheme")

    # Only return the path, because it should be relative to our domain
    return url.path
