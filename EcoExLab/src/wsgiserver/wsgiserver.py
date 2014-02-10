#!/usr/bin/python2

"""wsgiserver.py - a proxy server that serves web pages but delegates any queries and other
requests to a wsgi application.
"""


import os, fnmatch
from wsgiref import simple_server


def readDirTree(directory = '.', include = ['*'], exclude = []):
    """Returns all files of the current directory and all subdirectories
    as a list. Only files that match any of the wildcards or names
    in the include list and none of the wildcards or names in the
    exclude list will be included. The returned list contains the
    complete file paths relative to 'directory'."""
    files = []
    directory = os.path.normpath(directory); N = len(directory)
    for dirname, subdirs, names in os.walk(directory):
        dirname = dirname[N:]
        for entry in names:
            absolute_path = os.path.join(dirname, entry)
            for wildcard in include:
                if fnmatch.fnmatch(absolute_path, wildcard):
                    break
            else:
                continue
            for wildcard in exclude:
                if fnmatch.fnmatch(absolute_path, wildcard):
                    break
            else:         
                files.append(absolute_path)
    return files


class AppProxy(object):
    """A proxy WSGI-application that resembles a minimal webserver. Whenever
    a GET request is identified as a simple request for a web page
    (i.e. not a query) the page will be served by this proxy. Otherwise
    the request is handed over to the proxied application."""
    
    ERROR_404 = "<html><body><h1>404 - File not found: %s</h1></body></html>"
    ERROR_403 = "<html><body><h1>403 - Forbidden: %s</h1></body></html>"
    
    def __init__(self, application, directory = '.',
                 include = ['*'], exclude = ['*.py', '*~', '.*', '/.*']):
        """Crates AppProxy object. All files in 'directory' that match a wild
        card in 'include' and do not match any wild card in exclude will
        be served upon request. All queries or non GET requests (e.g. POST
        requests) will be delegated to 'application'. Files added after
        the AppProxy object was created will always be ignored."""
        self.directory = directory
        self.allowedFiles = set(readDirTree(directory, include, exclude))
        self.application = application
        
    def error_message(self, start_response, status_code, msg):
        headers = [('Content-Type', 'text/html; charset=utf-8'),
                   ('Content-Length', str(len(msg)))]  
        start_response(status_code, headers)
        return [msg]           

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'GET':
        
            if environ['QUERY_STRING']:
                # delegate query
                return self.application(environ, start_response)
            
            else: 
                # no query, therefore serve the requested web page
                path = environ['PATH_INFO']
                if path.startswith("/"): path = path[1:]
                if path in self.allowedFiles:
                    try:
                        f = open(os.path.join(self.directory, path))
                        # page = bytes(f.read(), "utf-8") # <-- works only with python 3
                        page = f.read().encode("utf-8")
                        headers = [('Content-Type','text/html; charset=utf-8'), 
                                   ('Content-Length', str(len(page)))]
                        start_response('200 OK', headers)
                        return [page]
                                                  
                    except IOError:
                        return self.error_message(start_response, '404 Not Found',
                                                  AppProxy.ERROR_404 % path)                      
                else:
                    return self.error_message(start_response, '403 Forbidden',
                                              AppProxy.ERROR_403 % path)
        
        else:
            # delegate request that is not a GET request
            return self.application(environ, start_response)


if __name__ == '__main__':
    if not os.path.exists("test.html"):
        try:
            f = open('test.html', 'w')
            f.write('<html><body><b>test successful</b></body></html>')
            f.close()
        except IOError:
            print ("IOError while creating file 'test.html'!")
        dont_delete = False
    else:
        dont_delete = True    
    httpd = simple_server.make_server(
            '', 8000, AppProxy(simple_server.demo_app))
    sn = httpd.socket.getsockname()
    print ("Serving HTTP on", sn[0], "port", sn[1], "...")
    import webbrowser
    webbrowser.open('http://localhost:8000/xyz?abc')
    webbrowser.open('http://localhost:8000/test.html')
    httpd.handle_request()
    httpd.handle_request()
    if not dont_delete:  
        try:
            os.remove('test.html')
        except OSError:
            pass

