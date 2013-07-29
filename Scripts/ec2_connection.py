import boto.ec2
import os.path
import json
import rsyslog_conf_gen as sdk
import ssh_keys

def load_config(file):
   conf_str = open(file,'r')
   CONFIG = json.load(conf_str)
   try:
      ACCOUNT_KEY = CONFIG['account_key']
   except:
      print 'Please enter your account key in '
   return ACCOUNT_KEY,CONFIG

#CONFIG_FILE = 'logentries_config.json'
#CONFIG = load_config(CONFIG_FILE)
AWS_ACCESS_KEY_ID = 'AKIAINT5AHHNNBWO3IOQ'
AWS_SECRET_ACCESS = '0vNc1N5F84mnkyE6Z5hTRBpp1JIjozhMgszrQ6Mu'
REGIONS = ["eu-west-1","us_west_1"]

CONS = [boto.ec2.connect_to_region(region,aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS) for region in REGIONS]


def set_cons():
    """ """
    global CONS 
    CONS = [boto.ec2.connect_to_region(region,aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS) for region in REGIONS]

def close_cons():
    """ """
    for con in CONS:
        if con is not None:
            con.close()

def get_con_id(region):
    """ """
    return REGIONS.index(region)

def get_con(region):
    """ """
    return CONS[get_con_id(region)]

def get_key_names(region):
    """ Args"""
    con = get_con(region)
    if con is not None:
        key_pairs = con.get_all_key_pairs()
        return [key_pair.name for key_pair in key_pairs]
    return []

def get_key_names():
    """ Args"""
    result = []
    for region in REGIONS:
        con = get_con(region)
        if con is not None:
            key_pairs = con.get_all_key_pairs()
            result.extend([key_pair.name for key_pair in key_pairs])
    return result

def get_key_onpath(path,key_name):
    """ """
    choices = ['%s%s.pem'%(path,key_name),'%s/%s.pem'%(path,key_name)]
    for choice in choices:
        if os.path.isfile(os.path.abspath(choice)):
            return choice
    return None

def get_keys_onpath(path,key_names):
    """ """
    result = {}
    for key_name in key_names:
        key_path = get_key_onpath(path,key_name)
        if key_path is not None:
            result[key_name] = key_path
    return result


def get_keys_onpaths(paths,key_names):
    """ """
    result = {}
    for path in paths:
        keys_path_dict = get_keys_onpath(path,key_names)
        result.update(keys_path_dict)
    return result

def get_default_user(platform):
    """ TO BE COMPLETED """
    if platform is None:
        return None
    return None

def get_instances(ssh_k):
    """ Args """
    result = []
    ssh_k.set_names(get_key_names())
    print 'Key Names = %s'%ssh_k.get_names()
    print 'Path Names = %s'%ssh_k.get_paths()
    local_keys = ssh_k.get_keys_onpaths(ssh_k.get_paths(),ssh_k.get_names())
    for region in REGIONS:
        con = get_con(region)
        if con is not None:
            reservations = con.get_all_instances()
            for reservation in reservations:
                for aws_instance in reservation.instances:
                    if local_keys[aws_instance.key_name] is not None:
                        if aws_instance.platform is None:
                            print 'Platform is Linux for instance with id=%s and can be ssh-ed!'%aws_instance.id
                            platf = 'linux'
                        else:
                            platf = aws_instance.platform
                            print 'Platform is %s for instance with id=%s'%(platf,aws_instance.id)
                        if 'Name' in aws_instance.tags:
                            name = aws_instance.tags['Name']
                        else:
                            name = aws_instance.id+'_'+aws_instance.ip_address
                        if 'user' in aws_instance.tags:
                            user = aws_instance.tags['user']
                        else:
                            user = get_default_user(aws_instance.platform)
                        instance = sdk.Instance(aws_id=aws_instance.id,ssh_key_name=local_keys[aws_instance.key_name],ip_address=aws_instance.ip_address,name=name,platform=platf,user=user)
                        result.append(instance)
    return result

if __name__ == '__main__':
   set_cons()
   aws_conf = sdk.AWSConfFile()
   ssh_k = ssh_keys.ssh_keys(paths=aws_conf.get_ssh_key_paths())
   aws_conf.add_instances(get_instances(ssh_k))
   aws_conf.save()
#   for instance in get_instances():
#        print json.dumps(instance.to_json())
   for con in CONS:
       if con is not None:
           con.close()

