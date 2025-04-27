from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import Node

class Router(Node):
    """ Nodo personalizado que actúa como router """
    def config(self, **params):
        super().config(**params)
        # Nodo con forwarding habilitado -> router virtual
        self.cmd("sysctl -w net.ipv4.ip_forward=1")  

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()

class RouterTopo(Topo):
    def build(self):
        self.host1_ip = "10.0.1.2"
        self.host2_ip = "10.0.2.2"
        router = self.addNode("router", cls=Router, ip=None)

        host1 = self.addHost("host1", ip = f"{self.host1_ip}/24", defaultRoute="via 10.0.1.1")
        host2 = self.addHost("host2",  ip = f"{self.host2_ip}/24", defaultRoute="via 10.0.2.1")
        # Enlaces e interfaces en el router
        self.addLink(host1, router,
                     intfName2="router-eth1",
                     params2={"ip": "10.0.1.1/24"})
        
        self.addLink(host2, router,
                     intfName2="router-eth2",
                     params2={"ip": "10.0.2.1/24"})
        
        # Visualización de la Topología:
        #
        # host1(10.0.1.2/24) <--> [router-eth1](10.0.1.1/24) 
        #                              |
        #                          [router-eth2](10.0.2.1/24) <--> host2(10.0.2.2/24) 

def apply_loss(node, intf_name, loss_percent):
    """Aplica pérdida de paquetes a una interfaz"""
    node.cmd(f"tc qdisc add dev {intf_name} root netem loss {loss_percent}%")

def run():
    topo = RouterTopo()
    net = Mininet(topo=topo)
    net.start()
    
    #Configuramos pérdida en ambas interfaces del router
    r1 = net.get("r1")
    apply_loss(r1, "r1-eth1", 10)
    apply_loss(r1, "r1-eth2", 10)
    
    # Iniciamos Command Line Interface interactiva para que puedas performar programas en esta red!
    CLI(net)
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    run()
