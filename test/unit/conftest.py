"""Test fixtures."""
from builtins import super

import pytest

import yaml
import copy

from napalm.base.test import conftest as parent_conftest

from napalm.base.test.double import BaseTestDouble

from napalm_arubaoss.ArubaOS import ArubaOSS

NAPALM_TEST_MOCK = "1"


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
        return {"is_alive": True}  # always alive during the tests...

    def open(self):
        pass

    def close(self):
        pass



class FakeArubaOSSDevice(BaseTestDouble):
    """ArubaOSS device test double."""
    def __init__(self):
        # self.rpc = FakeRPCObject(self)
        # self._conn = FakeConnection(self.rpc)
        self.alternative_facts_file = "facts.yml"
        # self.ON_JUNOS = True  # necessary for fake devices
        self.default_facts = {
	    "2930f": {
	        "out": {
        	    "vendor": "HPE Aruba",
	            "interface_list": [
	                "9",
	                "10",
	                "1",
	                "2",
	                "3",
	                "4",
	                "5",
	                "6",
	                "7",
	                "8"
	            ],
	            "hostname": "ansible-test",
	            "os_version": "WC.16.09.0004",
	            "serial_number": "CN93ABC3M1",
	            "model": "Aruba2930F-8G-PoE+-2SFP+ Switch(JL258A)",
	            "fqdn": "ansible-test.corp.ad.zalando.net"
	        },
	        "result": True,
	        "comment": ""
	    }
	} 
        self._uptime = 4380

    @property
    def facts(self):
        # we want to reinitialize it every time to avoid side effects
        self._facts = copy.deepcopy(self.default_facts)
        try:
            alt_facts_filepath = self.find_file(self.alternative_facts_file)
        except IOError:
            self._facts = self.default_facts
            return self._facts
        with open(alt_facts_filepath, "r") as alt_facts:
            self._facts.update(yaml.safe_load(alt_facts))
        return self._facts

    @property
    def uptime(self):
        return self._uptime

    def open(self):
        pass

    def close(self):
        pass

    def bind(*args, **kvargs):
        pass

    def cli(self, command=""):
        """Fake CLI method."""
        ret = dict()

        for command in command_list:
            filename = "{safe_command}.txt".format(safe_command=self.sanitize_text(command))
            filepath = self.find_file(filename)
        
            ret[self.sanitize_text(command)] = self.read_txt_file(filepath)

        return ret

    def run_commands(self, command_list, encoding='json'):
        """Fake run_commands."""
        result = list()

        for command in command_list:
            filename = '{}.{}'.format(self.sanitize_text(command), encoding)
            full_path = self.find_file(filename)

            if encoding == 'json':
                result.append(self.read_json_file(full_path))
            else:
                result.append({'output': self.read_txt_file(full_path)})

        return result

