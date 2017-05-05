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
    claro user add <username> --fullname="<fullname>" --email=<email> --account=<account>
"""

import logging
import os
import re
import subprocess
import sys
import pwd
import grp 
import ClusterShell
import docopt
from claro.utils import get_nodeset, get_from_config, claro_exit, run, clushcp


def validate_email(email):

    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)

    if match == None:
        claro_exit("This email address: {0}, doesn't have a valid syntax".format(email))


def validate_account(account):
    # sacctmgr returns always 0, for this reason cannot use subprocess.check_call 
    accountslist = []
    chkaccount = subprocess.Popen(["sacctmgr", "-n", "-p", "show", "account"],stdout=subprocess.PIPE)
    for line in chkaccount.stdout:
        accountslist.append(str(line).split('|')[0])

    if (account not in accountslist):
        claro_exit("Slurm account {0} doesn't exist in this system".format(account))

def get_confirmation(info,account): 
    
    if (len(info) == 11):
        username = info[10]
        userid = info[9]
        usergroups = username 
    elif (len(info) == 13):
        username = info[12]
        userid = info[11]
        usergroups = username + "," + info[8] 
    else:
        return None  

    userhome = info[4] 
    usershell = info[2] 
 
    logging.info("""A new user will be create with following options:  
        Username: {0} 
        User ID: {1}
        Home directory: {2}
        Default shel: {3}
        Groups: {4} 
        Slurm account: {5} \n""".format(username,userid,userhome,usershell,usergroups,account))
   
    answer = raw_input('Please enter "YES" to confirm: ')

    if (str(answer) == "YES"):
        return True
    else:
        return False
 
   

def get_lastid(objet): 

     if (objet == "user"):
         idrange = get_from_config("user", "uidrange")
         elements = pwd.getpwall()
     elif (objet == "group"):
         idrange = get_from_config("user", "gidrange", verbose = False) or get_from_config("user", "uidrange")
         elements = grp.getgrall()
     else:
         return None 

     idlist = []
     for e in elements:
        cruid = int(e[2])
        if (int(idrange.split(':')[0]) <= cruid <= int(idrange.split(':')[1])):
            idlist.append(cruid)

     if (len(idlist) > 0):
        lastid = max(idlist) + 1
     else:
        lastid = int(idrange.split(':')[0]) + 1

     return lastid

     
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

def welcome_mail(user, fullname, email, account, usershell, userhome, extragroups):
    print_mail = get_from_config("user", "print_mail", verbose = False)      
    send_mail = get_from_config("user", "send_mail", verbose = False)  
    sender = ""

    if (print_mail == "True"):
        print_mail = True
    else:
        print_mail = False

    if (send_mail == "True"):
        send_mail = True
    else:
        send_mail = False


    if (send_mail):
        smtp_server = get_from_config("user", "smtp_server")
        sender = get_from_config("user", "mail_sender")

    if (print_mail):
        logging.info("Printing welcome message")
    
    if (print_mail or send_mail):
        mailtext = ''
        mail_template = get_from_config("user", "mail_template")  
        import fileinput
        message = fileinput.input(mail_template)
        for line in message:
            line = line.replace("_USER_",user)
            line = line.replace("_FULLNAME_",fullname)
            line = line.replace("_EMAIL_",email)
            line = line.replace("_ACCOUNT_",account)
            line = line.replace("_USERSHELL_",usershell)
            line = line.replace("_USERHOME_",userhome)
            line = line.replace("_EXTRAGROUPS_",extragroups)
            line = line.replace("_SENDER_",sender)
            mailtext += str(line)
            if (print_mail):
                print line.rstrip()
        if (send_mail):
            import smtplib
            to = email
            cc = [sender]
            toaddrs = [to] + cc 
            server = smtplib.SMTP(smtp_server)
            server.sendmail(sender, toaddrs, mailtext)
            server.quit()
    else:
        return False 

def mail_forward(action, userhome, email = "", uid = 0, gid = 0): 
    
    forward = userhome + "/.forward"
    if (action == "write"): 
        if (uid == 0) or (gid == 0):  
            logging.info("Cannot write mail address in file: {0}".format(forward))
            return "" 
        else: 
            validate_email(email)
            f = open(forward, 'w')
            f.write(email + "\n")
            f.close()
            os.chmod(forward, 0o600)
            os.chown(forward, uid, gid)
            return email 
    elif (action == "read"): 
        f = open(forward, 'r') 
        usermail = str(f.read().rstrip())
        f.close()
        return usermail 
    else: 
        return ""           




def do_createuser(user, fullname, email, account):
    validate_email(email) 
    validate_account(account) 

    try:
        pwd.getpwnam(user)
        claro_exit("User {0} exists on this system".format(user))
    except KeyError:

        synchro = get_from_config("user", "synchronizer") 
        if (synchro == "clush"):
            hosts = get_from_config("common", "nodes") 
        lastuid = get_lastid("user") 
        lastgid = get_lastid("group") 
        usershell = get_from_config("user", "shell", verbose = False) or "/bin/bash"
        userhome = get_from_config("user", "main_home", verbose = False) or "/home"  
        extragroups = get_from_config("user", "extra_groups", verbose = False) or ""
        userhome = userhome + "/" + user 
        if ( len(extragroups) > 0):
            cmd = ["/usr/sbin/useradd","-s", str(usershell), "-d", str(userhome), "-g", str(lastgid), "-G", str(extragroups), "-m", "-u", str(lastuid), str(user)] 
        else:
            cmd = ["/usr/sbin/useradd","-s", str(usershell), "-d", str(userhome), "-g", str(lastgid), "-m", "-u", str(lastuid), str(user)] 

       
        if (get_confirmation(cmd,account)):
            addgrp = ["/usr/sbin/groupadd","-g", str(lastgid), str(user)] 
            run(addgrp) 
            run(cmd)
            cmd = ["/usr/bin/chfn","-f", fullname, user] 
            run(cmd) 
            ssh_dir = userhome + "/.ssh"
            if (not os.path.exists(ssh_dir)):
                os.makedirs(ssh_dir)
                os.chmod(ssh_dir, 0o700)
                autkeys = ssh_dir + "/authorized_keys"
                open(autkeys, 'w').close()
                os.chmod(autkeys, 0o600)
                for f in ssh_dir,autkeys:
                    os.chown(f, lastuid, lastgid)
            
            cmd = ["/usr/bin/sacctmgr","-i", "add","user",user,"DefaultAccount="+account] 
            run(cmd) 
            if (synchro == "wwsh"):
                target = ["passwd", "group"]
                for c in target:
                    cmdpwd = ["wwsh", "file", "sync", c] 
                    logging.info("wwsh: Synchronize file {0}".format(c))
                    run(cmdpwd) 
            elif (synchro == "clush"):
                target = ["/etc/passwd", "/etc/group"]
                for f in target:
                   logging.info("clush: copy {0} on nodes {1}".format(f,hosts))
                   clushcp(f,f,hosts)
            else:
                logging.info("Cannot determine the synchronization method")

            mail_forward("write", userhome, email, lastuid, lastgid) 
            welcome_mail(user, fullname, email, account, usershell, userhome, extragroups)  
            
        else:  
            claro_exit("Process aborted by user, nothing to do") 

def main():
    logging.debug(sys.argv)
    dargs = docopt.docopt(__doc__)

    if dargs['check']:
        do_checkuser(dargs['<username>'], dargs['<hostlist>'])
    elif dargs['add']:
        do_createuser(dargs['<username>'], dargs['--fullname'], dargs['--email'], dargs['--account'])

if __name__ == '__main__':
    main()
