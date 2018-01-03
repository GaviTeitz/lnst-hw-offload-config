from lnst.Controller.Task import ctl
import sys
sys.path.append('../ovs_offload')
from Testlib import Testlib

# ------
# SETUP
# ------

tl = Testlib(ctl)

h1 = ctl.get_host("host1")
h2 = ctl.get_host("host2")
g1 = ctl.get_host("guest1")

h1.sync_resources(modules=["IcmpPing", "Icmp6Ping", "Iperf"])
h2.sync_resources(modules=["Iperf"])

# ------
# TESTS
# ------

ipv = ctl.get_alias("ipv")

h1_hostnic = h1.get_interface("ens1f0")
h1_mac = h1_hostnic.get_hwaddr()
h2_hostnic = h2.get_interface("ens1f0")
h2_mac = h2_hostnic.get_hwaddr()

ping_count = 30
ping_interval = 0.2
ping_timeout = 10

def ping(options={}):
    options = dict(options)
    options.update({
       "addr": h2_hostnic.get_ip(0),
       "count": ping_count,
       "iface": h1_hostnic.get_devname(),
       "interval": ping_interval
    })
    ping_mod = ctl.get_module("IcmpPing", options=options)
    h1.run(ping_mod, timeout=ping_timeout)


def ping6(options={}):
    options = dict(options)
    options.update({
        "addr": h2_hostnic.get_ip(1),
        "count": ping_count,
        "iface": h1_hostnic.get_ip(1),
        "interval": ping_interval
    })
    ping_mod6 = ctl.get_module("Icmp6Ping", options=options)
    h1.run(ping_mod6, timeout=ping_timeout)


def verify_tc_rules(proto):
    def verify_tc_rule(ovsPortName, src_mac, dst_mac, srcName, dstName):
        m = tl.find_tc_rule(g1, ovsPortName, src_mac, dst_mac, proto, 'mirred')
        if m:
            tl.custom(h1, 'TC rule ' + str(proto) + ' ' + str(srcName) + ' --> ' + str(dstName), opts=m)
        else:
            tl.custom(h1, 'TC rule ' + str(proto) + ' ' + str(srcName) + ' --> ' + str(dstName), 'ERROR: cannot find tc rule')

    verify_tc_rule('rep-0', h1_mac, h2_mac, 'Host 1', 'Host 2')
    verify_tc_rule('ens6',  h2_mac, h1_mac, 'Host 2', 'Host 1')


if ipv in ('ipv4', 'both'):
    ping()
    verify_tc_rules('ip')
    for size in (200, 400, 1000):
        ping({'size': size})

if ipv in ('ipv6', 'both'):
    ping6()
    verify_tc_rules('ipv6')
    for size in (200, 400, 1000):
        ping6({'size': size})
