import threading
import urllib
from django.core.servers import basehttp 
from django.core.handlers.wsgi import WSGIHandler 

class TestServerThread(threading.Thread):
    """
    Thread for running a http server while tests are running.
    """
    def __init__(self, address, port):
        self.address = address
        self.port = port

        self._started = threading.Event()
        self._stopped = False
        self._error = None

        super(TestServerThread, self).__init__()

    def start(self):
        """ Start the server thread and wait for it to be ready. """
        super(TestServerThread, self).start()
        self._started.wait()
        if self._error:
            raise self._error

    def stop(self):
        """ Stop the server. """
        self._stopped = True

        # Send an http request to wake the server
        url = urllib.urlopen('http://%s:%d/fake/request/' % (self.address, self.port)) 
        url.read()

        # Wait for server to finish
        self.join(5)
        if self._error:
            raise self._error

    def run(self):
        """ Sets up test server and database and loops over handling http requests. """
        try:
            handler = basehttp.AdminMediaHandler(WSGIHandler())
            server_address = (self.address, self.port)
            httpd = basehttp.WSGIServer(server_address, basehttp.WSGIRequestHandler)
            httpd.set_app(handler)
        except basehttp.WSGIServerException as e:
            self._error = e
        finally:
            self._started.set()

        # Loop until we get a stop event.
        while not self._stopped:
            httpd.handle_request()
