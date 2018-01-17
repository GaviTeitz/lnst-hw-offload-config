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
            options["fail"] = "yes"
            options["msg"] = err_msg
        custom_mod = self._ctl.get_module("Custom", options=options)
        host.run(custom_mod, desc=desc)