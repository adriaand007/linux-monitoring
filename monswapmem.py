#!/usr/bin/python
"""
Script to monitor and report on Linux SWAP memory.
"""

import fnmatch
import pwd
from os import listdir
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-u", "--userswp", action="store_true", dest="userswp",
                  default=False, help="Print Per User Swap Usage [default: %default]")
parser.add_option("-t", "--total", action="store_true", dest="swptotal",
                  default=False, help="Display Total Swap Usage Summary [default: %default]")
parser.add_option("-p", "--processwp", action="store_true", dest="processwp",
                  default=False, help="Display per Process Swap Usage [default: %default]")
parser.add_option("-P", "--ppidswp", action="store_true", dest="ppidswp",
                  default=False, help="Display per Perrant Process Swap Usage [default: %default]")
(options, args) = parser.parse_args()


tswpsz = 0
siddir = [f for f in listdir('/proc') if fnmatch.fnmatch(f, '[0-9][0-9]*')]
uidswp = {}
ppidswp = {}

for dirr in siddir:
    with open("/proc/" + dirr + "/smaps") as f:
        prcswp = 0
        for line in f:
            if line.startswith('Swap:'):
                prcswp += int(line.split()[1])
        if prcswp == 0:
            continue
        else:
            infile = open("/proc/" + dirr + "/cmdline", 'r')
            firstLine = infile.readline()
            infile1 = open("/proc/" + dirr + "/status", 'r')
            for lines1 in infile1.readlines():
                if lines1.startswith('Uid:'):
                    try:
                        uidswp[str("uid" + lines1.split()[1])] += prcswp
                    except:
                        uidswp[str("uid" + lines1.split()[1])] = prcswp
                if lines1.startswith('PPid:'):
                    try:
                        ppidswp[str("ppid" + lines1.split()[1])] += prcswp
                    except:
                        ppidswp[str("ppid" + lines1.split()[1])] = prcswp
            if options.processwp:
                print str(dirr.ljust(8) + " : " +
                          (str(prcswp) + " KB").ljust(16) +
                          " :  CMD: " + firstLine
                         )
            tswpsz += prcswp

if options.processwp:
    print "\n"


if options.userswp:
    print str("User: ").ljust(16) + str("Uid: ").ljust(12) + str("Usage: KB").rjust(12)
    for uiidd in uidswp:
        if uiidd != 'key':
            print str(
                pwd.getpwuid(int(uiidd.replace('uid', '')))[0].ljust(16) +
                str(uiidd.replace('uid', '')).ljust(12) +
                str(uidswp[uiidd]).rjust(12)
                )
    print "\n"

if options.ppidswp:
    print str("App:").ljust(16) + str("Ppid:").ljust(12) + str("Usage: KB").rjust(12)
    for ppidd in ppidswp:
        if ppidd != 'key':
            infile2 = open("/proc/" + ppidd.replace('ppid', '') + "/comm", 'r')
            firstLine2 = infile2.readline()
            print str(
                firstLine2.replace('\n', ' ').replace('\r', '').strip().ljust(16) +
                str(ppidd.replace('ppid', '').ljust(12)) +
                str(ppidswp[ppidd]).rjust(12)
                )
    print "\n"

if options.swptotal:
    print "Total: " + str(tswpsz) + " KB"
    print "\n"
