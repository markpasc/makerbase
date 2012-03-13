from urlparse import urlsplit

from makerbase import app


@app.template_filter('date')
def date_format(dt, format):
    return dt.strftime(format)


@app.template_filter('pretty_url')
def pretty_url(url):
    urlparts = urlsplit(url)
    host, path = urlparts.netloc, urlparts.path
    if host.startswith('www.'):
        host = host[4:]
    if path == '/':
        path = ''
    elif len(path) > 23:
        path = path[:20] + '...'
    return host + path
