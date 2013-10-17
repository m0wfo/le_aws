import unittest

from logentriesprovisioning import Instance
from logentriessdk import models
from logentriessdk import client
from logentriessdk import constants

class TestModel(unittest.TestCase):
    """
    Test LogentriesSDK Models.
    """
    def SetUp(self):
        self.client = Client(account_key='9d1d1f88-eb3a-4522-8196-f45414530ef7')
        account = self.client.get_account()
        for host in account.get_hosts():
            self.client.remove_host(host)

    def test_host(self):
        host1 = self.client.create_host('test_host')
        host2 = self.client.get_host(host1.get_key())
        self.assertEqual(host1.get_key(),host2.get_key())
        self.assertEqual('test_host',host2.get_name())
        host3 = self.client.get_host(None,'test_key')
        self.assertEqual(host1.get_key(),host3.get_key())

    def test_log(self):
        host = self.client.create_host('test_host')
        log = self.client.create_log_token(host,'test_log')
        self.assertNotNone(log.get_token())
        log2 = self.client.get_log(log.get_key())
        self.assertEqual(log.get_name(),log2.get_name())

    def test_event_tags(self):
        event_id = client.create_event('test_event',constants.COLOR[0])
        host = self.client.create_host('test_host')
        log = self.client.create_log_token('test_log')

        event_data = client.get_event('test_event')
        self.assertEqual(event_data['name'],'test_event')
        self.assertIsNone(client.get_event('mhbsjhdfb'))

        client.remove_event(event_id))
        self.assertIsNone(client.get_event('test_event'))

        tag = client.create_tag( host, log.get_name(), 'test_tag', event_id, 'test_pattern')
        for _tag in client.get_tags(log.get_key())):
            self.assertEqual(tag['tagfilter_key'],_tag['tagfilter_key'])
