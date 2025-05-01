from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

class LinearTopo(Topo):
    def build(self):
        # Crear 2 hosts y 3 switches
        host1 = self.addHost('host1')
        host2 = self.addHost('host2')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Configurar enlaces con parámetros específicos
        self.addLink(host1, s1, cls=TCLink)
        self.addLink(s1, s2, cls=TCLink)
        
        # Enlace central con MTU reducido a 500 bytes
        self.addLink(s2, s3, cls=TCLink, params2={'delay': '1ms', 'mtu': 500})
        
        self.addLink(s3, host2, cls=TCLink)
        #     Visualización de la Topología:
        #
        #  h1 <--> s1 <--> s2 (MTU 500) <--> s3 <--> h2
        #                 (Pérdida 30% en s3-eth2)


def create_loss(net, switch, interface, loss_percent):
    """Configura pérdida de paquetes en una interfaz de switch"""
    # Los switches en Mininet no tienen IP, usamos tc directamente en la interfaz
    switch.cmd(f'tc qdisc add dev {interface} root netem loss {loss_percent}%')

def run():
    topo = LinearTopo()
    net = Mininet(topo=topo)
    net.start()

    # Configurar pérdida del 30% en la interfaz s3-ethost2 (hacia host2)
    create_loss(net, net.get('s3'), 's3-ethost2', 30)

    # Verificar conectividad
    print("Testeando conectividad básica:")
    net.pingAll()

    # Iniciar CLI interactiva
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()