try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from io import BytesIO as IO
except ImportError:
    from StringIO import StringIO as IO
from container.index import Handler 


class TestableHandler(Handler):
    # On Python3, in socketserver.StreamRequestHandler, if this is
    # set it will use makefile() to produce the output stream. Otherwise,
    # it will use socketserver._SocketWriter, and we won't be able to get
    # to the data
    wbufsize = 1

    def finish(self):
        # Do not close self.wfile, so we can read its value
        self.wfile.flush()
        self.rfile.close()

    def date_time_string(self, timestamp=None):
        """ Mocked date time string """
        return 'DATETIME'

    def version_string(self):
        """ mock the server id """
        return 'BaseHTTP/x.x Python/x.x.x'


class MockSocket(object):
    def getsockname(self):
        return ('sockname',)


class MockRequest(object):
    _sock = MockSocket()

    def __init__(self, path):
        self._path = path

    def makefile(self, *args, **kwargs):
        if args[0] == 'rb':
            return IO(b"GET %s HTTP/1.0" % self._path)
        elif args[0] == 'wb':
            return IO(b'')
        else:
            raise ValueError("Unknown file type to make", args, kwargs)


class HTTPRequestHandlerTestCase(unittest.TestCase):
    maxDiff = None

    def _test(self, request):
        handler = TestableHandler(request, (0, 0), None)
        return handler.wfile.getvalue()

    def test_success_response(self):
        self.assertEqual(
                self._test(MockRequest(b'/')),
                b'HTTP/1.0 400 OK\r\nServer: BaseHTTP/x.x Python/x.x.x\r\nDate: DATETIME\r\nContent-Type: text/html\r\n\r\n<!doctype html>\n<html><head><title>It works</title></head>\n<body>\n    <h1>Hello from a Docker container</h1>\n    <p>This container got built from an asset and runs on Fargate.</p>\n    <img src="https://media.giphy.com/media/XeXJlF9ouoWkeAyHhO/giphy.gif">\n</body>\n'
                )


def main():
    unittest.main()


if __name__ == "__main__":
    main()