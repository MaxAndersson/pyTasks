import os
import novaclient
from novaclient.client import Client
import time
import uuid

class CPOSPServer(object):
    """Abstract Class"""

    NOVA_VERSION = '2'
    _client = None
    _config = None
    _server_config = None


    #def __init__(self, name, context_commands, server_config):
    def __init__(self,name):
        if(self._client == None):
            try:
                CPOSPServer.factory()
            except Exception as e:
                raise Execption('Could not find credentials')
            return None
        #self._commands = context_commands
        self._server_config = self.get_server_config_defaults()

    #    if(self._check_server_name(name) == False):
    #        print 'There is already an instance running with name: {}'.format(name)
    #        return None


        return self

    def boot(self):
        image = self.get_image()
        if image != None:
            self._contexulize = False
            self._server_config['image'] = image
        else:
            self._contexulize = True
        try:
            self._id = uuid.uuid1()
            self._server_config['userdata'] = self._get_contextulizeation()
            self._server_config['name'] = self._server_config['name'] + '-' + str(self._id)
            print self._server_config
            self._server = self._client.servers.create(**self._server_config)
        except Exception as e:
            raise Exception('Booting Problem: {}'.format(e))

        return True

    def _check_floating_ip_assignment(self,server):
        try:
            floating_ip = [ip for ip in self._client.floating_ips.list() if ip.instance_id == self._server.id ].pop().ip
            return floating_ip
        except:
            return None

    def _check_floating_ips_reuse(self):
        return [ip for ip in self._client.floating_ips.list() if ip.instance_id == None]

    def _get_floating_ip(self,pool):
            ip  = self._check_floating_ips_reuse()
            if ip != []:
                return ip.pop()
            else:
                ip = self._client.floating_ips.create(pool)
                return ip
    def _deploy_with_context(self):
        try:
            self._ssh = client()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(self._ip,
                            username = 'ubuntu',
                            key_filename ='cposp_key.pem')

        except Exception as e:
            print e ,self._ip
            return

        for command in self._commands:
            try:

                (stdin,stdout,stderr) = self._ssh.exec_command(command)

                #if(stderr != None):
                #    raise Exception(stderr)
                print stdout.read()
                print stderr.read()

            except Exception as e:
                print 'Something went wrong while executeing commands:'.format(e), stdout, stderr

#    def _create_image(self, server = self._server, ):
#        return

    def _attach_floating_ip(self, pool = 'ext-net'):
        #TODO status never changes
        #    wait = 2
        #    while(self._server.status != 'ACTIVE'):
        #        print 'Server Not Active Yet, Retrying in {} secounds, Server Status {}'.format(wait, self._server.status)
        #        time.sleep(wait)
        #        wait = wait*2
            if(self._check_floating_ip_assignment(self._server) != None):
                raise Exception('Server already has an floating IP')
            ip = self._get_floating_ip(pool)
            try:
                self._server.add_floating_ip(ip.ip)
                self._ip = ip.ip
                return ip.ip

            except Exception as e:
                raise Exception("Failed to attach a floating IP to the controller.\n{0}".format(e))
            return ip.ip

    def _attach_security_group(self):
        ##TODO Seperate security groups for master and slave
        ports = [5672,15672,5000,5555]
        security_group = [sg  for sg in self._client.security_groups.list() if sg.name == 'CPOSP']
        if security_group == []:
            security_group = self._client.security_groups.create('CPOSP','This security group is used by the CellProfiler OpenStack Provitioner')
            for port in ports:
                self._client.security_group_rules.create(security_group.id,ip_protocol='TCP',from_port = port,to_port=port)
        else:
            security_group = security_group.pop()
        retry = 0
        while retry < 10 :
            try:
                self._server.add_security_group(security_group.id)
                break
            except Exception:
                print 'Retrying to attach security group: ', security_group
                time.sleep(2)
                retry = retry + 1





    def get_client(self):
        return _client

    def _set_client(self,client):
        _client = client
    def _get_key_pair(self, name = 'CPOSP_key'):
        try:
            return self._client.keypairs.find(name = name)
        except:
            return self._client.keypairs.create(name)
    @classmethod
    def factory(cls,client_config = None):
        if client_config == None:
            client_config = os.environ
            cls._config = {
            'username' : client_config['OS_USERNAME'],
            'api_key' : client_config['OS_PASSWORD'],
            'project_id' : client_config['OS_TENANT_NAME'],
            'auth_url' : client_config['OS_AUTH_URL'],
            }
        else:
            cls._client = client_config
        try:
            cls._client = Client(cls.NOVA_VERSION, **cls._config)
            #print cls._client
            return True
        except Exception as e:
            print 'Client connection could not be established: {}'.format(e)
            return False
