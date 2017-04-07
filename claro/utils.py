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

import errno
import logging
import os
import subprocess
import ConfigParser
import sys
import getpass

import ClusterShell.NodeSet
import ClusterShell.Task


class Conf:
    """Class which contains runtime variables"""
    def __init__(self):
        self.debug = False
        self.ddebug = False
        self.config = None

# global runtime Conf object
conf = Conf()


def clush(hosts, cmds):
    logging.debug("utils/clush: {0} {1}".format(cmds, hosts))

    task = ClusterShell.Task.task_self()
    task.run(cmds, nodes=hosts)

    for output, nodes in task.iter_buffers():
        logging.info("{0} {1}".format(ClusterShell.NodeSet.NodeSet.fromlist(nodes), output))


def run(cmd):
    logging.debug("utils/run: {0}".format(" ".join(cmd)))

    try:
        retcode = subprocess.call(cmd)
    except OSError, e:
        if (e.errno == errno.ENOENT):
            claro_exit("Binary not found, check your path and/or retry as root. \
                      You were trying to run:\n {0}".format(" ".join(cmd)))

    if retcode != 0:
        claro_exit(' '.join(cmd))


def get_from_config(section, value, dist = '', verbose = True):
    """ Read a value from config.ini and return it"""
    if dist == '':
        try:
            return getconfig().get(section, value).strip()
        except:
            if verbose:
                claro_exit("Value '{0}' not found in the section '{1}'".format(value, section))
            else:
               pass

    elif dist in getconfig().get("common", "allowed_distributions"):
        or_section = section + "-" + dist

        # If the value is not in the override section, return the base value
        if getconfig().has_option(or_section, value):
            try:
                return getconfig().get(or_section, value).strip()
            except:
                if verbose:
                    claro_exit("Value '{0}' not found in section '{1}'".format(value, section))
                else:
                    pass 
        else:
            try:
                return getconfig().get(section, value).strip()
            except:
                if verbose:
                    claro_exit("Value '{0}' not found in section '{1}'".format(value, section))
                else:
                    pass
    else:
        if verbose:
            claro_exit("{0} is not a known distribution".format(dist))


def getconfig():
    files = ['/etc/claro/config.ini']
    if conf.config:
        files.append(conf.config)

    if getconfig.config is None:
        getconfig.config = ConfigParser.ConfigParser()
        getconfig.config.read(files)
    return getconfig.config

getconfig.config = None


def value_from_file(myfile, key):
    """ Read a value from a headless ini file. """
    password = ""
    if os.access(myfile, os.R_OK): 
        with open(myfile, 'r') as hand:
            for line in hand:
                if key in line:
                    texto = line.rstrip().split("=")
                    password = texto[1].strip('"').strip("'")
        if password == "":
            claro_exit("{0} not found in the file {1}".format(key, myfile))
        return password
    else:
        claro_exit("{0}: file not accessible".format(myfile))

def get_nodeset(hosts):
    if (hosts == "nodes"):
        nodeset = ClusterShell.NodeSet.NodeSet(get_from_config("common", "nodes"))
    else:
        nodeset = ClusterShell.NodeSet.NodeSet(hosts)
    return nodeset 

def initialize_logger(debug):
    output_dir = "/var/log/claro"
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create logs directory if not exist
    if (not os.path.exists(output_dir)) or (not os.access(output_dir, os.W_OK)):
        try:
            os.makedirs(output_dir, 0o1777) 
        except:
            output_dir = os.getenv("HOME")+"/.claro/log"
            if (not os.path.exists(output_dir)):
                try:
                    os.makedirs(output_dir)
                except:
                    claro_exit("Cannot create the log directory {0}".format(output_dir))
         
         

    # Create console handler and set level to info or debug, when it's enabled
    handler = logging.StreamHandler()
    if debug:
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("claro - %(levelname)s - %(message)s")
    else:
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("claro - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Create a log file, with everything, handler and set level to debug
    filelog = getpass.getuser() + "_all.log"
    handler = logging.FileHandler(os.path.join(output_dir, filelog), "a")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create error file, with the most important messages, handler and set level to warning
    filelog = getpass.getuser() + "_important.log"
    handler = logging.FileHandler(os.path.join(output_dir, filelog), "a")
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def claro_exit(msg):
    logging.error(msg)
    sys.exit(1)
