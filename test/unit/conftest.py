"""Test fixtures."""
from builtins import super

from napalm.base.test import conftest as parent_conftest
from napalm.base.test.double import BaseTestDouble

from napalm_arubaoss.ArubaOS import ArubaOSS

import pytest


@pytest.fixture(scope='class')
def set_device_parameters(request):
    """Set up the class."""
    def fin():
        request.cls.device.close()
    request.addfinalizer(fin)

    request.cls.driver = ArubaOSS
    request.cls.patched_driver = PatchedArubaOSSDriver
    request.cls.vendor = 'arubaoss'

    parent_conftest.set_device_parameters(request)


def pytest_generate_tests(metafunc):
    """Generate test cases dynamically."""
    parent_conftest.pytest_generate_tests(metafunc, __file__)


class PatchedArubaOSSDriver(ArubaOSS):
    """Patched ArubaOSS Driver."""

    def __init__(
            self,
            hostname,
            username,
            password,
            timeout=60,
            optional_args=None):
        """Patched ArubaOSS Driver constructor."""
        super().__init__(hostname, username, password, timeout, optional_args)

        self.patched_attrs = ['device']
        self.device = FakeArubaOSSDevice()

    def is_alive(self):
        """Mock is_alive behaviour."""
        return {"is_alive": True}  # always alive during the tests...

    def open(self):
        """Mock open connection."""
        pass

    def close(self):
        """Mock close connection."""
        pass


class FakeArubaOSSDevice(BaseTestDouble):
    """ArubaOSS device test double."""
