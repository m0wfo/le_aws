import boto.ec2
import os.path

aws_access_key_id = 'AKIAINT5AHHNNBWO3IOQ'
aws_secret_access_key = '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'
regions = ["eu-west-1","us_west_1"]

cons = []


def set_cons():
    """ """
    global cons 
    cons = [boto.ec2.connect_to_region(region,aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key) for region in regions]

def close_cons():
    """ """
    for con in cons:
        if con is not None:
            con.close()

def get_con_id(region):
    """ """
    return regions.index(region)

def get_con(region):
    """ """
    return cons[get_con_id(region)]

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
    for region in regions:
        con = get_con(region)
        if con is not None:
            key_pairs = con.get_all_key_pairs()
            result.extend([key_pair.name for key_pair in key_pairs])
    return result

def get_key_path(path,key_name):
    """ """
    choices = ['%s%s.pem'%(path,key_name),'%s/%s.pem'%(path,key_name)]
    for choice in choices:
        print choice
        if os.path.isfile(os.path.abspath(choice)):
            return choice
    return None

def get_keys_path(path,key_names):
    """ """
    result = []
    for key_name in key_names:
        key_path = get_key_path(path,key_name)
        if key_path is not None:
            result.append(key_path)
    return result


def get_keys_paths(paths,key_names):
    """ """
    result = []
    for path in paths:
        key_path = get_keys_path(path,key_names)
        result.extend(key_path)
    return result

if __name__ == '__main__':
    set_cons()
    paths = ['%s/.ssh/'%os.path.expanduser('~')]
    key_names = get_key_names()
    print get_keys_paths(paths,key_names)
    [con.close() for con in cons]
