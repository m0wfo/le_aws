import boto.ec2
import os.path
import json
import rsyslog_conf_gen as sdk
import ssh_keys

def get_instance(ssh_k,ec2_instance):
    """
    Args:
    ssh_k is an ssh_keys object that is not None.
    ec2_instance is an Boto instance object.
    """
    ssh_k.set_names(get_key_names())
    print 'Key Names = %s'%ssh_k.get_names()
    print 'Path Names = %s'%ssh_k.get_paths()
    local_keys = ssh_k.get_keys_onpaths(ssh_k.get_paths(),ssh_k.get_names())

    if local_keys[ec2_instance.key_name] is not None:
       if ec2_instance.platform is None:
          print 'Platform is Linux for instance with id=%s and can be ssh-ed!'%ec2_instance.id
          platf = 'linux'
    else:
       platf = ec2_instance.platform
       print 'Platform is %s for instance with id=%s'%(platf,ec2_instance.id)
    if 'Name' in ec2_instance.tags:
       name = ec2_instance.tags['Name']
    else:
       name = ec2_instance.id+'_'+ec2_instance.ip_address
    if 'user' in ec2_instance.tags:
       user = ec2_instance.tags['user']
    else:
       user = get_default_user(ec2_instance.platform)
    return sdk.Instance(aws_id=ec2_instance.id,ssh_key_name=local_keys[ec2_instance.key_name],ip_address=ec2_instance.ip_address,name=name,platform=platf,user=user)


if __name__ == '__main__':
   # 
   aws_conf = sdk.AWSConfFile()
   ec2_conn = boto.ec2.connection.EC2Connection(aws_access_key_id=aws_conf.get_aws_access_key_id(), aws_secret_access_key=aws_conf.get_aws_secret_access_key())

   reservations = ec2_conn.get_all_instances()
   for reservation in reservations:
      for ec2_instance in reservation.instances:
         ssh_k = ssh_keys.ssh_keys(paths=aws_conf.get_ssh_key_paths())
         aws_conf.add_instance(get_instance(ssh_k,ec2_instance))
   aws_conf.save()
   print aws_conf.to_json()
   ec2_conn.close()

