import matplotlib.pyplot as plt
import simpy
from srds import ParameterizedDistribution

import ether.blocks.nodes as nodes
from ether.blocks.cells import IoTComputeBox, Cloudlet, FiberToExchange, MobileConnection
from ether.cell import SharedLinkCell, GeoCell
from ether.core import Node, Link, Flow
from ether.topology import Topology
from ether.vis import draw_basic

lognorm = ParameterizedDistribution.lognorm


def node_name(obj):
    if isinstance(obj, Node):
        return obj.name
    elif isinstance(obj, Link):
        return f'link_{id(obj)}'
    else:
        return str(obj)


def counter():
    i = 0
    st = "halo"
    while True:
        yield from (i,st) # ist ein blocking call
        i += 1



def main5():
    topology = Topology()

    aot_node = IoTComputeBox(nodes=[nodes.rpi3, nodes.rpi3])
    neighborhood = lambda size: SharedLinkCell(
        nodes=[
            [aot_node] * size,
            IoTComputeBox([nodes.nuc] + ([nodes.tx2] * size * 2))
        ],
        shared_bandwidth=500,
        backhaul=MobileConnection('internet_chix'))
    city = GeoCell(
        5, nodes=[neighborhood], density=lognorm((0.82, 2.02)))
    cloudlet = Cloudlet(
        5, 2, backhaul=FiberToExchange('internet_chix'))

    topology.add(city)
    topology.add(cloudlet)

    #######################

    draw_basic(topology)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.show()  # display

    print('num nodes:', len(topology.nodes))


def main2():
    print("Hi")
    gen = counter()
    print(next(gen))
    print(next(gen))
    print(next(gen))
    return gen


def main3(gen):
    print(next(gen))
    print(next(gen))
    print(next(gen))



def printer(env):
    while True:
        print(env.now)
        yield env.timeout(1)


def wrapper(source, dest, size, env, topology, results):
    route = topology.route(source, dest)
    flow1 = Flow(env, size, route)
    start_ts = env.now
    yield flow1.start()
    end_ts = env.now
    results.append(end_ts - start_ts)





def create_topology():
    topology = Topology()

    aot_node = IoTComputeBox(nodes=[nodes.rpi3, nodes.rpi3])
    neighborhood = lambda size: SharedLinkCell(
        nodes=[
            [aot_node] * size,
            IoTComputeBox([nodes.nuc] + ([nodes.tx2] * size * 2))
        ],
        shared_bandwidth=500,
        backhaul=MobileConnection('internet_chix'))
    city = GeoCell(
        5, nodes=[neighborhood], density=lognorm((0.82, 2.02)))
    cloudlet = Cloudlet(
        5, 2, backhaul=FiberToExchange('internet_chix'))

    topology.add(city)
    topology.add(cloudlet)
    return topology



def main():
    topology = create_topology()
    env = simpy.Environment()
    source = topology.get_nodes()[0]
    dest = topology.get_nodes()[1]
    size = 10000000
    results = []
    env.process(wrapper(source, dest, size, env, topology, results))
    env.process(wrapper(topology.get_nodes()[3], topology.get_nodes()[4], size, env, topology, results))
    env.process(wrapper(topology.get_nodes()[3], topology.get_nodes()[4], size, env, topology, results))
    env.run(until=3)
    print(results)




if __name__ == '__main__':
    main()
