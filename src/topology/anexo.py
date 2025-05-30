#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import OVSController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


def myNetwork():
    net = Mininet(topo=None, build=False, ipBase='10.0.0.0/8')

    info(' Adding controller\n')
    c0 = net.addController(name='c0', controller=OVSController)

    info(' Add switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    info(' Add hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/8')
    h2 = net.addHost('h2', ip='10.0.0.2/8')

    info(' Add links (con TCLink)\n')
    net.addLink(h1, s1, cls=TCLink)
    net.addLink(s1, s2, cls=TCLink)
    net.addLink(s2, s3, cls=TCLink)

    net.addLink(s3, h2, cls=TCLink, loss=10)

    info(' Starting network\n')
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])

    info(' Ajustando MTU en s2\n')

    s2.cmd('ifconfig s2-eth1 mtu 500')

    info('*** Running CLI\n')
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
