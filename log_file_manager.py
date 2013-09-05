

class Log_File_Manager(object):
    """ 
    This class manages synchronization between logentries log configuration files, log files present on the instance and Logentries hosts.
    """

    def __init__(self, instance=None, host=None, client=None):
        """
        Args:
        instance represents an ec2 instance
        host represents a Logentries host
        client represents a Logentries client
        """
        self._instance = instance
        self._host = host
        self._client = client
    
    def set_instance(self,instance):
        self._instance = instance

    def set_host(self,host):
        self._host = host

    def set_client(self,client):
        self._client = client

    def get_instance(self):
        return self._instance

    def get_host(self):
        return self._host

    def get_client(self):
        return self._client

    def sync_log_config(self):
        pass
