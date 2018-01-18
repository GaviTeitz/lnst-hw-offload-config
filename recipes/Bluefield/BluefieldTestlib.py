#!/usr/bin/python
#written by Gavi - gavi@mellanox.com

import sys
sys.path.append('../ovs_offload')
from Testlib import Testlib

class BluefieldTestlib(Testlib):
    def syncTestModules(self, hostToTestModulesDict):
        for currentHost in hostToTestModulesDict:
            currentTestModulesList = list(set(hostToTestModulesDict[currentHost] + ['Custom']))
            currentHost.sync_resources(modules=currentTestModulesList)

    #Override
    def custom(self, host, desc, err_msg=None, opts=None):
        options = {}
        if opts:
            options.update(opts)
        if err_msg:
            options['fail'] = 'yes'
            options['msg'] = err_msg
        custom_mod = self._ctl.get_module('Custom', options=options)
        host.run(custom_mod, desc=desc)

    def ping(self, host, srcInterface, dstIp, pingModule = 'IcmpPing', pingCount = 30, pingInterval = 0.2, pingTimeout = 10, options = {}, runInBackground = False, backgroundDelay = 1):
        options = dict(options)
        options.update({'addr'     : dstIp,
                        'count'    : pingCount,
                        'iface'    : srcInterface,
                        'interval' : pingInterval
        })
        host.run(self._ctl.get_module(pingModule, options=options), timeout=pingTimeout, bg=runInBackground)
        if runInBackground:
            self._ctl.wait(backgroundDelay)
