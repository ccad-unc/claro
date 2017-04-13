#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright (C) 2017 CONICET                                                #
#                                                                            #
#  This file is part of Claro                                                #
#                                                                            #
#  This software is governed by the CeCILL-C license under French law and    #
#  abiding by the rules of distribution of free software. You can use,       #
#  modify and/ or redistribute the software under the terms of the CeCILL-C  #
#  license as circulated by CEA, CNRS and INRIA at the following URL         #
#  "http://www.cecill.info".                                                 #
#                                                                            #
#  As a counterpart to the access to the source code and rights to copy,     #
#  modify and redistribute granted by the license, users are provided only   #
#  with a limited warranty and the software's author, the holder of the      #
#  economic rights, and the successive licensors have only limited           #
#  liability.                                                                #
#                                                                            #
#  In this respect, the user's attention is drawn to the risks associated    #
#  with loading, using, modifying and/or developing or reproducing the       #
#  software by the user in light of its specific status of free software,    #
#  that may mean that it is complicated to manipulate, and that also         #
#  therefore means that it is reserved for developers and experienced        #
#  professionals having in-depth computer knowledge. Users are therefore     #
#  encouraged to load and test the software's suitability as regards their   #
#  requirements in conditions enabling the security of their systems and/or  #
#  data to be ensured and, more generally, to use and operate it in the      #
#  same conditions as regards security.                                      #
#                                                                            #
#  The fact that you are presently reading this means that you have had      #
#  knowledge of the CeCILL-C license and that you accept its terms.          #
#                                                                            #
##############################################################################
"""
Manages users in a cluster.

Usage:
    claro user check <username> <hostlist>
"""

#import errno
#import multiprocessing
import logging
#import os
#import re
#import socket
#import subprocess
import sys

import ClusterShell
import docopt
from claro.utils import get_nodeset




def do_checkuser(username,hosts):

    hosts = get_nodeset(hosts) 
    hostlist = "" 
    cmd = "id -u" + " " + username 
    logging.debug("clush: {0} {1}".format(cmd, hosts))

    chkid = ClusterShell.Task.task_self()
    chkid.run(cmd, nodes=hosts)

    for output, nodes in chkid.iter_buffers():
        nodelist = ClusterShell.NodeSet.NodeSet.fromlist(nodes)
        try:
            userid = int(str(output))
            logging.info("User {0} exist in node(s) {1} with id {2}".format(username, nodelist, output))
            hostlist = hostlist + " " + str(nodelist) 
        except:
            logging.info("User {0} doesn't exist in node(s) {1}".format(username, nodelist))
 
    if (len(hostlist) > 0): 
        cmd = "groups" + " " + username 
        chkgrp = ClusterShell.Task.task_self() 
        chkgrp.run(cmd, nodes=hostlist)
 
        for output, nodes in chkgrp.iter_buffers():
            nodelist = ClusterShell.NodeSet.NodeSet.fromlist(nodes)
            try: 
                groups = str(output).split(':')
                logging.info("In node(s) {0}, user {1} is member of the following groups:{2}".format(nodelist,username,groups[1]))
            except: 
                logging.info("In node(s) {0} cannot determine group membership".format(nodelist))

def main():
    logging.debug(sys.argv)
    dargs = docopt.docopt(__doc__)

    if dargs['check']:
        do_checkuser(dargs['<username>'], dargs['<hostlist>'])

if __name__ == '__main__':
    main()
