% Claro User's Guide
% Antonio J. Russo
% April 7, 2017

# What's Claro?

Claro is a set of cluster administration tools, that started as a fork of 
[clara](https://github.com/edf-hpc/clara/).  
Clara has created to help in the installation and maintenance of clusters 
at EDF (Electricité de France).

The different tools are written as independent plugins that can be added,
removed and modified independently. This plugins are compatibles with many GNU/Linux 
distributions, including Debian and RHEL derivatives.

Claro is distributed under the CeCILL-C Free Software License Agreement version
1.0. You can find more information about the CeCILL licenses at
[http://www.cecill.info/index.en.html](http://www.cecill.info/index.en.html).


# Obtaining, building and installing Claro

Claro's code is available at GitHub [https://github.com/ccad-unc/claro](https://github.com/ccad-unc/claro).
You can obtain a copy using *git*:

    $ git clone https://github.com/edf-hpc/claro.git

Claro is developed in a RHEL system, but probably also useful in a Debian or a Debian derivative
system. 

Claro provides a setuptools script for its installation.
Just run:

    # python setup.py install

Before, you also will need to install the runtime dependencies. 
The dependencies common to all plugins are:
[python](http://www.python.org), [docopt](http://docopt.org/) and [clustershell](http://cea-hpc.github.io/clustershell/).

The remaining dependencies, listed by plugin, are:

+ impi: [fping](http://fping.org/), [ipmitool](http://sourceforge.net/projects/ipmitool/), [sshpass](https://sourceforge.net/projects/sshpass/)


# Getting started

Claro itself is not a tool, but rather provides a common interface to several
tools. To see the list of available tools, just type `claro` like in the following
example.

    # claro
    Usage: claro [-d | -dd] [options] <plugin> [<args>...]
       claro help <plugin>
       claro [--version]
       claro [--help]

    Options:
       -d                 Enable debug output
       -dd                Enable debug output for third party applications
       --config=<file>    Provide a configuration file

    Claro provides the following plugins:
       ipmi     Manages and get the status from the nodes of a cluster.

    See 'claro help <plugin>' for detailed help on a plugin
    and 'claro <plugin> --help' for a quick list of options of a plugin.


Then to use the tool *ipmi*, just type `claro ipmi` and it'll show you the
options of *ipmi*:

     
    # claro ipmi
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

You can check quickly the help of the tool *ipmi* invoking the manpage:
`man claro-ipmi` or just typing `claro help ipmi`.

# Configuration file

The configuration file of Claro is installed at `/etc/claro/config.ini` and it
is a simple text file using the [INI file format](http://en.wikipedia.org/wiki/INI_file).
This file has a basic structure composed of sections, properties, and values.
For example, a portion from the Claro's configuration file is copied:

    [common]
    master_passwd_file=/srv/claro/master_pwd
    nodes=mendieta[01-23]

    [ipmi]
    parallel=12
    suffix=-ipmi
    chassis=supermicro
    conmand=None



The lines starting with a semi-colon are commentaries and they're ignored.

`[common]` and `[ipmi]` indicate the begin of a section and its name.

The remaining lines contain properties. Every property has a name and a value,
delimited by an equals sign (=). The name appears to the left of the equals sign
and the value appears to the right. All properties listed after a section
declarotion are associated with that section.

The section `[common]` is common to all the plugins and then every plugin
can add a section with the name of the plugin.

Sometimes, we want to add specific values for different distros and in that case
we'll need to add the name of the plugin, a hyphen `-` followed by the name of
the distribution. For example, if we want to add different configurations
values for the plugin `repo` for centos6 and centos7, we'll need to add them
under the sections `[repo-centos6]` and `[repo-centos7]`.


# Plugins

## Plugin 'ipmi'

*claro ipmi* offers a simplified interface of ipmitool, an utility for controlling
IPMI-enabled devices. The username and password needed by ipmitool are handled
automatically.

Usernames and passwords are stored in a text file indicated in common sections under 
the property `master_passwd_file`. This plugin is expected to find the following 
values: 

    IMMUSER=ADMIN
    IMMPASSWORD=SOMEPASS710



### Sypnosis

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
    claro ipmi [--p=<level>] ssh <hostlist> <command>
    claro ipmi -h | --help

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
    claro ipmi [--p=<level>] <hostlist> ssh <command>

### Options

    claro ipmi connect [-jf] <host>

Connect to IMM serial console, including video, keyboard and mouse controlling
The flag -j joins the connection and the flag -f forces it.

    claro ipmi deconnect <host>

Deconnect from a IMM serial console

    claro ipmi on <hostlist>

Power up chassis

    claro ipmi off <hostlist>

Power down chassis into soft off. WARNING: it does do a clean shutdown of the OS.

    claro ipmi reboot <hostlist>

This command will perform a hard reset

    claro ipmi status <hostlist>

Get target node power status using the IMM device

    claro ipmi setpwd <hostlist>

Set up IMM user id/password on a new device

    claro ipmi getmac <hostlist>

Get node MAC addresses using the IMM device

    claro ipmi pxe <hostlist>

Use IMM to perform a network boot on the next reboot

    claro ipmi disk <hostlist>

Use IMM to perform a disk boot on the next reboot

    claro ipmi ping <hostlist>

Use fping to check status of the machines

    claro ipmi blink <hostlist>

Make chassis blink to help on-site admins to identify the machine

    claro ipmi immdhcp <hostlist>

Set selected ipmi interfaces to grab an IP via DHCP

    claro ipmi bios <hostlist>

Make selected machines go directly into BIOS on next reboot

    claro ipmi sellist <hostlist>

Display the entire content of the System Event Log (SEL).

    claro ipmi selclear <hostlist>

Clear the contents of the System Event Log (SEL). It cannot be undone so be careful.

    claro ipmi reset <hostlist>

Reset the IMM device (cold reset)

    claro ipmi ssh <hostlist> <command>

Run a command through the SSH interface of the IMM

For the commands that allow to interact multiple nodes at the same time,
the command can be run in parallel using [--p=<level>].
The parallelism to use by default can be set in the configuration file
in the [ipmi] section with the paramenter "parallel". This value is
overridden by the input from the command line.

Furthermore, the <hostlist> can be replaced by the key word "nodes", defined
in the configuration file in the [common] section.



### Examples

This command will ping all hosts nodes in a cluster:

    # claro ipmi ping nodes

To check the status from node13:

    # claro ipmi status node13

Or also:

    # claro ipmi node13 status

And you can check the status of all the nodes using parallelism:

    # claro ipmi --p=16 status node[12-99]
