#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#  Copyright (C) 2014-2016 EDF SA                                            #
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
Manages and get the status from the nodes of a cluster.

Usage:
    claro ipmi connect [-jf] <host>
    claro ipmi getmac <hostlist>
    claro ipmi [--p=<level>] deconnect <hostlist>
    claro ipmi [--p=<level>] (on|off|reboot) <hostlist>
    claro ipmi [--p=<level>] status <hostlist>
    claro ipmi [--p=<level>] setpwd <hostlist>
    claro ipmi [--p=<level>] pxe <hostlist>
    claro ipmi [--p=<level>] disk <hostlist>
    claro ipmi [--p=<level>] ping <hostlist>
    claro ipmi [--p=<level>] blink <hostlist>
    claro ipmi [--p=<level>] immdhcp <hostlist>
    claro ipmi [--p=<level>] bios <hostlist>
    claro ipmi [--p=<level>] reset <hostlist>
    claro ipmi [--p=<level>] sellist <hostlist>
    claro ipmi [--p=<level>] selclear <hostlist>
    claro ipmi ssh <hostlist> <command>
    claro ipmi -h | --help
Alternative:
    claro ipmi <host> connect [-jf]
    claro ipmi <hostlist> getmac
    claro ipmi [--p=<level>] <hostlist> deconnect
    claro ipmi [--p=<level>] <hostlist> (on|off|reboot)
    claro ipmi [--p=<level>] <hostlist> status
    claro ipmi [--p=<level>] <hostlist> setpwd
    claro ipmi [--p=<level>] <hostlist> pxe
    claro ipmi [--p=<level>] <hostlist> disk
    claro ipmi [--p=<level>] <hostlist> ping
    claro ipmi [--p=<level>] <hostlist> blink
    claro ipmi [--p=<level>] <hostlist> immdhcp
    claro ipmi [--p=<level>] <hostlist> bios
    claro ipmi [--p=<level>] <hostlist> reset
    claro ipmi [--p=<level>] <hostlist> sellist
    claro ipmi [--p=<level>] <hostlist> selclear
    claro ipmi <hostlist> ssh <command>
"""

import errno
import multiprocessing
import logging
import os
import re
import socket
import subprocess
import sys

import ClusterShell
import docopt
from claro.utils import claro_exit, run, get_from_config, value_from_file


def ipmi_run(cmd):

    ipmi_p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output = ipmi_p.communicate()[0].strip()
    exit_code = ipmi_p.wait()
    if exit_code:
        return "ERROR: " + output
    else:
        return "OK: " + output


def ipmi_do(hosts, *cmd):

    imm_user = value_from_file(get_from_config("common", "master_passwd_file"), "IMMUSER")
    os.environ["IPMI_PASSWORD"] = value_from_file(get_from_config("common", "master_passwd_file"), "IMMPASSWORD")
    nodeset = ClusterShell.NodeSet.NodeSet(hosts)

    p = multiprocessing.Pool(parallel)
    result_map = {}

    for host in nodeset:

        pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if not pat.match(host):
            prefix = get_from_config("ipmi", "prefix")
            sufix = get_from_config("ipmi", "sufix")
            host = prefix + host + sufix

        ipmitool = ["ipmitool", "-I", "lanplus", "-H", host, "-U", imm_user, "-E", "-e!"]
        ipmitool.extend(cmd)
        logging.debug("ipmi/ipmi_do: {0}".format(" ".join(ipmitool)))
        result_map[host] = p.apply_async(ipmi_run, (ipmitool,))

    p.close()
    p.join()

    for host, result in result_map.items():
        print host, result.get()


def getmac(hosts):
    imm_user = value_from_file(get_from_config("common", "master_passwd_file"), "IMMUSER")
    os.environ["IPMI_PASSWORD"] = value_from_file(get_from_config("common", "master_passwd_file"), "IMMPASSWORD")
    nodeset = ClusterShell.NodeSet.NodeSet(hosts)
    for host in nodeset:

        pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if not pat.match(host):
            prefix = get_from_config("ipmi", "prefix")
            sufix = get_from_config("ipmi", "sufix")
            host = prefix + host + sufix

        logging.info("{0}: ".format(host))
        chassis = get_from_config("ipmi", "chassis")

        if (chassis == 'supermicro'):
            cmd = ["ipmitool", "-I", "lanplus", "-H", host,
                   "-U", imm_user, "-E", "raw", "0x30", "0x21"]
            datainline = 1
        elif(chassis == 'dell'):
            cmd = ["ipmitool", "-I", "lanplus", "-H", host,
                   "-U", imm_user, "-E", "raw", "0x30", "0x21"]
        else:
            cmd = ["ipmitool", "-I", "lanplus", "-H", host,
                   "-U", imm_user, "-E", "fru", "print", "0"]
            datainline = 1

        logging.debug("ipmi/getmac: {0}".format(" ".join(cmd)))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        lines = proc.stdout.readlines()

        if (len(lines) < datainline ):
	        claro_exit("The host {0} can't be reached".format(host))

        if (chassis == 'supermicro'):
            full_mac = lines[0].upper()
            mac_address1 = full_mac[13:].replace(" ", ":")
            logging.info("eth0's MAC address is {0}".format(mac_address1)) 
            
        else: 
            full_mac = lines[14].split(":")[1].strip().upper()
            mac_address1 = "{0}:{1}:{2}:{3}:{4}:{5}".format(full_mac[0:2],
                                                            full_mac[2:4],
                                                            full_mac[4:6],
                                                            full_mac[6:8],
                                                            full_mac[8:10],
                                                            full_mac[10:12])

            mac_address2 = "{0}:{1}:{2}:{3}:{4}:{5}".format(full_mac[12:14],
                                                            full_mac[14:16],
                                                            full_mac[16:18],
                                                            full_mac[18:20],
                                                           full_mac[20:22],
                                                            full_mac[22:24])

            logging.info("  eth0's MAC address is {0}\n"
                     "  eth1's MAC address is {1}".format(mac_address1, mac_address2))


def do_connect_ipmi(host):

    imm_user = value_from_file(get_from_config("common", "master_passwd_file"), "USER")
    os.environ["IPMI_PASSWORD"] = value_from_file(get_from_config("common", "master_passwd_file"), "IMMPASSWORD")

    pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    if not pat.match(host):
        prefix = get_from_config("ipmi", "prefix")
        sufix = get_from_config("ipmi", "sufix")
        host = prefix + host + sufix

    ipmitool = ["ipmitool", "-I", "lanplus", "-H", host, "-U", imm_user, "-E", "-e!", "sol", "activate"]
    logging.debug("ipmi/ipmi_do: {0}".format(" ".join(ipmitool)))
    run(ipmitool)


def do_connect(host, j=False, f=False):
    nodeset = ClusterShell.NodeSet.NodeSet(host)
    if (len(nodeset) != 1):
        claro_exit('Only one host allowed for this command')

    pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    if pat.match(host):
        logging.debug("The host is an IP adddres: {0}. Using ipmitool without conman.".format(host))
        do_connect_ipmi(host)
    else:
        conmand = get_from_config("ipmi", "conmand")
        port = int(get_from_config("ipmi", "port"))
        if (len(conmand) == 0):
            claro_exit("You must set the paramenter 'conmand' in the configuration file")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((conmand, port))
            os.environ["CONMAN_ESCAPE"] = '!'

            cmd = ["conman"]
            if j:
                cmd = cmd + ["-j"]
            if f:
                cmd = cmd + ["-f"]
            cmd = cmd + ["-d", conmand, host]
            run(cmd)
        except socket.error as e:
            logging.debug("Conman not running. Message on connect: Errno {0} - {1}".format(e.errno, e.strerror))
            do_connect_ipmi(host)

        s.close()


def do_ping(hosts):
    nodes = ClusterShell.NodeSet.NodeSet(hosts)
    cmd = ["fping", "-r1", "-u", "-s"] + list(nodes)
    run(cmd)


def do_ssh(hosts, command):

    prefix = get_from_config("ipmi", "prefix")
    sufix = get_from_config("ipmi", "sufix")
    hosts = prefix + hosts + sufix

    os.environ["SSHPASS"] = \
        value_from_file(get_from_config("common", "master_passwd_file"),
                        "IMMPASSWORD")
    imm_user = \
        value_from_file(get_from_config("common", "master_passwd_file"),
                        "IMMUSER")

    task = ClusterShell.Task.task_self()
    task.set_info("ssh_user", imm_user)
    task.set_info("ssh_path", "/usr/bin/sshpass -e /usr/bin/ssh")
    task.set_info("ssh_options", "-oBatchMode=no")
    task.shell(command, nodes=hosts)
    task.resume()

    for buf, nodes in task.iter_buffers():
        print "---\n%s:\n---\n %s" \
              % (ClusterShell.NodeSet.fold(",".join(nodes)),
                 buf)

def main():
    logging.debug(sys.argv)
    dargs = docopt.docopt(__doc__)

    global parallel
    # Read the value from the config file and use 1 if it hasn't been set
    try:
        parallel = int(get_from_config("ipmi", "parallel"))
    except:
        logging.warning("parallel hasn't been set in config.ini, using 1 as value")
        parallel = 1
    # Use the value provided by the user in the command line
    if dargs['--p'] is not None and dargs['--p'].isdigit():
        parallel = int(dargs['--p'])

    if dargs['connect']:
        do_connect(dargs['<host>'], dargs['-j'], dargs['-f'])
    elif dargs['deconnect']:
        ipmi_do(dargs['<hostlist>'], "sol", "deactivate")
    elif dargs['status']:
        ipmi_do(dargs['<hostlist>'], "power", "status")
    elif dargs['setpwd']:
        imm_user = value_from_file(get_from_config("common", "master_passwd_file"), "IMMUSER")
        imm_pwd = value_from_file(get_from_config("common", "master_passwd_file"), "IMMPASSWORD")
        ipmi_do(dargs['<hostlist>'], "user", "set", "name", "2", imm_user)
        ipmi_do(dargs['<hostlist>'], "user", "set", "password", "2", imm_pwd)
    elif dargs['getmac']:
        getmac(dargs['<hostlist>'])
    elif dargs['on']:
        ipmi_do(dargs['<hostlist>'], "power", "on")
    elif dargs['off']:
        ipmi_do(dargs['<hostlist>'], "power", "off")
    elif dargs['reboot']:
        ipmi_do(dargs['<hostlist>'], "chassis", "power", "reset")
    elif dargs['blink']:
        ipmi_do(dargs['<hostlist>'], "chassis", "identify", "1")
    elif dargs['bios']:
        ipmi_do(dargs['<hostlist>'], "chassis", "bootparam", "set", "bootflag", "force_bios")
    elif dargs['immdhcp']:
        ipmi_do(dargs['<hostlist>'], "lan", "set", "1", "ipsrc", "dhcp")
    elif dargs['pxe']:
        ipmi_do(dargs['<hostlist>'], "chassis", "bootdev", "pxe")
    elif dargs['disk']:
        ipmi_do(dargs['<hostlist>'], "chassis", "bootdev", "disk")
    elif dargs['reset']:
        ipmi_do(dargs['<hostlist>'], "mc", "reset", "cold")
    elif dargs['sellist']:
        ipmi_do(dargs['<hostlist>'], "sel", "list")
    elif dargs['selclear']:
        ipmi_do(dargs['<hostlist>'], "sel", "clear")
    elif dargs['ping']:
        do_ping(dargs['<hostlist>'])
    elif dargs['ssh']:
        do_ssh(dargs['<hostlist>'], dargs['<command>'])

if __name__ == '__main__':
    main()
