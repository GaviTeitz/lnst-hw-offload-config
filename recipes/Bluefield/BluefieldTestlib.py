#!/usr/bin/python
#written by Gavi - gavi@mellanox.com

import sys
sys.path.append('../ovs_offload')
from Testlib import Testlib
import re
import logging
from os import linesep

class HwRule(object):
    def __init__(self, description):
        self.regex = r''
        self.description = description

    def matches(self, line):
        return True if re.search(self.regex, line) else False

class L2ForwardingRule(HwRule):
    def __init__(self, description, srcMacAddress, dstMacAddress, forwardingDestination, ethType = '0x[0-9a-f]{4}', inPort = None):
        super(L2ForwardingRule, self).__init__(description)
        self.regex = r'eth\(src=%s,dst=%s\),eth_type\(%s\),.*action:%s' % (str(srcMacAddress).lower(), str(dstMacAddress).lower(), str(ethType), forwardingDestination.lower())
        if inPort:
            self.regex = r'in_port\(%s\),' % (inPort) + self.regex

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

    def verifyRulesAreInHw(self, host, gvmi, rules):
        host.run('mlxdump -d ' + str(self._ctl.get_alias('mstDev')) + ' fsdump --no_zero 1 --type FT --gvmi ' + str(gvmi) + ' > /tmp/lnstHwDump')
        prettyDumpResults = host.run('python pretty-fs-dump/pretty_dump.py -s /tmp/lnstHwDump -vvv').out().strip()
        if len(prettyDumpResults) < 1 and len(rules) > 0:
            self.custom(host, 'Verifying rules are in HW', err_msg = 'Didn\'t find any HW dump results')
            return
        prettyDumpResults = prettyDumpResults.split(linesep)

        allRulesWereFound = True
        for currentRule in rules:
            matchingLineFound = False
            for line in prettyDumpResults:
                if currentRule.matches(line):
                    matchingLineFound = True
                    break
            if not matchingLineFound:
                allRulesWereFound = False
                self.custom(host, 'Verifying rules are in HW', err_msg = 'Couldn\'t find a mathcing rule for: ' + str(currentRule.description))
        if allRulesWereFound:
            logging.debug('Verified the following rules are in HW: ' + linesep + linesep.join(['    ' + rule.description for rule in rules]))
            self.custom(host, 'Verified rules are in HW')
