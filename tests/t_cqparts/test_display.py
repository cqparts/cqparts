import unittest
import mock
import sys

import cadquery

from base import CQPartsTest
from base import testlabel
from base import skip_if_no_freecad
from base import suppress_stdout_stderr

from partslib import Box
from partslib import CubeStack

# Unit under test
import cqparts
from cqparts import display


# Forgiving mock.patch wrapper:
#   Wrap mock.patch to not fall over on an import error.
#   negative side: This promotes test-failures to be runtime instead of
#       compile-time, however...
#   positive side: These tests should be skipped anyway... see reasoning
#       in more detail below
def patch_forgiving(*args, **kwargs):
    def decorator(func):
        try:
            return mock.patch(*args, **kwargs)(func)
        except (ImportError, AttributeError):
            # Patch module or attribute could not be patched.
            # return something nonetheless.
            def inner(*args, **kwargs):
                #args.append(mock.MagicMock())
                args.append(None)  # should fail in any testcase
                return func(*args, **kwargs)
            return inner

    return decorator


# Skip if no FreeCAD:
#   Skip Logic:
#       Test is skipped if necessary FreeCAD Python module(s) cannot be imported.
#   Justification:
#       cqparts should not require FreeCAD to be installed to function.
#       This IS currently a problem with cadquery, which is being worked on
#       to resolve... but that limitation should not follow through to cqparts.
#       So if the OS of the host test machine does not have FreeCAD, then these
#       tests are skipped in favour of failing.
@unittest.skipIf(*skip_if_no_freecad())
class FreeCADTests(CQPartsTest):

    @patch_forgiving('Helpers.show')
    def test_part(self, mock_show):
        part = Box()
        disp_env = display.freecad.FreeCADDisplayEnv()
        disp_env.display(part)
        mock_show.assert_called_once_with(part.local_obj, (192, 192, 192, 0))

    @patch_forgiving('Helpers.show')
    def test_assembly(self, mock_show):
        assembly = CubeStack()
        disp_env = display.freecad.FreeCADDisplayEnv()
        disp_env.display(assembly)

        self.assertEqual(len(mock_show.call_args_list), 2)  # 2 objects
        for (args, kwargs) in mock_show.call_args_list:
            self.assertIn(args[0], map(lambda x: x.world_obj, assembly.components.values()))

    @patch_forgiving('Helpers.show')
    def test_cadquery_obj(self, mock_show):
        obj = cadquery.Workplane('XY').box(1,1,1)
        disp_env = display.freecad.FreeCADDisplayEnv()
        disp_env.display(obj)
        mock_show.assert_called_once_with(obj)


@testlabel('web')
class WebTests(CQPartsTest):

    @mock.patch('time.sleep', mock.Mock(side_effect=KeyboardInterrupt()))
    @mock.patch('webbrowser.open')
    @mock.patch(('socketserver' if sys.version_info[0] >= 3 else 'SocketServer') + '.ThreadingTCPServer')
    def test_basic(self, mock_serverobj, mock_webbrowser_open):
        # setup mocks
        mock_server = mock.MagicMock(server_address=('abc', 123))
        mock_serverobj.return_value = mock_server

        part = Box()
        disp_env = display.web.WebDisplayEnv()
        with suppress_stdout_stderr():
            disp_env.display(part)

        # webbrowser.open called
        self.assertEquals(len(mock_webbrowser_open.call_args_list), 1)
        mock_webbrowser_open.assert_called_once_with('http://abc:123/')

        # SocketServer.ThreadingTCPServer.serve_forever called
        mock_server.serve_forever.assert_called_once_with()

    def test_bad_component(self):
        disp_env = display.web.WebDisplayEnv()
        with self.assertRaises(TypeError):
            disp_env.display(123)


@testlabel('web')
class CQPartsServerTests(CQPartsTest):

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    @mock.patch('os.environ', {'CQPARTS_SERVER': 'http://abc:123'})
    def test_basic(self, mock_requests_post, mock_requests_get):
        part = Box()
        disp_env = display.cqparts_server.CQPartsServerDisplayEnv()
        disp_env.display(part)

        # status
        mock_requests_get.assert_called_once_with('http://abc:123/status')

        self.assertEqual(len(mock_requests_post.call_args_list), 2)
        # upload
        (args, kwargs) = mock_requests_post.call_args_list[0]
        self.assertEqual(args, ('http://abc:123/upload',))
        self.assertEqual(len(kwargs['files']), 2)
        # notify
        (args, kwargs) = mock_requests_post.call_args_list[1]
        self.assertEqual(args, ('http://abc:123/notify',))

    def _raise_connectionerror(*args, **kwargs):
        import requests
        raise requests.exceptions.ConnectionError

    @mock.patch('requests.get', _raise_connectionerror)
    @mock.patch('requests.post')
    @mock.patch('os.environ', {'CQPARTS_SERVER': 'http://abc:123'})
    def test_no_connection(self, mock_requests_post):
        part = Box()
        disp_env = display.cqparts_server.CQPartsServerDisplayEnv()
        disp_env.display(part)

        # no error, and no further contact attempted
        mock_requests_post.assert_not_called()

    @mock.patch('os.environ', {})  # empty
    def test_bad_env(self):
        disp_env = display.cqparts_server.CQPartsServerDisplayEnv()
        with self.assertRaises(KeyError):
            disp_env.display(Box())

    @mock.patch('os.environ', {'CQPARTS_SERVER': 'http://abc:123'})
    def test_bad_component(self):
        disp_env = display.cqparts_server.CQPartsServerDisplayEnv()
        with self.assertRaises(TypeError):
            disp_env.display(123)
