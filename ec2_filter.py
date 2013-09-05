import json

class Ec2Map:
    
    @staticmethod
    def get_true(ec2_instance):
        return True

    @staticmethod
    def get_false(ec2_instance):
        return False


    _map = {
        "get_true":get_true,
        "get_false":get_false,
        }

    def get_map(map_name):
        if map_name in _map:
            return _map[map_name]
        else:
            return None

    def get_map_name(map_f):
        for map_name in _map.keys():
            if _map[map_name]==map_f:
                return map_name
        return False


class EC2Filter(object):

    ALL='*'

    def __init__(self,name='default',include={ALL:'get_true'},exclude={}):
        self._name = name
        self._include = include
        self._exclude = exclude

    def set_name(self,name):
        self._name = name

    def get_name(self):
        return self._name

    def set_include(self,include):
        self._include = include

    def get_include(self):
        return self._include

    def set_exclude(self,exclude):
        self._exclude = exclude

    def get_exclude(self):
        return self._exclude

    def is_valid(self,ec2_instance):
        for key in self.get_include():
            map_f = EC2Map.get_map(self.get_include()[key])
            if map_f is not None:
                return map_f(ec2_instance)
        return False

    def to_json(self):
        return {"name":self.get_name(),"include":self.get_include(),"exclude":self.get_exclude()}

    @staticmethod
    def load_json(data):
        ec2_filter = EC2Filter()
        if 'name' in data:
            ec2_filter.set_name(data['name'])
        else:
            ec2_filter.set_name(None)

        if 'include' in data:
            ec2_filter.set_include(data['include'])
        else:
            ec2_filter.set_include({})

        if 'exclude' in data:
            ec2_filter.set_exclude(data['exclude'])
        else:
            ec2_filter.set_exclude({})
        return ec2_filter
