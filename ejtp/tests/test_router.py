import logging

from ejtp.util.compat import unittest, StringIO
from ejtp import router

class TestRouter(unittest.TestCase):

    def setUp(self):
        self.router = router.Router()

    def test_jack_already_loaded(self):
        from ejtp.jacks import Jack
        class DummyJack(Jack):
            def run(self, *args):
                pass

        jack = DummyJack(self.router, (1, 2, 3))
        self.assertRaisesRegexp(ValueError,
            'jack already loaded', self.router._loadjack, jack)

    def test_client_already_loaded(self):
        from ejtp.client import Client
        client = Client(None, (4, 5, 6), make_jack = False)
        self.router._loadclient(client)
        self.assertRaisesRegexp(ValueError,
            'client already loaded', self.router._loadclient, client)


class TestRouterStream(unittest.TestCase):

    def setUp(self):
        self.router = router.Router()
        self.stream = StringIO()
        handler = logging.StreamHandler(self.stream)
        router.logger.setLevel(logging.INFO)
        router.logger.addHandler(handler)

    def _assertInStream(self, expected):
        value = self.stream.getvalue()
        self.assertIn(expected, value)

    def _test_message(self, expected, message='Jam and cookies', destination='["local",null,"example"]', format=None):
        data = ''.join([format, destination, '\x00', message])
        self.router.recv(data)
        self._assertInStream(expected)

    def test_recv_invalid_message(self):
        self.router.recv('qwerty')
        self._assertInStream("Router could not parse frame: 'qwerty'")

    def test_client_inexistent(self):
        self._test_message('Router could not deliver frame', format='r')

    def test_frame_with_no_destination(self):
        self._test_message('Frame recieved directly from', format='s')

    def test_frame_with_weird_type(self):
        self._test_message('Frame has a type that the router does not understand', format='x')