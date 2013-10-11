import unittest

import Instance

class TestInstance(unittest.TestCase):

    def SetUp(self):
        pass

    def test_getter_setter(self):
        """
        Test Instance getter and setter functions
        """
        instance = Instance.Instance('id1')
        self.assertEqual(instance.get_instance_id(),'id1')
        self.assertEqual(instance.get_name(),'id1')

        instance.set_instance_id('id2')
        self.assertEqual(instance.get_instance_id(),'id2')
        self.assertEqual(instance.get_name(),'id2')

        instance.set_name('myInstance')
        self.assertEqual(instance.get_name(),'myInstance')

        self.assertIsNone(instance.get_ssh_key_name())
        self.assertIsNone(instance.get_log_conf())
        self.assertIsNone(instance.get_ip_address())

        self.assertEqual(instance.get_filters(),['/var/log/'])
        self.assertEqual(instance.get_logs(),[])

#from LogentriesSDK.client import Client
#logentries = Client('cc639a67-1d48-448b-b5f2-85adbe16e79a')
#new_host = logentries.create_host('myscripthost')
#new_log = logentries.create_log_token( new_host, 'mynewlog' )
#output = logentries.to_json()
#f = open('output.txt', 'w')
#f.write(output)
#f.close()
