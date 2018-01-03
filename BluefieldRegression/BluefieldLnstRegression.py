#!/usr/bin/python
#written by Gavi - gavi@mellanox.com

import subprocess
from BluefieldLnstTests import testsToRun

for currentTest in testsToRun:
    testCommand = 'lnst-ctl -d -C lnst-ctl.conf --pools pools/' + testsToRun[currentTest]['Pool'] + ' run recipes/Bluefield/' + testsToRun[currentTest]['Recipe']
    with open(currentTest + '.log', 'w+') as outFile:
        with open(currentTest + '.err.log', 'w+') as errFile:
            subprocess.Popen(testCommand, shell=True, stdout=outFile, stderr=errFile).wait()

    with open(currentTest + '.log', 'r') as testOutputFile:
        for line in testOutputFile:
            if 'SUMMARY' in line:
                try:
                    summaryLine = next(testOutputFile).strip()
                    testsToRun[currentTest]['Result'] = 'PASS' if 'PASS' in summaryLine else 'FAIL'
                except StopIteration:
                    testsToRun[currentTest]['Result'] = 'FAIL'
for currentTest in testsToRun:
    print currentTest + ': ' + testsToRun[currentTest]['Result']
