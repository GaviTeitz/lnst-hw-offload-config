from lnst.Controller.Task import ctl
from BluefieldTestlib import BluefieldTestlib

# ------
# SETUP
# ------

tl = BluefieldTestlib(ctl)

h1 = ctl.get_host('host1')
h2 = ctl.get_host('host2')
g1 = ctl.get_host('guest1')

h1_hostnic = h1.get_interface('ens1f0')
h1_mac = h1_hostnic.get_hwaddr()
h2_hostnic = h2.get_interface('ens1f0')
h2_mac = h2_hostnic.get_hwaddr()

tl.syncTestModules({h1 : ['IcmpPing', 'Icmp6Ping', 'Iperf'],
                    h2 : ['Iperf']})

# ------
# TESTS
# ------

def verify_tc_rules(proto):
    def verify_tc_rule(ovsPortName, src_mac, dst_mac, srcName, dstName):
        m = tl.find_tc_rule(g1, ovsPortName, src_mac, dst_mac, proto, 'mirred')
        if m:
            tl.custom(h1, 'TC rule ' + str(proto) + ' ' + str(srcName) + ' --> ' + str(dstName), opts=m)
        else:
            tl.custom(h1, 'TC rule ' + str(proto) + ' ' + str(srcName) + ' --> ' + str(dstName), 'ERROR: cannot find tc rule')

    verify_tc_rule('rep-0', h1_mac, h2_mac, 'Host 1', 'Host 2')
    verify_tc_rule('ens6',  h2_mac, h1_mac, 'Host 2', 'Host 1')


def verifyPing(srcInterface, dstIp, pingModule, tcProto):
    tl.ping(h1, srcInterface, dstIp, pingModule, runInBackground=True)

    verify_tc_rules(tcProto)

    for size in (200, 400, 1000):
        tl.ping(h1, srcInterface, dstIp, pingModule, options = {'size': size})

ipv = ctl.get_alias('ipv')

if ipv in ('ipv4', 'both'):
    verifyPing(h1_hostnic.get_devname(), h2_hostnic.get_ip(0), 'IcmpPing', 'ipv4')

if ipv in ('ipv6', 'both'):
    verifyPing(h1_hostnic.get_ip(1), h2_hostnic.get_ip(1), 'Icmp6Ping', 'ipv6')
