from cposp_server import CPOSPServer

class C3Master(CPOSPServer):
    """docstring for C3Master"""
    def __init__(self):
        super(C3Master, self).__init__('C3Master')


    def _get_contextulizeation(self):
        if(self._contexulize):
            f = open('c3_master.sh')
            context = f.readline() + "" + f.read()
            f.close()
            return context
        else:
            f = open('c3_master_run.sh')
            context = f.readline() + "" + f.read()
            f.close()
            return context


    def boot(self):
        super(C3Master,self).boot()
        import time
        time.sleep(2)
        self._attach_security_group()
        self._attach_floating_ip()



    def get_image(self):
        try:
            return self._client.images.find(name='C3-Image')
        except:
            return None
            pass

    def get_server_config_defaults(self):
        return {
    'name': 'C3Master',
    'key_name' : self._get_key_pair().name,
    'flavor' : self._client.flavors.find(name='m1.medium'),
    'image' :self._client.images.find(name='Ubuntu Server 14.04 LTS (Trusty Tahr)'),
    }






class C3Slave(CPOSPServer):
    """docstring for C3Slave"""
    _master = None

    def __init__(self):
        super(C3Slave, self).__init__('C3Slave')

    def _get_contextulizeation(self):
        apo = CPOSPServer._client.servers.ips(self._master.id)
        key = apo.keys().pop()
        master_ip = apo[key].pop()['addr']
        if(self._contexulize):

            f = open('c3_slave.sh')
            context = f.readline() + "MASTER_IP='{}' \n".format(master_ip) + f.read()
            f.close()
            return context
        else:
            f = open('c3_slave_run.sh')
            context = f.readline() + "MASTER_IP='{}' \n".format(master_ip) + f.read()
            f.close()
            return context

    def boot(self):
        super(C3Slave,self).boot()


    @classmethod
    def boot_n(cls,n_slaves = 1):
        try:
            servers = [C3Slave() for i in range(0,n_slaves)]
            booted_servers = [server.boot() for server in servers]
            return [server._server for server in servers]
        except Exception as e:
            raise


    def get_image(self):
        try:
            return self._client.images.find(name='C3Slave-Image')
        except:
            return None
            pass

    def get_server_config_defaults(self):
            return {
        'name': 'C3Slave',
        'key_name' : self._get_key_pair().name,
        'flavor' : self._client.flavors.find(name='m1.medium'),
        'image' :self._client.images.find(name='Ubuntu Server 14.04 LTS (Trusty Tahr)'),
        }

def boot_cluster(num_workers = 1):
    master= C3Master()
    master.boot()
    C3Slave._master = master._server
    slaves = C3Slave().boot_n(num_workers)
    return dict(master=master,slaves=slaves)

def teminate_cluster(master,slaves):
    for slave in slaves:
        slave.delete()
    master.delete()
